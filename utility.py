from random import randint as ri
import pygame

from config import *


def get_random_color():
    return [ri(0, 255) for _ in range(3)]
    # color = []
    # for i in range(3):
    #     color.append(ri(0, 255))
    # return color


def image_load(path, size=(TILE, TILE), alpha=True):
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, size)
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image
