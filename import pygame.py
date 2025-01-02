import pygame
import sys
import math
import random

# Инициализация Pygame
pygame.init()

# Настройка экрана
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 700
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Простое меню")


# Позиции для границ игрока и монстров
PLAYER_BOUNDS = pygame.Rect(50, 100, 1200, 500)   # Прямоугольник для границ игрока
MONSTER_BOUNDS = pygame.Rect(100, 150, 1100, 400) # Прямоугольник для границ монстров

# Загрузка изображений кнопок
play_button_image = pygame.image.load("menu/play.png")
exit_button_image = pygame.image.load("menu/exit.png")

# Загрузка изображений фона
menu_background = pygame.image.load("menu/menu.png").convert_alpha()
background_image = pygame.image.load("backgraund/fon.png")
over_image = pygame.image.load("backgraund/g.png")
win_image = pygame.image.load("backgraund/win.png")

# Установка позиций кнопок
play_button_rect = play_button_image.get_rect(topleft=(570, 200))
exit_button_rect = exit_button_image.get_rect(topleft=(570, 300))

# Определение классов
class PlayerBullet:
    def __init__(self, x, y, mouse_x, mouse_y):
        self.x = x
        self.y = y
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.speed = 10
        self.angle = math.atan2(y - mouse_y, x - mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

    def main(self, display):
        self.x -= self.x_vel
        self.y -= self.y_vel
        pygame.draw.circle(display, (255, 255, 255), (int(self.x), int(self.y)), 5)

class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.speed = 1
        self.height = height
        self.animate_count = 0
        self.ammo = 35
        self.shoot_delay = 150  # время задержки между выстрелами в миллисекундах
        self.last_shot_time = pygame.time.get_ticks()
        self.reloading = False
        self.reload_time = 3000
        self.reload_start_time = 0  # Время начала перезарядки
        self.health = 100
        self.armor = 100
        self.animation_images_right = [
            pygame.transform.scale(pygame.image.load("hero/hero1r.png"), (64, 64)),
            pygame.transform.scale(pygame.image.load("hero/hero2r.png"), (64, 64)),
            pygame.transform.scale(pygame.image.load("hero/hero3r.png"), (64, 64)),
            pygame.transform.scale(pygame.image.load("hero/hero4r.png"), (64, 64))
        ]
        self.animation_images_left = [
            pygame.transform.scale(pygame.image.load("hero/hero1l.png"), (64, 64)),
            pygame.transform.scale(pygame.image.load("hero/hero2l.png"), (64, 64)),
            pygame.transform.scale(pygame.image.load("hero/hero3l.png"), (64, 64)),
            pygame.transform.scale(pygame.image.load("hero/hero4l.png"), (64, 64))
        ]
        self.current_animation = self.animation_images_right
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:  # Влево
            self.x = max(PLAYER_BOUNDS.left, self.x - self.speed)
        if keys[pygame.K_d]:  # Вправо
            self.x = min(PLAYER_BOUNDS.right - self.width, self.x + self.speed)
        if keys[pygame.K_w]:  # Вверх
            self.y = max(PLAYER_BOUNDS.top, self.y - self.speed)
        if keys[pygame.K_s]:  # Вниз
            self.y = min(PLAYER_BOUNDS.bottom - self.height, self.y + self.speed)

    def draw(self, display):
        pygame.draw.rect(display, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def main(self, display):
        if self.animate_count + 2 >= len(self.current_animation) * 32:
            self.animate_count = 0
        display.blit(self.current_animation[self.animate_count // 32], (self.x, self.y))

        self.animate_count += 1
        self.handle_gun(display)
        pygame.draw.rect(display, (255, 0, 0), (self.x, self.y - 20, self.width * (self.health / 100), 5))
        pygame.draw.rect(display, (0, 0, 255), (self.x, self.y - 10, self.width * (self.armor / 100), 5))
        font = pygame.font.Font(None, 24)
        ammo_text = font.render(f"Боеприпасы: {self.ammo}", True, (255, 255, 255))
        display.blit(ammo_text, (1000, 15))

        if self.ammo == 0 and not self.reloading:
            self.reloading = True
            pygame.time.set_timer(pygame.USEREVENT, self.reload_time)

    def handle_gun(self, display):
        keys = pygame.key.get_pressed()
        # Если нажата клавиша D (движение вправо)
        if keys[pygame.K_d]:
            self.current_animation = self.animation_images_right
        # Если нажата клавиша A (движение влево)
        elif keys[pygame.K_a]:
            self.current_animation = self.animation_images_left

    def take_damage(self, damage):
        if self.armor > 0:
            self.armor -= damage
            if self.armor < 0:
                self.health += self.armor  # Возвращаем "излишнее" повреждение обратно к здоровью
                self.armor = 0
        else:
            self.health -= damage

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return not self.reloading and self.ammo > 0 and current_time - self.last_shot_time >= self.shoot_delay

    def shoot(self):
        if self.can_shoot():
            self.ammo -= 1
            self.last_shot_time = pygame.time.get_ticks()
            if self.ammo == 0:
                self.reloading = True
                self.reload_start_time = pygame.time.get_ticks()

    def reload(self):
        self.ammo = 35  # Полное перезарядка оружия
        self.reloading = False
        self.reload_start_time = 0


class Monster:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.animation_images = [
            pygame.image.load("monster/monster1r.png"),
            pygame.image.load("monster/monster2r.png"),
            pygame.image.load("monster/monster3r.png"),
            pygame.image.load("monster/monster4r.png"),
            pygame.image.load("monster/monster5r.png"),
            pygame.image.load("monster/monster6r.png"),
            pygame.image.load("monster/monster7r.png"),
            pygame.image.load("monster/monster8r.png")

        ]
        self.animation_count = 0
        self.rect = pygame.Rect(x, y, width, height)# Добавляем прямоугольник для обнаружения столкновений
        self.reset_offset = 0
        self.offset_x = random.randint(-1, 1)
        self.offset_y = random.randint(-1, 1)
        self.width = width
        self.height = height
        self.speed = 0.6
        self.fire_rate = 300
        self.fire_countdown = random.randint(0, self.fire_rate)
        self.aim_offset_x = 0
        self.aim_offset_y = 0
        self.health = 100
        self.hit_count = 0
        # Обновляем координаты монстра с учетом случайного изменения
    def main(self, display):
        self.x += self.offset_x * self.speed
        self.y += self.offset_y * self.speed
        # Проверка на выход за границы экрана
        if self.x < 0:
            self.x = 0
            self.offset_x = random.randint(1, 2)
        elif self.x > 800 - self.width:
            self.x = 800 - self.width
            self.offset_x = random.randint(-2, -1)

        if self.y < 0:
            self.y = 0
            self.offset_y = random.randint(1, 2)
        elif self.y > 600 - self.height:
            self.y = 600 - self.height
            self.offset_y = random.randint(-2, -1)
        # Отображение анимации монстра
        monster_image = pygame.transform.scale(self.animation_images[self.animation_count // 16], (self.width, self.height))
        display.blit(monster_image, (self.x, self.y))
        self.animation_count += 1
        if self.animation_count >= len(self.animation_images) * 8:
            self.animation_count = 0

        pygame.draw.rect(display, (255, 0, 0), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(display, (0, 255, 0), (self.x, self.y - 10, self.width * (self.health / 100), 5))

        if self.fire_countdown <= 0:
            self.fire_bullet(display)
            self.fire_countdown = self.fire_rate
        else:
            self.fire_countdown -= 1
    def move(self):
        if self.direction == 'left':
            self.x -= self.speed
            if self.x < MONSTER_BOUNDS.left:
                self.direction = 'right'
        elif self.direction == 'right':
            self.x += self.speed
            if self.x + self.width > MONSTER_BOUNDS.right:
                self.direction = 'left'
        elif self.direction == 'up':
            self.y -= self.speed
            if self.y < MONSTER_BOUNDS.top:
                self.direction = 'down'
        elif self.direction == 'down':
            self.y += self.speed
            if self.y + self.height > MONSTER_BOUNDS.bottom:
                self.direction = 'up'

    def draw(self, display):
        pygame.draw.rect(display, (255, 0, 0), (self.x, self.y, self.width, self.height))
        
    def update_aim_offsets(self):
        self.aim_offset_x = random.randint(-10, 10)
        self.aim_offset_y = random.randint(-10, 10)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        # Создаем пулю направленную на игрока с учетом случайного смещения
    def fire_bullet(self, display):
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2
        angle_to_player = math.atan2(player_center_y - (self.y + self.height / 2 + self.aim_offset_y), player_center_x - (self.x + self.width / 2 + self.aim_offset_x))
        x_vel = math.cos(angle_to_player) * 8
        y_vel = math.sin(angle_to_player) * 8
        monster_bullet = MonsterBullet(self.x + self.width / 2, self.y + self.height / 2, x_vel, y_vel)
        monster_bullets.append(monster_bullet)

class Boss(Monster):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.animation_images = [
                pygame.image.load("boss/boss0.png"),
                pygame.image.load("boss/boss1.png"),
                pygame.image.load("boss/boss2.png"),
                pygame.image.load("boss/boss3.png")
            ]
        self.speed = 0.6
        self.fire_rate = 100

    def main(self, display):
        super().main(display)
        pygame.draw.rect(display, (0, 255, 0), (self.x, self.y - 20, self.width * (self.health / 100), 5))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            # Код, выполняемый при смерти босса
             pass


class MonsterBullet:
    def __init__(self, x, y, x_vel, y_vel):
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel

    def main(self, display):
        self.x += self.x_vel
        self.y += self.y_vel
        pygame.draw.circle(display, (255, 0, 0), (int(self.x), int(self.y)), 5)


# Определение функции для отображения текста на экране
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

def game():
    global player
    global font, clock,running

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    running = True  # Установка значения True для переменной running
    player_spawn_point = (700 - 32, 700 - 32)
    player = Player(*player_spawn_point, 64, 64)
    player_bullets = []
    global monster_bullets
    monster_bullets = []
    monsters = [Monster(random.randint(0, 900), random.randint(0, 700), 64, 64)]
    display_scroll = [0, 0]
    killed_monsters = 0

    reloading_event = pygame.USEREVENT + 1  # Создаем новый тип события для перезарядки
    pygame.time.set_timer(reloading_event, player.reload_time)  # Устанавливаем таймер перезарядки

    boss = Boss(random.randint(0, 800), random.randint(0, 600), 0, 0)
    #основной игровой цикл

    while running:
        display.blit(background_image, (0 - display_scroll[0], 0 - display_scroll[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if player.can_shoot():
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        player_bullet = PlayerBullet(player.x + player.width / 2, player.y + player.height / 2, mouse_x,mouse_y)
                        player_bullets.append(player_bullet)
                        player.shoot()
                        # Устанавливаем таймер перезарядки, если игрок стреляет
                        pygame.time.set_timer(reloading_event, player.reload_time)
            elif event.type == reloading_event:
                player.reload()  # Перезарядка оружия игрока
                for bullet in player_bullets:
                    bullet.main(display)
                # Проверка здоровья игрока
                if player.health <= 0:
                    running = False  # Устанавливаем running в False, чтобы выйти из цикла
        # Создание копии списка монстров, чтобы избежать проблемы с удалением во время итерации
        monsters_copy = monsters[:]
        for monster in monsters_copy:
            monster.main(display)
            monster_rect = monster.get_rect()
            # Создание копии списка пуль, чтобы избежать проблемы с удалением во время итерации
            bullets_copy = player_bullets[:]
            for bullet in bullets_copy:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)

                if bullet_rect.colliderect(monster_rect):
                    player_bullets.remove(bullet)
                    monster.hit_count += 1
                    if monster.hit_count >= 1:
                        monster.health -= 50
                        monster.hit_count = 0
                        if monster.health <= 0:
                            monsters.remove(monster)
                            killed_monsters += 1
                            monsters.append(Monster(random.randint(0, 800), random.randint(0, 600), 64, 64))


        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x > 0:
            player.x -= 10
        if keys[pygame.K_d] and player.x < SCREEN_WIDTH - player.width:
            player.x += 10
        if keys[pygame.K_w] and player.y > 0:
            player.y -= 10
        if keys[pygame.K_s] and player.y < SCREEN_HEIGHT - player.height:
            player.y += 15
        # Проверка границ экрана для игрока
        if player.x < 0:
            player.x = 0
        elif player.x > SCREEN_WIDTH - player.width:
            player.x = SCREEN_WIDTH - player.width
        if player.y < 0:
            player.y = 0
        elif player.y > SCREEN_HEIGHT - player.height:
            player.y = SCREEN_HEIGHT - player.height

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if player.can_shoot():
                        player.shoot()
                elif event.button == 1:  # Правая кнопка мыши
                    if player.can_shoot():
                        player.shoot()

            elif event.type == reloading_event:
                player.reload()

        for monster in monsters:
            monster_rect = monster.get_rect()
            if monster_rect.x < 0 or monster_rect.x > SCREEN_WIDTH - monster_rect.width:
                monster.offset_x *= -1
            if monster_rect.y < 0 or monster_rect.y > SCREEN_HEIGHT - monster_rect.height:
                monster.offset_y *= -1

            # Добавляем отображение "win" на весь экран, если убито 20 монстров
            if killed_monsters >= 20:
                display.blit(win_image, (55, 10))
                pygame.display.flip()
                pygame.time.delay(3000)  # Оставляем изображение "win" на экране в течение 5 секунд
                return

            for bullet in player_bullets:
                bullet.main(display)

            monsters_copy = monsters[:]
            for monster in monsters_copy:
                monster.main(display)
                monster_rect = monster.get_rect()

            if not player.reloading and player.ammo > 0:
                if keys[pygame.K_SPACE]:
                    player.shoot()

            monsters_copy = monsters[:]
            for monster in monsters_copy:
                monster.main(display)
                monster_rect = monster.get_rect()
        # Обработка пуль монстров
        for monster_bullet in monster_bullets:
            monster_bullet.main(display)
            if pygame.Rect(player.x, player.y, player.width, player.height).colliderect(
                    pygame.Rect(monster_bullet.x, monster_bullet.y, 5, 5)):
                player.take_damage(10)
                monster_bullets.remove(monster_bullet)
        # Для босса
        if boss.x < 0 or boss.x > SCREEN_WIDTH - boss.width:
            boss.offset_x *= -1
        if boss.y < 0 or boss.y > SCREEN_HEIGHT - boss.height:
            boss.offset_y *= -1
        # Обновление и отображение босса
        boss.main(display)

        player.handle_gun(display)
        player.main(display)

        for bullet in player_bullets:
            bullet.main(display)
        # В функции обработки движения монстров
        monsters_copy = monsters[:]
        for monster in monsters_copy:
            monster.main(display)
            monster_rect = monster.get_rect()

            bullets_copy = player_bullets[:]
            for bullet in bullets_copy:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)

                if bullet_rect.colliderect(monster_rect):
                    player_bullets.remove(bullet)
                    monster.hit_count += 1
                    if monster.hit_count >= 1:
                        monster.health -= 50
                        monster.hit_count = 0
                        if monster.health <= 0:
                            monsters.remove(monster)
                            killed_monsters += 1
                            monsters.append(Monster(random.randint(0, 800), random.randint(0, 600), 64, 64))
        # Обновляем случайное смещение для направления пуль монстра
        monster.update_aim_offsets()

        draw_text("Убито: {}".format(killed_monsters), font, (255, 255, 255), display, 10, 10)
        # Создаем босса, если убито 3 монстра и в списке монстров только 1 элемент
        if killed_monsters >= 10 and len(monsters) == 1:
            monsters.append(Boss(random.randint(0, 800), random.randint(0, 600), 128, 128))
            for _ in range(0):
                monsters.append(Monster(random.randint(0, 800), random.randint(0, 600), 64, 64))
        # Отображаем монстров с учетом смещения экрана
        for monster in monsters:
            monster_rect = monster.get_rect()
            monster_x = monster.x - display_scroll[0]
            monster_y = monster.y - display_scroll[1]
            monster_rect.topleft = (monster_x, monster_y)
            monster.main(display)

        pygame.display.update()
        clock.tick(30)


def main_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if play_button_rect.collidepoint(event.pos):
                        game()  # Вызов функции game() при нажатии кнопки "Играть"
                        return True  # Возврат True для начала игры
                    elif exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

        display.blit(menu_background, (-150, -380))
        display.blit(play_button_image, play_button_rect)
        display.blit(exit_button_image, exit_button_rect)
        pygame.display.flip()

while True:
    main_menu()
