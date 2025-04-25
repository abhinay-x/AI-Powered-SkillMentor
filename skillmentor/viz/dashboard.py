"""
Dashboard generation for business metrics visualization
"""
import io
import base64
import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class Dashboard:
    """
    Generates visualizations and dashboards for business metrics
    """
    
    def __init__(self):
        """Initialize the dashboard generator"""
        # Set up matplotlib style
        plt.style.use('ggplot')
        logging.info("Dashboard generator initialized")
    
    def generate_profit_trend(self, data=None):
        """
        Generate a profit trend line chart
        
        Args:
            data (dict): Dictionary with 'x' and 'y' values for plotting
                         If None, generates sample data
        
        Returns:
            str: Base64 encoded PNG image
        """
        if not data:
            # Generate sample data for demonstration
            x = np.array([1, 2, 3, 4, 5, 6])
            y = np.array([100, 120, 115, 130, 145, 160])
            data = {'x': x, 'y': y, 'label': 'Monthly Profit (USD)'}
        
        # Create figure and axis
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)
        
        # Plot data
        ax.plot(data['x'], data['y'], 'b-', marker='o')
        
        # Add labels and title
        ax.set_xlabel('Month')
        ax.set_ylabel(data.get('label', 'Value'))
        ax.set_title('Profit Trend')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Save figure to buffer
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        
        # Encode the buffer to base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return img_base64
    
    def generate_cost_revenue_comparison(self, data=None):
        """
        Generate a bar chart comparing costs and revenue
        
        Args:
            data (dict): Dictionary with 'categories', 'costs', and 'revenue'
                         If None, generates sample data
        
        Returns:
            str: Base64 encoded PNG image
        """
        if not data:
            # Generate sample data for demonstration
            categories = ['Product A', 'Product B', 'Product C']
            costs = [50, 60, 45]
            revenue = [80, 90, 70]
            data = {'categories': categories, 'costs': costs, 'revenue': revenue}
        
        # Create figure and axis
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)
        
        # Set up bar positions
        x = np.arange(len(data['categories']))
        width = 0.35
        
        # Plot bars
        ax.bar(x - width/2, data['costs'], width, label='Costs')
        ax.bar(x + width/2, data['revenue'], width, label='Revenue')
        
        # Add labels and title
        ax.set_xlabel('Products')
        ax.set_ylabel('Amount (USD)')
        ax.set_title('Cost vs Revenue Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(data['categories'])
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Save figure to buffer
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        
        # Encode the buffer to base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return img_base64
    
    def generate_bleu_score_chart(self, data=None):
        """
        Generate a bar chart of BLEU scores by query type
        
        Args:
            data (dict): Dictionary with 'categories' and 'scores'
                         If None, generates sample data
        
        Returns:
            str: Base64 encoded PNG image
        """
        if not data:
            # Generate sample data for demonstration
            categories = ['Pricing', 'Marketing', 'Sustainability', 'Production']
            scores = [0.82, 0.75, 0.88, 0.79]
            data = {'categories': categories, 'scores': scores}
        
        # Create figure and axis
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)
        
        # Plot bars
        bars = ax.bar(data['categories'], data['scores'], width=0.6)
        
        # Add labels and title
        ax.set_xlabel('Query Type')
        ax.set_ylabel('BLEU Score')
        ax.set_title('Advice Quality by Query Type (BLEU Score)')
        
        # Set y-axis range
        ax.set_ylim(0, 1.0)
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Save figure to buffer
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        
        # Encode the buffer to base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return img_base64
    
    def generate_full_dashboard(self):
        """
        Generate a full dashboard with multiple charts
        
        Returns:
            str: Base64 encoded PNG image
        """
        # Create figure with subplots
        fig = Figure(figsize=(12, 10))
        
        # Profit trend (top left)
        ax1 = fig.add_subplot(2, 2, 1)
        x = np.array([1, 2, 3, 4, 5, 6])
        y = np.array([100, 120, 115, 130, 145, 160])
        ax1.plot(x, y, 'b-', marker='o')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Profit (USD)')
        ax1.set_title('Profit Trend')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Cost vs Revenue (top right)
        ax2 = fig.add_subplot(2, 2, 2)
        categories = ['Product A', 'Product B', 'Product C']
        costs = [50, 60, 45]
        revenue = [80, 90, 70]
        x = np.arange(len(categories))
        width = 0.35
        ax2.bar(x - width/2, costs, width, label='Costs')
        ax2.bar(x + width/2, revenue, width, label='Revenue')
        ax2.set_xlabel('Products')
        ax2.set_ylabel('Amount (USD)')
        ax2.set_title('Cost vs Revenue')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories)
        ax2.legend()
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # BLEU scores (bottom left)
        ax3 = fig.add_subplot(2, 2, 3)
        categories = ['Pricing', 'Marketing', 'Sustainability', 'Production']
        scores = [0.82, 0.75, 0.88, 0.79]
        bars = ax3.bar(categories, scores, width=0.6)
        ax3.set_xlabel('Query Type')
        ax3.set_ylabel('BLEU Score')
        ax3.set_title('Advice Quality (BLEU Score)')
        ax3.set_ylim(0, 1.0)
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom')
        ax3.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Response time (bottom right)
        ax4 = fig.add_subplot(2, 2, 4)
        query_lengths = [10, 20, 30, 40, 50]
        response_times = [1.2, 1.5, 1.8, 2.1, 2.4]
        ax4.plot(query_lengths, response_times, 'r-', marker='s')
        ax4.set_xlabel('Query Length (words)')
        ax4.set_ylabel('Response Time (s)')
        ax4.set_title('Response Time vs Query Length')
        ax4.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        fig.tight_layout()
        
        # Save figure to buffer
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        
        # Encode the buffer to base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return img_base64 