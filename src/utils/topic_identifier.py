from langchain_core.prompts import ChatPromptTemplate
from langchain_together import ChatTogether

class TopicIdentifier:
    """
    Class to identify physics topics from user input using LLM.
    """
    
    def __init__(self, config_loader):
        """
        Initialize TopicIdentifier with configurations.
        
        Args:
            config_loader: ConfigLoader instance with access to prompt and model configs
        """
        # Load necessary configurations
        self.prompt_config = config_loader.load_prompt_config()
        self.model_config = config_loader.load_model_config()
        
        # Initialize the prompt template and model
        self._initialize_components()

    def _initialize_components(self):

        # Get model configuration
        model_name = self.model_config['model']
        temperature = self.model_config['temperature']['evaluation_temperature']
        
        # Create LLM instance
        self.llm = ChatTogether(
            model=model_name,
            temperature=temperature
        )
        
        # Get prompt template
        topic_identifier_prompt = self.prompt_config['prompts']['topic_identifier_prompt']
        
        # Create prompt template
        self.topic_check = ChatPromptTemplate.from_messages([
            ("system", topic_identifier_prompt),
            ("placeholder", "{messages}")
        ])
        
        # Create the chain
        self.chain = self.topic_check | self.llm

    def identify_topic(self, input_text: str) -> str:
        """
        Identify the physics topic from the input text.
        
        Args:
            input_text (str): User input text containing physics topic
            
        Returns:
            str: Identified physics topic
        """
        try:
            # Invoke the chain
            result = self.chain.invoke(
                {"messages": [("user", input_text)]}
            )
            
            # Extract and clean the topic
            topic = result.content.strip()
            
            return topic
            
        except Exception as e:
            raise ValueError(f"Error identifying topic: {str(e)}")

    def __call__(self, input_text: str) -> str:
        """
        Make the class callable to match the tool interface.
        
        Args:
            input_text (str): User input text
            
        Returns:
            str: Identified physics topic
        """
        return self.identify_topic(input_text)