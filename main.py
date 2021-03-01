import pygame as game
import time
import os
import random as rand
import adversarial_search as ai

game.font.init()
game.init()

# Window Name and Icon
game.display.set_caption("Frogger")
# Attribute Freepik for the icon if used for noncommercial purposes
icon = game.image.load("assets/frog.png")
game.display.set_icon(icon)

# Screen size and color
size = width, height = 1280, 720
black = 0, 0, 0
color = 150, 150, 150
screen = game.display.set_mode(size)

delay = 0

# Art assets
charsprite = game.transform.scale(game.image.load(
    os.path.join("assets", "Frogger-Sprite-2.png")), (int(width / 12), int(height / 7)))
background = game.transform.scale(game.image.load(os.path.join("assets", "Frogger-Background.png")), (width, height))
car1 = game.transform.scale(game.image.load(
    os.path.join("assets", "Frogger Car 1.png")), (int(width / 12), int(height / 7)))
car2 = game.transform.scale(game.image.load(
    os.path.join("assets", "Frogger Car 2.png")), (int(width / 12), int(height / 7)))
car3 = game.transform.scale(game.image.load(
    os.path.join("assets", "Frogger Car 3.png")), (int(width / 12), int(height / 7)))
car4 = game.transform.scale(game.image.load(
    os.path.join("assets", "Frogger Car 4.png")), (int(width / 12), int(height / 7)))
car5 = game.transform.scale(game.image.load(
    os.path.join("assets", "Frogger Car 5.png")), (int(width / 12), int(height / 7)))

enemies = []
car1_vel = 70  # Base value: 5
car2_vel = 70  # Base value: 6
car3_vel = 70  # Base value: 5
car4_vel = 70  # Base value: 4
car5_vel = 70  # Base value: 5
stagger1 = 500  # Base value: 500
stagger2 = 600  # Base value: 600
buffer = 100  # Base value: 100
buffer2 = 200  # Base value: 200
x_check = 65  # Base value: 70
y_check = 50  # Base value: 50
AI_mode = True


# Defines the general structure for player and enemy characters
class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = None
        self.mask = None
        self.speed = None

    def draw(self, window):
        window.blit(self.sprite, (self.x, self.y))

    def get_width(self):
        return self.sprite.get_width()

    def get_height(self):
        return self.sprite.get_height()

    def collision(self, obj):
        return collide(obj, self)


# Inherits from the Character class and defines more specifically the traits of the player character
class Player(Character):
    def __init__(self, x, y, timer=45):
        super().__init__(x, y)
        self.sprite = charsprite
        self.mask = game.mask.from_surface(self.sprite)
        self.timer = timer


# Inherits from the Character class and includes several car sprites and velocities to account for different types
class Enemy(Character):
    car_type = {
        1: car1,
        2: car2,
        3: car3,
        4: car4,
        5: car5
    }

    def __init__(self, x, y, car, vel):
        super().__init__(x, y)
        self.sprite = self.car_type[car]
        self.mask = game.mask.from_surface(self.sprite)
        self.velocity = vel
        self.car_number = car

    def get_vel(self):
        return self.velocity

    def get_car(self):
        return self.car_number

    def move(self, v, car_type):
        if car_type % 2 == 0:
            self.x += v
        else:
            self.x -= v


# Detects if the sprites of two objects are overlapping (i.e. object collision)
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None


def main():
    running = True
    fps = 60  # Base Frames Per Second: 60
    clock = game.time.Clock()
    count = 0
    success = 0
    game_font = game.font.SysFont("centuryschoolbook", int((height + width) / 50))
    if AI_mode:
        player_velocity = 70
    else:
        player_velocity = 68  # Most compatible for a standard 1280 x 720 screen resolution: 68
    frogger = Player(int(0.4 * width), int(0.85 * height))

    # An array of objects, namely enemy cars with starting position, type, and speed attributes
    enemies = []
    enemies.append(
        Enemy(rand.randint(width, width + stagger1), int(0.78 * height), 1, car1_vel))
    enemies.append(
        Enemy(rand.randint(width + stagger1 + buffer, width + 2 * stagger1), int(0.78 * height), 1, car1_vel))
    enemies.append(
        Enemy(rand.randint(width + 2 * stagger1 + buffer, width + 3 * stagger1), int(0.78 * height), 1, car1_vel))

    enemies.append(
        Enemy(rand.randint(-(2 * stagger2), -stagger2), int(0.71 * height), 2, car2_vel))
    enemies.append(
        Enemy(rand.randint(-(3 * stagger2), -(2 * stagger2 + buffer)), int(0.71 * height), 2, car2_vel))
    enemies.append(
        Enemy(rand.randint(-(4 * stagger2), -(3 * stagger2 + buffer)), int(0.71 * height), 2, car2_vel))

    enemies.append(
        Enemy(rand.randint(width, width + stagger1), int(0.65 * height), 3, car3_vel))
    enemies.append(
        Enemy(rand.randint(width + stagger1 + buffer, width + 2 * stagger1), int(0.65 * height), 3, car3_vel))
    enemies.append(
        Enemy(rand.randint(width + 2 * stagger1 + buffer, width + 3 * stagger1), int(0.65 * height), 3, car3_vel))

    enemies.append(
        Enemy(rand.randint(-(2 * stagger2), -stagger2), int(0.59 * height), 4, car4_vel))
    enemies.append(
        Enemy(rand.randint(-(3 * stagger2), -(2 * stagger2 + buffer)), int(0.59 * height), 4, car4_vel))
    enemies.append(
        Enemy(rand.randint(-(4 * stagger2), -(3 * stagger2 + buffer)), int(0.59 * height), 4, car4_vel))

    enemies.append(
        Enemy(rand.randint(width, width + stagger1), int(0.52 * height), 5, car5_vel))
    enemies.append(
        Enemy(rand.randint(width + stagger1 + buffer2, width + 2 * stagger1), int(0.52 * height), 5, car5_vel))
    enemies.append(
        Enemy(rand.randint(width + 2 * stagger1 + buffer2, width + 3 * stagger1), int(0.52 * height), 5, car5_vel))

    # Refreshes game surfaces every frame
    def redraw():
        screen.blit(background, (0, 0))
        label1 = game_font.render(f"Deaths: {count}", False, color)
        label2 = game_font.render(f"Successes: {success}", False, color)
        screen.blit(label1, (width / 20, height - height / 8 + height / 15))
        screen.blit(label2, (width / 20 + stagger1, height - height / 8 + height / 15))
        frogger.draw(screen)
        for k in range(len(enemies)):
            enemies[k].move(enemies[k].get_vel(), int(k / 3) + 1)
            enemies[k].draw(screen)

        game.display.update()

    # Indicates to the AI algorithm that the player is within range of an enemy car's collision box
    def will_hit():
        hit = False
        pos_right = False
        for x in range(len(enemies)):
            future_check = enemies[x].x
            if enemies[x].get_car() % 2 == 0:
                future_check += 2 * enemies[x].velocity
            else:
                future_check -= 2 * enemies[x].velocity

            if frogger.y - player_velocity in range(enemies[x].y - y_check, enemies[x].y + y_check):
                if frogger.x in range(future_check - x_check, future_check + x_check):
                    hit = True
                    if frogger.x < enemies[x].x:
                        pos_right = True
        return hit, pos_right

    # Tells the AI algorithm how much to reward the player for performing specific actions
    def action():
        actions = [0] * 64
        for n in range(0, 16):
            # Actions are in the cardinal directions in sets of four like [Up, Left, Right, Down]
            # Reward is negative if player will collide with enemy b/c death is least optimal
            if will_hit()[0]:
                actions[4 * n] = -50
                if will_hit()[1]:
                    actions[(4 * n) + 1] = -47
                    actions[(4 * n) + 2] = -48
                else:
                    actions[(4 * n) + 1] = -46
                    actions[(4 * n) + 2] = -45
                actions[(4 * n) + 3] = -51
            else:
                actions[4 * n] = 20  # Highest value for moving up b/c we want the player to move up to win
                actions[(4 * n) + 1] = 10  # Player can move left or right but optimally not down
                actions[(4 * n) + 2] = 9  # Player can move left or right but optimally not down
                actions[(4 * n) + 3] = 5  # Going down has the smallest reward b/c it is opposite the goal
            if frogger.x + player_velocity == width:
                actions[(4 * n) + 1] = -100
            if frogger.x - player_velocity == 0:
                actions[(4 * n) + 2] = -101

        return actions

    while running:
        clock.tick(fps)
        redraw()

        for i in range(len(enemies)):
            # Loops the enemies around to their starting positions if they pass the edge of the screen
            if (int(i / 3) + 1) % 2 == 0 and enemies[i].x - enemies[i].get_width() > width:
                enemies[i].x = rand.randint(-(2 * stagger2), -stagger2)
                redraw()
            elif (int(i / 3) + 1) % 2 != 0 and enemies[i].x + enemies[i].get_width() < 0:
                enemies[i].x = rand.randint(width, width + stagger1)
                redraw()

            if enemies[i].collision(frogger):
                frogger.x = int(0.4 * width)
                frogger.y = int(0.85 * height)
                count += 1
                redraw()

        if AI_mode:
            if frogger.y <= 0:
                frogger.y = height
                success += 1
                frogger.x = rand.randint(int(width / 8), int(7 * width / 8))
            node_arr = action()
            best_val = ai.search(node_arr)
            print(best_val)

            if best_val == 20 or best_val == -51:
                frogger.y -= player_velocity
                redraw()
            elif best_val == 5 or best_val == -50:
                frogger.y += player_velocity
                redraw()
            elif best_val == 10 or best_val == -101 or best_val == -48 or best_val == -45:
                frogger.x += player_velocity
                redraw()
            elif best_val == 9 or best_val == -100 or best_val == -47 or best_val == -46:
                frogger.x -= player_velocity
                redraw()

        for event in game.event.get():
            if event.type == game.QUIT:
                running = False
                print("Final Statistics:")
                print(f"Deaths: {count}")
                print(f"Successes: {success}")
                print(f"Success to Death Ratio: 1:{count / success}")

            # This block of code controls every aspect of player movement
            if not AI_mode:
                if event.type == game.KEYDOWN:
                    pressed_key = game.key.get_pressed()
                    if pressed_key[game.K_a] and frogger.x - player_velocity > 0:
                        frogger.x -= player_velocity
                        # frogger.sprite = game.transform.rotate(frogger.sprite, 90)
                        redraw()
                        time.sleep(delay)
                        # frogger.sprite = charsprite
                    elif pressed_key[game.K_d] and frogger.x + frogger.get_width() + player_velocity * 0.65 < width:
                        frogger.x += player_velocity
                        # frogger.sprite = game.transform.rotate(frogger.sprite, 270)
                        redraw()
                        time.sleep(delay)
                        # frogger.sprite = charsprite
                    elif pressed_key[game.K_w] and frogger.y - player_velocity > 0:
                        frogger.y -= player_velocity * 0.65
                    elif pressed_key[game.K_s] and frogger.y + frogger.get_height() + player_velocity * 0.65 < height:
                        frogger.y += player_velocity * 0.65
                        # frogger.sprite = game.transform.rotate(frogger.sprite, 180)
                        redraw()
                        time.sleep(delay)
                        # frogger.sprite = charsprite
                    time.sleep(delay)


try:
    main()
except:
    print("No ratio can be found because no successes were recorded.")
