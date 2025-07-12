from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import re
import time
import random
from typing import List, Optional, Tuple

class YouTubeProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Enhanced video ID extraction with validation"""
        url = url.strip()
        
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:youtube\.com\/shorts\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', video_id):
                    return video_id
        
        # If URL is already just a video ID
        if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
            return url
        
        return None
    
    def get_transcript(self, video_id: str, max_retries: int = 3) -> Tuple[Optional[str], Optional[dict]]:
        """Get transcript with comprehensive error handling and retry logic"""
        
        # Validate video ID first
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format"}
        
        for attempt in range(max_retries):
            try:
                # Add delay for retry attempts
                if attempt > 0:
                    time.sleep(random.uniform(1, 3))
                
                # Try to get available transcripts first
                try:
                    transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # Try to find English transcripts
                    try:
                        transcript = transcript_list_obj.find_transcript(['en', 'en-US', 'en-GB'])
                        transcript_data = transcript.fetch()
                    except:
                        # If no English transcript, try any available transcript
                        available_transcripts = list(transcript_list_obj)
                        if not available_transcripts:
                            return None, {"error": "No transcripts available for this video"}
                        
                        transcript_data = available_transcripts[0].fetch()
                
                except:
                    # Fallback to direct transcript fetch
                    transcript_data = YouTubeTranscriptApi.get_transcript(
                        video_id, 
                        languages=["en", "en-US", "en-GB"]
                    )
                
                # Create full transcript text
                transcript_text = " ".join([chunk["text"] for chunk in transcript_data])
                
                if not transcript_text.strip():
                    return None, {"error": "Empty transcript received"}
                
                # Create metadata
                metadata = {
                    "video_id": video_id,
                    "total_chunks": len(transcript_data),
                    "total_length": len(transcript_text),
                    "attempt": attempt + 1
                }
                
                return transcript_text, metadata
                
            except TranscriptsDisabled:
                return None, {"error": "Transcripts are disabled for this video"}
            except NoTranscriptFound:
                return None, {"error": "No transcript found for this video"}
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle specific error cases
                if "no element found" in error_msg:
                    if attempt < max_retries - 1:
                        continue  # Retry for parsing errors
                    return None, {"error": "Video transcript unavailable or restricted"}
                elif "private" in error_msg or "unavailable" in error_msg:
                    return None, {"error": "Video is private or unavailable"}
                elif "rate limit" in error_msg:
                    if attempt < max_retries - 1:
                        time.sleep(5)  # Longer delay for rate limiting
                        continue
                    return None, {"error": "Rate limited by YouTube API"}
                
                if attempt == max_retries - 1:
                    return None, {"error": f"Error fetching transcript: {str(e)}"}
        
        return None, {"error": "Failed to fetch transcript after all retry attempts"}
    
    def process_transcript(self, transcript: str, video_id: str) -> List[Document]:
        """Split transcript into chunks and create documents"""
        if not transcript or not transcript.strip():
            return []
        
        chunks = self.splitter.split_text(transcript)
        
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Only add non-empty chunks
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "video_id": video_id,
                        "chunk_id": i,
                        "source": f"YouTube Video {video_id}"
                    }
                )
                documents.append(doc)
        
        return documents
