from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print(f"File: {inspect.getfile(YouTubeTranscriptApi)}")
print(f"Dir: {dir(YouTubeTranscriptApi)}")

try:
    # Try list_transcripts
    print("Trying list_transcripts...")
    transcript_list = YouTubeTranscriptApi.list_transcripts("dQw4w9WgXcQ") # Rick Roll
    print("List transcripts success.")
    transcript = transcript_list.find_generated_transcript(['en'])
    print("Find transcript success.")
except Exception as e:
    print(f"Error: {e}")
