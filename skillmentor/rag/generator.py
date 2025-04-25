"""
Advice generation module using LangChain and LLMs
"""
import os
import logging
from langchain import PromptTemplate
from langchain.llms import HuggingFacePipeline
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

class AdviceGenerator:
    """
    Generates tailored business advice using LLM and retrieved context
    """
    
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf", device="cpu"):
        """
        Initialize the advice generator with specified LLM model
        
        Args:
            model_name (str): HF model name or path to local model
            device (str): Device to run the model on (cpu or cuda)
        """
        self.model_name = model_name
        self.device = device
        self.llm = None
        self.initialize_llm()
        
        # Define the prompt template
        self.template = """
        You are SkillMentor, an AI business advisor for micro-entrepreneurs in underserved communities.
        Your goal is to provide actionable, sustainable business advice.
        
        USER QUERY: {query}
        
        RELEVANT CONTEXT:
        {context}
        
        Provide a concise, practical response that:
        1. Directly addresses the user's question
        2. Incorporates sustainable business practices
        3. Is actionable with limited resources
        4. Considers local context and constraints
        
        YOUR ADVICE:
        """
        
        self.prompt_template = PromptTemplate(
            input_variables=["query", "context"],
            template=self.template
        )
        
        logging.info(f"AdviceGenerator initialized with model {model_name}")
    
    def initialize_llm(self):
        """
        Initialize the LLM pipeline
        
        Returns:
            bool: Success status
        """
        try:
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=self.device,
                load_in_8bit=True if self.device == "cuda" else False
            )
            
            # Create text generation pipeline
            text_generation_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            # Create LangChain HF pipeline
            self.llm = HuggingFacePipeline(pipeline=text_generation_pipeline)
            
            return True
        except Exception as e:
            logging.error(f"Error initializing LLM: {str(e)}")
            # Fallback to a dummy generator for testing purposes
            self.llm = None
            return False
    
    def generate_advice(self, query, context):
        """
        Generate advice based on user query and retrieved context
        
        Args:
            query (str): User's business query
            context (list): List of retrieved relevant documents
            
        Returns:
            str: Generated business advice
        """
        if not self.llm:
            logging.warning("LLM not initialized, using fallback response")
            return self._generate_fallback_advice(query, context)
        
        try:
            # Format context as a single string
            context_text = "\n".join(context)
            
            # Create the prompt
            prompt = self.prompt_template.format(
                query=query,
                context=context_text
            )
            
            # Generate response
            response = self.llm(prompt)
            
            # Extract the advice part
            advice = response.split("YOUR ADVICE:")[1].strip() if "YOUR ADVICE:" in response else response
            
            return advice
        except Exception as e:
            logging.error(f"Error generating advice: {str(e)}")
            return self._generate_fallback_advice(query, context)
    
    def _generate_fallback_advice(self, query, context):
        """
        Generate a fallback response when LLM is not available
        
        Args:
            query (str): User's business query
            context (list): List of retrieved relevant documents
            
        Returns:
            str: Fallback business advice
        """
        # Simple rule-based fallback response
        if "price" in query.lower() or "pricing" in query.lower():
            return "To price your products effectively, consider your material costs, labor time, and a reasonable profit margin. Research what similar products sell for in your local market and adjust accordingly."
        
        elif "marketing" in query.lower() or "sell" in query.lower():
            return "Focus on highlighting the unique features of your products. Start with local markets and use word-of-mouth marketing. Consider collaborating with other local businesses for cross-promotion."
        
        elif "sustain" in query.lower() or "environment" in query.lower():
            return "Adopt sustainable practices like using local materials, minimizing waste, and reusing resources when possible. This can both reduce costs and appeal to environmentally conscious customers."
        
        else:
            return "Start by identifying your business strengths and the specific needs of your local community. Focus on delivering quality products or services consistently, and gradually expand your offerings based on customer feedback." 