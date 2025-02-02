from typing import List, Dict, Union
from tqdm import tqdm

def extract_text_by_timerange(
    transcript: List[Dict[str, Union[str, float]]], 
    start_time: int, 
    end_time: int
) -> str:
    """
    从字幕中提取指定时间范围内的文本。
    
    Args:
        transcript: 字幕列表
        start_time: 开始时间（秒）
        end_time: 结束时间（秒）
        
    Returns:
        str: 合并后的文本
    """
    # 过滤出指定时间范围内的字幕
    segments = [
        segment['text'].strip() 
        for segment in transcript 
        if start_time <= segment['start'] < end_time
    ]
    
    if not segments:
        return ""
    
    # 预定义标点符号集合
    punctuation_marks = frozenset({'.', '?', '!', ':', ';'})
    
    # 处理文本段落
    formatted_segments = []
    for i, text in enumerate(segments):
        if not text:  # 跳过空文本
            continue
            
        if i > 0:
            prev_text = formatted_segments[-1]
            # 如果前一段文本不以标点结尾，添加逗号
            if not any(prev_text.endswith(p) for p in punctuation_marks):
                formatted_segments[-1] = prev_text + ","
                
        formatted_segments.append(text)
    
    # 合并所有文本段落
    return " ".join(formatted_segments)

def generate_chapter_summary(chapter: Dict[str, any], text: str) -> str:
    """
    为单个章节生成概括。
    
    Args:
        chapter: 章节信息
        text: 该章节的文本内容
        
    Returns:
        str: 章节概括
    """
    prompt = (
        f"请对以下视频章节内容进行概括。章节标题：{chapter['title']}\n\n"
        f"章节内容：\n{text}\n\n"
        "要求：\n"
        "1. 提取该章节的核心内容和关键信息；\n"
        "2. 保留重要的数据和具体细节；\n"
        "3. 使用清晰、专业的中文表述；\n"
        "4. 概括篇幅适中，突出重点。\n"
    )
    
    try:
        import requests
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:70b-llama-distill-q4_K_M",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        print(f"Warning: Failed to generate chapter summary: {str(e)}")
        return ""

def process_chapters(
    chapters: List[Dict[str, any]], 
    transcript: List[Dict[str, Union[str, float]]]
) -> List[Dict[str, str]]:
    """
    处理所有章节并生成概括。
    
    Args:
        chapters: 章节列表
        transcript: 字幕列表
        
    Returns:
        List[Dict[str, str]]: 包含章节标题和概括的列表
    """
    summaries = []
    
    print("\n开始逐章节处理...")
    for chapter in tqdm(chapters, desc="Processing chapters"):
        # 提取该章节的文本
        chapter_text = extract_text_by_timerange(
            transcript,
            chapter["start_time"],
            chapter["end_time"]
        )
        
        if not chapter_text:
            print(f"Warning: No text found for chapter '{chapter['title']}'")
            continue
            
        # 生成该章节的概括
        summary = generate_chapter_summary(chapter, chapter_text)
        
        summaries.append({
            "title": chapter["title"],
            "timestamp": f"{chapter['start_time']//60:02d}:{chapter['start_time']%60:02d}",
            "summary": summary
        })
    
    return summaries 