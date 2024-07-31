import math
import pandas as pd
from sentence_transformers import SentenceTransformer
from data import get_data_from_file
from upload_data import upload
import os
from clustering import get_poems_with_topics_from_file

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CSV_PATH = f'{CURRENT_DIR}/poems-with-embeddings.csv'

def get_embedding_model():
    # Load the pre-trained model suitable for Italian
    return SentenceTransformer('distiluse-base-multilingual-cased-v2')  # This model outputs 512-dimensional embedding

def generate_embeddings():
    model = get_embedding_model()

    # Load your DataFrame
    df = get_poems_with_topics_from_file()

    # Generate embeddings
    print('Generating embeddings')
    df['embedding'] = df['text'].apply(lambda x: model.encode(x).tolist())

    return df

def generate_and_save_to_file() -> None:
    data = generate_embeddings()
    print(data)
    data.to_csv(CSV_PATH, index = False)
    print(f'Saved at {CSV_PATH}')

def generate_and_upload():
    poems = generate_embeddings()
    upload(poems)

def parse_embedding(embedding: str):
    return list(map(lambda value: float(value), embedding.strip('[]').split()))

def get_poems_with_embeddings_from_file():
    dtypes = {'id': 'str', 'date': 'str', 'title': 'str', 'text': 'str', 'topic1': 'int', 'topic2': 'int', 'topic3': 'int', 'embedding': 'str'}
    poems = pd.read_csv(CSV_PATH, dtype=dtypes)
    poems['date'] = poems['date'].apply(lambda x: None if x == 'NaN' else x )
    poems['embedding'] = poems['embedding'].apply(parse_embedding)
    return poems

def get_poems_with_embeddings_from_file_and_upload():
    poems = get_poems_with_embeddings_from_file()
    upload(poems)

#generate_and_save_to_file()
get_poems_with_embeddings_from_file_and_upload()