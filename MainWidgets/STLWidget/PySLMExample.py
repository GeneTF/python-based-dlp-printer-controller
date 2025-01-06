import pyslm
import numpy as np
import trimesh
from PIL import Image
import cv2
from scipy.ndimage import label, measurements
from scipy.ndimage import label, binary_erosion, binary_dilation
from skimage.measure import regionprops
import matplotlib.pyplot as plt
import time

# Imports the part and sets the geometry to an STL file (frameGuide.stl)
solidPart = pyslm.Part('myFrameGuide')
file_path = r"C:\Users\Gene Felix\Downloads\TAMU\BMEN\Solidworks\68 - Flow Channels\\"
file_name = 'One Channel Cut.STL'
solidPart.setGeometry(file_path + file_name)
solidPart.dropToPlatform()

"""
Transform the part:
Rotate the part 30 degrees about the Z-Axis - given in degrees
Translate by an offset of (5,10) and drop to the platform the z=0 Plate boundary
"""
# solidPart.origin = [0.0, 0.0, 0.0]
# solidPart.rotation = np.array([0, 0, 30])
# solidPart.scaleFactor = 2.0
# solidPart.dropToPlatform()

# Note the resolution units are [mm/px], DPI = [px/inch]
dpi = 300.0
um_per_px = 50
z_val = 0.1
img_width = 1280
img_height = 800

print_width = img_width * um_per_px * 10**-3
print_height = img_height * um_per_px * 10**-3
print_area = np.array([print_width, print_height])
# print("print_area:", print_area)
print_center = print_area / 2
centroid_xy = solidPart._geometry.centroid[0:2]
# print("centroid_xy:", centroid_xy)
center_vector = print_center - centroid_xy
center = list(center_vector) + [0]


def get_slice(z_val_in):
    # Return the Path2D object from Trimesh by setting second argument to False
    slice = solidPart.getTrimeshSlice(z_val_in)

    slice.apply_translation(center[0:-1])

    # Rasterise and cast to a numpy array
    # The origin is set based on the minium XY bounding box of the part. Depending on the platform the user may
    slice_image = slice.rasterize(pitch=um_per_px * 10**-3, origin=[0, 0], resolution=[img_width, img_height])

    slice_image_arr = np.array(slice_image)

    return slice_image_arr


def shrink(image_in, shrink_size_in):
    """
    Reduces the shapes within the image by a discrete unit. Pretty interesting stuff. <3 cv2
    :param image_in:
    :param shrink_size_in:
    :return:
    """
    # https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
    erosion_size = shrink_size_in
    erosion_shape = cv2.MORPH_RECT
    element = cv2.getStructuringElement(erosion_shape, (2 * erosion_size + 1, 2 * erosion_size + 1),
                                       (erosion_size, erosion_size))
    return cv2.erode(image_in, element)


def fill_internal_holes(bitmap_img_in, color_in):
    """
    Will fill empty holes in a slice with a specific color
    :param bitmap_img_in:
    :param color_in:
    :return:
    """
    # Assuming sliceImage_arr is a 2D numpy array (True = filled, False = empty)
    bitmap_image = bitmap_img_in.astype(np.uint8)

    # Step 1: Create an empty mask with the correct size (height + 2, width + 2)
    mask = np.zeros((bitmap_image.shape[0] + 2, bitmap_image.shape[1] + 2), dtype=np.uint8)

    # Step 2: Flood-fill external regions (connected to the boundary) with 1
    # Use a flood-fill from all edges (external boundary)
    cv2.floodFill(bitmap_image, mask, (0, 0), 1)  # Top-left corner (0, 0)
    cv2.floodFill(bitmap_image, mask, (bitmap_image.shape[1] - 1, 0), 1)  # Top-right corner
    cv2.floodFill(bitmap_image, mask, (0, bitmap_image.shape[0] - 1), 1)  # Bottom-left corner
    cv2.floodFill(bitmap_image, mask, (bitmap_image.shape[1] - 1, bitmap_image.shape[0] - 1), 1)  # Bottom-right corner

    # Step 3: Now, the regions connected to the boundary are marked with 1 in the mask.
    # Any region with 0 in the mask corresponds to internal empty regions.

    # Step 4: Create an output image (color) where we assign color based on the classification
    output_image = np.zeros((bitmap_image.shape[0], bitmap_image.shape[1], 3), dtype=np.uint8)

    # Fill color for solid regions (True/1 regions)
    output_image[bitmap_image == 1] = [255, 255, 255]  # White (solid regions)

    # Fill color for external empty regions (connected to the boundary, mask == 1)
    output_image[mask[1:-1, 1:-1] == 1] = [0, 0, 0]  # Black (external empty regions)

    # Fill color for internal empty regions (where mask == 0 and bitmap_image == 0)
    output_image[(mask[1:-1, 1:-1] == 0) & (bitmap_image == 0)] = color_in

    return output_image


def change_colors(cv2_img_in, old_color_in, new_color_in):
    # Define the color to replace (e.g., blue color in RGB format)
    # For blue, let's say the region has the color (255, 0, 0) in BGR format
    old_color = np.array(old_color_in)  # Blue color in BGR
    new_color = np.array(new_color_in)  # Red color in BGR

    # Convert the image to a NumPy array (if it's not already)
    image = np.array(cv2_img_in)

    # Identify the regions where the color matches the old color
    # You can use a condition that checks if all three channels match
    mask = np.all(image == old_color, axis=-1)  # mask will be True where color matches

    # Change the color in those regions
    image[mask] = new_color  # Set the color in the masked regions

    return


def pil_show(cv2_img_in):
    Image.fromarray(cv2_img_in).show()


def convert_to_cv2(array_in):
    array_in = array_in.astype(np.uint8)
    array_in *= 255
    array_in = array_in.astype(np.uint8)
    return array_in


def get_cure_depth(exposure_time_in, max_cure_depth_in):
    """
    :param exposure_time_in: Exposure time in seconds
    :param max_cure_depth_in: Cure depth in millimeters
    :return:
    """
    delay_factor = 1
    cure_depths = 0.1371 * np.log(exposure_time_in + 0.00001) - 0.1015
    cure_depths[cure_depths < 0] = 0
    cure_depths[cure_depths > max_cure_depth_in] = max_cure_depth_in
    cure_depths = cure_depths[delay_factor:]
    cure_depths = np.append(cure_depths, cure_depths[-delay_factor])
    return cure_depths


def algorithm():
    global masked_slice
    max_cure_depth = 500
    layer_height = 50
    layer = 5
    exposure_time = 15
    slice_frequency = 1
    slice_count = exposure_time * slice_frequency

    slices = []
    max_layers = max_cure_depth / layer_height + layer
    blank = np.full((800, 1280), False)
    erosion_rate = 10  # pixels per second

    time_values = np.linspace(0, exposure_time, int(slice_count))

    cure_depths = get_cure_depth(time_values, max_cure_depth)

    # print(cure_depths)

    erosion_arr = np.floor(erosion_rate * time_values)

    layers = cure_depths / (layer_height * 10**-3)

    # print(layers)

    layers = layer - layers

    z_vals = layer * layer_height * 10**-3 - cure_depths

    # print(layers)

    layers[layers < 0] = 0

    layers = layers[layers < max_layers]

    z_vals[z_vals < 0] = 0

    z_vals = z_vals[z_vals < max_cure_depth]

    z_vals = z_vals

    print(z_vals)

    # print(layers)

    global_slice = get_slice(layer * layer_height * 10 ** -3)

    masked_slice = 0

    for i, z_val in enumerate(z_vals):
        current_slice = get_slice(z_val)
        # current_slice = self.convert_to_cv2(current_slice)

        # eroded_slice = self.erode(current_slice, int(erosion_arr[i]))

        # eroded_slice = self.convert_to_bitmap(eroded_slice)

        masked_slice = global_slice & current_slice

        # img = convert_to_cv2(masked_slice)

        # cv2.imwrite(r"C:\Users\Gene Felix\Downloads\\" + f"{i}.png", img)

        # slices.append(masked_slice)

        global_slice = current_slice

    pil_show(masked_slice)

algorithm()
