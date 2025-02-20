from pathlib import Path
import yaml
from typing import Dict, Optional

class ConfigLoader:
    """
    Load all config files
    """
    
    def __init__(self, config_dir: Optional[str] = None):

        if config_dir is None:
            # Start from current file location
            current_file = Path(__file__)
            
            # Navigate up until we find the project root (where configs dir is)
            project_root = current_file
            while project_root.name != "MCQ_Distractors" and project_root.parent != project_root:
                project_root = project_root.parent
            
            if project_root.name != "MCQ_Distractors":
                raise ValueError("Could not find MCQ_Distractors directory in path")
                
            self.config_dir = project_root / 'configs'
        else:
            self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found at {self.config_dir}")

    def load_skill_config(self) -> Dict:
        return self._load_yaml('skill_config.yaml')

    def load_model_config(self) -> Dict:
        return self._load_yaml('model_config.yaml')

    def load_output_config(self) -> Dict:
        return self._load_yaml('output_config.yaml')

    def load_prompt_config(self) -> Dict:
        return self._load_yaml('prompt_config.yaml')

    def _load_yaml(self, filename: str) -> Dict:
        try:
            with open(self.config_dir / filename, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file {filename} not found in {self.config_dir}"
            )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Error parsing {filename}: {str(e)}"
            )

# if __name__ == "__main__":
    
#     config_loader = ConfigLoader()
    
#     try:
#         # Load individual configs
#         skill_config = config_loader.load_skill_config()
#         model_config = config_loader.load_model_config()
#         output_config = config_loader.load_output_config()
#         prompt_config = config_loader.load_prompt_config()
        
#         print("Model name:", model_config['model'])
#         print("Available skills:", skill_config['skills']['requirements']['Remember'])
#         print("Available prompts:", list(prompt_config['prompts'].keys()))
        
#     except (FileNotFoundError, yaml.YAMLError) as e:
        # print(f"Error loading configurations: {str(e)}")
    