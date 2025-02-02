import requests
from youtube_transcript_api import YouTubeTranscriptApi
from transcript_extractor import get_transcript, format_transcript
from youtube_transcript_api.formatters import TextFormatter, PrettyPrintFormatter

def extract_structure_from_description(title: str, description: str) -> str:
    """从视频标题和描述中提取结构化大纲"""
    prompt = (
        f"视频标题：{title}\n\n"
        f"视频描述：\n{description}\n\n"
        "请从上述视频标题和描述中提取一个结构化的大纲框架。要求：\n"
        "1. 如果描述中包含时间戳信息（如 0:00, 1:02 等），请保留完整的时间戳结构；\n"
        "2. 如果描述中包含 Part 1, Part 2 等分段信息，请保持这种分段结构；\n"
        "3. 提取所有关键主题和子主题；\n"
        "4. 保持原有的层次结构和顺序；\n"
        "5. 输出格式要清晰，使用适当的缩进和编号。\n"
    )
    
    try:
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
        print(f"Warning: Failed to extract structure: {str(e)}")
        return ""

def generate_detailed_summary(structure: str, transcript: str) -> str:
    """根据提取的结构和文字稿生成详细的概括"""
    prompt = (
        "请根据以下大纲结构和视频文字稿，生成一份详细的中文概括。\n\n"
        f"大纲结构：\n{structure}\n\n"
        f"视频文字稿：\n{transcript}\n\n"
        "要求：\n"
        "1. 严格按照提供的大纲结构组织内容；\n"
        "2. 对每个主题，从文字稿中提取相关内容并进行概括；\n"
        "3. 保持内容的完整性和连贯性；\n"
        "4. 使用清晰、专业的中文表述；\n"
        "5. 突出重要的数据和关键观点。\n"
    )
    
    try:
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
        print(f"Warning: Failed to generate detailed summary: {str(e)}")
        return ""

def main():
    try:
        # 获取 YouTube 视频 URL 或 ID
        video_url_or_id = input("Enter the YouTube video URL or ID: ")
        
        # 获取 transcript 和视频信息
        print("Fetching transcript and video info from YouTube...")
        transcript, video_info = get_transcript(video_url_or_id)
        formatted_text = format_transcript(transcript)

        print("\n视频文字稿：")
        print("-" * 50)
        print(formatted_text)
        
        print("\n视频标题：")
        print("-" * 50)
        print(video_info["title"])

        print("\n视频描述：")
        print("-" * 50)
        print(video_info["description"])
        
        # 第一步：提取结构
        print("\n正在从描述中提取结构框架...")
        structure = extract_structure_from_description(
            video_info["title"], 
            video_info["description"]
        )
        
        print("\n【提取的结构框架】")
        print("-" * 50)
        print(structure)
        
        # 第二步：生成详细概括
        print("\n正在生成详细概括...")
        detailed_summary = generate_detailed_summary(structure, formatted_text)
        
        print("\n【最终生成的概括】")
        print("-" * 50)
        print(detailed_summary)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
