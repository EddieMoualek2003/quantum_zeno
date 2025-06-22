import pygame
import sys
from zeno_demo_functions import *
import os
# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zeno Game")

# Colors
COLORS = {
    "BACKGROUND": (233, 206, 255),
    "TEXT": (26, 0, 71),
    "INPUT_BOX": (199, 70, 175),
    "BUTTON": (148, 189, 242),
    "BUTTON_TEXT": (26, 0, 71),
    "INPUT_TEXT": (255, 255, 255),
    "EXIT_BTN": (177, 193, 254),
    "FIGURE_BOX": (255, 255, 255)  # White figure area
}

# Fonts
FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 48)

# UI elements
input_box = pygame.Rect(300, 250, 200, 40)
simulate_button = pygame.Rect(320, 320, 160, 50)
exit_button = pygame.Rect(20, 20, 80, 36)
figure_box = pygame.Rect(600, 150, 360, 320)

# State
user_input = ''
active_input = False
message = "Enter number of measurements (1–100):"

# Path to figure
FIGURE_PATH = "resource_folder/zeno_probability_plot.png"
loaded_figure = None  # Surface to hold the loaded image

def draw_interface():
    screen.fill(COLORS["BACKGROUND"])

    # Exit button
    pygame.draw.rect(screen, COLORS["EXIT_BTN"], exit_button, border_radius=10)
    exit_text = FONT.render("Exit", True, COLORS["TEXT"])
    screen.blit(exit_text, (exit_button.x + 10, exit_button.y + 5))

    # Title
    title = BIG_FONT.render("Zeno Game", True, COLORS["TEXT"])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    # Message
    instruction = FONT.render(message, True, COLORS["TEXT"])
    screen.blit(instruction, (100, 140))  # ? moved left and down

    # Input box
    pygame.draw.rect(screen, COLORS["INPUT_BOX"], input_box, border_radius=10)
    input_text = FONT.render(user_input, True, COLORS["INPUT_TEXT"])
    screen.blit(input_text, (input_box.x + 10, input_box.y + 5))

    # Simulate button
    pygame.draw.rect(screen, COLORS["BUTTON"], simulate_button, border_radius=10)
    button_text = FONT.render("Simulate", True, COLORS["BUTTON_TEXT"])
    screen.blit(button_text, (simulate_button.x + 20, simulate_button.y + 10))

    # Figure box label
    fig_label = FONT.render("Simulation Output", True, COLORS["TEXT"])
    screen.blit(fig_label, (figure_box.x + 50, figure_box.y - 35))

    # Try displaying the loaded image if available
    pygame.draw.rect(screen, COLORS["FIGURE_BOX"], figure_box, border_radius=15)
    pygame.draw.rect(screen, COLORS["TEXT"], figure_box, 2, border_radius=15)

    if loaded_figure:
        resized_fig = pygame.transform.scale(loaded_figure, (figure_box.width, figure_box.height))
        screen.blit(resized_fig, (figure_box.x, figure_box.y))


    pygame.display.flip()


# Main loop
clock = pygame.time.Clock()
running = True
while running:
    draw_interface()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active_input = True
            else:
                active_input = False

            if simulate_button.collidepoint(event.pos):
                # print("Simulate clicked with input:", user_input)
                # try:
                #     zeno_demo_main(numOperators=int(user_input))
                #     # In the future: draw figure here
                # except Exception as e:
                #     print("Error running simulation:", e)
                # Run simulation and load updated figure
                zeno_demo_main(numOperators=int(user_input))

                if os.path.exists(FIGURE_PATH):
                    loaded_figure = pygame.image.load(FIGURE_PATH)
                    print("Image loaded successfully.")
                else:
                    print("Plot not found at:", FIGURE_PATH)

            if exit_button.collidepoint(event.pos):
                running = False

        elif event.type == pygame.KEYDOWN and active_input:
            if event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            elif event.unicode.isdigit():
                user_input += event.unicode

    clock.tick(30)

pygame.quit()
sys.exit()
