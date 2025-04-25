#!/usr/bin/env python
"""
Test script for SkillMentor core functionality
"""
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skillmentor.core import SkillMentor
from skillmentor.nlp.processor import TextProcessor
from skillmentor.rag.retriever import DocumentRetriever
from skillmentor.rag.generator import AdviceGenerator
from skillmentor.viz.dashboard import Dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_text_processor():
    """Test the text processor functionality"""
    logging.info("Testing TextProcessor...")
    processor = TextProcessor()
    
    # Test English text
    english_query = "How should I price my handmade wooden crafts?"
    result_en = processor.process_input(english_query, 'en')
    logging.info(f"English tokens: {result_en['tokens']}")
    
    # Test simulated Hindi text (using English for demo)
    hindi_query = "How should I price my handmade wooden crafts? (Pretending this is Hindi)"
    result_hi = processor.process_input(hindi_query, 'hi')
    logging.info(f"'Hindi' processed text: {result_hi['processed_text']}")
    
    return True

def test_document_retriever():
    """Test the document retriever functionality"""
    logging.info("Testing DocumentRetriever...")
    
    # Create sample documents
    documents = [
        "Price your products by calculating materials, labor, and profit margin.",
        "Source materials locally to reduce carbon footprint.",
        "Market your products through community events and word-of-mouth.",
        "Plan for seasonal income fluctuations by saving during high seasons."
    ]
    
    # Create retriever and index
    retriever = DocumentRetriever()
    retriever.create_index(documents)
    
    # Test retrieval
    query = "How should I price my products?"
    results = retriever.retrieve(query, k=2)
    
    logging.info(f"Query: {query}")
    for i, doc in enumerate(results):
        logging.info(f"Result {i+1}: {doc}")
    
    return True

def test_advice_generator():
    """Test the advice generator functionality"""
    logging.info("Testing AdviceGenerator...")
    
    # The LLM won't be initialized in test mode, so this will use the fallback
    generator = AdviceGenerator()
    
    query = "How should I price my handmade furniture?"
    context = [
        "Price your products by calculating the cost of materials and labor, then add a profit margin.",
        "Research local market rates and avoid undercutting, as this devalues craftsmanship."
    ]
    
    advice = generator.generate_advice(query, context)
    logging.info(f"Query: {query}")
    logging.info(f"Advice: {advice}")
    
    return True

def test_dashboard():
    """Test the dashboard visualization functionality"""
    logging.info("Testing Dashboard generation...")
    
    dashboard = Dashboard()
    
    # Generate sample dashboard components
    profit_trend = dashboard.generate_profit_trend()
    cost_revenue = dashboard.generate_cost_revenue_comparison()
    bleu_chart = dashboard.generate_bleu_score_chart()
    
    logging.info("Generated dashboard visualizations successfully")
    
    return True

def test_full_pipeline():
    """Test the complete SkillMentor pipeline"""
    logging.info("Testing full SkillMentor pipeline...")
    
    # Initialize with sample documents
    app = SkillMentor()
    
    # Create sample documents and index
    documents = [
        "Price your products by calculating materials, labor, and profit margin.",
        "Source materials locally to reduce carbon footprint.",
        "Market your products through community events and word-of-mouth.",
        "Plan for seasonal income fluctuations by saving during high seasons."
    ]
    
    # Initialize dataset
    app.initialize_dataset(documents)
    
    # Process a query
    query = "How should I price my wooden chairs?"
    result = app.process_query(query)
    
    logging.info(f"Query: {query}")
    logging.info(f"Advice: {result['advice']}")
    logging.info(f"Response time: {result['response_time']:.2f} seconds")
    
    return True

def main():
    """Run all tests"""
    tests = [
        test_text_processor,
        test_document_retriever,
        test_advice_generator,
        test_dashboard,
        test_full_pipeline
    ]
    
    success = True
    for test in tests:
        try:
            test_success = test()
            if not test_success:
                success = False
                logging.error(f"Test {test.__name__} failed")
        except Exception as e:
            success = False
            logging.error(f"Test {test.__name__} raised an exception: {str(e)}")
    
    if success:
        logging.info("All tests completed successfully!")
        return 0
    else:
        logging.error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 