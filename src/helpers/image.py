import math

import cv2


def get_scaled_dimensions(old_size, new_size):
    width, height, _ = old_size
    new_width, new_height = new_size
    ratio = width / height

    if ratio > 1:
        new_width = int(new_height * ratio)
    else:
        new_height = int(new_width * ratio)

    if new_width > new_size[0]:
        ratio = new_size[0] / new_width

        new_height *= ratio
        new_width *= ratio

    if new_height > new_size[1]:
        ratio = new_size[1] / new_height

        new_height *= ratio
        new_width *= ratio

    return int(new_width), int(new_height)


def blur_image(image, blur=0):
    if blur == 0:
        return image

    kernels = {
        1: (3, 3),
        2: (5, 5),
        3: (7, 7),
        4: (9, 9),
        5: (11, 11),
        6: (13, 13),
        7: (15, 15),
        8: (17, 17),
        9: (19, 19),
        10: (21, 21)
    }

    return cv2.GaussianBlur(image, kernels[blur], 0)


def apply_canny(image, canny_threshold):
    return cv2.Canny(image, *canny_threshold)


def resize_image(image, size=(500, 500)):
    new_dimensions = get_scaled_dimensions(image.shape, size)

    print(new_dimensions)

    return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)


def process_image(image, size=(500, 500), blur=0, canny_threshold=(25, 45)):
    new_dimensions = get_scaled_dimensions(image.shape, size)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur image
    gray_image = blur_image(gray_image, blur)

    # Canny
    gray_image = apply_canny(gray_image, canny_threshold)

    canny = cv2.resize(gray_image, new_dimensions, interpolation=cv2.INTER_AREA)
    _, res = cv2.threshold(canny, 50, 255, cv2.THRESH_BINARY_INV)

    return res
