from typing import List
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str) -> List[str]:
    """文本分块，支持重叠"""
    chunks = []
    start = 0
    
    while start < len(text):
        # 取一个块
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        
        # 如果不是最后一块，尝试在一个完整的句子结束处截断
        if end < len(text):
            last_period = chunk.rfind('。')
            if last_period != -1:
                end = start + last_period + 1
                chunk = text[start:end]
        
        chunks.append(chunk)
        # 考虑重叠移动窗口
        start = end - CHUNK_OVERLAP
        
    return chunks