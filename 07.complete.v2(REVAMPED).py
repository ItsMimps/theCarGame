import pygame
import math
import sys
import random

# Initialize pygame
pygame.init()

# Constants through gameplay
FPS = 60
screen_width = 800
screen_height = 600
racing_track_right_border = 670
racing_track_left_border = 130
max_lanes = 4 # The maximum number of lanes to be occupied at once (to make sure that the players car can ALWAYS get past
car_images = ['car_2.png', 'car_3.png', 'car_4.png', 'car_5.png', 'car_6.png']

# Defining the x co-ordinates for the lanes on the racing track
fixed_x_positions = [
    150, # Lane one
    250, # Lane two
    350, # Lane three
    450, # Lane four
    550 # Lane five
]

# Font and colour set up for the display
font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)

# Load the high score from a file, or set to 0 if file not found
def load_high_score():
    file_path = '../../Assessment/theCarGame/HI_score.txt'

    try:
        with open(file_path, 'r') as hi_score_file:
            value = hi_score_file.read()
    except IOError:
        with open(file_path, 'w') as hi_score_file:
            hi_score_file.write('0')
        value = '0' # Default high score if the file does not exist is ZERO
    return value

# This is a function to update the record of the highest score
def update_high_score(score, high_score):
    if int(score) > int(high_score):
        return score
    else:
        return high_score

# This is a function that saves the updated high score if player beats it (becomes the NEW high score in the file)
def save_high_score(high_score):
    high_score_file = open('../../Assessment/theCarGame/HI_score.txt', 'w')
    high_score_file.write(str(high_score))
    high_score_file.close()

# This is the Car class
class Car:
    def __init__(self, x_position, y_position):
        self.image = pygame.transform.scale(pygame.image.load('../../Assessment/theCarGame/car_1.png'), (60, 80))
        self.rect = self.image.get_rect(topleft=(x_position, y_position))
        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 10
        self.deceleration = 0.1
        self.direction = 0

    # This updates the car's position based on the keys
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

    # This piece of code prevents the car from moving off of the screen
    def keep_within_bounds(self):
        self.rect.left = max(self.rect.left, racing_track_left_border)
        self.rect.right = min(self.rect.right, racing_track_right_border)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, screen_height)

    # This piece of code draws the car on the screen
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# This is the opposing NPC car class
class OpposingCar:
    def __init__(self, lane_position):
        self.speed = random.randint(3, 6) # Assigns a random speed to the cars (range of 3 - 6)
        self.image = pygame.transform.scale(pygame.image.load(random.choice(car_images)), (60, 80))
        self.rect = self.image.get_rect(topleft=(lane_position, random.randint(-150, -100))) # Positioned os that the new cars are spawning completely off the screen and THEN load in

    # Move the NPC cars depending on the players movement
    def update(self, player_speed):
        # Moving the NPC cars down the screen ONLY if players car is moving forewords
        if player_speed > 0:
            self.rect.y += self.speed
        else:
            # Move the opposing car upwards if the player car is stopped
            self.rect.y -= self.speed

        # Reset position if it goes off the screen
        if self.rect.top > screen_height:
            return True # Indicate that a car needs to respawn
        return False

    # Respawn the NPC car in the new lane
    def respawn(self, lane_position):
        self.speed = random.randint(3, 6) # Assign the new car a random speed
        selected_image = random.choice(car_images)
        self.image = pygame.transform.scale(pygame.image.load(selected_image), (60, 80))
        self.rect.topleft = (lane_position, random.randint(-150, -100)) # Respawn COMPLETELY off the screen

    # Draw the NPC car on the screen
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# This is the MAIN game class
class Game:
    def __init__(self):
        self.high_score = load_high_score()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Racing Game by Millie Young')
        game_icon = pygame.image.load('../../Assessment/theCarGame/car_image.png')
        pygame.display.set_icon(game_icon)
        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(pygame.image.load('../../Assessment/theCarGame/racing_track.png'), (screen_width, screen_height))
        self.scroll = 0
        self.car = Car(300, screen_height - 100) # This positions the car on the second lane to the left to start

        # Initialize NPC cars
        self.opposing_cars = []
        self.lane_occupancy ={} # This is used to track the lanes that are being occupied
        self.score = 0 # Initialize score

        self.create_opposing_cars()

    # Create up to four NPC cars in random lanes
    def create_opposing_cars(self):
        selected_lanes = random.sample(fixed_x_positions, max_lanes) # Select UP TO four lanes
        for lane_position in selected_lanes:
            opposing_car = OpposingCar(lane_position) # Create a car in the selected lane
            self.opposing_cars.append(opposing_car)
            self.lane_occupancy[lane_position] = opposing_car # Mark the lane as occupied

    # Main game loop
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.car.update(keys)
            self.check_collisions()

            for opposing_car in self.opposing_cars:
                if opposing_car.update(self.car.speed):
                    for lane, car in list(self.lane_occupancy.items()):
                        if car == opposing_car:
                            del self.lane_occupancy[lane]
                            break

                    # Find a NEW free lane
                    available_lanes = [lane for lane in fixed_x_positions if lane not in self.lane_occupancy]
                    if available_lanes:
                        new_lane_position = random.choice(available_lanes)
                        opposing_car.respawn(new_lane_position)
                        self.lane_occupancy[new_lane_position] = opposing_car
                        self.score += 1

            # Make the background scroll and draw the normal setting etc
            self.scroll_background()
            self.draw()
            pygame.display.update() # Making sure that the display is UPDATED

    # Detect player collision with any NPC car
    def check_collisions(self):
        for opposing_car in self.opposing_cars:
            if self.car.rect.colliderect(opposing_car.rect):
                self.game_over()

    # Pause menu screen
    def pause_menu(self):
        self.screen.fill(black)
        pause_text = font.render('Game Paused', True, white)
        instructions_pause_text = font.render('Press R to resume or Q to Quit', True, white)
        self.screen.blit(pause_text, (screen_width // 2 - 80, screen_height // 2 - 40)) # Double dash mean divide to the nearest whole number
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
                        return # AKA resume game

    # Game over screen
    def game_over(self):
        self.high_score = update_high_score(self.score, self.high_score)
        save_high_score(self.high_score)
        self.screen.fill(black) # Fill the screen with a black background

        game_over_text = font.render('Game Over!', True, white)
        score_text = font.render(f'Score: {self.score}', True, white)
        high_score_text = font.render(f'High Score: {self.high_score}', True, white)
        instructions_text = font.render('Press R to Restart or Q to Quit', True, white)

        # Game over and options text
        self.screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 240))
        self.screen.blit(instructions_text, (screen_width // 2 - instructions_text.get_width() // 2, 290))

        # Get the widths of the texts (SCORES)
        score_width = score_text.get_width()
        high_score_width = high_score_text.get_width()
        gap = 40 # Allows for a gap

        # Calculate the nice spacing from center
        total_width = score_width + high_score_width + gap
        score_x = (screen_width // 2) - total_width // 2
        high_score_x = score_x + score_width + gap

        # Draw the texts on the same line UNDER the instructions
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
                        Game().run() # This means that the game will restart
                        return

    # Handle quit events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.pause_menu() # Refer to pause menu for next option instead of just quit

    # Scroll the background VERTICALLY
    def scroll_background(self):
        self.scroll += self.car.speed
        if self.scroll >= self.background.get_height():
            self.scroll = 0

    # Draw all game elements on screen
    def draw(self):
        for i in [-1, 0, 1]:
            self.screen.blit(self.background, (0, i * self.background.get_height() + self.scroll))
        self.car.draw(self.screen)

        # Drawing the NPC cars
        for opposing_car in self.opposing_cars:
            opposing_car.draw(self.screen)

        # Draw the score box (top L)
        pygame.draw.rect(self.screen, black, (0, 0, 130, 40))
        score_text = font.render(f'Score: {self.score}', True, white)
        self.screen.blit(score_text, (10, 10))

        # Draw the high score boc (top R)
        high_score_text = font.render(f'High Score: {self.high_score}', True, white)
        high_score_width = high_score_text.get_width()
        pygame.draw.rect(self.screen, black, (screen_width - high_score_width - 20, 0, high_score_width + 20, 40))
        self.screen.blit(high_score_text, (screen_width - high_score_width - 10, 10))

        # Shows the games 'instructions' when the up/forewords arrow is NOT pushed
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_UP]:
            game_instructions = font.render("<- = Move Left Move right = ->", True, white)
            accelerate_instructions = font.render("UP ARROW = ACCELERATE", True, white)

            # Get widths and heights
            game_instructions_width = game_instructions.get_width() + 20
            box_height = game_instructions.get_height() + 10
            accelerate_instructions_width = accelerate_instructions.get_width() + 20

            # Use the wider of the two boxes to align
            box_width = max(game_instructions_width, accelerate_instructions_width)
            box_x = (screen_width - box_width) // 2
            box_y1 = screen_height - 140 # This is for the first line
            box_y2 = box_y1 + box_height + 10 # Seconds line, spaced below the first

            # Draw the black rectangle bases
            pygame.draw.rect(self.screen, black, (box_x, box_y1, box_width, box_height))
            pygame.draw.rect(self.screen, black, (box_x, box_y2, box_width, box_height))

            # Blit (block transfer) the white text instructions
            self.screen.blit(game_instructions, (box_x + 10, box_y1 + 5))
            self.screen.blit(accelerate_instructions, (box_x +10, box_y2 +5))

# Start the game
if __name__ == "__main__":
    Game().run()