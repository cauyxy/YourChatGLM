import os
import shutil

from config import YCG_ROOT_PATH
from kbase import TextKnowledgeBase
from utils import from_alnum, to_alnum

KBASE_ROOT = os.path.join(YCG_ROOT_PATH, "kbase", "data")


def get_all_kbase() -> list[str]:
    alnum_floder = os.listdir(KBASE_ROOT)
    return [from_alnum(f) for f in alnum_floder]


def build_a_kbase(db_name: str, files: list[str]):
    k = TextKnowledgeBase(db_name=db_name)
    for file in files:
        file_name = get_last_file_name(file)
        file_content = read_chinese_text_file(file)
        k.add_document(title=file_name, content=file_content, path=None)
    k.close()
    return


def read_chinese_text_file(file_path):
    with open(file_path, 'rb') as f:
        raw_text = f.read()

        # Try to decode text using different encoding formats
        try_encodings = ['utf-8', 'gbk', 'big5', 'gb18030', 'utf-16']
        for encoding in try_encodings:
            try:
                text = raw_text.decode(encoding)
                return text
            except UnicodeDecodeError:
                continue

        # If all encodings fail, raise an error
        raise ValueError("Cannot decode text file: {}".format(file_path))


def delete_a_kbase(k_name):
    k_name = to_alnum(k_name)
    k_path = os.path.join(KBASE_ROOT, k_name)
    shutil.rmtree(k_path)


def get_last_file_name(file_path):
    # 先使用 "/" 将路径分割成一个列表
    path_parts = file_path.split("/")
    # 返回列表中的最后一个元素，即文件名
    return path_parts[-1]
