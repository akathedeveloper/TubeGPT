from youtube_transcript_api import YouTubeTranscriptApi
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

        if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
            return url

        return None

    def get_all_available_transcripts(self, video_id: str) -> List[dict]:
        """Get all available transcript languages and types"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_transcripts = []

            for transcript in transcript_list:
                available_transcripts.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable,
                    'transcript_obj': transcript
                })

            return available_transcripts
        except Exception as e:
            print(f"[Error] Failed to list transcripts for video {video_id}: {e}")
            return []

    def get_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[dict]]:
        """Get transcript with fallback strategy: manual > auto > translated > any"""
        if not video_id or len(video_id) != 11:
            return None, {"error": "Invalid video ID format"}

        available_transcripts = self.get_all_available_transcripts(video_id)
        if not available_transcripts:
            return None, {"error": "No transcripts available for this video"}

        language_priorities = [
            'en', 'en-US', 'en-GB', 'en-CA', 'en-AU',
            'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'
        ]

        def try_fetch(transcript_info, method_label, translated=False):
            try:
                if translated:
                    transcript_data = transcript_info['transcript_obj'].translate('en').fetch()
                else:
                    transcript_data = transcript_info['transcript_obj'].fetch()

                transcript_text = " ".join([chunk["text"] for chunk in transcript_data])

                metadata = {
                    "video_id": video_id,
                    "language": "English (Translated)" if translated else transcript_info['language'],
                    "language_code": "en" if translated else transcript_info['language_code'],
                    "is_generated": transcript_info['is_generated'],
                    "total_chunks": len(transcript_data),
                    "total_length": len(transcript_text),
                    "method": method_label
                }

                return transcript_text, metadata
            except Exception as e:
                print(f"[Transcript Error] Method: {method_label}, Lang: {transcript_info['language_code']}, Error: {e}")
                return None, None

        # Manual transcripts
        for lang_code in language_priorities:
            for t in [t for t in available_transcripts if not t['is_generated']]:
                if t['language_code'].startswith(lang_code):
                    transcript, meta = try_fetch(t, "manual_transcript")
                    if transcript:
                        return transcript, meta

        # Auto-generated
        for lang_code in language_priorities:
            for t in [t for t in available_transcripts if t['is_generated']]:
                if t['language_code'].startswith(lang_code):
                    transcript, meta = try_fetch(t, "auto_generated")
                    if transcript:
                        return transcript, meta

        # Translated transcripts
        for t in available_transcripts:
            if t['is_translatable']:
                transcript, meta = try_fetch(t, "translated", translated=True)
                if transcript:
                    return transcript, meta

        # Any available transcript (fallback)
        for t in available_transcripts:
            transcript, meta = try_fetch(t, "fallback")
            if transcript:
                return transcript, meta

        # Nothing worked
        return None, {
            "error": "Failed to fetch any available transcript",
            "available_languages": [t['language_code'] for t in available_transcripts]
        }

    def process_transcript(self, transcript: str, video_id: str) -> List[Document]:
        """Split transcript into chunks and create documents"""
        if not transcript or not transcript.strip():
            return []

        chunks = self.splitter.split_text(transcript)

        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "video_id": video_id,
                        "chunk_id": i,
                        "source": f"YouTube Video {video_id}"
                    }
                ))

        return documents
