from abc import ABC, abstractmethod
from typing import Dict, Optional
import json

class BaseQuestionGenerator(ABC):
    """Abstract base class for question generators."""
    
    def __init__(self, config_loader):
        self.model_config = config_loader.load_model_config()
        self.prompt_config = config_loader.load_prompt_config()
        self.skill_config = config_loader.load_skill_config()
        self.output_config = config_loader.load_output_config()
        self._initialize_components()
    
    @abstractmethod
    def needs_context(self) -> bool:
        """Return True if generator requires context"""
        pass

    @abstractmethod
    def _initialize_components(self):
        """Initialize method-specific components (LLM, prompts, etc.)"""
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        """Return the name of the generation method."""
        pass

    @abstractmethod
    def generate_question(self, topic: str, skill: str, output_format_generation: str, grade: int, context: Optional[str] = None) -> Optional[Dict]:
        """Generate a single question. To be implemented by each method."""
        pass

    def generate_all_questions(self, topic: str, grade: int, context: str) -> Dict:
        """
        Generate questions for all skills. Common implementation for all methods.
        Each method only needs to implement generate_question().
        """
        responses = {
            "topic": topic,
            "questions": []
        }
        
        for skill in self.skill_config['skills']['list']:
            output_format_generation = self.output_config['formats']['generation']
            
            if self.needs_context():
                question = self.generate_question(topic, skill, output_format_generation, grade, context)
            else:
                question = self.generate_question(topic, skill, output_format_generation, grade)
                
            if question:
                responses["questions"].append(question)
        
        self.save_to_json(responses, topic)
        return responses

    def save_to_json(self, data: Dict, topic: str) -> None:
        """Save generated questions to JSON file."""
        model_name = self.model_config['model'].split('/')[-1]
        method = self.get_method_name()
        filename = f"{method}_{topic}_{model_name}.json"
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)