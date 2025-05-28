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

#loading in the image
background = pygame.image.load('racing_track.png')
background = pygame.transform.scale(background, (800, 500))
background_height = background.get_height()

# Define game variables
tiles = math.ceil(screen_height / background_height) + 1 #adding an extra scroll so that there is no blurry mess, by adding one we add a buffer
scroll = 0

#Game loop
run = True
while run:

    clock.tick(FPS)

    # Draw the scrolling background
    for i in range(0, tiles):
        screen.blit(background, (0, i*background_height + scroll))

    # Scroll background
    scroll -= 3

    #reset the scroll
    if abs(scroll) > background_height:
        scroll = 0

    #how to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

