import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json

load_dotenv()

# Database connection parameters
DATABASE = os.getenv('DB_NAME')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')

connection_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Create a SQLAlchemy engine
engine = create_engine(connection_string)

csv_path = "path_to_csv_file"

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
    
def check_row_lengths(df):
    # Get length of each column's content for all rows
    for col in df.columns:
        # Convert each value to string and get its length
        df[f'{col}_length'] = df[col].astype(str).apply(len)
        
        # Find rows where length > 2500
        long_rows = df[df[f'{col}_length'] > 2500]
        if not long_rows.empty:
            print(f"\nColumn '{col}' has values exceeding 2500 characters in these rows:")
            for idx, row in long_rows.iterrows():
                print(f"Row {idx}: {row[f'{col}_length']} characters")
                print(f"First 100 characters: {row[col][:100]}...")
                print("-" * 80)
    
    # Remove the temporary length columns
    length_cols = [col for col in df.columns if col.endswith('_length')]
    df.drop(columns=length_cols, inplace=True)
    
    return df

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
    
    # Try different encodings to read CSV
    encodings_to_try = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"\nSuccessfully read CSV with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise ValueError("Could not read the CSV file with any of the attempted encodings")
    
    print("\nCSV columns:", df.columns.tolist())
    
    # Find exceeding rows before any processing
    df = check_row_lengths(df)
    
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
