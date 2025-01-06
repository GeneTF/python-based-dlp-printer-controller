import trimesh
import numpy as np
import cv2
import MainConstants
import io
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
import pyslm
import math

import Messaging


class Slicer:
    # The slicer cannot obtain the top most layer of a given stl model
    slice_tolerance = 0.99
    initial_slice_tolerance = 0.01

    # Constants to offset image if it is not directly are the center of build plate
    offset_x = 0
    offset_y = -2  # -2 for small one

    def __init__(self):
        super().__init__()

        self.line_color = (255, 255, 255)
        self.line_width = 1

        self.layer_height = MainConstants.DEFAULT_LAYER_HEIGHT

        self.img_width = MainConstants.DEFAULT_PROJECTOR_X
        self.img_height = MainConstants.DEFAULT_PROJECTOR_Y

        self.um_per_px = MainConstants.DEFAULT_UM_PER_PX

        # Vector to translate all objects to the center
        self.center = [0, 0, 0]

    def preview_all_meshes(self, mesh_list_in):
        if len(mesh_list_in) > 0:
            combined = trimesh.util.concatenate(mesh_list_in)
            combined.show()

            self.set_center_vector(mesh_list_in)

            try:
                for i in np.arange(0, 10, 1):
                    img = self.slice(i, mesh_list_in)
                    img.save(r"C:\Users\Gene Felix\Downloads\\" + f"{i}.png")
            except Exception as ex:
                Messaging.Messenger.generic_error(ex)

    def set_center_vector(self, mesh_list_in):
        combined = trimesh.util.concatenate(mesh_list_in)

        print_width = self.img_width * (self.um_per_px * 10**-3)  # Print width in mm
        print_height = self.img_height * (self.um_per_px * 10**-3)  # Print height in mm

        print_area = np.array([print_width, print_height])
        print_center = print_area / 2

        centroid_xy = combined.centroid[0:2]

        # print(centroid_xy)

        center_vector = print_center - centroid_xy  # Calculates center vector in mm

        center_vector += [self.offset_x, self.offset_y]

        self.center = list(center_vector) + [0]

    def get_max_layers(self, mesh_list_in):
        combined = trimesh.util.concatenate(mesh_list_in)
        bounds = combined.bounds
        dz = bounds[1][2] - bounds[0][2]
        tolerance = 0.01
        rounded_up = math.ceil(dz * 100) / 100
        rounded_down = math.floor(dz * 100) / 100

        if rounded_up - dz < tolerance:
            dz = rounded_up
        else:
            dz = rounded_down


        print("dz:", dz)
        return dz / (self.layer_height * 10**-3)

    def convert_to_pix(self, bitmap_in):
        image = Image.fromarray(bitmap_in)

        q_img = ImageQt(image)

        pix = QPixmap.fromImage(q_img)

        return pix

    def slice(self, layer_in, mesh_list_in):
        mesh = trimesh.util.concatenate(mesh_list_in)

        solidPart = pyslm.Part('myPart')
        solidPart.setGeometry(mesh)
        solidPart.dropToPlatform()

        z_val = self.initial_slice_tolerance if layer_in == 0 else layer_in * self.layer_height * self.slice_tolerance * 10 ** -3

        slice = solidPart.getTrimeshSlice(z_val)

        slice.apply_translation(self.center[0:-1])

        slice_bitmap = slice.rasterize(pitch=self.um_per_px * 10**-3,
                                     origin=[0, 0],
                                     resolution=[self.img_width, self.img_height])
        slice_bitmap = np.array(slice_bitmap)

        return slice_bitmap

    def get_cure_depth(self, exposure_time_in, max_cure_depth_in):
        """
        :param exposure_time_in: Exposure time in seconds
        :param max_cure_depth_in: Cure depth in microns
        :return:
        """
        delay_factor = 1  # By index
        cure_depths = 0.1371 * np.log(exposure_time_in + 0.00001) - 0.1015
        cure_depths[cure_depths < 0] = 0
        cure_depths[cure_depths > max_cure_depth_in] = max_cure_depth_in
        cure_depths = cure_depths[delay_factor:]
        cure_depths = np.append(cure_depths, cure_depths[-delay_factor])
        return cure_depths

    def erode(self, image_in, shrink_size_in):
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
        image_out = cv2.erode(image_in, element)
        return image_out

    def convert_to_cv2(self, array_in):
        array_in = array_in.astype(np.uint8)
        array_in *= 255
        array_in = array_in.astype(np.uint8)
        return array_in

    def convert_to_bitmap(self, array_in):
        array_in = array_in / 255
        array_in = array_in.astype(np.uint8)
        array_in = array_in.astype(bool)
        return array_in

    def get_slices(self, layer_in, mesh_list_in, max_cure_depth_in, slice_count_in, exposure_time_in):
        slices = []
        max_layers = max_cure_depth_in / self.layer_height + layer_in
        blank = np.full((800, 1280), False)
        erosion_rate = 10  # pixels per second
        minimum_curing_time = 5  # in seconds

        time_values = np.linspace(0, exposure_time_in, int(slice_count_in))

        cure_depths = self.get_cure_depth(time_values, max_cure_depth_in)

        # print(cure_depths)

        erosion_arr = np.floor(erosion_rate * time_values)

        layers = cure_depths / (self.layer_height * 10**-3)

        # print(layers)

        layers = layer_in - layers

        # print(layers)

        layers[layers < 0] = 0

        layers = layers[layers < max_layers]

        # print(layers)

        initial_slice = self.slice(layer_in, mesh_list_in)

        global_slice = self.slice(layer_in, mesh_list_in)

        slicing_algorithm = 2

        if slicing_algorithm == 0:
            try:
                for i, layer in enumerate(layers):
                    current_slice = self.slice(layer, mesh_list_in)
                    # current_slice = self.convert_to_cv2(current_slice)

                    # eroded_slice = self.erode(current_slice, int(erosion_arr[i]))

                    # eroded_slice = self.convert_to_bitmap(eroded_slice)

                    masked_slice = global_slice & current_slice

                    slices.append(self.convert_to_pix(masked_slice))

                    global_slice = current_slice

            except AttributeError:
                print("Attribute Error")
            except Exception as ex:
                Messaging.Messenger.print_error(ex)

        elif slicing_algorithm == 1:
            try:
                masked_slice = 0

                for layer in layers:
                    current_slice = self.slice(layer, mesh_list_in)

                    masked_slice = global_slice & current_slice

                    global_slice = masked_slice

                slices += [self.convert_to_pix(initial_slice)] * len(time_values[time_values <= minimum_curing_time])

                slices += [self.convert_to_pix(masked_slice)] * len(time_values[time_values > minimum_curing_time])

            except Exception as ex:
                Messaging.Messenger.print_error(ex)

        else:
            try:
                print(type(slice_count_in))
                slices = [self.convert_to_pix(global_slice)] * int(slice_count_in)
            except Exception as ex:
                Messaging.Messenger.print_error(ex)

        return slices
