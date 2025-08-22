"""
Base AI model interface for HyperAI Builder.

Defines the common interface for all AI model integrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from ...core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AIModelResponse:
    """Response from AI model."""
    
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def is_success(self) -> bool:
        """Check if the response was successful."""
        return self.error is None
    
    def get_tokens_used(self) -> int:
        """Get the number of tokens used."""
        if self.usage and 'total_tokens' in self.usage:
            return self.usage['total_tokens']
        return 0
    
    def get_cost(self) -> float:
        """Get the estimated cost of the request."""
        if self.usage and 'cost' in self.usage:
            return self.usage['cost']
        return 0.0


@dataclass
class AIModelRequest:
    """Request to AI model."""
    
    prompt: str
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    system_message: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.prompt and not self.messages:
            raise ValueError("Either prompt or messages must be provided")
        
        if self.temperature is not None and not (0 <= self.temperature <= 2):
            raise ValueError("Temperature must be between 0 and 2")
        
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")


class BaseAIModel(ABC):
    """Base class for AI model integrations."""
    
    def __init__(self, api_key: str, model_name: str = "default"):
        """Initialize AI model."""
        self.api_key = api_key
        self.model_name = model_name
        self.logger = get_logger(f"{self.__class__.__name__}.{model_name}")
        
        # Validate API key
        if not self._validate_api_key(api_key):
            raise ValueError(f"Invalid API key for {self.__class__.__name__}")
    
    @abstractmethod
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate the API key format."""
        pass
    
    @abstractmethod
    async def generate_text(
        self, 
        request: AIModelRequest
    ) -> AIModelResponse:
        """Generate text using the AI model."""
        pass
    
    @abstractmethod
    async def generate_code(
        self, 
        request: AIModelRequest
    ) -> AIModelResponse:
        """Generate code using the AI model."""
        pass
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> AIModelResponse:
        """Generate chat completion."""
        pass
    
    async def generate_with_retry(
        self, 
        request: AIModelRequest,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> AIModelResponse:
        """Generate text with retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Attempt {attempt + 1} for model {self.model_name}")
                return await self.generate_text(request)
            
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}"
                )
                
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All retries failed
        self.logger.error(f"All {max_retries} attempts failed for model {self.model_name}")
        return AIModelResponse(
            content="",
            model=self.model_name,
            error=f"All retry attempts failed: {str(last_error)}"
        )
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in text (rough approximation)."""
        # Rough approximation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    def estimate_cost(
        self, 
        input_tokens: int, 
        output_tokens: int,
        model_name: Optional[str] = None
    ) -> float:
        """Estimate the cost of a request."""
        # This is a base implementation - subclasses should override with actual pricing
        model = model_name or self.model_name
        
        # Default pricing (should be overridden by subclasses)
        input_cost_per_1k = 0.001
        output_cost_per_1k = 0.002
        
        total_cost = (
            (input_tokens / 1000) * input_cost_per_1k +
            (output_tokens / 1000) * output_cost_per_1k
        )
        
        return round(total_cost, 6)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "class": self.__class__.__name__,
            "model_name": self.model_name,
            "supports_streaming": hasattr(self, 'generate_stream'),
            "max_tokens": getattr(self, 'max_tokens', None),
            "supports_chat": hasattr(self, 'chat_completion'),
            "supports_code_generation": hasattr(self, 'generate_code'),
        }
    
    async def health_check(self) -> bool:
        """Check if the model is healthy and accessible."""
        try:
            # Simple health check with minimal tokens
            test_request = AIModelRequest(
                prompt="Hello",
                model=self.model_name,
                max_tokens=5
            )
            
            response = await self.generate_text(test_request)
            return response.is_success()
        
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}({self.model_name})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return f"{self.__class__.__name__}(api_key='***', model_name='{self.model_name}')"