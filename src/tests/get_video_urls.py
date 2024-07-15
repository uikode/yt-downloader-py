import os
import subprocess
import argparse

def get_video_urls(channel_url):
    """Get all video URLs from a YouTube channel."""
    command = ["yt-dlp", "--get-id", channel_url]
    result = subprocess.run(command, capture_output=True, text=True)

    video_ids = result.stdout.strip().split("\n")
    video_urls = [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids]

    return video_urls

def write_urls_to_file(urls, file_path):
    """Write URLs to a specified file."""
    with open(file_path, "w") as file:
        for url in urls:
            file.write(f"{url}\n")
    print(f"URLs have been written to {file_path}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Get all video URLs from a YouTube channel and save to a file.")
    parser.add_argument("channel_url", help="The URL of the YouTube channel's videos page.")
    args = parser.parse_args()

    # Define the file path
    data_folder = os.path.expanduser("~/yt-downloader-py-data")
    os.makedirs(data_folder, exist_ok=True)
    file_path = os.path.join(data_folder, "download-list.txt")

    # Get video URLs from the given channel
    video_urls = get_video_urls(args.channel_url)

    # Write the video URLs to the specified file
    write_urls_to_file(video_urls, file_path)
