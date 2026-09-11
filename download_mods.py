import argparse
import json
import os
import ssl
import time
import urllib.error
import urllib.request

# Prevent SSL certificate verification crashes on outdated user machines
ssl._create_default_https_context = ssl._create_unverified_context

MANIFEST_FILE = 'manifest.json'
MODS_DIR = 'mods'
EXCLUDED_MOD = 'Nerrel-MMN64HD'
MAX_RETRIES = 3
RETRY_DELAY = 2  # Base delay in seconds between retries

def get_latest_version(namespace, name):
    api_url = f"https://thunderstore.io/api/experimental/package/{namespace}/{name}/"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('latest', {}).get('version_number')
    except Exception as e:
        print(f"  -> API error fetching latest version for {name}: {e}")
        return None

def download_file_with_retry(url, dest_path, mod_name):
    """Downloads a file with automatic retry logic and cleans up partial files on failure."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response, open(dest_path, 'wb') as out_file:
                out_file.write(response.read())
            return True
        except (urllib.error.URLError, TimeoutError, ConnectionResetError) as e:
            print(f"  -> [Attempt {attempt}/{MAX_RETRIES}] Network error for {mod_name}: {e}")
            
            # Clean up partial/corrupted download
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass

            if attempt < MAX_RETRIES:
                sleep_time = RETRY_DELAY * attempt
                print(f"     Retrying in {sleep_time}s...")
                time.sleep(sleep_time)

    return False

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
    total = len(dependencies)
    print(f"Found {total} dependencies. Fetching latest versions...\n")

    failed_downloads = []

    for idx, dep in enumerate(dependencies, start=1):
        parts = dep.split('-')
        if len(parts) != 3:
            continue

        namespace, name, original_version = parts
        print(f"[{idx}/{total}] Checking {name}...")

        latest_version = get_latest_version(namespace, name)
        version_to_use = latest_version if latest_version else original_version

        if latest_version and latest_version != original_version:
            print(f"  -> Found newer version: v{latest_version} (Manifest was v{original_version})")

        zip_filename = f"{namespace}-{name}-{version_to_use}.zip"
        zip_filepath = os.path.join(MODS_DIR, zip_filename)

        if os.path.exists(zip_filepath):
            print("  -> Already downloaded. Skipping.")
            time.sleep(0.2)
            continue

        url = f"https://thunderstore.io/package/download/{namespace}/{name}/{version_to_use}/"
        print(f"  -> Downloading v{version_to_use}...")

        success = download_file_with_retry(url, zip_filepath, name)
        if not success:
            print(f"  -> [FAILED] Could not download {name} after {MAX_RETRIES} attempts.")
            failed_downloads.append(name)

        time.sleep(0.3)

    if failed_downloads:
        print(f"\nDownload finished with errors. The following mods failed: {', '.join(failed_downloads)}")
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
