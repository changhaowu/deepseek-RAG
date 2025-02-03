from typing import Dict, Tuple, List, Union
import requests
from bs4 import BeautifulSoup
import re
# from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various forms of YouTube URLs.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: YouTube video ID
        
    Raises:
        ValueError: If the video ID cannot be extracted from the URL
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Could not extract video ID from URL. Please check if the URL is valid.")

def get_video_info(video_url: str) -> Dict[str, str]:
    """
    Get video description and other metadata from YouTube.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        Dict[str, str]: Dictionary containing video information
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(video_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        
        # 尝试多种方式获取标题
        title = ""
        title_candidates = [
            soup.find("meta", {"property": "og:title"}),
            soup.find("meta", {"name": "title"}),
            soup.find("title"),
            soup.find("h1", {"class": "title"})
        ]
        
        for candidate in title_candidates:
            if candidate:
                if "content" in candidate.attrs:
                    title = candidate["content"]
                    break
                else:
                    title = candidate.text
                    break
        
        # 尝试多种方式获取描述
        description = ""
        desc_candidates = [
            soup.find("meta", {"property": "og:description"}),
            soup.find("meta", {"name": "description"}),
            soup.find("meta", {"itemprop": "description"})
        ]
        
        for candidate in desc_candidates:
            if candidate and "content" in candidate.attrs:
                description = candidate["content"]
                break
        
        return {
            "title": title.strip(),
            "description": description.strip()
        }
    except Exception as e:
        print(f"Warning: Could not fetch video info: {str(e)}")
        return {"title": "", "description": ""} 

def clean_description(description: str) -> str:
    """
    清理视频描述中的无关内容。
    
    Args:
        description: 原始描述文本
        
    Returns:
        str: 清理后的描述文本
    """
    # 需要移除的模式
    patterns_to_remove = [
        r'\d+ episodes',
        r'The Julia La Roche Show\s*(?:\n|$)',
        r'Podcasts\s*(?:\n|$)',
        r'Transcript\s*(?:\n|$)',
        r'Follow along using the transcript\.',
        r'Show transcript\s*(?:\n|$)',
        r'\d+(?:\.\d+)?K subscribers\s*(?:\n|$)',
        r'Videos\s*(?:\n|$)',
        r'About\s*(?:\n|$)',
        r'Show less\s*(?:\n|$)',
        r'View all\s*(?:\n|$)',
        r'Chapters\s*(?:\n|$)'
    ]
    
    cleaned = description
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # 移除多余的空行
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    return cleaned.strip()

def generate_description_summary(description: str) -> Dict[str, str]:
    """
    从描述生成标题和摘要。
    
    Args:
        description: 清理后的描述文本
        
    Returns:
        Dict[str, str]: 包含生成的标题和摘要的字典
    """
    prompt = (
        f"请根据以下视频描述生成一个简洁的标题和摘要。\n\n"
        f"原始描述：\n{description}\n\n"
        "要求：\n"
        "1. 标题应简洁明了，突出视频的主要内容和关键人物；\n"
        "2. 摘要应保留描述中的核心信息，去除冗余内容；\n"
        "3. 使用专业、清晰的语言；\n"
        "4. 输出格式：\n"
        "标题：xxx\n"
        "摘要：xxx\n"
    )
    
    try:
        # import requests
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:70b-llama-distill-q4_K_M",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json().get("response", "")
        
        # 解析生成的标题和摘要
        title_match = re.search(r'标题：(.*?)(?:\n|$)', result)
        summary_match = re.search(r'摘要：(.*)', result, re.DOTALL)
        
        return {
            "title": title_match.group(1).strip() if title_match else "",
            "description": summary_match.group(1).strip() if summary_match else ""
        }
    except Exception as e:
        print(f"Warning: Failed to generate description summary: {str(e)}")
        return {"title": "", "description": ""}

def get_transcript(video_url: str) -> Tuple[List[Dict[str, Union[str, float]]], Dict[str, str]]:
    """
    Get transcript and video info for a YouTube video.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        Tuple[List[Dict[str, Union[str, float]]], Dict[str, str]]: 
            Tuple of (transcript segments, video info)
        
    Raises:
        Exception: If transcript cannot be retrieved
    """
    try:
        video_id = extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        video_info = get_video_info(f"https://www.youtube.com/watch?v={video_id}")
        
        # 清理描述并生成摘要
        cleaned_description = clean_description(video_info["description"])
        summary_info = generate_description_summary(cleaned_description)
        
        # 如果生成的标题为空，使用原始标题
        if not summary_info["title"] and video_info["title"]:
            summary_info["title"] = video_info["title"]
        
        return transcript, summary_info
    except Exception as e:
        raise Exception(f"Failed to get transcript: {str(e)}") 