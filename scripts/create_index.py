#!/usr/bin/env python
"""
Script to process raw business strategy documents and create FAISS index
"""
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skillmentor.core import SkillMentor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """
    Main function to create the index
    """
    # Paths
    raw_data_path = 'data/raw/sample_strategies.txt'
    index_path = 'data/processed/faiss_index.bin'
    documents_path = 'data/processed/documents.txt'
    
    # Create directories if they don't exist
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialize SkillMentor app
    app = SkillMentor()
    
    # Load raw documents
    try:
        with open(raw_data_path, 'r', encoding='utf-8') as f:
            documents = f.read().split('\n\n')
        logging.info(f"Loaded {len(documents)} documents from {raw_data_path}")
    except FileNotFoundError:
        logging.error(f"File not found: {raw_data_path}")
        return 1
    except Exception as e:
        logging.error(f"Error loading documents: {str(e)}")
        return 1
    
    # Create index
    logging.info("Creating index...")
    success = app.initialize_dataset(
        documents=documents,
        save_index_path=index_path,
        save_documents_path=documents_path
    )
    
    if success:
        logging.info(f"Index successfully created and saved to {index_path}")
        logging.info(f"Documents saved to {documents_path}")
        return 0
    else:
        logging.error("Failed to create index")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 