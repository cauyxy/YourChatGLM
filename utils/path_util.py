import base64


def to_alnum(text):
    """
    将文本中的所有字符都进行 base64 编码，返回处理后的字符串
    """
    return base64.urlsafe_b64encode(text.encode()).decode()


def from_alnum(text):
    """
    将文本中的所有字符都进行 base64 解码，返回处理后的字符串
    """
    return base64.urlsafe_b64decode(text.encode()).decode()
