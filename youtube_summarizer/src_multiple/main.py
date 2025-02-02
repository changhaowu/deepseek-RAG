import sys
import os

# 添加父目录到系统路径以导入原有模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transcript_extractor import get_transcript

from chapter_extractor import get_youtube_chapters, parse_chapters_from_description
from text_processor import process_chapters

def format_final_output(summaries: list) -> str:
    """格式化最终输出"""
    output = []
    
    # 添加Part 1, Part 2等分段标记
    current_part = None
    for chapter in summaries:
        # 检查是否是新的Part
        if "Part" in chapter["title"] and ":" in chapter["title"]:
            current_part = chapter["title"].split(":")[0].strip()
            output.append(f"\n## {current_part}")
        elif current_part and chapter == summaries[0]:
            output.append("\n## Part 1: Main Discussion")
            
        # 添加章节标题和概括
        output.append(f"\n### {chapter['timestamp']} - {chapter['title']}")
        output.append(chapter['summary'])
    
    return "\n\n".join(output)

def main():
    try:
        # 获取视频URL
        video_url = input("请输入YouTube视频URL: ")
        
        # 获取视频信息和字幕
        print("\n正在获取视频信息和字幕...")
        transcript, video_info = get_transcript(video_url)
        
        # 首先尝试从描述中解析章节
        print("\n正在从视频描述中解析章节...")
        chapters = parse_chapters_from_description(video_info["description"])
        
        if not chapters:
            print("未从描述中找到章节信息，尝试从网页获取...")
            chapters = get_youtube_chapters(video_url)
        
        if not chapters:
            print("错误：无法获取视频章节信息！")
            return
        
        print(f"\n找到 {len(chapters)} 个章节:")
        for chapter in chapters:
            print(f"{chapter['start_time']//60:02d}:{chapter['start_time']%60:02d} - {chapter['title']}")
        
        # 处理每个章节并生成概括
        summaries = process_chapters(chapters, transcript)
        
        # 格式化并输出结果
        print("\n【最终生成的章节概括】")
        print("-" * 50)
        final_output = format_final_output(summaries)
        print(final_output)
        
        # 保存结果到文件
        output_file = "chapter_summary.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {video_info['title']}\n\n")
            f.write(final_output)
        print(f"\n概括已保存到 {output_file}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 