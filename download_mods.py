import json
import os
import time
import urllib.request
import urllib.error

MANIFEST_FILE = 'manifest.json'
MODS_DIR = 'mods'

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
    
    print(f"Found {len(dependencies)} dependencies. Checking installation status...\n")

    for dep in dependencies:
        parts = dep.split('-')
        if len(parts) != 3:
            continue

        namespace, name, version = parts
        
        # MM Recomp reads zips directly, so we just save the zip
        zip_filename = f"{dep}.zip"
        zip_filepath = os.path.join(MODS_DIR, zip_filename)
        
        # Check if already installed
        if os.path.exists(zip_filepath):
            print(f"[{name}] is already downloaded. Skipping.")
            continue

        url = f"https://thunderstore.io/package/download/{namespace}/{name}/{version}/"
        print(f"Downloading: {name} (v{version})...")

        try:
            # Using built-in urllib so users don't need to install anything
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_filepath, 'wb') as out_file:
                out_file.write(response.read())
            
        except urllib.error.URLError as e:
            print(f"  -> Network error for {name}: {e}")
            
        # Polite API pacing
        time.sleep(0.5)

    print("\nDownload complete! All mod zip files are ready in the 'mods' folder.")

if __name__ == "__main__":
    install_dependencies()