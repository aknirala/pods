# A simple repository to manage YouTube downloads.

## Scenario

The user manually saves YouTube links or video IDs to a text file named `to_download.txt`. A Python script then processes this file to download and manage the videos. The process is designed to be resilient to download failures, allowing for retries on subsequent runs.

## Core Components

*   **`manage_downloads.py`**: The main script that orchestrates the download and processing workflow.
*   **`utils.py`**: A helper module containing functions for video processing, logging, and filename generation.
*   **`to_download.txt`**: A user-maintained list of YouTube video URLs or IDs. The script automatically converts IDs to URLs, removes duplicates, and updates the file.
*   **`logs.txt`**: A log file that records successfully downloaded and processed videos for the current session.

## Workflow

The process is initiated by running the `manage_downloads.py` script.

### 1. Initialization and Cleanup

1.  **Process `to_download.txt`**:
    *   The script reads `to_download.txt`.
    *   It converts any YouTube video IDs (e.g., `XIOKr51Q_hA`) into full URLs. The video ID can be between 5 and 20 characters long.
    *   It removes duplicate entries.
2.  **Scan for Existing and Partial Videos**:
    *   The script scans the current directory for video files that have a YouTube ID in their filename (e.g., `My Video [XIOKr51Q_hA].mp4`).
    *   It also scans for partially downloaded files (`.part` and `.ytdl` extensions).
        *   If a partial file has a recognizable YouTube ID, it's added to a list for re-downloading.
        *   If no ID is found, the file is marked for deletion.
    *   It also reads `logs.txt` from previous runs to identify already processed videos.
3.  **Exclusion and Reporting**:
    *   The script identifies which videos from the `to_download.txt` list have already been downloaded.
    *   It prints a detailed report of which videos are being excluded and why (found in `logs.txt`, found in the directory, or both).
    *   It then prints a clean list of all the new videos that will be downloaded, and a list of incomplete files that will be deleted.
4.  **User Confirmation**: The script will ask for user confirmation (y/n) before proceeding with the downloads and deletions. If the user does not enter 'y', the script will abort.
5.  **File Updates**: If the user confirms, the script will:
    *   Overwrite `to_download.txt` with the cleaned list of URLs.
    *   Delete `logs.txt` to prepare for the new session.
    *   Delete the incomplete files.

### 2. Download and Process Cycle

If the user confirms, the script enters a loop, processing one video at a time. This one-by-one processing provides a natural delay between downloads to help avoid IP blocking.

For each video:

1.  **Download**: The script downloads the video using `yt-dlp` with the `-C` flag to resume interrupted downloads. It names the file in the format `Video Title [VIDEO_ID].ext`. The downloaded filename is used as the video's title for further processing.
2.  **Process**: Upon successful download, the video is processed by functions in `utils.py`:
    *   **Generate Name**: A new, short, and unique filename is created from the original filename (e.g., `NewVideoName.mp4`).
    *   **Transcode with `ffmpeg`**: The video is downsized to a smaller resolution (e.g., 360p) to save space.
3.  **Log**: The successful download and processing are recorded in `logs.txt`.
4.  **Cleanup**: The original, larger downloaded file is deleted.
5.  **Next Video**: The script moves to the next video in the list.

### Helper Functions in `utils.py`

*   **Name Generation**: Contains the logic for creating short and unique video filenames from the original video title.
*   **`ffmpeg` Execution**: A dedicated function to run the `ffmpeg` command and wait for it to complete.
*   **Logging**: A function to handle writing new entries to `logs.txt`.
