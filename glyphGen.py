import pygame
import os
import math
from constants import *
import eztext
import shelve
import random
from collections import deque

# -----Some globally-relevant stuff-----

lock_menus = True
mode = "line"
debug = True
color = BLACK
line_thickness = 3

pygame.init()
pygame.display.set_caption("CityBlocks, by kcg")
text16 = pygame.font.Font("freesansbold.ttf", 16)

# -----Classes -----

class Line:
    def __init__(self, color, start, end, thickness):
        self.color = color
        self.start = start
        self.end = end
        self.thickness = thickness

    def draw(self):
        pygame.draw.line(screen,self.color,self.start,self.end,self.thickness)

class Fill:
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos

    def draw(self):
        pygame.draw.rect(screen, self.color,
                             [self.pos[0]+2,self.pos[1]+2,TILE_SIZE-3, TILE_SIZE-3])

class Triangle:
    def __init__(self, color, start, mid, end):
        self.color = color
        self.start = start
        self.mid = mid
        self.end = end

    def draw(self):
        pygame.draw.polygon(screen,self.color, [self.start, self.mid, self.end])

class Circle:
    def __init__(self, color, center, radius, thick):
        self.color = color
        self.center = center
        self.radius = radius
        self.thick = thick

    def draw(self):
        pygame.draw.circle(screen, self.color, self.center, self.radius, self.thick)

class Char:
    def __init__(self, color, pos, char):
        self.color = color
        self.pos = pos
        self.char = char

    def draw(self):
        write_text = text16.render("{0}".format(self.char), True, self.color)
        write_rect = write_text.get_rect(bottomleft = (self.pos[0]+4,self.pos[1]+20))
        screen.blit(write_text, write_rect)

class Node:
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos

    def draw(self):
        draw_node(self.pos[0], self.pos[1], self.color)

# -----Draw Methods-----

def create_screen():
    screen = pygame.display.set_mode(SCREEN_RES)
    return screen

def refresh_screen(screen):
    screen.fill(WHITE)
    #draw_all_lines()
    #draw_all_nodes()

def draw_screen():
    refresh_screen(screen)
    draw_objects()
    draw_bot_text()

def draw_all_lines():
    bigger = 0
    if SCREEN_WIDTH > SCREEN_HEIGHT:
        bigger = SCREEN_WIDTH / TILE_SIZE
    else:
        bigger = SCREEN_HEIGHT / TILE_SIZE
    for i in range(0, bigger):
        pygame.draw.line(screen, GREY, (i*TILE_SIZE,0), (i*TILE_SIZE,
                                                        SCREEN_HEIGHT), 1)
        pygame.draw.line(screen, GREY, (0,i*TILE_SIZE), (SCREEN_WIDTH,
                                                        i*TILE_SIZE), 1)

def draw_all_nodes():
    for j in range(1, SCREEN_WIDTH / TILE_SIZE):
        for k in range(1, SCREEN_HEIGHT / TILE_SIZE):
            draw_node(j*TILE_SIZE, k*TILE_SIZE, GREY)

def draw_node(x,y,color):
    # pygame.draw.rect(screen, color, [x-2, y-2, 5, 5])
    pass

def draw_bot_text():
    mode_text = text16.render(" Mode = {0}".format(mode.capitalize()), True,
                    BLACK, GREY)
    color_text = text16.render("Color = {0}".format(color), True, color, GREY)
    mouse_text = text16.render("Mouse Pos = {0}".format(
                    pygame.mouse.get_pos()), True, BLACK, GREY)
    mode_rect = mode_text.get_rect(bottomleft = (0, SCREEN_HEIGHT))
    color_rect = color_text.get_rect(bottomleft = (160, SCREEN_HEIGHT))
    mouse_rect = mouse_text.get_rect(bottomleft = (360, SCREEN_HEIGHT))
    pygame.draw.rect(screen, GREY, (0, mode_rect.top, SCREEN_WIDTH,
                                    SCREEN_HEIGHT))
    screen.blit(mode_text, mode_rect)
    screen.blit(color_text, color_rect)
    screen.blit(mouse_text, mouse_rect)

def draw_selected(sel):
    draw_selected_node(sel)
    draw_selected_text(sel)
    pygame.display.flip()

def draw_selected_node(sel):
    try:
        pygame.draw.rect(screen,HPINK,[sel[0]-2,sel[1]-2,5,5])
    except TypeError:
        for i in sel:
            pygame.draw.rect(screen,HPINK,[i[0]-2,i[1]-2,5,5])

def draw_selected_text(sel):
    info_text = text16.render("Selected = {0}".format(sel),True,BLACK,GREY)
    info_rect = info_text.get_rect(bottomleft = (500, SCREEN_HEIGHT))
    pygame.draw.rect(screen, GREY, (500, info_rect.top, (SCREEN_WIDTH-500),
                                    SCREEN_HEIGHT))
    screen.blit(info_text, info_rect)

def draw_objects():
    global objects
    for i in objects:
        i.draw()

# -----Get positions in various ways -----

def get_pos():
    x, y = pygame.mouse.get_pos()
    x = int(round_to_nearest(x, TILE_SIZE/2.0))
    y = int(round_to_nearest(y, TILE_SIZE/2.0))
    return (x,y)

def get_fill_pos():
    x, y = pygame.mouse.get_pos()
    x = int(round_to_nearest(x, TILE_SIZE))
    y = int(round_to_nearest(y, TILE_SIZE))
    return (x,y)

def get_wait_pos():
    while True:
        draw_selected(get_pos())
        draw_screen()
        pygame.display.flip()
        e = pygame.event.wait()
        if e.type == pygame.QUIT:
            return None
        elif e.type == pygame.MOUSEBUTTONUP:
            return get_pos()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return None

def round_to_nearest(number, to):
    return round(number / to, 0) * to

# -----Draw list appends-----

def circle():
    p1 = get_pos()
    draw_selected(p1)
    p2 = get_wait_pos()
    if not p2:
        return
    if p1[0] > p2[0]:
        a = p1[0] - p2[0]
    else:
        a = p2[0] - p1[0]
    if p1[1] > p2[1]:
        b = p2[1] - p1[1]
    else:
        b = p1[1] - p2[1]
    rad = int(math.sqrt(math.pow(a,2) + math.pow(b,2)))
    c = Circle(color, p1, rad)
    objects.append(c)

def fill():
    f = Fill(color, get_fill_pos())
    objects.append(f)

def line():
    p1 = get_pos()
    draw_selected(p1)
    p2 = get_wait_pos()
    if not p2:
        return
    ln = Line(color, p1, p2, line_thickness)
    objects.append(ln)

def triangle():
    p1 = get_pos()
    draw_selected(p1)
    p2 = get_wait_pos()
    if not p2:
        return
    draw_selected([p1,p2])
    p3 = get_wait_pos()
    if not p3:
        return
    t = Triangle(color, p1, p2, p3)
    objects.append(t)

def write():
    p1 = get_fill_pos()
    e = pygame.event.wait()
    while e.type != pygame.KEYDOWN:
        e = pygame.event.wait()
    if len(pygame.key.name(e.dict['key'])) < 2:
        msg = pygame.key.name(e.dict['key'])
        c = Char(color, p1, msg)
        checkChar(c)
        objects.append(c)

def checkChar(item):
    # used for overwriting characters
    global objects
    for o in objects:
        if isinstance(o, Char):
            if o.pos == item.pos:
                objects.remove(o)

def charErase():
    # used for erasing characters
    (x,y) = get_fill_pos()
    for o in objects:
        if isinstance(o,Char):
            if o.pos == (x,y):
                objects.remove(o)


# -----The Annihilator-----

def clear_lists():
    global objects
    objects = []

# -----Lists for drawing-----

objects = []

# -----Key dictionaries-----

key_to_mode = {
    pygame.K_F1: "line",
    pygame.K_F2: "fill",
    pygame.K_F3: "triangle",
    pygame.K_F4: "circle",
    pygame.K_F5: "write",
    pygame.K_F7: "char erase",
}

key_to_color = {
    pygame.K_r: RED,
    pygame.K_a: BLACK,
    pygame.K_b: BLUE,
    pygame.K_e: GREY,
    pygame.K_g: GREEN,
    pygame.K_w: WHITE,
    pygame.K_d: GOLD,
    pygame.K_y: YELLOW,
    pygame.K_o: BROWN
}

key_to_line_thickness = {
    pygame.K_1: 1,
    pygame.K_2: 3,
    pygame.K_3: 5
}

mode_to_method = {
    "circle": circle,
    "fill": fill,
    "line": line,
    "triangle": triangle,
    "write": write,
    "char erase": charErase,
}

# Save/Load

def save():
    textbox = eztext.Input(maxlength=45, color=(255,0,0), prompt="Save name: ")
    looping = True
    while looping:
        pygame.draw.rect(screen, WHITE, ((0, 0), (600, 20)))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN:
                    looping = False
        val = textbox.update(events)
        textbox.draw(screen)
        pygame.display.flip()
    file = shelve.open(val, 'n')
    file['objects'] = objects
    file.close()

def load():
    #global line_list, fill_list, triangle_list, circle_list, write_list
    #global symbol_list
    global objects

    textbox = eztext.Input(maxlength=45, color=(255,0,0), prompt="Load name: ")
    looping = True
    while looping:
        pygame.draw.rect(screen, WHITE, ((0, 0), (600, 20)))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN:
                    looping = False
        val = textbox.update(events)
        textbox.draw(screen)
        pygame.display.flip()
    try:
        file = shelve.open(val, 'r')
        objects = file['objects']
        file.close()
    except:
        print "File not found."

#
#
# -----StreetGen Stuff-----
#
#

class GenNode(Node):
    def __init__(self, color, pos, exits):
        Node.__init__(self, color, pos)
        self.exits = exits
        self.branches = []

    def draw(self):
        Node.draw(self)

    def create_branch(dir):
        self.branches.append(dir)

frontier = deque([])
nodes = []

def branchesToLines(n):
    ends = []
    distance = random.randint(1,10) * 15
    if 'n' in n.branches:
        ends.append((n.pos[0], n.pos[1] - distance))
    if 'e' in n.branches:
        ends.append((n.pos[0] + distance, n.pos[1]))
    if 's' in n.branches:
        ends.append((n.pos[0], n.pos[1] + distance))
    if 'w' in n.branches:
        ends.append((n.pos[0] - distance, n.pos[1]))

    for end in ends:
        new_node = GenNode(BLACK, end, ['n', 's', 'e', 'w'])
        objects.append(Line(BLACK, n.pos, end, 3))
        objects.append(new_node)
        frontier.append(new_node)

def newNode45(end):
    return GenNode(BLACK, end, ['n', 's', 'e', 'w'] * 20 + ['ne', 'se', 'sw', 'nw'])

def branchesToLines45(n):
    ends = []
    distance = random.randint(1,10) * 15
    if 'n' in n.branches:
        ends.append((n.pos[0], n.pos[1] - distance))
    if 'e' in n.branches:
        ends.append((n.pos[0] + distance, n.pos[1]))
    if 's' in n.branches:
        ends.append((n.pos[0], n.pos[1] + distance))
    if 'w' in n.branches:
        ends.append((n.pos[0] - distance, n.pos[1]))
    if 'ne' in n.branches:
        ends.append((n.pos[0] + distance, n.pos[1] - distance))
    if 'se' in n.branches:
        ends.append((n.pos[0] + distance, n.pos[1] + distance))
    if 'sw' in n.branches:
        ends.append((n.pos[0] - distance, n.pos[1] + distance))
    if 'nw' in n.branches:
        ends.append((n.pos[0] - distance, n.pos[1] - distance))

    for end in ends:
        if random.randint(0,5) < 4:
            new_node = newNode45(end)
            objects.append(Line(BLACK, n.pos, end, 3))
            objects.append(new_node)
            frontier.append(new_node)
        else:
            rad = random.randint(1,3) * 15
            objects.append(Circle(BLACK, n.pos, rad, random.randint(0,5)))
            new_poses = [(n.pos[0], n.pos[1] + rad), (n.pos[0], n.pos[1] - rad),
                        (n.pos[0] + rad, n.pos[1]), (n.pos[0] - rad, n.pos[1])]
            for i in new_poses:
                frontier.append(newNode45(end))

def pick_branches(n):
    if random.randint(0,10) > 8:
        return
    for i in range(0,3):
        n.branches.append(random.choice(n.exits))

def generate(steps):
    n = GenNode(BLACK, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), ['n', 's', 'e', 'w'])
    frontier.append(n)

    j = 0
    while len(frontier) > 0 and j < steps:
        j+=1
        if random.randint(0, 50) == 0:
            n = frontier.popleft()
        else:
            n = frontier.pop()
        pick_branches(n)
        branchesToLines45(n)

    if len(frontier) == 0:
        generate(steps)

    for i in frontier:
        objects.append(i)

def gen():
    global objects
    objects = []
    generate(4)

#
#
# -----Main-----
#
#

screen = create_screen()
refresh_screen(screen)

def main():
    global color, line_thickness, mode

    pygame.display.flip()

    gen()

    running = True
    while running:
        draw_selected(get_pos())
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in key_to_mode:
                mode = key_to_mode[event.key]

            elif event.key in key_to_color:
                color = key_to_color[event.key]

            elif event.key in key_to_line_thickness:
                line_thickness = key_to_line_thickness[event.key]

            elif event.key in key_to_color:
                color = key_to_color[event.key]

            elif event.key == pygame.K_DELETE:
                clear_lists()

            elif event.key == pygame.K_BACKSPACE:
                if len(objects) > 0:
                    objects.pop()

            elif event.key == pygame.K_HOME:
                save()

            elif event.key == pygame.K_END:
                load()

            elif event.key == pygame.K_SPACE:
                gen()

        elif event.type == pygame.MOUSEBUTTONUP:
            mode_to_method[mode]()

        draw_screen()
        pygame.display.flip()

#
#
# -----Run-----
#
#

if __name__ == "__main__":
    main()
    pygame.quit()
