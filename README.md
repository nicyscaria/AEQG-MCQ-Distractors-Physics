# AEQG-MCQ-Distractors-Physics

Generating high-quality multiple choice questions (MCQs), especially those targeting diverse cognitive levels and incorporating common misconceptions into distractor design, is a time-consuming and expertise-intensive process, making manual creation impractical at scale. Existing automated approaches typically generate questions at lower cognitive levels and fail to systematically incorporate domain-specific misconceptions and plausible distractors in their design. This paper presents a hierarchical concept map-based framework that enhances the capabilities of a Large Language Model (LLM) for automated MCQ generation for Physics. We developed a comprehensive hierarchical concept map covering major Physics topics and their interconnections. Through an automated pipeline, topic-relevant sections of these concept maps are retrieved to serve as a structured context for the LLM to generate questions and distractors that specifically target common misconceptions. We evaluate our framework against two baseline approaches: a standard LLM and a Retrieval Augmented Generation (RAG) based generation. We conducted expert evaluation and student assessments of the generated MCQs. The expert evaluation shows that our method significantly outperforms baseline approaches, achieving a 75.20% success rate in meeting all quality criteria compared to approximately 37% for both baseline methods. Student assessment data reveals that our concept map-driven approach achieved a significantly lower guessing success rate of 28.05% compared to the LLM's 37.10%, indicating more effective assessment of conceptual understanding. The results demonstrate that concept map enhanced MCQ generation enables both robust assessment across cognitive levels and instant identification of specific conceptual gaps, facilitating faster feedback loops and targeted interventions.


## Project Structure

```
├── books/                            # Textbook used
├── configs/                          # Configuration files
│   ├── config.yaml                   # General configuration
│   ├── model_config.yaml             # Model-specific settings
│   ├── output_config.yaml            # Output format specifications
│   ├── prompt_config.yaml            # Prompt templates
│   └── skill_config.yaml             # Bloom's taxonomy skill definitions
├── data/
│   ├── chroma_db_huggingface/        # Vector store for RAG
│   └── concept_map/                  # Concept map database
├── notebooks/                        # Jupyter notebooks for MCQ generation and testing easily
│   ├── QS_ConceptMap.ipynb
│   ├── QS_LLM.ipynb
│   └── QS_RAG.ipynb
├── src/
│   ├── constants/
│   │   └── skill.py                  # Skill-related constants
│   ├── question_generators/
│   │   ├── base.py                   # Abstract base class for generators
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
├── main.py                          # Main file to run all the experiments
└── requirements.txt                 # Project dependencies
```

## Setup

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   - Create a `.env` file with:
     ```
     DB_NAME=your_db_name
     DB_USER=your_db_user
     DB_PASSWORD=your_db_password
     DB_HOST=your_db_host
     DB_PORT=your_db_port
     TOGETHER_API_KEY=your_api_key
     ```

4. **Database Setup**
   - Set up PostgreSQL database
   - Import concept map data
   - Run schema migrations

5. **Vector Store Setup** (for RAG)
   - OpenStax textbook embedding available in data

## Usage

Run the generation script:
```bash
python3 main.py #give the input when prompted
```

## Configuration

Adjust settings in the config files:
- `configs/model_config.yaml`: Model parameters
- `configs/prompt_config.yaml`: Generation prompts
- `configs/output_config.yaml`: Output formats
- `configs/skill_config.yaml`: Skill requirements

## Important Usage Restriction
⚠️ **This material may not be used in the training of large language models or otherwise be ingested into large language models or generative AI offerings without OpenStax's permission.**

## Attribution and Citation

These concept maps are derivative works based on material from the OpenStax Physics textbook.

### Source Attribution
- **Original Material:** OpenStax Physics textbook
- **URL:** https://openstax.org/books/physics/pages/1-introduction
- **Original Material Available at:** https://www.texasgateway.org/book/tea-physics
- **License:** Creative Commons Attribution License
- **Authors:** Paul Peter Urone, Roger Hinrichs
- **Publisher:** OpenStax
- **Publication Date:** Mar 26, 2020

### Academic Citation
When citing our work in academic publications, please include the following citation too:

**APA Format:**
```
Urone, P. P., & Hinrichs, R. (2020). Physics. OpenStax. https://openstax.org/books/physics/
```

### License Notice
The concept maps and derivative works in this repository are licensed under the Creative Commons Attribution License. Changes and adaptations have been made to the original material.

For complete license terms, please see the [LICENSE.md](LICENSE.md) file in this repository.
