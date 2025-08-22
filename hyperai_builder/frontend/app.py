"""
HyperAI Builder - Frontend Application

A professional, modern web interface for building AI applications
using natural language descriptions.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from hyperai_builder.core.config import get_settings
from hyperai_builder.core.logging import setup_logging
from hyperai_builder.ai.generators.code_generator import CodeGenerator

# Setup logging
setup_logging()

# Page configuration
st.set_page_config(
    page_title="HyperAI Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://hyperai.com/docs",
        "Report a bug": "https://hyperai.com/support",
        "About": "HyperAI Builder - Create professional AI applications with natural language"
    }
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global styles */
    .main {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* Card styling */
    .stCard {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e1e5e9;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stCard:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 10px;
        border: 1px solid #e1e5e9;
    }
    
    /* Success/Error message styling */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Feature card styling */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .feature-card h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {}
    
    if 'generation_progress' not in st.session_state:
        st.session_state.generation_progress = 0
    
    # Header
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🚀 HyperAI Builder</h1>
        <p>Create professional, production-ready AI applications with natural language</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Quick Start")
        st.markdown("""
        1. **Describe** your app idea
        2. **Choose** AI model & settings
        3. **Generate** professional code
        4. **Deploy** instantly
        """)
        
        st.markdown("### 🔧 Settings")
        
        # AI Model Selection
        ai_provider = st.selectbox(
            "AI Provider",
            ["openai", "anthropic", "google"],
            help="Choose your preferred AI model provider"
        )
        
        # API Key Input
        api_key = st.text_input(
            "API Key",
            type="password",
            help=f"Enter your {ai_provider.upper()} API key",
            placeholder="sk-..." if ai_provider == "openai" else "Enter API key"
        )
        
        # Model Configuration
        if ai_provider == "openai":
            model_name = st.selectbox(
                "Model",
                ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                help="Choose the OpenAI model to use"
            )
        elif ai_provider == "anthropic":
            model_name = st.selectbox(
                "Model",
                ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"],
                help="Choose the Anthropic model to use"
            )
        else:  # Google
            model_name = st.selectbox(
                "Model",
                ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                help="Choose the Google model to use"
            )
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            temperature = st.slider(
                "Creativity (Temperature)",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Higher values make output more creative, lower values more focused"
            )
            
            max_tokens = st.slider(
                "Max Tokens",
                min_value=1000,
                max_value=16000,
                value=8000,
                step=1000,
                help="Maximum number of tokens in the generated response"
            )
        
        st.markdown("### 📊 Usage")
        st.metric("Projects Created", "0")
        st.metric("Code Generated", "0 lines")
        
        # Theme toggle
        st.markdown("### 🌙 Theme")
        theme = st.selectbox("Choose Theme", ["Light", "Dark", "Auto"])
    
    # Main content area
    if st.session_state.current_step == 0:
        show_welcome_page()
    elif st.session_state.current_step == 1:
        show_project_creation()
    elif st.session_state.current_step == 2:
        show_generation_progress()
    elif st.session_state.current_step == 3:
        show_project_results()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Built with ❤️ by HyperAI Team | <a href="https://hyperai.com" target="_blank">hyperai.com</a></p>
    </div>
    """, unsafe_allow_html=True)


def show_welcome_page():
    """Display the welcome page with features and examples."""
    
    # Welcome message
    st.markdown("""
    <div class="fade-in">
        <h2>🎉 Welcome to the Future of App Development</h2>
        <p>Transform your ideas into professional, production-ready applications using the power of AI.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🚀 AI-Powered Generation</h3>
            <p>Describe your app in natural language and watch AI generate professional code with best practices.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ Instant Deployment</h3>
            <p>One-click deployment to popular platforms with built-in CI/CD and monitoring.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🔒 Enterprise Ready</h3>
            <p>Built with security, scalability, and maintainability in mind for production use.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Example projects
    st.markdown("### 💡 Example Projects")
    
    examples = [
        {
            "title": "Customer Support Chatbot",
            "description": "AI-powered chatbot with natural language processing and ticket management",
            "tech": "Python + FastAPI + OpenAI",
            "icon": "🤖"
        },
        {
            "title": "Data Analytics Dashboard",
            "description": "Interactive dashboard for visualizing business metrics and KPIs",
            "tech": "Python + Streamlit + Plotly",
            "icon": "📊"
        },
        {
            "title": "Image Recognition API",
            "description": "RESTful API for image classification and object detection",
            "tech": "Python + Flask + TensorFlow",
            "icon": "🖼️"
        }
    ]
    
    for example in examples:
        with st.expander(f"{example['icon']} {example['title']}"):
            st.markdown(f"**Description:** {example['description']}")
            st.markdown(f"**Tech Stack:** {example['tech']}")
            
            if st.button(f"Generate {example['title']}", key=f"example_{example['title']}"):
                st.session_state.example_description = example['description']
                st.session_state.current_step = 1
                st.rerun()
    
    # Get started button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Start Building Your App", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()


def show_project_creation():
    """Display the project creation form."""
    
    st.markdown("### 🏗️ Create Your AI Application")
    
    # Project details form
    with st.form("project_creation"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name",
                placeholder="My Amazing AI App",
                help="Give your project a descriptive name"
            )
        
        with col2:
            project_type = st.selectbox(
                "Project Type",
                ["Web Application", "Mobile App", "API Service", "Chatbot", "Data Analyzer", "Custom"],
                help="Choose the type of application you want to build"
            )
        
        # Project description
        description = st.text_area(
            "Describe Your App",
            placeholder="Describe your application idea in detail. For example: 'I want to build a customer support chatbot that can understand user queries, provide helpful responses, and escalate complex issues to human agents. It should integrate with our CRM system and support multiple languages.'",
            height=150,
            help="Be as detailed as possible about what you want your app to do"
        )
        
        # Example description (if selected from welcome page)
        if 'example_description' in st.session_state:
            description = st.session_state.example_description
            st.info(f"Using example description: {description}")
        
        # Advanced options
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                include_tests = st.checkbox("Include Unit Tests", value=True)
                include_docs = st.checkbox("Include Documentation", value=True)
                include_docker = st.checkbox("Include Docker Support", value=True)
            
            with col2:
                include_ci_cd = st.checkbox("Include CI/CD Pipeline", value=True)
                include_monitoring = st.checkbox("Include Monitoring", value=True)
                include_security = st.checkbox("Include Security Features", value=True)
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate My App", use_container_width=True)
        
        if submitted:
            if not project_name or not description:
                st.error("Please provide both project name and description.")
                return
            
            if not st.session_state.get('api_key'):
                st.error("Please enter your API key in the sidebar.")
                return
            
            # Store project data
            st.session_state.project_data = {
                "name": project_name,
                "type": project_type,
                "description": description,
                "options": {
                    "include_tests": include_tests,
                    "include_docs": include_docs,
                    "include_docker": include_docker,
                    "include_ci_cd": include_ci_cd,
                    "include_monitoring": include_monitoring,
                    "include_security": include_security
                }
            }
            
            # Move to generation step
            st.session_state.current_step = 2
            st.rerun()


def show_generation_progress():
    """Display the code generation progress."""
    
    st.markdown("### ⚡ Generating Your Application")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Generation steps
    steps = [
        "Analyzing project requirements...",
        "Designing architecture...",
        "Generating source code...",
        "Creating documentation...",
        "Setting up testing...",
        "Configuring deployment...",
        "Finalizing project..."
    ]
    
    # Simulate generation process
    for i, step in enumerate(steps):
        status_text.text(step)
        progress = (i + 1) / len(steps)
        progress_bar.progress(progress)
        
        # Simulate processing time
        import time
        time.sleep(0.5)
    
    # Complete generation
    progress_bar.progress(1.0)
    status_text.text("✅ Generation complete!")
    
    # Generate actual project (this would be async in production)
    try:
        # For demo purposes, create a sample project
        st.session_state.generated_project = generate_sample_project()
        st.session_state.current_step = 3
        st.rerun()
        
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")
        st.session_state.current_step = 1


def show_project_results():
    """Display the generated project results."""
    
    st.markdown("### 🎉 Your App is Ready!")
    
    # Project overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="success-message">
            <h3>✅ Generation Successful!</h3>
            <p>Your professional, production-ready application has been generated.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        project_data = st.session_state.get('generated_project', {})
        st.metric("Files Generated", project_data.get('total_files', 0))
        st.metric("Lines of Code", project_data.get('total_lines', 0))
    
    # Project details
    st.markdown("### 📁 Generated Files")
    
    # File tree
    if 'generated_project' in st.session_state:
        project = st.session_state.generated_project
        
        # Display file structure
        for file_path, file_data in project.get('source_code', {}).items():
            with st.expander(f"📄 {file_path}"):
                if isinstance(file_data, dict) and 'content' in file_data:
                    st.code(file_data['content'], language='python')
                else:
                    st.text(str(file_data))
    
    # Action buttons
    st.markdown("### 🚀 Next Steps")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download Project", use_container_width=True):
            st.success("Project download started!")
    
    with col2:
        if st.button("🌐 Deploy to Cloud", use_container_width=True):
            st.info("Deployment options coming soon!")
    
    with col3:
        if st.button("🔄 Generate Another", use_container_width=True):
            st.session_state.current_step = 0
            st.rerun()


def generate_sample_project():
    """Generate a sample project for demonstration."""
    
    return {
        "name": "Customer Support Chatbot",
        "description": "AI-powered chatbot for customer support",
        "total_files": 8,
        "total_lines": 450,
        "source_code": {
            "main.py": {
                "content": '''"""
Customer Support Chatbot - Main Application

A professional AI-powered chatbot for handling customer inquiries
and providing automated support with human escalation capabilities.
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Chatbot",
    description="AI-powered customer support system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Chat session identifier")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Bot response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    requires_human: bool = Field(False, description="Whether human intervention is needed")

# Chatbot service
class ChatbotService:
    def __init__(self):
        self.conversation_history = {}
    
    async def process_message(self, message: str, session_id: str) -> ChatResponse:
        """Process user message and generate response."""
        try:
            # Simple response logic (would be replaced with AI model)
            if "help" in message.lower():
                response = "I\'m here to help! How can I assist you today?"
                confidence = 0.9
            elif "complaint" in message.lower():
                response = "I understand you have a complaint. Let me connect you with a human agent."
                confidence = 0.7
                requires_human = True
            else:
                response = "Thank you for your message. I\'ll do my best to help you."
                confidence = 0.8
            
            return ChatResponse(
                response=response,
                confidence=confidence,
                requires_human=requires_human
            )
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Initialize services
chatbot_service = ChatbotService()

# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Customer Support Chatbot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chatbot"}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process chat message."""
    try:
        session_id = message.session_id or "default"
        response = await chatbot_service.process_message(message.message, session_id)
        return response
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                "type": "file",
                "size": 2500,
                "lines": 120
            },
            "requirements.txt": {
                "content": """# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0

# AI and ML dependencies
openai>=1.3.0
langchain>=0.0.350

# Database dependencies
sqlalchemy>=2.0.23
alembic>=1.12.1

# Development dependencies
pytest>=7.4.3
pytest-asyncio>=0.21.1
black>=23.11.0
flake8>=6.1.0

# Generated by HyperAI Builder
""",
                "type": "file",
                "size": 300,
                "lines": 20
            },
            "README.md": {
                "content": """# Customer Support Chatbot

A professional AI-powered chatbot for handling customer inquiries and providing automated support with human escalation capabilities.

## Features

- Natural language processing for customer queries
- Automated response generation
- Human escalation for complex issues
- Session management and conversation history
- RESTful API interface
- Comprehensive logging and monitoring

## Tech Stack

- **Type**: API Service
- **Technology**: Python + FastAPI
- **Architecture**: Microservice

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

```bash
pytest
```

## Security

Basic security measures implemented including input validation and error handling.

## Performance

Standard performance optimizations applied with async processing and connection pooling.

## License

MIT License

Generated by [HyperAI Builder](https://hyperai.com)
""",
                "type": "file",
                "size": 800,
                "lines": 50
            }
        }
    }


if __name__ == "__main__":
    main()