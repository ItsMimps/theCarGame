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
car_images = ['car_2.png', 'car_3.png', 'car_4.png', 'car_5.png', 'car_6.png']

#defining the x co-ordinates for the lanes on the racing track
fixed_x_positions = [
    150, #lane one
    250, #lane two
    350, #lane three
    450, #lane four
    550 #lane five
]

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
        self.speed = random.randint(3,6) #assign a new random speed on respawn
        self.image = pygame.transform.scale(pygame.image.load(random.choice(car_images)), (60, 80)) #assign a new random car image on respawn
        self.rect.topleft = (lane_position, random.randint(-150, -100)) #respawn COMPLETELY off the screen

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
        self.opposing_cars = []
        self.lane_occupancy ={} #this is used to track the lanes that are being occupied

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

            #update NPC cars and check for new spawning ones
            for opposing_car in self.opposing_cars:
                if opposing_car.update(self.car.speed):  # players speed to opposing car

                # find a new lane for respawn
                    new_lane_position = random.choice(fixed_x_positions)
                    while new_lane_position in self.lane_occupancy: #ensure that the lane is free
                        new_lane_position = random.choice(fixed_x_positions)

                    opposing_car.respawn(new_lane_position) #respawn in a new lane
                    self.lane_occupancy[new_lane_position] = opposing_car #update lane occupancy

                    #remove the old lane from occupancy
                    for lane in list(self.lane_occupancy):
                        if self.lane_occupancy[lane] == opposing_car:
                            del self.lane_occupancy[lane]
                            break

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