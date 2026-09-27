import json
import os
import time
import urllib.error
import urllib.request
import zipfile

MANIFEST_FILE = 'manifest.json'
ZIP_FILENAME = 'MMDE.zip'
FILES_TO_ZIP = [
    'README.md',
    'manifest.json',
    'icon.png',
    'download_mods.py'
]

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

def update_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: Could not find {MANIFEST_FILE}.")
        return False

    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {MANIFEST_FILE} is not a valid JSON file.")
        return False

    dependencies = manifest.get('dependencies', [])
    if not dependencies:
        print("No dependencies found.")
        return False

    print(f"Checking {len(dependencies)} dependencies for updates...\n")
    
    updated_dependencies = []
    changes_made = 0

    for dep in dependencies:
        parts = dep.split('-')
        if len(parts) != 3:
            updated_dependencies.append(dep)
            continue

        namespace, name, current_version = parts
        print(f"Checking {name} (Current: v{current_version})...")
        
        latest_version = get_latest_version(namespace, name)
        
        if latest_version and latest_version != current_version:
            print(f"  -> Update found! Changing to v{latest_version}")
            updated_dependencies.append(f"{namespace}-{name}-{latest_version}")
            changes_made += 1
        else:
            if not latest_version:
                print(f"  -> Could not verify latest version, keeping v{current_version}")
            else:
                print("  -> Already up to date.")
            updated_dependencies.append(dep)
            
        time.sleep(0.3)

    if changes_made > 0:
        manifest['dependencies'] = updated_dependencies

        print(f"\nFound {changes_made} mod update(s).")
        print(f"Writing changes to {MANIFEST_FILE}...")
        
        with open(MANIFEST_FILE, 'w') as f:
            json.dump(manifest, f, indent=4)
        print("Done! manifest.json is updated.")
    else:
        print(f"\nNo dependency updates needed. Modpack remains on v{manifest.get('version_number')}.")

    return True

def create_thunderstore_zip():
    with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in FILES_TO_ZIP:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file}")
            else:
                print(f"Warning: {file} not found and was skipped.")
                
    print(f"\nSuccessfully created {ZIP_FILENAME} for Thunderstore.")

if __name__ == "__main__":
    print("=== Step 1: Checking & Updating Dependencies ===")
    update_manifest()
    print("\n=== Step 2: Packaging Distribution Zip ===")
    create_thunderstore_zip()