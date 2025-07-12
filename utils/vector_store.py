from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from typing import List, Optional
import streamlit as st

class VectorStoreManager:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> bool:
        """Create FAISS vector store from documents"""
        try:
            if not documents:
                st.error("No documents provided for vector store creation")
                return False
            
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            return True
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search"""
        if not self.vector_store:
            return []
        
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            st.error(f"Error in similarity search: {str(e)}")
            return []
    
    def get_retriever(self, k: int = 4):
        """Get retriever for the vector store"""
        if not self.vector_store:
            return None
        
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
