import pygame
import os
from src.constants import *
from src.ui_utils import *
from src.session_manager import SessionManager

class FlashcardApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Flashcard App")
        
        self.session = SessionManager()
        self.font, self.large_font = get_fonts(self.width, self.height)
        self.update_layout()
        
        self.correct_sound = pygame.mixer.Sound(CORRECT_SOUND_PATH)
        self.wrong_sound = pygame.mixer.Sound(WRONG_SOUND_PATH)
        
        self.clock = pygame.time.Clock()
        self.status_message = ""
        self.status_color = TEXT_COLOR
        self.status_timer = 0

    def update_sizes(self, width, height):
        self.width, self.height = width, height
        self.font, self.large_font = get_fonts(self.width, self.height)
        self.update_layout()

    def update_layout(self):
        self.card_width = int(self.width * 0.85)
        self.card_height = int(self.height * 0.7)
        self.card_x = (self.width - self.card_width) // 2
        self.card_y = (self.height - self.card_height) // 2

    def set_status(self, message, color, duration=60):
        self.status_message = message
        self.status_color = color
        self.status_timer = duration

    def show_main_menu(self):
        has_saved_session = os.path.exists("session.json")
        running = True
        while running:
            self.screen.fill(BG_COLOR)
            
            y_offset = int(self.height * 0.2)
            draw_text(self.screen, "Flashcard App", self.width // 2, y_offset, self.large_font, BRIGHT_GREEN)
            
            y_offset += int(self.height * 0.15)
            if has_saved_session:
                draw_text(self.screen, "(C) Continue Last Session", self.width // 2, y_offset, self.font)
                y_offset += int(self.height * 0.05)
            
            draw_text(self.screen, "(N) Start New Session", self.width // 2, y_offset, self.font)
            
            y_offset += int(self.height * 0.1)
            mode_text = f"Display: {'Terms' if self.session.show_term_first else 'Definitions'} First (Press T/D)"
            draw_text(self.screen, mode_text, self.width // 2, y_offset, self.font, LIGHT_BLUE)
            
            y_offset += int(self.height * 0.05)
            shuffle_text = f"Shuffle: {'ENABLED' if self.session.shuffle_enabled else 'DISABLED'} (Press S)"
            draw_text(self.screen, shuffle_text, self.width // 2, y_offset, self.font, GREEN if self.session.shuffle_enabled else LIGHT_BLUE)
            
            draw_text(self.screen, "Press ESC to Quit", self.width // 2, self.height - 50, self.font)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.VIDEORESIZE:
                    self.update_sizes(event.w, event.h)
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c and has_saved_session:
                        self.session.load_session()
                        return "STUDY"
                    if event.key == pygame.K_n:
                        self.session.clear_session()
                        return "STUDY"
                    if event.key == pygame.K_t:
                        self.session.show_term_first = True
                    if event.key == pygame.K_d:
                        self.session.show_term_first = False
                    if event.key == pygame.K_s:
                        self.session.toggle_shuffle()
                    if event.key == pygame.K_ESCAPE:
                        return "QUIT"
        return "QUIT"

    def draw_study_screen(self, flipped, session_start_time):
        self.screen.fill(BG_COLOR)
        
        mode_text = "Term Mode  " if self.session.show_term_first else "Definition Mode  "
        shuffle_text = "Shuffled" if self.session.shuffle_enabled else "Unshuffled"
        draw_text_left(self.screen, mode_text, 20, 20, self.font)
        
        base_width = self.font.size(mode_text)[0]
        draw_text_left(self.screen, shuffle_text, 20 + base_width + 10, 20, self.font, GREEN if self.session.shuffle_enabled else LIGHT_BLUE)
        
        if self.session.current_index < len(self.session.cards):
            counter_text = f"Card {self.session.current_index + 1}/{len(self.session.cards)}"
            draw_text(self.screen, counter_text, self.width // 2, int(self.height * 0.04), self.font)
            
            mastery_text = f"Mastered {len(self.session.mastered_indices)}/{self.session.current_index}"
            draw_text(self.screen, mastery_text, self.width // 2, int(self.height * 0.08), self.font, GREEN)
            
            term, definition = self.session.cards[self.session.current_index]
            text = term if not flipped else definition
            if not self.session.show_term_first:
                text = definition if not flipped else term
                
            pygame.draw.rect(self.screen, TEXTBOX_COLOR, (self.card_x + 3, self.card_y + 3, self.card_width - 6, self.card_height - 6))
            pygame.draw.rect(self.screen, BORDER_COLOR, (self.card_x, self.card_y, self.card_width, self.card_height), 3)
            draw_wrapped_text(self.screen, text, self.width // 2, self.card_y + self.card_height // 2, self.card_width - 40, self.large_font)
            
            if flipped:
                label = "(Showing Definition)" if self.session.show_term_first else "(Showing Term)"
                draw_text(self.screen, f"Flipped {label}", self.width // 2, self.card_y + self.card_height + int(self.height * 0.03), self.font, LIGHT_BLUE)
            
            progress = self.session.current_index / len(self.session.cards)
            draw_progress_bar(self.screen, self.card_x, self.card_y + self.card_height + int(self.height * 0.01), self.card_width, 10, progress)
            
        if self.status_message:
            draw_text(self.screen, self.status_message, self.width // 2, self.card_y + self.card_height + int(self.height * 0.07), self.font, self.status_color)
            
        instructions = "[SPACE] Flip   |   [LEFT] Study   |   [RIGHT] Mastered   |   [BACK] Undo   |   [ESC] Menu"
        draw_text(self.screen, instructions, self.width // 2, self.height - 30, self.font)

    def show_summary(self, session_start_time):
        total = len(self.session.all_cards)
        mastered = len(self.session.mastered_indices)
        accuracy = (mastered / total * 100) if total > 0 else 0
        
        elapsed = (pygame.time.get_ticks() - session_start_time) // 1000
        mins, secs = elapsed // 60, elapsed % 60
        
        running = True
        while running:
            self.screen.fill(BG_COLOR)
            draw_text(self.screen, "Session Summary", self.width // 2, int(self.height * 0.2), self.large_font, BRIGHT_GREEN)
            draw_text(self.screen, f"Cards Studied: {total}", self.width // 2, int(self.height * 0.4), self.font)
            draw_text(self.screen, f"Mastery Rate: {accuracy:.1f}%", self.width // 2, int(self.height * 0.5), self.font, GREEN)
            draw_text(self.screen, f"Time Spent: {mins}m {secs}s", self.width // 2, int(self.height * 0.6), self.font)
            draw_text(self.screen, "Press ENTER to Finish", self.width // 2, int(self.height * 0.8), self.font)
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    self.update_sizes(event.w, event.h)
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        running = False
        
        self.session.clear_session()

    def run_study_session(self):
        study_running = True
        flipped = False
        start_time = pygame.time.get_ticks()
        
        while study_running:
            self.draw_study_screen(flipped, start_time)
            pygame.display.flip()
            
            if self.status_timer > 0:
                self.status_timer -= 1
                if self.status_timer == 0: self.status_message = ""
                
            if self.session.is_complete():
                if self.session.needs_study:
                    if self.session.get_next_loop():
                        flipped = False
                        continue
                self.show_summary(start_time)
                study_running = False
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.session.save_session()
                    return "QUIT"
                if event.type == pygame.VIDEORESIZE:
                    self.update_sizes(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.session.save_session()
                        study_running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN):
                        flipped = not flipped
                    elif event.key == pygame.K_LEFT:
                        self.wrong_sound.play()
                        self.session.mark_needs_study(self.session.current_index)
                        self.session.current_index += 1
                        flipped = False
                        self.set_status("Need to Study", RED)
                    elif event.key == pygame.K_RIGHT:
                        self.correct_sound.play()
                        self.session.mark_mastered(self.session.current_index)
                        self.session.current_index += 1
                        flipped = False
                        self.set_status("Mastered!", GREEN)
                    elif event.key == pygame.K_BACKSPACE:
                        if self.session.current_index > 0:
                            self.session.current_index -= 1
                            self.session.undo_action(self.session.current_index)
                            flipped = False
                            self.set_status("Undone", LIGHT_BLUE)
            
            self.clock.tick(60)
        return "MENU"

    def run(self):
        state = "MENU"
        while state != "QUIT":
            if state == "MENU":
                state = self.show_main_menu()
            elif state == "STUDY":
                state = self.run_study_session()
        pygame.quit()

if __name__ == "__main__":
    app = FlashcardApp()
    app.run()
