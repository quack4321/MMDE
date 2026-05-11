import json
import os
import time
import urllib.request
import urllib.error

MANIFEST_FILE = 'manifest.json'

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

def update_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: Could not find {MANIFEST_FILE}.")
        return

    # Load the existing manifest
    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {MANIFEST_FILE} is not a valid JSON file.")
        return

    dependencies = manifest.get('dependencies', [])
    if not dependencies:
        print("No dependencies found.")
        return

    print(f"Checking {len(dependencies)} dependencies for updates...\n")
    
    updated_dependencies = []
    changes_made = 0

    for dep in dependencies:
        parts = dep.split('-')
        if len(parts) != 3:
            # If the format is weird, keep it exactly as it was and skip
            updated_dependencies.append(dep)
            continue

        namespace, name, current_version = parts
        print(f"Checking {name} (Current: v{current_version})...")
        
        # Ask the API for the newest version
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
            
        # Polite API pacing
        time.sleep(0.5)

    # Save the changes back to the manifest if updates were found
    if changes_made > 0:
        manifest['dependencies'] = updated_dependencies
        print(f"\nWriting {changes_made} updates to {MANIFEST_FILE}...")
        
        # Write back with indentation to keep it readable
        with open(MANIFEST_FILE, 'w') as f:
            json.dump(manifest, f, indent=4)
        print("Done! Your manifest.json is now up to date.")
    else:
        print("\nNo updates were needed. Your manifest.json is already up to date.")

if __name__ == "__main__":
    update_manifest()