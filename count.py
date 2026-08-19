import os

# ============================================================
# CONFIGURATION
# ============================================================

# Root folder whose tree you want to save
ROOT_FOLDER = r"Z:\Projects\Smart Farming"

# ------------------------------------------------------------
# FOLDERS TO COMPLETELY IGNORE
# ------------------------------------------------------------
# These folders will not appear in the tree at all.
IGNORE_FOLDERS = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
]

# ------------------------------------------------------------
# DATASET FOLDERS
# ------------------------------------------------------------
# Put dataset folder names here.
#
# For example:
#
# dataset/
# ├── train/
# │   ├── apple/
# │   ├── banana/
# │   └── mango/
# └── test/
#     ├── apple/
#     ├── banana/
#     └── mango/
#
# If "dataset" is added here, only the first 5 files
# inside each subfolder will be displayed.
#
# The file count will still show the TOTAL number of files.
# ------------------------------------------------------------

DATASET_FOLDERS = [
    "Final Datasets",
    "dataset_split",
    "disease_dataset",
    "generated_crops",
    "pest_dataset"
]

# Number of files to display for dataset folders
MAX_DATASET_FILES = 5

# Output file
OUTPUT_FILE = "folder_tree.txt"


# ============================================================
# HELPER: CHECK WHETHER FOLDER IS IGNORED
# ============================================================

def is_ignored(folder_name, ignore_folders):
    return folder_name in ignore_folders


# ============================================================
# COUNT FILES
# ============================================================

def count_files(folder_path, ignore_folders):
    """
    Recursively count all files inside folder_path.

    Ignored folders are excluded from the count.
    """

    count = 0

    for current_path, directories, files in os.walk(folder_path):

        # Remove ignored folders
        directories[:] = [
            directory
            for directory in directories
            if not is_ignored(directory, ignore_folders)
        ]

        count += len(files)

    return count


# ============================================================
# GET FILES DIRECTLY INSIDE A FOLDER
# ============================================================

def get_files(folder_path):
    """
    Return files directly inside the given folder.
    """

    try:
        files = [
            file
            for file in os.listdir(folder_path)
            if os.path.isfile(
                os.path.join(folder_path, file)
            )
        ]

        return sorted(files)

    except PermissionError:
        return []


# ============================================================
# GENERATE FOLDER TREE
# ============================================================

def save_folder_tree(
    root_folder,
    output_file,
    ignore_folders=None,
    dataset_folders=None
):

    if ignore_folders is None:
        ignore_folders = []

    if dataset_folders is None:
        dataset_folders = []

    ignore_folders = set(ignore_folders)
    dataset_folders = set(dataset_folders)

    root_folder = os.path.abspath(root_folder)

    # --------------------------------------------------------
    # Recursive tree writer
    # --------------------------------------------------------

    def write_folder(
        folder_path,
        prefix="",
        is_root=False,
        inside_dataset=False
    ):

        folder_name = os.path.basename(folder_path)

        # Count ALL files recursively
        total_files = count_files(
            folder_path,
            ignore_folders
        )

        # ----------------------------------------------------
        # WRITE FOLDER
        # ----------------------------------------------------

        if is_root:
            f.write(
                f"{folder_name}/ "
                f"({total_files} files)\n"
            )
        else:
            f.write(
                f"{prefix}├── {folder_name}/ "
                f"({total_files} files)\n"
            )

        # ----------------------------------------------------
        # FIND CHILD FOLDERS + FILES
        # ----------------------------------------------------

        try:
            entries = sorted(
                os.listdir(folder_path)
            )
        except PermissionError:
            return

        child_folders = []
        files = []

        for entry in entries:

            entry_path = os.path.join(
                folder_path,
                entry
            )

            # Skip ignored folders
            if os.path.isdir(entry_path):

                if entry in ignore_folders:
                    continue

                child_folders.append(entry)

            elif os.path.isfile(entry_path):

                files.append(entry)

        # ----------------------------------------------------
        # DETERMINE WHETHER THIS IS A DATASET FOLDER
        # ----------------------------------------------------

        current_is_dataset = (
            folder_name in dataset_folders
            or inside_dataset
        )

        # ----------------------------------------------------
        # WRITE CHILD FOLDERS
        # ----------------------------------------------------

        for child_folder in child_folders:

            child_path = os.path.join(
                folder_path,
                child_folder
            )

            child_total_files = count_files(
                child_path,
                ignore_folders
            )

            # Indentation
            if is_root:
                child_prefix = "    "
            else:
                child_prefix = prefix + "    "

            f.write(
                f"{child_prefix}├── "
                f"{child_folder}/ "
                f"({child_total_files} files)\n"
            )

            # ----------------------------------------------
            # Recursively process child folder
            # ----------------------------------------------

            write_contents(
                child_path,
                child_prefix + "    ",
                current_is_dataset
            )

        # ----------------------------------------------------
        # WRITE FILES
        # ----------------------------------------------------

        if current_is_dataset:

            # Dataset folder:
            # only show first N files
            files_to_show = files[:MAX_DATASET_FILES]

        else:

            # Normal folder:
            # show all files
            files_to_show = files

        for file in files_to_show:

            if is_root:
                file_prefix = "    "
            else:
                file_prefix = prefix + "    "

            f.write(
                f"{file_prefix}├── {file}\n"
            )

        # Show how many files were hidden
        if current_is_dataset and len(files) > MAX_DATASET_FILES:

            hidden_count = (
                len(files) - MAX_DATASET_FILES
            )

            if is_root:
                hidden_prefix = "    "
            else:
                hidden_prefix = prefix + "    "

            f.write(
                f"{hidden_prefix}└── "
                f"... {hidden_count} more files\n"
            )

    # --------------------------------------------------------
    # WRITE CONTENTS OF A FOLDER
    # --------------------------------------------------------

    def write_contents(
        folder_path,
        prefix,
        inside_dataset=False
    ):

        folder_name = os.path.basename(folder_path)

        try:
            entries = sorted(
                os.listdir(folder_path)
            )
        except PermissionError:
            return

        child_folders = []
        files = []

        for entry in entries:

            entry_path = os.path.join(
                folder_path,
                entry
            )

            if os.path.isdir(entry_path):

                if entry in ignore_folders:
                    continue

                child_folders.append(entry)

            elif os.path.isfile(entry_path):

                files.append(entry)

        # ----------------------------------------------------
        # Current folder is dataset?
        # ----------------------------------------------------

        current_is_dataset = (
            folder_name in dataset_folders
            or inside_dataset
        )

        # ----------------------------------------------------
        # CHILD FOLDERS
        # ----------------------------------------------------

        for child_folder in child_folders:

            child_path = os.path.join(
                folder_path,
                child_folder
            )

            total_files = count_files(
                child_path,
                ignore_folders
            )

            f.write(
                f"{prefix}├── "
                f"{child_folder}/ "
                f"({total_files} files)\n"
            )

            # Recursively continue
            write_contents(
                child_path,
                prefix + "    ",
                current_is_dataset
            )

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        if current_is_dataset:

            files_to_show = files[:MAX_DATASET_FILES]

        else:

            files_to_show = files

        for file in files_to_show:

            f.write(
                f"{prefix}├── {file}\n"
            )

        # ----------------------------------------------------
        # HIDDEN FILE COUNT
        # ----------------------------------------------------

        if current_is_dataset and len(files) > MAX_DATASET_FILES:

            hidden_count = (
                len(files) - MAX_DATASET_FILES
            )

            f.write(
                f"{prefix}└── "
                f"... {hidden_count} more files\n"
            )

    # ========================================================
    # CREATE OUTPUT
    # ========================================================

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        root_name = os.path.basename(root_folder)

        root_count = count_files(
            root_folder,
            ignore_folders
        )

        f.write(
            f"{root_name}/ "
            f"({root_count} files)\n"
        )

        write_contents(
            root_folder,
            "    ",
            root_name in dataset_folders
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    save_folder_tree(
        root_folder=ROOT_FOLDER,
        output_file=OUTPUT_FILE,
        ignore_folders=IGNORE_FOLDERS,
        dataset_folders=DATASET_FOLDERS
    )

    print(
        "Folder tree successfully saved!"
    )

    print(
        f"Output: {os.path.abspath(OUTPUT_FILE)}"
    )