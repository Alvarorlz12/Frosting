import json
import os
import shutil
import argparse

def filter_cameras(model_path):
    """
    Splits cameras.json into train and test sets based on image names.
    Overwrites cameras.json with only train cameras for Frosting optimization.
    """
    json_path = os.path.join(model_path, "cameras.json")
    
    if not os.path.exists(json_path):
        print(f"[Error] File not found: {json_path}")
        return

    print(f"Processing: {json_path}")

    # 1. Create a backup of the original full file
    backup_path = os.path.join(model_path, "cameras_original_backup.json")
    shutil.copy(json_path, backup_path)
    print(f"> Backup created at: {backup_path}")

    # 2. Load data
    with open(json_path, 'r') as f:
        cameras = json.load(f)

    train_cams = []
    test_cams = []

    # 3. Filter cameras
    # We assume test images start with "test" (e.g., "test_0001")
    for cam in cameras:
        img_name = cam.get('img_name', '')
        if img_name.startswith('test'):
            test_cams.append(cam)
        else:
            train_cams.append(cam)

    print(f"> Total cameras: {len(cameras)}")
    print(f"> Train cameras found: {len(train_cams)}")
    print(f"> Test cameras found:  {len(test_cams)}")

    # 4. Save Test cameras to a separate file (for later evaluation)
    test_json_path = os.path.join(model_path, "cameras_test.json")
    with open(test_json_path, 'w') as f:
        json.dump(test_cams, f, indent=4)
    print(f"> Saved test cameras to: {test_json_path}")

    # 5. Save a safe copy of Train cameras
    train_json_path = os.path.join(model_path, "cameras_train.json")
    with open(train_json_path, 'w') as f:
        json.dump(train_cams, f, indent=4)

    # 6. Overwrite the main cameras.json with ONLY Train cameras
    # This ensures Frosting only sees training data and avoids index errors
    with open(json_path, 'w') as f:
        json.dump(train_cams, f, indent=4)
    
    print("[Success] cameras.json overwritten with training data only.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter cameras.json to isolate training cameras.")
    parser.add_argument("--model_path", "-m", type=str, required=True, 
                        help="Path to the model output directory (e.g., output/vanilla_gs/khady)")
    args = parser.parse_args()

    filter_cameras(args.model_path)