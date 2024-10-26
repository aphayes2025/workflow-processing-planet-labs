import shutil
import os
import zipfile
import os
import json


def unzip_file(zip_file_path, extract_to_dir):
    # Check if the zip file exists
    if not os.path.exists(zip_file_path):
        print(f"File {zip_file_path} not found.")
        return
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(extract_to_dir):
        os.makedirs(extract_to_dir)
    
    # Unzipping the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_dir)
        print(f"Extracted all files to {extract_to_dir}")
    try:
        os.remove(zip_file_path)
        print(f"Deleted zip file: {zip_file_path}")
    except OSError as e:
        print(f"Error: {e.strerror}")



def rewrite_files(dest_folder, extract_to_dir, stringToCheck):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    root = os.getcwd()
    directory = extract_to_dir + '/files'
    counter = 0
    for file in (os.listdir(directory)):
        # making sure only stringToCheck is being processed
        if stringToCheck in file:
            src_file_path = os.path.join(root, directory, file)
            dest_file_path = os.path.join(f'{root}/{dest_folder}', file)
            
            # copying file
            shutil.copy(src_file_path, dest_file_path)
            counter += 1
    print(f"Copied {counter} {stringToCheck} files to {root}/{dest_folder}")


if __name__ == "__main__":
    zip_file_path = 'output.zip'  # Replace with your zip file path
    extract_to_dir = 'UVM_gage-high-cloud-cover-2'  # Replace with your desired output directory
    unzip_file(zip_file_path, extract_to_dir)   

    stringToCheckSR = 'SR'
    stringToCheckJSON = '.json'

    dest_folderSR = 'UVM_gage-high-cloud-cover-tif'
    dest_folderJSON = 'UVM_gage-high-cloud-cover-json'

    # get two seperate folders 
    rewrite_files(dest_folderSR, extract_to_dir, stringToCheckSR)
    rewrite_files(dest_folderJSON, extract_to_dir, stringToCheckJSON)