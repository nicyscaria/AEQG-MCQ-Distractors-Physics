import os
import yaml
from dotenv import load_dotenv
from pyprojroot import here


class LoadConfigs:
    def __init__(self) -> None:
        with open(here("configs/cofig.yml")) as cfg:
            agent_config = yaml.load(cfg, Loader=yaml.FullLoader)
            
        self.load_directories(agent_config=agent_config)
        self.load_llm_configs(agent_config=agent_config)
        self.load_models()
        
    
    def load_directories(self, agent_config):
        self.csv_directory = here(agent_config["directories"]["csv_directory"])
    
    def load_llm_configs(self, agent_config):
        self.model_name = os.getenv("")
        self.agent_llm_system_role = 
    