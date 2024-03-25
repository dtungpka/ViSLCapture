import os
import cv2

# Path to the directory containing the images
image_dir = '/path/to/images'

# Path to the crop data file
crop_file = '/path/to/1.txt'

# Read the crop data from the file
with open(crop_file, 'r') as file:
    crop_data = file.readlines()

# Process each line of crop data
for line in crop_data:
    # Split the line into label and crop coordinates
    label, *crop_coords = line.strip().split()

    # Get the image file name based on the label
    image_file = os.path.join(image_dir, f'{label}.jpg')

    # Check if the image file exists
    if os.path.exists(image_file):
        # Load the image
        image = cv2.imread(image_file)

        # Convert crop coordinates to integers
        crop_coords = [int(float(coord) * image.shape[1]) for coord in crop_coords]

        # Crop the image
        cropped_image = image[crop_coords[1]:crop_coords[3], crop_coords[0]:crop_coords[2]]

        # Save the cropped image
        output_file = os.path.join(image_dir, f'{label}_cropped.jpg')
        cv2.imwrite(output_file, cropped_image)
