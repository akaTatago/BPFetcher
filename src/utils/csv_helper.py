import pandas as pd
import os
import sys


def load_books(file_path, mode='isbn'):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []

    try:
        df = pd.read_csv(file_path, dtype=str)

        books_list = []
        
        if mode == 'isbn':
            if 'ISBN13' not in df.columns:
                print(f"ISBN13 column not found in {file_path}")
                return []
            
            df['ISBN13'] = df['ISBN13'].fillna('').astype(str)
            df['Identifier'] = df['ISBN13'].str.replace('=', '').str.replace('"', '').str.replace('-', '').str.strip()
            books_list = df.to_dict('records')
            books_list = [b for b in books_list if b.get('Identifier')]

        elif mode == 'text':
            required = ['Title', 'Author']
            if not all(col in df.columns for col in required):
                print(f"Columns 'Title' and 'Author' not found in {file_path}")
                return []
            
            df = df.dropna(subset=['Title', 'Author'])
            books_list = df.to_dict('records')

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