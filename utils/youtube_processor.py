from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import re
from typing import List, Optional, Tuple

class YouTubeProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[dict]]:
        """Get transcript from YouTube video"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=["en", "en-US", "en-GB"]
            )
            
            # Create full transcript text
            transcript_text = " ".join([chunk["text"] for chunk in transcript_list])
            
            # Create metadata
            metadata = {
                "video_id": video_id,
                "total_chunks": len(transcript_list),
                "total_length": len(transcript_text)
            }
            
            return transcript_text, metadata
            
        except TranscriptsDisabled:
            return None, {"error": "No captions available for this video"}
        except Exception as e:
            return None, {"error": f"Error fetching transcript: {str(e)}"}
    
    def process_transcript(self, transcript: str, video_id: str) -> List[Document]:
        """Split transcript into chunks and create documents"""
        chunks = self.splitter.split_text(transcript)
        
        documents = []
        for i, chunk in enumerate(chunks):
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
