import streamlit as st
import google.generativeai as genai
import yt_dlp
import tempfile
import os
import re
import json
import time
import random
from typing import List, Tuple
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

class GeminiTubeGPT:
    def __init__(self):
        self.transcript = None
        self.video_id = None
        self.model = None
        self.chunks = []
        self.video_title = None
        self.last_request_time = 0
        
    def setup_gemini(self, api_key: str) -> bool:
        """Setup Gemini API"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,
                }
            )
            return True
        except Exception as e:
            st.error(f"Error setting up Gemini: {str(e)}")
            return False
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        if len(url) == 11 and url.replace('-', '').replace('_', '').isalnum():
            return url
            
        return None
    
    def get_transcript(self, video_id: str) -> Tuple[str, bool]:
        """Enhanced transcript fetching with multiple reliable methods"""
        
        # Method 1: Try yt-dlp first (most reliable against blocking)
        transcript, success = self._get_transcript_ytdlp(video_id)
        if success and transcript.strip():
            return transcript, True
        
        # Method 2: Try original API with enhanced rate limiting
        transcript, success = self._get_transcript_original_enhanced(video_id)
        if success and transcript.strip():
            return transcript, True
        
        # Method 3: Try alternative yt-dlp configuration
        transcript, success = self._get_transcript_ytdlp_alternative(video_id)
        if success and transcript.strip():
            return transcript, True
        
        return "All transcript methods failed. Please try a different video or check if captions are available.", False
    
    def _get_transcript_ytdlp(self, video_id: str) -> Tuple[str, bool]:
        """Primary method using yt-dlp for subtitle extraction"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {
                    'writeautomaticsub': True,
                    'writesubtitles': True,
                    'subtitleslangs': ['en', 'en-US', 'en-GB'],
                    'subtitlesformat': 'vtt',
                    'skip_download': True,
                    'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        # Extract info and download subtitles
                        info = ydl.extract_info(url, download=False)
                        ydl.download([url])
                        
                        # Look for subtitle files
                        for file in os.listdir(temp_dir):
                            if file.endswith(('.vtt', '.srt')):
                                file_path = os.path.join(temp_dir, file)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    transcript = self._clean_subtitle_content(content)
                                    if transcript.strip():
                                        return transcript, True
                    except Exception as e:
                        pass
                        
            return "No subtitles found with yt-dlp", False
            
        except Exception as e:
            return f"yt-dlp error: {str(e)}", False
    
    def _get_transcript_ytdlp_alternative(self, video_id: str) -> Tuple[str, bool]:
        """Alternative yt-dlp configuration"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            ydl_opts = {
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'best',
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    
                    # Check if subtitles are available in the info
                    if 'subtitles' in info:
                        for lang in ['en', 'en-US', 'en-GB']:
                            if lang in info['subtitles']:
                                subtitle_url = info['subtitles'][lang][0]['url']
                                # You could fetch and parse this URL
                                return "Subtitles available but need URL parsing", False
                    
                    if 'automatic_captions' in info:
                        for lang in ['en', 'en-US', 'en-GB']:
                            if lang in info['automatic_captions']:
                                return "Auto captions available but need URL parsing", False
                                
                except Exception:
                    pass
                    
            return "Alternative yt-dlp method failed", False
            
        except Exception as e:
            return f"Alternative yt-dlp error: {str(e)}", False
    
    def _get_transcript_original_enhanced(self, video_id: str) -> Tuple[str, bool]:
        """Enhanced original method with better rate limiting"""
        try:
            # Enhanced rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < 5:  # Increased to 5 seconds
                wait_time = 5 + random.uniform(2, 5)  # 7-10 second delay
                time.sleep(wait_time)
            
            self.last_request_time = time.time()
            
            # Try multiple language configurations
            language_attempts = [
                ["en"],
                ["en-US"],
                ["en-GB"],
                ["en", "en-US", "en-GB"],
            ]
            
            for languages in language_attempts:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
                    transcript = " ".join(chunk["text"] for chunk in transcript_list)
                    if transcript.strip():
                        return transcript, True
                except TranscriptsDisabled:
                    continue
                except Exception as e:
                    if "blocked" in str(e).lower():
                        break  # Don't continue if blocked
                    continue
            
            # Final attempt without language specification
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join(chunk["text"] for chunk in transcript_list)
                return transcript, True
            except Exception as e:
                error_msg = str(e)
                if "blocked" in error_msg.lower() or "ip" in error_msg.lower():
                    return "YouTube API temporarily blocked. Trying alternative methods...", False
                return f"Original API error: {error_msg}", False
                
        except Exception as e:
            return f"Enhanced original method error: {str(e)}", False
    
    def _clean_subtitle_content(self, content: str) -> str:
        """Clean VTT/SRT subtitle content to plain text"""
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip VTT headers, timestamps, and sequence numbers
            if (line and 
                not line.startswith('WEBVTT') and
                not line.startswith('NOTE') and
                not '-->' in line and
                not line.isdigit() and
                not line.startswith('<') and
                not line.endswith('>') and
                line != ''):
                text_lines.append(line)
        
        return ' '.join(text_lines)
    
    def chunk_transcript(self, transcript: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split transcript into chunks for better processing"""
        chunks = []
        start = 0
        
        while start < len(transcript):
            end = start + chunk_size
            
            if end < len(transcript):
                # Try to break at sentence boundaries
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if transcript[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = transcript[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def find_relevant_chunks(self, question: str, chunks: List[str], max_chunks: int = 4) -> List[str]:
        """Find most relevant chunks using Gemini for semantic similarity"""
        if not chunks:
            return []
        
        try:
            # Limit chunks to prevent token overflow
            chunks_to_analyze = chunks[:6]  # Further reduced for reliability
            
            relevance_prompt = f"""
            Given this question: "{question}"
            
            Rate the relevance of each text chunk below on a scale of 1-10, where 10 is most relevant.
            Return only a JSON array of scores, one for each chunk.
            
            Chunks:
            {json.dumps(chunks_to_analyze)}
            """
            
            response = self.model.generate_content(relevance_prompt)
            
            try:
                # Enhanced response cleaning
                response_text = response.text.strip()
                
                # Remove markdown formatting
                if response_text.startswith("```"):
                    parts = response_text.split("```")
                    if len(parts) >= 2:
                        response_text = parts[1]
                
                # Remove 'json' prefix if present
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()
                
                # Try to parse JSON
                scores = json.loads(response_text)
                if isinstance(scores, list) and len(scores) == len(chunks_to_analyze):
                    chunk_scores = list(zip(chunks_to_analyze, scores))
                    chunk_scores.sort(key=lambda x: x[1], reverse=True)  # Fixed sorting key
                    return [chunk for chunk, score in chunk_scores[:max_chunks]]
                    
            except json.JSONDecodeError:
                # Enhanced fallback: try to extract numbers from response
                try:
                    import re
                    numbers = re.findall(r'\d+', response_text)
                    if len(numbers) == len(chunks_to_analyze):
                        scores = [int(n) for n in numbers]
                        chunk_scores = list(zip(chunks_to_analyze, scores))
                        chunk_scores.sort(key=lambda x: x[1], reverse=True)
                        return [chunk for chunk, score in chunk_scores[:max_chunks]]
                except:
                    pass
            
            # Final fallback: return first chunks
            return chunks_to_analyze[:max_chunks]
            
        except Exception as e:
            st.error(f"Error finding relevant chunks: {str(e)}")
            return chunks[:max_chunks]
    
    def answer_question(self, question: str) -> str:
        """Answer question using Gemini with relevant transcript chunks"""
        if not self.transcript or not self.model:
            return "Please load a video first and ensure Gemini is configured."
        
        try:
            relevant_chunks = self.find_relevant_chunks(question, self.chunks)
            context = "\n\n".join(relevant_chunks)
            
            prompt = f"""
            You are TubeGPT, a helpful AI assistant that answers questions about YouTube videos.
            Answer ONLY from the provided transcript context below.
            If the context is insufficient to answer the question, say you don't know.
            Be conversational, helpful, and provide specific details from the transcript when possible.
            
            Context from video transcript:
            {context}
            
            Question: {question}
            
            Please provide a clear, helpful answer based only on the information in the transcript:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def generate_summary(self) -> str:
        """Generate a comprehensive summary of the video"""
        if not self.transcript or not self.model:
            return "Please load a video first."
        
        try:
            # Use more chunks for better summary
            summary_context = "\n\n".join(self.chunks[:8])
            
            prompt = f"""
            Create a comprehensive summary of this YouTube video based on the transcript below.
            Include:
            1. Main topic/theme
            2. Key points discussed
            3. Important people or entities mentioned
            4. Any conclusions or takeaways
            
            Transcript:
            {summary_context}
            
            Summary:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
