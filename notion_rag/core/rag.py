from typing import List, Dict, Any
import requests
from config.settings import OLLAMA_URL, QDRANT_COLLECTION_NAME

class RAGEngine:
    def __init__(self, qdrant_client, embedding_processor):
        self.qdrant_client = qdrant_client
        self.embedding_processor = embedding_processor
        
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """语义搜索相关文档"""
        query_vector = self.embedding_processor.encode_query(query)
        results = self.qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            top=top_k
        )
        return results
        
    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """生成回答"""
        context_text = self._format_context(context_docs)
        prompt = self._create_prompt(query, context_text)
        
        response = requests.post(
            OLLAMA_URL,
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt},
            stream=True
        )
        
        return "".join(chunk for chunk in response.iter_lines(decode_unicode=True) if chunk)
        
    def _format_context(self, docs: List[Dict[str, Any]]) -> str:
        """格式化上下文文本"""
        context = []
        for doc in docs:
            payload = doc.payload
            context.append(f"[Title: {payload['title']}]\n{payload['text']}\n")
        return "\n".join(context)
        
    def _create_prompt(self, query: str, context: str) -> str:
        """创建prompt模板"""
        return f"""
                You are a helpful assistant. Answer the following question based on the provided context.

                Question: {query}

                Context:
                {context}

                Answer:
                """.strip()