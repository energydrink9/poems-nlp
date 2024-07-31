from typing import List
import textract
from fs import open_fs
import os
from docs import get_docs

DATA_DIR = './data'


def convert_file_to_txt(path: str) -> None:
    try:
        content = textract.process(path).decode("utf-8")
        txt_file_path = (path
                         .removesuffix('.txt')
                         .removesuffix('.doc')
                         .removesuffix('.DOC')
                         .removesuffix('.docx')
                         .removesuffix('.DOCX')
                         .removesuffix('.rtf')) + '.txt'
        with open(txt_file_path, 'w+') as file:
            file.write(content)
        os.remove(path)
    except Exception as e:
        print(e)
        os.remove(path)


def convert_docs_to_txt(directory: str) -> None:
    docs = get_docs(directory, ['.doc', '.docx', '.DOC', '.DOCX'])
    for doc in docs:
        convert_file_to_txt(directory + doc)
