import json

def fix_notebook_06():
    path = "notebooks/06_prepare_disease_dataset.ipynb"
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            for i, line in enumerate(cell["source"]):
                if 'dest = dest_dir / f"{src.stem}_{abs(hash(str(src)))}{src.suffix}"' in line:
                    cell["source"][i] = line.replace(
                        'dest = dest_dir / f"{src.stem}_{abs(hash(str(src)))}{src.suffix}"',
                        'dest = dest_dir / f"img_{abs(hash(str(src)))}{src.suffix}"'
                    )
                    modified = True
                    print("Updated 06 notebook line!")
    
    if modified:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1)
        print("Saved 06 notebook.")
    else:
        print("06 notebook already updated or target not found.")

def fix_notebook_07():
    path = "notebooks/07_train_disease_classifier.ipynb"
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            for i, line in enumerate(cell["source"]):
                if "A.CoarseDropout(max_holes=4, max_height=24, max_width=24, p=0.3)" in line:
                    cell["source"][i] = line.replace(
                        "A.CoarseDropout(max_holes=4, max_height=24, max_width=24, p=0.3)",
                        "A.CoarseDropout(num_holes_range=(1, 4), hole_height_range=(12, 24), hole_width_range=(12, 24), p=0.3)"
                    )
                    modified = True
                    print("Updated 07 notebook line!")
    
    if modified:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1)
        print("Saved 07 notebook.")
    else:
        print("07 notebook already updated or target not found.")

if __name__ == "__main__":
    fix_notebook_06()
    fix_notebook_07()
