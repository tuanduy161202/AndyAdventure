import pygame
import math
import random
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 1280
MAX_WIDTH = 1280*5
SCREEN_HEIGHT = 640
V_JUMP = -40
GRAVITY = 5
P_BULLET_DELAY = 10
E_BULLET_DELAY = 50

def rescaleSprite(surface, scale):
    w, h = surface.get_size()
    new_h = SCREEN_HEIGHT*scale
    new_w = w * new_h // h
    return pygame.transform.scale(surface, (new_w, new_h))

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/Items/coin1.png')
        self.image = rescaleSprite(self.image, 0.1)
        self.rect = self.image.get_rect(topleft = pos)
        self.count = 0
        self.score = 1
        self.addbullet = 0
    def update(self):
        self.count = (self.count + 1)%8 + 1
        self.image = pygame.image.load(f'Sprites/Items/coin{self.count}.png')
        self.image = rescaleSprite(self.image, 0.1)
    def draw(self, surface):
        self.image.render(surface, self.rect)
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)
class AddBullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/Bullets/bullet.png')
        self.image = rescaleSprite(self.image, 0.05)
        self.image = pygame.transform.rotate(self.image, 45)
        self.rect = self.image.get_rect(topleft = pos)
        self.count = 1
        self.score = 0
        self.addbullet = 2
    def update(self):
        self.count = (self.count + 1) % 2
        if self.count == 0:
            self.rect.move_ip(0, -1)
        else:
            self.rect.move_ip(0, 1)
    def draw(self, surface):
        self.image.render(surface, self.rect)
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direct):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/Bullets/bullet.png')
        self.image = rescaleSprite(self.image, 0.02)
        self.rect = self.image.get_rect(topleft = pos)
        self.damage = 10
        self.velocity = 15
        self.direct = direct
    def update(self):
        d = math.sqrt(self.direct[0]**2 + self.direct[1]**2)
        self.rect.move_ip(int(self.direct[0]*self.velocity / d), int(self.direct[1]*self.velocity / d))
        if self.rect.left <0 or self.rect.right > SCREEN_WIDTH or self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/Character/player.png')
        self.image = rescaleSprite(self.image, 0.15)
        self.bottom_distance = 40
        self.rect = pygame.Rect(pos[0], pos[1], self.image.get_size()[0], self.image.get_size()[1]+self.bottom_distance)
        self.isJump = False
        self.vJump = V_JUMP
        self.direct = (1, 0)
        self.bulletCounter = 0
        self.bottom_limit = SCREEN_HEIGHT
        self.isFall = False
        self.num_bullets = 1
        self.delta_angle = 15
        self.hp = 100
        
    def update(self, pressed_keys):
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(8, 0)
            self.direct = (1, 0)
        elif pressed_keys[K_LEFT]:
            self.rect.move_ip(-8, 0)
            self.direct = (-1, 0)
        if (not self.isJump) and (not self.isFall) and pressed_keys[K_UP]:
            self.isJump = True
            self.vJump = V_JUMP
        if (not self.isJump) and self.rect.bottom  - self.bottom_distance < SCREEN_HEIGHT:
            self.isFall = True
            self.rect.move_ip(0, self.vJump)
            self.vJump += GRAVITY
        if self.isJump:
            if self.vJump >= 0:
                self.isFall = True
            self.rect.move_ip(0, self.vJump)
            self.vJump += GRAVITY
        if self.isFall:
            self.bottom_limit = SCREEN_HEIGHT
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom - self.bottom_distance >= self.bottom_limit:
            self.rect.bottom = self.bottom_limit + self.bottom_distance
            self.vJump = 0
            self.isJump = False
            self.isFall = False
    def fall(self, land):
        if self.isFall and land.rect.top <= self.rect.bottom:
            self.bottom_limit = land.rect.top
            self.rect.bottom = self.bottom_limit + self.bottom_distance
            self.isJump = False
            self.isFall = False
            self.vJump = 0
    def fire(self):
        self.bulletCounter = (self.bulletCounter + 1) % P_BULLET_DELAY
        if self.bulletCounter == 0:
            pos = (self.rect.left + self.rect.right)//2, (self.rect.top + self.rect.bottom - self.bottom_distance) // 2
            bullets = pygame.sprite.Group()
            b = Bullet(pos, self.direct)
            bullets.add(b)
            for i in range (1, (self.num_bullets+1) // 2):
                b = Bullet(pos, (self.direct[0], self.direct[0]*math.tan(self.delta_angle/180*math.pi * i)))
                bullets.add(b)
                b = Bullet(pos, (self.direct[0], -self.direct[0]*math.tan(self.delta_angle/180*math.pi * i)))
                bullets.add(b)
            return bullets
        return None
    def hurted(self, dam):
        self.hp -= dam
        if self.hp <= 0:
            pass
    def upgrade(self, addbullet):
        self.num_bullets += addbullet
        if self.num_bullets > 5:
            self.num_bullets = 5
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/Monsters/enemy.png')
        self.image = rescaleSprite(self.image, 0.15)
        self.bottom_distance = 40
        self.rect = pygame.Rect(pos[0], pos[1], self.image.get_size()[0], self.image.get_size()[1]+self.bottom_distance)
        self.isJump = False
        self.vJump = V_JUMP
        self.direct = (1, 0)
        self.bulletCounter = 0
        self.bottom_limit = SCREEN_HEIGHT
        self.isFall = False
        self.hp = 30
        self.isLeft = True
        
    def update(self, player_rect):
        choice = random.randint(0, 4)
        if choice >= 3:
            if player_rect.left - self.rect.left > 0:
                choice = 0
            elif player_rect.left - self.rect.left < 0:
                choice = 1
            elif (player_rect.top - self.rect.top < 0):
                choice = 2
        if choice == 0:
            self.rect.move_ip(3, 0)
            self.direct = (1, 0)
            
        elif choice == 1:
            self.rect.move_ip(-3, 0)
            self.direct = (-1, 0)
        if (self.direct[0] == 1 and self.isLeft) or (self.direct[0] == -1 and not self.isLeft):
            self.image = pygame.transform.flip(self.image, True, False)
            self.isLeft = not self.isLeft
        if (not self.isJump) and choice == 2:
            self.isJump = True
            self.vJump = V_JUMP
        if (not self.isJump) and self.rect.bottom  - self.bottom_distance < SCREEN_HEIGHT:
            self.isFall = True
            self.rect.move_ip(0, self.vJump)
            self.vJump += GRAVITY
        if self.isJump:
            if self.vJump >= 0:
                self.isFall = True
            self.rect.move_ip(0, self.vJump)
            self.vJump += GRAVITY
        if self.isFall:
            self.bottom_limit = SCREEN_HEIGHT
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom - self.bottom_distance >= self.bottom_limit:
            self.rect.bottom = self.bottom_limit + self.bottom_distance
            self.isJump = False
            self.isFall = False
    def fall(self, land):
        if self.isFall and land.rect.top <= self.rect.bottom:
            self.bottom_limit = land.rect.top
            self.rect.bottom = self.bottom_limit + self.bottom_distance
            self.isJump = False
            self.isFall = False
            self.vJump = 0
    def fire(self):
        self.bulletCounter = (self.bulletCounter + 1) % E_BULLET_DELAY
        if self.bulletCounter == 0:
            pos = (self.rect.left + self.rect.right)//2, (self.rect.top + self.rect.bottom - self.bottom_distance) // 2
            # pos = self.rect.left, self.rect.top
            if random.randint(0, 2) == 1:
                b = Bullet(pos, self.direct)
                return b
        return None
    def hurted(self, dam):
        self.hp -= dam
        if self.hp <= 0:
            self.kill()
            if random.randint(0, 10) == 9:
                return AddBullet((self.rect.left, self.rect.top))
            else:
                return Coin((self.rect.left, self.rect.top))
        return None
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/Monsters/enemy.png')
        self.image = rescaleSprite(self.image, 0.6)
        self.bottom_distance = 40
        self.rect = pygame.Rect(pos[0], pos[1], self.image.get_size()[0], self.image.get_size()[1]+self.bottom_distance)
        self.isJump = False
        self.vJump = V_JUMP*1.5
        self.direct = (1, 0)
        self.bulletCounter = 0
        self.bottom_limit = SCREEN_HEIGHT
        self.isFall = False
        self.hp = 1000
        self.isLeft = True
        self.delta_angle = 30
        self.num_bullets = 3
        
    def update(self, player_rect):
        choice = random.randint(0, 2)
        if player_rect.left - self.rect.left > 0:
            self.rect.move_ip(3, 0)
            self.direct = (1, 0)
            
        elif player_rect.left - self.rect.left < 0:
            self.rect.move_ip(-3, 0)
            self.direct = (-1, 0)
            
        if (self.direct[0] == 1 and self.isLeft) or (self.direct[0] == -1 and not self.isLeft):
            self.image = pygame.transform.flip(self.image, True, False)
            self.isLeft = not self.isLeft
            
        if (not self.isJump) and choice == 1:
            self.isJump = True
            self.vJump = V_JUMP
        if (not self.isJump) and self.rect.bottom  - self.bottom_distance < SCREEN_HEIGHT:
            self.isFall = True
            self.rect.move_ip(0, self.vJump)
            self.vJump += GRAVITY
        if self.isJump:
            if self.vJump >= 0:
                self.isFall = True
            self.rect.move_ip(0, self.vJump)
            self.vJump += GRAVITY
        if self.isFall:
            self.bottom_limit = SCREEN_HEIGHT
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom - self.bottom_distance >= self.bottom_limit:
            self.rect.bottom = self.bottom_limit + self.bottom_distance
            self.isJump = False
            self.isFall = False
    def fall(self, land):
        if self.isFall and land.rect.top <= self.rect.bottom:
            self.bottom_limit = land.rect.top
            self.rect.bottom = self.bottom_limit + self.bottom_distance
            self.isJump = False
            self.isFall = False
            self.vJump = 0
    def fire(self):
        self.bulletCounter = (self.bulletCounter + 1) % 30
        if self.bulletCounter == 0:
            pos = (self.rect.left + self.rect.right)//2, (self.rect.top + self.rect.bottom - self.bottom_distance) // 2
            bullets = pygame.sprite.Group()
            b = Bullet(pos, self.direct)
            bullets.add(b)
            for i in range (1, (self.num_bullets+1) // 2):
                b = Bullet(pos, (self.direct[0], self.direct[0]*math.tan(self.delta_angle/180*math.pi * i)))
                bullets.add(b)
                b = Bullet(pos, (self.direct[0], -self.direct[0]*math.tan(self.delta_angle/180*math.pi * i)))
                bullets.add(b)
            return bullets
        return None
    def hurted(self, dam):
        self.hp -= dam
        if self.hp <= 0:
            self.kill()
            if random.randint(0, 10) == 9:
                return AddBullet((self.rect.left, self.rect.top))
            else:
                return Coin((self.rect.left, self.rect.top))
        return None
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)

class Ladder(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.color = color
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)

class Boundary(pygame.sprite.Sprite):
    def __init__(self, pos, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 0, 255))
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
    def trans_screen(self, dx):
        self.rect.move_ip(-dx, 0)
        
class Score(pygame.sprite.Sprite):
    def __init__(self, sprite_img, width, height, pos):
        self.score = 0
        width = int(width)
        height = int(height)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.W = width
        self.H = height
        self.font = pygame.font.SysFont("Arial", height)
        self.color = (255, 255, 255)
        self.icon = pygame.image.load(sprite_img)
        self.icon = rescaleSprite(self.icon, height / SCREEN_HEIGHT)
        self.textSurf = self.font.render('x0', 1, self.color)
    def update(self):
        self.textSurf = self.font.render(f'x{self.score}', 1, self.color)
        self.image.fill((0, 0, 0))
        self.image.blit(self.icon, [0, 0])
        self.image.blit(self.textSurf, [self.icon.get_width()+1, 0])
class PlayerHealth(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.height = int(0.09*SCREEN_HEIGHT)
        self.width = 500 + self.height
        self.image = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.hp_bar = pygame.Surface((500, self.height-10))
        self.icon = pygame.image.load('Sprites/Character/player.png')
        self.icon = rescaleSprite(self.icon, self.height / SCREEN_HEIGHT)
    def update(self, hp):
        self.image.fill((0, 0, 0))
        self.image.blit(self.icon, [0, 0])
        self.hp_bar = pygame.Surface(((hp*5 if hp > 0 else 0), self.height-10))
        self.hp_bar.fill((0, 255, 0))
        self.image.blit(self.hp_bar, [self.icon.get_width()+1, 5])
class BossHealth(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.height = int(0.09*SCREEN_HEIGHT)
        self.width = 500 + self.height
        self.image = pygame.Surface((SCREEN_WIDTH - self.width, self.height))
        self.rect = pygame.Rect(SCREEN_WIDTH - self.width, 0, self.width, self.height)
        self.hp_bar = pygame.Surface((500, self.height-10))
        
##        self.font = pygame.font.SysFont("Arial", height)
##        self.color = (255, 255, 255)
        self.icon = pygame.image.load('Sprites/Monsters/enemy.png')
        self.icon = rescaleSprite(self.icon, self.height / SCREEN_HEIGHT)
    def update(self, hp):
        self.image.fill((0, 0, 0))
        self.image.blit(self.icon, [self.width - self.icon.get_width(), 0])
        boss_hp_width = hp*500/1000 if hp > 0 else 0
        self.hp_bar = pygame.Surface((boss_hp_width, self.height-10))
        self.hp_bar.fill((0, 255, 0))
        self.image.blit(self.hp_bar, [500 - boss_hp_width, 5])
pygame.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("ANDY'S ADVENTURE")
player = Player((0, 0))
running = True
clock = pygame.time.Clock()
coin_score = Score('Sprites/Items/coin1.png', 4*0.09*SCREEN_HEIGHT, 0.09*SCREEN_HEIGHT, (0, 0.1*SCREEN_HEIGHT))
p_bullets = pygame.sprite.Group()
e_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
ladders = pygame.sprite.Group()
items = pygame.sprite.Group()
num_enemy = 50
all_sprites = pygame.sprite.Group()
left_boundary = Boundary((-10, 0), 20, SCREEN_HEIGHT)
right_boundary = Boundary((MAX_WIDTH-10, 0), 20, SCREEN_HEIGHT)

all_sprites.add(left_boundary)
all_sprites.add(right_boundary)

p_health = PlayerHealth()
b_health = BossHealth()
for i in range(num_enemy):
    enemy = Enemy((random.randint(0, MAX_WIDTH), random.randint(0, SCREEN_HEIGHT)))
    enemies.add(enemy)
    all_sprites.add(enemy)
for i in range(0, MAX_WIDTH, SCREEN_WIDTH):
    for h_ratio in [0.25, 0.5, 0.75]:
        ladder = Ladder((random.randint(i, i+SCREEN_WIDTH //2), h_ratio*SCREEN_HEIGHT), random.randint(SCREEN_WIDTH //4, SCREEN_WIDTH //2 - 50), 20, (255, 0, 0))
        ladders.add(ladder)
        all_sprites.add(ladder)
isBossAppeared = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pressed_keys = pygame.key.get_pressed()
    p_bullet = player.fire()
    if p_bullet:
        p_bullets.add(p_bullet)
        all_sprites.add(p_bullet)
    for enemy in enemies.sprites():
        e_bullet = enemy.fire()
        if e_bullet:
            e_bullets.add(e_bullet)
            all_sprites.add(e_bullet)
    enemies.update(player_rect = player.rect)
    enemy_collide = pygame.sprite.groupcollide(enemies,p_bullets,False, True)
    enemy_falls = pygame.sprite.groupcollide(enemies,ladders,False, False)
    player_collide = pygame.sprite.spritecollide(player,ladders,False)
    player_bullet = pygame.sprite.spritecollide(player,e_bullets,False)
    player.update(pressed_keys)
    if len(enemies.sprites()) == 0 and not isBossAppeared:
        isBossAppeared = True
        boss = Boss((SCREEN_WIDTH - 100, 0))
    if isBossAppeared:
        boss.update(player_rect = player.rect)
        e_bullet = boss.fire()
        if e_bullet:
            e_bullets.add(e_bullet)
            all_sprites.add(e_bullet)
        boss_hurted = pygame.sprite.spritecollide(boss,p_bullets,False)
        if boss_hurted:
            for bullet in boss_hurted:
                boss.hurted(bullet.damage)
                bullet.kill()
        b_health.update(boss.hp)
    if player_bullet:
        for bullet in player_bullet:
            player.hurted(bullet.damage)
            bullet.kill()
    if player_collide:
        for lad in player_collide:
            player.fall(lad)
    if enemy_falls:
        for res in enemy_falls:
            res.fall(enemy_falls[res][0])
    if player.rect.left > SCREEN_WIDTH // 2 and right_boundary.rect.left + 10 > (SCREEN_WIDTH):
        dx = player.rect.left - (SCREEN_WIDTH // 2)
        for sprite in all_sprites.sprites():
            sprite.trans_screen(dx)
        player.rect.left = SCREEN_WIDTH // 2
    elif player.rect.left < 10 and left_boundary.rect.left+10 < 0:
        dx = player.rect.left - 10
        for sprite in all_sprites.sprites():
            sprite.trans_screen(dx)
        player.rect.left = 10
    if enemy_collide:
        for res in enemy_collide:
            item = res.hurted(enemy_collide[res][0].damage)
            if item:
                items.add(item)
                all_sprites.add(item)
    pitem_collide = pygame.sprite.spritecollide(player,items,False)
    if pitem_collide:
        for item in pitem_collide:
            coin_score.score += item.score
            player.upgrade(item.addbullet)
            item.kill()
    p_bullets.update()
    e_bullets.update()
    items.update()
    p_health.update(player.hp)
    coin_score.update()
    screen.fill((0, 0, 0))


    screen.blit(left_boundary.image, left_boundary.rect)
    screen.blit(right_boundary.image, right_boundary.rect)
    screen.blit(coin_score.image, coin_score.rect)
    screen.blit(p_health.image, p_health.rect)
    ladders.draw(screen)
    if isBossAppeared:
        screen.blit(b_health.image, b_health.rect)
        screen.blit(boss.image, boss.rect)
    screen.blit(player.image, player.rect)
    items.draw(screen)
    p_bullets.draw(screen)
    e_bullets.draw(screen)
    enemies.draw(screen)
    
    pygame.display.flip()
    clock.tick(30)

# Done! Time to quit.
pygame.quit()
