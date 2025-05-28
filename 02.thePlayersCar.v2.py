import pygame
import math

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

#Position of the car
x_position = 300
y_position = screen_height - 100

#loading in the image
background = pygame.image.load('racing_track.png')
background = pygame.transform.scale(background, (screen_width, screen_height))
background_height = background.get_height()
players_car = pygame.transform.scale(pygame.image.load('car_1.png'),(60, 80))

# Instansiate the rectangle for the car
players_car_rect = players_car.get_rect(topleft = (x_position, y_position))

# Define game variables
scroll = 0
speed = 3

#Game loop
def game_loop():
    run = True
    while run:

        clock.tick(FPS)

        # Draw the scrolling background
        for i in range(-1, 2):
            screen.blit(background, (0, i*background_height + scroll))

        # Scroll background
        scroll += speed

        #reset the scroll
        if abs(scroll) >= background_height:
            scroll = 0

        #how to quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.blit(players_car, players_car_rect)
        pygame.display.update()

    pygame.quit()

