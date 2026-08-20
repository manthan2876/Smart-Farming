import os

ROOT_FOLDER = r"Z:\Projects\Smart-Farming"
IGNORE_FOLDERS = [".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"]
DATASET_FOLDERS = ["datasets", "final_combined_datasets", "dataset_split", "disease_dataset", "generated_crops", "pest_dataset", "processed_dataset-old"]
OUTPUT_FILE = "folder_tree.txt"

def is_ignored(folder_name, ignore_folders):
    return folder_name in ignore_folders

def count_files(folder_path, ignore_folders):
    count = 0
    for current_path, directories, files in os.walk(folder_path):
        directories[:] = [d for d in directories if not is_ignored(d, ignore_folders)]
        count += len(files)
    return count

def save_folder_tree(root_folder, output_file, ignore_folders=None, dataset_folders=None):
    ignore_folders = set(ignore_folders or [])
    dataset_folders = set(dataset_folders or [])
    root_folder = os.path.abspath(root_folder)

    def write_contents(folder_path, prefix, inside_dataset=False):
        folder_name = os.path.basename(folder_path)
        try:
            entries = sorted(os.listdir(folder_path))
        except PermissionError:
            return

        child_folders = []
        files = []
        for entry in entries:
            entry_path = os.path.join(folder_path, entry)
            if os.path.isdir(entry_path):
                if entry in ignore_folders:
                    continue
                child_folders.append(entry)
            elif os.path.isfile(entry_path):
                files.append(entry)

        current_is_dataset = folder_name in dataset_folders or inside_dataset

        for child_folder in child_folders:
            child_path = os.path.join(folder_path, child_folder)
            total_files = count_files(child_path, ignore_folders)
            f.write(f"{prefix}├── {child_folder}/ ({total_files} files)\n")
            write_contents(child_path, prefix + "    ", current_is_dataset)

        # Only write individual files if we are NOT inside a dataset folder
        if not current_is_dataset:
            for file in files:
                f.write(f"{prefix}├── {file}\n")

    with open(output_file, "w", encoding="utf-8") as f:
        root_name = os.path.basename(root_folder)
        root_count = count_files(root_folder, ignore_folders)
        f.write(f"{root_name}/ ({root_count} files)\n")
        write_contents(root_folder, "    ", root_name in dataset_folders)

if __name__ == "__main__":
    save_folder_tree(root_folder=ROOT_FOLDER, output_file=OUTPUT_FILE, ignore_folders=IGNORE_FOLDERS, dataset_folders=DATASET_FOLDERS)
    print("Folder tree successfully saved!")
    print(f"Output: {os.path.abspath(OUTPUT_FILE)}")