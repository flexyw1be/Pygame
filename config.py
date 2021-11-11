import pygame

TILE = 96
WIN_SIZE = pygame.Rect(0, 0, TILE * 16, TILE * 9)
FPS = 60

PLAYER_SIZE = (TILE, TILE)
PLAYER_SPEED = 8
JUMP_POWER = TILE // 3.5

# COLOR       R    G    B
GREEN = (0, 128, 0)
NOTGREEN = (32, 178, 170)

GRAVITY = 1

PLAYER_HP = 100

PLAYER_IDLE = 'data/platformChar_idle.png'
PLAYER_LEFT = 'data/platformChar_right.png'
PLAYER_JUMP = 'data/platformChar_jump.png'
COIN = 'data/hudCoin.png'
HEART = 'data/tile_0373.png'
BACKGROUND = 'data/back.png'
BULLET = 'data/bullet.png'
BULLET_LEFT = 'data/bullet_left.png'
BULLET_SPEED = 10
TURRET_BLOCKS = 'T'

BLOCKS = {
    'G': 'data/grassMid.png',
    'L': 'data/dirtHalf_left.png',
    'R': 'data/dirtHalf_right.png',
    'D': 'data/dirtMid.png',
    'S': 'data/tile_0573.png',
    'C': COIN,
    'T': 'data/turret.png'
}

HARD_BLOCKS = 'GDS'
SPIKE_BLOCKS = 'S'
COIN_BLOCKS = 'C'

MAP_0, MAP_1, MAP_2 = 'map_0.txt', 'map_1.txt', 'map_2.txt'
MAP_LIST = [MAP_0, MAP_1, MAP_2]
