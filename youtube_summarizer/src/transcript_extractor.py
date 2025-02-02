from typing import List, Dict, Union
from youtube_transcript_api import YouTubeTranscriptApi
import re

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
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Could not extract video ID from URL. Please check if the URL is valid.")

def get_transcript(video_url: str) -> List[Dict[str, Union[str, float]]]:
    """
    Get transcript for a YouTube video.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        List[Dict[str, Union[str, float]]]: List of transcript segments with text, start time, and duration
        
    Raises:
        Exception: If transcript cannot be retrieved
    """
    try:
        video_id = extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        raise Exception(f"Failed to get transcript: {str(e)}")

def format_transcript(transcript: List[Dict[str, Union[str, float]]]) -> str:
    """
    Format transcript segments into a readable text document.
    
    Args:
        transcript (List[Dict[str, Union[str, float]]]): List of transcript segments
        
    Returns:
        str: Formatted transcript text
    """
    formatted_text = []
    for segment in transcript:
        # Convert start time to minutes:seconds format
        minutes = int(segment['start'] // 60)
        seconds = int(segment['start'] % 60)
        time_str = f"[{minutes:02d}:{seconds:02d}]"
        
        # Add formatted line
        formatted_text.append(f"{time_str} {segment['text']}")
    
    return "\n".join(formatted_text) 