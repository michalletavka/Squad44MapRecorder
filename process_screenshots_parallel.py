from PIL import Image, ImageDraw, ImageFilter
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Parameters
# 540 for 5000 step

cropping_width = 540
cropping_height = 540
stitching_overlap_percentage = 18 # a default value
stitching_images_per_row = 51 # a default value

# Globals
input_folder = sys.argv[1]
crop_images_folder = input_folder + "/tmp_cropped"
joined_row_images_folder = input_folder + "/tmp_rows"
output_folder = sys.argv[2]
stitching_images_per_row = int(sys.argv[3])
stitching_overlap_percentage = int(sys.argv[4])

def crop_center(image_path, target_width, target_height):
    # Open the image
    original_image = Image.open(image_path)

    # Get the size of the original image
    original_width, original_height = original_image.size

    # Calculate the cropping box
    left = (original_width - target_width) / 2
    top = (original_height - target_height) / 2
    right = (original_width + target_width) / 2
    bottom = (original_height + target_height) / 2

    # Crop the image
    cropped_image = original_image.crop((left, top, right, bottom))

    return cropped_image

def process_image(input_path, output_path, target_width, target_height):
    # Crop the image
    cropped_image = crop_center(input_path, target_width, target_height)

    # Save the cropped image
    cropped_image.save(output_path)


def crop_images_in_folder(input_folder, output_folder, target_width, target_height):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get total number of images in the input folder
    total_images = len([f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
    current_image = 1

    with ThreadPoolExecutor() as executor:
        futures = []

        # Iterate over all files in the input folder
        for filename in os.listdir(input_folder):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):  # Add more extensions if needed
                print(f"Cropping image {current_image} of {total_images}...")
                current_image += 1

                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, f"cropped_{filename}")

                # Submit the task to the thread pool
                future = executor.submit(process_image, input_path, output_path, target_width, target_height)
                futures.append(future)

        # Wait for all tasks to complete
        for future in futures:
            future.result()

def stitch_images_horizontally(images, overlap_percent):
    overlap_pixels = int(images[0].width * overlap_percent / 100)
    final_width = sum(img.width - overlap_pixels for img in images) + overlap_pixels
    final_image = Image.new("RGBA", (final_width, max(img.height for img in images)))

    current_x = 0
    for img in images:
        final_image.paste(img, (current_x, 0))
        current_x += img.width - overlap_pixels

    return final_image

def process_row(input_images, output_path, overlap_percent):
    row_image = stitch_images_horizontally(input_images, overlap_percent)
    row_image.save(output_path)


def stitch_images_vertically(images, overlap_percent=40):
    overlap_pixels = int(images[0].height * overlap_percent / 100)
    final_height = sum(img.height - overlap_pixels for img in images) + overlap_pixels
    final_image = Image.new("RGBA", (max(img.width for img in images), final_height))

    current_y = 0
    for img in images:
        final_image.paste(img, (0, current_y))
        current_y += img.height - overlap_pixels

    return final_image

def stitch_images_into_rows(folder_path, output_path, images_in_row, overlap_percent):
    # Ensure the output folder exists
    os.makedirs(output_path, exist_ok=True)

    # Get total number of images in the input folder
    total_images = int(len([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]) / images_in_row)
    current_image = 1

    with ThreadPoolExecutor() as executor:
        futures = []
        # Stitch together images by row
        for root, dirs, files in os.walk(folder_path):
            for i in range(0, len(files), images_in_row):
                print(f"Stitching row {current_image} of {total_images}...")
                current_image += 1

                images = [Image.open(os.path.join(root, file)) for file in files[i:i+images_in_row]]

                # Submit the task to the thread pool
                future = executor.submit(process_row,
                                         images,
                                         os.path.join(output_path, f"row_{str(i).zfill(6)}.png"),
                                         overlap_percent)
                futures.append(future)

        # Wait for all tasks to complete
        for future in futures:
            future.result()


def stitch_rows_into_final(folder_path, output_path, overlap_percent):
    # Ensure the output folder exists
    os.makedirs(output_path, exist_ok=True)

    # Get a list of all files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Open each image in the folder
    images = [Image.open(os.path.join(folder_path, filename)) for filename in image_files]

    # Stitch the images together
    print(f"Stitching final image...")
    result_image = stitch_images_vertically(images, overlap_percent)

    # Save the result
    result_image.save(output_path + "final.png")
    print(f"Final image saved to {output_path}final.png")

crop_images_in_folder(input_folder, crop_images_folder, cropping_width, cropping_height)

stitch_images_into_rows(crop_images_folder, joined_row_images_folder, stitching_images_per_row, stitching_overlap_percentage)

stitch_rows_into_final(joined_row_images_folder, output_folder, stitching_overlap_percentage)
