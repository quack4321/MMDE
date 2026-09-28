import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import shutil
import ssl
import threading
import time
import urllib.error
import urllib.request

# Prevent SSL certificate verification crashes on outdated environments
ssl._create_default_https_context = ssl._create_unverified_context

MANIFEST_FILE = 'manifest.json'
MODS_DIR = 'mods'
EXCLUDED_MOD = 'Nerrel-MMN64HD'
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_WORKERS = 6  # Parallel download threads

# Lock to ensure API checks don't burst Thunderstore simultaneously
api_lock = threading.Lock()

def get_latest_version(namespace, name):
    api_url = f"https://thunderstore.io/api/experimental/package/{namespace}/{name}/"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with api_lock:
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode('utf-8'))
                # Small cooldown between serialized API calls to respect rate limits
                time.sleep(0.35)

            return data.get('latest', {}).get('version_number')

        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = attempt * 2
                print(f"[{name}] Rate limited (429). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[{name}] API HTTP error fetching version: {e}")
                break
        except Exception as e:
            print(f"[{name}] API error fetching version: {e}")
            break

    return None

def download_file_with_retry(url, dest_path, mod_name):
    """Downloads a file in chunks with automatic retry logic and cleanup."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response, open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file, length=64 * 1024)
            return True
        except (urllib.error.URLError, TimeoutError, ConnectionResetError) as e:
            print(f"[{mod_name}] Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    return False

def process_mod(dep):
    parts = dep.split('-')
    if len(parts) != 3:
        return None, True

    namespace, name, original_version = parts
    latest_version = get_latest_version(namespace, name)
    version = latest_version if latest_version else original_version

    zip_filename = f"{namespace}-{name}-{version}.zip"
    zip_filepath = os.path.join(MODS_DIR, zip_filename)

    if os.path.exists(zip_filepath):
        print(f"[{name}] Already downloaded. Skipping.")
        return name, True

    url = f"https://thunderstore.io/package/download/{namespace}/{name}/{version}/"
    print(f"[{name}] Downloading v{version}...")

    success = download_file_with_retry(url, zip_filepath, name)
    if success:
        print(f"[{name}] Done.")
    else:
        print(f"[{name}] FAILED.")
    return name, success

def install_dependencies(exclude_textures=False):
    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {MANIFEST_FILE}.")
        return

    dependencies = manifest.get('dependencies', [])
    if not dependencies:
        print("No dependencies found.")
        return

    if exclude_textures:
        dependencies = [dep for dep in dependencies if not dep.startswith(EXCLUDED_MOD)]
        print(f"Excluding texture pack ({EXCLUDED_MOD}).\n")

    os.makedirs(MODS_DIR, exist_ok=True)
    print(f"Processing {len(dependencies)} mods using {MAX_WORKERS} workers...\n")

    failed_downloads = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_mod, dep) for dep in dependencies]
        for future in as_completed(futures):
            mod_name, success = future.result()
            if not success and mod_name:
                failed_downloads.append(mod_name)

    if failed_downloads:
        print(f"\nDownload finished with errors. Failed mods: {', '.join(failed_downloads)}")
    else:
        print("\nDownload complete! All mod zip files are ready in the 'mods' folder.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download mods for Majora's Mask: Definitive Edition.")
    parser.add_argument(
        '-e', '--exclude-textures',
        action='store_true',
        help="Skip downloading Nerrel's HD texture pack"
    )
    args = parser.parse_args()
    install_dependencies(exclude_textures=args.exclude_textures)