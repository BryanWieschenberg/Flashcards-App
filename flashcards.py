import pygame
import random
import csv
import tkinter as tk
from pygame import mixer

pygame.init()
root = tk.Tk()

WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (200, 200, 200)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
LIGHT_BLUE = (135, 206, 250)
BRIGHT_GREEN = (0, 255, 0)

FONT_SIZE = int(HEIGHT * 0.02)
LARGE_FONT_SIZE = int(HEIGHT * 0.03)
FONT = pygame.font.SysFont('Verdana', FONT_SIZE)
LARGE_FONT = pygame.font.SysFont('Verdana', LARGE_FONT_SIZE)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flashcard App")

show_term_first = True

needs_study = []
mastered_cards = []
mastered_count = 0
current_index = 0
flipped = False
status_message = ""
status_color = TEXT_COLOR
status_timer = 0
shuffle_enabled = False

pygame.mixer.init()
correct_sound = pygame.mixer.Sound("correct.wav")
wrong_sound = pygame.mixer.Sound("wrong.wav")

CARD_WIDTH = int(WIDTH * 0.7)
CARD_HEIGHT = int(HEIGHT * 0.5)
CARD_X = (WIDTH - CARD_WIDTH) // 2
CARD_Y = (HEIGHT - CARD_HEIGHT) // 2

def update_sizes():
    global FONT_SIZE, LARGE_FONT_SIZE, FONT, LARGE_FONT, CARD_WIDTH, CARD_HEIGHT, CARD_X, CARD_Y
    
    FONT_SIZE = int(HEIGHT * 0.02)
    LARGE_FONT_SIZE = int(HEIGHT * 0.03)
    FONT = pygame.font.SysFont('Verdana', FONT_SIZE)
    LARGE_FONT = pygame.font.SysFont('Verdana', LARGE_FONT_SIZE)
    
    CARD_WIDTH = int(WIDTH * 0.7)
    CARD_HEIGHT = int(HEIGHT * 0.5)
    CARD_X = (WIDTH - CARD_WIDTH) // 2
    CARD_Y = (HEIGHT - CARD_HEIGHT) // 2

def draw_text(text, x, y, color=TEXT_COLOR, large=False):
    font = LARGE_FONT if large else FONT
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_text_left(text, x, y, color=TEXT_COLOR):
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def draw_wrapped_text(text, x, y, max_width, color=TEXT_COLOR, large=False):
    font = LARGE_FONT if large else FONT
    words = text.split(' ')
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        test_line = current_line + ' ' + word
        test_width = font.size(test_line)[0]
        
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    
    start_y = y - (total_height // 2)
    
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(x, start_y + i * line_height))
        screen.blit(text_surface, text_rect)

def reset_study_session():
    global needs_study, mastered_cards, mastered_count, current_index, flipped, status_message, status_timer
    needs_study = []
    mastered_cards = []
    mastered_count = 0
    current_index = 0
    flipped = False
    status_message = ""
    status_timer = 0

def show_settings():
    global show_term_first, shuffle_enabled
    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_text("Choose what to display first:", WIDTH // 2, int(HEIGHT * 0.33))
        draw_text("Press 'T' for Terms first, 'D' for Definitions first", WIDTH // 2, int(HEIGHT * 0.5))
        
        shuffle_status = "Shuffle: ENABLED" if shuffle_enabled else "Shuffle: DISABLED"
        status_color = BRIGHT_GREEN if shuffle_enabled else LIGHT_BLUE
        draw_text(shuffle_status, WIDTH // 2, int(HEIGHT * 0.6), color=status_color)
        
        draw_text("Press 'S' to toggle shuffle", WIDTH // 2, int(HEIGHT * 0.65))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    show_term_first = True
                    running = False
                elif event.key == pygame.K_d:
                    show_term_first = False
                    running = False
                elif event.key in (pygame.K_s, pygame.K_r):
                    shuffle_enabled = not shuffle_enabled
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    root.destroy()
                    exit()

def draw_flashcard():
    """Displays the current flashcard"""
    screen.fill(BG_COLOR)
    
    mode_text = "Term Mode  " if show_term_first else "Definition Mode  "
    shuffle_text = "Shuffled" if shuffle_enabled else "Unshuffled"
    shuffle_color = BRIGHT_GREEN if shuffle_enabled else LIGHT_BLUE
    draw_text_left(mode_text, 20, 20)

    base_width = FONT.size(mode_text)[0]
    draw_text_left(shuffle_text, 20 + base_width + 10, 20, color=shuffle_color)

    if current_index >= len(cards):
        draw_text("Review Complete!", WIDTH // 2, HEIGHT // 2, large=True)
        draw_text("Press ESC to Return to Main Menu", WIDTH // 2, HEIGHT // 2 + int(HEIGHT * 0.1))
        pygame.display.flip()
        return
    
    counter_text = f"Card {current_index + 1}/{len(cards)}"
    draw_text(counter_text, WIDTH // 2, int(HEIGHT * 0.08))
    
    viewed_cards = min(current_index, len(cards))
    mastery_text = f"Mastered {mastered_count}/{viewed_cards}"
    draw_text(mastery_text, WIDTH // 2, int(HEIGHT * 0.15), GREEN)
    
    term, definition = cards[current_index]

    if show_term_first:
        text = term if not flipped else definition
    else:
        text = definition if not flipped else term

    pygame.draw.rect(screen, BORDER_COLOR, (CARD_X, CARD_Y, CARD_WIDTH, CARD_HEIGHT), 3)
    
    draw_wrapped_text(text, WIDTH // 2, CARD_Y + CARD_HEIGHT // 2, CARD_WIDTH - 40, TEXT_COLOR, large=True)
    
    if flipped:
        if show_term_first:
            draw_text("Flipped (Showing Definition)", WIDTH // 2, CARD_Y + CARD_HEIGHT + int(HEIGHT * 0.05))
        else:
            draw_text("Flipped (Showing Term)", WIDTH // 2, CARD_Y + CARD_HEIGHT + int(HEIGHT * 0.05))
    
    if status_message:
        draw_text(status_message, WIDTH // 2, CARD_Y + CARD_HEIGHT + int(HEIGHT * 0.1), status_color)
    
    instruction_text = "[SPACE/UP/DOWN] Flip Card   |   [LEFT] Need to Study   |   [RIGHT] Mastered   |   [BACKSPACE] Previous Card   |   [ESC] Main Menu"
    draw_text(instruction_text, WIDTH // 2, HEIGHT - int(HEIGHT * 0.05))

def main():
    global current_index, flipped, status_message, status_color, status_timer, mastered_count, WIDTH, HEIGHT, screen, cards, mastered_cards

    main_running = True
    while main_running:
        reset_study_session()
        
        show_settings()  
        
        cards = list(flashcards.items())
        
        if shuffle_enabled:
            random.shuffle(cards)

        study_running = True
        clock = pygame.time.Clock()
        
        while study_running:
            screen.fill(BG_COLOR)
            draw_flashcard()
            pygame.display.flip()

            if status_timer > 0:
                status_timer -= 1
                if status_timer == 0:
                    status_message = ""

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    root.destroy()
                    exit()
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.size
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    update_sizes()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        study_running = False
                    elif current_index >= len(cards):
                        if event.key == pygame.K_RETURN:
                            study_running = False
                    else:
                        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN):
                            flipped = not flipped
                        elif event.key == pygame.K_LEFT:
                            wrong_sound.play()
                            needs_study.append(cards[current_index])
                            status_message = "Need to Study"
                            status_color = RED
                            status_timer = 60
                            
                            if current_index in mastered_cards:
                                mastered_cards.remove(current_index)
                                mastered_count -= 1
                                
                            current_index += 1
                            flipped = False
                        elif event.key == pygame.K_RIGHT:
                            correct_sound.play()
                            status_message = "Mastered!"
                            status_color = GREEN
                            status_timer = 60

                            if current_index not in mastered_cards:
                                mastered_cards.append(current_index)
                                mastered_count += 1
                                
                            current_index += 1
                            flipped = False
                        elif event.key == pygame.K_BACKSPACE:
                            if current_index > 0:
                                current_index -= 1
                                flipped = False
                                status_message = "Previous Card"
                                status_color = LIGHT_BLUE
                                status_timer = 60

                                if current_index in mastered_cards:
                                    mastered_cards.remove(current_index)
                                    mastered_count -= 1

            if current_index >= len(cards) and needs_study:
                cards[:] = needs_study
                needs_study.clear()
                current_index = 0
                mastered_count = 0
                mastered_cards = []
                
            if current_index >= len(cards) and not needs_study:
                pass
                
            clock.tick(60)
            
if __name__ == "__main__":
    flashcards = {}
    # Input terms and definitions in terms.csv
    with open("terms.csv", newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                term, definition = row[0].strip(), row[1].strip()
                flashcards[term] = definition
    
    main()
