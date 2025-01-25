import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DATABASE = os.getenv('DB_NAME')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')

# Create a connection string
connection_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Create a SQLAlchemy engine
engine = create_engine(connection_string)

# csv_path = os.getenv('CSV_PATH')
csv_path = "/Users/nicyscaria/PhD/Research/Auro/MCQ_Distractors/data/subtopics.csv"

def get_table_structure(table_name):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                column_name,
                data_type
            FROM 
                information_schema.columns 
            WHERE 
                table_schema = 'public'
                AND table_name = :table_name
            ORDER BY 
                ordinal_position;
        """), {"table_name": table_name})
        
        columns = {row[0]: row[1] for row in result}
        print(f"\nTable columns in database:")
        for col, dtype in columns.items():
            print(f"  {col}: {dtype}")
        return columns

def process_csv_to_sql(csv_path):
    # Get table name from CSV filename
    table_name = os.path.splitext(os.path.basename(csv_path))[0]
    
    # Get table structure first
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = :table_name
            ORDER BY ordinal_position;
        """), {"table_name": table_name})
        
        table_columns = {row[0]: row[1] for row in result}
        print("\nTable structure:")
        for col, dtype in table_columns.items():
            print(f"  {col}: {dtype}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print("\nCSV columns:", df.columns.tolist())
    
    # Only keep columns that exist in the table
    valid_columns = [col for col in df.columns if col in table_columns]
    df = df[valid_columns]
    
    # Process JSON columns
    json_columns = [col for col, dtype in table_columns.items() 
                   if dtype.lower() in ('json', 'jsonb') and col in df.columns]
    
    if json_columns:
        print(f"\nProcessing JSON columns: {json_columns}")
        for col in json_columns:
            df[col] = df[col].apply(clean_json_field)
    
    # Write to database
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Data imported successfully into the {table_name} table!")

def clean_json_field(text):
    try:
        if pd.isna(text):
            return None

        # If it's already a list or dict, convert to JSON string
        if isinstance(text, (list, dict)):
            return json.dumps(text, ensure_ascii=False)
            
        # If it's a string, clean it up
        if isinstance(text, str):
            # Handle heavily escaped format
            if text.startswith('[""[') and text.endswith('"]"]'):
                text = text[3:-3]
                text = text.replace('\\"', '"')
            
            # Handle LaTeX equations by preserving backslashes
            text = text.replace('\\\\', '\\\\\\\\')  # Double the backslashes
            text = text.replace('\n', ' ').strip()
            text = text.replace('\\u2019', "'")
            
            if text.strip().startswith('[') and text.strip().endswith(']'):
                # Clean up the list items
                items = text.strip('[]').split('",')
                cleaned_items = []
                for item in items:
                    item = item.strip().strip('"').strip("'")
                    if item:
                        cleaned_items.append(item)
                return json.dumps(cleaned_items)
            
            try:
                parsed = json.loads(text)
                return json.dumps(parsed, ensure_ascii=False)
            except:
                # If parsing fails, try to evaluate as Python literal
                import ast
                try:
                    parsed = ast.literal_eval(text)
                    return json.dumps(parsed, ensure_ascii=False)
                except:
                    print(f"Failed to parse JSON: {text}")
                    return text
                
    except Exception as e:
        print(f"Error processing JSON: {e}")
        print(f"Problematic text: {text}")
        return '[null]'

process_csv_to_sql(csv_path)