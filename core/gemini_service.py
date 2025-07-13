import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
import json
import time
import random
from typing import List, Tuple

class GeminiTubeGPT:
    def __init__(self):
        self.transcript = None
        self.video_id = None
        self.model = None
        self.chunks = []
        self.video_title = None
        self.last_request_time = 0  # For rate limiting
        
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
        """Enhanced transcript fetching with rate limiting and fallbacks"""
        try:
            # Add rate limiting to prevent IP blocking
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < 3:  # Wait at least 3 seconds between requests
                wait_time = 3 + random.uniform(1, 2)  # Random delay 4-5 seconds
                time.sleep(wait_time)
            
            self.last_request_time = time.time()
            
            # Try multiple language options and methods
            language_options = [
                ["en"],           # English only
                ["en-US"],        # US English
                ["en-GB"],        # UK English
                ["en", "en-US"],  # Multiple English variants
            ]
            
            for languages in language_options:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
                    transcript = " ".join(chunk["text"] for chunk in transcript_list)
                    if transcript.strip():  # Ensure we got actual content
                        return transcript, True
                except TranscriptsDisabled:
                    continue
                except Exception:
                    continue
            
            # Final attempt without language specification (auto-detect)
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join(chunk["text"] for chunk in transcript_list)
                return transcript, True
            except TranscriptsDisabled:
                return "No captions available for this video. Please try a video with captions enabled.", False
            except Exception as e:
                error_msg = str(e)
                if "blocked" in error_msg.lower() or "ip" in error_msg.lower():
                    return "YouTube is temporarily blocking requests. Please wait 10-15 minutes and try again, or try a different video.", False
                return f"Error fetching transcript: {error_msg}", False
                
        except Exception as e:
            return f"Unexpected error: {str(e)}", False
    
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
            chunks_to_analyze = chunks[:8]  # Reduced from 10 to 8
            
            relevance_prompt = f"""
            Given this question: "{question}"
            
            Rate the relevance of each text chunk below on a scale of 1-10, where 10 is most relevant.
            Return only a JSON array of scores, one for each chunk.
            
            Chunks:
            {json.dumps(chunks_to_analyze)}
            """
            
            response = self.model.generate_content(relevance_prompt)
            
            try:
                # Clean response text (remove markdown formatting if present)
                response_text = response.text.strip()
                if response_text.startswith("```
                    response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                
                scores = json.loads(response_text)
                if isinstance(scores, list) and len(scores) == len(chunks_to_analyze):
                    chunk_scores = list(zip(chunks_to_analyze, scores))
                    chunk_scores.sort(key=lambda x: x[1], reverse=True)
                    return [chunk for chunk, score in chunk_scores[:max_chunks]]
            except json.JSONDecodeError:
                # Fallback: return first chunks if JSON parsing fails
                pass
            
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
