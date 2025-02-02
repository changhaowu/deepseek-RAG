# YouTube Transcript Extractor

A Python tool to extract and format transcripts from YouTube videos.

## Features

- Extract transcripts from YouTube videos using video URL
- Support for various YouTube URL formats (standard watch URLs, shorts, embedded videos)
- Format transcripts with timestamps
- Save transcripts to text file

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
cd src
python main.py
```

The script will:
1. Prompt you for a YouTube video URL
2. Extract the transcript
3. Display the formatted transcript
4. Save the transcript to a text file

## Example Output Format

The transcript will be formatted as:
```
[00:00] First line of transcript
[00:05] Second line of transcript
...
```

## Error Handling

The script handles various error cases:
- Invalid YouTube URLs
- Videos without available transcripts
- Network connection issues

## Project Structure

```
youtube_summarizer/
├── requirements.txt
├── src/
│   ├── transcript_extractor.py
│   └── main.py
└── README.md
``` 