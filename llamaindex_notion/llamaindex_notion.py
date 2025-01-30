import os
import logging
from llama_index.core import SummaryIndex
from llama_index.readers.notion import NotionPageReader
from IPython.display import Markdown, display

# 启用详细日志
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# 1. 设置你的 Notion Integration Token 和 Database ID
integration_token = "your-notion-integration-token"
database_id = "your-notion-database-id"

# 2. 读取 Notion 数据库
documents = NotionPageReader(integration_token=integration_token).load_data(
    database_id=database_id
)

# 3. 创建索引
index = SummaryIndex.from_documents(documents)

# 4. 进行查询
query_engine = index.as_query_engine()
response = query_engine.query("请总结数据库内容")

# 5. 展示结果
display(Markdown(f"<b>{response}</b>"))