import json
import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

CHANNEL_URL = "https://www.youtube.com/channel/UC6t0ees15Lp0gyrLrAyLeJQ/videos"
DATA_DIR = "d:/개발/pregnancy_knowledge_system/data"
OUTPUT_FILE = os.path.join(DATA_DIR, "videos.json")

def get_channel_videos(channel_url):
    ydl_opts = {
        'extract_flat': True,
        'dump_single_json': True,
        'quiet': True,
        'ignore_errors': True
    }
    
    print(f"Fetching video list from {channel_url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        
    if 'entries' in result:
        return result['entries']
    return []


# Instantiate API
yt_api = YouTubeTranscriptApi()

def get_transcript(video_id):
    try:
        transcript = yt_api.fetch(video_id, languages=['ko'])
        return transcript.to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"No Korean transcript for {video_id}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    videos = get_channel_videos(CHANNEL_URL)
    print(f"Found {len(videos)} videos.")
    
    extracted_data = []
    
    # Process only the first 20 videos for initial testing/speed
    # Remove the slice [:20] to process all videos later
    for i, video in enumerate(videos[:20]):
        video_id = video['id']
        title = video['title']
        print(f"[{i+1}/{len(videos[:20])}] Processing: {title} ({video_id})")
        # specific debugging
        # print(video) 
        
        if 'url' in video:
            url = video['url']
        else:
            url = f"https://www.youtube.com/watch?v={video_id}"

        
        transcript = get_transcript(video_id)
        
        if transcript:
            extracted_data.append({
                'id': video_id,
                'title': title,
                'url': url,
                'transcript': transcript
            })
    
    print(f"Successfully extracted data for {len(extracted_data)} videos.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
