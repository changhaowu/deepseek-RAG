from transcript_extractor import get_transcript, format_transcript

def main():
    # Example usage
    try:
        # Get video URL from user
        video_url = input("Please enter the YouTube video URL: ")
        
        # Get transcript
        print("Fetching transcript...")
        transcript = get_transcript(video_url)
        
        # Format transcript
        formatted_text = format_transcript(transcript)
        
        # Print the formatted transcript
        print("\nTranscript:")
        print("-" * 50)
        print(formatted_text)
        
        # Optionally save to file
        output_file = "transcript.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_text)
        print(f"\nTranscript saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 