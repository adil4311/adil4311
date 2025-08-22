"""
AI Model Factory for HyperAI Builder.

Creates and manages different AI model instances based on configuration.
"""

from typing import Any, Dict, List, Optional, Type

from .base import BaseAIModel
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel
from .google_model import GoogleModel

from ...core.logging import get_logger

logger = get_logger(__name__)


class AIModelFactory:
    """Factory for creating AI model instances."""
    
    # Registry of available model classes
    MODEL_REGISTRY = {
        "openai": OpenAIModel,
        "anthropic": AnthropicModel,
        "google": GoogleModel,
    }
    
    def __init__(self):
        """Initialize the AI model factory."""
        self._instances: Dict[str, BaseAIModel] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def register_model(
        self, 
        provider: str, 
        model_class: Type[BaseAIModel]
    ) -> None:
        """Register a new model class."""
        self.MODEL_REGISTRY[provider] = model_class
        logger.info(f"Registered AI model provider: {provider}")
    
    def create_model(
        self, 
        provider: str, 
        api_key: str, 
        model_name: str = "default",
        **kwargs: Any
    ) -> BaseAIModel:
        """Create a new AI model instance."""
        if provider not in self.MODEL_REGISTRY:
            raise ValueError(f"Unknown AI model provider: {provider}")
        
        try:
            model_class = self.MODEL_REGISTRY[provider]
            model_instance = model_class(api_key, model_name, **kwargs)
            
            # Store instance
            instance_key = f"{provider}:{model_name}"
            self._instances[instance_key] = model_instance
            
            logger.info(f"Created AI model instance: {instance_key}")
            return model_instance
        
        except Exception as e:
            logger.error(f"Failed to create AI model {provider}:{model_name}: {str(e)}")
            raise
    
    def get_model(
        self, 
        provider: str, 
        model_name: str = "default"
    ) -> Optional[BaseAIModel]:
        """Get an existing AI model instance."""
        instance_key = f"{provider}:{model_name}"
        return self._instances.get(instance_key)
    
    def get_or_create_model(
        self, 
        provider: str, 
        api_key: str, 
        model_name: str = "default",
        **kwargs: Any
    ) -> BaseAIModel:
        """Get existing model or create new one."""
        existing_model = self.get_model(provider, model_name)
        if existing_model:
            return existing_model
        
        return self.create_model(provider, api_key, model_name, **kwargs)
    
    def list_providers(self) -> List[str]:
        """Get list of available AI model providers."""
        return list(self.MODEL_REGISTRY.keys())
    
    def list_instances(self) -> List[str]:
        """Get list of created model instances."""
        return list(self._instances.keys())
    
    def remove_model(self, provider: str, model_name: str = "default") -> bool:
        """Remove a model instance."""
        instance_key = f"{provider}:{model_name}"
        if instance_key in self._instances:
            del self._instances[instance_key]
            logger.info(f"Removed AI model instance: {instance_key}")
            return True
        return False
    
    def clear_instances(self) -> None:
        """Clear all model instances."""
        count = len(self._instances)
        self._instances.clear()
        logger.info(f"Cleared {count} AI model instances")
    
    def get_model_info(self, provider: str, model_name: str = "default") -> Optional[Dict[str, Any]]:
        """Get information about a specific model instance."""
        model = self.get_model(provider, model_name)
        if model:
            return model.get_model_info()
        return None
    
    def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all model instances."""
        results = {}
        
        for instance_key, model in self._instances.items():
            try:
                # Note: This is a synchronous health check, but models are async
                # In a real implementation, you'd want to handle this properly
                results[instance_key] = True  # Placeholder
            except Exception as e:
                logger.error(f"Health check failed for {instance_key}: {str(e)}")
                results[instance_key] = False
        
        return results
    
    def get_total_cost(self) -> float:
        """Get total cost across all model instances."""
        total_cost = 0.0
        
        for model in self._instances.values():
            # This would need to be implemented based on actual usage tracking
            # For now, return 0
            pass
        
        return total_cost
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all models."""
        stats = {
            "total_instances": len(self._instances),
            "providers": self.list_providers(),
            "instances": self.list_instances(),
            "total_cost": self.get_total_cost(),
        }
        
        return stats


# Global factory instance
ai_model_factory = AIModelFactory()


def get_ai_model(
    provider: str, 
    api_key: str, 
    model_name: str = "default",
    **kwargs: Any
) -> BaseAIModel:
    """Convenience function to get or create an AI model."""
    return ai_model_factory.get_or_create_model(provider, api_key, model_name, **kwargs)


def list_ai_providers() -> List[str]:
    """Get list of available AI model providers."""
    return ai_model_factory.list_providers()


def get_ai_model_info(provider: str, model_name: str = "default") -> Optional[Dict[str, Any]]:
    """Get information about an AI model."""
    return ai_model_factory.get_model_info(provider, model_name)


def clear_ai_models() -> None:
    """Clear all AI model instances."""
    ai_model_factory.clear_instances()