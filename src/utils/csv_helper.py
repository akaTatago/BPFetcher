import pandas as pd
import os
import sys


def load_books(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []

    try:
        df = pd.read_csv(file_path, dtype=str)
        
        if 'ISBN13' in df.columns:
            col_name = 'ISBN13'
        else:
            print(f"ISBN13 column not found in {file_path}")
            return []
        
        df[col_name] = df[col_name].fillna('').astype(str)
        df['Identifier'] = df[col_name].str.replace('=', '').str.replace('"', '').str.replace('-', '').str.strip()

        books_list = df.to_dict('records')
        
        books_list = [b for b in books_list if b.get('Identifier')]

        return books_list

    except Exception as e:
        print(f"Error: {e}")
        return []

def save_results(data, output_path):
    try:
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False