#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('simple_index_builder')

# Check if we have FAISS and SentenceTransformer
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_ADVANCED_DEPS = True
    logger.info("Advanced dependencies found. Using FAISS and SentenceTransformer.")
except ImportError:
    HAS_ADVANCED_DEPS = False
    logger.warning("FAISS or SentenceTransformer not found. Using simple text index.")

def generate_embeddings(texts: List[str], model_name: str = 'paraphrase-MiniLM-L6-v2') -> np.ndarray:
    """
    Generate embeddings for a list of texts using SentenceTransformer.
    
    Args:
        texts: List of text documents
        model_name: Name of the SentenceTransformer model to use
        
    Returns:
        Numpy array of embeddings
    """
    if not HAS_ADVANCED_DEPS:
        # Return random embeddings if we don't have the dependencies
        logger.warning("Generating random embeddings as placeholder")
        return np.random.rand(len(texts), 384).astype(np.float32)
    
    try:
        logger.info(f"Loading model: {model_name}")
        model = SentenceTransformer(model_name)
        logger.info("Generating embeddings")
        embeddings = model.encode(texts, show_progress_bar=True)
        return embeddings.astype(np.float32)
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        # Fallback to random embeddings
        logger.warning("Falling back to random embeddings")
        return np.random.rand(len(texts), 384).astype(np.float32)

def create_index(documents: List[str], index_path: str, docs_path: str) -> bool:
    """
    Create a FAISS index from documents and save it to disk.
    
    Args:
        documents: List of text documents
        index_path: Path to save the FAISS index
        docs_path: Path to save the documents
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Save documents to disk
        with open(docs_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(doc.strip() + '\n---\n')
        logger.info(f"Saved {len(documents)} documents to {docs_path}")
        
        if not HAS_ADVANCED_DEPS:
            logger.info("Skipping FAISS index creation (dependencies not available)")
            return True
            
        # Generate embeddings
        embeddings = generate_embeddings(documents)
        dimension = embeddings.shape[1]
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Save index to disk
        faiss.write_index(index, index_path)
        logger.info(f"Created FAISS index with {len(documents)} documents and saved to {index_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        return False

def load_raw_documents(file_path: str) -> List[str]:
    """
    Load documents from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        List of documents
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split content by section headers
        documents = []
        sections = content.split('# ')
        
        for section in sections:
            if not section.strip():
                continue
                
            # Process each paragraph in the section
            paragraphs = section.strip().split('\n\n')
            section_title = paragraphs[0].strip()
            
            for i, para in enumerate(paragraphs[1:]):
                if para.strip():
                    doc = f"Category: {section_title}\n\n{para.strip()}"
                    documents.append(doc)
        
        return documents
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return []

def main():
    """Main function to create the index."""
    try:
        # Define paths
        raw_path = 'data/raw/sample_strategies.txt'
        processed_dir = 'data/processed'
        index_path = os.path.join(processed_dir, 'faiss_index.bin')
        docs_path = os.path.join(processed_dir, 'documents.txt')
        
        # Create necessary directories
        os.makedirs(processed_dir, exist_ok=True)
        
        # Load documents
        logger.info(f"Loading documents from {raw_path}")
        documents = load_raw_documents(raw_path)
        
        if not documents:
            logger.error("No documents found or error loading documents")
            return False
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Create index
        success = create_index(documents, index_path, docs_path)
        
        if success:
            logger.info("Index creation completed successfully")
            return True
        else:
            logger.error("Index creation failed")
            return False
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 