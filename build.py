import zipfile
import os

# Added the new script to the distribution list
files_to_zip = [
    'README.md', 
    'manifest.json', 
    'icon.png', 
    'download_mods.py', 
    'download_mods_exclude_textures.py'
]
zip_filename = 'MMDE.zip'

def create_thunderstore_zip():
    # ZIP_DEFLATED applies standard compression
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file}")
            else:
                print(f"Warning: {file} not found and was skipped.")
                
    print(f"\nSuccessfully created {zip_filename} for Thunderstore.")

if __name__ == "__main__":
    create_thunderstore_zip()
