from typing import List, Dict, Union, Tuple
from tqdm import tqdm
import re

def format_transcript_with_timestamps(transcript: List[Dict[str, Union[str, float]]]) -> str:
    """
    格式化字幕，保留时间戳。
    
    Args:
        transcript: 字幕列表
        
    Returns:
        str: 带时间戳的格式化文本
    """
    formatted_text = []
    for segment in transcript:
        minutes = int(segment['start'] // 60)
        seconds = int(segment['start'] % 60)
        time_str = f"[{minutes:02d}:{seconds:02d}]"
        formatted_text.append(f"{time_str} {segment['text'].strip()}")
    
    return "\n".join(formatted_text)

def extract_text_by_timerange(
    transcript: List[Dict[str, Union[str, float]]], 
    start_time: int, 
    end_time: int,
    buffer_seconds: int = 10
) -> Tuple[str, str]:
    """
    从字幕中提取指定时间范围内的文本，包括带时间戳和不带时间戳两种格式。
    
    Args:
        transcript: 字幕列表
        start_time: 开始时间（秒）
        end_time: 结束时间（秒）
        buffer_seconds: 前后缓冲时间（秒）
        
    Returns:
        Tuple[str, str]: (带时间戳的文本, 纯文本)
    """
    # 添加缓冲时间
    actual_start = max(0, start_time - buffer_seconds)
    actual_end = end_time + buffer_seconds
    
    # 过滤出指定时间范围内的字幕
    segments = [
        segment 
        for segment in transcript 
        if actual_start <= segment['start'] < actual_end
    ]
    
    if not segments:
        return "", ""
    
    # 生成带时间戳的文本
    timestamped_text = []
    for segment in segments:
        minutes = int(segment['start'] // 60)
        seconds = int(segment['start'] % 60)
        time_str = f"[{minutes:02d}:{seconds:02d}]"
        timestamped_text.append(f"{time_str} {segment['text'].strip()}")
    
    # 生成纯文本（用于概括）
    pure_text = []
    punctuation_marks = frozenset({'.', '?', '!', ':', ';'})
    
    for i, segment in enumerate(segments):
        text = segment['text'].strip()
        if not text:
            continue
            
        if i > 0:
            prev_text = pure_text[-1]
            if not any(prev_text.endswith(p) for p in punctuation_marks):
                pure_text[-1] = prev_text + ","
                
        pure_text.append(text)
    
    return "\n".join(timestamped_text), " ".join(pure_text)

def generate_chapter_summary(chapter: Dict[str, any], timestamped_text: str, pure_text: str) -> str:
    """
    为单个章节生成概括。
    
    Args:
        chapter: 章节信息
        timestamped_text: 带时间戳的原文
        pure_text: 用于概括的纯文本
        
    Returns:
        str: 章节概括
    """
    start_time = f"{chapter['start_time']//60:02d}:{chapter['start_time']%60:02d}"
    
    prompt = (
        f"请对以下视频章节内容进行概括。\n\n"
        f"章节信息：\n时间戳：{start_time}\n标题：{chapter['title']}\n\n"
        f"原始文本（带时间戳）：\n{timestamped_text}\n\n"
        f"处理后文本：\n{pure_text}\n\n"
        "要求：\n"
        "1. 以'**时间戳 – 标题**'格式开头；\n"
        "2. 用无序列表'-'的形式列出该章节的核心内容；\n"
        "3. 保留重要的数据和具体细节；\n"
        "4. 使用清晰、专业的中文表述；\n"
        "5. 确保概括完整、准确地反映原文内容；\n"
        "6. 直接输出结果，不要包含思考过程。\n"
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
        summary = result.get("response", "")
        
        # 移除<think>标签之间的内容
        summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL)
        
        return summary.strip()
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
        # 提取该章节的文本（带时间戳和纯文本）
        timestamped_text, pure_text = extract_text_by_timerange(
            transcript,
            chapter["start_time"],
            chapter["end_time"]
        )
        
        if not pure_text:
            print(f"Warning: No text found for chapter '{chapter['title']}'")
            continue
            
        # 生成该章节的概括
        summary = generate_chapter_summary(chapter, timestamped_text, pure_text)
        
        summaries.append({
            "title": chapter["title"],
            "timestamp": f"{chapter['start_time']//60:02d}:{chapter['start_time']%60:02d}",
            "summary": summary
        })
    
    return summaries 