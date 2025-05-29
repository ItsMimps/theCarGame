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
racing_track_right_border = 610
racing_track_left_border = 130
max_lanes = 4 #maxiumum number of lanes occupied at once
min_distance = 60 #this is the minumum spawn distance between SPAWN cars
max_attempts = 100 # limit the number of attempts to find a valid spawn position (to not crash)

class Car:
    def __init__(self, x_position, y_position):
        self.image = pygame.transform.scale(pygame.image.load('car_1.png'), (60, 80))
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
        if self.rect.left < racing_track_left_border:
            self.rect.left = racing_track_left_border
        elif self.rect.right > racing_track_right_border:
            self.rect.right = racing_track_right_border

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class OpposingCar:
    def __init__(self, existing_cars):
        self.spawn_new_car(existing_cars) #call the method to initialize car properties
        self.speed = random.randint(3, 6) #initialize speed here

    def spawn_new_car(self, existing_cars):
        extra_cars_list = ['car_2.png', 'car_3.png', 'car_4.png', 'car_5.png', 'car_6.png']
        self.image = pygame.transform.scale(pygame.image.load(random.choice(extra_cars_list)), (60, 80))

        #randomly choose an x position within the track boundries
        for _ in range(max_attempts):
            x_position = random.randint(racing_track_left_border, racing_track_right_border)
            self.rect = self.image.get_rect(topleft=(x_position, -80)) #set the rectangle position AND start from off screen area

            #check for minimum spawn distance
            if all(abs(self.rect.x - car.rect.x) >= min_distance for car in existing_cars):
                return # position is valid

            #if we exceed max attempts, just position it randomly (could be improved further)
            self.rect = self.image.get_rect(topleft=(x_position, -80))

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Racing Game by Millie Young')
        game_icon = pygame.image.load('car_image.png')
        pygame.display.set_icon(game_icon)
        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(pygame.image.load('racing_track.png'), (screen_width, screen_height))
        self.scroll = 0
        self.car = Car(300, screen_height - 100) #this positions the car on the secound lane to the left to start

        # Initialize NPC cars
        self.opposing_cars = [OpposingCar([]) for _ in range(5)] # create multiple NPC cars

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.car.update(keys)

            #update NPC cars and check for new spawning ones
            for opposing_car in self.opposing_cars:
                if opposing_car.update(self.car.speed): #players speed to opposing car
                    opposing_car.spawn_new_car(self.opposing_cars) #respawn with NEW properties

            self.scroll_background()
            self.draw()
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() #system exit

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

if __name__ == "__main__":
    Game().run()