# %%
import os
import cv2
import numpy as np
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# %%
def resize_image(image, target_height, target_width):
    h, w = image.shape[:2]
    aspect = w / h

    if w > h:
        new_w = target_width
        new_h = int(new_w / aspect)
    else:
        new_h = target_height
        new_w = int(new_h * aspect)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Pad the image if necessary
    delta_w = target_width - new_w
    delta_h = target_height - new_h
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [0, 0, 0]
    return cv2.copyMakeBorder(
        resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )


def process_images(input_dir, output_dir, target_height, target_width):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for img_path in input_path.glob("*.JPG"):
        # Read image
        img = cv2.imread(str(img_path))

        # Resize image
        resized_img = resize_image(img, target_height, target_width)

        # Save processed image
        output_file = output_path / img_path.name
        cv2.imwrite(str(output_file), resized_img)

        print(f"Processed: {img_path.name}")


# %%
input_directory = "../pilot_data_2024/camera"
output_directory = "../pilot_data_2024/resize"


target_height = 440
target_width = 756

# %%
process_images(input_directory, output_directory, target_height, target_width)
