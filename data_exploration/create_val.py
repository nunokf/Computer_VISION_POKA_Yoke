import os
import shutil
import random


def move_files_to_validation(
        train_images_dir,
        train_labels_dir,
        val_images_dir,
        val_labels_dir,
        image_suffix='.jpg',
        label_suffix='.txt',
        move_fraction=0.2,
        seed=42
):
    """
    Move a fraction of images and their corresponding labels from training to validation set.

    :param train_images_dir: Directory containing training images.
    :param train_labels_dir: Directory containing training labels.
    :param val_images_dir: Directory to move images to for validation.
    :param val_labels_dir: Directory to move labels to for validation.
    :param image_suffix: File suffix for images (e.g., '.jpg').
    :param label_suffix: File suffix for labels (e.g., '.txt').
    :param move_fraction: Fraction of images to move to validation set.
    :param seed: Seed for reproducibility.
    """
    # Ensure val directories exist
    os.makedirs(val_images_dir, exist_ok=True)
    os.makedirs(val_labels_dir, exist_ok=True)

    # Get list of all image and label files
    image_files = [f for f in os.listdir(train_images_dir) if f.endswith(image_suffix)]
    label_files = [f for f in os.listdir(train_labels_dir) if f.endswith(label_suffix)]

    # Remove extensions to match names
    image_base_names = set(f[:-len(image_suffix)] for f in image_files)
    label_base_names = set(f[:-len(label_suffix)] for f in label_files)

    # Ensure that each image has a corresponding label
    missing_labels = image_base_names - label_base_names
    missing_images = label_base_names - image_base_names

    if missing_labels:
        print(f"Warning: Images without labels (base names): {missing_labels}")
    if missing_images:
        print(f"Warning: Labels without images (base names): {missing_images}")

    # Only consider images that have corresponding labels
    valid_base_names = image_base_names & label_base_names

    # Filter images and labels based on valid base names
    valid_image_files = [f for f in image_files if f[:-len(image_suffix)] in valid_base_names]
    valid_label_files = [f for f in label_files if f[:-len(label_suffix)] in valid_base_names]

    # Calculate number of files to move
    num_files_to_move = int(move_fraction * len(valid_image_files))

    # Randomly select files to move
    random.seed(seed)
    files_to_move = random.sample(valid_image_files, num_files_to_move)

    # Move selected files and their corresponding labels
    for file_name in files_to_move:
        base_name = file_name[:-len(image_suffix)]
        # Move image
        shutil.move(os.path.join(train_images_dir, file_name), os.path.join(val_images_dir, file_name))

        # Move label
        corresponding_label = base_name + label_suffix
        if corresponding_label in valid_label_files:
            shutil.move(os.path.join(train_labels_dir, corresponding_label),
                        os.path.join(val_labels_dir, corresponding_label))

    print(f"Moved {num_files_to_move} files to the validation set.")
