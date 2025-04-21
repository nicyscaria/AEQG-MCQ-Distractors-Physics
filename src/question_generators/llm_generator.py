from src.question_generators.base import BaseQuestionGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_together import ChatTogether
from typing import Dict, Optional
import json

class LLMQuestionGenerator(BaseQuestionGenerator):
    """Question generator using LLM approach."""
    
    def _initialize_components(self):
        """Initialize LLM and prompt template."""
        self.llm = ChatTogether(
            model=self.model_config['model'],
            temperature=self.model_config['temperature']['generation_temperature']
        )
        
        # Get method-specific prompt
        input = self.prompt_config['prompts']['llm_prompt']
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Please make sure you follow user instructions."),
            ("human", input)
        ])
    
    def needs_context(self) -> bool:
        return False

    def get_method_name(self) -> str:
        return "LLM"

    def generate_question(self, topic: str, skill: str, output_format_generation: str, grade: int) -> Optional[Dict]:
        """
        Generate a single question. Only implement the method-specific logic here.
        The rest is handled by the base class.
        """
        try:
            prompt = self.prompt_template.format(
                skill=skill,
                topic=topic,
                grade=grade,
                skill_requirement=self.skill_config['skills']['requirements'][skill],
                output_format_generation=output_format_generation
            )
            
            response = self.llm.invoke(prompt)
            cleaned_content = response.content.strip()
            
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:-3]
            
            return json.loads(cleaned_content)
            
        except Exception as e:
            print(f"Error generating question for {skill}: {str(e)}")
            return None
        
# example generation directly here
# if __name__ == "__main__":
    
#     config_loader = ConfigLoader()
#     topic_identifier = TopicIdentifier(config_loader)
#     test_input = "Create 5 questions on work-energy theorem"
#     topic = topic_identifier(test_input)
    
#     # Each generator only needs to implement its specific parts
#     llm_gen = LLMQuestionGenerator(config_loader)
#     llm_results = llm_gen.generate_all_questions(topic, grade = 9)
