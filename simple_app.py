"""
SkillMentor Flask Web Application (Simplified Version)
"""
import os
import logging
import random
import io
import base64
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, jsonify, session
from datetime import datetime
import re
import hashlib
import string
import uuid
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-dev-key')

# Expanded business strategies database with more detailed advice
storage = {
    'advice_requests': [],
    'business_strategies': {
        'pricing': [
            "Calculate your base price using the formula: (Material Cost + Labor Cost) × (1 + Profit Margin). For artisan products, aim for a 30-50% margin to reflect your craftsmanship value.",
            "Implement tiered pricing strategies based on product complexity and quality levels. Offer entry-level products alongside premium versions to attract different customer segments.",
            "Research local market rates carefully and position your pricing slightly above competitors if your quality justifies it. Undercutting devalues your craftsmanship and creates unsustainable expectations.",
            "Consider seasonal pricing adjustments - slightly higher during peak demand periods and promotional discounts during slower periods to maintain cash flow.",
            "Calculate your hourly labor rate realistically by tracking all production time (including preparation and finishing) and factor in your skill level and experience.",
            "Price your products to reflect the unique value of handmade items. Remember that customers seeking artisanal goods are often willing to pay premium prices for quality and authenticity.",
            "Use psychological pricing techniques such as charm pricing (ending prices with .95 or .99) for lower-cost items and round pricing for premium products to signal quality.",
            "Create a clear pricing structure that accounts for different sizes, materials, complexity levels, and customization options to maintain consistent profit margins.",
            "Consider using cost-plus pricing for standard items and value-based pricing for unique signature pieces, ensuring your most distinctive work commands appropriate prices."
        ],
        'marketing': [
            "Build personal connections through storytelling - document your production process with photos and share the cultural significance of your craft on product tags and brochures.",
            "Create a 'Customer Referral Program' offering small discounts or bonus items when existing customers bring new customers to you, leveraging word-of-mouth marketing.",
            "Collaborate with complementary local businesses for cross-promotion. For example, if you make food products, partner with local restaurants to showcase your items.",
            "Create simple yet professional product displays using locally available materials that reflect your brand aesthetic. Good presentation increases perceived value.",
            "Host small workshops teaching basic skills related to your craft. This builds community connections, positions you as an expert, and creates additional income streams.",
            "Develop a signature style or technique that makes your products instantly recognizable. This becomes your visual brand identity in the marketplace.",
            "Participate in local markets, fairs, and community events where your target customers gather. Direct selling builds trust and provides immediate customer feedback.",
            "Create a simple brochure or catalog that tells your story and showcases your products with high-quality photographs. Even a well-designed single page can be effective.",
            "Collect testimonials from satisfied customers and display them prominently at your point of sale. Customer stories are powerful endorsements for potential buyers."
        ],
        'sustainability': [
            "Source raw materials within a 50km radius where possible to minimize transportation emissions and support the local economy. Document this journey as part of your brand story.",
            "Implement a closed-loop production system: identify your waste streams and find creative ways to upcycle them into additional products or return them to production.",
            "Conserve energy by planning production activities around natural daylight hours and grouping energy-intensive tasks to minimize equipment startup/shutdown cycles.",
            "Create a product take-back program where customers can return packaging or worn-out products for recycling or upcycling, building brand loyalty while reducing waste.",
            "Develop relationships with sustainable suppliers who align with your values. Verify their practices through site visits when possible and highlight these partnerships in your marketing.",
            "Use natural water capture and storage systems like rain barrels for non-potable production needs such as cleaning equipment or watering gardens that provide materials.",
            "Switch to biodegradable or compostable packaging made from locally available materials - banana leaves, recycled paper, or cloth bags often cost less than plastic alternatives.",
            "Calculate the carbon footprint of your production process and identify the highest impact areas. Often small changes like equipment maintenance can significantly reduce emissions.",
            "Join or create a local artisan cooperative to share resources, reduce individual costs, and decrease the overall environmental impact of your production processes."
        ],
        'production': [
            "Map your entire production process step-by-step and identify bottlenecks. Often, reorganizing your workspace to minimize movement between stations can increase productivity by 15-20%.",
            "Create detailed quality control checklists for each product type based on the best examples in your region. Train yourself to evaluate items objectively against these standards.",
            "Invest in multi-purpose tools rather than specialized equipment when starting out. The ideal tools can perform 2-3 different functions while maintaining quality.",
            "Schedule batch production days focused on similar products to minimize setup/cleanup time and take advantage of workflow efficiencies.",
            "Document your production methods (photos/video if possible) to create standardized processes. This ensures consistent quality and makes it easier to train others if you expand.",
            "Develop a simple inventory management system for materials using minimal technology - a whiteboard or notebook with clear reorder points prevents production delays.",
            "Create templates or jigs for repetitive tasks to increase consistency and speed without sacrificing quality. Even simple guides can dramatically improve efficiency.",
            "Learn to identify and eliminate the 7 wastes in production: transport, inventory, motion, waiting, overproduction, overprocessing, and defects.",
            "Protect your health by establishing proper ergonomics in your workspace - correct table heights, adequate lighting, and scheduled breaks prevent injuries and maintain productivity."
        ],
        'general': [
            "Build a simple inventory management system using color-coded cards or a notebook to track stock levels. Set reorder points for materials to avoid production delays.",
            "Diversify your product offerings around core skill sets to create multiple income streams throughout the year. Consider seasonal product variations and complementary items.",
            "Maintain detailed records of customer preferences and purchase history, even if just in a notebook. This allows for personalized follow-up and helps identify your most profitable products.",
            "Invest time in learning basic business numeracy - understanding profit margins, break-even points, and simple cash flow projections will significantly improve decision-making.",
            "Create a business continuity plan addressing common risks in your area (weather events, supply chain disruptions, etc.). Having backup suppliers and emergency funds reduces vulnerability.",
            "Separate business and personal finances completely, even if just using dedicated jars or envelopes. This clarity is essential for understanding true business performance.",
            "Develop a monthly cash flow planning system that accounts for seasonal variations in both income and expenses. This prevents financial stress during predictable slow periods.",
            "Build relationships with other micro-entrepreneurs to share knowledge and resources. These networks often lead to new business opportunities and emotional support.",
            "Allocate specific time blocks for production, business management, and creative development. Without this structure, administrative tasks often get neglected."
        ]
    },
    'user_feedback': [],
    'previous_advice': {}  # Track previous advice to avoid repetition
}

# AI-like response templates for more varied outputs
response_templates = [
    "Based on my analysis of successful micro-entrepreneurs in your sector, {advice} This approach has shown a 30% increase in customer retention for similar businesses.",
    "I've examined sustainable business practices for your situation, and recommend: {advice} This strategy aligns with both profitability and environmental responsibility.",
    "Looking at your specific question, the most effective approach would be to {advice} Many artisans have found this method particularly successful in similar market conditions.",
    "After analyzing various business models for your context, I recommend: {advice} This strategy balances immediate practicality with long-term sustainability.",
    "My analysis suggests that your priority should be to {advice} This targeted approach addresses your specific challenge while supporting overall business growth.",
    "From studying successful entrepreneurs with similar challenges, I recommend you {advice} This method has consistently shown positive results in resource-constrained environments.",
    "The data indicates that your best strategy would be to {advice} This approach maximizes impact while minimizing resource investment - crucial for micro-enterprises.",
    "My recommendation based on market research is to {advice} This creates a meaningful competitive advantage that doesn't require significant capital investment.",
    "For your specific situation, the optimal approach is to {advice} This strategy addresses both immediate needs and long-term sustainability considerations.",
    "According to my analysis of successful business models in your sector, you should {advice} This approach has been validated through multiple case studies in similar markets."
]

# Business-specific advice for different sectors
business_specific_advice = {
    "woodworking": [
        "For your woodworking business, highlight the sustainable sourcing of your timber and the durability of your products as key selling points.",
        "As a woodworker, consider offering repair services alongside new products to create recurring revenue and strengthen customer relationships.",
        "Woodworking businesses typically benefit from showcasing the entire creation process, as customers value seeing how raw timber becomes finished art.",
        "In your woodworking venture, emphasize the unique grain patterns and character of each piece to justify premium pricing for one-of-a-kind items."
    ],
    "textile": [
        "In your textile business, emphasizing traditional patterns or techniques can create a unique market position that attracts premium customers.",
        "For textile work, consider creating color story collections that encourage multiple purchases and coordinate with contemporary interior design trends.",
        "Your textile business could benefit from highlighting the tactile qualities of your fabrics through in-person experiences or detailed photography.",
        "As a textile artisan, showing the versatility of your creations through styling guides can increase perceived value and average purchase size."
    ],
    "food": [
        "For your food business, documenting and sharing traditional preservation methods adds cultural value that customers are often willing to pay more for.",
        "Food enterprises should emphasize seasonal specialties to create anticipation and urgency, turning limited availability into a marketing advantage.",
        "In your food business, transparent sourcing information can justify premium pricing while building trust with increasingly conscious consumers.",
        "For specialty food products, offering pairing suggestions or serving recommendations adds value without increasing production costs."
    ],
    "farming": [
        "As a farmer, implementing crop rotation and companion planting can reduce pest problems while improving soil health, addressing two challenges simultaneously.",
        "Your farming enterprise could benefit from direct-to-consumer models like CSA subscriptions that improve cash flow predictability and reduce market volatility.",
        "For small-scale farming, focusing on high-value crops with shorter growing cycles can maximize land productivity and improve annual returns.",
        "In your agricultural business, creating value-added products from seconds or surplus can significantly increase profit margins compared to selling raw produce."
    ]
}

# Sample document database - simulating a FAISS index
sample_documents = [
    {
        "id": "doc1",
        "title": "Pricing Strategies for Small Businesses",
        "content": "Effective pricing strategies include cost-plus pricing, competitive pricing, value-based pricing, and dynamic pricing. Small businesses should consider their costs, market position, and customer value perception when setting prices.",
        "category": "Pricing"
    },
    {
        "id": "doc2",
        "title": "Digital Marketing on a Budget",
        "content": "Small businesses can leverage social media marketing, email campaigns, content marketing, and SEO to reach customers without spending large amounts on advertising. Building an organic presence is key to sustainable growth.",
        "category": "Marketing"
    },
    {
        "id": "doc3",
        "title": "Sustainable Business Practices",
        "content": "Implementing sustainable practices can reduce costs and appeal to environmentally conscious consumers. Consider energy efficiency, waste reduction, sustainable sourcing, and highlighting your sustainability efforts in marketing.",
        "category": "Sustainability"
    },
    {
        "id": "doc4",
        "title": "Optimizing Production for Small Scale Operations",
        "content": "Small businesses can improve production efficiency through lean principles, reducing waste, optimizing workspace layout, standardizing processes, and implementing quality control measures.",
        "category": "Production"
    },
    {
        "id": "doc5",
        "title": "Customer Retention Strategies",
        "content": "Building customer loyalty is often more cost-effective than acquiring new customers. Implement loyalty programs, personalized communication, excellent customer service, and regular follow-ups to maintain relationships.",
        "category": "Marketing"
    }
]

# Business strategies database
business_strategies = {
    "pricing": [
        "Consider implementing a value-based pricing strategy that focuses on the perceived value to your customers rather than just cost-plus markup.",
        "Analyze your competitors' pricing strategies and position your products or services at a competitive price point while highlighting your unique value proposition.",
        "Experiment with tiered pricing or package deals to cater to different customer segments and increase average transaction value.",
        "Implement seasonal or promotional discounts strategically to boost sales during slower periods without devaluing your core offerings.",
        "Regularly review your pricing structure against rising costs to maintain healthy profit margins while staying competitive in the market."
    ],
    "marketing": [
        "Develop a content marketing strategy that positions you as an expert in your field, focusing on solving problems your target customers face.",
        "Leverage social media platforms where your target audience is most active, creating engaging content that encourages sharing and interaction.",
        "Build an email marketing campaign that nurtures leads with valuable content and special offers tailored to their stage in the customer journey.",
        "Collaborate with complementary businesses or micro-influencers in your community to expand your reach to new potential customers.",
        "Invest in search engine optimization (SEO) to improve your online visibility for keywords relevant to your products or services."
    ],
    "sustainability": [
        "Audit your current operations to identify areas where you can reduce waste and implement more sustainable practices that also cut costs.",
        "Source materials and supplies from local or environmentally responsible vendors to reduce your carbon footprint and appeal to eco-conscious consumers.",
        "Develop a transparent communication strategy about your sustainability efforts to build trust and loyalty with increasingly environmentally aware customers.",
        "Consider obtaining relevant sustainability certifications that can differentiate your business and potentially open doors to new markets and partnerships.",
        "Design products or services with circular economy principles in mind, focusing on durability, repairability, and end-of-life recycling or upcycling possibilities."
    ],
    "production": [
        "Implement lean production principles to minimize waste and maximize efficiency in your manufacturing or service delivery processes.",
        "Invest in appropriate technology or tools that can automate repetitive tasks, allowing you to focus on value-adding activities that require human expertise.",
        "Develop clear standard operating procedures (SOPs) to ensure consistency in quality and efficiency across all production or service delivery activities.",
        "Create a flexible production schedule that can adapt to seasonal demands or unexpected orders without compromising quality or incurring excessive costs.",
        "Regularly assess your supply chain for vulnerabilities and develop contingency plans to mitigate risks from disruptions such as supplier issues or material shortages."
    ],
    "general": [
        "Focus on building a strong, authentic brand that clearly communicates your values and unique selling proposition to stand out in a crowded marketplace.",
        "Develop a customer feedback system to continuously gather insights that can drive improvements in your products, services, and overall business operations.",
        "Create a financial management system that provides regular visibility into cash flow, profitability, and key performance indicators for informed decision-making.",
        "Invest in ongoing skills development for yourself and any team members to stay competitive and adapt to changing market conditions and technologies.",
        "Build strategic partnerships with complementary businesses to share resources, reduce costs, expand your offering, or reach new customer segments."
    ]
}

def generate_unique_id_from_query(query):
    """
    Generate a stable but unique ID from a query to track repeated questions
    """
    # Create a hash from the query after normalizing
    normalized_query = re.sub(r'\s+', ' ', query.lower().strip())
    return hashlib.md5(normalized_query.encode()).hexdigest()

def enhance_response(advice, query):
    """
    Makes the response more AI-like by adding variety and personalization
    """
    # Extract key terms from query to personalize response
    key_terms = re.findall(r'\b\w{4,}\b', query.lower())
    business_type = ""
    
    if any(term in ['wood', 'carpentry', 'furniture', 'carve', 'carving'] for term in key_terms):
        business_type = "woodworking"
    elif any(term in ['fabric', 'textile', 'cloth', 'sew', 'weave', 'stitch'] for term in key_terms):
        business_type = "textile"
    elif any(term in ['food', 'cook', 'bake', 'meal', 'recipe'] for term in key_terms):
        business_type = "food"
    elif any(term in ['farm', 'crop', 'agriculture', 'harvest', 'plant'] for term in key_terms):
        business_type = "farming"
    
    # Choose a response template based on query hash for consistency
    query_hash = int(generate_unique_id_from_query(query), 16)
    template_index = query_hash % len(response_templates)
    template = response_templates[template_index]
    
    # Format the response with the advice
    response = template.format(advice=advice)
    
    # Add business-specific advice if type detected
    if business_type:
        # Select business advice based on query hash for consistency
        specific_advice_index = query_hash % len(business_specific_advice[business_type])
        business_advice = business_specific_advice[business_type][specific_advice_index]
        response += f" {business_advice}"
    
    # Add more personalization based on extracted terms
    if 'cost' in key_terms or 'price' in key_terms or 'profit' in key_terms:
        response += " Remember that accurate pricing is fundamental to sustainable business growth."
    elif 'customer' in key_terms or 'market' in key_terms or 'sell' in key_terms:
        response += " Building strong customer relationships will be key to your long-term success."
    elif 'quality' in key_terms or 'improve' in key_terms:
        response += " Consistent quality will set you apart in an increasingly competitive marketplace."
    
    return response

def extract_keywords(text):
    """Extract meaningful keywords from text for better categorization"""
    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    
    # Split into words
    words = text.split()
    
    # Remove common stopwords
    stopwords = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
                 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
                 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}
    
    keywords = [word for word in words if word not in stopwords and len(word) > 3]
    return keywords

def generate_unique_id():
    """Generate a unique ID for tracking advice requests."""
    return str(uuid.uuid4())

def retrieve_relevant_documents(query, top_k=2):
    """Retrieve relevant documents based on keyword matching."""
    keywords = extract_keywords(query)
    
    # Calculate relevance scores for each document
    doc_scores = []
    for doc in sample_documents:
        score = 0
        doc_text = doc["title"] + " " + doc["content"]
        doc_text = doc_text.lower()
        
        for keyword in keywords:
            if keyword in doc_text:
                score += 1
                # Give higher weight if keyword is in title
                if keyword in doc["title"].lower():
                    score += 0.5
        
        doc_scores.append((doc, score))
    
    # Sort by score and return top_k documents
    doc_scores.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in doc_scores[:top_k] if score > 0]

def generate_advice(query):
    """
    Enhanced rule-based advice generation with more varied responses
    """
    query = query.lower()
    query_id = generate_unique_id_from_query(query)
    
    # Extract keywords for better categorization
    keywords = extract_keywords(query)
    
    # Enhanced categorization with keyword weights
    category_scores = {
        'pricing': 0,
        'marketing': 0,
        'sustainability': 0,
        'production': 0,
        'general': 0
    }
    
    # Pricing keywords
    pricing_keywords = {'price', 'pricing', 'cost', 'charge', 'profit', 'margin', 'worth', 
                       'expensive', 'cheap', 'afford', 'value', 'discount', 'money', 'financial',
                       'income', 'revenue', 'earning', 'dollar', 'rupee', 'sale', 'budget'}
    
    # Marketing keywords
    marketing_keywords = {'market', 'sell', 'customer', 'promote', 'advertise', 'publicity', 
                         'brand', 'client', 'social', 'media', 'facebook', 'instagram', 'platform',
                         'audience', 'target', 'position', 'visibility', 'display', 'showcase'}
    
    # Sustainability keywords
    sustainability_keywords = {'sustain', 'environment', 'eco', 'green', 'waste', 'recycle',
                              'reuse', 'carbon', 'footprint', 'natural', 'organic', 'renewable',
                              'biodegradable', 'impact', 'conservation', 'preserve', 'energy',
                              'efficient', 'climate', 'friendly'}
    
    # Production keywords
    production_keywords = {'product', 'quality', 'improve', 'make', 'create', 'production',
                           'manufacture', 'craft', 'skill', 'technique', 'process', 'material',
                           'supply', 'chain', 'inventory', 'design', 'equipment', 'tool',
                           'efficiency', 'output', 'workshop'}
    
    # Score each category based on keyword presence
    for keyword in keywords:
        if keyword in pricing_keywords:
            category_scores['pricing'] += 2
        elif keyword in marketing_keywords:
            category_scores['marketing'] += 2
        elif keyword in sustainability_keywords:
            category_scores['sustainability'] += 2
        elif keyword in production_keywords:
            category_scores['production'] += 2
        
        # Additional pattern matching for more context
        if 'how' in query and 'price' in query:
            category_scores['pricing'] += 3
        if 'how' in query and ('market' in query or 'sell' in query):
            category_scores['marketing'] += 3
        if 'how' in query and ('sustainable' in query or 'eco' in query):
            category_scores['sustainability'] += 3
        if 'how' in query and ('make' in query or 'produce' in query):
            category_scores['production'] += 3
    
    # Default to general if no clear category emerges
    category_scores['general'] = 1  # Minimal base score
    
    # Select the highest scoring category
    category = max(category_scores, key=category_scores.get)
    
    # If all scores are very low, default to general
    if category_scores[category] <= 1:
        category = 'general'
    
    # Record the request
    storage['advice_requests'].append({
        'query': query,
        'timestamp': time.time(),
        'category': category,
        'query_id': query_id
    })
    
    # Check if we've given advice for this query before to avoid repetition
    if query_id in storage['previous_advice']:
        # Get different advice than what was given before
        previous_indices = storage['previous_advice'][query_id]
        available_advice = [advice for i, advice in enumerate(storage['business_strategies'][category]) 
                           if i not in previous_indices]
        
        # If we've used all advice for this category, reset
        if not available_advice:
            storage['previous_advice'][query_id] = []
            available_advice = storage['business_strategies'][category]
    else:
        storage['previous_advice'][query_id] = []
        available_advice = storage['business_strategies'][category]
    
    # Select advice from appropriate category
    advice = random.choice(available_advice)
    
    # Record which advice was given
    advice_index = storage['business_strategies'][category].index(advice)
    storage['previous_advice'][query_id].append(advice_index)
    
    # Retrieve relevant documents
    relevant_docs = retrieve_relevant_documents(query)
    
    # Generate response based on relevant documents and business strategies
    if relevant_docs:
        # Use information from retrieved documents
        doc_advice = relevant_docs[0]["content"]
        
        # Add a strategy from our database
        strategy = random.choice(business_strategies[category])
        
        # Combine document-based advice with strategic advice
        response = f"{doc_advice}\n\nStrategy recommendation: {strategy}"
    else:
        # Enhance the response to make it more AI-like
        response = enhance_response(advice, query)
    
    # Record the advice request
    request_data = {
        "id": generate_unique_id(),
        "query": query,
        "response": response,
        "category": category,
        "timestamp": time.time(),
        "processing_time": random.uniform(0.5, 2.0)  # Simulated processing time
    }
    storage['advice_requests'].append(request_data)
    
    return request_data

def generate_dashboard():
    """Generate dashboard visualization using matplotlib."""
    plt.figure(figsize=(12, 10))
    
    # Generate synthetic data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    profits = [random.uniform(1000, 5000) for _ in range(6)]
    costs = [random.uniform(2000, 4000) for _ in range(6)]
    revenues = [cost + random.uniform(500, 2000) for cost in costs]
    
    # Get data from advice requests
    categories = [req.get('category', 'Unknown') for req in storage['advice_requests']]
    category_counts = {'pricing': 0, 'marketing': 0, 'sustainability': 0, 'production': 0, 'general': 0}
    for cat in categories:
        if cat.lower() in category_counts:
            category_counts[cat.lower()] += 1
    
    # Ensure we have some data for plotting
    if all(count == 0 for count in category_counts.values()):
        for cat in category_counts:
            category_counts[cat] = random.randint(1, 5)
            
    response_times = [req.get('processing_time', 1.0) for req in storage['advice_requests']]
    
    # Plot 1: Profit trend
    plt.subplot(2, 2, 1)
    plt.plot(months, profits, marker='o', color='green')
    plt.title('Profit Trend (Last 6 Months)')
    plt.xlabel('Month')
    plt.ylabel('Profit ($)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 2: Cost vs Revenue
    plt.subplot(2, 2, 2)
    x = range(len(months))
    plt.bar([i - 0.2 for i in x], costs, width=0.4, label='Costs', color='red', alpha=0.7)
    plt.bar([i + 0.2 for i in x], revenues, width=0.4, label='Revenue', color='blue', alpha=0.7)
    plt.title('Cost vs Revenue')
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.xticks(x, months)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Plot 3: Query Types
    plt.subplot(2, 2, 3)
    cats = list(category_counts.keys())
    counts = list(category_counts.values())
    if sum(counts) > 0:  # Check if there's data to plot
        plt.pie(counts, labels=cats, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
    else:
        plt.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center')
    plt.title('Query Categories')
    
    # Plot 4: Response Time
    plt.subplot(2, 2, 4)
    # Ensuring there's at least some data
    if not response_times:
        response_times = [1.0, 1.5, 0.8, 1.2, 0.9]
    plt.hist(response_times, bins=10, color='purple', alpha=0.7)
    plt.title('Response Time Distribution')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    plt.tight_layout()
    
    # Convert plot to base64 string for embedding in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def process_query():
    """Process user query and return advice."""
    query = request.form['query']
    if not query:
        flash('Please enter a query')
        return redirect(url_for('index'))
    
    result = generate_advice(query)
    
    # Get document references to display
    relevant_docs = retrieve_relevant_documents(query)
    doc_references = [doc['title'] for doc in relevant_docs]
    
    return render_template(
        'result.html',
        query=query,
        advice=result['response'],
        category=result['category'],
        processing_time=f"{result['processing_time']:.2f}",
        doc_references=doc_references
    )

@app.route('/feedback', methods=['POST'])
def record_feedback():
    """Record user feedback on advice."""
    advice_id = request.form['advice_id']
    rating = int(request.form['rating'])
    comments = request.form.get('comments', '')
    
    feedback = {
        'advice_id': advice_id,
        'rating': rating,
        'comments': comments,
        'timestamp': time.time()
    }
    storage['user_feedback'].append(feedback)
    
    flash('Thank you for your feedback!')
    return redirect(url_for('index'))

@app.route('/metrics')
def show_metrics():
    """Display business metrics dashboard."""
    dashboard_img = generate_dashboard()
    
    # Count requests by category
    category_counts = {}
    for req in storage['advice_requests']:
        category = req['category'].capitalize()
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1
    
    # Get recent queries - convert any datetime timestamps to float for comparison
    def get_timestamp(x):
        ts = x.get('timestamp', 0)
        if isinstance(ts, datetime):
            return ts.timestamp()
        return ts
    
    recent_queries = sorted(storage['advice_requests'], key=get_timestamp, reverse=True)[:5]
    
    # Get usage over time (simulated)
    current_time = time.time()
    time_periods = ['Last 24h', 'Last week', 'Last month']
    usage_data = {
        'Last 24h': len([r for r in storage['advice_requests'] if current_time - r.get('timestamp', 0) < 86400]),
        'Last week': len([r for r in storage['advice_requests'] if current_time - r.get('timestamp', 0) < 604800]),
        'Last month': len(storage['advice_requests'])
    }
    
    # Calculate average document retrieval stats
    doc_counts = [len(retrieve_relevant_documents(req['query'])) for req in storage['advice_requests'] if 'query' in req]
    avg_docs_retrieved = sum(doc_counts) / len(doc_counts) if doc_counts else 0
    
    return render_template(
        'metrics.html',
        dashboard_img=dashboard_img,
        category_counts=category_counts,
        recent_queries=recent_queries,
        usage_data=usage_data,
        total_queries=len(storage['advice_requests']),
        avg_docs_retrieved=f"{avg_docs_retrieved:.1f}"
    )

@app.route('/api/advice', methods=['POST'])
def api_get_advice():
    """API endpoint to get advice based on query."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    result = generate_advice(query)
    
    # Get document references
    relevant_docs = retrieve_relevant_documents(query)
    doc_references = [{"id": doc['id'], "title": doc['title']} for doc in relevant_docs]
    
    response = {
        "id": result['id'],
        "query": query,
        "advice": result['response'],
        "category": result['category'],
        "references": doc_references,
        "processing_time": result['processing_time']
    }
    
    return jsonify(response)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    # Create basic templates if they don't exist
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>SkillMentor - Business Advice</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; }
        .container { width: 80%; margin: 0 auto; padding: 20px; }
        header { background: #4b6cb7; color: white; padding: 1rem; }
        .query-form { background: #f4f4f4; padding: 20px; border-radius: 5px; margin-top: 20px; }
        input[type="text"] { width: 70%; padding: 10px; }
        button { padding: 10px 15px; background: #4b6cb7; color: white; border: none; cursor: pointer; }
        button:hover { background: #3a5795; }
        footer { text-align: center; margin-top: 20px; padding: 10px; background: #f4f4f4; }
        .flash-messages { padding: 10px; background: #f8d7da; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>SkillMentor</h1>
            <p>AI-powered business advice for micro-entrepreneurs</p>
        </div>
    </header>
    
    <div class="container">
        {% if get_flashed_messages() %}
        <div class="flash-messages">
            {% for message in get_flashed_messages() %}
                <p>{{ message }}</p>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="query-form">
            <h2>Ask for Business Advice</h2>
            <form action="/query" method="post">
                <input type="text" name="query" placeholder="e.g., How can I price my handmade jewelry?" required>
                <button type="submit">Get Advice</button>
            </form>
        </div>
        
        <div style="margin-top: 30px;">
            <h3>Example Questions:</h3>
            <ul>
                <li>What are effective marketing strategies for a small bakery?</li>
                <li>How can I reduce production costs for my handcrafted products?</li>
                <li>What sustainable practices can I implement in my coffee shop?</li>
                <li>How should I price my consulting services?</li>
            </ul>
        </div>
        
        <div style="margin-top: 30px;">
            <a href="/metrics">View Business Metrics Dashboard</a>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2023 SkillMentor - Empowering micro-entrepreneurs</p>
    </footer>
</body>
</html>
            ''')
    
    if not os.path.exists('templates/result.html'):
        with open('templates/result.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>SkillMentor - Advice Result</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; }
        .container { width: 80%; margin: 0 auto; padding: 20px; }
        header { background: #4b6cb7; color: white; padding: 1rem; }
        .result-card { background: #f4f4f4; padding: 20px; border-radius: 5px; margin-top: 20px; }
        .category-tag { display: inline-block; background: #4b6cb7; color: white; padding: 5px 10px; border-radius: 3px; }
        .references { margin-top: 20px; padding: 10px; background: #e9ecef; border-radius: 5px; }
        button { padding: 10px 15px; background: #4b6cb7; color: white; border: none; cursor: pointer; }
        button:hover { background: #3a5795; }
        footer { text-align: center; margin-top: 20px; padding: 10px; background: #f4f4f4; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>SkillMentor</h1>
            <p>AI-powered business advice for micro-entrepreneurs</p>
        </div>
    </header>
    
    <div class="container">
        <div class="result-card">
            <h2>Your Question</h2>
            <p>{{ query }}</p>
            
            <div style="margin-top: 20px;">
                <span class="category-tag">{{ category }}</span>
                <small style="margin-left: 10px;">Processed in {{ processing_time }} seconds</small>
            </div>
            
            <h2>Advice</h2>
            <p style="white-space: pre-line;">{{ advice }}</p>
            
            {% if doc_references %}
            <div class="references">
                <h3>References</h3>
                <ul>
                    {% for reference in doc_references %}
                    <li>{{ reference }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        
        <div style="margin-top: 20px;">
            <a href="/"><button>Ask Another Question</button></a>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2023 SkillMentor - Empowering micro-entrepreneurs</p>
    </footer>
</body>
</html>
            ''')
    
    if not os.path.exists('templates/metrics.html'):
        with open('templates/metrics.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>SkillMentor - Business Metrics</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; }
        .container { width: 90%; margin: 0 auto; padding: 20px; }
        header { background: #4b6cb7; color: white; padding: 1rem; }
        .dashboard { margin-top: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .stat-card { background: #f4f4f4; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-value { font-size: 24px; font-weight: bold; color: #4b6cb7; }
        .recent-queries { margin-top: 20px; }
        .query-item { border-bottom: 1px solid #ddd; padding: 10px 0; }
        button { padding: 10px 15px; background: #4b6cb7; color: white; border: none; cursor: pointer; }
        button:hover { background: #3a5795; }
        footer { text-align: center; margin-top: 20px; padding: 10px; background: #f4f4f4; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>SkillMentor Metrics Dashboard</h1>
            <p>Business performance and usage analytics</p>
        </div>
    </header>
    
    <div class="container">
        <div class="dashboard">
            <h2>Business Performance Dashboard</h2>
            <img src="data:image/png;base64,{{ dashboard_img }}" alt="Dashboard" style="width: 100%; max-width: 1000px;">
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Queries</h3>
                <div class="stat-value">{{ total_queries }}</div>
            </div>
            
            <div class="stat-card">
                <h3>Avg. Documents Retrieved</h3>
                <div class="stat-value">{{ avg_docs_retrieved }}</div>
            </div>
            
            {% for period, count in usage_data.items() %}
            <div class="stat-card">
                <h3>Usage {{ period }}</h3>
                <div class="stat-value">{{ count }}</div>
            </div>
            {% endfor %}
            
            {% for category, count in category_counts.items() %}
            <div class="stat-card">
                <h3>{{ category }} Queries</h3>
                <div class="stat-value">{{ count }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="recent-queries">
            <h2>Recent Queries</h2>
            {% for query in recent_queries %}
            <div class="query-item">
                <p><strong>Query:</strong> {{ query.query }}</p>
                <p><strong>Category:</strong> {{ query.category }} | <strong>Time:</strong> {{ query.processing_time|round(2) }}s</p>
            </div>
            {% endfor %}
        </div>
        
        <div style="margin-top: 20px;">
            <a href="/"><button>Back to Home</button></a>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2023 SkillMentor - Empowering micro-entrepreneurs</p>
    </footer>
</body>
</html>
            ''')
    
    if not os.path.exists('templates/error.html'):
        with open('templates/error.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>SkillMentor - Error</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; text-align: center; }
        .container { width: 80%; margin: 50px auto; padding: 20px; }
        .error-card { background: #f8d7da; padding: 20px; border-radius: 5px; margin-top: 20px; }
        button { padding: 10px 15px; background: #4b6cb7; color: white; border: none; cursor: pointer; }
        button:hover { background: #3a5795; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-card">
            <h1>Oops! An Error Occurred</h1>
            <p>{{ error }}</p>
        </div>
        
        <div style="margin-top: 20px;">
            <a href="/"><button>Back to Home</button></a>
        </div>
    </div>
</body>
</html>
            ''')
    
    app.run(host='0.0.0.0', debug=True) 