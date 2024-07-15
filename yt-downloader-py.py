import os
import subprocess
import requests

def check_youtube_dl():
    youtube_dl_path = "/usr/local/bin/youtube-dl"
    youtube_dl_symlink = "/usr/bin/youtube-dl"
    
    if not os.path.exists(youtube_dl_path):
        print("youtube-dl tidak ditemukan. Mendownload youtube-dl...")
        response = requests.get("https://yt-dl.org/downloads/latest/youtube-dl")
        with open(youtube_dl_path, "wb") as file:
            file.write(response.content)
        os.chmod(youtube_dl_path, 0o755)
        print("youtube-dl berhasil di-download dan diinstal.")

    if not os.path.exists(youtube_dl_symlink):
        os.symlink(youtube_dl_path, youtube_dl_symlink)
        print(f"Symbolic link untuk youtube-dl dibuat di {youtube_dl_symlink}")
    else:
        print("Symbolic link untuk youtube-dl sudah ada.")

def validate_download_folder():
    download_folder = os.path.expanduser("~/downloaded-yt-video")
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Folder {download_folder} telah dibuat.")
    else:
        print(f"Folder {download_folder} sudah tersedia.")

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
    
    valid_urls = []
    for url in urls:
        video_id = url.split("v=")[-1]
        video_path = os.path.expanduser(f"~/downloaded-yt-video/{video_id}.mp4")
        
        if os.path.exists(video_path):
            print(f"Video {url} sudah di-download sebelumnya. Menghapus dari daftar.")
            continue
        
        try:
            result = subprocess.run(["youtube-dl", "--get-title", url], capture_output=True, text=True)
            if result.returncode == 0:
                valid_urls.append(url)
            else:
                print(f"URL tidak valid: {url}. Menghapus dari daftar.")
        except subprocess.CalledProcessError as e:
            print(f"Error memeriksa URL: {url}. Pesan error: {e}")
    
    if not valid_urls:
        print("Tidak ada URL valid yang ditemukan di download-list.txt.")
        return False
    
    with open(download_list_path, "w") as file:
        file.write("\n".join(valid_urls))
    
    return True

def batch_download_videos():
    download_folder = os.path.expanduser("~/downloaded-yt-video")
    download_list_path = os.path.expanduser("~/download-list.txt")
    
    command = [
        "youtube-dl",
        "-f", "bestvideo[height<=720]+bestaudio/best",
        "--merge-output-format", "mp4",
        "-a", download_list_path,
        "-o", os.path.join(download_folder, "%(title)s.%(ext)s")
    ]
    
    subprocess.run(command)

if __name__ == "__main__":
    check_youtube_dl()
    validate_download_folder()
    
    if validate_download_list():
        batch_download_videos()
    else:
        print("Proses download dihentikan karena tidak ada URL valid di download-list.txt.")
