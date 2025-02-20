# AEQG-MCQ-Distractors-Physics

Generating high-quality multiple choice questions (MCQs), especially those targeting diverse cognitive levels and incorporating common misconceptions into distractor design, is a time-consuming and expertise-intensive process, making manual creation impractical at scale. Existing automated approaches typically generate questions at lower cognitive levels and fail to systematically incorporate domain-specific misconceptions and plausible distractors in their design. This paper presents a hierarchical concept map-based framework that enhances the capabilities of a Large Language Model (LLM) for automated MCQ generation for Physics. We developed a comprehensive hierarchical concept map covering major Physics topics and their interconnections. Through an automated pipeline, topic-relevant sections of these concept maps are retrieved to serve as a structured context for the LLM to generate questions and distractors that specifically target common misconceptions. We evaluate our framework against two baseline approaches: a standard LLM-based generation and a Retrieval Augmented Generation (RAG) method. We conducted expert evaluation and student assessments of the generated MCQs. The expert evaluation shows that our method significantly outperforms baseline approaches, achieving a 75.20% success rate in meeting all quality criteria compared to approximately 37% for both baseline methods. Student assessment data reveals that our concept map-driven approach achieved a significantly lower guessing success rate of 28.05% compared to the LLM's 37.10%, indicating more effective assessment of conceptual understanding. The results demonstrate that concept map enhanced MCQ generation enables both robust assessment across cognitive levels and instant identification of specific conceptual gaps, facilitating faster feedback loops and targeted interventions.


## Project Structure

```
├── books/                      # Textbook used
├── configs/                    # Configuration files
│   ├── config.yaml             # General configuration
│   ├── model_config.yaml       # Model-specific settings
│   ├── output_config.yaml      # Output format specifications
│   ├── prompt_config.yaml      # Prompt templates
│   └── skill_config.yaml       # Bloom's taxonomy skill definitions
├── data/
│   ├── chroma_db_huggingface/  # Vector store for RAG
│   └── concept_map/            # Concept map database
├── notebooks/                  # Jupyter notebooks for development and testing
│   ├── QS_ConceptMap.ipynb
│   ├── QS_LLM.ipynb
│   └── QS_RAG.ipynb
├── src/
│   ├── constants/
│   │   └── skill.py           # Skill-related constants
│   ├── question_generators/
│   │   ├── base.py            # Abstract base class for generators
│   │   ├── conceptmap_generator.py
│   │   ├── llm_generator.py
│   │   └── rag_generator.py
│   └── utils/
│       ├── config_loader.py
│       ├── csv_to_sql_conversion.py
│       ├── testgeneration.py
│       └── topic_identifier.py
├── LICENSE
├── README.md
├── main.py                   # Main entry point
└── requirements.txt          # Project dependencies
```
