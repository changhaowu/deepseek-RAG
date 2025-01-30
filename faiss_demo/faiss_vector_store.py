import logging
import sys
import os
import faiss
from llama_index.core import (
    SimpleDirectoryReader,
    load_index_from_storage,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from IPython.display import Markdown, display

# Logging setup
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# 设置 Ollama 模型
llm = Ollama(model="deepseek-r1:32b-qwen-distill-q8_0", request_timeout=120.0)
embed_model = OllamaEmbedding(model_name="deepseek-r1:32b-qwen-distill-q8_0")
Settings.llm = llm
Settings.embed_model = embed_model

# 获取实际的嵌入维度
sample_text = "Sample text to get embedding dimension"
sample_embedding = embed_model.get_text_embedding(sample_text)
d = len(sample_embedding)
print(f"Actual embedding dimension: {d}")
faiss_index = faiss.IndexFlatL2(d)

# Directory for data
data_dir = "./paul_graham/"
# os.makedirs(data_dir, exist_ok=True)

# Download data
# os.system(f"wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O '{data_dir}paul_graham_essay.txt'")

# Load documents
documents = SimpleDirectoryReader(data_dir).load_data()

# Create and save Faiss index
vector_store = FaissVectorStore(faiss_index=faiss_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, 
    storage_context=storage_context,
)
index.storage_context.persist()

# Load index from storage
vector_store = FaissVectorStore.from_persist_dir("./storage")
storage_context = StorageContext.from_defaults(
    vector_store=vector_store, 
    persist_dir="./storage"
)
index = load_index_from_storage(storage_context=storage_context)

# Query the index
query_engine = index.as_query_engine()

# Sample queries
response1 = query_engine.query("What did the author do growing up?")
print(f"Response 1: {response1}")

response2 = query_engine.query("What did the author do after his time at Y Combinator?")
print(f"Response 2: {response2}")