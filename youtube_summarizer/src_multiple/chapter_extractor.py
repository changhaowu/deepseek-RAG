from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def timestamp_to_seconds(timestamp: str) -> int:
    """Convert YouTube timestamp (HH:MM:SS or MM:SS) to seconds."""
    # 移除可能的前导零
    timestamp = re.sub(r'^0+:', '', timestamp)
    parts = timestamp.split(':')
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

def merge_chapters_by_timestamp(chapters: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    合并时间戳相同的章节。
    
    Args:
        chapters: 原始章节列表
        
    Returns:
        List[Dict[str, any]]: 合并后的章节列表
    """
    if not chapters:
        return []
    
    # 按时间戳分组
    timestamp_groups = {}
    for chapter in chapters:
        start_time = chapter['start_time']
        if start_time not in timestamp_groups:
            timestamp_groups[start_time] = []
        timestamp_groups[start_time].append(chapter)
    
    # 合并每个时间戳组的标题
    merged = []
    for start_time in sorted(timestamp_groups.keys()):
        group = timestamp_groups[start_time]
        if len(group) == 1:
            merged.append(group[0])
        else:
            # 使用第一个章节作为基础
            merged_chapter = group[0].copy()
            # 合并所有标题
            titles = [ch['title'] for ch in group]
            merged_chapter['title'] = ', '.join(titles)
            merged.append(merged_chapter)
    
    return merged

def merge_close_chapters(chapters: List[Dict[str, any]], min_duration: int = 60) -> List[Dict[str, any]]:
    """
    合并时间间隔过小的章节。
    
    Args:
        chapters: 原始章节列表
        min_duration: 最小章节时长（秒）
        
    Returns:
        List[Dict[str, any]]: 合并后的章节列表
    """
    if not chapters:
        return []
    
    # 先合并相同时间戳的章节
    chapters = merge_chapters_by_timestamp(chapters)
    
    # 按开始时间排序
    sorted_chapters = sorted(chapters, key=lambda x: x['start_time'])
    
    # 合并结果
    merged = []
    current = sorted_chapters[0].copy()
    
    for i, next_chapter in enumerate(sorted_chapters[1:], 1):
        # 计算下一个章节的持续时间
        next_duration = (sorted_chapters[i+1]['start_time'] if i < len(sorted_chapters)-1 
                        else next_chapter['start_time'] + 3600) - next_chapter['start_time']
        
        # 如果下一个章节的持续时间小于最小时长，合并标题
        if next_duration < min_duration:
            current['title'] = f"{current['title']}, {next_chapter['title']}"
            current['end_time'] = next_chapter['end_time']
        else:
            merged.append(current)
            current = next_chapter.copy()
    
    # 添加最后一个章节
    merged.append(current)
    
    return merged

def parse_chapters_from_description(description: str) -> List[Dict[str, any]]:
    """
    从视频描述中解析章节信息。
    
    Args:
        description: 视频描述文本
        
    Returns:
        List[Dict[str, any]]: 包含章节信息的列表
    """
    chapters = []
    # 匹配时间戳和标题的正则表达式
    # 支持多种格式：
    # 00:00 Title
    # 00:00:00 Title
    # [00:00] Title
    # (00:00) Title
    timestamp_pattern = r'(?:^|\n)(?:\[|\()?(\d{1,2}:(?:\d{1,2}:)?\d{1,2})(?:\]|\))?\s*[-\s]*(.*?)(?=\n|$)'
    
    matches = re.finditer(timestamp_pattern, description, re.MULTILINE)
    
    for match in matches:
        timestamp, title = match.groups()
        title = title.strip()
        if title:  # 只有当标题不为空时才添加
            start_time = timestamp_to_seconds(timestamp)
            chapters.append({
                "title": title,
                "start_time": start_time
            })
    
    # 按时间戳排序
    chapters.sort(key=lambda x: x["start_time"])
    
    # 计算每个章节的结束时间
    for i in range(len(chapters)-1):
        chapters[i]["end_time"] = chapters[i+1]["start_time"]
    
    # 最后一个章节的结束时间设置为开始时间后一小时（或其他合适的值）
    if chapters:
        chapters[-1]["end_time"] = chapters[-1]["start_time"] + 3600
    
    # 先合并相同时间戳的章节，再合并时长过短的章节
    chapters = merge_close_chapters(chapters)
    
    return chapters

def get_youtube_chapters(video_url: str, video_description: str = "") -> List[Dict[str, any]]:
    """
    获取YouTube视频的章节信息，优先从描述中解析。
    
    Args:
        video_url: 视频URL
        video_description: 视频描述（如果已经获取）
        
    Returns:
        List[Dict[str, any]]: 章节信息列表
    """
    # 首先尝试从描述中解析
    if video_description:
        chapters = parse_chapters_from_description(video_description)
        if chapters:
            return chapters
    
    # 如果描述中没有找到章节，尝试使用Selenium
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    print("Starting Chrome in headless mode...")
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print(f"Navigating to {video_url}")
        driver.get(video_url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 15)
        
        # 尝试多个可能的章节选择器
        chapter_selectors = [
            "ytd-chapter-renderer",  # 新版YouTube章节
            "a#chapter-title",       # 旧版章节标题
            ".ytp-chapter-title-content"  # 播放器中的章节
        ]
        
        chapters = []
        for selector in chapter_selectors:
            try:
                # 滚动页面以加载所有章节
                driver.execute_script("window.scrollTo(0, 500)")
                time.sleep(2)
                
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        title = element.text.strip()
                        # 尝试获取时间戳
                        timestamp = ""
                        try:
                            timestamp = element.get_attribute("data-timestamp") or \
                                      element.get_attribute("href").split("t=")[-1] or \
                                      element.find_element(By.CSS_SELECTOR, ".timestamp").text
                        except:
                            continue
                            
                        if title and timestamp:
                            chapters.append({
                                "title": title,
                                "start_time": timestamp_to_seconds(timestamp)
                            })
                    break  # 如果找到章节就退出循环
            except Exception as e:
                print(f"Failed with selector {selector}: {str(e)}")
                continue
        
        # 计算每个章节的结束时间
        for i in range(len(chapters)-1):
            chapters[i]["end_time"] = chapters[i+1]["start_time"]
        
        # 最后一个章节的结束时间设置为视频结束
        if chapters:
            try:
                duration_element = driver.find_element(By.CSS_SELECTOR, ".ytp-time-duration")
                total_duration = timestamp_to_seconds(duration_element.text)
                chapters[-1]["end_time"] = total_duration
            except:
                # 如果无法获取视频总时长，设置一个较大的值
                chapters[-1]["end_time"] = chapters[-1]["start_time"] + 3600
        
        return chapters
        
    except Exception as e:
        print(f"Failed to get chapters: {str(e)}")
        return []
        
    finally:
        if driver:
            driver.quit()
            print("Chrome closed successfully") 