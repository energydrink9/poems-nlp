#!/usr/bin/env python
import datetime
from typing import List, Optional
import re
from docs import get_files_content
import pandas as pd
import os
import datefinder
import thefuzz.fuzz as fuzz
import thefuzz.process as fuzz_process
import uuid
from functools import lru_cache
from toolz import unique
import string

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = f'{CURRENT_DIR}/data'
DOC_EXTENSIONS = ['.txt']
CSV_PATH = f'{CURRENT_DIR}/poems.csv'
UUID_NAMESPACE_NAME = "brunolugano.poetry"
POEM_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, UUID_NAMESPACE_NAME)

def generate_poem_uuid(text: str) -> str:
  return uuid.uuid5(POEM_NAMESPACE, text)

def string_contains_date(text: str) -> bool:
    return any(char.isdigit() for char in text) or '-' in text or '/' in text

def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))

def strip_lines(poem: str) -> str:
    return '\n'.join(line.strip(' ') for line in poem.split('\n'))

def strip_poem(poem: str) -> str:
    return poem.strip()

def remove_double_spaces(poem: str) -> str:
    return re.sub(' +', ' ', poem)

def process_text(text: str) -> str:
    return strip_poem(remove_double_spaces(strip_lines(strip_poem(text))))

def get_title(poem: tuple[datetime.datetime, str, str]) -> str:
    return poem[1]

def get_text(poem: tuple[datetime.datetime, str, str]) -> str:
    return poem[2]

def take_only_first_n_words(text: str, n: int) -> str:
    return ' '.join([word for i, word in enumerate(text.split(' ')) if i < n])

def build_title(text: str) -> str:
    lines = remove_punctuation(text).split('\n')
    title_line = []
    iterator = (line for line in lines if not string_contains_date(line) and not line.strip() == '')
    for line in iterator:
        if len(' '.join(title_line)) >= 5:
            break
        title_line.append(line)
    title_line_text = ' '.join(title_line)
    cleaned_line = take_only_first_n_words(title_line_text, 18)

    return cleaned_line.capitalize()

def format_date(date: datetime.datetime) -> str:
    return date

def extract_date(text: str, filename: str, verbose = False) -> Optional[str]:
    lines = text.split('\n')
    date_lines = [line for line in lines if string_contains_date(line)]
    if len(date_lines) == 0:
        return None
    first_date = date_lines[0]
    date_without_dots = re.sub('\.', ':', first_date)
    matches = list(datefinder.find_dates(date_without_dots, first = 'day'))
    if (verbose and len(matches) == 0):
        print(f'Couldn\'t find date: {date_without_dots}. File name: {filename}')
    return format_date(matches[0]) if len(matches) > 0 else None

def add_ids(poems: List[tuple[datetime.datetime, str, str, str]]) -> List[tuple[str, datetime.datetime, str, str, str]]:
    return list(map(lambda tuple: (generate_poem_uuid(get_text(tuple)), tuple[0], tuple[1], get_text(tuple), tuple[3]), poems))

@lru_cache
def scorer(s1, s2, force_ascii=True, full_process=True):
    return fuzz.token_set_ratio(s1, s2, force_ascii, full_process)

def get_duplicate_poems(texts: List[str]):
    poems_to_remove = set()
    for i, text in enumerate(texts):
        start = max(0, i - 20)
        end = min(len(texts), i + 20 + 1)
        texts_to_consider = texts[start:end]
        matches = fuzz_process.extractBests(text, texts_to_consider, scorer=scorer, score_cutoff=70, limit=None)
        matches = list(map(lambda x: x[0], matches))
        to_keep = max(matches, key=lambda x: len(x))
        to_remove = set(matches)
        if to_keep is not None and to_keep in to_remove:
            to_remove.remove(to_keep)
        poems_to_remove = poems_to_remove.union(to_remove)
    return poems_to_remove

def comparing_function_title(poem):
    return get_title(poem)

def sort_poems(poems: List[tuple[datetime.datetime, str, str, str]]) -> List[tuple[datetime.datetime, str, str, str]]:
    return sorted(poems, key=comparing_function_title)

def dedupe_poems(poems: List[tuple[datetime.datetime, str, str, str]]) -> List[tuple[datetime.datetime, str, str, str]]:
    poems = sort_poems(poems)
    poems = list(unique(poems, key=lambda poem: get_text(poem)))
    texts = list(map(lambda tuple: get_text(tuple), poems))
    print(f'Total texts: {len(texts)}')
    duplicate_poems = get_duplicate_poems(texts)
    print(f'To remove: {len(duplicate_poems)}')
    def is_poem_to_remove(text: str):
        return text in duplicate_poems
    return list(filter(lambda tuple: not is_poem_to_remove(get_text(tuple)), poems))

def build_poem(tuple: tuple[str, str]) -> tuple[datetime.datetime, str, str, str]:
    text = process_text(tuple[1])
    date = extract_date(tuple[1], tuple[0])
#    if date is None:
#        print(f'None {text}')
    return (date, build_title(text), text, tuple[0])

def get_data() -> List[tuple[str, datetime.datetime, str, str, str]]:
    all_poems = get_files_content(DATA_DIR, DOC_EXTENSIONS)
    poems = map(lambda poem_tuple: build_poem(poem_tuple), all_poems)
    poems = list(filter(lambda poem_tuple: get_text(poem_tuple) != '', poems))
    print(f'Number of poems before dedupe: {len(poems)}')
    deduped_poems = dedupe_poems(poems)
    deduped_poems = add_ids(deduped_poems)
    print(f'Number of poems: {len(deduped_poems)}')
    return deduped_poems

def get_data_frame():
    data = get_data()
    dataframe = pd.DataFrame(data, columns=['id', 'date', 'title', 'text', 'filename'])
    return dataframe

def get_data_from_file():
    return pd.read_csv(CSV_PATH)

def save_data_to_file() -> None:
    print('Retrieving and processing data')
    data = get_data_frame()
    print(data)
    data.to_csv(CSV_PATH, index = False)
    print(f'Saved at {CSV_PATH}')

#save_data_to_file()