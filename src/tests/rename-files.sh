#!/bin/bash

# Directory containing the files
DIR="/home/uikode/yt-downloader-py-data/downloaded-yt-video"

# Move to the directory
cd "$DIR" || exit

# Loop through each file that matches the pattern
for file in *_720p*.mp4; do
  # Remove all instances of '_720p' and then add back one instance
  new_file=$(echo "$file" | sed -e 's/_720p//g' -e 's/\.mp4/_720p.mp4/')
  
  # Rename the file
  mv "$file" "$new_file"
done
