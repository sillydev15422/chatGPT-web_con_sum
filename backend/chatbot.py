from fastapi import APIRouter, Request
import re
import requests
from bs4 import BeautifulSoup
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from pydantic import BaseModel
import array as arr
from urllib.parse import urljoin
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain import OpenAI, PromptTemplate, LLMChain

import spacy
nlp = spacy.load("en_core_web_sm")
doc = []
price_array = []
router = APIRouter()
limit_count = 25

OPENAI_API_KEY = "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"
PINECONE_ENV = "us-east1-gcp"
PINECONE_KEY = "f53897af-ce2e-437a-a533-6222af0aace2"

# ------------------data-------------------------#
init_urls = ""


class Links(BaseModel):
    data: object


class Query(BaseModel):
    data: object


def saveTrainData(all_links, init_url):
    for link in all_links:
        link = urljoin(init_url, link)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup)
        tags = soup.find_all(
            ['div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'b'])
        all_text = ''
        for tag in tags:
            all_text += (tag.get_text() + '\n')
            print(tag.get_text())
        try:
            with open('test.txt', 'w', encoding='utf-8') as f:
                f.write(all_text)
        except Exception as e:
            print(e)

        doc = nlp(all_text)

        price = None
        option = None
        # for ent in doc.ents:
        # print(ent.text.strip('$'))
        # print('entententent', ent)
        # Check if entity is a price
        # print(ent.label_)
        # if ent.label_ == 'MONEY':
        # Extract the numerical value from the price entity

        # if(ent.label_ == 'MONEY'):
        #     price_array.append(ent)
        # print('money', price)
        # Check if entity is an option
        # print(ent.text.lower())
        # if ent.label_ == 'PERSON':
        #     option = ent.text.lower()
        # print('option', option)
        # Print the results
        # print(f"The price of {option} is ${price}")

    return


# ------------------crawling-------------------------#

def crawl_website(init_url):
    print('11111111111111111111', init_url)
    response = requests.get(init_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = ['/']
    all_links = []
    for link in soup.find_all('a'):
        i = 0
        if (link.get('href') == None):
            continue
        links.append(link.get('href'))
    # Print out the first 25 links
    all_links = links[:25]
    print(all_links)
    return all_links


@router.post('/getReply')
async def getReply(data: Links):
    # print(question)
    # print(data.data)
    init_urls = data
    print('123123123123', data)
    for init_url in init_urls:
        print(init_url[1])
        all_links = crawl_website(init_url[1])
        print(all_links)
        saveTrainData(all_links, init_url[1])
        loader = UnstructuredFileLoader("test.txt")
        data = loader.load()
        # print(data)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(data)
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        # initialize pinecone
        pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)
        index_name = "quickstart"
        namespace = "scrapping"
        docsearch = Pinecone.from_texts(
            [t.page_content for t in texts], embeddings,
            index_name=index_name, namespace=namespace)
        print('End')


@router.post('/getInput')
async def getInput(data: Links):
    init_urls = data
    for init_url in init_urls:
        all_links = crawl_website(init_url[1])
        try:
            saveTrainData(all_links, init_url[1])
        except:
            print('Please confirm again.')
        print('\n Finished Saving Files \n')

        loader = UnstructuredFileLoader("test.txt")
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(data)

    # getSummary
        llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
        text_splitter1 = CharacterTextSplitter()
        with open("test.txt", 'r', encoding='UTF-8') as f:
            state_of_the_union = f.read()
        texts = text_splitter1.split_text(state_of_the_union)
        docs = [Document(page_content=t) for t in texts[:3]]
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        try:
            sum = str(chain.run(input_documents=docs))
        except:
            print('error')
            # for price in price_array:
        # print(price_array)
        return {"sum": sum}
    # chain.run(docs)


@router.post('/getQuery')
async def getQuery(data: Query):
    query = data
    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")
    pinecone.init(
        api_key=PINECONE_KEY,
        environment=PINECONE_ENV
    )
    index_name = "quickstart"
    namespace = "scraping"

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    doclist = Pinecone.from_existing_index(
        index_name, embeddings, namespace=namespace)

    docs = doclist.similarity_search(
        data.data, include_metadata=True, namespace=namespace)

    answer = str(chain.run(input_documents=docs, question=data.data))
    print(answer)

    return {"answer": answer}
