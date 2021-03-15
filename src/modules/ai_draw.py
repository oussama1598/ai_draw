import operator
from collections import defaultdict

import cv2
import kdtree
import numpy as np
from sklearn.cluster import KMeans

from src.helpers.image import process_image, resize_image
from src.modules.commands_executer import CommandsExecuter


def normalize_vector(x):
    return np.array(x) / np.linalg.norm(np.array(x))


def bgr_to_hex(color):
    b, g, r = color

    return "#{0:02x}{1:02x}{2:02x}".format(int(r), int(g), int(b))


class AIDraw:
    def __init__(self, image_path, **kwargs):
        self.image_path = image_path

        # screen size
        self.padding: tuple = kwargs.get('padding', (0, 0))
        self.canvas_width: int = kwargs.get('canvas_width')
        self.canvas_height: int = kwargs.get('canvas_height')

        # Config
        self.blur = kwargs.get('blur', 0)
        self.number_of_colors = kwargs.get('number_of_colors', 3)
        self.logger = kwargs.get('logger', print)

        # Load image
        self.image = self._load_image()

        # internal variables
        self.commands = CommandsExecuter(
            logger=self.logger
        )
        self.hash_set = set()
        self.KD_tree = None

        # Initialize directions for momentum when creating path
        self.maps = {0: (1, 1), 1: (1, 0), 2: (1, -1), 3: (0, -1), 4: (0, 1), 5: (-1, -1), 6: (-1, 0), 7: (-1, 1)}
        self.momentum = 1

    def _load_image(self):
        return cv2.imread(self.image_path)

    def _translate(self, x, y):
        return {
            'x': x + self.padding[0],
            'y': y + self.padding[1]
        }

    def _get_direction(self, point):
        current_delta = self.maps[self.momentum]
        deltas = list(filter(
            lambda moment: tuple(map(operator.add, point, moment)) in self.hash_set,
            self.maps.values()
        ))

        deltas.sort(key=lambda x: np.dot(
            normalize_vector(x), normalize_vector(current_delta)
        ), reverse=True)

        if len(deltas) > 0:
            self.momentum = [key for key, value in self.maps.items() if value == deltas[0]][0]

            return deltas[0]

        return None

    def _create_path(self):
        # Run the algorithm
        total_points = len(self.hash_set)
        current_position = self.KD_tree.search_nn([0, 0])[0].data

        # Remove the point from the data we have
        self.KD_tree = self.KD_tree.remove(current_position)
        self.hash_set.remove(tuple(current_position))

        self.commands.add_command({
            'name': 'mouse',
            'pressed': False
        })
        self.commands.add_command({
            'name': 'move',
            **self._translate(*current_position)
        })

        self.commands.add_command({
            'name': 'mouse',
            'pressed': True
        })
        self.commands.add_command({
            'name': 'move',
            **self._translate(*current_position)
        })

        while len(self.hash_set) > 0:
            previous_direction = self.momentum
            direction = self._get_direction(current_position)

            if direction is not None:
                current_position = list(map(
                    operator.add, current_position, direction
                ))

                if previous_direction == self.momentum and self.commands.get_last_command()['name'] == 'move':
                    self.commands.pop_last_command()

                self.commands.add_command({
                    'name': 'move',
                    **self._translate(*current_position)
                })
            else:
                self.commands.add_command({
                    'name': 'mouse',
                    'pressed': False
                })

                current_position = self.KD_tree.search_nn(current_position)[0].data

                self.commands.add_command({
                    'name': 'move',
                    **self._translate(*current_position)
                })

                self.commands.add_command({
                    'name': 'mouse',
                    'pressed': True
                })
                self.commands.add_command({
                    'name': 'move',
                    **self._translate(*current_position)
                })

            self.KD_tree = self.KD_tree.remove(current_position)
            self.hash_set.remove(tuple(current_position))

            self.logger(f'Generating points {round((total_points - len(self.hash_set)) / total_points, 2) * 100}%')

    def generate_outline_commands(self):
        image = process_image(
            self.image,
            size=(self.canvas_width, self.canvas_height),
            blur=self.blur
        )

        image = np.swapaxes(image, 0, 1)

        black_points_indices = np.argwhere(image == 0).tolist()
        index_tuples = map(tuple, black_points_indices)

        self.hash_set = set(index_tuples)
        self.KD_tree = kdtree.create(black_points_indices)

        self._create_path()

    def generate_coloring_commands(self):
        new_size = (self.canvas_width, self.canvas_height)
        image = resize_image(self.image, size=new_size)
        image = np.swapaxes(image, 0, 1)

        sum_rgb_for_each_pixel = np.sum(image, axis=2) / 3
        colored_pixels_indices = np.argwhere(sum_rgb_for_each_pixel <= 256)
        colored_pixels_indices = np.swapaxes(colored_pixels_indices, 0, 1)

        BGR_colors = image[colored_pixels_indices[0], colored_pixels_indices[1], :]
        k_means = KMeans(n_clusters=self.number_of_colors).fit(BGR_colors)

        colored_pixels_indices = np.swapaxes(colored_pixels_indices, 0, 1).tolist()
        clusters = [[] for _ in range(len(k_means.cluster_centers_))]

        for label, point in zip(k_means.labels_, colored_pixels_indices):
            clusters[label].append(point)

        for (i, color) in enumerate(k_means.cluster_centers_):
            print(f'Generating for color {i + 1}')

            self.commands.add_command({
                'name': 'pen_color',
                'color': bgr_to_hex(color)
            })

            points_indices = clusters[i]
            index_tuples = map(tuple, points_indices)

            self.hash_set = set(index_tuples)
            self.KD_tree = kdtree.create(points_indices)

            self._create_path()
