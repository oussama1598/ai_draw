import os
import random
import string
import tempfile
import time

import cv2
from dearpygui import simple, core

from src.helpers.image import process_image
from src.modules.ai_draw import AIDraw


def get_random_string(length):
    letters = string.ascii_lowercase

    return ''.join(random.choice(letters) for _ in range(length))


class Gui:
    def __init__(self):
        self.core = core
        self.simple = simple

        self.file_path = os.path.join(os.getcwd(), 'images/img.jpg')
        self.blur_level = 2
        self.canny_min = 25
        self.canny_max = 45

        self.core.set_main_window_size(800, 800)

        self._create_file_selector_window()

    def _preview_image(self):
        _, extension = os.path.splitext(self.file_path)
        temp_file_path = f'{os.path.join(tempfile.gettempdir(), get_random_string(16))}{extension}'

        image = cv2.imread(self.file_path)
        image = process_image(image, size=(500, 500), blur=self.blur_level,
                              canny_threshold=(self.canny_min, self.canny_max))

        cv2.imwrite(temp_file_path, image)

        self.core.draw_image('Preview', temp_file_path, [0, 0], [500, 500])

    def _image_selected(self, _, data):
        self.file_path = os.path.join(data[0], data[1])

        self._preview_image()

    def _open_image_selector(self):
        self.core.open_file_dialog(extensions='.jpeg,.png,.jpg', callback=self._image_selected)

    def _blur_level_changed(self, _):
        self.blur_level = self.core.get_value(_)

        self._preview_image()

    def _canny_min_changed(self, _):
        self.canny_min = self.core.get_value(_)

        self._preview_image()

    def _canny_max_changed(self, _):
        self.canny_max = self.core.get_value(_)

        self._preview_image()

    def _start_drawing(self):
        self.simple.show_logger()

        ai_draw = AIDraw(
            self.file_path,
            padding=(150, 150),
            canvas_width=800,
            canvas_height=800,
            blur=self.blur_level,
            logger=self.core.log_debug
        )

        ai_draw.generate_outline_commands()

        self.core.log_debug('Waiting 5 seconds before starting')
        time.sleep(5)

        ai_draw.commands.run()

    def _create_file_selector_window(self):
        with self.simple.window(
                'Image Settings',
                width=500,
                height=750,
                x_pos=int((800 - 500) / 2),
                y_pos=int((800 - 750) / 2),
                no_move=True,
                no_close=True,
                no_collapse=True,
                no_scrollbar=True,
                no_resize=True
        ):
            self.core.add_drawing('Preview', width=500, height=500)
            self._preview_image()

            self.core.add_spacing(count=2)
            self.core.add_dummy(width=35)
            self.core.add_same_line()
            self.core.add_button('Change Image', width=400, callback=self._open_image_selector)

            self.core.add_spacing(count=2)
            self.core.add_separator()
            self.core.add_spacing(count=2)

            self.core.add_indent()
            self.core.add_text('Blur Level: ')
            self.core.add_same_line()
            self.core.add_slider_int(
                'blur_level',
                label='',
                min_value=0,
                max_value=10,
                default_value=3,
                callback=self._blur_level_changed
            )
            self.core.unindent()

            self.core.add_spacing(count=2)
            self.core.add_separator()
            self.core.add_spacing(count=2)

            self.core.add_indent()
            self.core.add_text('Canny Min: ')
            self.core.add_same_line()
            self.core.add_slider_int(
                'canny_min',
                label='',
                min_value=0,
                max_value=255,
                default_value=self.canny_min,
                callback=self._canny_min_changed
            )
            self.core.add_text('Canny Max: ')
            self.core.add_same_line()
            self.core.add_slider_int(
                'canny_max',
                label='',
                min_value=0,
                max_value=255,
                default_value=self.canny_max,
                callback=self._canny_max_changed
            )
            self.core.unindent()

            self.core.add_spacing(count=2)
            self.core.add_separator()
            self.core.add_spacing(count=2)

            self.core.add_dummy(width=35)
            self.core.add_same_line()
            self.core.add_button('Draw', width=400, callback=self._start_drawing)

    def run(self):
        self.core.start_dearpygui()
