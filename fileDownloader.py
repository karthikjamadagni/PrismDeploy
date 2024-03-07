import os
import sqlite3

import requests
from bs4 import BeautifulSoup
import wget
import zipfile
from urllib.parse import urljoin
import subprocess
import re

database_path = "ie_info.db"
# conn = sqlite3.connect(database_path)
# cursor = conn.cursor()
# cursor.execute('''CREATE TABLE IF NOT EXISTS version_info (
#                             id INTEGER PRIMARY KEY AUTOINCREMENT,
#                             ver TEXT
#                          )''')
# conn.commit()

# URL of the HTML page
url = 'https://www.3gpp.org/ftp/Specs/archive/38_series/38.331/'

# Directory to save downloaded files
download_dir = '3gpp_specs'

# File to store downloaded filenames
downloaded_files_file = 'downloaded_files.txt'
# print("folder creating")

# Create the download directory if it doesn't exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
# print("folder created")
# Set to store downloaded filenames
downloaded_files = set()

# Read existing downloaded filenames from the file
if os.path.exists(downloaded_files_file):
    with open(downloaded_files_file, 'r') as file:
        downloaded_files = set(file.read().splitlines())

# Fetch the HTML content of the page
response = requests.get(url)
html_content = response.text

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the link to the specific zip file
zip_links = soup.find_all('a', href=lambda href: href and href.startswith('https://www.3gpp.org/ftp/Specs/archive/38_series/38.331/38331-h'))
count=0
for zip_link in zip_links:
    # print(zip_link.text)
    parts = re.split(r'(\d+-|[^\d-]+)', zip_link.text)
    before = parts[4][:-1]
    after = parts[4][-1]
    parts[3]=ord(parts[3].lower()) - ord('a') + 10
    new_filename=parts[1]+str(parts[3])+"."+str(parts[4])
    # print(new_filename)
    version=str(parts[3])+"."+str(before)+"."+str(after)
    if count<5:
        zip_url = urljoin(url, zip_link['href'])
        zip_filename = os.path.join(download_dir, os.path.basename(zip_url))

        # Check if the file has already been downloaded
        if zip_filename not in downloaded_files:
            print(f"Downloading {zip_url} ...")
            wget.download(zip_url, zip_filename)
            print(f"\nDownloaded {zip_filename}")

            # Extract files from the downloaded zip file
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
                print(f"Extracted files from {zip_filename}")

                # Add the filename to the set of downloaded files
                downloaded_files.add(zip_filename)

                # Write the updated downloaded filenames to the file
                with open(downloaded_files_file, 'a') as file:
                    file.write(f"{zip_filename}\n")
                docx_filename = zip_filename.replace("zip", "docx")
                docx_filename = docx_filename.replace("\\", "\\\\")
                # print(version)
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS version_info (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            ver TEXT
                                         )''')
                conn.commit()
                cursor.execute("INSERT INTO version_info (ver) VALUES (?)", (version, ))
                conn.commit()
                conn.close()
                subprocess.run(["python", "textExtraction.py", docx_filename, version], check=True)

                # Delete the downloaded file
                zip_ref.close()
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)
                    print(f"Zip file {zip_filename} deleted successfully")
                    # os.remove(docx_filename)
                    # print(f"File {docx_filename} deleted successfully")
                else:
                    print(f"File {zip_filename} does not exist")
        else:
            print(f"File {zip_filename} already exists, skipping download.")
            docx_filename = zip_filename.replace("zip", "docx")
            # print(version)
            # subprocess.run(["python", "textExtraction.py", docx_filename, version])
        count+=1

print("Process completed successfully.")
# conn.close()

