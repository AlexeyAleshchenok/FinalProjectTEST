import sys
import time

import pygame
from DataCollector import NetworkDataCollector
import threading

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WIDTH, HEIGHT = 1920, 1080
FILE_SIZES = [50, 100, 200, 250]
NUM_REPEATS = [3, 5, 7, 10]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Network Test")
font = pygame.font.SysFont("", 40)
small_font = pygame.font.SysFont("", 30)

running = True
test_started = False
analyze_thread = threading.Thread()
selected_file = 50
selected_num_repeats = 3
collector = None
ping_results = {}
bandwidth_results = {}
animation_start_time = 0
frame_count = 0


def draw_text(text, text_font, color, x, y):
    text_surface = text_font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def draw_button(text, x, y, width, height, color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    draw_text(text, font, BLACK, x + width / 2, y + height / 2)


def draw_speed_graph(graph_screen, analyzed_bandwidth, bandwidth_res, position, size):
    graph_x, graph_y = position
    graph_width, graph_height = size
    max_speed = analyzed_bandwidth['max_speed']
    avg_speed = analyzed_bandwidth['average_speed']
    pygame.draw.rect(graph_screen, BLACK, (graph_x, graph_y, graph_width, graph_height), 2)

    normalized_speeds = []
    for value in bandwidth_res:
        normalized_speeds.append(value / max_speed)

    for j in range(1, len(normalized_speeds)):
        x1 = graph_x + (j - 1) * (graph_width / (len(normalized_speeds) - 1))
        y1 = graph_y + 75 + graph_height - (normalized_speeds[j - 1] * graph_height)
        x2 = graph_x + j * (graph_width / (len(normalized_speeds) - 1))
        y2 = graph_y + 75 + graph_height - (normalized_speeds[j] * graph_height)
        pygame.draw.line(graph_screen, BLUE, (x1, y1 * 1.25), (x2, y2 * 1.25), 2)

    avg_y = graph_y + 75 + graph_height - (avg_speed / max_speed * graph_height)
    pygame.draw.line(graph_screen, RED, (graph_x, avg_y * 1.25), (graph_x + graph_width, avg_y * 1.25),
                     2)

    graph_font = pygame.font.Font(None, 24)
    max_speed_text = graph_font.render(f"Max speed : {max_speed:.2f} KB/s", True, BLACK)
    avg_speed_text = graph_font.render(f"Average speed: {avg_speed:.2f} KB/s", True, BLACK)
    screen.blit(max_speed_text, (graph_x, graph_y - 20))
    screen.blit(avg_speed_text, (graph_x, graph_y + graph_height + 5))


def animate_loading(text, text_font, color, x, y, frame_counter):
    dot_count = (frame_counter // 200) % 4
    animated_text = text + '.' * dot_count
    draw_text(animated_text, text_font, color, x, y)


def analyze_network():
    global collector, ping_results, bandwidth_results
    collector.ping()
    collector.bandwidth()
    ping_results = collector.analyze_ping_results()
    bandwidth_results = collector.analyze_bandwidth_results()


def start_analysis():
    global test_started, analyze_thread
    test_started = True
    analyze_thread = threading.Thread(target=analyze_network())
    analyze_thread.start()


while running:
    screen.fill(WHITE)
    file_buttons_rects = []
    repeat_button_rects = []
    start_button_rects = None

    if not test_started:
        draw_text("Select file size (MB):", font, BLACK, WIDTH / 2, 150)
        draw_text("Select number of repeats:", font, BLACK, WIDTH / 2, 350)

        for i, file_size in enumerate(FILE_SIZES):
            button_x = WIDTH / 2 - (len(FILE_SIZES) * 50) + i * 100
            button_y = 200
            draw_button(str(file_size), button_x, button_y, 80, 50, GRAY)
            file_buttons_rects.append(pygame.Rect(button_x, button_y, 80, 50))

        for i, num_repeat in enumerate(NUM_REPEATS):
            button_x = WIDTH / 2 - (len(NUM_REPEATS) * 30) + i * 60
            button_y = 400
            draw_button(str(num_repeat), button_x, button_y, 50, 30, GRAY)
            repeat_button_rects.append(pygame.Rect(button_x, button_y, 20, 30))

        start_button_rects = pygame.Rect(WIDTH / 2 - 100, 500, 200, 50)
        draw_button("Start test", start_button_rects.x, start_button_rects.y, start_button_rects.width,
                    start_button_rects.height, GRAY)
        pygame.display.update()

    else:
        current_time = time.time()
        if current_time - animation_start_time > 5:
            draw_text("Ping Results:", font, BLACK, WIDTH / 4, 300)
            draw_text(f"Average Delay: {ping_results['average_delay']} ms", small_font, BLACK, WIDTH / 4, 350)
            draw_text(f"Total Loss: {ping_results['total_loss']}", small_font, BLACK, WIDTH / 4, 400)
            draw_text(f"Loss Percentage: {ping_results['loss_percentage']}%", small_font, BLACK, WIDTH / 4, 450)
            draw_text("Bandwidth", font, BLACK, WIDTH * 3 / 4, 300)
            draw_text(f"Average Speed: {bandwidth_results['average_speed']} Mbps", small_font, BLACK, WIDTH * 3 / 4,
                      350)
            draw_text(f"Max Speed: {bandwidth_results['max_speed']} Mbps", small_font, BLACK, WIDTH * 3 / 4, 400)
            draw_speed_graph(screen, bandwidth_results, collector.get_bandwidth_results(),
                             (WIDTH / 2, 500), (WIDTH / 3, HEIGHT / 3))
        else:
            animate_loading("Analyzing your network", font, BLACK, WIDTH / 2, HEIGHT / 2, frame_count)
            frame_count += 1
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not test_started:
                for i, file_size in enumerate(FILE_SIZES):
                    if file_buttons_rects[i].collidepoint(event.pos):
                        selected_file = file_size

                for i, num_repeat in enumerate(NUM_REPEATS):
                    if repeat_button_rects[i].collidepoint(event.pos):
                        selected_num_repeats = num_repeat

                if start_button_rects.collidepoint(event.pos):
                    collector = NetworkDataCollector(selected_file, selected_num_repeats)
                    animation_start_time = time.time()
                    start_analysis()

pygame.quit()
sys.exit()
