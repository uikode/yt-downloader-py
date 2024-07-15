## YT Downloader Py

Welcome to **YT Downloader Py**, the ultimate Python tool for downloading and merging YouTube videos in the highest quality available. This project is designed to simplify the process of downloading videos from YouTube, providing options for various video qualities, and ensuring seamless merging of video and audio tracks using `yt-dlp` and `ffmpeg`.

### Features

- **High-Quality Downloads**: Choose from multiple video quality options including 1080p, 720p, 480p, or the best available quality.
- **Automatic Dependency Management**: Automatically checks and installs required dependencies (`yt-dlp` and `ffmpeg`).
- **Batch Downloading**: Easily download multiple videos at once from a list of URLs.
- **Customizable Output**: Automatically formats and names downloaded files with video quality in the filename.
- **User-Friendly CLI**: Simple and intuitive command-line interface for managing downloads.
- **Works on Ubuntu all version:** I build this tool on Ubuntu 20.04 WSL

### Usage

To get started with YT Downloader Py, follow the instructions below:

#### 1. Clone the Repository

```bash
git clone https://github.com/uikode/yt-downloader-py.git cd yt-downloader-py`
```

#### 2. Prepare Your Download List

Create a file named `download-list.txt` in your home directory and add the YouTube video URLs you want to download, each on a new line.

```bash
nano ~/download-list.txt # Add your URLs here
```

#### 3. Run the Script

You can run the script with the default quality (best available) or specify a desired quality:

- **Default Quality (Best Available)**

```bash
python3 yt-downloader-py.py
```

- **Specify Quality (1080p, 720p, 480p)**

```bash
python3 yt-downloader-py.py -q 720p
```

or

```bash
python3 yt-downloader-py.py --quality 1080p
```

#### 4. Check Your Downloads

Downloaded videos will be saved in the `~/downloaded-yt-video` directory with the specified quality in the filename.

### Dependencies

- **Python 3.8+**: Required for running the script.
- **yt-dlp**: Used for downloading YouTube videos.
- **ffmpeg**: Required for merging video and audio tracks.

The script will automatically install `yt-dlp` and `ffmpeg` if they are not already installed.

### Contribution

Feel free to contribute to this project by submitting issues or pull requests. Let's make YT Downloader Py even better together!

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
