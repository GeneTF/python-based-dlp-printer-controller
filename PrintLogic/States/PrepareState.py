import time
import STLSelectorGUI

from PyQt6.QtCore import QObject


class Prepare(QObject):

    def __init__(self):
        super().__init__()
        self.slices = []  # List of prepare bitmap images for exposure
        self.max_cure_depth = 500  # In um

    def run(self, progress_in, stl_selector_in, ink_number_in, layer_in, slice_count_in, exposure_time_in):
        progress_in.emit("Preparing slices!\n")

        stl_selector_in = stl_selector_in  # type: STLSelectorGUI.STLSelector

        slices = stl_selector_in.get_slices(ink_number_in, layer_in, self.max_cure_depth, slice_count_in,
                                            exposure_time_in)

        return slices
