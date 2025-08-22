"""
Code Generation Service for HyperAI Builder.

Orchestrates AI models to generate professional, production-ready applications
based on natural language descriptions.
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...core.logging import get_logger
from ...models.project import Project, ProjectType, TechStack
from ..models import get_ai_model, AIModelRequest

logger = get_logger(__name__)


class CodeGenerator:
    """Main code generation service."""
    
    def __init__(self):
        """Initialize the code generator."""
        self.logger = get_logger(__name__)
        
        # Code generation templates and prompts
        self.templates = self._load_templates()
        self.prompts = self._load_prompts()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load code generation templates."""
        return {
            "web_app": {
                "structure": [
                    "app.py", "requirements.txt", "README.md", "config.py",
                    "static/", "templates/", "models/", "services/", "tests/"
                ],
                "tech_stack": TechStack.PYTHON_FLASK,
                "dependencies": {
                    "flask": "^2.3.0",
                    "sqlalchemy": "^2.0.0",
                    "pytest": "^7.4.0"
                }
            },
            "chatbot": {
                "structure": [
                    "bot.py", "config.py", "handlers/", "models/", "utils/",
                    "requirements.txt", "README.md", "tests/"
                ],
                "tech_stack": TechStack.PYTHON_FASTAPI,
                "dependencies": {
                    "fastapi": "^0.104.0",
                    "uvicorn": "^0.24.0",
                    "openai": "^1.3.0"
                }
            },
            "data_analyzer": {
                "structure": [
                    "analyzer.py", "data_loader.py", "visualizations.py",
                    "requirements.txt", "README.md", "examples/", "tests/"
                ],
                "tech_stack": TechStack.PYTHON_STREAMLIT,
                "dependencies": {
                    "streamlit": "^1.28.0",
                    "pandas": "^2.1.0",
                    "plotly": "^5.17.0"
                }
            }
        }
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load AI prompts for different generation tasks."""
        return {
            "project_analysis": """Analyze the following project description and provide a detailed breakdown:

Description: {description}

Please provide:
1. Project type classification
2. Recommended technology stack
3. Key features to implement
4. Architecture recommendations
5. Security considerations
6. Performance optimizations
7. Testing strategy

Format your response as JSON with these keys:
- project_type
- tech_stack
- features
- architecture
- security
- performance
- testing
""",
            
            "code_generation": """Generate professional, production-ready code for the following application:

Project: {project_name}
Type: {project_type}
Tech Stack: {tech_stack}
Description: {description}

Requirements:
- Use best practices and design patterns
- Include proper error handling and validation
- Add comprehensive documentation and type hints
- Follow language-specific style guidelines
- Include unit tests where appropriate
- Make the code modular and maintainable
- Consider security best practices
- Include configuration management
- Add logging and monitoring

Generate the complete application structure with all necessary files.
""",
            
            "file_structure": """Create a professional file structure for a {project_type} application using {tech_stack}.

Requirements:
- Follow industry best practices
- Include all necessary configuration files
- Organize code into logical modules
- Include documentation and testing directories
- Consider deployment and CI/CD needs

Return the file structure as a JSON array with objects containing:
- path: file/directory path
- type: "file" or "directory"
- description: brief description of purpose
- content: file content (for files only)
"""
        }
    
    async def generate_project(
        self, 
        description: str, 
        project_name: str,
        user_id: str,
        ai_provider: str = "openai",
        ai_api_key: str = "",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate a complete project from description.
        
        Args:
            description: Natural language project description
            project_name: Name of the project
            user_id: ID of the user requesting generation
            ai_provider: AI model provider (openai, anthropic, google)
            ai_api_key: API key for the AI provider
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated project data
        """
        try:
            self.logger.info(f"Starting project generation: {project_name}")
            
            # Step 1: Analyze project description
            analysis = await self._analyze_project(description, ai_provider, ai_api_key)
            
            # Step 2: Generate project structure
            structure = await self._generate_project_structure(
                analysis, project_name, ai_provider, ai_api_key
            )
            
            # Step 3: Generate source code
            source_code = await self._generate_source_code(
                analysis, structure, project_name, ai_provider, ai_api_key
            )
            
            # Step 4: Generate additional files
            additional_files = await self._generate_additional_files(
                analysis, project_name, ai_provider, ai_api_key
            )
            
            # Step 5: Compile final project
            project_data = self._compile_project(
                project_name, description, analysis, structure, 
                source_code, additional_files, user_id
            )
            
            self.logger.info(f"Project generation completed: {project_name}")
            return project_data
            
        except Exception as e:
            self.logger.error(f"Project generation failed: {str(e)}")
            raise
    
    async def _analyze_project(
        self, 
        description: str, 
        ai_provider: str, 
        ai_api_key: str
    ) -> Dict[str, Any]:
        """Analyze project description using AI."""
        try:
            # Get AI model
            ai_model = get_ai_model(ai_provider, ai_api_key)
            
            # Prepare prompt
            prompt = self.prompts["project_analysis"].format(description=description)
            
            # Create request
            request = AIModelRequest(
                prompt=prompt,
                model=ai_model.model_name,
                max_tokens=2000,
                temperature=0.3
            )
            
            # Generate analysis
            response = await ai_model.generate_text(request)
            
            if not response.is_success():
                raise Exception(f"AI analysis failed: {response.error}")
            
            # Parse JSON response
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                analysis = self._extract_json_from_text(response.content)
            
            # Validate analysis
            required_keys = ["project_type", "tech_stack", "features"]
            for key in required_keys:
                if key not in analysis:
                    raise ValueError(f"Missing required analysis key: {key}")
            
            self.logger.info(f"Project analysis completed: {analysis['project_type']}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Project analysis failed: {str(e)}")
            raise
    
    async def _generate_project_structure(
        self, 
        analysis: Dict[str, Any], 
        project_name: str,
        ai_provider: str, 
        ai_api_key: str
    ) -> List[Dict[str, Any]]:
        """Generate project file structure."""
        try:
            # Get AI model
            ai_model = get_ai_model(ai_provider, ai_api_key)
            
            # Prepare prompt
            prompt = self.prompts["file_structure"].format(
                project_type=analysis.get("project_type", "web application"),
                tech_stack=analysis.get("tech_stack", "Python")
            )
            
            # Create request
            request = AIModelRequest(
                prompt=prompt,
                model=ai_model.model_name,
                max_tokens=3000,
                temperature=0.2
            )
            
            # Generate structure
            response = await ai_model.generate_text(request)
            
            if not response.is_success():
                raise Exception(f"Structure generation failed: {response.error}")
            
            # Parse structure
            try:
                structure = json.loads(response.content)
            except json.JSONDecodeError:
                structure = self._extract_json_from_text(response.content)
            
            # Validate structure
            if not isinstance(structure, list):
                raise ValueError("Invalid structure format: expected list")
            
            self.logger.info(f"Project structure generated: {len(structure)} items")
            return structure
            
        except Exception as e:
            self.logger.error(f"Structure generation failed: {str(e)}")
            raise
    
    async def _generate_source_code(
        self, 
        analysis: Dict[str, Any], 
        structure: List[Dict[str, Any]], 
        project_name: str,
        ai_provider: str, 
        ai_api_key: str
    ) -> Dict[str, Any]:
        """Generate source code for the project."""
        try:
            # Get AI model
            ai_model = get_ai_model(ai_provider, ai_api_key)
            
            # Prepare prompt
            prompt = self.prompts["code_generation"].format(
                project_name=project_name,
                project_type=analysis.get("project_type", "web application"),
                tech_stack=analysis.get("tech_stack", "Python"),
                description=analysis.get("description", "")
            )
            
            # Create request
            request = AIModelRequest(
                prompt=prompt,
                model=ai_model.model_name,
                max_tokens=8000,
                temperature=0.1
            )
            
            # Generate code
            response = await ai_model.generate_code(request)
            
            if not response.is_success():
                raise Exception(f"Code generation failed: {response.error}")
            
            # Parse and organize code
            source_code = self._parse_generated_code(response.content, structure)
            
            self.logger.info(f"Source code generated: {len(source_code)} files")
            return source_code
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            raise
    
    async def _generate_additional_files(
        self, 
        analysis: Dict[str, Any], 
        project_name: str,
        ai_provider: str, 
        ai_api_key: str
    ) -> Dict[str, Any]:
        """Generate additional project files (README, requirements, etc.)."""
        try:
            additional_files = {}
            
            # Generate README
            readme_content = await self._generate_readme(
                project_name, analysis, ai_provider, ai_api_key
            )
            additional_files["README.md"] = readme_content
            
            # Generate requirements.txt
            requirements_content = self._generate_requirements(analysis)
            additional_files["requirements.txt"] = requirements_content
            
            # Generate .gitignore
            gitignore_content = self._generate_gitignore(analysis)
            additional_files[".gitignore"] = gitignore_content
            
            # Generate Dockerfile if applicable
            if analysis.get("tech_stack") in ["python", "node"]:
                dockerfile_content = await self._generate_dockerfile(
                    analysis, ai_provider, ai_api_key
                )
                additional_files["Dockerfile"] = dockerfile_content
            
            self.logger.info(f"Additional files generated: {len(additional_files)} files")
            return additional_files
            
        except Exception as e:
            self.logger.error(f"Additional files generation failed: {str(e)}")
            raise
    
    def _compile_project(
        self, 
        project_name: str, 
        description: str, 
        analysis: Dict[str, Any], 
        structure: List[Dict[str, Any]], 
        source_code: Dict[str, Any], 
        additional_files: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """Compile all generated components into final project."""
        try:
            # Merge all files
            all_files = {**source_code, **additional_files}
            
            # Create project data
            project_data = {
                "name": project_name,
                "description": description,
                "analysis": analysis,
                "structure": structure,
                "source_code": all_files,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "generator_version": "1.0.0",
                    "total_files": len(all_files),
                    "total_lines": self._count_total_lines(all_files),
                    "tech_stack": analysis.get("tech_stack"),
                    "project_type": analysis.get("project_type"),
                },
                "dependencies": self._extract_dependencies(analysis),
                "deployment": self._generate_deployment_config(analysis),
                "testing": self._generate_testing_config(analysis),
            }
            
            self.logger.info(f"Project compilation completed: {project_name}")
            return project_data
            
        except Exception as e:
            self.logger.error(f"Project compilation failed: {str(e)}")
            raise
    
    def _parse_generated_code(
        self, 
        content: str, 
        structure: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse generated code content into organized files."""
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        files = {}
        
        # Split content by file markers (assuming AI generates with clear file separators)
        file_sections = re.split(r'```\w*:([^\n]+)\n', content)
        
        for i in range(1, len(file_sections), 2):
            if i + 1 < len(file_sections):
                filename = file_sections[i].strip()
                file_content = file_sections[i + 1].strip()
                
                if filename and file_content:
                    files[filename] = {
                        "content": file_content,
                        "type": "file",
                        "size": len(file_content),
                        "lines": len(file_content.split('\n'))
                    }
        
        # If no files were parsed, create a default structure
        if not files:
            files["main.py"] = {
                "content": content,
                "type": "file",
                "size": len(content),
                "lines": len(content.split('\n'))
            }
        
        return files
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response."""
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: return basic structure
        return {
            "project_type": "web_app",
            "tech_stack": "python",
            "features": ["basic functionality"],
            "architecture": "monolithic",
            "security": "basic",
            "performance": "standard",
            "testing": "unit tests"
        }
    
    def _count_total_lines(self, files: Dict[str, Any]) -> int:
        """Count total lines of code across all files."""
        total_lines = 0
        for file_data in files.values():
            if isinstance(file_data, dict) and "lines" in file_data:
                total_lines += file_data["lines"]
        return total_lines
    
    def _extract_dependencies(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract dependencies based on analysis."""
        # This would be more sophisticated in production
        base_deps = {
            "python": {
                "pytest": "^7.4.0",
                "black": "^23.11.0",
                "flake8": "^6.1.0"
            }
        }
        
        tech_stack = analysis.get("tech_stack", "python").lower()
        if tech_stack in base_deps:
            return base_deps[tech_stack]
        
        return {}
    
    def _generate_deployment_config(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment configuration."""
        return {
            "platforms": ["local", "docker"],
            "requirements": ["python 3.11+", "pip"],
            "commands": {
                "install": "pip install -r requirements.txt",
                "run": "python main.py",
                "test": "pytest"
            }
        }
    
    def _generate_testing_config(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate testing configuration."""
        return {
            "framework": "pytest",
            "coverage": True,
            "test_types": ["unit", "integration"],
            "commands": {
                "test": "pytest",
                "coverage": "pytest --cov=.",
                "lint": "flake8 ."
            }
        }
    
    async def _generate_readme(
        self, 
        project_name: str, 
        analysis: Dict[str, Any], 
        ai_provider: str, 
        ai_api_key: str
    ) -> str:
        """Generate README.md content."""
        # Simplified README generation
        readme = f"""# {project_name}

{analysis.get('description', 'A professional application generated by HyperAI Builder.')}

## Features

"""
        
        for feature in analysis.get("features", []):
            readme += f"- {feature}\n"
        
        readme += f"""
## Tech Stack

- **Type**: {analysis.get('project_type', 'Web Application')}
- **Technology**: {analysis.get('tech_stack', 'Python')}
- **Architecture**: {analysis.get('architecture', 'Monolithic')}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Testing

```bash
pytest
```

## Security

{analysis.get('security', 'Basic security measures implemented.')}

## Performance

{analysis.get('performance', 'Standard performance optimizations applied.')}

## License

MIT License

Generated by [HyperAI Builder](https://hyperai.com)
"""
        
        return readme
    
    def _generate_requirements(self, analysis: Dict[str, Any]) -> str:
        """Generate requirements.txt content."""
        # This would be more sophisticated in production
        return """# Core dependencies
flask>=2.3.0
sqlalchemy>=2.0.0

# Development dependencies
pytest>=7.4.0
black>=23.11.0
flake8>=6.1.0

# Generated by HyperAI Builder
"""
    
    def _generate_gitignore(self, analysis: Dict[str, Any]) -> str:
        """Generate .gitignore content."""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Generated by HyperAI Builder
"""
    
    async def _generate_dockerfile(
        self, 
        analysis: Dict[str, Any], 
        ai_provider: str, 
        ai_api_key: str
    ) -> str:
        """Generate Dockerfile content."""
        return """# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]

# Generated by HyperAI Builder
"""