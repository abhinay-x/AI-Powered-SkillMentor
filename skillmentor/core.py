"""
Core application module that integrates all SkillMentor components
"""
import os
import logging
import time
from skillmentor.nlp.processor import TextProcessor
from skillmentor.rag.retriever import DocumentRetriever
from skillmentor.rag.generator import AdviceGenerator
from skillmentor.viz.dashboard import Dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SkillMentor:
    """
    Main application class that integrates all components
    """
    
    def __init__(self, 
                 index_path=None, 
                 documents_path=None, 
                 model_name="meta-llama/Llama-2-7b-chat-hf",
                 device="cpu"):
        """
        Initialize the SkillMentor application
        
        Args:
            index_path (str): Path to the FAISS index
            documents_path (str): Path to the documents file
            model_name (str): HF model name or path to local model
            device (str): Device to run the model on (cpu or cuda)
        """
        self.text_processor = TextProcessor()
        self.retriever = DocumentRetriever(index_path=index_path, documents_path=documents_path)
        self.generator = AdviceGenerator(model_name=model_name, device=device)
        self.dashboard = Dashboard()
        
        self.metrics = {
            'response_times': [],
            'query_types': {},
            'bleu_scores': {},
            'user_feedback': []
        }
        
        logging.info("SkillMentor application initialized")
    
    def process_query(self, query, source_lang='en'):
        """
        Process a user query and generate advice
        
        Args:
            query (str): User's business query
            source_lang (str): Source language code
            
        Returns:
            dict: Response information
                - original_query: The original query
                - processed_query: The processed query (translated if needed)
                - advice: Generated business advice
                - advice_source_lang: Advice in the source language
                - dashboard_image: Base64 encoded dashboard image
                - response_time: Time taken to generate response
        """
        start_time = time.time()
        
        # Process the input text
        processed_input = self.text_processor.process_input(query, source_lang)
        
        # Retrieve relevant documents
        processed_query = processed_input['processed_text']
        relevant_docs = self.retriever.retrieve(processed_query, k=3)
        
        # Generate advice
        advice = self.generator.generate_advice(processed_query, relevant_docs)
        
        # Translate advice back to source language if needed
        advice_source_lang = advice
        if source_lang != 'en':
            advice_source_lang = self.text_processor.translate_to_source(advice, source_lang)
        
        # Generate dashboard visualization
        dashboard_image = self.dashboard.generate_full_dashboard()
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Update metrics
        self.metrics['response_times'].append(response_time)
        
        # Determine query type for metrics (simple keyword-based classification)
        query_type = self._classify_query(processed_query)
        if query_type in self.metrics['query_types']:
            self.metrics['query_types'][query_type] += 1
        else:
            self.metrics['query_types'][query_type] = 1
        
        # Log the response
        logging.info(f"Generated advice for query type '{query_type}' in {response_time:.2f} seconds")
        
        return {
            'original_query': query,
            'processed_query': processed_query,
            'advice': advice,
            'advice_source_lang': advice_source_lang,
            'dashboard_image': dashboard_image,
            'response_time': response_time
        }
    
    def _classify_query(self, query):
        """
        Simple keyword-based query classification
        
        Args:
            query (str): Processed query text
            
        Returns:
            str: Query type category
        """
        query = query.lower()
        
        if 'price' in query or 'pricing' in query or 'cost' in query:
            return 'Pricing'
        elif 'market' in query or 'sell' in query or 'customer' in query:
            return 'Marketing'
        elif 'sustain' in query or 'environment' in query or 'eco' in query:
            return 'Sustainability'
        elif 'produc' in query or 'make' in query or 'create' in query:
            return 'Production'
        else:
            return 'General'
    
    def record_user_feedback(self, query_id, rating, comments=None):
        """
        Record user feedback on advice quality
        
        Args:
            query_id (str): Unique identifier for the query
            rating (int): Rating from 1-5
            comments (str): Optional user comments
            
        Returns:
            bool: Success status
        """
        self.metrics['user_feedback'].append({
            'query_id': query_id,
            'rating': rating,
            'comments': comments,
            'timestamp': time.time()
        })
        
        logging.info(f"Recorded user feedback for query {query_id}: {rating}/5")
        return True
    
    def get_performance_metrics(self):
        """
        Get application performance metrics
        
        Returns:
            dict: Performance metrics
        """
        if not self.metrics['response_times']:
            return {
                'avg_response_time': 0,
                'num_queries': 0,
                'query_distribution': {},
                'avg_user_rating': 0
            }
        
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        num_queries = len(self.metrics['response_times'])
        
        # Calculate average user rating
        ratings = [feedback['rating'] for feedback in self.metrics['user_feedback']]
        avg_user_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            'avg_response_time': avg_response_time,
            'num_queries': num_queries,
            'query_distribution': self.metrics['query_types'],
            'avg_user_rating': avg_user_rating
        }
    
    def initialize_dataset(self, documents, save_index_path=None, save_documents_path=None):
        """
        Initialize the dataset and create index
        
        Args:
            documents (list): List of document strings
            save_index_path (str): Path to save the FAISS index
            save_documents_path (str): Path to save the documents
            
        Returns:
            bool: Success status
        """
        # Create FAISS index
        success = self.retriever.create_index(documents, save_path=save_index_path)
        
        # Save documents if requested
        if save_documents_path and success:
            try:
                with open(save_documents_path, 'w', encoding='utf-8') as f:
                    for doc in documents:
                        f.write(doc + '\n')
                logging.info(f"Documents saved to {save_documents_path}")
            except Exception as e:
                logging.error(f"Error saving documents: {str(e)}")
                return False
        
        return success 