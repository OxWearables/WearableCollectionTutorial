# %% Imports
import re
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from datetime import datetime
from typing import Tuple
from IPython.display import clear_output


# %% main function
def notebook_annotation(
    label_dir_name: str,
    schema: dict[str, str],
    image_paths: np.ndarray[str],
    image_datetimes: np.ndarray[np.datetime64],
    imgs_to_display: int = 5,
    save_freq: int = 5,
    figsize: Tuple[int] | None = None,
):
    """
    A simple annotation tool for annotating images using maptlotlib in a jupyter notebook.
    Args:
    - label_dir_name: the name of the directory to save the annotations to
    - schema: a dictionary mapping short names to long names, e.g. {"s": "Sedentary", "l": "Light", "m": "MVPA"}
    - image_paths: a numpy array of image paths
    - image_datetimes: a numpy array of image datetimes
    - imgs_to_display: the number of images to display at once
    - save_freq: how often to save the annotations
    - figsize: the size of the figure to display


    At each iteration, we display up to imgs_to_display images in a row (from image_paths), display their timestamp (from image_datetimes), and their current annotation (from the numpy array).

    The loop has the the following commands:
    - "help"/"h" - display the commands
    - "next"/. - move to the next N images (if there are any left, but only jumping one image along)
    - "prev"/, - move to the previous N images (if there are any left, but only jumping one image along)
    - "copy/ c [N]" - copy the current annotation to the (optionally, N) next image(s), and display the next N images
    - "quit/ q" - quit the loop, saving the annotations to the numpy array

    We save the current image index, so that we can resume the loop from where we left off, as well as how many images we have annotated so far.
    This can be viewed in summary.txt file under raw_data/annotations/{label_dir_name}.
    This file is of the form:
    Current image index: <where annotation left off>
    Number of annotated images: <number of images annotated so far>
    """

    # ============= Setup =============
    # check there is at least one image to annotate
    if (len(image_paths) < 1) or (len(image_datetimes) < 1):
        raise ValueError("Empty image paths or image datetimes provided.")

    # check that the image paths and image_datetimes are the same length
    if len(image_paths) != len(image_datetimes):
        raise ValueError(
            "The length of `image_paths` does not match `image_datetimes`."
        )

    commands_strs = ["next", ".", "prev", ",", "copy", "c", "quit", "q"]
    # check the schema short names do not contain any of the commands
    for short_name in schema.keys():
        if short_name in commands_strs:
            raise ValueError(f"Schema short name '{short_name}' is a command")

    # check the schema long names do not contain any of the commands
    for long_name in schema.values():
        if long_name in commands_strs:
            raise ValueError(f"Schema long name '{long_name}' is a command")

    # check the schema short names are unique
    if len(schema.keys()) != len(set(schema.keys())):
        raise ValueError("Schema short names are not unique")

    # check the schema long names are unique
    if len(schema.values()) != len(set(schema.values())):
        raise ValueError("Schema long names are not unique")

    # Convert label_dir_name to str and strip "/" from the end
    label_dir_name = str(label_dir_name).rstrip("/")
    # check if the directory exists and there are already annotations
    if Path(f"{label_dir_name}").exists():
        # try load the annotations
        if Path(f"{label_dir_name}/labels.npy").exists():
            annotations = np.load(f"{label_dir_name}/labels.npy", allow_pickle=True)
        else:
            annotations = np.empty(len(image_paths), dtype=str)
        # try load the summary
        if Path(f"{label_dir_name}/summary.txt").exists():
            with open(f"{label_dir_name}/summary.txt", "r") as f:
                lines = f.readlines()
                current_index = int(lines[0].split(": ")[1])
                n_annotated = int(lines[1].split(": ")[1])
        else:
            current_index = 0
            n_annotated = 0
    else:
        # create the directory
        Path(f"{label_dir_name}").mkdir(parents=True)
        annotations = np.empty(len(image_paths), dtype=object)
        current_index = 0
        n_annotated = 0

    # sort the image paths and datetimes by datetime
    tuples = list(zip(image_paths, image_datetimes))
    tuples.sort(key=lambda x: x[1])
    image_paths, image_datetimes = zip(*tuples)

    # maintain pointers to a few asynchronously loaded images to speed up image loading

    # ============= Loop =============

    left_offset = min(imgs_to_display - 1, 1)  # have at least 1 image to the left
    right_offset = imgs_to_display - left_offset

    while True:
        # === Display images ===
        plt.figure(figsize=figsize)

        min_image_index = max(current_index - left_offset, 0)
        max_image_index = min(current_index + right_offset, len(image_paths))

        for disp_i, i in enumerate(range(min_image_index, max_image_index)):
            n_on_display = max_image_index - min_image_index
            plt.subplot(1, n_on_display, disp_i + 1)
            plt.imshow(Image.open(image_paths[i]))
            rel_i = np.abs(i - current_index) if (i - current_index) != 0 else i
            title = f"{rel_i} {str(image_datetimes[i])[11:19]}"  # relative numbers
            if i == max_image_index - 1:  # for last image show progress
                title += f" {n_annotated}/{len(image_paths)}"
            plt.title(title)
            plt.xlabel(annotations[i])
            # remove all ticks and border
            plt.xticks([])
            plt.yticks([])
            # draw a bounding box around the middle image
            if i == current_index:
                plt.gca().spines["left"].set_color("red")
                plt.gca().spines["right"].set_color("red")
                plt.gca().spines["top"].set_color("red")
                plt.gca().spines["bottom"].set_color("red")

        plt.show()

        plt.pause(0.0001)  # pause to allow the figure to display

        # === Get command ===

        command = input("Enter annotation/command: ")
        # remove any leading/trailing whitespace
        command = command.strip()

        if command in schema.keys():
            annotations[current_index] = schema[command]
            current_index = min(current_index + 1, len(image_paths) - 1)
            n_annotated += 1
        elif command in schema.values():
            annotations[current_index] = command
            current_index = min(current_index + 1, len(image_paths) - 1)
            n_annotated += 1
        elif command.startswith("next") or command.startswith("."):
            n = get_repeat(command)
            current_index = min(current_index + n, len(image_paths) - 1)
        elif command.startswith("prev") or command.startswith(","):
            n = get_repeat(command)
            current_index = max(current_index - n, 0)
        elif command.startswith("copy") or command.startswith("c"):  # copy n
            n = get_repeat(command)
            if current_index > 0 and current_index + n < len(image_paths):
                annotations[current_index : current_index + n] = annotations[
                    current_index - 1
                ]
                current_index = min(current_index + n, len(image_paths) - 1)
                n_annotated += n
        elif command in ["help", "h"]:
            print("Commands:")
            print("- next/. - move to the next image")
            print("- prev/, - move to the previous image")
            print("- copy/c - copy the previous annotation to the current image")
            print("- quit/q - quit the loop")
        elif command in ["quit", "q"]:
            break

        # === save the annotations and summary ===
        if n_annotated % save_freq == 0:
            np.save(f"{label_dir_name}/labels.npy", annotations)

            with open(f"{label_dir_name}/summary.txt", "w") as f:
                f.write(f"Current image index: {current_index}\n")
                f.write(
                    f"Number of annotated images: {np.count_nonzero(annotations)}\n"
                )

        # === refresh the output ===
        clear_output(wait=True)

    np.save(f"{label_dir_name}/labels.npy", annotations)

    with open(f"{label_dir_name}/summary.txt", "w") as f:
        f.write(f"Current image index: {current_index}\n")
        f.write(f"Number of annotated images: {np.count_nonzero(annotations)}\n")


def get_repeat(command: str) -> int:
    """
    For commands of the form "<command><number>", returns the number.
    If the command is just of the form "<command>", return 1.
    """
    match = re.search(r"\d+", command)
    if match:
        return int(match.group())
    else:
        return 1


# %%
def main():
    # %%
    time_format = "%Y%m%d_%H%M%S"

    def get_img_times(paths):
        return [datetime.strptime(path.parts[-1][17:32], time_format) for path in paths]

    small_img_paths = list(Path("../raw_data/camera/small").glob("*.JPG"))
    small_img_times = get_img_times(small_img_paths)

    # convert to np.ndarray
    image_datetimes = np.array(small_img_times, dtype=np.datetime64)
    image_paths = np.array(small_img_paths)

    # %% start annotation
    label_dir_name = "test"  # change this to something more descriptive
    schema = {
        # short name: long name
        "s": "Sedentary",
        "l": "Light",
        "m": "MVPA",
    }

    notebook_annotation(
        label_dir_name,
        schema,
        image_paths,
        image_datetimes,
    )


# %%
if __name__ == "__main__":
    main()
