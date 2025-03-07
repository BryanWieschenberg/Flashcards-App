import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
FONT = pygame.font.SysFont(None, 36)  # Arial has better Unicode support

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flashcard Program")

# Flashcard data (key: term, value: definition)
flashcards = {
    "Python": "A high-level, interpreted programming language",
    "Java": "A class-based, object-oriented programming language",
    "C++": "A general-purpose programming language",
    "JavaScript": "A high-level, interpreted programming language",
    "HTML": "Standard markup language for documents",
    "CSS": "Style sheet language used for describing the presentation of a document",
    "SQL": "Language used to communicate with databases",
    "API": "Application Programming Interface",
    "GUI": "Graphical User Interface",
    "IDE": "Integrated Development Environment",
    "OOP": "Object-Oriented Programming",
    "CLI": "Command Line Interface",
    "URL": "Uniform Resource Locator",
    "HTTP": "Hypertext Transfer Protocol",
    "HTTPS": "Hypertext Transfer Protocol Secure",
    "FTP": "File Transfer Protocol",
    "SSH": "Secure Shell",
    "DNS": "Domain Name System"
}

# Settings - Show term or definition first?
show_term_first = True  # User selection before starting

# Flashcard mechanics
cards = list(flashcards.items())  # Convert to a list
# random.shuffle(cards)
needs_study = []  # Stores cards marked as "Needs to Study"
current_index = 0
flipped = False

def draw_text(text, x, y, color=BLACK):
    """Helper function to draw centered text"""
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def show_settings():
    """Settings menu to allow user to choose whether to show terms or definitions first"""
    global show_term_first
    running = True
    while running:
        screen.fill(WHITE)
        draw_text("Choose what to display first:", WIDTH//2, HEIGHT//3)
        draw_text("Press 'T' for Terms first, 'D' for Definitions first", WIDTH//2, HEIGHT//2)
        
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

def draw_flashcard():
    """Displays the current flashcard"""
    screen.fill(WHITE)
    
    if current_index >= len(cards):
        draw_text("Review Complete!", WIDTH//2, HEIGHT//2)
        draw_text("Press ESC to Exit", WIDTH//2, HEIGHT//2 + 50)
        pygame.display.flip()
        return
    
    term, definition = cards[current_index]
    text = term if (show_term_first and not flipped) or (not show_term_first and flipped) else definition

    pygame.draw.rect(screen, BLACK, (150, 200, 500, 200), 3)  # Flashcard border
    draw_text(text, WIDTH//2, HEIGHT//2)
    
    draw_text("[SPACE] Flip Card | [←] Needs Study | [→] Understood", WIDTH//2, HEIGHT - 50, BLACK)

def main():
    """Main function handling game loop"""
    global current_index, flipped

    show_settings()  # Ask for user preference
    
    running = True
    while running:
        screen.fill(WHITE)
        draw_flashcard()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_index >= len(cards):  # If all cards are reviewed
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    continue
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    flipped = not flipped  # Flip the card
                elif event.key == pygame.K_LEFT:  # Needs Study
                    needs_study.append(cards[current_index])
                    current_index += 1
                    flipped = False
                elif event.key == pygame.K_RIGHT:  # Understood
                    current_index += 1
                    flipped = False

        # If we finish the first pass, restart with the "Needs Study" stack
        if current_index >= len(cards) and needs_study:
            cards[:] = needs_study
            needs_study.clear()
            current_index = 0
            # random.shuffle(cards)  # Shuffle for variety

    pygame.quit()

if __name__ == "__main__":
    main()
