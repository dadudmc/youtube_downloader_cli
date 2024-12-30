import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import os


# Convert time from format "00:01" to seconds
def time_to_seconds(time_str):
    if time_str == "0":
        return 0
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds


# Get start and end time input
def get_time_range():
    start_time = input("Enter start time (format: MM:SS or '0' for beginning): ")
    end_time = input("Enter end time (format: MM:SS or '0' for full length): ")
    return time_to_seconds(start_time), time_to_seconds(end_time)


# Function to check if 4K is available
def is_4k_available(link):
    ydl_opts = {
        'listformats': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        formats = info_dict.get('formats', [])
        for f in formats:
            if f.get('height') == 2160:  # 2160p = 4K
                return True
    return False


# Function to download video/audio
def download_youtube(link, start_time, end_time, download_type, quality=None):
    # Get user's desktop path
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(desktop_path, 'video.mp4') if download_type == 'v' else os.path.join(desktop_path,
                                                                                                     'audio.mp4'),
    }

    if download_type == 'a':
        ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'

    # Adjust for quality (4K or 1080p) if applicable
    if quality == 'h':
        ydl_opts['format'] = 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]'
    elif quality == 'l':
        ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]'

    # Download video/audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    # Handle video or audio processing after download
    if download_type == 'v':
        clip = VideoFileClip(os.path.join(desktop_path, 'video.mp4'))
        if start_time or end_time:
            clip = clip.subclipped(start_time, end_time if end_time > 0 else clip.duration)
        output_video_path = os.path.join(desktop_path, 'output_video.mp4')
        clip.write_videofile(output_video_path, codec='libx264')
        clip.close()
        os.remove(os.path.join(desktop_path, 'video.mp4'))
        print(f"Video downloaded as '{output_video_path}'.")

    elif download_type == 'a':
        clip = AudioFileClip(os.path.join(desktop_path, 'audio.mp4'))
        if start_time or end_time:
            clip = clip.subclipped(start_time, end_time if end_time > 0 else clip.duration)
        output_audio_path = os.path.join(desktop_path, 'output_audio.mp3')
        clip.write_audiofile(output_audio_path)
        clip.close()
        os.remove(os.path.join(desktop_path, 'audio.mp4'))
        print(f"Audio downloaded as '{output_audio_path}'.")


# Main execution
def main():
    link = input("Enter the YouTube link: ")
    start_time, end_time = get_time_range()

    download_type = input("Do you want the video (v) or audio (a)? ").lower()

    quality = None  # Default, no quality setting unless required

    # Check for quality selection if downloading video
    if download_type == 'v':
        if is_4k_available(link):
            quality = input("4K is available. Do you want 1080p (l) or 4K (h)? ").lower()
        else:
            print("4K not available. Downloading in the highest quality available.")
            quality = 'l'  # Default to 1080p or best available if no 4K

    download_youtube(link, start_time, end_time, download_type, quality)


if __name__ == "__main__":
    main()