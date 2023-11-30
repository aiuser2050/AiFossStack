from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# global variables
base_url="http://localhost:11434"   #where the LLM server lives
model="mistral"  #orca-mini , mistral, or zephyr , "mistral-openorca"
temperature = 0.2
search_type = "similarity"   # or "mmr"
top_k = 5
active_index = "index"
llm = Ollama(base_url=base_url, model=model, temperature=temperature, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

system_prompt = '''
You are an expert. Execute the instruction given to you following these criteria:
* Cite the exact source next to each paragraph.
* Indicate date, location, and entities related to each fact you cite.
* Write in an elegant, professional, diplomatic style. 
'''
template = system_prompt + '''Use the following pieces of context: {context} to respond the instruction in this: {question}.
If the context provided does not contain the answer:
* do not generate a response, 
* instead respond with this sentence exactly: "The knowledge base does not have enough information about your question.
''' 

## Vars for indexing
input_dir = "./data/"   # where raw data is stored
chunk_size=1000
chunk_overlap=200
persist_directory="./indexes/"   # folder where the vector databases will persist

# finding list of existing indexes
import os
def list_indexes():
    return os.listdir("./indexes/")

#Directory loader, including text, pdf
from langchain.document_loaders import DirectoryLoader
def load_data(input_dir = "./data/"):
    fulldocs = DirectoryLoader(input_dir , use_multithreading=True).load()
    return fulldocs

# split files into chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter
def chunking(data, chunk_size=chunk_size, chunk_overlap=chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(data)
    return chunks

#Vectorize & store
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
# index_name = "undocs"
# vectorstore = Chroma.from_documents(documents=all_splits, embedding=GPT4AllEmbeddings(), persist_directory="./indexes/" + index_name)

def vectorize(documents, index_name = "newindex", persist_directory="./indexes/"):
    vectorstore = Chroma.from_documents(documents=documents, embedding=GPT4AllEmbeddings(), persist_directory=persist_directory + index_name)
    return vectorstore

########### To do in Langchain ############

# # Creating a new index
# def index_data(knowledgebase = "data", embed_model="local", model="zephyr", temperature=0.2, index_name="newindex"):
#     persist_dir = "./indexes/" + index_name
#     reader = SimpleDirectoryReader(input_dir=knowledgebase, recursive=True)
#     docs = reader.load_data()
#     service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)  #try model="zephyr" for better but slower results.
#     index = VectorStoreIndex.from_documents(docs, service_context=service_context)
#     index.storage_context.persist(persist_dir=persist_dir)

# #Loading an index from disk
# from llama_index import StorageContext, load_index_from_storage
# def load_index(embed_model="local", model="zephyr", temperature=0.2, persist_dir="./indexes/index"):
#     storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
#     service_context = ServiceContext.from_defaults(llm=llm , embed_model=embed_model)  #try model="zephyr" for better but slower results.
#     index = load_index_from_storage(storage_context, service_context=service_context)
#     return index



########## content management ########
welcome_text = '''# Welcome, I am your expert companion. \n ## I will respond only based on the data sources provided to me.'''