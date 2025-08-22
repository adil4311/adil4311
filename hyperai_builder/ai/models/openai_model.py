"""
OpenAI model integration for HyperAI Builder.

Provides integration with OpenAI's GPT models including GPT-4o.
"""

import asyncio
from typing import Any, Dict, List, Optional

import openai
from openai import AsyncOpenAI

from .base import BaseAIModel, AIModelRequest, AIModelResponse

from ...core.logging import get_logger

logger = get_logger(__name__)


class OpenAIModel(BaseAIModel):
    """OpenAI model integration."""
    
    # OpenAI model pricing (per 1K tokens)
    PRICING = {
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        """Initialize OpenAI model."""
        super().__init__(api_key, model_name)
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Set default parameters
        self.max_tokens = 4000
        self.temperature = 0.7
        
        # Validate model name
        if model_name not in self.PRICING:
            logger.warning(f"Unknown model {model_name}, using default pricing")
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate OpenAI API key format."""
        # OpenAI API keys start with 'sk-' and are typically 51 characters long
        return api_key.startswith('sk-') and len(api_key) >= 20
    
    async def generate_text(self, request: AIModelRequest) -> AIModelResponse:
        """Generate text using OpenAI model."""
        try:
            # Prepare messages
            messages = self._prepare_messages(request)
            
            # Prepare parameters
            params = {
                "model": request.model or self.model_name,
                "messages": messages,
                "max_tokens": request.max_tokens or self.max_tokens,
                "temperature": request.temperature or self.temperature,
                "stream": request.stream,
            }
            
            # Add additional parameters
            if request.additional_params:
                params.update(request.additional_params)
            
            self.logger.debug(f"Generating text with OpenAI model {params['model']}")
            
            if request.stream:
                return await self._generate_streaming(params)
            else:
                return await self._generate_non_streaming(params)
        
        except Exception as e:
            self.logger.error(f"OpenAI text generation failed: {str(e)}")
            return AIModelResponse(
                content="",
                model=self.model_name,
                error=f"OpenAI API error: {str(e)}"
            )
    
    async def generate_code(self, request: AIModelRequest) -> AIModelResponse:
        """Generate code using OpenAI model with code-specific prompts."""
        try:
            # Enhance prompt for code generation
            enhanced_prompt = self._enhance_code_prompt(request.prompt)
            
            # Create code-specific request
            code_request = AIModelRequest(
                prompt=enhanced_prompt,
                model=request.model or self.model_name,
                max_tokens=request.max_tokens or 8000,  # Higher token limit for code
                temperature=request.temperature or 0.1,  # Lower temperature for code
                system_message=request.system_message or self._get_code_system_message(),
                additional_params=request.additional_params
            )
            
            return await self.generate_text(code_request)
        
        except Exception as e:
            self.logger.error(f"OpenAI code generation failed: {str(e)}")
            return AIModelResponse(
                content="",
                model=self.model_name,
                error=f"OpenAI code generation error: {str(e)}"
            )
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs: Any
    ) -> AIModelResponse:
        """Generate chat completion."""
        try:
            # Create request from messages
            request = AIModelRequest(
                prompt="",  # Not used when messages are provided
                model=kwargs.get('model', self.model_name),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                messages=messages,
                additional_params=kwargs
            )
            
            return await self.generate_text(request)
        
        except Exception as e:
            self.logger.error(f"OpenAI chat completion failed: {str(e)}")
            return AIModelResponse(
                content="",
                model=self.model_name,
                error=f"OpenAI chat completion error: {str(e)}"
            )
    
    def _prepare_messages(self, request: AIModelRequest) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API."""
        messages = []
        
        # Add system message if provided
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        
        # Add conversation messages if provided
        if request.messages:
            messages.extend(request.messages)
        else:
            # Add user message from prompt
            messages.append({"role": "user", "content": request.prompt})
        
        return messages
    
    def _enhance_code_prompt(self, prompt: str) -> str:
        """Enhance prompt for better code generation."""
        enhanced = f"""Please generate professional, production-ready code based on the following description:

{prompt}

Requirements:
- Use best practices and design patterns
- Include proper error handling and validation
- Add comprehensive documentation and type hints
- Follow PEP 8 style guidelines (for Python)
- Include unit tests where appropriate
- Make the code modular and maintainable
- Consider security best practices

Please provide the complete, runnable code with all necessary files and dependencies."""
        
        return enhanced
    
    def _get_code_system_message(self) -> str:
        """Get system message for code generation."""
        return """You are an expert software engineer specializing in creating professional, production-ready applications. 

Your code should:
- Be clean, readable, and well-documented
- Follow industry best practices and design patterns
- Include proper error handling and validation
- Be modular, maintainable, and scalable
- Include appropriate tests and documentation
- Follow language-specific conventions and style guides

Always provide complete, runnable code with clear explanations of design decisions."""
    
    async def _generate_non_streaming(self, params: Dict[str, Any]) -> AIModelResponse:
        """Generate non-streaming response."""
        response = await self.client.chat.completions.create(**params)
        
        # Extract content
        content = response.choices[0].message.content or ""
        
        # Calculate usage and cost
        usage = self._extract_usage(response)
        cost = self._calculate_cost(usage)
        
        return AIModelResponse(
            content=content,
            model=params["model"],
            usage=usage,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "model": response.model,
                "id": response.id,
            }
        )
    
    async def _generate_streaming(self, params: Dict[str, Any]) -> AIModelResponse:
        """Generate streaming response."""
        # For now, collect the full response (can be enhanced for real streaming)
        full_content = ""
        
        try:
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            return AIModelResponse(
                content=full_content,
                model=params["model"],
                metadata={"streaming": True}
            )
        
        except Exception as e:
            self.logger.error(f"OpenAI streaming generation failed: {str(e)}")
            return AIModelResponse(
                content=full_content,
                model=params["model"],
                error=f"OpenAI streaming error: {str(e)}"
            )
    
    def _extract_usage(self, response: Any) -> Dict[str, Any]:
        """Extract usage information from OpenAI response."""
        if hasattr(response, 'usage') and response.usage:
            return {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return {}
    
    def _calculate_cost(self, usage: Dict[str, Any]) -> float:
        """Calculate the cost of the request."""
        if not usage or "total_tokens" not in usage:
            return 0.0
        
        model = self.model_name
        if model not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[model]
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        total_cost = input_cost + output_cost
        
        # Add to usage for cost tracking
        usage["cost"] = round(total_cost, 6)
        
        return total_cost
    
    def estimate_cost(
        self, 
        input_tokens: int, 
        output_tokens: int,
        model_name: Optional[str] = None
    ) -> float:
        """Estimate the cost of a request."""
        model = model_name or self.model_name
        
        if model not in self.PRICING:
            return super().estimate_cost(input_tokens, output_tokens, model_name)
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            # Simple health check
            response = await self.client.models.list()
            return True
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        return list(self.PRICING.keys())
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about the model."""
        info = super().get_model_info()
        info.update({
            "provider": "OpenAI",
            "pricing": self.PRICING.get(self.model_name, {}),
            "available_models": self.get_available_models(),
        })
        return info