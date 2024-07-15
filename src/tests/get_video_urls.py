import os
import subprocess
import argparse

def get_video_urls(channel_url):
    """
    Get all video URLs from a YouTube channel.

    Parameters:
    - channel_url: The URL of the YouTube channel's videos page.

    Returns:
    - A list of video URLs.
    """
    command = ["yt-dlp", "--get-id", channel_url]
    result = subprocess.run(command, capture_output=True, text=True)

    video_ids = result.stdout.strip().split("\n")
    video_urls = [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids]

    return video_urls

def write_urls_to_file(urls, file_path):
    """
    Write URLs to a specified file.

    Parameters:
    - urls: A list of URLs to write.
    - file_path: The path to the file where URLs will be written.
    """
    with open(file_path, "w") as file:
        for url in urls:
            file.write(f"{url}\n")
    print(f"URLs have been written to {file_path}")

def usage():
    """
    Display usage instructions and examples.
    """
    usage_text = """
Usage: python get_video_urls.py [options] <channel_url>

Options:
  -h, --help            Show this help message and exit
  
Examples:
  1. Get all video URLs from a YouTube channel and save to the default file:
     python get_video_urls.py "https://www.youtube.com/@LaelaKhanZa99/videos"
     
Description:
  This script fetches all video URLs from a specified YouTube channel and saves them to a file.
  The URLs will be written to the file located at ~/yt-downloader-py-data/download-list.txt.
  
Note:
  Ensure that the provided URL is a valid YouTube channel's videos page URL.
"""
    print(usage_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get all video URLs from a YouTube channel and save to a file.", add_help=False)
    parser.add_argument("channel_url", nargs='?', help="The URL of the YouTube channel's videos page.")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    args = parser.parse_args()

    if args.help or not args.channel_url:
        usage()
        exit()

    data_folder = os.path.expanduser("~/yt-downloader-py-data")
    os.makedirs(data_folder, exist_ok=True)
    file_path = os.path.join(data_folder, "download-list.txt")

    video_urls = get_video_urls(args.channel_url)
    write_urls_to_file(video_urls, file_path)
