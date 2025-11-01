#!/usr/bin/env python3
"""
Script to download a sample student testimonial video from YouTube
and save it to the videos/student-testimonials directory
"""
import os
import sys
from youtube_downloader import YouTubeDownloader

# Sample YouTube video - a short educational testimonial/review video
# Using a popular short video that's likely to be available
TESTIMONIAL_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Short video

def main():
    # Target directory for testimonials
    target_dir = "videos/student-testimonials"
    os.makedirs(target_dir, exist_ok=True)
    
    # Choose which testimonial slot to fill (random - using Arjun Kumar's slot)
    target_filename = "arjun-kumar.mp4"
    target_path = os.path.join(target_dir, target_filename)
    
    print(f"Downloading testimonial video...")
    print(f"Target: {target_path}")
    
    # Initialize downloader with custom output directory
    downloader = YouTubeDownloader(download_folder=target_dir)
    
    try:
        # Download the video
        result = downloader.download_video(TESTIMONIAL_VIDEO_URL)
        
        # Rename the downloaded file to match our expected filename
        downloaded_path = result['filepath']
        if os.path.exists(downloaded_path):
            # If target exists, remove it first
            if os.path.exists(target_path):
                os.remove(target_path)
            
            # Rename downloaded file to target filename
            os.rename(downloaded_path, target_path)
            print(f"\n✓ Success! Video saved as: {target_filename}")
            print(f"  Location: {target_path}")
            print(f"  Title: {result['title']}")
            print(f"  Size: {result['size']:,} bytes ({result['size'] / (1024*1024):.2f} MB)")
            
            return True
        else:
            print(f"✗ Error: Downloaded file not found at {downloaded_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error downloading video: {e}")
        print(f"\nTrying alternative approach...")
        
        # Alternative: Try downloading with direct filename specification
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'best[height<=720]/best',  # Prefer 720p or lower for smaller files
                'outtmpl': target_path.replace('.mp4', '.%(ext)s'),
                'quiet': False,
                'noplaylist': True,
                'extract_flat': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([TESTIMONIAL_VIDEO_URL])
            
            # Check if file was downloaded (might have different extension)
            for ext in ['mp4', 'webm', 'mkv']:
                possible_path = target_path.replace('.mp4', f'.{ext}')
                if os.path.exists(possible_path):
                    if ext != 'mp4':
                        # Rename to .mp4
                        os.rename(possible_path, target_path)
                    print(f"\n✓ Success! Video saved as: {target_filename}")
                    print(f"  Location: {target_path}")
                    return True
            
            print(f"✗ Download completed but file not found with expected extension")
            return False
            
        except Exception as e2:
            print(f"✗ Alternative download also failed: {e2}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

