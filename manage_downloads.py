import os
import json
import re
import subprocess
import sys
from utils import generate_short_name, run_ffmpeg, update_logs


def get_video_id_from_url(url):
    """Extracts the YouTube video ID from a URL."""
    match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None


def scan_directory(directory):
    """
    Scans the given directory for existing video files and partially downloaded files.

    Args:
        directory (str): The path to the directory to scan.

    Returns:
        tuple: A tuple containing three lists:
            - existing_files (list): A list of existing video file basenames (without extensions).
            - files_to_delete (list): A list of partially downloaded files to be deleted.
            - files_to_download (list): A list of YouTube URLs to be re-downloaded.
    """
    existing_files = set()
    files_to_delete = []
    files_to_download = []
    for filename in os.listdir(directory):
        if filename.endswith((".mp4", ".mkv", ".webm")):
            match = re.search(r"\[([a-zA-Z0-9_-]{5,20})\]", filename)
            if match:
                video_id = match.group(1)
                existing_files.add(video_id)
        elif filename.endswith((".part", ".ytdl")):
            base_filename = os.path.splitext(filename)[0]
            match = re.search(r"\[([a-zA-Z0-9_-]{5,20})\]", base_filename)
            if match:
                video_id = match.group(1)
                files_to_download.append(f"https://www.youtube.com/watch?v={video_id}")
                print("Partial download: ", video_id)
            else:
                files_to_delete.append(filename)
    return list(existing_files), files_to_delete, files_to_download


def download_video(url):
    """Downloads a video and returns its original filename."""
    command = ["yt-dlp", "-C", "-o", "%(title)s [%(id)s].%(ext)s", url]
    try:
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        original_filename = None
        for line in iter(proc.stdout.readline, ""):
            # yt-dlp uses carriage returns to create the progress bar effect.
            # We need to handle this to print on a single line.
            if line.startswith("[download]") and "%" in line:
                sys.stdout.write("\r" + line.strip())
                sys.stdout.flush()
            else:
                print(line.strip())

            if "[download] Destination:" in line:
                original_filename = line.split("Destination:")[1].strip()

        proc.wait()
        sys.stdout.write("\n")  # Move to the next line after download is complete

        if proc.returncode != 0:
            print(f"Error downloading {url}")
            return None

        if not original_filename:
            ls_proc = subprocess.run(["ls", "-t"], capture_output=True, text=True)
            if ls_proc.stdout:
                original_filename = ls_proc.stdout.split("\n")[0]

        return original_filename
    except Exception as e:
        print(f"An error occurred during download: {e}")
        return None


def main():
    """Main function to manage the download and processing of videos."""
    directory = "."
    to_download_file = "to_download.txt"
    logs_file = "logs.txt"

    try:
        with open(to_download_file, "r") as f:
            urls_or_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(
            f"{to_download_file} not found. Please create it with a list of video URLs or IDs."
        )
        return

    # Convert IDs to URLs
    urls_to_download = []
    for item in urls_or_ids:
        if "/" in item or ":" in item or "." in item:
            urls_to_download.append(item)
        elif 5 <= len(item) <= 20 and re.match(r"^[a-zA-Z0-9_-]+$", item):
            urls_to_download.append(f"https://www.youtube.com/watch?v={item}")
        else:
            print(f"Warning: Skipping invalid line in {to_download_file}: {item}")

    urls_to_download = list(set(urls_to_download))

    existing_video_ids, files_to_delete, partial_downloads_to_redownload = (
        scan_directory(directory)
    )

    processed_urls = set()
    if os.path.exists(logs_file):
        with open(logs_file, "r") as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    processed_urls.add(log_entry["original_url"])
                except (json.JSONDecodeError, KeyError):
                    processed_urls.add(line.strip())

    urls_to_process = []
    excluded_items = []
    for url in urls_to_download:
        video_id = get_video_id_from_url(url)
        in_logs = url in processed_urls
        in_dir = video_id in existing_video_ids if video_id else False

        if in_logs or in_dir:
            reason = []
            if in_logs:
                reason.append(f"found in {logs_file}")
            if in_dir:
                reason.append(f"found in directory")
            excluded_items.append(f"- {url} (excluded because: {'; '.join(reason)})")
        else:
            urls_to_process.append(url)

    urls_to_process.extend(partial_downloads_to_redownload)
    urls_to_process = list(set(urls_to_process))

    print(f"Found {len(urls_to_download)} unique URLs/IDs in {to_download_file}.")
    if excluded_items:
        print("\nExcluding the following already downloaded items:")
        for item in excluded_items:
            print(item)

    if files_to_delete:
        print("\n--- Files to be deleted ---")
        for filename in files_to_delete:
            print(filename)

    print(f"\nWill process {len(urls_to_process)} new videos.")
    if urls_to_process:
        print("URLs to be processed:")
        for url in urls_to_process:
            print(f"- {url}")

    if not urls_to_process and not files_to_delete:
        print("Nothing to do.")
        return

    try:
        confirm = input("Continue with download and/or deletion? (y/n): ")
    except EOFError:
        confirm = "n"

    if confirm.lower() != "y":
        print("Aborting.")
        return

    print("Now making the changes in .txt files and deleting files")
    with open(to_download_file, "w") as f:
        f.write("\n".join(urls_to_download))

    if os.path.exists(logs_file):
        os.remove(logs_file)

    for filename in files_to_delete:
        try:
            os.remove(os.path.join(directory, filename))
            print(f"Removed incomplete download: {filename}")
        except OSError as e:
            print(f"Error removing file {filename}: {e}")

    for url in urls_to_process:
        print(f"\n--- Processing: {url} ---")

        original_filename = download_video(url)
        if not original_filename:
            continue

        title = os.path.splitext(original_filename)[0]
        new_name = generate_short_name(title)

        if run_ffmpeg(original_filename, new_name):
            log_info = {
                "original_url": url,
                "original_filename": original_filename,
                "new_filename": new_name,
                "title": title,
            }
            update_logs(json.dumps(log_info))

            try:
                os.remove(original_filename)
                print(f"Removed original file: {original_filename}")
            except OSError as e:
                print(f"Error removing original file {original_filename}: {e}")


if __name__ == "__main__":
    main()
