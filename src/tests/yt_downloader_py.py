import os
import subprocess
import requests
import argparse

def check_dependency(command, install_command, version_arg="--version"):
    """
    Check if a program (dependency) is installed, and install it if it is not.

    Parameters:
    - command: The command to check for the program.
    - install_command: The command to install the program.
    - version_arg: The argument to check the program's version (default is "--version").
    """
    try:
        subprocess.run([command, version_arg], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"{command} is already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{command} is not found. Installing {command}...")
        subprocess.run(install_command, check=True)
        print(f"{command} is now installed.")

def check_yt_dlp():
    """
    Check if yt-dlp is installed, and download and install it if it is not.

    Returns:
    - True if yt-dlp is installed or successfully installed, False otherwise.
    """
    yt_dlp_path = "/usr/local/bin/yt-dlp"
    yt_dlp_symlink = "/usr/bin/yt-dlp"
    
    if not os.path.exists(yt_dlp_path):
        print("yt-dlp is not found. Downloading yt-dlp...")
        try:
            response = requests.get("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp", stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # block size for downloading
            with open("/tmp/yt-dlp", "wb") as file:
                for data in response.iter_content(block_size):
                    file.write(data)
            print("yt-dlp is downloaded.")
            subprocess.run(["sudo", "mv", "/tmp/yt-dlp", yt_dlp_path])
            subprocess.run(["sudo", "chmod", "a+rx", yt_dlp_path])
            print("yt-dlp is installed.")
        except requests.RequestException as e:
            print(f"Error downloading yt-dlp: {e}")
            return False

    if not os.path.exists(yt_dlp_symlink):
        subprocess.run(["sudo", "ln", "-s", yt_dlp_path, yt_dlp_symlink])
        print(f"Symbolic link for yt-dlp created at {yt_dlp_symlink}")
    else:
        print("Symbolic link for yt-dlp already exists.")
    
    return True

def validate_download_folder():
    """
    Check if the download folder exists, and create it if it does not.
    """
    data_folder = os.path.expanduser("~/yt-downloader-py-data")
    download_folder = os.path.join(data_folder, "downloaded-yt-video")
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Folder {download_folder} is created.")
    else:
        print(f"Folder {download_folder} already exists.")

def clean_url(url):
    """
    Clean the URL by removing extra parameters.

    Parameters:
    - url: The original URL.

    Returns:
    - The cleaned URL.
    """
    return url.split('&')[0]

def fix_url_format(urls):
    """
    Clean all URLs in a list.

    Parameters:
    - urls: The list of URLs.

    Returns:
    - A list of cleaned URLs.
    """
    return [clean_url(url) for url in urls]

def get_video_title(url):
    """
    Get the title of the video from its URL.

    Parameters:
    - url: The video URL.

    Returns:
    - The video title if successful, None otherwise.
    """
    try:
        result = subprocess.run(["yt-dlp", "--get-title", url], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error getting title for URL: {url}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error getting title for URL: {url}. Error message: {e}")
        return None

def validate_download_list(video_quality):
    """
    Check if the download list file exists and contains valid URLs. Remove URLs that are already downloaded.

    Parameters:
    - video_quality: The quality of the video to check for existing downloads.

    Returns:
    - A list of valid URLs to download.
    """
    data_folder = os.path.expanduser("~/yt-downloader-py-data")
    download_list_path = os.path.join(data_folder, "download-list.txt")
    download_folder = os.path.join(data_folder, "downloaded-yt-video")
    
    if not os.path.exists(download_list_path):
        print("File download-list.txt not found. Create the file and add the video URLs you want to download.")
        return []
    
    with open(download_list_path, "r") as file:
        urls = file.readlines()
    
    urls = [url.strip() for url in urls if url.strip()]
    
    if not urls:
        print("The URL list in download-list.txt is empty. Add the video URLs you want to download.")
        return []
    
    fixed_urls = fix_url_format(urls)
    
    valid_urls = []
    for url in fixed_urls:
        video_title = get_video_title(url)
        if video_title is None:
            print(f"Invalid URL: {url}. Removing from the list.")
            continue

        video_path = os.path.join(download_folder, f"{video_title}_{video_quality}.mp4")
        
        if os.path.exists(video_path):
            print(f"Video {url} with title {video_title} and quality {video_quality} is already downloaded. Removing from the list.")
            continue
        
        valid_urls.append(url)  # Use the original URL for downloading
    
    with open(download_list_path, "w") as file:
        file.write("\n".join(valid_urls))
    
    return valid_urls

def batch_download_videos(video_quality, urls):
    """
    Download and merge videos from the URLs in the download list.

    Parameters:
    - video_quality: The quality of the video to download.
    - urls: The list of URLs to download.
    """
    data_folder = os.path.expanduser("~/yt-downloader-py-data")
    download_folder = os.path.join(data_folder, "downloaded-yt-video")
    download_list_path = os.path.join(data_folder, "download-list.txt")

    quality_map = {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
        "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
        "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]"
    }
    
    format_option = quality_map.get(video_quality, quality_map["best"])

    for url in urls:
        command = [
            "yt-dlp",
            "-f", format_option,
            "--merge-output-format", "mp4",
            url,
            "-o", os.path.join(download_folder, f"%(title)s.%(ext)s")
        ]
        
        subprocess.run(command)

        # Rename files after download and merge
        for root, _, files in os.walk(download_folder):
            for file in files:
                if file.endswith(".mp4") and not file.endswith(f"_{video_quality}.mp4"):
                    base, ext = os.path.splitext(file)
                    new_name = f"{base}_{video_quality}{ext}"
                    os.rename(os.path.join(root, file), os.path.join(root, new_name))

        # Remove the processed URL from the download list
        with open(download_list_path, "r") as file:
            lines = file.readlines()
        with open(download_list_path, "w") as file:
            for line in lines:
                if line.strip() != url:
                    file.write(line)

def usage():
    """
    Display usage instructions and examples.
    """
    usage_text = """
Usage: python3 yt-downloader-py.py [options]

Options:
  -h, --help            Show this help message and exit
  -q, --quality         Video quality to download (choices: best, 1080p, 720p, 480p)
  
Examples:
  1. Download with default quality (best available):
     python3 yt-downloader-py.py
     
  2. Download with specified quality:
     python3 yt-downloader-py.py --quality 720p
     python3 yt-downloader-py.py -q 1080p
     
Description:
  This script downloads YouTube videos based on a list of URLs provided in the ~/yt-downloader-py-data/download-list.txt file.
  The videos will be downloaded to the ~/yt-downloader-py-data/downloaded-yt-video directory.
  If the required dependencies (yt-dlp and ffmpeg) are not installed, the script will install them automatically.
  The downloaded videos will be saved in MP4 format with the specified quality.

Note:
  Ensure that the URLs in ~/yt-downloader-py-data/download-list.txt are valid YouTube video URLs.
"""
    print(usage_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube videos with specified quality.", add_help=False)
    parser.add_argument("-q", "--quality", choices=["best", "1080p", "720p", "480p"], default="best", help="Video quality to download")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    args = parser.parse_args()

    if args.help:
        usage()
        exit()

    check_dependency("ffmpeg", ["sudo", "apt", "install", "-y", "ffmpeg"], version_arg="-version")
    if check_yt_dlp():
        validate_download_folder()
        
        urls_to_download = validate_download_list(args.quality)
        if urls_to_download:
            batch_download_videos(args.quality, urls_to_download)
        else:
            print("Download process stopped because no valid URLs found in download-list.txt.")
