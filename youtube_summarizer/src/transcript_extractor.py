from typing import List, Dict, Union, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def get_video_info_fallback(video_url: str) -> Dict[str, str]:
    """
    Fallback method using requests and BeautifulSoup to get video info.
    """
    try:
        # 使用更完整的headers模拟真实浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        # 首先尝试获取完整页面
        response = requests.get(video_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        
        # 尝试多种方式获取描述
        description = ""
        # 1. 通过meta标签
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc and "content" in meta_desc.attrs:
            description = meta_desc["content"]
        
        # 2. 通过JSON-LD
        if not description:
            script_tag = soup.find("script", {"type": "application/ld+json"})
            if script_tag:
                import json
                try:
                    json_data = json.loads(script_tag.string)
                    if isinstance(json_data, dict):
                        description = json_data.get("description", "")
                except:
                    pass
        
        # 获取标题
        title = ""
        meta_title = soup.find("meta", {"name": "title"})
        if meta_title and "content" in meta_title.attrs:
            title = meta_title["content"]
        
        # 如果meta标签没有标题，尝试其他方式
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text
        
        return {
            "title": title.strip(),
            "description": description.strip()
        }
    except Exception as e:
        print(f"Warning: Fallback method failed: {str(e)}")
        return {"title": "", "description": ""}

def get_video_info(video_url: str) -> Dict[str, str]:
    """
    Get complete video description and metadata using multiple methods.
    """
    # 首先尝试使用fallback方法（更快且更可靠）
    info = get_video_info_fallback(video_url)
    if info["description"] and len(info["description"]) > 100:  # 如果获取到了较长的描述
        return info
        
    # 如果fallback方法没有获取到足够的信息，尝试使用Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 使用新的headless模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # 添加更多的错误处理信息
    print("Attempting to start Chrome in headless mode...")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome started successfully")
        
        print(f"Navigating to {video_url}")
        driver.get(video_url)
        
        # 增加页面加载等待时间
        wait = WebDriverWait(driver, 15)
        
        # 获取标题
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer"))
            )
            info["title"] = title_element.text
            print("Title found successfully")
        except Exception as e:
            print(f"Failed to get title: {str(e)}")
        
        # 尝试点击"显示更多"按钮
        try:
            # 滚动到按钮位置
            driver.execute_script("window.scrollTo(0, 500)")
            time.sleep(2)
            
            # 尝试多个可能的选择器
            selectors = [
                "tp-yt-paper-button#expand",
                "ytd-button-renderer#expand",
                "ytd-text-inline-expander#expand",
                "//button[contains(text(), '显示更多') or contains(text(), 'Show more')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        more_button = driver.find_element(By.XPATH, selector)
                    else:
                        more_button = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", more_button)
                    print("Successfully clicked 'Show more' button")
                    time.sleep(2)
                    break
                except:
                    continue
        except Exception as e:
            print(f"Failed to click 'Show more' button: {str(e)}")
        
        # 获取描述
        try:
            desc_selectors = [
                "ytd-video-secondary-info-renderer #description",
                "ytd-expander#description",
                "#description-inline-expander",
                "//div[@id='description']"
            ]
            
            for selector in desc_selectors:
                try:
                    if selector.startswith("//"):
                        desc_element = driver.find_element(By.XPATH, selector)
                    else:
                        desc_element = driver.find_element(By.CSS_SELECTOR, selector)
                    info["description"] = desc_element.text
                    print("Description found successfully")
                    break
                except:
                    continue
        except Exception as e:
            print(f"Failed to get description: {str(e)}")
        
        return info
        
    except Exception as e:
        print(f"Selenium method failed: {str(e)}")
        return info
    
    finally:
        if driver:
            try:
                driver.quit()
                print("Chrome closed successfully")
            except:
                print("Failed to close Chrome properly")

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
        return transcript, video_info
    except Exception as e:
        raise Exception(f"Failed to get transcript: {str(e)}")

def format_transcript(transcript: List[Dict[str, Union[str, float]]]) -> str:
    """
    Format transcript segments into a readable text document.
    Adds commas between segments that don't end with punctuation marks.
    
    Args:
        transcript (List[Dict[str, Union[str, float]]]): List of transcript segments
        
    Returns:
        str: Formatted transcript text with proper punctuation
    """
    # 预处理：过滤空段落并提前准备好文本
    segments = [(i, segment['text'].strip()) 
               for i, segment in enumerate(transcript) 
               if segment['text'].strip()]
    
    if not segments:
        return ""
    
    # 预定义标点符号集合
    punctuation_marks = frozenset({'.', '?', '!', ':', ';'})
    
    # 使用列表推导式和条件表达式优化处理
    formatted_segments = []
    with tqdm(total=len(segments), desc="Formatting transcript") as pbar:
        for i, (_, text) in enumerate(segments):
            if i > 0:
                prev_text = formatted_segments[-1]
                # 使用 any() 和生成器表达式优化标点符号检查
                if not any(prev_text.endswith(p) for p in punctuation_marks):
                    formatted_segments[-1] = prev_text + ","
            formatted_segments.append(text)
            pbar.update(1)
    
    # 直接join，避免额外的空格处理
    return " ".join(formatted_segments) 

