import os
import json
import shutil
import argparse
from pathlib import Path

def preprocess_shelly_dataset(dataset_path):
    print(f"Processing dataset at: {dataset_path}")
    
    # Paths
    train_src_dir = os.path.join(dataset_path, "train")
    test_src_dir = os.path.join(dataset_path, "test")
    images_dest_dir = os.path.join(dataset_path, "images")
    
    json_train_path = os.path.join(dataset_path, "transforms_train.json")
    json_test_path = os.path.join(dataset_path, "transforms_test.json")

    # Ensure destination 'images' folder exists
    os.makedirs(images_dest_dir, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Process TRAIN: Copy to 'images/' & Fix JSON
    # ---------------------------------------------------------
    if os.path.exists(train_src_dir) and os.path.exists(json_train_path):
        print("-> Processing TRAIN data...")

        # Copy images
        for filename in os.listdir(train_src_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                src = os.path.join(train_src_dir, filename)
                dst = os.path.join(images_dest_dir, filename)
                shutil.copy2(src, dst)

        # Update transforms_train.json
        with open(json_train_path, 'r') as f:
            data = json.load(f)

        for frame in data['frames']:
            # Fix path: 'train/0001.png' -> 'images/0001'
            if "train/" in frame['file_path']:
                new_path = frame['file_path'].replace("train/", "images/")
            else:
                # Fallback if path is already relative
                new_path = os.path.join("images", os.path.basename(frame['file_path']))
            
            # Remove extension
            new_path = os.path.splitext(new_path)[0]
            frame['file_path'] = new_path

        with open(json_train_path, 'w') as f:
            json.dump(data, f, indent=4)
        print("   [OK] Train images copied to 'images/' and JSON updated.")
    else:
        print("   [Warning] 'train' folder or 'transforms_train.json' not found.")

    # ---------------------------------------------------------
    # 2. Process TEST: Rename, Copy to 'images/' & Fix JSON
    # ---------------------------------------------------------
    if os.path.exists(test_src_dir) and os.path.exists(json_test_path):
        print("-> Processing TEST data...")
        
        # A. Rename physical files in 'test/' to avoid collision (0001.png -> test_0001.png)
        for filename in os.listdir(test_src_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and not filename.startswith("test_"):
                old_file = os.path.join(test_src_dir, filename)
                new_file = os.path.join(test_src_dir, f"test_{filename}")
                os.rename(old_file, new_file)

        # B. Copy renamed files to 'images/'
        for filename in os.listdir(test_src_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                src = os.path.join(test_src_dir, filename)
                dst = os.path.join(images_dest_dir, filename)
                shutil.copy2(src, dst)

        # C. Update transforms_test.json
        with open(json_test_path, 'r') as f:
            data = json.load(f)

        for frame in data['frames']:
            original_path = frame['file_path'] # e.g. "test/0001.png"
            
            # Extract basic name
            name = os.path.basename(original_path)  # "0001.png"
            
            # Apply renaming prefix logic (if not already present in JSON)
            if not name.startswith("test_"):
                name = f"test_{name}"
            
            # Construct new path pointing to 'images/'
            # "images/test_001" (no extension)
            name_no_ext = os.path.splitext(name)[0]
            new_path = os.path.join("images", name_no_ext) 
            
            frame['file_path'] = new_path

        with open(json_test_path, 'w') as f:
            json.dump(data, f, indent=4)
        print("   [OK] Test images renamed, copied to 'images/' and JSON updated.")
    else:
        print("   [Warning] 'test' folder or 'transforms_test.json' not found.")

    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess Shelly/Blender dataset for Frosting.")
    parser.add_argument("--path", "-p", type=str, required=True,
                        help="Path to the dataset root.")
    args = parser.parse_args()

    preprocess_shelly_dataset(args.path)