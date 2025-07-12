import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List, Dict, Any
import json

class GeminiHandler:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000,
                top_p=0.8,
                top_k=40
            )
        )
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key
        )
    
    def generate_response(self, prompt: str, context: str) -> str:
        """Generate response using Gemini model"""
        try:
            full_prompt = f"""
            You are TubeGPT, an AI assistant specialized in analyzing YouTube video content.
            
            Context from video transcript:
            {context}
            
            User Question: {prompt}
            
            Instructions:
            - Answer ONLY based on the provided transcript context
            - Be conversational and helpful
            - If the context doesn't contain relevant information, politely say you don't know
            - Provide specific details when available
            - Keep responses concise but informative
            - If you can reference specific parts of the video, do so
            
            Answer:
            """
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Return embeddings instance"""
        return self.embeddings
