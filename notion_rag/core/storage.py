from typing import List, Dict, Any
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config.settings import *

class StorageManager:
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._init_qdrant()
        
    def _init_qdrant(self):
        """初始化Qdrant集合"""
        collections = [c.name for c in self.qdrant_client.get_collections().collections]
        if QDRANT_COLLECTION_NAME not in collections:
            self.qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
            )
            
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
        """存储分块到MongoDB和Qdrant"""
        # 存储到MongoDB
        collection = self.mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_CHUNKS]
        for chunk in chunks:
            collection.insert_one({
                "text": chunk["text"],
                "embedding": chunk["embedding"].tolist(),
                "metadata": chunk["metadata"]
            })
            
        # 存储到Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            points.append(PointStruct(
                id=i,
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    **chunk["metadata"]
                }
            ))
            
        self.qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )
        
    def get_last_sync_time(self) -> str:
        """获取最后同步时间"""
        collection = self.mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_PAGES]
        last_page = collection.find_one(sort=[("last_edited_time", -1)])
        return last_page["last_edited_time"] if last_page else None