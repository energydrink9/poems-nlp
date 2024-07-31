from top2vec import Top2Vec
from data import get_data_from_file
import os
import json
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CSV_PATH = f'{CURRENT_DIR}/poems-with-topics.csv'
TOPICS_PATH = f'{CURRENT_DIR}/topics.json'

def get_poems_with_topics_from_file():
    return pd.read_csv(CSV_PATH)

def get_poems_with_topics():
    poems = get_data_from_file()
    texts = poems['text'].values.tolist()
    document_ids = poems['id'].values.tolist()

    model = Top2Vec(documents=texts, document_ids=document_ids, speed="deep-learn", workers=8, embedding_model='universal-sentence-encoder-multilingual', hdbscan_args={'min_cluster_size': 15}, umap_args={'n_components': 5, 'n_neighbors': 5})
    topic_words, word_scores, topic_nums = model.get_topics()

    for i, topic in enumerate(topic_words):
        print(f'Topic {i}')
        for j, word in enumerate(topic):
            if j < 30:
                print(f'Word {word}, score: {word_scores[i, j]}')

    content = []
    for i, topic in enumerate(topic_words):
        topic_content = []
        for j, word in enumerate(topic):
            topic_content.append((word, float(word_scores[i, j])))
        content.append(topic_content)

    with open(TOPICS_PATH, 'w+') as topics_file:
        json.dump(content, topics_file)

    print('Retrieving documents topics')
    ids = list(range(0, len(texts)))

    result = model.get_documents_topics(document_ids, num_topics=3)

    topic_nums = result[0]

    print('Updating documents topics')

    poems['topic1'] = ''
    poems['topic2'] = ''
    poems['topic3'] = ''

    for i, doc in enumerate(topic_nums):
        if len(doc) > 0:
            poems.loc[i, 'topic1'] = doc[0]
        if len(doc) > 1:
            poems.loc[i, 'topic2'] = doc[1]
        if len(doc) > 2:
            poems.loc[i, 'topic3'] = doc[2]

    print(poems)

    return poems

def save_poems_with_topics_to_file():
    poems = get_poems_with_topics()
    poems.to_csv(CSV_PATH, index = False, columns=['id', 'date', 'title', 'text', 'topic1', 'topic2', 'topic3'])
    print(f'Saved at {CSV_PATH}')