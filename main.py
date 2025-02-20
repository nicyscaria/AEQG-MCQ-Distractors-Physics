from src.utils.topic_identifier import TopicIdentifier
from src.utils.config_loader import ConfigLoader
from src.question_generators.llm_generator import LLMQuestionGenerator
from src.question_generators.rag_generator import RAGQuestionGenerator
from src.question_generators.conceptmap_generator import ConceptMapQuestionGenerator

def main():
    config_loader = ConfigLoader()
    topic_identifier = TopicIdentifier(config_loader)
    
    test_input = input("Enter your query: ")
    topic = topic_identifier(test_input)
    
    # Each generator only needs to implement its specific parts
    llm_gen = LLMQuestionGenerator(config_loader)
    rag_gen = RAGQuestionGenerator(config_loader)
    conceptmap_gen = ConceptMapQuestionGenerator(config_loader)
    
    # The common logic is handled by the base class
    llm_results = llm_gen.generate_all_questions(topic, grade = 9, context=None)
    rag_results = rag_gen.generate_all_questions(topic, grade = 9, context=None)
    conceptmap_results = conceptmap_gen.generate_all_questions(topic, grade = 9, context=None)
    
    return llm_results, rag_results, conceptmap_results

if __name__ == "__main__":
    main()