import os
from pathlib import Path

# Notion配置
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "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")
NOTION_DB_ID = os.getenv("NOTION_DB_ID", "172a93fa70f0800f89baee1cfe7745cd")
NOTION_VERSION = "2022-06-28"

# MongoDB配置
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "notion_rag"
MONGO_COLLECTION_PAGES = "notion_pages"
MONGO_COLLECTION_CHUNKS = "notion_chunks"

# Qdrant配置
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "notion_vectors"

# 模型配置
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIM = 768

# Ollama配置
OLLAMA_URL = "http://localhost:11411/completions"

# 文本分块配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
