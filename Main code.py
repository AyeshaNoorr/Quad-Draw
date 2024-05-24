import pygame
import sys
from quadtree_adt import *

pygame.init()

CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
canvas = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
pygame.display.set_caption("QuadDraw")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

color = BLACK
stroke_size = 3
current_color=BLACK

clock = pygame.time.Clock()

quadtree = create_quadtree((0, 0, CANVAS_WIDTH, CANVAS_HEIGHT), capacity=50)

points = []
show_quadtree = True

button_font = pygame.font.SysFont(None, 24)
button_texts = {
    "toggle_quadtree": button_font.render("Toggle Quadtree", True, BLACK),
    "red": button_font.render("Red", True, RED),
    "green": button_font.render("Green", True, GREEN),
    "blue": button_font.render("Blue", True, BLUE),
    "black": button_font.render("Black", True, BLACK),
    "eraser": button_font.render("Eraser", True, BLACK)
}
button_rects = {
    "toggle_quadtree": button_texts["toggle_quadtree"].get_rect(topleft=(10, 10)),
    "red": button_texts["red"].get_rect(topleft=(10, 50)),
    "green": button_texts["green"].get_rect(topleft=(10, 90)),
    "blue": button_texts["blue"].get_rect(topleft=(10, 130)),
    "black": button_texts["black"].get_rect(topleft=(10, 170)),
    "eraser": button_texts["eraser"].get_rect(topleft=(10, 210))
}

def draw_buttons():
    for button, text in button_texts.items():
        canvas.blit(text, button_rects[button])
        pygame.draw.rect(canvas, BLACK, button_rects[button], 1)

def draw_quadtree(canvas, quadtree):
    if quadtree['divided']:
        draw_quadtree(canvas, quadtree['northeast'])
        draw_quadtree(canvas, quadtree['northwest'])
        draw_quadtree(canvas, quadtree['southeast'])
        draw_quadtree(canvas, quadtree['southwest'])
    else:
        bounds = quadtree['bounds']
        pygame.draw.rect(canvas, (100, 100, 100), bounds, 1)  
        for point in quadtree['points']:
            pygame.draw.circle(canvas, (0, 0, 255), point, 2)

def erase_points(quadtree, eraser_rect):
    points_to_erase = check_range(quadtree, eraser_rect)
    for point in points_to_erase:
        remove_point(quadtree, point)
        # Remove point from strokes
        remove_point_from_strokes(point)

def remove_point_from_strokes(point):
    global all_strokes
    new_strokes = []
    for color, stroke_points in all_strokes:
        if point in stroke_points:
            index = stroke_points.index(point)
                                                    # If the point is not at the ends, split the stroke
            if 0 < index < len(stroke_points) - 1:
                new_strokes.append((color, stroke_points[:index]))
                new_strokes.append((color, stroke_points[index + 1:]))
            elif index == 0:
                new_strokes.append((color, stroke_points[1:]))
            elif index == len(stroke_points) - 1:
                new_strokes.append((color, stroke_points[:-1]))
        else:
            new_strokes.append((color, stroke_points))
    all_strokes = new_strokes

def backtrack_quadtree(quadtree, eraser_pos, eraser_size, eraser_rect):
    if intersects(quadtree, eraser_rect):
        if quadtree['divided']:
            backtrack_quadtree(quadtree['northeast'], eraser_pos, eraser_size, eraser_rect)
            backtrack_quadtree(quadtree['northwest'], eraser_pos, eraser_size, eraser_rect)
            backtrack_quadtree(quadtree['southeast'], eraser_pos, eraser_size, eraser_rect)
            backtrack_quadtree(quadtree['southwest'], eraser_pos, eraser_size, eraser_rect)
            if not quadtree['northeast']['points'] and \
               not quadtree['northwest']['points'] and \
               not quadtree['southeast']['points'] and \
               not quadtree['southwest']['points']:
                quadtree['northeast'] = None
                quadtree['northwest'] = None
                quadtree['southeast'] = None
                quadtree['southwest'] = None
                quadtree['divided'] = False
                draw_quadtree(canvas, quadtree)

running = True
drawing = False
all_strokes = []  
current_color = BLACK
eraser_mode = False
eraser_rect = pygame.Rect(0, 0, 35, 35)

while running:
    canvas.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  
                for button, rect in button_rects.items():
                    if rect.collidepoint(event.pos):
                        if button == "toggle_quadtree":
                            show_quadtree = not show_quadtree
                        elif button == "red":
                            current_color = RED
                        elif button == "green":  
                            current_color = GREEN
                        elif button == "blue":
                            current_color = BLUE
                        elif button == "black":
                            current_color = BLACK
                        elif button == "eraser":
                            eraser_mode = not eraser_mode
                        break  
                else:
                    drawing = True
                    points.clear()

        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                drawing = False
                all_strokes.append((current_color, points.copy()))  
        elif event.type == pygame.MOUSEMOTION and drawing:
            pos = pygame.mouse.get_pos()
            if eraser_mode:
                erase_points(quadtree,eraser_rect)
                backtrack_quadtree(quadtree,pos,(35,35),eraser_rect)
                eraser_rect.center = pygame.mouse.get_pos()
            else:
                points.append(pos)
                if contains_point(quadtree, pos):
                    insert(quadtree, pos)

    if eraser_mode:
    
        pygame.draw.rect(canvas, RED, eraser_rect)  # Adjust color as needed
        eraser_center = pygame.mouse.get_pos()
        eraser_rect.center = eraser_center  # Update eraser rectangle position
        erase_points(quadtree, eraser_rect)
        backtrack_quadtree(quadtree,pos,(35,35),eraser_rect)
       
        

    for stroke_color, stroke_points in all_strokes:
        if len(stroke_points) > 1:  
            pygame.draw.lines(canvas, stroke_color, False, stroke_points, stroke_size)

    if len(points) > 1 and drawing and not eraser_mode:  
         pygame.draw.lines(canvas, current_color, False, points, stroke_size)  

    if show_quadtree:
        draw_quadtree(canvas, quadtree)

    draw_buttons()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
