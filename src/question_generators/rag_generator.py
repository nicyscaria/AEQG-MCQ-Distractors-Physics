from src.question_generators.base import BaseQuestionGenerator
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_together import ChatTogether
from typing import Dict, Optional
import json
from langchain_community.vectorstores import Chroma
import os

class RAGQuestionGenerator(BaseQuestionGenerator):
    """Question generator using RAG (Retrieval Augmented Generation) approach."""
    
    def _initialize_components(self):
        """Initialize LLM, prompt template, and retriever components."""
        self.llm = ChatTogether(
            model=self.model_config['model'],
            temperature=self.model_config['temperature']['generation_temperature']
        )
        
        # Get method-specific prompt that includes context
        input = self.prompt_config['prompts']['rag_prompt']
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Please make sure you follow user instructions."),
            ("human", input)
        ])
        
        # Initialize retriever settings
        self.db_dir = self.model_config['vector_store']['db_dir']
        self.store_name = self.model_config['vector_store']['store_name']
        self.top_k = self.model_config['vector_store']['top_k']
        
        # Initialize HuggingFace embeddings
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=self.model_config['vector_store']['embedding_model'],
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def needs_context(self) -> bool:
        return True

    def get_method_name(self) -> str:
        return "RAG"
    
    def _query_vector_store(self, query: str) -> str:
        """Query the vector store to get relevant context."""
        try:
            # Get the project root directory
            project_root = os.getcwd()
            persistent_directory = os.path.join(project_root, 'data', self.store_name)
            
            print(f"Looking for vector store in: {persistent_directory}")
            
            if not os.path.exists(persistent_directory):
                print(f"Current working directory: {project_root}")
                raise ValueError(f"Vector store directory {persistent_directory} does not exist")

            db = Chroma(
                persist_directory=persistent_directory,
                embedding_function=self.embedding_function,
            )

            retriever = db.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k}
            )
            
            documents = retriever.invoke(query)
            
            if not documents:
                print(f"Warning: No relevant documents found for query: {query}")
                return ""
                
            # Combine all retrieved documents into a single context string
            context = " ".join(doc.page_content for doc in documents)
            
            print(f"Retrieved context length: {len(context)} characters")
            return context
            
        except Exception as e:
            print(f"Error querying vector store: {str(e)}")
            return ""

    def generate_question(self, topic: str, skill: str, output_format_generation: str, grade: int, context: Optional[str] = None) -> Optional[Dict]:
        """
        Generate a single question using RAG approach.
        Uses retrieved context to enhance question generation.
        """
        try:

            if not context:
                context = self._query_vector_store(topic)
                print(f"Context retrieved for {skill}")
            
            prompt = self.prompt_template.format(
                skill=skill,
                topic=topic,
                grade=grade,
                context=context,
                skill_requirement=self.skill_config['skills']['requirements'][skill],
                output_format_generation=output_format_generation
            )
            
            response = self.llm.invoke(prompt)
            
            cleaned_content = response.content.strip()
            
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:-3]
            
            question_json = json.loads(cleaned_content)
            return question_json
            
        except json.JSONDecodeError as e:
            return None
        except Exception as e:
            print(f"Error generating question for {skill}: {str(e)}")
            return None

# Example usage:
# if __name__ == "__main__":
#     config_loader = ConfigLoader()
#     topic_identifier = TopicIdentifier(config_loader)
#     test_input = "Create 5 questions on work-energy theorem"
#     topic = topic_identifier(test_input)
#     
#     rag_gen = RAGQuestionGenerator(config_loader)
#     rag_results = rag_gen.generate_all_questions(topic, grade=9, context=None)  # Context will be retrieved internally
