# "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"
import requests
from tqdm import tqdm
import time

# 设置你的 Notion Integration Token
NOTION_TOKEN = "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"

# Notion API 版本
NOTION_VERSION = "2022-06-28"

# Notion API 搜索端点
NOTION_SEARCH_URL = "https://api.notion.com/v1/search"

def get_notion_databases():
    """使用 Notion API 搜索可访问的数据库"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }

    # 显示进度条，表示正在查询数据库
    with tqdm(total=100, desc="正在发送请求到 Notion API") as pbar:
        for i in range(10):
            time.sleep(0.1)  # 模拟请求发送过程
            pbar.update(10)

    # 发送搜索请求获取数据库信息
    response = requests.post(NOTION_SEARCH_URL, headers=headers, json={"filter": {"property": "object", "value": "database"}})

    if response.status_code == 200:
        data = response.json()
        databases = data.get("results", [])

        if not databases:
            print("❌ 没有找到可访问的 Notion 数据库，请检查你的 Integration 权限！")
            return

        print("✅ 找到以下 Notion 数据库：")
        for db in databases:
            db_id = db["id"].replace("-", "")  # 去掉 Notion ID 里的 "-"
            title_list = db.get("title", [])
            if title_list:
                db_title = title_list[0].get("text", {}).get("content", "无标题")
            else:
                db_title = "无标题"
            print(f"- **{db_title}** → `Database ID`: {db_id}")
            

    else:
        print(f"❌ 请求失败，错误代码: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    get_notion_databases()