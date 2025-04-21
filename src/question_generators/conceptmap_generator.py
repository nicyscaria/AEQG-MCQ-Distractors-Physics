from src.question_generators.base import BaseQuestionGenerator
from langchain_together import ChatTogether
from langchain_community.utilities import SQLDatabase
from typing import Dict, Optional, List
from dotenv import load_dotenv
import os
import json

class ConceptMapGenerator:
    """Handles the generation of individual questions."""
    def __init__(self, llm, prompt):
        self.llm = llm
        self.base_prompt = prompt
    
    def generate_question(self, skill: str, skill_requirement: str, topic: str, context: str, question_history: List[str], grade: int, output_format_generation: str) -> Dict:
        """Generate a single question."""
        prompt = self.base_prompt.format(
            skill=skill,
            skill_requirement=skill_requirement,
            topic=topic,
            context=context,
            question_history=question_history,
            grade=grade,
            output_format_generation=output_format_generation
        )
        response = self.llm.invoke(prompt)
        cleaned_content = response.content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:-3]
        return json.loads(cleaned_content)

class ConceptMapEvaluator:
    """Evaluates questions for validity and uniqueness."""
    def __init__(self, llm, evaluation_prompt):
        self.llm = llm
        self.evaluation_prompt = evaluation_prompt
    
    def evaluate_question(self, question: Dict, previous_questions: List[str], output_format_evaluation: str) -> Dict:
        """Evaluate a question based on defined criteria."""
        try:
            prompt = self.evaluation_prompt.format(
                question=json.dumps(question),
                previous_questions=json.dumps(previous_questions),
                output_format_evaluation=output_format_evaluation
            )
            response = self.llm.invoke(prompt)
            evaluation = json.loads(response.content)
            return evaluation
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            return {
                "valid": False,
                "1": {"uniqueness": False, "uniqueness_issues": "Failed to evaluate"},
                "2": {"answer": False, "answer_issues": "Failed to evaluate"}
            }

class ConceptMapFixer:
    """Fixes invalid questions."""
    def __init__(self, llm, fix_prompt):
        self.llm = llm
        self.fix_prompt = fix_prompt

    def fix_question(self, question: Dict, evaluation: Dict, previous_questions: List[str]) -> Optional[Dict]:
        """Fix question based on evaluation results."""
        try:
            # Apply fix based on evaluation result
            if not evaluation["1"]["uniqueness"]:
                # Generate new question for uniqueness issues
                prompt = self.fix_prompt.format(
                    question=json.dumps(question),
                    previous_questions=json.dumps(previous_questions),
                    evaluation=json.dumps(evaluation),
                    skill=question["skill"]  # Added skill from question
                )
            else:
                prompt = self.fix_prompt.format(
                    question=json.dumps(question),
                    evaluation=json.dumps(evaluation),
                    skill=question["skill"]  # Added skill from question
                )

            response = self.llm.invoke(prompt)
            fixed_question = json.loads(response.content)
            return fixed_question

        except Exception as e:
            print(f"Fix error: {str(e)}")
            return None

class ConceptMapQuestionGenerator(BaseQuestionGenerator):
    """Question generator using concept map and database approach."""
    
    def _initialize_components(self):
        """Initialize all components."""
        load_dotenv()
        
        self.llm = ChatTogether(
            model=self.model_config['model'],
            temperature=self.model_config['temperature']['generation_temperature']
        )
        
        self.db = SQLDatabase.from_uri(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        
        self.generator = ConceptMapGenerator(
            self.llm,
            self.prompt_config['prompts']['conceptmap_prompt']
        )
        
        self.evaluator = ConceptMapEvaluator(
            self.llm,
            self.prompt_config['prompts']['conceptmap_evaluation_prompt']
        )
        
        self.fixer = ConceptMapFixer(
            self.llm,
            self.prompt_config['prompts']['conceptmap_fix_prompt']
        )
        
        self.topic_matcher_template = self.prompt_config['prompts']['topic_identification_conceptmap_prompt']

        self.generated_questions = []
    
    def needs_context(self) -> bool:
        return True

    def get_method_name(self) -> str:
        return "ConceptMap"

    def _find_matching_topic_id(self, topic: str) -> str:
        """Find matching topic ID from database."""
        try:
            query = "SELECT topic_name, topic_id FROM topics;"
            topics = self.db.run_no_throw(query)
            
            if not topics:
                raise ValueError("No topics found in database")
            
            prompt = self.topic_matcher_template.format(
                topic_of_interest=topic,
                topics="\n".join(topics)
            )
            
            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error finding matching topic: {str(e)}")
            return None

    def _get_context_from_db(self, topic_id: str) -> str:
        """Get context from database using topic ID."""
        try:
            query = f"""WITH topic_search AS 
            (SELECT topic_id FROM topics 
            WHERE topic_id ILIKE '{topic_id}')
            SELECT s.subtopic_name, 
            s.description, 
            s.mathematical_formulation,
            s.prerequisites,
            s.misconceptions,
            s.engineering_applications,
            s.cross_cutting_topics,
            s.analogies
            FROM subtopics s 
            JOIN topic_search ts 
            ON s.topic_id = ts.topic_id 
            ORDER BY RANDOM()
            LIMIT 3;"""
            
            return self.db.run(query)
            
        except Exception as e:
            print(f"Error getting context from DB: {str(e)}")
            return None

    def _generate_valid_question(
        self,
        skill: str,
        topic: str,
        output_format_generation: str,
        grade: int,
        context: str,
        max_attempts: int = 2
    ) -> Optional[Dict]:
        """Generate and validate a question with multiple attempts."""
        for attempt in range(max_attempts):
            print(f"\nAttempt {attempt + 1}/{max_attempts}")
            
            # Get question history (just the questions, not the full objects)
            question_history = [q['question'] for q in self.generated_questions] if self.generated_questions else []
            
            try:
                # Generate initial question
                question = self.generator.generate_question(
                    skill=skill,
                    skill_requirement=self.skill_config['skills']['requirements'][skill],
                    topic=topic,
                    context=context,
                    question_history=question_history,
                    grade=grade,
                    output_format_generation=output_format_generation
                )
                
                # Get the evaluation format from config
                output_format_evaluation = self.output_config['formats']['evaluation']
                
                # Evaluate the question
                evaluation = self.evaluator.evaluate_question(
                    question, 
                    question_history,
                    output_format_evaluation
                )
                
                if evaluation.get("valid", False):
                    return question
                
                # Try fixing the question if invalid
                fixed_question = self.fixer.fix_question(question, evaluation, question_history)
                if fixed_question:
                    # Re-evaluate fixed question
                    fixed_evaluation = self.evaluator.evaluate_question(
                        fixed_question, 
                        question_history,
                        output_format_evaluation
                    )
                    
                    if fixed_evaluation.get("valid", False):
                        return fixed_question
                
            except Exception as e:
                print(f"Error in attempt {attempt + 1}: {str(e)}")
                continue
        
        return None

    def generate_question(
        self,
        topic: str,
        skill: str,
        output_format_generation: str,
        grade: int,
        context: Optional[str] = None
    ) -> Optional[Dict]:
        """Generate a single question."""
        try:
            # Get context from database if not provided
            if not context:
                topic_id = self._find_matching_topic_id(topic)
                if not topic_id:
                    raise ValueError("Could not find matching topic ID")
                    
                context = self._get_context_from_db(topic_id)
                if not context:
                    raise ValueError("Could not retrieve context from database")
            
            # Generate and validate question
            question = self._generate_valid_question(
                skill=skill,
                topic=topic,
                output_format_generation=output_format_generation,
                grade=grade,
                context=context
            )
            
            if question:
                self.generated_questions.append(question)
                
            return question
            
        except Exception as e:
            print(f"Error generating question for {skill}: {str(e)}")
            return None

# Example usage:
# if __name__ == "__main__":
#     config_loader = ConfigLoader()
#     conceptmap_gen = ConceptMapQuestionGenerator(config_loader)
#     results = conceptmap_gen.generate_all_questions("work-energy theorem", grade=12)
