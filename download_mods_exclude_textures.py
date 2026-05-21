import json
import os
import time
import urllib.request
import urllib.error

MANIFEST_FILE = 'manifest.json'
MODS_DIR = 'mods'
# The unique identifier for Nerrel's texture pack to exclude
EXCLUDED_MOD = 'Nerrel-MMN64HD'

def get_latest_version(namespace, name):
    # Endpoint to get package metadata from Thunderstore
    api_url = f"https://thunderstore.io/api/experimental/package/{namespace}/{name}/"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('latest', {}).get('version_number')
    except Exception as e:
        print(f"  -> API error fetching latest version for {name}: {e}")
        return None

def install_dependencies():
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

    os.makedirs(MODS_DIR, exist_ok=True)
    
    # Filter out the excluded mod pack early to get an accurate count
    active_dependencies = [dep for dep in dependencies if not dep.startswith(EXCLUDED_MOD)]
    
    print(f"Found {len(active_dependencies)} dependencies (excluding Nerrel's HD Pack). Fetching latest versions...\n")

    for dep in active_dependencies:
        parts = dep.split('-')
        if len(parts) != 3:
            continue

        namespace, name, original_version = parts
        print(f"Checking {name}...")
        
        # 1. Ask the API for the newest version
        latest_version = get_latest_version(namespace, name)
        
        # 2. Decide which version to use (fallback to manifest if API fails)
        version_to_use = latest_version if latest_version else original_version
        
        if latest_version and latest_version != original_version:
            print(f"  -> Found newer version: v{latest_version} (Manifest was v{original_version})")
            
        zip_filename = f"{namespace}-{name}-{version_to_use}.zip"
        zip_filepath = os.path.join(MODS_DIR, zip_filename)
        
        # 3. Check if already downloaded
        if os.path.exists(zip_filepath):
            print(f"  -> Already downloaded. Skipping.")
            time.sleep(0.5) 
            continue

        url = f"https://thunderstore.io/package/download/{namespace}/{name}/{version_to_use}/"
        print(f"  -> Downloading v{version_to_use}...")

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_filepath, 'wb') as out_file:
                out_file.write(response.read())
            
        except urllib.error.URLError as e:
            print(f"  -> Network error for {name}: {e}")
            
        # Polite API pacing
        time.sleep(0.5)

    print("\nDownload complete! All mod zip files (minus Nerrel's HD Pack) are ready in the 'mods' folder.")

if __name__ == "__main__":
    install_dependencies()