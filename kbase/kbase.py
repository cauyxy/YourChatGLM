import os
import re

from jieba.analyse import ChineseAnalyzer
from whoosh import highlight, qparser
from whoosh.fields import Schema, TEXT, ID
from whoosh.filedb.filestore import FileStorage
from whoosh.index import create_in
from whoosh.qparser import QueryParser

from config import YCG_ROOT_PATH
from utils import to_alnum

KBASE_ROOT = os.path.join(YCG_ROOT_PATH, "kbase", "data")


class TextKnowledgeBase:
    """
    使用Whoosh实现的txt文本知识库，支持持久化到磁盘
    """

    def __init__(self, db_name):
        """
        初始化方法，用于创建或加载索引
        """
        db_name = to_alnum(db_name)
        self.index_dir = os.path.join(KBASE_ROOT, db_name)
        self.storage = FileStorage(self.index_dir)
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)
            schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                            path=ID(stored=True))
            self.index = create_in(self.index_dir, schema)
        else:
            self.index = self.storage.open_index()

    def add_document(self, title, content, path):
        """
        添加文档到索引中
        """
        writer = self.index.writer()
        writer.add_document(title=title, content=content, path=path)
        writer.commit()

    def delete_document(self, path):
        """
        从索引中删除指定文档
        """
        writer = self.index.writer()
        writer.delete_by_term('path', path)
        writer.commit()

    def update_document(self, title, content, path):
        """
        更新指定文档的内容
        """
        writer = self.index.writer()
        writer.update_document(title=title, content=content, path=path)
        writer.commit()

    def search(self, query_str):
        """
        根据查询字符串搜索文档
        """
        if isinstance(query_str, list):
            query_str = f"{query_str[0]} AND {query_str[1]}"
        searcher = self.index.searcher()
        query_parser = QueryParser("content", self.index.schema)
        query_parser.remove_plugin_class(qparser.PhrasePlugin)
        query_parser.add_plugin(qparser.SequencePlugin())
        query = query_parser.parse(query_str)

        results = searcher.search(query)
        print(results)
        results.fragmenter = highlight.ContextFragmenter(maxchars=200, surround=50)
        if len(results) == 0:
            return None, None
        else:
            result = results[0]
            return result["title"], self.remove_tags(result.highlights("content"))

    def close(self):
        """
        关闭索引
        """
        self.index.close()
        self.storage.close()

    @staticmethod
    def remove_tags(input_str):
        # 删除所有带有 class 属性且值中包含 term 的 <b> 标签
        input_str = re.sub(r'<b\s+class\s*=\s*"[^"]*term[^"]*"\s*>', "", input_str)
        # 删除 </b> 标签
        input_str = input_str.replace("</b>", "")
        return input_str
