"""
Document retrieval functionality using FAISS vector store
"""
import os
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class DocumentRetriever:
    """
    Retrieves relevant documents based on query embeddings
    using FAISS vector store for efficient similarity search
    """
    
    def __init__(self, index_path=None, embeddings_path=None, documents_path=None):
        """
        Initialize the document retriever
        
        Args:
            index_path (str): Path to the FAISS index
            embeddings_path (str): Path to the embeddings
            documents_path (str): Path to the documents
        """
        self.model = SentenceTransformer('microsoft/codebert-base')
        self.index = None
        self.documents = []
        
        # Load index and documents if paths are provided
        if index_path and os.path.exists(index_path) and documents_path and os.path.exists(documents_path):
            self.load_index(index_path)
            self.load_documents(documents_path)
            logging.info("Document retriever initialized with existing index and documents")
        else:
            logging.info("Document retriever initialized without index")
    
    def create_index(self, documents, save_path=None):
        """
        Create a FAISS index from documents
        
        Args:
            documents (list): List of document strings
            save_path (str): Path to save the index (optional)
            
        Returns:
            bool: Success status
        """
        try:
            # Store documents
            self.documents = documents
            
            # Generate embeddings
            embeddings = self.generate_embeddings(documents)
            
            # Create and train FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            
            # Save index if path provided
            if save_path:
                faiss.write_index(self.index, save_path)
                logging.info(f"FAISS index saved to {save_path}")
            
            return True
        except Exception as e:
            logging.error(f"Error creating index: {str(e)}")
            return False
    
    def load_index(self, index_path):
        """
        Load a FAISS index from file
        
        Args:
            index_path (str): Path to the FAISS index
            
        Returns:
            bool: Success status
        """
        try:
            self.index = faiss.read_index(index_path)
            logging.info(f"FAISS index loaded from {index_path}")
            return True
        except Exception as e:
            logging.error(f"Error loading index: {str(e)}")
            return False
    
    def load_documents(self, documents_path):
        """
        Load documents from file
        
        Args:
            documents_path (str): Path to the documents file
            
        Returns:
            bool: Success status
        """
        try:
            with open(documents_path, 'r', encoding='utf-8') as f:
                self.documents = f.readlines()
            logging.info(f"Documents loaded from {documents_path}")
            return True
        except Exception as e:
            logging.error(f"Error loading documents: {str(e)}")
            return False
    
    def generate_embeddings(self, texts):
        """
        Generate embeddings for a list of texts
        
        Args:
            texts (list): List of text strings
            
        Returns:
            numpy.ndarray: Text embeddings
        """
        embeddings = self.model.encode(texts)
        return np.array(embeddings).astype('float32')
    
    def retrieve(self, query, k=3):
        """
        Retrieve the top-k most relevant documents for a query
        
        Args:
            query (str): The query text
            k (int): Number of documents to retrieve
            
        Returns:
            list: List of retrieved documents
        """
        if not self.index:
            logging.error("FAISS index not initialized")
            return []
        
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])
        
        # Perform search
        distances, indices = self.index.search(query_embedding, k)
        
        # Get the corresponding documents
        retrieved_docs = [self.documents[idx] for idx in indices[0]]
        
        return retrieved_docs 