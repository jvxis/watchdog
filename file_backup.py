import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Define the files you want to monitor with their full paths
files_to_monitor = [
    "/root/bitcoin-rpc-service/subscriptions.db",
    "/home/webuser/brln-services/db.sqlite3",
    "/root/brln-bots/brln_ranking.db",
    "/root/brln-clearnet/clearnet_users.db",
    "/root/data/.super_user",
    "/root/data/database.sqlite3",
    "/root/data/ext_lndhub.sqlite3",
    "/root/data/ext_lnurlp.sqlite3",
    "/root/data/ext_tpos.sqlite3",
    # Add more files here
]

# Define the backup folder
backup_folder = "/brln_backup"
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)

# Configure logging
log_file = os.path.join(backup_folder, "backup_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

class FileBackupHandler(FileSystemEventHandler):
    def __init__(self, files):
        self.files = files

    def on_modified(self, event):
        if event.src_path in self.files:
            file_name = os.path.basename(event.src_path)
            # Get the current datetime and format it
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Append the timestamp to the file name
            backup_file_name = f"{file_name}_{timestamp}"
            backup_path = os.path.join(backup_folder, backup_file_name)
            # Copy the modified file to the backup path
            shutil.copy2(event.src_path, backup_path)
            logging.info(f"File {file_name} modified and backed up to {backup_path}")

def monitor_files():
    event_handler = FileBackupHandler(files_to_monitor)
    observer = Observer()

    # Start monitoring the directories containing the files
    directories = set([os.path.dirname(f) for f in files_to_monitor])
    for directory in directories:
        observer.schedule(event_handler, directory, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)  # Keeps the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    logging.info("Starting file monitoring and backup process...")
    monitor_files()
