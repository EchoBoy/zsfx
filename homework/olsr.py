



# 1. 预处理(nltk.download('stopwords'), nltk.download('wordnet')
#   1.1 标点符号、去除停止词、xml转义符号、非打印字符、url、长度小于2的字符。
#   1.2 porter stemmer 词干提取/ wordnet lemmatizer 词形还原

import re
import nltk
from pymongo import MongoClient
import json
mongo_client = MongoClient()
coll_articles = mongo_client.nlp.articles
coll_documents = mongo_client.nlp.documents
coll_querys = mongo_client.nlp.querys
coll_train = mongo_client.nlp.train_relationship
coll_test = mongo_client.nlp.test_relationship


query_clean_path = './data/query_simple.txt'
document_clean_path = './data/documents_simple.tx'


def pre_process():
    # xml转义符 &...;
    xml_symbols_re = re.compile(r'&.*?;')
    stop_words = nltk.corpus.stopwords.words('english')
    # pick out sequences of alphanumeric characters as tokens and drop everything else
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    wordnet_lemmatizer = nltk.stem.WordNetLemmatizer()
    

    def clean(s):
        s = xml_symbols_re.sub(lambda m: ' ', s)
        return [word for word in tokenizer.tokenize(s) if word not in stop_words and len(word) > 1]

    def lemmatize(words):
        return [wordnet_lemmatizer.lemmatize(word) for word in words]

    with open(query_clean_path, 'wt') as f:
        for item in coll_querys.find({}):
            new_item = dict()
            new_item['id'] = item['_id']
            new_item['query'] = lemmatize(clean(item['query']))
            f.write('{0}\n'.format(new_item))

    with open(document_clean_path, 'wt', encoding='utf-8') as f:
        for item in coll_documents.find({}):
            new_item = dict()
            new_item['id'] = item['_id']
            new_item['title'] = lemmatize(clean(item['title']))
            f.write('{0}\n'.format(new_item))


def read_doucments(url=document_clean_path):
    docs = list()
    with open(url, 'rt', encoding='utf-8') as f:
        for line in f:
            line = line.replace("'", '"').replace('\n', '')
            docs.append(json.loads(line))
    return docs

'''
def train():

    for i in range(201, 251):
        qid = str(i)
        for relationship in coll_train.find({'query_id':qid}):
'''


if __name__ == '__main__':
    r = read_doucments()
    print(len(r), r[0])




