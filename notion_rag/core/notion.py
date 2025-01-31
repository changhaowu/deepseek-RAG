from typing import List, Dict, Any
import requests
from datetime import datetime
from config.settings import NOTION_TOKEN, NOTION_DB_ID, NOTION_VERSION

class NotionClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"
        }
        
    def fetch_pages(self, last_sync_time: str = None) -> List[Dict[str, Any]]:
        """从Notion获取页面数据"""
        url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
        
        body = {}
        if last_sync_time:
            body["filter"] = {
                "timestamp": "last_edited_time",
                "last_edited_time": {"after": last_sync_time}
            }
            
        response = requests.post(url, headers=self.headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch from Notion: {response.status_code}")
            
        return response.json().get("results", [])
        
    def extract_page_content(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """从Notion页面提取结构化内容"""
        properties = page.get("properties", {})
        
        # 提取标题
        title = ""
        title_obj = properties.get("Name", {})
        if "title" in title_obj:
            title = "".join([t.get("plain_text", "") for t in title_obj["title"]])
            
        # 提取内容
        content = ""
        content_obj = properties.get("Content", {})
        if "rich_text" in content_obj:
            content = "".join([t.get("plain_text", "") for t in content_obj["rich_text"]])
            
        # 提取标签
        tags = []
        tag_obj = properties.get("Tags", {})
        if "multi_select" in tag_obj:
            tags = [item["name"] for item in tag_obj["multi_select"]]
            
        return {
            "page_id": page["id"],
            "title": title,
            "content": content,
            "tags": tags,
            "last_edited_time": page["last_edited_time"]
        }