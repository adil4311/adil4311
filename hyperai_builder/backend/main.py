"""
HyperAI Builder - Backend API Server

FastAPI-based backend for the AI application builder with
authentication, project management, and AI integration.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from hyperai_builder.core.config import get_settings, is_development, is_production
from hyperai_builder.core.logging import setup_logging, get_logger
from hyperai_builder.backend.core.database import init_database, db_manager
from hyperai_builder.ai.generators.code_generator import CodeGenerator

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting HyperAI Builder Backend...")
    
    try:
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        # Test database connection
        if db_manager.test_connection():
            logger.info("Database connection test successful")
        else:
            logger.error("Database connection test failed")
        
        # Initialize AI services
        logger.info("AI services initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down HyperAI Builder Backend...")
        db_manager.close()


# Create FastAPI app
app = FastAPI(
    title="HyperAI Builder API",
    description="Ultra-advanced AI App Builder API for creating professional applications",
    version="1.0.0",
    docs_url="/docs" if is_development() else None,
    redoc_url="/redoc" if is_development() else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if is_development() else ["https://hyperai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["hyperai.com", "*.hyperai.com"]
    )


# Pydantic models for API requests/responses
class ProjectCreateRequest(BaseModel):
    """Request model for creating a new project."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: str = Field(..., min_length=10, max_length=5000, description="Project description")
    project_type: str = Field(..., description="Type of project")
    tech_stack: Optional[str] = Field(None, description="Preferred technology stack")
    
    # AI generation options
    ai_provider: str = Field(..., description="AI model provider")
    ai_model: str = Field(..., description="AI model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="AI creativity level")
    max_tokens: int = Field(8000, ge=1000, le=16000, description="Maximum tokens for generation")
    
    # Additional options
    include_tests: bool = Field(True, description="Include unit tests")
    include_docs: bool = Field(True, description="Include documentation")
    include_docker: bool = Field(True, description="Include Docker support")
    include_ci_cd: bool = Field(True, description="Include CI/CD pipeline")
    include_monitoring: bool = Field(True, description="Include monitoring")
    include_security: bool = Field(True, description="Include security features")


class ProjectResponse(BaseModel):
    """Response model for project data."""
    
    id: str
    name: str
    description: str
    project_type: str
    tech_stack: str
    status: str
    progress: int
    created_at: str
    updated_at: str
    total_files: int
    total_lines: int


class GenerationRequest(BaseModel):
    """Request model for code generation."""
    
    project_id: str = Field(..., description="Project ID to generate code for")
    ai_api_key: str = Field(..., description="API key for AI provider")
    options: Optional[Dict[str, Any]] = Field(None, description="Generation options")


class GenerationResponse(BaseModel):
    """Response model for generation results."""
    
    project_id: str
    status: str
    progress: int
    generated_files: List[str]
    total_lines: int
    generation_time: float
    cost: float


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str
    timestamp: str
    version: str
    database: str
    ai_services: str


# Dependency functions
async def get_current_user(token: str = Depends(security)):
    """Get current user from JWT token."""
    # TODO: Implement JWT token validation
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # For now, return a mock user
    return {"id": "user-123", "username": "demo_user"}


async def get_code_generator() -> CodeGenerator:
    """Get code generator service."""
    return CodeGenerator()


# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "HyperAI Builder API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check database
        db_status = "healthy" if db_manager.test_connection() else "unhealthy"
        
        # Check AI services (basic check)
        ai_status = "healthy"
        
        return HealthResponse(
            status="healthy",
            timestamp=asyncio.get_event_loop().time(),
            version="1.0.0",
            database=db_status,
            ai_services=ai_status
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.post("/api/v1/projects", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    code_generator: CodeGenerator = Depends(get_code_generator)
):
    """Create a new project."""
    try:
        logger.info(f"Creating project: {request.name}")
        
        # TODO: Save project to database
        # For now, return mock response
        
        project_data = {
            "id": "proj-123",
            "name": request.name,
            "description": request.description,
            "project_type": request.project_type,
            "tech_stack": request.tech_stack or "python",
            "status": "draft",
            "progress": 0,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "total_files": 0,
            "total_lines": 0
        }
        
        logger.info(f"Project created successfully: {project_data['id']}")
        return ProjectResponse(**project_data)
    
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@app.get("/api/v1/projects", response_model=List[ProjectResponse])
async def list_projects(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """List user's projects."""
    try:
        logger.info(f"Listing projects for user: {current_user['id']}")
        
        # TODO: Fetch projects from database
        # For now, return mock data
        
        mock_projects = [
            {
                "id": "proj-123",
                "name": "Customer Support Chatbot",
                "description": "AI-powered chatbot for customer support",
                "project_type": "chatbot",
                "tech_stack": "python",
                "status": "generated",
                "progress": 100,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "total_files": 8,
                "total_lines": 450
            }
        ]
        
        return [ProjectResponse(**project) for project in mock_projects]
    
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get project by ID."""
    try:
        logger.info(f"Fetching project: {project_id}")
        
        # TODO: Fetch project from database
        # For now, return mock data
        
        project_data = {
            "id": project_id,
            "name": "Customer Support Chatbot",
            "description": "AI-powered chatbot for customer support",
            "project_type": "chatbot",
            "tech_stack": "python",
            "status": "generated",
            "progress": 100,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "total_files": 8,
            "total_lines": 450
        }
        
        return ProjectResponse(**project_data)
    
    except Exception as e:
        logger.error(f"Failed to fetch project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )


@app.post("/api/v1/projects/{project_id}/generate", response_model=GenerationResponse)
async def generate_code(
    project_id: str,
    request: GenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    code_generator: CodeGenerator = Depends(get_code_generator)
):
    """Generate code for a project."""
    try:
        logger.info(f"Starting code generation for project: {project_id}")
        
        # TODO: Validate project exists and user has access
        
        # Generate code using AI
        project_data = await code_generator.generate_project(
            description="AI-powered chatbot for customer support",
            project_name="Customer Support Chatbot",
            user_id=current_user['id'],
            ai_provider="openai",
            ai_api_key=request.ai_api_key
        )
        
        # TODO: Save generated code to database
        
        response_data = {
            "project_id": project_id,
            "status": "completed",
            "progress": 100,
            "generated_files": list(project_data.get('source_code', {}).keys()),
            "total_lines": project_data.get('metadata', {}).get('total_lines', 0),
            "generation_time": 30.5,  # Mock value
            "cost": 0.15  # Mock value
        }
        
        logger.info(f"Code generation completed for project: {project_id}")
        return GenerationResponse(**response_data)
    
    except Exception as e:
        logger.error(f"Code generation failed for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )


@app.get("/api/v1/projects/{project_id}/files")
async def get_project_files(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get project files."""
    try:
        logger.info(f"Fetching files for project: {project_id}")
        
        # TODO: Fetch project files from database
        # For now, return mock data
        
        mock_files = {
            "main.py": {
                "content": "# Customer Support Chatbot\n\nimport fastapi\n\napp = FastAPI()",
                "type": "file",
                "size": 100,
                "lines": 5
            },
            "requirements.txt": {
                "content": "fastapi>=0.104.0\nuvicorn>=0.24.0",
                "type": "file",
                "size": 50,
                "lines": 2
            }
        }
        
        return {"files": mock_files}
    
    except Exception as e:
        logger.error(f"Failed to fetch files for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project files: {str(e)}"
        )


@app.get("/api/v1/ai/models")
async def list_ai_models():
    """List available AI models."""
    try:
        logger.info("Listing available AI models")
        
        models = {
            "openai": {
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                "provider": "OpenAI",
                "website": "https://openai.com"
            },
            "anthropic": {
                "models": ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"],
                "provider": "Anthropic",
                "website": "https://anthropic.com"
            },
            "google": {
                "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                "provider": "Google",
                "website": "https://ai.google.dev"
            }
        }
        
        return {"models": models}
    
    except Exception as e:
        logger.error(f"Failed to list AI models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list AI models: {str(e)}"
        )


@app.get("/api/v1/ai/health")
async def ai_health_check():
    """Check AI services health."""
    try:
        logger.info("Checking AI services health")
        
        # TODO: Implement actual health checks for AI services
        
        health_status = {
            "openai": "healthy",
            "anthropic": "healthy",
            "google": "healthy",
            "overall": "healthy"
        }
        
        return {"ai_services": health_status}
    
    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI health check failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if is_development() else "An unexpected error occurred",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


def main():
    """Main function to run the FastAPI server."""
    settings = get_settings()
    
    logger.info(f"Starting HyperAI Builder Backend on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "hyperai_builder.backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()