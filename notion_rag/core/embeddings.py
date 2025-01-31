from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL_NAME
from utils.text_utils import chunk_text

class EmbeddingProcessor:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        
    def process_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理页面并生成嵌入向量"""
        results = []
        
        for page in pages:
            content = page["content"]
            if not content.strip():
                continue
                
            # 文本分块
            chunks = chunk_text(content)
            
            # 为每个分块生成嵌入向量
            for chunk in chunks:
                embedding = self.model.encode(chunk)
                doc_info = {
                    "text": chunk,
                    "embedding": embedding,
                    "metadata": {
                        "page_id": page["page_id"],
                        "title": page["title"],
                        "tags": page["tags"],
                        "last_edited_time": page["last_edited_time"]
                    }
                }
                results.append(doc_info)
                
        return results
        
    def encode_query(self, query: str):
        """对查询文本进行向量化"""
        return self.model.encode(query)