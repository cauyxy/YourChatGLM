import sys

sys.path.append("../")

from kbase import TextKnowledgeBase

# 初始化一个知识库
knowledge_base = TextKnowledgeBase("动手学机器学习")

# 添加一些文档到知识库
knowledge_base.add_document("Python Basic", "Python is a high-level programming language.", "python_basic.txt")
knowledge_base.add_document("Python Advanced",
                            "Python is widely used for web development, scientific computing, data analysis, artificial intelligence, and more.",
                            "python_advanced.txt")
knowledge_base.add_document("Machine Learning",
                            "Machine learning is a subset of artificial intelligence that involves training models to make predictions or decisions based on data.",
                            "machine_learning.txt")

# 搜索知识库中的文档
title, content = knowledge_base.search(["python", "development"])

print(title)
print(content)

# 关闭知识库
knowledge_base.close()
