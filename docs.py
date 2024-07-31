from typing import List
import textract
from fs import open_fs
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_doc_glob(extension: str) -> str:
    return f'./**/*{extension}'

def get_docs(directory: str, extensions: List[str]) -> List[str]:
    globs = map(lambda extension: get_doc_glob(extension), extensions)
    return [match.path for glob in globs for match in open_fs(directory).glob(glob)]

def get_file_content(path: str) -> tuple[str, str]:
    try:
        file_name = os.path.relpath(path, CURRENT_DIR)
        file_content = textract.process(path).decode('utf-8')
        return file_name, file_content
    except Exception as e:
        print(e)

def get_files_content(directory: str, extensions: List[str]) -> List[tuple[str, str]]:
    docs = get_docs(directory, extensions)
    docs = [get_file_content(directory + file) for file in docs]
    docs = list(filter(lambda doc: doc[1] != '', docs))
    return docs

