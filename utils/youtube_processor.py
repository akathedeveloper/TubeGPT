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
    
    def get_all_available_transcripts(self, video_id: str) -> List[dict]:
        """Get all available transcript languages and types"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_transcripts = []
            
            for transcript in transcript_list:
                transcript_info = {
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable,
                    'transcript_obj': transcript
                }
                available_transcripts.append(transcript_info)
            
            return available_transcripts
        except Exception:
            return []
    
    def get_transcript(self, video_id: str, max_retries: int = 3) -> Tuple[Optional[str], Optional[dict]]:
        """Get transcript with comprehensive fallback methods"""
        
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format"}
        
        # Get all available transcripts
        available_transcripts = self.get_all_available_transcripts(video_id)
        
        if not available_transcripts:
            return None, {"error": "No transcripts available for this video"}
        
        # Priority order for transcript selection
        language_priorities = [
            'en', 'en-US', 'en-GB', 'en-CA', 'en-AU',  # English variants
            'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'  # Other major languages
        ]
        
        # Try manual transcripts first (higher quality)
        manual_transcripts = [t for t in available_transcripts if not t['is_generated']]
        for lang_code in language_priorities:
            for transcript_info in manual_transcripts:
                if transcript_info['language_code'].startswith(lang_code):
                    try:
                        transcript_data = transcript_info['transcript_obj'].fetch()
                        transcript_text = " ".join([chunk["text"] for chunk in transcript_data])
                        
                        metadata = {
                            "video_id": video_id,
                            "language": transcript_info['language'],
                            "language_code": transcript_info['language_code'],
                            "is_generated": False,
                            "total_chunks": len(transcript_data),
                            "total_length": len(transcript_text),
                            "method": "manual_transcript"
                        }
                        
                        return transcript_text, metadata
                    except Exception:
                        continue
        
        # Try auto-generated transcripts
        auto_transcripts = [t for t in available_transcripts if t['is_generated']]
        for lang_code in language_priorities:
            for transcript_info in auto_transcripts:
                if transcript_info['language_code'].startswith(lang_code):
                    try:
                        transcript_data = transcript_info['transcript_obj'].fetch()
                        transcript_text = " ".join([chunk["text"] for chunk in transcript_data])
                        
                        metadata = {
                            "video_id": video_id,
                            "language": transcript_info['language'],
                            "language_code": transcript_info['language_code'],
                            "is_generated": True,
                            "total_chunks": len(transcript_data),
                            "total_length": len(transcript_text),
                            "method": "auto_generated"
                        }
                        
                        return transcript_text, metadata
                    except Exception:
                        continue
        
        # Try translation if available
        for transcript_info in available_transcripts:
            if transcript_info['is_translatable']:
                try:
                    # Try to translate to English
                    translated = transcript_info['transcript_obj'].translate('en')
                    transcript_data = translated.fetch()
                    transcript_text = " ".join([chunk["text"] for chunk in transcript_data])
                    
                    metadata = {
                        "video_id": video_id,
                        "language": "English (Translated)",
                        "language_code": "en",
                        "is_generated": True,
                        "original_language": transcript_info['language'],
                        "total_chunks": len(transcript_data),
                        "total_length": len(transcript_text),
                        "method": "translated"
                    }
                    
                    return transcript_text, metadata
                except Exception:
                    continue
        
        # Use any available transcript as last resort
        for transcript_info in available_transcripts:
            try:
                transcript_data = transcript_info['transcript_obj'].fetch()
                transcript_text = " ".join([chunk["text"] for chunk in transcript_data])
                
                metadata = {
                    "video_id": video_id,
                    "language": transcript_info['language'],
                    "language_code": transcript_info['language_code'],
                    "is_generated": transcript_info['is_generated'],
                    "total_chunks": len(transcript_data),
                    "total_length": len(transcript_text),
                    "method": "fallback"
                }
                
                return transcript_text, metadata
            except Exception:
                continue
        
        return None, {"error": "Failed to fetch any available transcript"}
    
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
