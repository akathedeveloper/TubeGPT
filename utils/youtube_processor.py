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
        input_text = url_or_id.strip()
        if len(input_text) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', input_text):
            return input_text
        return None

    def get_transcript_data(self, video_id: str) -> Tuple[Optional[list], Optional[dict]]:
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format."}
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            if not transcript_data:
                return None, {"error": "No transcript data received"}
            metadata = {
                "video_id": video_id,
                "total_segments": len(transcript_data),
                "duration": max([seg.get('start', 0) + seg.get('duration', 0) for seg in transcript_data]) if transcript_data else 0,
                "method": "direct_api_call"
            }
            return transcript_data, metadata
        except TranscriptsDisabled:
            return None, {"error": "Transcripts are disabled for this video"}
        except NoTranscriptFound:
            return None, {"error": "No transcript found for this video"}
        except Exception as e:
            return None, {"error": f"Error fetching transcript: {e}"}

    def process_transcript_data(self, transcript_data: List[Dict[str, Any]]) -> str:
        if not transcript_data:
            return ""
        sorted_transcript = sorted(transcript_data, key=lambda x: x.get('start', 0))
        transcript_text = " ".join([
            chunk.get("text", "").strip()
            for chunk in sorted_transcript
            if chunk.get("text", "").strip()
        ])
        return transcript_text

    def process_transcript(self, transcript: str, video_id: str) -> List[Document]:
        if not transcript or not transcript.strip():
            return []
        cleaned_transcript = re.sub(r'\s+', ' ', transcript.strip())
        chunks = self.splitter.split_text(cleaned_transcript)
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
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
