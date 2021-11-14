import pygame
from random import randint as ri
from random import choice

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


class Turret:
    def __init__(self, image_path, coord):
        Block.__init__(self, image_path, coord)

    def update(self):
        pass


class Camera(pygame.Rect):
    def __init__(self, x=0, y=0):
        pygame.Rect.__init__(self, (x, y), WIN_SIZE.size)

    def update(self, player_x, player_y):
        if not player_x < WIN_SIZE.size[0] // 2 and not player_x > MAP_X - WIN_SIZE.size[0] // 2:
            self.centerx = player_x
        if not player_y < WIN_SIZE.size[1] // 2 and not player_y > MAP_Y - WIN_SIZE.size[1] // 2:
            self.centery = player_y

    def draw(self, screen, objects):
        for obj in objects:
            screen.blit(obj.image, (obj.rect.x - self.x, obj.rect.y - self.y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, coord, vx, vy=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = image_load(BULLET)
        print(vx)
        self.rect = pygame.Rect(coord, PLAYER_SIZE)
        self.vx, self.vy = vx, vy
        if self.vx > 0:
            self.image = image_load(BULLET, (TILE // 2, TILE // 2))
        else:
            self.image = image_load(BULLET_LEFT, (TILE // 2, TILE // 2))

    def update(self):
        self.rect.x += self.vx
        self.rect.y -= self.vy
        for i in game.hard_blocks:
            if self.rect.colliderect(i.rect):
                self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.time_spike = 0
        self.vx, self.vy = 0, 0
        self.right_image = image_load(PLAYER_IDLE)
        self.left_image = image_load(PLAYER_LEFT)
        self.jump_image = image_load(PLAYER_JUMP)
        self.image = self.right_image

        self.rect = pygame.Rect((0, 0), PLAYER_SIZE)
        self.hp = PLAYER_HP
        self.clock = pygame.time.Clock()
        self.time = 0

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
        if shift:
            self.vx *= 2
        if self.vx < 0:
            self.image = self.left_image
        if self.vx > 0:
            self.image = self.right_image
        self.rect.x += self.vx
        x = keys[pygame.K_x]
        if x:
            self.shoot()

        collided_blocks = pygame.sprite.spritecollide(self, hard_blocks, False)
        for block in collided_blocks:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            if self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0
        if self.rect.y <= 0:
            self.rect.y = 0
        print(self.rect.x)
        if self.rect.right >= MAP_X:
            self.rect.right = MAP_X
        if self.rect.left <= 0:
            self.rect.left = 0
        collided_spikes = pygame.sprite.spritecollide(self, spike_blocks, False)
        for block in collided_spikes:
            ms = self.clock.tick_busy_loop(FPS)
            self.time += ms / 1000
            if self.time_spike + 1 <= self.time:
                self.time_spike = self.time
                self.hp -= SPIKE_DAMAGE
        for coin in game.coins:
            if self.rect.colliderect(coin.rect):
                self.money += 1
                coin.kill()

    def get_money(self):
        return self.money

    def shoot(self):
        if not self.time:
            self.time = pygame.time.get_ticks()
        second_time = pygame.time.get_ticks()
        if second_time - self.time > 200:
            self.time = second_time
            vx = 20
            bullet = Bullet((self.rect.centerx, self.rect.centery), vx)
            bullet.add(game.bullets)
            bullet.add(game.all_blocks)


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
        self.turret_blocks = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player()
        self.camera = Camera()
        self.camera.update(self.player.rect.centerx, self.player.rect.centery)

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
        self.turret_blocks.empty()
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
                        if letter in TURRET_BLOCKS:
                            block.add(self.turret_blocks)
                            Turret(BLOCKS[letter], coord)

                        elif letter in COIN_BLOCKS:
                            block.add(self.coins)
                    if letter == 'P':
                        self.player.rect = pygame.Rect(coord, PLAYER_SIZE)

    def run(self):
        self.load_map()
        self.running = True
        time = pygame.time.get_ticks()
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            ms = self.clock.tick_busy_loop(FPS)
            self.time += ms / 1000
            pygame.display.set_caption(f'{self.time:.2f} сек. {self.player.hp} ' \
                                       f'Деньжата {self.player.get_money()}')
            self.player.update(self.coins, self.hard_blocks, self.spike_blocks)

            self.screen.blit(self.background, (0, 0))
            second_time = pygame.time.get_ticks()
            if second_time - time > 1000:
                time = second_time
                for i in self.turret_blocks:
                    bullet = Bullet((i.rect.centerx, i.rect.centery), choice([-BULLET_SPEED, BULLET_SPEED]))
                    bullet.add(self.bullets)
                    bullet.add(self.all_blocks)
            self.bullets.update()

            # self.all_blocks.draw(self.screen)
            self.camera.update(self.player.rect.centerx, self.player.rect.centery)
            self.camera.draw(self.screen, self.all_blocks)

            pygame.display.flip()


if __name__ == '__main__':
    game = Window()
    game.run()
