from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import re
from typing import List, Optional, Tuple, Dict, Any

class YouTubeProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        """Extract video ID from YouTube URL or validate direct video ID"""
        input_text = url_or_id.strip()
        
        # If it's already a video ID (11 characters, alphanumeric with _ and -)
        if len(input_text) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', input_text):
            return input_text
        
        # Extract from various YouTube URL formats
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:youtube\.com\/shorts\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, input_text)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', video_id):
                    return video_id
        
        return None
    
    def process_transcript_data(self, transcript_data: List[Dict[str, Any]]) -> str:
        """Process transcript data with text, start, and duration fields"""
        if not transcript_data:
            return ""
        
        # Sort by start time to ensure chronological order
        sorted_transcript = sorted(transcript_data, key=lambda x: x.get('start', 0))
        
        # Extract and join text content
        transcript_text = " ".join([
            chunk.get("text", "").strip() 
            for chunk in sorted_transcript 
            if chunk.get("text", "").strip()
        ])
        
        return transcript_text
    
    def get_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[dict]]:
        """Get transcript using direct video ID"""
        
        # Validate video ID
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format. Please provide an 11-character video ID."}
        
        try:
            # Get transcript data directly
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            if not transcript_data:
                return None, {"error": "No transcript data received"}
            
            # Process the transcript data to extract text
            transcript_text = self.process_transcript_data(transcript_data)
            
            if not transcript_text.strip():
                return None, {"error": "Empty transcript received"}
            
            # Create metadata
            metadata = {
                "video_id": video_id,
                "total_segments": len(transcript_data),
                "total_length": len(transcript_text),
                "duration": max([seg.get('start', 0) + seg.get('duration', 0) for seg in transcript_data]) if transcript_data else 0,
                "method": "direct_api_call",
                "format": "timestamped_segments"
            }
            
            return transcript_text, metadata
            
        except TranscriptsDisabled:
            return None, {"error": "Transcripts are disabled for this video"}
        except NoTranscriptFound:
            return None, {"error": "No transcript found for this video"}
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return None, {"error": "Video not found or transcript unavailable"}
            elif "private" in error_msg.lower():
                return None, {"error": "Video is private or restricted"}
            else:
                return None, {"error": f"Error fetching transcript: {error_msg}"}
    
    def get_transcript_with_timestamps(self, video_id: str) -> Tuple[Optional[List[Dict]], Optional[dict]]:
        """Get full transcript data with timestamps for advanced processing"""
        
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format"}
        
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            if not transcript_data:
                return None, {"error": "No transcript data received"}
            
            # Sort by start time
            sorted_transcript = sorted(transcript_data, key=lambda x: x.get('start', 0))
            
            metadata = {
                "video_id": video_id,
                "total_segments": len(sorted_transcript),
                "duration": max([seg.get('start', 0) + seg.get('duration', 0) for seg in sorted_transcript]) if sorted_transcript else 0,
                "method": "timestamped_data"
            }
            
            return sorted_transcript, metadata
            
        except Exception as e:
            return None, {"error": f"Error fetching timestamped transcript: {str(e)}"}
    
    def process_transcript(self, transcript: str, video_id: str) -> List[Document]:
        """Split transcript into chunks and create documents"""
        if not transcript or not transcript.strip():
            return []
        
        # Clean the transcript text
        cleaned_transcript = re.sub(r'\s+', ' ', transcript.strip())
        
        # Split into chunks
        chunks = self.splitter.split_text(cleaned_transcript)
        
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Only add non-empty chunks
                doc = Document(
                    page_content=chunk.strip(),
                    metadata={
                        "video_id": video_id,
                        "chunk_id": i,
                        "source": f"YouTube Video {video_id}",
                        "chunk_length": len(chunk)
                    }
                )
                documents.append(doc)
        
        return documents
    
    def create_timestamped_chunks(self, transcript_data: List[Dict], video_id: str, chunk_duration: int = 60) -> List[Document]:
        """Create chunks based on time segments for better context"""
        if not transcript_data:
            return []
        
        documents = []
        current_chunk = []
        current_start = 0
        chunk_id = 0
        
        for segment in transcript_data:
            start_time = segment.get('start', 0)
            duration = segment.get('duration', 0)
            text = segment.get('text', '').strip()
            
            if not text:
                continue
            
            # Start new chunk if time gap is too large
            if not current_chunk:
                current_start = start_time
            
            current_chunk.append(text)
            
            # Create chunk if duration threshold is reached
            if start_time + duration - current_start >= chunk_duration:
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    doc = Document(
                        page_content=chunk_text,
                        metadata={
                            "video_id": video_id,
                            "chunk_id": chunk_id,
                            "source": f"YouTube Video {video_id}",
                            "start_time": current_start,
                            "end_time": start_time + duration,
                            "duration": start_time + duration - current_start,
                            "chunk_type": "timestamped"
                        }
                    )
                    documents.append(doc)
                    chunk_id += 1
                    current_chunk = []
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "video_id": video_id,
                    "chunk_id": chunk_id,
                    "source": f"YouTube Video {video_id}",
                    "start_time": current_start,
                    "chunk_type": "timestamped"
                }
            )
            documents.append(doc)
        
        return documents
