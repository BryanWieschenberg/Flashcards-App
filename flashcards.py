import pygame
import random
import tkinter as tk

# Initialize pygame and tkinter
pygame.init()
root = tk.Tk()

# Get screen dimensions
WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # 800, 600  # 

# Dark mode color scheme
BG_COLOR = (30, 30, 30)          # Dark background
TEXT_COLOR = (255, 255, 255)     # Light text
BORDER_COLOR = (200, 200, 200)   # Light border for flashcards
GREEN = (50, 205, 50)
RED = (220, 20, 60)
LIGHT_BLUE = (135, 206, 250)  # Light blue for disabled shuffle
BRIGHT_GREEN = (0, 255, 0)    # Bright green for enabled shuffle

# Set font size proportional to screen height - made larger
FONT_SIZE = int(HEIGHT * 0.02)  # Increased from 0.03
LARGE_FONT_SIZE = int(HEIGHT * 0.03)  # Larger font for card content
FONT = pygame.font.SysFont('Verdana', FONT_SIZE)
LARGE_FONT = pygame.font.SysFont('Verdana', LARGE_FONT_SIZE)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flashcard App")

# Settings - Show term or definition first?
show_term_first = True  # User selection before starting

# Flashcard mechanics
needs_study = []  # Stores cards marked as "Needs to Study"
mastered_cards = []  # Track which cards have been mastered
mastered_count = 0  # Counter for mastered cards
current_index = 0
flipped = False
status_message = ""
status_color = TEXT_COLOR
status_timer = 0
shuffle_enabled = False  # Track if shuffle is enabled

# Calculate flashcard dimensions and position based on screen size - made larger
CARD_WIDTH = int(WIDTH * 0.7)  # Increased from 0.5
CARD_HEIGHT = int(HEIGHT * 0.5)  # Increased from 0.3
CARD_X = (WIDTH - CARD_WIDTH) // 2
CARD_Y = (HEIGHT - CARD_HEIGHT) // 2

def update_sizes():
    """Update all size variables based on current window dimensions"""
    global FONT_SIZE, LARGE_FONT_SIZE, FONT, LARGE_FONT, CARD_WIDTH, CARD_HEIGHT, CARD_X, CARD_Y
    
    # Update font sizes
    FONT_SIZE = int(HEIGHT * 0.02)
    LARGE_FONT_SIZE = int(HEIGHT * 0.03)
    FONT = pygame.font.SysFont('Verdana', FONT_SIZE)
    LARGE_FONT = pygame.font.SysFont('Verdana', LARGE_FONT_SIZE)
    
    # Update card dimensions
    CARD_WIDTH = int(WIDTH * 0.7)
    CARD_HEIGHT = int(HEIGHT * 0.5)
    CARD_X = (WIDTH - CARD_WIDTH) // 2
    CARD_Y = (HEIGHT - CARD_HEIGHT) // 2

def draw_text(text, x, y, color=TEXT_COLOR, large=False):
    """Helper function to draw centered text"""
    font = LARGE_FONT if large else FONT
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_text_left(text, x, y, color=TEXT_COLOR):
    """Helper function to draw left-aligned text"""
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def draw_wrapped_text(text, x, y, max_width, color=TEXT_COLOR, large=False):
    """Draw text that wraps to fit within max_width"""
    font = LARGE_FONT if large else FONT
    words = text.split(' ')
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        # Test width with another word added
        test_line = current_line + ' ' + word
        test_width = font.size(test_line)[0]
        
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    # Add the last line
    lines.append(current_line)
    
    # Calculate total height for centering
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    
    # Calculate starting y position to center text vertically
    start_y = y - (total_height // 2)
    
    # Draw each line
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(x, start_y + i * line_height))
        screen.blit(text_surface, text_rect)

def reset_study_session():
    """Reset all study session variables except shuffle setting"""
    global needs_study, mastered_cards, mastered_count, current_index, flipped, status_message, status_timer
    needs_study = []
    mastered_cards = []  # Reset the list of mastered cards
    mastered_count = 0
    current_index = 0
    flipped = False
    status_message = ""
    status_timer = 0

def show_settings():
    """Settings menu to allow user to choose whether to show terms or definitions first"""
    global show_term_first, shuffle_enabled
    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_text("Choose what to display first:", WIDTH // 2, int(HEIGHT * 0.33))
        draw_text("Press 'T' for Terms first, 'D' for Definitions first", WIDTH // 2, int(HEIGHT * 0.5))
        
        # Display shuffle status with appropriate color
        shuffle_status = "Shuffle: ENABLED" if shuffle_enabled else "Shuffle: DISABLED"
        status_color = BRIGHT_GREEN if shuffle_enabled else LIGHT_BLUE
        draw_text(shuffle_status, WIDTH // 2, int(HEIGHT * 0.6), color=status_color)
        
        # Draw toggle instruction closer to the shuffle status
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
                elif event.key in (pygame.K_s, pygame.K_r):  # Handle S or R key
                    shuffle_enabled = not shuffle_enabled  # Toggle shuffle state
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    root.destroy()
                    exit()

def draw_flashcard():
    """Displays the current flashcard"""
    screen.fill(BG_COLOR)
    
    # Display current mode in top left corner
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
    
    # Draw counter at the top
    counter_text = f"Card {current_index + 1}/{len(cards)}"
    draw_text(counter_text, WIDTH // 2, int(HEIGHT * 0.08))
    
    # Draw mastery counter - show correctly how many of the viewed cards have been mastered
    viewed_cards = min(current_index, len(cards))
    mastery_text = f"Mastered {mastered_count}/{viewed_cards}"
    draw_text(mastery_text, WIDTH // 2, int(HEIGHT * 0.15), GREEN)
    
    term, definition = cards[current_index]
    # Decide what to show based on the settings and flipped state
    if show_term_first:
        text = term if not flipped else definition
    else:
        text = definition if not flipped else term

    # Draw flashcard border (centered rectangle)
    pygame.draw.rect(screen, BORDER_COLOR, (CARD_X, CARD_Y, CARD_WIDTH, CARD_HEIGHT), 3)
    
    # Draw card text with larger font and word wrapping
    draw_wrapped_text(text, WIDTH // 2, CARD_Y + CARD_HEIGHT // 2, CARD_WIDTH - 40, TEXT_COLOR, large=True)
    
    # Show flipped status below the card
    if flipped:
        if show_term_first:
            draw_text("Flipped (Showing Definition)", WIDTH // 2, CARD_Y + CARD_HEIGHT + int(HEIGHT * 0.05))
        else:
            draw_text("Flipped (Showing Term)", WIDTH // 2, CARD_Y + CARD_HEIGHT + int(HEIGHT * 0.05))
    
    # Draw status message if there is one
    if status_message:
        draw_text(status_message, WIDTH // 2, CARD_Y + CARD_HEIGHT + int(HEIGHT * 0.1), status_color)
    
    # Draw instructions at bottom center
    instruction_text = "[SPACE/UP/DOWN] Flip Card   |   [LEFT] Need to Study   |   [RIGHT] Mastered   |   [BACKSPACE] Previous Card   |   [ESC] Main Menu"
    draw_text(instruction_text, WIDTH // 2, HEIGHT - int(HEIGHT * 0.05))

def main():
    """Main function handling game loop"""
    global current_index, flipped, status_message, status_color, status_timer, mastered_count
    global WIDTH, HEIGHT, screen  # Add these globals at the beginning of the function
    global cards, mastered_cards

    # Main app loop
    main_running = True
    while main_running:
        # Reset study session variables
        reset_study_session()
        
        # Show settings menu
        show_settings()  
        
        # Prepare the cards
        # Setup cards list from flashcards dictionary
        cards = list(flashcards.items())
        
        if shuffle_enabled:
            random.shuffle(cards)

        # Study session loop
        study_running = True
        clock = pygame.time.Clock()
        
        while study_running:
            screen.fill(BG_COLOR)
            draw_flashcard()
            pygame.display.flip()
            
            # Update status message timer
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
                        # Return to settings menu instead of exiting
                        study_running = False
                    elif current_index >= len(cards):  # If all cards are reviewed
                        if event.key == pygame.K_RETURN:
                            # Return to settings menu when ENTER is pressed at completion screen
                            study_running = False
                    else:
                        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN):
                            flipped = not flipped  # Flip the card
                        elif event.key == pygame.K_LEFT:  # Mark as "Needs Study"
                            needs_study.append(cards[current_index])
                            status_message = "Need to Study"
                            status_color = RED
                            status_timer = 60
                            
                            # If this card was previously mastered, remove from mastered list
                            if current_index in mastered_cards:
                                mastered_cards.remove(current_index)
                                mastered_count -= 1
                                
                            current_index += 1
                            flipped = False
                        elif event.key == pygame.K_RIGHT:  # Mark as "Understood"
                            status_message = "Mastered!"
                            status_color = GREEN
                            status_timer = 60
                            
                            # Only increment if this card wasn't already mastered
                            if current_index not in mastered_cards:
                                mastered_cards.append(current_index)
                                mastered_count += 1  # Increment mastery counter
                                
                            current_index += 1
                            flipped = False
                        elif event.key == pygame.K_BACKSPACE:  # Go back to previous card
                            if current_index > 0:
                                current_index -= 1
                                flipped = False
                                status_message = "Previous Card"
                                status_color = LIGHT_BLUE
                                status_timer = 60
                                # No need to adjust mastered_count here - we track it per card now
                                if current_index in mastered_cards:
                                    mastered_cards.remove(current_index)
                                    mastered_count -= 1

            # Restart with the "Needs Study" stack if first pass is complete
            if current_index >= len(cards) and needs_study:
                cards[:] = needs_study
                needs_study.clear()
                current_index = 0
                mastered_count = 0  # Reset mastery counter for the review round
                mastered_cards = []  # Reset the mastered cards list
                
            # Check if all cards are mastered and no cards need study
            if current_index >= len(cards) and not needs_study:
                # Wait for user to press ENTER or ESC
                # The actual return to menu happens in the event handler above
                pass
                
            clock.tick(60)  # 60 FPS
            
if __name__ == "__main__":
    
    # --- INPUT FLASHCARDS SET BELOW ---

    flashcards = {
        "": ""
    }
    
    # --- INPUT FLASHCARDS SET ABOVE ---

    main()
