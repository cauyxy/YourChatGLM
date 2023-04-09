import jieba.posseg as pseg

pos_tags = ["v", "vd",  "a", "ad",  "d", "m", "q", "r", "p", "c", "u", "xc", "x"]


def jieba_ner(text):
    # Tokenize text and filter out tokens with specified POS tags
    tokens = [token for token in pseg.cut(text) if token.flag not in pos_tags]
    print(tokens)

    # If only one token is left, return it directly
    if len(tokens) == 1:
        return tokens[0].word

    # Sort tokens by length and get the longest two
    tokens_sorted = sorted(tokens, key=lambda x: len(x.word), reverse=True)
    longest_tokens = [tokens_sorted[0].word, tokens_sorted[1].word]

    return longest_tokens
