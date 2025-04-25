# SkillMentor

An AI-powered business advice platform for micro-entrepreneurs, providing contextual guidance on pricing, marketing, sustainability, and production strategies.

## Overview

SkillMentor uses natural language processing and document retrieval to provide tailored business advice. It features:

- Multilingual text processing
- Document retrieval for context-aware responses
- AI-driven advice generation
- Business metrics visualization
- User-friendly web interface

## Quick Start

### Prerequisites

- Python 3.9+
- pip package manager

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/skillmentor.git
   cd skillmentor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. Download NLTK data (for text processing):
   ```
   python -c "import nltk; nltk.download('punkt')"
   ```

5. Create data directories:
   ```
   mkdir -p data/raw data/processed
   ```

### Running the Application

Two options are available:

#### 1. Full Application (with all dependencies)

```
python app.py
```

#### 2. Simplified Version (minimal dependencies)

```
python simple_app.py
```

The application will be available at: http://localhost:5000

## Features

### Business Advice Generation

Submit business-related queries through the web interface to receive tailored advice based on:
- Document retrieval from business knowledge base
- Category-based advice strategies
- Context-aware responses

### Business Metrics Dashboard

View business performance metrics at `/metrics`, including:
- Query categories distribution
- Usage statistics
- Performance analytics
- Document retrieval efficiency

## Docker Support

Build and run with Docker:

```
docker build -t skillmentor .
docker run -p 8080:8080 skillmentor
```

## Project Structure

```
skillmentor/
├── app.py                  # Main Flask application
├── simple_app.py           # Simplified version with minimal dependencies
├── requirements.txt        # Project dependencies
├── Dockerfile              # Container configuration
├── .env.example            # Environment variables template
├── data/                   # Data storage
│   ├── raw/                # Raw document storage
│   └── processed/          # Processed indices and vectors
├── scripts/                # Utility scripts
│   ├── create_index.py     # FAISS index creation
│   └── test_app.py         # Application testing
├── skillmentor/            # Core module
│   ├── __init__.py
│   ├── core.py             # Main application logic
│   ├── processor.py        # Text processing
│   ├── retriever.py        # Document retrieval
│   ├── generator.py        # Advice generation
│   └── dashboard.py        # Metrics visualization
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Home page
    ├── result.html         # Results display
    ├── metrics.html        # Metrics dashboard
    └── error.html          # Error pages
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 