from core.notion import NotionClient
from core.embeddings import EmbeddingProcessor
from core.storage import StorageManager
from core.rag import RAGEngine

def main():
    # 初始化组件
    notion_client = NotionClient()
    embedding_processor = EmbeddingProcessor()
    storage_manager = StorageManager()
    rag_engine = RAGEngine(storage_manager.qdrant_client, embedding_processor)
    
    # 1. 获取上次同步时间
    last_sync_time = storage_manager.get_last_sync_time()
    
    # 2. 从Notion获取更新的页面
    raw_pages = notion_client.fetch_pages(last_sync_time)
    if not raw_pages:
        print("No new or updated pages.")
        return
        
    # 3. 处理页面内容
    processed_pages = [notion_client.extract_page_content(p) for p in raw_pages]
    
    # 4. 存储原始页面
    storage_manager.store_pages(processed_pages)
    
    # 5. 生成文档分块和嵌入
    chunks_with_embeddings = embedding_processor.process_pages(processed_pages)
    
    # 6. 存储分块和向量
    storage_manager.store_chunks(chunks_with_embeddings)
    
    # 7. 测试查询
    query = "请介绍机器学习模型训练的基本步骤"
    results = rag_engine.search(query)
    if results:
        answer = rag_engine.generate_answer(query, results)
        print("\nQuery:", query)
        print("\nAnswer:", answer)
    
if __name__ == "__main__":
    main()