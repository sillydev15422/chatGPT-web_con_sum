from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import time
import requests
OPENAI_API_KEY = "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"

PINECONE_KEY = "f89cdc90-9d00-4965-9156-ee04407c42ae"
PINECONE_ENV = "northamerica-northeast1-gcp"

if __name__ == '__main__':

    loader = UnstructuredFileLoader("test.txt")
    data = loader.load()
    # print(data)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(data)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    print('123123123', embeddings)
    # initialize pinecone
    pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)
    index_name = "quickstart"
    namespace = "scrapping"

    docsearch = Pinecone.from_texts(
        [t.page_content for t in texts], embeddings,
        index_name=index_name, namespace=namespace)
    print('End')
