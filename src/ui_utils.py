import pygame
from src.constants import *

def get_fonts(width, height):
    font_size = int(height * 0.03)
    large_font_size = int(height * 0.05)
    font = pygame.font.SysFont('Verdana', font_size)
    large_font = pygame.font.SysFont('Verdana', large_font_size)
    return font, large_font

def draw_text(screen, text, x, y, font, color=TEXT_COLOR):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_text_left(screen, text, x, y, font, color=TEXT_COLOR):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def draw_wrapped_text(screen, text, x, y, max_width, font, color=TEXT_COLOR):
    words = text.split(' ')
    lines = []
    current_line = words[0] if words else ""
    
    if words:
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
    start_y = y - (total_height // 2) + (line_height // 2)
    
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(x, start_y + i * line_height))
        screen.blit(text_surface, text_rect)

def draw_progress_bar(screen, x, y, width, height, progress, color=LIGHT_BLUE):
    pygame.draw.rect(screen, TEXTBOX_COLOR, (x, y, width, height))
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, width, height), 1)

    if progress > 0:
        pygame.draw.rect(screen, color, (x, y, int(width * progress), height))
