import pandas as pd
import os

def load_books(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} file not found")
        return []

    try:
        df = pd.read_csv(file_path, dtype=str)
        
        df['Title'] = df['Title'].fillna('').str.strip()
        df['Author'] = df['Author'].fillna('').str.strip()

        books_list = df.to_dict('records')
        
        return books_list

    except Exception as e:
        print(f"Error while reading file: {e}")
        return []

def save_results(data, output_path):
    try:
        df = pd.DataFrame(data)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Output successfully saved in {output_path}")
        return True
        
    except Exception as e:
        print(f"Error while saving file: {e}")
        return False