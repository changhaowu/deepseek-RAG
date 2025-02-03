import sys
import os
import time

# 添加父目录到系统路径以导入原有模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_multiple.transcript_extractor import get_transcript

from chapter_extractor import get_youtube_chapters, parse_chapters_from_description
from text_processor import process_chapters, format_transcript_with_timestamps

def format_raw_data(video_info: dict, chapters: list, transcript: list) -> str:
    """格式化原始数据输出"""
    output = []
    
    # 添加视频标题
    output.append("# 视频信息")
    output.append("\n## 视频标题")
    output.append("-" * 50)
    output.append(video_info["title"])
    
    # 添加视频描述
    output.append("\n## 视频描述")
    output.append("-" * 50)
    output.append(video_info["description"])
    
    # 添加章节信息和对应时间段的文本
    output.append("\n## 章节时间轴")
    output.append("-" * 50)
    for chapter in chapters:
        timestamp = f"{chapter['start_time']//60:02d}:{chapter['start_time']%60:02d}"
        output.append(f"{timestamp} - {chapter['title']}")
    
    # 添加完整的带时间戳文本
    output.append("\n## 完整字幕文本")
    output.append("-" * 50)
    output.append(format_transcript_with_timestamps(transcript))
    
    return "\n".join(output)

def format_chapter_summaries(summaries: list) -> str:
    """格式化章节概括输出"""
    output = []
    
    output.append("# 视频内容概括")
    output.append("\n## 章节概括")
    
    # 检测并添加Part分段
    current_part = None
    for summary in summaries:
        # 检查是否是新的Part
        if "Part" in summary["title"] and ":" in summary["title"]:
            current_part = summary["title"].split(":")[0].strip()
            output.append(f"\n### {current_part}")
        elif current_part is None and summary == summaries[0]:
            output.append("\n### Part 1: Main Discussion")
        
        # 添加章节概括
        output.append(f"\n{summary['summary']}")
    
    return "\n".join(output)

def main():
    try:
        # 获取视频URL
        video_url = input("请输入YouTube视频URL: ")
        
        # 获取视频信息和字幕
        print("\n正在获取视频信息和字幕...")
        transcript, video_info = get_transcript(video_url)

        # 输出视频信息
        print(video_info)
        
        # 首先尝试从描述中解析章节
        print("\n正在从视频描述中解析章节...")
        chapters = parse_chapters_from_description(video_info["description"])
        
        if not chapters:
            print("未从描述中找到章节信息，尝试从网页获取...")
            chapters = get_youtube_chapters(video_url)
        
        if not chapters:
            print("错误：无法获取视频章节信息！")
            return
        
        # 输出原始数据
        raw_data = format_raw_data(video_info, chapters, transcript)
        print("\n【原始数据】")
        # 打印前十行
        # print(raw_data)
        print("\n".join(raw_data.splitlines()[:100]))
        
        # 处理章节并生成概括
        print("\n正在生成章节概括...")
        summaries = process_chapters(chapters, transcript)
        
        # 输出章节概括
        chapter_summaries = format_chapter_summaries(summaries)
        print("\n【章节概括】")
        print(chapter_summaries)
        
        # 保存结果到文件
        timestamp = f"{int(time.time())}"
        raw_data_file = f"raw_data_{timestamp}.md"
        summary_file = f"chapter_summary_{timestamp}.md"
        
        with open(raw_data_file, "w", encoding="utf-8") as f:
            f.write(raw_data)
        print(f"\n原始数据已保存到 {raw_data_file}")
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(chapter_summaries)
        print(f"章节概括已保存到 {summary_file}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 