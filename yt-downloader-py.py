import os
import subprocess
import requests
import argparse

def check_dependency(command, install_command):
    """Check if a dependency is installed, and install it if it is not."""
    try:
        subprocess.run([command, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"{command} sudah terinstal.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{command} tidak ditemukan. Menginstal {command}...")
        subprocess.run(install_command, check=True)
        print(f"{command} berhasil diinstal.")

def check_yt_dlp():
    yt_dlp_path = "/usr/local/bin/yt-dlp"
    yt_dlp_symlink = "/usr/bin/yt-dlp"
    
    if not os.path.exists(yt_dlp_path):
        print("yt-dlp tidak ditemukan. Mendownload yt-dlp...")
        try:
            response = requests.get("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp", stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # ukuran blok untuk mengunduh
            with open("/tmp/yt-dlp", "wb") as file:
                for data in response.iter_content(block_size):
                    file.write(data)
            print("yt-dlp berhasil di-download.")
            subprocess.run(["sudo", "mv", "/tmp/yt-dlp", yt_dlp_path])
            subprocess.run(["sudo", "chmod", "a+rx", yt_dlp_path])
            print("yt-dlp berhasil diinstal.")
        except requests.RequestException as e:
            print(f"Error saat mendownload yt-dlp: {e}")
            return False

    if not os.path.exists(yt_dlp_symlink):
        subprocess.run(["sudo", "ln", "-s", yt_dlp_path, yt_dlp_symlink])
        print(f"Symbolic link untuk yt-dlp dibuat di {yt_dlp_symlink}")
    else:
        print("Symbolic link untuk yt-dlp sudah ada.")
    
    return True

def validate_download_folder():
    download_folder = os.path.expanduser("~/downloaded-yt-video")
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Folder {download_folder} telah dibuat.")
    else:
        print(f"Folder {download_folder} sudah tersedia.")

def clean_url(url):
    # Memisahkan URL pada parameter tambahan dan hanya menggunakan bagian pertama
    return url.split('&')[0]

def fix_url_format(urls):
    return [clean_url(url) for url in urls]

def validate_download_list():
    download_list_path = os.path.expanduser("~/download-list.txt")
    
    if not os.path.exists(download_list_path):
        print("File download-list.txt tidak ditemukan. Buat file dan isi dengan URL video yang ingin di-download.")
        return False
    
    with open(download_list_path, "r") as file:
        urls = file.readlines()
    
    urls = [url.strip() for url in urls if url.strip()]
    
    if not urls:
        print("Daftar URL di download-list.txt kosong. Tambahkan URL video yang ingin di-download.")
        return False
    
    # Memperbaiki format URL sebelum validasi
    fixed_urls = fix_url_format(urls)
    
    valid_urls = []
    for url in fixed_urls:
        video_id = url.split("v=")[-1]
        video_path = os.path.expanduser(f"~/downloaded-yt-video/{video_id}.mp4")
        
        if os.path.exists(video_path):
            print(f"Video {url} sudah di-download sebelumnya. Menghapus dari daftar.")
            continue
        
        try:
            result = subprocess.run(["yt-dlp", "--get-title", url], capture_output=True, text=True)
            if result.returncode == 0:
                valid_urls.append(url)  # Gunakan URL asli untuk mengunduh
            else:
                print(f"URL tidak valid: {url}. Menghapus dari daftar.")
        except subprocess.CalledProcessError as e:
            print(f"Error memeriksa URL: {url}. Pesan error: {e}")
    
    if not valid_urls:
        print("Tidak ada URL valid yang ditemukan di download-list.txt.")
        return False
    
    # Memperbarui file download-list.txt dengan URL yang telah diperbaiki
    with open(download_list_path, "w") as file:
        file.write("\n".join(valid_urls))
    
    return True

def batch_download_videos(video_quality):
    download_folder = os.path.expanduser("~/downloaded-yt-video")
    download_list_path = os.path.expanduser("~/download-list.txt")

    quality_map = {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
        "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
        "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]"
    }
    
    format_option = quality_map.get(video_quality, quality_map["best"])

    command = [
        "yt-dlp",
        "-f", format_option,
        "--merge-output-format", "mp4",
        "-a", download_list_path,
        "-o", os.path.join(download_folder, f"%(title)s.%(ext)s")
    ]
    
    subprocess.run(command)

    # Rename the merged files with quality information
    for root, _, files in os.walk(download_folder):
        for file in files:
            if file.endswith(".mp4"):
                base, ext = os.path.splitext(file)
                new_name = f"{base}_{video_quality}{ext}"
                os.rename(os.path.join(root, file), os.path.join(root, new_name))

def usage():
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
  This script downloads YouTube videos based on a list of URLs provided in the ~/download-list.txt file.
  The videos will be downloaded to the ~/downloaded-yt-video directory.
  If the required dependencies (yt-dlp and ffmpeg) are not installed, the script will install them automatically.
  The downloaded videos will be saved in MP4 format with the specified quality.

Note:
  Ensure that the URLs in ~/download-list.txt are valid YouTube video URLs.
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

    check_dependency("ffmpeg", ["sudo", "apt", "install", "-y", "ffmpeg"])
    if check_yt_dlp():
        validate_download_folder()
        
        if validate_download_list():
            batch_download_videos(args.quality)
        else:
            print("Proses download dihentikan karena tidak ada URL valid di download-list.txt.")
