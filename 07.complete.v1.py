import pygame
import math
import sys
import random

#initialize pygame
pygame.init()

#constants through gaeplay
FPS = 60
screen_width = 800
screen_height = 600
racing_track_right_border = 670
racing_track_left_border = 130
max_lanes = 4 #maxiumum number of lanes occupied at once
car_images = ['car_2.png', 'car_3.png', 'car_4.png', 'car_5.png', 'car_6.png']

#defining the x co-ordinates for the lanes on the racing track
fixed_x_positions = [
    150, #lane one
    250, #lane two
    350, #lane three
    450, #lane four
    550 #lane five
]

#font set up for the score display
font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)

#function to keep track of the highest score - writes value to a file
def load_high_score():
    try:
        hi_score_file = open('../../Exercises/Llama game/HI_score.txt', 'r')
    except IOError:
        hi_score_file = open('../../Exercises/Llama game/HI_score.txt', 'w')
        hi_score_file.write('0')
    hi_score_file = open('../../Exercises/Llama game/HI_score.txt', 'r')
    value = hi_score_file.read()
    hi_score_file.close()

    return value

#function to update record of the highest score
def update_high_score(score, high_score):
    if int(score) > int(high_score):
        return score
    else:
        return high_score

#save updated hgh score if player beats it
def save_high_score(high_score):
    high_score_file = open('../../Exercises/Llama game/HI_score.txt', 'w')
    high_score_file.write(str(high_score))
    high_score_file.close()

class Car:
    def __init__(self, x_position, y_position):
        self.image = pygame.transform.scale(pygame.image.load('../../Exercises/Llama game/car_1.png'), (60, 80))
        self.rect = self.image.get_rect(topleft=(x_position, y_position))
        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 10
        self.deceleration = 0.1
        self.direction = 0

    def update(self, keys):
        if keys[pygame.K_UP]:
            self.speed = min(self.speed +self.acceleration, self.max_speed)
        else:
            self.speed = max(self.speed - self.deceleration, 0)

        if keys[pygame.K_RIGHT]:
            self.direction = 0
        elif keys[pygame.K_LEFT]:
            self.direction = 180
        else:
            self.direction = None

        if self.direction is not None and self.speed > 0:
            dx = self.speed * math.cos(math.radians(self.direction))
            dy = -self.speed * math.sin(math.radians(self.direction))
            self.rect.x += dx
            self.rect.y += dy

        self.keep_within_bounds()

    def keep_within_bounds(self):
        self.rect.left = max(self.rect.left, racing_track_left_border)
        self.rect.right = min(self.rect.right, racing_track_right_border)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, screen_height)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class OpposingCar:
    def __init__(self, lane_position):
        self.speed = random.randint(3, 6) #random speed assigned to the cars
        self.image = pygame.transform.scale(pygame.image.load(random.choice(car_images)), (60, 80))
        self.rect = self.image.get_rect(topleft=(lane_position, random.randint(-150, -100))) #spawning completely off the screen and then they load in

    def update(self, player_speed):
        #moving the NPC cars down the screen only if players car is moving forewards
        if player_speed > 0:
            self.rect.y += self.speed
        else:
            #move the opposing car upwards if the player car is stopped
            self.rect.y -= self.speed

        #reset positon if it goes off the the screen
        if self.rect.top > screen_height:
            return True #indicate that a car needs to respawn
        return False

    def respawn(self, lane_position):
        self.speed = random.randint(3, 6) #assign the new car a random speed

        selected_image = random.choice(car_images)
        self.image = pygame.transform.scale(pygame.image.load(selected_image), (60, 80))

        self.rect.topleft = (lane_position, random.randint(-150, -100)) #respawn COMPLETELY off the screen

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Game:
    def __init__(self):
        self.high_score = load_high_score()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Racing Game by Millie Young')
        game_icon = pygame.image.load('../../Exercises/Llama game/car_image.png')
        pygame.display.set_icon(game_icon)
        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(pygame.image.load('../../Exercises/Llama game/racing_track.png'), (screen_width, screen_height))
        self.scroll = 0
        self.car = Car(300, screen_height - 100) #this positions the car on the secound lane to the left to start

        # Initialize NPC cars
        self.opposing_cars = []
        self.lane_occupancy ={} #this is used to track the lanes that are being occupied
        self.score = 0 #initialize score

        self.create_opposing_cars()

    def create_opposing_cars(self):
        selected_lanes = random.sample(fixed_x_positions, max_lanes) #select UP TO four lanes
        for lane_position in selected_lanes:
            opposing_car = OpposingCar(lane_position) #create a car in the selected lane
            self.opposing_cars.append(opposing_car)
            self.lane_occupancy[lane_position] = opposing_car #mark the lane as occupied

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.car.update(keys)

            #check for collisions
            self.check_collisions()

            #update opposing cars
            for opposing_car in self.opposing_cars:
                if opposing_car.update(self.car.speed):
                    #remove the old lane from occumapncy
                    for lane, car in list(self.lane_occupancy.items()):
                        if car == opposing_car:
                            del self.lane_occupancy[lane]
                            break

                    #find a NEW free lane
                    available_lanes = [lane for lane in fixed_x_positions if lane not in self.lane_occupancy]
                    if available_lanes:
                        new_lane_position = random.choice(available_lanes)
                        opposing_car.respawn(new_lane_position)
                        self.lane_occupancy[new_lane_position] = opposing_car
                        self.score += 1

            #make the backgroundd sroll and draw the normal setting etc
            self.scroll_background()
            self.draw()
            pygame.display.update() #making sure that the display is UPDATED

    def check_collisions(self):
        for opposing_car in self.opposing_cars:
            if self.car.rect.colliderect(opposing_car.rect):
                self.game_over()

    def pause_menu(self):
        self.screen.fill(black)
        pause_text = font.render('Game Paused', True, white)
        instructions_pause_text = font.render('Press R to resume or Q to Quit', True, white)
        self.screen.blit(pause_text, (screen_width // 2 - 80, screen_height // 2 - 40)) #double dash mean divide to the nearesy whole number
        self.screen.blit(instructions_pause_text, (screen_width // 2 - 180, screen_height // 2 + 10))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        return #AKA resume game

    def game_over(self):
        self.high_score = update_high_score(self.score, self.high_score)
        save_high_score(self.high_score)
        self.screen.fill(black) #fill the screen with a black background

        game_over_text = font.render('Game Over!', True, white)
        score_text = font.render(f'Score: {self.score}', True, white)
        high_score_text = font.render(f'High Score: {self.high_score}', True, white)
        instructions_text = font.render('Press R to Restart or Q to Quit', True, white) #added in the RESTART instructions :)

        #normal like game over and options text
        self.screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 240))
        self.screen.blit(instructions_text, (screen_width // 2 - instructions_text.get_width() // 2, 290))

        #get the widths of the texts (SCORES)
        score_width = score_text.get_width()
        high_score_width = high_score_text.get_width()
        gap = 40 #allows for a gap

        #calculate the nice spacing from center
        total_width = score_width + high_score_width + gap
        score_x = (screen_width // 2) - total_width // 2
        high_score_x = score_x + score_width + gap

        #draw the texts on the same line UNDER the instructions
        self.screen.blit(score_text, (score_x, 340))
        self.screen.blit(high_score_text, (high_score_x, 340))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        Game().run() #this means that the game will restart
                        return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.pause_menu() #refer to pause menu for next option instead of just quit

    def scroll_background(self):
        self.scroll += self.car.speed
        if self.scroll >= self.background.get_height():
            self.scroll = 0

    def draw(self):
        for i in range(-1, 2):
            self.screen.blit(self.background, (0, i * self.background.get_height() + self.scroll))
        self.car.draw(self.screen)

        #drawing the NPC cars
        for opposing_car in self.opposing_cars:
            opposing_car.draw(self.screen)

        #draw the score box (top L)
        pygame.draw.rect(self.screen, black, (0, 0, 130, 40))
        score_text = font.render(f'Score: {self.score}', True, white)
        self.screen.blit(score_text, (10, 10))

        #draw the high score boc (top R)
        high_score_text = font.render(f'High: {self.high_score}', True, white)
        high_score_width = high_score_text.get_width()
        pygame.draw.rect(self.screen, black, (screen_width - high_score_width - 20, 0, high_score_width + 20, 40))
        self.screen.blit(high_score_text, (screen_width - high_score_width - 10, 10))

if __name__ == "__main__":
    Game().run()