import pandas as pd
import json
import os
import random
from typing import List, Dict, Set, Tuple, Optional

class TestGenerator:
    def __init__(self, method1_path: str, method2_path: str, method3_path: str, output_dir: str = 'generated_tests'):
        """Initialize the test generator with input files and output directory."""
        # Read CSV files and add method information
        self.method1_df = pd.read_csv(method1_path)
        self.method1_df['method'] = 'Method 1'
        
        self.method2_df = pd.read_csv(method2_path)
        self.method2_df['method'] = 'Method 2'
        
        self.method3_df = pd.read_csv(method3_path)
        self.method3_df['method'] = 'Method 3'
        
        # Initialize tracking sets and lists
        self.used_questions: Set[str] = set()
        self.invalid_combinations: Set[str] = set()  # Track combinations that couldn't be used
        self.tests: List[Dict] = []
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Skills
        self.bloom_levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate']
        
        # Dictionary to track used topic-skill combinations per test
        self.current_test_topic_skills: Set[str] = set()

    def reset_test_constraints(self):
        """Reset the topic-skill combination tracking for a new test."""
        self.current_test_topic_skills = set()

    def select_question(self, method_df: pd.DataFrame, skill: str, test_topics: Set[str]) -> Optional[pd.Series]:
        """Try to select a valid question with given constraints."""
        # Get available questions for this skill
        mask = (method_df['skill'] == skill) & (~method_df['question'].isin(self.used_questions))
        available = method_df[mask]
        
        if available.empty:
            return None
        
        # Filter by valid topic-skill combinations
        valid_questions = available[available.apply(
            lambda x: f"{x['topic']}_{x['skill']}" not in self.current_test_topic_skills, 
            axis=1
        )]
        
        if valid_questions.empty:
            # Track these invalid combinations
            for _, question in available.iterrows():
                self.invalid_combinations.add(f"{question['topic']}_{question['skill']}")
            return None
            
        # Try to select from unused topics if possible
        unused_topics = valid_questions[~valid_questions['topic'].isin(test_topics)]
        selection_pool = unused_topics if not unused_topics.empty else valid_questions
        
        selected = selection_pool.sample(n=1).iloc[0]
        self.current_test_topic_skills.add(f"{selected['topic']}_{selected['skill']}")
        
        return selected

    def generate_method_questions(self, method_df: pd.DataFrame, test_topics: Set[str]) -> List[Dict]:
        """Generate questions for one method."""
        method_questions = []
        skills_needed = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate']
        random.shuffle(skills_needed)  # Randomize skill order
        
        for skill in skills_needed:
            selected = self.select_question(method_df, skill, test_topics)
            if selected is None:
                continue
                
            test_topics.add(selected['topic'])
            self.used_questions.add(selected['question'])
            
            method_questions.append({
                'question': selected['question'],
                'skill': selected['skill'],
                'topic': selected['topic'],
                'correct_answer': selected['correct_answer'],
                'options': {
                    'a': selected['option_a'],
                    'b': selected['option_b'],
                    'c': selected['option_c'],
                    'd': selected['option_d']
                }
            })
        
        return method_questions

    def convert_test_to_dataframe(self, test: Dict, test_number: int) -> pd.DataFrame:
        """Convert a single test from dictionary format to a pandas DataFrame."""
        rows = []
        for method_key in ['method1_questions', 'method2_questions', 'method3_questions']:
            method_number = method_key[6]
            
            for question in test[method_key]:
                rows.append({
                    'test_number': test_number,
                    'method': f'Method {method_number}',
                    'question': question['question'],
                    'topic': question['topic'],
                    'skill': question['skill'],
                    'correct_answer': question['correct_answer'],
                    'option_a': question['options']['a'],
                    'option_b': question['options']['b'],
                    'option_c': question['options']['c'],
                    'option_d': question['options']['d']
                })
        
        return pd.DataFrame(rows)

    def save_tests(self) -> None:
        """Save generated tests to files."""
        # Save tests as JSON
        with open(os.path.join(self.output_dir, 'generated_tests.json'), 'w') as f:
            json.dump(self.tests, f, indent=2)
        
        # Create individual test CSVs and combined CSV
        all_tests_df = pd.DataFrame()
        
        for i, test in enumerate(self.tests, 1):
            test_df = self.convert_test_to_dataframe(test, i)
            
            # Save individual test
            test_df.to_csv(os.path.join(self.output_dir, f'test_{i}.csv'), index=False)
            
            # Add to combined DataFrame
            all_tests_df = pd.concat([all_tests_df, test_df])
        
        # Save combined tests
        all_tests_df.to_csv(os.path.join(self.output_dir, 'all_tests.csv'), index=False)

    def generate_test(self) -> Dict:
        """Generate one complete test with questions from all three methods."""
        self.reset_test_constraints()
        test_topics = set()
        
        methods = [
            (self.method1_df, 'method1_questions'),
            (self.method2_df, 'method2_questions'),
            (self.method3_df, 'method3_questions')
        ]
        random.shuffle(methods)
        
        test = {}
        for method_df, method_key in methods:
            test[method_key] = self.generate_method_questions(method_df, test_topics)
        
        return test

    def generate_all_tests(self, num_tests: int) -> None:
        """Generate specified number of tests."""
        for i in range(num_tests):
            try:
                test = self.generate_test()
                if all(len(questions) > 0 for questions in test.values()):
                    self.tests.append(test)
                    print(f"Generated test {i+1}")
                else:
                    print(f"Skipped test {i+1} due to insufficient valid questions")
            except Exception as e:
                print(f"Error generating test {i+1}: {str(e)}")
                break

    def get_all_unused_questions(self) -> pd.DataFrame:
        """Get all questions that weren't used in tests."""
        unused_m1 = self.method1_df[~self.method1_df['question'].isin(self.used_questions)]
        unused_m2 = self.method2_df[~self.method2_df['question'].isin(self.used_questions)]
        unused_m3 = self.method3_df[~self.method3_df['question'].isin(self.used_questions)]
        
        all_unused = pd.concat([unused_m1, unused_m2, unused_m3])
        return all_unused

    def save_unused_questions(self) -> None:
        """Save unused questions to CSV files with detailed statistics."""
        unused_dir = os.path.join(self.output_dir, 'unused_questions')
        os.makedirs(unused_dir, exist_ok=True)
        
        # Get all unused questions
        unused_df = self.get_all_unused_questions()
        
        # Split by method
        for method in ['Method 1', 'Method 2', 'Method 3']:
            method_unused = unused_df[unused_df['method'] == method]
            method_unused.to_csv(
                os.path.join(unused_dir, f'unused_{method.lower().replace(" ", "_")}.csv'),
                index=False
            )
        
        # Save combined unused questions
        unused_df.to_csv(os.path.join(unused_dir, 'all_unused_questions.csv'), index=False)
        
        # Generate and save statistics
        stats = {
            'total_unused': len(unused_df),
            'by_method': unused_df['method'].value_counts().to_dict(),
            'by_skill': unused_df['skill'].value_counts().to_dict(),
            'by_topic': unused_df['topic'].value_counts().to_dict(),
            'invalid_combinations': list(self.invalid_combinations)
        }
        
        with open(os.path.join(unused_dir, 'unused_statistics.json'), 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Print statistics
        print("\nUnused Questions Statistics:")
        print(f"Total unused questions: {len(unused_df)}")
        print("\nBy method:")
        print(unused_df['method'].value_counts())
        print("\nBy skill:")
        print(unused_df['skill'].value_counts())
        print("\nBy topic:")
        print(unused_df['topic'].value_counts())
        print(f"\nInvalid combinations encountered: {len(self.invalid_combinations)}")

def main():
    # Set random seed for reproducibility (optional)
    random.seed(42)
    
    # Initialize generator
    generator = TestGenerator(
        '/home/nicyscaria/mcq_distractors/datasets/Part3/ConceptMap_Part3.csv',
        '/home/nicyscaria/mcq_distractors/datasets/Part3/LLM_Part3.csv',
        '/home/nicyscaria/mcq_distractors/datasets/Part3/RAG_Part3.csv'
    )
    
    # Generate tests
    generator.generate_all_tests(15)
    
    # Save tests
    generator.save_tests()
    
    # Save unused questions with statistics
    generator.save_unused_questions()
    
    print(f"\nSuccessfully generated {len(generator.tests)} tests")
    print(f"Total questions used: {len(generator.used_questions)}")

if __name__ == "__main__":
    main()