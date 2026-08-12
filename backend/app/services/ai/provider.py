"""
Abstract AI Provider Interface for Oyster360
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, context: List[str]) -> str:
        pass

    @abstractmethod
    def analyze_image(self, image_url: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def predict_yield(self, features: Dict[str, Any]) -> Dict[str, Any]:
        pass