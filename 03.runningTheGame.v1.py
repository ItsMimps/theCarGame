import pygame
import math
import sys

pygame.init()

clock = pygame.time.Clock()
FPS = 60

screen_width = 800
screen_height = 600

# creating the game display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Racing Game by Millie Young')
game_icon = pygame.image.load('car_image.png')
pygame.display.set_icon(game_icon)

#Position and peramiters of the car
x_position = 300
y_position = screen_height - 100
speed = 5
direction = 0

#setting up the keyboard keys that can control the car
up_key = pygame.K_UP
left_key = pygame.K_LEFT
right_key = pygame.K_RIGHT

#loading in the image
background = pygame.image.load('racing_track.png')
background = pygame.transform.scale(background, (screen_width, screen_height))
background_height = background.get_height()
players_car = pygame.transform.scale(pygame.image.load('car_1.png'),(60, 80))

# Instansiate the rectangle for the car
players_car_rect = players_car.get_rect(topleft = (x_position, y_position))

# Define game variables
scroll = 0
bg_speed = 3

#Game loop
run = True
while run:
    clock.tick(FPS)

    #Handling the events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #check if the up, left or right keys are pressed
    keys = pygame.key.get_pressed()
    if keys[up_key]:
        scroll += scroll + 0.1
    elif keys[right_key]:
        direction = 0
    elif keys[left_key]:
        direction = 180
    else:
        direction = None #stop the movement if NO keys are pressed

    # update the position of the car based in the direction and speed of the car
    if direction is not None:
        dx = speed * math.cos(math.radians(direction))
        dy = -speed * math.sin(math.radians(direction))

        players_car_rect.x += dx
        players_car_rect.y += dy

    #keep the car within the screen boundries
    if players_car_rect.left < 0:
        players_car_rect.left = 0
    elif players_car_rect.right > screen_width:
        players_car_rect.right = screen_width
    if players_car_rect.top < 0:
        players_car_rect.top = 0
    elif players_car_rect.bottom > screen_height:
        players_car_rect.bottom = screen_height

    #drawing the scrolling background
    for i in range (-1, 2):
        screen.blit(background, (0,i * background_height + scroll))

    # scroll background
    scroll += bg_speed

    #reset the scroll
    if scroll>= background_height:
        scroll = 0

    #draw the player's car
    screen.blit(players_car, players_car_rect)
    pygame.display.update()
pygame.quit()




