from typing import List, Dict, Any
from pymongo import MongoClient
import chromadb
from chromadb.config import Settings
from config.settings import *

class StorageManager:
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self._init_chroma()
        
    def _init_chroma(self):
        """初始化ChromaDB集合"""
        try:
            self.collection = self.chroma_client.get_collection(CHROMA_COLLECTION_NAME)
        except:
            self.collection = self.chroma_client.create_collection(CHROMA_COLLECTION_NAME)
            
    def store_pages(self, pages: List[Dict[str, Any]]):
        """存储原始页面到MongoDB"""
        collection = self.mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_PAGES]
        for page in pages:
            collection.update_one(
                {"page_id": page["page_id"]},
                {"$set": page},
                upsert=True
            )
            
    def store_chunks(self, chunks: List[Dict[str, Any]]):
        """存储分块到MongoDB和ChromaDB"""
        # 存储到MongoDB
        collection = self.mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_CHUNKS]
        for chunk in chunks:
            collection.insert_one({
                "text": chunk["text"],
                "embedding": chunk["embedding"].tolist(),
                "metadata": chunk["metadata"]
            })
            
        # 存储到ChromaDB
        ids = [str(i) for i in range(len(chunks))]
        embeddings = [chunk["embedding"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
    def get_last_sync_time(self) -> str:
        """获取最后同步时间"""
        collection = self.mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_PAGES]
        last_page = collection.find_one(sort=[("last_edited_time", -1)])
        return last_page["last_edited_time"] if last_page else None