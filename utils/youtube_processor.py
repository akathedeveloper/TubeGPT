# YouTubeProcessor.py

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import re
from typing import List, Optional, Tuple, Dict


class YouTubeProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        """
        Extract a YouTube video ID from a URL or validate a direct ID.
        Returns the 11‑char ID or None if invalid.
        """
        url_or_id = url_or_id.strip()
        # Direct ID
        if len(url_or_id) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url_or_id):
            return url_or_id

        # URL patterns
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11})",
            r"(?:embed\/)([0-9A-Za-z_-]{11})",
            r"(?:watch\?v=)([0-9A-Za-z_-]{11})",
            r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
            r"(?:youtube\.com\/shorts\/)([0-9A-Za-z_-]{11})"
        ]
        for pattern in patterns:
            m = re.search(pattern, url_or_id)
            if m:
                vid = m.group(1)
                if re.match(r'^[0-9A-Za-z_-]{11}$', vid):
                    return vid
        return None

    def get_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[dict]]:
        """
        Fetch the full transcript text for a given video ID.
        Returns (transcript_text, metadata) or (None, error_dict).
        """
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format"}

        try:
            segments = YouTubeTranscriptApi.get_transcript(video_id)
            # Join only non-empty text segments
            transcript_text = " ".join(seg["text"].strip() for seg in segments if seg["text"].strip())

            metadata = {
                "video_id": video_id,
                "total_segments": len(segments),
                "total_length": len(transcript_text),
                "method": "get_transcript"
            }
            return transcript_text, metadata

        except TranscriptsDisabled:
            return None, {"error": "Transcripts are disabled for this video"}
        except NoTranscriptFound:
            return None, {"error": "No transcript found for this video"}
        except Exception as e:
            return None, {"error": f"Unexpected error: {str(e)}"}

    def process_transcript(self, transcript: str, video_id: str) -> List[Document]:
        """
        Split a raw transcript string into LangChain Document chunks.
        """
        if not transcript or not transcript.strip():
            return []

        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', transcript.strip())
        chunks = self.splitter.split_text(cleaned)

        documents = []
        for idx, chunk in enumerate(chunks):
            if chunk.strip():
                documents.append(Document(
                    page_content=chunk.strip(),
                    metadata={
                        "video_id": video_id,
                        "chunk_id": idx,
                        "source": f"YouTube Video {video_id}"
                    }
                ))
        return documents
