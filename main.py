import pygame
from random import randint as ri

from config import *
from utility import *


class Block(pygame.sprite.Sprite):

    def __init__(self, image_path, coord):
        pygame.sprite.Sprite.__init__(self)

        self.image = image_load(image_path)
        self.rect = self.image.get_rect()
        self.rect.topleft = coord


class Coin(Block):

    def __init__(self, image_path, coord):
        Block.__init__(self, image_path, coord)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.vx, self.vy = 0, 0
        self.right_image = image_load(PLAYER_IDLE)
        self.left_image = image_load(PLAYER_LEFT)
        self.jump_image = image_load(PLAYER_JUMP)
        self.image = self.right_image

        self.rect = pygame.Rect((0, WIN_SIZE.height - TILE), PLAYER_SIZE)
        self.heart_image = image_load(HEART, (TILE // 2, TILE // 2))
        self.hp = PLAYER_HP

        self.on_ground = False

        self.money = 0

    def update(self, coins, hard_blocks, spike_blocks):
        keys = pygame.key.get_pressed()
        # y
        up = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]

        if up and self.on_ground:
            self.vy = -JUMP_POWER
            self.on_ground = False

        if not self.on_ground:
            self.vy += GRAVITY
        self.rect.y += self.vy

        collided_blocks = pygame.sprite.spritecollide(self, hard_blocks, False)
        if len(collided_blocks) == 0:
            self.on_ground = False
        for block in collided_blocks:
            if block in spike_blocks:
                self.hp -= 25
                if self.rect.x < block.rect.x:
                    self.rect.right = block.rect.left - TILE // 2
                else:
                    self.rect.left = block.rect.right + TILE // 2
            else:
                if self.vy > 0:
                    self.rect.bottom = block.rect.top
                    self.vy = 0
                    self.on_ground = True
                if self.vy < 0:
                    self.rect.top = block.rect.bottom
                    self.vy = 0

        # x
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if left and not right:
            self.vx = -PLAYER_SPEED
        elif right and not left:
            self.vx = PLAYER_SPEED
        else:
            self.vx = 0

        shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if shift and self.on_ground:
            self.vx *= 2
        if self.vx < 0:
            self.image = self.left_image
        if self.vx > 0:
            self.image = self.right_image
        self.rect.x += self.vx

        collided_blocks = pygame.sprite.spritecollide(self, hard_blocks, False)
        for block in collided_blocks:
            if block in spike_blocks:
                self.hp -= 25
                if self.vx > 0:
                    self.rect.right = block.rect.left - TILE // 2
                    self.vx = 0
                if self.vx < 0:
                    self.rect.left = block.rect.right + TILE // 2
                    self.vx = 0
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            if self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        if self.rect.y < 0:
            self.rect.y = WIN_SIZE.y
            self.vy = 0
        if self.rect.x < WIN_SIZE.left:
            self.rect.x = WIN_SIZE.left

        for coin in game.coins:
            if self.rect.colliderect(coin.rect):
                self.money += 1
                coin.kill()
        if self.rect.right >= WIN_SIZE.right:
            if len(game.coins) == 0:
                game.map = (MAP_LIST[(MAP_LIST.index(game.map) + 1) % 3])
                game.load_map()
                self.rect.x = 0
            else:
                self.rect.right = WIN_SIZE.right

    def get_money(self):
        return self.money


class Window:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIN_SIZE.width, WIN_SIZE.height))
        self.background = pygame.image.load(BACKGROUND)
        self.background = self.background.convert()
        self.background = pygame.transform.scale(self.background, (WIN_SIZE.width, WIN_SIZE.height))

        self.all_blocks = pygame.sprite.Group()
        self.hard_blocks = pygame.sprite.Group()
        self.spike_blocks = pygame.sprite.Group()
        self.player = Player()

        self.running = True

        self.clock = pygame.time.Clock()
        self.time = 0

        self.coins = pygame.sprite.Group()
        self.map = MAP_LIST[0]

    def load_map(self):
        self.player.money = 0
        self.all_blocks.empty()
        self.hard_blocks.empty()
        self.spike_blocks.empty()
        self.player.add(self.all_blocks)
        with open(self.map, 'r', encoding='utf-8') as file:
            for y, line in enumerate(file):
                for x, letter in enumerate(line):
                    coord = x * TILE, y * TILE
                    if letter in BLOCKS.keys():
                        block = Block(BLOCKS[letter], coord)
                        block.add(self.all_blocks)
                        if letter in HARD_BLOCKS:
                            block.add(self.hard_blocks)
                        if letter in SPIKE_BLOCKS:
                            block.add(self.spike_blocks)
                        elif letter in COIN_BLOCKS:
                            block.add(self.coins)

    def run(self):
        self.load_map()
        self.running = True
        while self.running:
            # события
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # действия
            ms = self.clock.tick_busy_loop(FPS)
            self.time += ms / 1000
            pygame.display.set_caption(f'{self.time:.2f} сек. {self.player.hp} ' \
                                       f'Деньжата {self.player.get_money()}')

            self.player.update(self.coins, self.hard_blocks, self.spike_blocks)

            # отрисовка
            self.screen.blit(self.background, (0, 0))

            self.all_blocks.draw(self.screen)

            pygame.display.flip()


if __name__ == '__main__':
    game = Window()
    game.run()
