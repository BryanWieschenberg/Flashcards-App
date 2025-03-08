import pygame
import random
import tkinter as tk

# Initialize pygame and tkinter
pygame.init()
root = tk.Tk()

# Get screen dimensions
WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flashcard Program")

# Flashcard data (key: term, value: definition)
flashcards = {
    "Give the definition of a system call. Explain why it is needed.": 
        "A system call is a program that asks the OS to do something. It is needed because it ensures that user programs do not directly access critical parts of the system. This separation (user mode vs. kernel mode) protects system integrity.",
    
    "What is the difference between kernel mode and user mode? Explain how having two distinct modes aids in designing an OS.":
        "Kernel mode has unrestricted access to hardware and can execute any instruction, while user mode restricts programs from accessing critical hardware directly. This separation enhances security, protection, and abstraction, making the OS more robust and easier to manage.",
    
    "Explain what a monolithic kernel is with a real-world example and compare it to a microkernel.":
        "A monolithic kernel is an OS design where all components (device drivers, file systems, schedulers, etc.) run in kernel space as one large binary, as seen in Unix or Windows. In contrast, a microkernel (e.g., L4 or Mach) minimizes the core functions in kernel space, pushing other services to user space for improved modularity and security.",
    
    "Compare monolithic kernel and microkernel with layered-approach.":
        "A layered approach divides the OS into levels (with hardware at the bottom and the user interface at the top), which simplifies modifications but adds overhead from inter-layer communications. Monolithic kernels are fast and low-overhead but are complex and harder to modify, while microkernels simplify kernel functions but can incur communication overhead between user-space services.",
    
    "For each of the following system calls, give a scenario which would cause it to fail: fork(), exec(), unlink()":
        "fork() may fail if there is insufficient memory or resource limits are reached; exec() may fail if the target file cannot be opened or does not exist; unlink() may fail if the file is currently open or cannot be found.",
    
    "What is the purpose of interrupts? What are the differences between a trap and an interrupt? Can traps be generated intentionally by a user program? If so, for what purpose?":
        "Interrupts notify the CPU of external events that require its attention. A trap is an exception triggered by an error or specific condition in the running program. Traps can be intentionally generated by user programs (e.g., for debugging or error handling) to transfer control to the OS.",
    
    "How does the CPU know when memory operations are complete?":
        "The DMA (Direct Memory Access) controller uses interrupts and other signals to notify the CPU when a memory operation has finished. Although the CPU can perform other tasks while DMA is active, contention may occur if both try accessing the same memory, causing bus contention or priority inversion.",
    
    "How are iOS and Android similar? How are they different? Provide 3 examples for each.":
        "Similarities: Both use existing kernels (iOS uses a variant of Mac OS X; Android is Linux-based), follow layered architectures, and offer rich developer frameworks. Differences: iOS is closed-source while Android is open-source; iOS apps are typically developed in Objective-C/Swift whereas Android apps are developed in Java/Kotlin; iOS executes code natively while Android often uses a virtual machine.",
    
    "Why is the separation of mechanism and policy desirable?":
        "Separating mechanism and policy allows the core functions of an OS (mechanism) to remain stable while policies (rules and configurations) can be modified as needed. This leads to a flexible and easily customizable system.",
    
    "What are the advantages of using loadable kernel modules?":
        "Loadable kernel modules enable adding or removing functionality from the kernel without needing to recompile or reboot the system, allowing dynamic updates and easier maintenance.",
    
    "What are the 5 major activities of an OS in regard to file management?":
        "They are: (1) creation and deletion of files, (2) creation and deletion of directories, (3) providing primitives for file and directory manipulation, (4) mapping files onto secondary storage, and (5) backing up files on nonvolatile storage media.",
    
    "What are the advantages (2 points) and disadvantages (2 points) of using the same system call interface for manipulating both files and devices?":
        "Advantage: It unifies the interface, allowing devices to be treated like files, simplifying programming and driver development. Disadvantage: Some device-specific functionality may not map well to file operations, potentially reducing performance or functionality.",
    
    "The issue of resource utilization shows up in different forms in different types of operating systems. List what resources must be managed carefully in the following settings: mainframe or minicomputer systems, workstation connected to servers, and handheld computers or mobile devices.":
        "Mainframe/Minicomputer: Memory, CPU, and I/O resources. Workstation/Servers: Network bandwidth, CPU/memory utilization, and storage. Handheld/Mobile: Battery life, memory, and network bandwidth.",
    
    "What are the two models of inter-process communication (IPC)? What are the strengths and weaknesses of the two approaches?":
        "The two models are shared memory and message passing. Shared memory provides fast data transfer for large volumes but can pose security issues, while message passing is simpler and more secure for small amounts of data but may be slower for larger transfers.",
    
    "Explain how a system command (e.g. rm or mkdir) can be implemented:":
        "A system command such as 'rm' or 'mkdir' is implemented through a combination of system calls, library functions, and low-level OS operations. Typically, the command triggers a trap that calls the appropriate syscall (via an interrupt mechanism) to perform the requested action.",
    
    "Discuss one merit and one demerit of open-source software on operating system design.":
        "Merit: Flexibility – users can modify and customize the OS to meet their needs. Demerit: Fragmentation – multiple versions can lead to compatibility issues across different systems.",
    
    "Mention two OS design paradigms you learned in this course and briefly discuss merits and demerits of each.":
        "Two paradigms are message passing and shared memory. Message passing is fast for small data exchanges but slow for large data transfers, while shared memory is efficient for large data but can be insecure if shared memory addresses are exposed."
}

# Settings - Show term or definition first?
show_term_first = True  # User selection before starting

# Flashcard mechanics
cards = list(flashcards.items())  # Convert to a list of tuples
needs_study = []  # Stores cards marked as "Needs to Study"
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
        draw_text("Press ESC to Exit", WIDTH // 2, HEIGHT // 2 + int(HEIGHT * 0.1))
        pygame.display.flip()
        return
    
    # Draw counter at the top
    counter_text = f"Card {current_index + 1}/{len(cards)}"
    draw_text(counter_text, WIDTH // 2, int(HEIGHT * 0.08))
    
    # Draw mastery counter
    mastery_text = f"Mastered {mastered_count}/{current_index}"
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
    instruction_text = "[SPACE/UP/DOWN] Flip Card   |   [LEFT] Needs Study   |   [RIGHT] Understood"
    draw_text(instruction_text, WIDTH // 2, HEIGHT - int(HEIGHT * 0.05))

def main():
    """Main function handling game loop"""
    global current_index, flipped, status_message, status_color, status_timer, mastered_count

    show_settings()  # Ask for user preference
    
    if shuffle_enabled:
        random.shuffle(cards)

    running = True
    clock = pygame.time.Clock()
    
    while running:
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
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    root.destroy()
                    exit()
                elif current_index >= len(cards):  # If all cards are reviewed
                    continue
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN):
                    flipped = not flipped  # Flip the card
                elif event.key == pygame.K_LEFT:  # Mark as "Needs Study"
                    needs_study.append(cards[current_index])
                    status_message = "Needs Study"
                    status_color = RED
                    status_timer = 60  # Reduced from 60 to 30
                    current_index += 1
                    flipped = False
                elif event.key == pygame.K_RIGHT:  # Mark as "Understood"
                    status_message = "Mastered!"
                    status_color = GREEN
                    status_timer = 60  # Reduced from 60 to 30
                    mastered_count += 1  # Increment mastery counter
                    current_index += 1
                    flipped = False

        # Restart with the "Needs Study" stack if first pass is complete
        if current_index >= len(cards) and needs_study:
            cards[:] = needs_study
            needs_study.clear()
            current_index = 0
            mastered_count = 0  # Reset mastery counter for the review round
            
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()
    root.destroy()

if __name__ == "__main__":
    main()
