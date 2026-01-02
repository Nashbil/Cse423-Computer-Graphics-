from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ROOM_SIZE = 20.0
WALL_HEIGHT = 8.0
TIME_LIMIT = 60
FLOOR_Z = 0.0

PLAYER_HEIGHT = 1.7
PLAYER_RADIUS = 0.5
MOVE_SPEED = 0.15
ROTATION_SPEED = 2.0
MOUSE_SENSITIVITY = 0.2

COLOR_WALL = (0.4, 0.35, 0.3)
COLOR_FLOOR = (0.3, 0.25, 0.2)
COLOR_CEILING = (0.35, 0.3, 0.25)
COLOR_BOX = (0.6, 0.4, 0.2)
COLOR_LOCKED_BOX = (0.5, 0.2, 0.2)
COLOR_APPLE = (0.9, 0.1, 0.1)
COLOR_BANANA = (0.95, 0.9, 0.2)
COLOR_ORANGE = (1.0, 0.5, 0.0)
COLOR_GRAPE = (0.5, 0.0, 0.5)
COLOR_KEY = (0.9, 0.8, 0.1)

class GameState:
    def __init__(self):
        self.player_x = 0.0
        self.player_y = PLAYER_HEIGHT
        self.player_z = 5.0
        self.player_rotation_y = 0.0
        self.player_rotation_x = 0.0
        self.camera_mode = "first_person"
        self.camera_distance = 5.0
        self.move_forward = False
        self.move_backward = False
        self.move_left = False
        self.move_right = False
        self.rotate_left = False
        self.rotate_right = False
        self.start_time = time.time()
        self.time_remaining = TIME_LIMIT
        self.current_room = 0
        self.gate_open = [False, False]
        self.gate_opening_progress = [0.0, 0.0]
        self.gate_open_time = [0, 0]
        self.collected_fruits = []
        self.required_fruits = ["apple", "banana", "orange"]
        self.keys_found = 0
        self.held_object = None
        self.nearby_interactive = None
        self.current_message = ""
        self.message_timer = 0
        self.message_duration = 3.0
        self.final_score = 0
        self.game_completed = False

game = GameState()


# ROOM 1: FRUIT PUZZLE

class Fruit:
    def __init__(self, fruit_type, position):
        self.type = fruit_type
        self.position = list(position)
        self.collected = False
        self.size = 0.3
        self.color = {
            "apple": COLOR_APPLE,
            "banana": COLOR_BANANA,
            "orange": COLOR_ORANGE,
            "grape": COLOR_GRAPE
        }.get(fruit_type, (0.5, 0.5, 0.5))

class Box:
    def __init__(self, position, locked=False, contains_fruit=None, riddle=""):
        self.position = list(position)
        self.locked = locked
        self.opened = False
        self.contains_fruit = contains_fruit
        self.size = (1.0, 0.8, 1.0)
        self.riddle = riddle

class Key:
    def __init__(self, position, clue_text=""):
        self.position = list(position)
        self.collected = False
        self.size = 0.2
        self.clue_text = clue_text

class Clue:
    def __init__(self, position, text):
        self.position = list(position)
        self.text = text
        self.read = False
        self.size = 0.3

boxes = []
fruits = []
keys = []
clues = []

def initialize_room1_objects():
    global boxes, fruits, keys, clues
    
    boxes.append(Box([-6, 0, -6], locked=False, contains_fruit="apple", 
                     riddle="I am red and keep doctors away. What am I?"))
    boxes.append(Box([6, 0, -6], locked=True, contains_fruit="banana", 
                     riddle="Yellow and curved, monkeys love me. Find the key near the center."))
    boxes.append(Box([-6, 0, 6], locked=False, contains_fruit="grape", 
                     riddle="Purple and small, I grow in bunches."))
    boxes.append(Box([6, 0, 6], locked=True, contains_fruit="orange", 
                     riddle="I am round and orange. My key is in the corner."))
    
    keys.append(Key([-3, 0.5, 0], clue_text="This key unlocks the yellow fruit box."))
    keys.append(Key([3, 0.5, 3], clue_text="This key unlocks the orange fruit box."))
    
    clues.append(Clue([0, 0.5, -8], "Collect: Apple, Banana, and Orange to escape!"))
    clues.append(Clue([-8, 0.5, 0], "Red boxes are unlocked. Dark boxes need keys."))
    clues.append(Clue([8, 0.5, 0], "Look for shiny objects - they might be keys!"))

def get_nearby_object():
    interact_range = 2.0
    px, pz = game.player_x, game.player_z
    
    for clue in clues:
        cx, cy, cz = clue.position
        distance = math.sqrt((px - cx)**2 + (pz - cz)**2)
        if distance < interact_range:
            return ("clue", clue)
    
    for box in boxes:
        bx, by, bz = box.position
        distance = math.sqrt((px - bx)**2 + (pz - bz)**2)
        if distance < interact_range:
            return ("box", box)
    
    for key in keys:
        kx, ky, kz = key.position
        distance = math.sqrt((px - kx)**2 + (pz - kz)**2)
        if distance < interact_range and not key.collected:
            return ("key", key)
    
    for fruit in fruits:
        fx, fy, fz = fruit.position
        distance = math.sqrt((px - fx)**2 + (pz - fz)**2)
        if distance < interact_range and not fruit.collected:
            return ("fruit", fruit)
    
    return None

def interact_room1():
    nearby = get_nearby_object()
    
    if nearby:
        obj_type, obj = nearby
        
        if obj_type == "clue":
            obj.read = True
            game.current_message = obj.text
            game.message_timer = time.time()
            print(f"Clue: {obj.text}")
        
        elif obj_type == "key":
            obj.collected = True
            game.keys_found += 1
            if obj.clue_text:
                game.current_message = obj.clue_text
                game.message_timer = time.time()
            print(f"Picked up a key! Keys found: {game.keys_found}")
            if obj.clue_text:
                print(f"Key hint: {obj.clue_text}")
        
        elif obj_type == "box":
            if obj.locked and game.keys_found > 0:
                obj.locked = False
                obj.opened = True
                game.keys_found -= 1
                print("Unlocked the box!")
                if obj.riddle:
                    print(f"Box riddle: {obj.riddle}")
                
                if obj.contains_fruit:
                    game.collected_fruits.append(obj.contains_fruit)
                    print(f"Found and collected a {obj.contains_fruit}! ({len(game.collected_fruits)}/{len(game.required_fruits)})")
                    game.current_message = f"You got a {obj.contains_fruit}!"
                    game.message_timer = time.time()
                    check_puzzle_solved()
            
            elif not obj.locked and not obj.opened:
                obj.opened = True
                if obj.riddle:
                    print(f"Box riddle: {obj.riddle}")
                    game.current_message = obj.riddle
                    game.message_timer = time.time()
                if obj.contains_fruit:
                    game.collected_fruits.append(obj.contains_fruit)
                    print(f"Found and collected a {obj.contains_fruit}! ({len(game.collected_fruits)}/{len(game.required_fruits)})")
                    game.current_message = f"You got a {obj.contains_fruit}!"
                    game.message_timer = time.time()
                    check_puzzle_solved()
            
            elif obj.locked:
                if obj.riddle:
                    game.current_message = obj.riddle
                    game.message_timer = time.time()
                    print(f"Box riddle: {obj.riddle}")
                print("This box is locked! Find a key to open it.")
        
        elif obj_type == "fruit":
            obj.collected = True
            game.collected_fruits.append(obj.type)
            print(f"Collected {obj.type}! ({len(game.collected_fruits)}/{len(game.required_fruits)})")
            check_puzzle_solved()

def check_puzzle_solved():
    collected_types = set(game.collected_fruits)
    required_types = set(game.required_fruits)
    
    if required_types.issubset(collected_types):
        if not game.gate_open[0]:
            game.gate_open[0] = True
            print("\n" + "="*50)
            print("ROOM 1 PUZZLE SOLVED! The gate is opening...")
            print("="*50 + "\n")

def check_box_collision(x, z, box):
    box_x, box_y, box_z = box.position
    w, h, d = box.size
    return (abs(x - box_x) < (w/2 + PLAYER_RADIUS) and
            abs(z - box_z) < (d/2 + PLAYER_RADIUS))

def draw_box(box):
    x, y, z = box.position
    w, h, d = box.size
    
    if box.locked and not box.opened:
        color = COLOR_LOCKED_BOX
    else:
        color = COLOR_BOX
    
    draw_cuboid(x, y, z, w, h, d, color)
    
    if box.locked and not box.opened:
        glColor3f(0.8, 0.8, 0.8)
        lock_size = 0.2
        draw_cuboid(x, y + h/2, z + d/2 + 0.05, lock_size, lock_size, 0.1, (0.3, 0.3, 0.3))

def draw_fruit(fruit):
    if not fruit.collected:
        x, y, z = fruit.position
        draw_sphere(x, y, z, fruit.size, fruit.color)

def draw_key(key):
    if not key.collected:
        x, y, z = key.position
        draw_sphere(x, y, z, key.size, COLOR_KEY)
        draw_cuboid(x, y, z, key.size * 0.5, key.size * 0.3, key.size * 1.5, COLOR_KEY)

def draw_clue(clue):
    x, y, z = clue.position
    if clue.read:
        draw_sphere(x, y, z, clue.size, (0.5, 0.5, 0.5))
    else:
        draw_sphere(x, y, z, clue.size, (1.0, 1.0, 0.0))
    draw_cuboid(x, y + 0.3, z, 0.4, 0.05, 0.6, (0.9, 0.9, 0.9))

def draw_room1_hud():
    draw_text(20, WINDOW_HEIGHT - 60, "Room 1: The Fruit Puzzle")
    
    collected_text = f"Fruits: {len(game.collected_fruits)}/{len(game.required_fruits)}"
    draw_text(20, WINDOW_HEIGHT - 90, collected_text)
    
    draw_text(20, WINDOW_HEIGHT - 120, f"Keys: {game.keys_found}")
    
    nearby = get_nearby_object()
    if nearby:
        obj_type, obj = nearby
        if obj_type == "box":
            if obj.locked:
                hint = "Press F to unlock (needs key)"
            elif not obj.opened:
                hint = "Press F to open box"
            else:
                hint = "Box is empty"
        elif obj_type == "key":
            hint = "Press F to pick up key"
        elif obj_type == "fruit":
            hint = f"Press F to collect {obj.type}"
        elif obj_type == "clue":
            hint = "Press F to read clue"
        
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50, hint)
    
    if game.gate_open[0]:
        draw_text(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2, 
                 "PUZZLE SOLVED! Walk through the gate to Room 2!")
    
    if game.current_message and (time.time() - game.message_timer) < game.message_duration:
        time_left = game.message_duration - (time.time() - game.message_timer)
        alpha = min(1.0, time_left / 0.5)
        glColor3f(0.2 * alpha, 0.8 * alpha, 0.2 * alpha)
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, game.current_message)


# ROOM 2: COLOR SEQUENCE PUZZLE

COLOR_SEQUENCE = ['red', 'blue', 'green', 'yellow']
AVAILABLE_COLORS = ['red', 'blue', 'green', 'yellow']
color_switches = [
    {"pos": [-300, 200], "color": "red", "active": False, "col": (0.9, 0.1, 0.1)},
    {"pos": [300, 200], "color": "blue", "active": False, "col": (0.1, 0.1, 0.9)},
    {"pos": [-300, -200], "color": "green", "active": False, "col": (0.1, 0.9, 0.1)},
    {"pos": [300, -200], "color": "yellow", "active": False, "col": (0.95, 0.95, 0.1)},
]
current_sequence = []
sequence_correct = False
last_switch_time = 0
SWITCH_COOLDOWN = 0.5
ROOM2_COLLIDERS = []
player_pos = [0, 0, 0]

def randomize_color_sequence():
    global COLOR_SEQUENCE
    COLOR_SEQUENCE = [AVAILABLE_COLORS[i] for i in range(len(AVAILABLE_COLORS))]
    for i in range(len(COLOR_SEQUENCE)):
        swap_idx = random.randint(0, len(COLOR_SEQUENCE) - 1)
        COLOR_SEQUENCE[i], COLOR_SEQUENCE[swap_idx] = COLOR_SEQUENCE[swap_idx], COLOR_SEQUENCE[i]   
    print(f"Room 2 - Color sequence: {COLOR_SEQUENCE}")

def rebuild_room2_colliders():
    global ROOM2_COLLIDERS
    ROOM2_COLLIDERS = []
    for switch in color_switches:
        x, y = switch["pos"]
        ROOM2_COLLIDERS.append((x, y, 30, 30))
    ROOM2_COLLIDERS.append((0, 0, 35, 35))

def room_offset_y(room_num):
    if room_num == 0:
        return 0
    else:
        return -400

def draw_cylinder(radius, height, slices=16):
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
    glEnd()
    
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, height)
    for i in range(slices + 1):  
        angle = 2.0 * math.pi * i / slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, height)
    glEnd()
    
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
        glVertex3f(x, y, height)
    glEnd()

def draw_color_switches(room_base_y):
    for switch in color_switches:
        x, y = switch["pos"]
        world_x = x / 100.0
        world_z = y / 100.0
        
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(world_x, FLOOR_Z, world_z)
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.25, 0.3, 16)
        glPopMatrix()
        
        if switch["active"]:
            glow_factor = 1.5
            glColor3f(min(1.0, switch["col"][0] * glow_factor), 
                      min(1.0, switch["col"][1] * glow_factor), 
                      min(1.0, switch["col"][2] * glow_factor))
        else:
            glColor3f(*switch["col"])
        
        z_offset = 0.35 + (0.05 if switch["active"] else 0)
        draw_sphere(world_x, z_offset, world_z, 0.15, switch["col"] if not switch["active"] else 
                   (min(1.0, switch["col"][0] * 1.5), min(1.0, switch["col"][1] * 1.5), min(1.0, switch["col"][2] * 1.5)))

def draw_central_buzzer(room_base_y):
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0, FLOOR_Z, 0)
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.3, 0.5, 16)
    glPopMatrix()
    
    if sequence_correct and not game.gate_open[1]:
        pulse = 0.3 + 0.2 * math.sin(time.time() * 4.0)
        glColor3f(0.2 + pulse, 1.0, 0.2 + pulse)
    elif game.gate_open[1]:
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3f(1.0, 1.0, 1.0)
    
    z_offset = 0.55 + (0.05 if sequence_correct else 0)
    current_color = (1.0, 1.0, 1.0)
    if sequence_correct and not game.gate_open[1]:
        pulse = 0.3 + 0.2 * math.sin(time.time() * 4.0)
        current_color = (0.2 + pulse, 1.0, 0.2 + pulse)
    elif game.gate_open[1]:
        current_color = (1.0, 1.0, 1.0)
    
    draw_sphere(0, z_offset, 0, 0.2, current_color)

def try_activate_switch():
    global current_sequence, sequence_correct, last_switch_time
    
    if game.current_room != 1:
        return
    
    if time.time() - last_switch_time < SWITCH_COOLDOWN:
        return
    
    room_base_y = room_offset_y(game.current_room)
    
    if sequence_correct and not game.gate_open[1]:
        if activate_buzzer(room_base_y):
            return
    
    nearest_switch = find_nearest_switch(room_base_y)
    if nearest_switch:
        handle_switch_activation(nearest_switch)

def activate_buzzer(room_base_y):
    buzzer_x, buzzer_z = 0, 0
    buzzer_dist = calculate_distance(game.player_x, game.player_z, buzzer_x, buzzer_z)
    
    if buzzer_dist < 1.0:
        update_gate_status()
        return True
    return False

def find_nearest_switch(room_base_y):
    nearest_switch = None
    nearest_dist = float('inf')
    
    for switch in color_switches:
        x, y = switch["pos"]
        world_x = x / 100.0
        world_z = y / 100.0
        dist = calculate_distance(game.player_x, game.player_z, world_x, world_z)
        
        if dist < 1.0 and dist < nearest_dist:
            nearest_dist = dist
            nearest_switch = switch
    
    return nearest_switch

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def handle_switch_activation(nearest_switch):
    global current_sequence, sequence_correct, last_switch_time
    
    last_switch_time = time.time()
    expected_next = len(current_sequence)
    
    if is_valid_switch_activation(nearest_switch, expected_next):
        nearest_switch["active"] = True
        current_sequence.append(nearest_switch["color"])
        print(f"Activated {nearest_switch['color']} switch. Sequence: {current_sequence}")
        
        if len(current_sequence) == len(COLOR_SEQUENCE):
            sequence_correct = True
            print("Color sequence complete! Go to central buzzer and press F")
    else:
        print(f"Wrong switch! Expected {COLOR_SEQUENCE[expected_next] if expected_next < len(COLOR_SEQUENCE) else 'none'}, got {nearest_switch['color']}")
        reset_color_sequence()

def is_valid_switch_activation(nearest_switch, expected_next):
    return (expected_next < len(COLOR_SEQUENCE) and
            nearest_switch["color"] == COLOR_SEQUENCE[expected_next])

def update_gate_status():
    game.gate_open[1] = True
    game.gate_open_time[1] = time.time()
    print(f"Buzzer activated! Game complete!")

def reset_color_sequence():
    clear_current_sequence()
    deactivate_all_switches()

def clear_current_sequence():
    global current_sequence, sequence_correct
    current_sequence = []
    sequence_correct = False

def deactivate_all_switches():
    for switch in color_switches:
        switch["active"] = False

def draw_room2_hud():
    draw_text(20, WINDOW_HEIGHT - 60, "Room 2: Color Sequence")
    
    seq_text = f"Sequence: {' -> '.join(current_sequence) if current_sequence else 'Start!'}"
    draw_text(20, WINDOW_HEIGHT - 90, seq_text)
    
    target_text = f"Target: {' -> '.join(COLOR_SEQUENCE)}"
    draw_text(20, WINDOW_HEIGHT - 120, target_text)
    
    if sequence_correct and not game.gate_open[1]:
        draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 
                 "Sequence Complete! Activate the central buzzer (Press F)")
    elif game.gate_open[1]:
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 
                 "GAME COMPLETE!")


# Shared rendering and game logic functions:


def draw_cuboid(x, y, z, width, height, depth, color):
    glPushMatrix()
    glTranslatef(x, y + height/2, z)
    glColor3f(*color)
    
    glBegin(GL_QUADS)
    glVertex3f(-width/2, -height/2, depth/2)
    glVertex3f(width/2, -height/2, depth/2)
    glVertex3f(width/2, height/2, depth/2)
    glVertex3f(-width/2, height/2, depth/2)
    
    glVertex3f(-width/2, -height/2, -depth/2)
    glVertex3f(-width/2, height/2, -depth/2)
    glVertex3f(width/2, height/2, -depth/2)
    glVertex3f(width/2, -height/2, -depth/2)
    
    glVertex3f(-width/2, -height/2, -depth/2)
    glVertex3f(-width/2, -height/2, depth/2)
    glVertex3f(-width/2, height/2, depth/2)
    glVertex3f(-width/2, height/2, -depth/2)
    
    glVertex3f(width/2, -height/2, -depth/2)
    glVertex3f(width/2, height/2, -depth/2)
    glVertex3f(width/2, height/2, depth/2)
    glVertex3f(width/2, -height/2, depth/2)
    
    glVertex3f(-width/2, height/2, -depth/2)
    glVertex3f(-width/2, height/2, depth/2)
    glVertex3f(width/2, height/2, depth/2)
    glVertex3f(width/2, height/2, -depth/2)
    
    glVertex3f(-width/2, -height/2, -depth/2)
    glVertex3f(width/2, -height/2, -depth/2)
    glVertex3f(width/2, -height/2, depth/2)
    glVertex3f(-width/2, -height/2, depth/2)
    glEnd()
    
    glPopMatrix()

def draw_sphere(x, y, z, radius, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    quadric = gluNewQuadric()
    gluSphere(quadric, radius, 20, 20)
    gluDeleteQuadric(quadric)
    glPopMatrix()

def draw_floor():
    glColor3f(*COLOR_FLOOR)
    glBegin(GL_QUADS)
    glVertex3f(-ROOM_SIZE/2, 0, -ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, 0, -ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, 0, ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, 0, ROOM_SIZE/2)
    glEnd()

def draw_ceiling():
    glColor3f(*COLOR_CEILING)
    glBegin(GL_QUADS)
    glVertex3f(-ROOM_SIZE/2, WALL_HEIGHT, -ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, WALL_HEIGHT, -ROOM_SIZE/2)
    glEnd()

def draw_walls():
    glColor3f(*COLOR_WALL)
    
    glBegin(GL_QUADS)
    glVertex3f(-ROOM_SIZE/2, 0, -ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, WALL_HEIGHT, -ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, WALL_HEIGHT, -ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, 0, -ROOM_SIZE/2)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(-ROOM_SIZE/2, 0, -ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, 0, ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, WALL_HEIGHT, -ROOM_SIZE/2)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(ROOM_SIZE/2, 0, -ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, WALL_HEIGHT, -ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, 0, ROOM_SIZE/2)
    glEnd()
    
    gate_width = 3.0
    gate_height = 4.0
    gate_offset = game.gate_opening_progress[game.current_room] * gate_height
    
    glBegin(GL_QUADS)
    glVertex3f(-ROOM_SIZE/2, 0, ROOM_SIZE/2)
    glVertex3f(-ROOM_SIZE/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(-gate_width/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(-gate_width/2, 0, ROOM_SIZE/2)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(gate_width/2, 0, ROOM_SIZE/2)
    glVertex3f(gate_width/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(ROOM_SIZE/2, 0, ROOM_SIZE/2)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(-gate_width/2, gate_height, ROOM_SIZE/2)
    glVertex3f(-gate_width/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(gate_width/2, WALL_HEIGHT, ROOM_SIZE/2)
    glVertex3f(gate_width/2, gate_height, ROOM_SIZE/2)
    glEnd()
    
    if game.gate_opening_progress[game.current_room] < 1.0:
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-gate_width/2, gate_offset, ROOM_SIZE/2 - 0.1)
        glVertex3f(-gate_width/2, gate_height, ROOM_SIZE/2 - 0.1)
        glVertex3f(gate_width/2, gate_height, ROOM_SIZE/2 - 0.1)
        glVertex3f(gate_width/2, gate_offset, ROOM_SIZE/2 - 0.1)
        glEnd()

def draw_player_body(x, y, z, rotation_y):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation_y, 0, 1, 0)
    
    torso_color = (0.1, 0.15, 0.25)
    accent_color = (0.0, 0.8, 1.0)
    head_color = (0.95, 0.85, 0.75)
    limb_color = (0.08, 0.12, 0.2)
    joint_color = (0.0, 0.6, 0.9)
    
    head_radius = 0.22
    head_y = 0.5
    draw_sphere(0, head_y, 0, head_radius, head_color)
    
    eye_offset = 0.08
    eye_forward = 0.18
    draw_sphere(-eye_offset, head_y + 0.05, eye_forward, 0.04, accent_color)
    draw_sphere(eye_offset, head_y + 0.05, eye_forward, 0.04, accent_color)
    
    neck_width = 0.12
    neck_height = 0.15
    neck_depth = 0.12
    neck_y = 0.3
    draw_cuboid(0, neck_y, 0, neck_width, neck_height, neck_depth, limb_color)
    
    upper_torso_width = 0.5
    upper_torso_height = 0.35
    upper_torso_depth = 0.28
    upper_torso_y = 0.05
    draw_cuboid(0, upper_torso_y, 0, upper_torso_width, upper_torso_height, upper_torso_depth, torso_color)
    
    draw_cuboid(0, 0.1, upper_torso_depth/2 + 0.01, upper_torso_width * 0.3, 0.08, 0.02, accent_color)
    
    lower_torso_width = 0.42
    lower_torso_height = 0.3
    lower_torso_depth = 0.26
    lower_torso_y = -0.25
    draw_cuboid(0, lower_torso_y, 0, lower_torso_width, lower_torso_height, lower_torso_depth, torso_color)
    
    shoulder_radius = 0.1
    shoulder_x = upper_torso_width/2
    shoulder_y = 0.15
    draw_sphere(-shoulder_x, shoulder_y, 0, shoulder_radius, joint_color)
    draw_sphere(shoulder_x, shoulder_y, 0, shoulder_radius, joint_color)
    
    arm_width = 0.13
    upper_arm_height = 0.35
    arm_depth = 0.13
    left_upper_arm_x = -upper_torso_width/2 - arm_width/2 - 0.03
    upper_arm_y = 0.0
    draw_cuboid(left_upper_arm_x, upper_arm_y, 0, arm_width, upper_arm_height, arm_depth, limb_color)
    draw_cuboid(-left_upper_arm_x, upper_arm_y, 0, arm_width, upper_arm_height, arm_depth, limb_color)
    
    elbow_y = -0.15
    draw_sphere(left_upper_arm_x, elbow_y, 0, 0.08, joint_color)
    draw_sphere(-left_upper_arm_x, elbow_y, 0, 0.08, joint_color)
    
    lower_arm_height = 0.32
    lower_arm_y = -0.4
    draw_cuboid(left_upper_arm_x, lower_arm_y, 0, arm_width * 0.9, lower_arm_height, arm_depth * 0.9, limb_color)
    draw_cuboid(-left_upper_arm_x, lower_arm_y, 0, arm_width * 0.9, lower_arm_height, arm_depth * 0.9, limb_color)
    
    hand_y = -0.6
    draw_sphere(left_upper_arm_x, hand_y, 0, 0.09, accent_color)
    draw_sphere(-left_upper_arm_x, hand_y, 0, 0.09, accent_color)
    
    hip_x = lower_torso_width/3
    hip_y = -0.42
    draw_sphere(-hip_x, hip_y, 0, 0.09, joint_color)
    draw_sphere(hip_x, hip_y, 0, 0.09, joint_color)
    
    leg_width = 0.16
    upper_leg_height = 0.4
    leg_depth = 0.16
    left_leg_x = -lower_torso_width/3.5
    upper_leg_y = -0.7
    draw_cuboid(left_leg_x, upper_leg_y, 0, leg_width, upper_leg_height, leg_depth, limb_color)
    draw_cuboid(-left_leg_x, upper_leg_y, 0, leg_width, upper_leg_height, leg_depth, limb_color)
    
    knee_y = -0.92
    draw_sphere(left_leg_x, knee_y, 0, 0.08, joint_color)
    draw_sphere(-left_leg_x, knee_y, 0, 0.08, joint_color)
    
    lower_leg_height = 0.42
    lower_leg_y = -1.2
    draw_cuboid(left_leg_x, lower_leg_y, 0, leg_width * 0.9, lower_leg_height, leg_depth * 0.9, limb_color)
    draw_cuboid(-left_leg_x, lower_leg_y, 0, leg_width * 0.9, lower_leg_height, leg_depth * 0.9, limb_color)
    
    foot_width = 0.18
    foot_height = 0.12
    foot_depth = 0.28
    foot_y = -1.48
    foot_z = 0.08
    draw_cuboid(left_leg_x, foot_y, foot_z, foot_width, foot_height, foot_depth, limb_color)
    draw_cuboid(-left_leg_x, foot_y, foot_z, foot_width, foot_height, foot_depth, limb_color)
    draw_cuboid(left_leg_x, foot_y + 0.03, foot_z + foot_depth/2, foot_width * 0.8, 0.05, 0.02, accent_color)
    draw_cuboid(-left_leg_x, foot_y + 0.03, foot_z + foot_depth/2, foot_width * 0.8, 0.05, 0.02, accent_color)
    
    glPopMatrix()

def check_wall_collision(x, z):
    half_room = ROOM_SIZE / 2 - PLAYER_RADIUS
    
    if game.gate_open[game.current_room]:
        gate_width = 3.0
        if z > half_room and abs(x) < gate_width / 2:
            return False
    
    return (abs(x) > half_room or abs(z) > half_room)

def can_move_to(new_x, new_z):
    if check_wall_collision(new_x, new_z):
        return False
    
    if game.current_room == 0:
        for box in boxes:
            if check_box_collision(new_x, new_z, box):
                return False
    
    return True

def interact():
    if game.current_room == 1:
        try_activate_switch()
        return
    
    interact_room1()

def update_player_movement():
    if game.camera_mode == "first_person":
        if game.rotate_left:
            game.player_rotation_y -= ROTATION_SPEED
        if game.rotate_right:
            game.player_rotation_y += ROTATION_SPEED
    else:
        if game.rotate_left:
            game.player_rotation_y -= ROTATION_SPEED
        if game.rotate_right:
            game.player_rotation_y += ROTATION_SPEED
    
    if game.move_forward or game.move_backward or game.move_left or game.move_right:
        angle = math.radians(game.player_rotation_y)
        
        dx = 0
        dz = 0
        
        if game.camera_mode == "first_person":
            if game.move_forward:
                dx += math.cos(math.radians(game.player_rotation_y)) * MOVE_SPEED
                dz += math.sin(math.radians(game.player_rotation_y)) * MOVE_SPEED
            if game.move_backward:
                dx -= math.cos(math.radians(game.player_rotation_y)) * MOVE_SPEED
                dz -= math.sin(math.radians(game.player_rotation_y)) * MOVE_SPEED
            if game.move_left:
                dx += math.sin(math.radians(game.player_rotation_y)) * MOVE_SPEED
                dz -= math.cos(math.radians(game.player_rotation_y)) * MOVE_SPEED
            if game.move_right:
                dx -= math.sin(math.radians(game.player_rotation_y)) * MOVE_SPEED
                dz += math.cos(math.radians(game.player_rotation_y)) * MOVE_SPEED
        else:
            if game.move_forward:
                dx -= math.sin(angle) * MOVE_SPEED
                dz -= math.cos(angle) * MOVE_SPEED
            if game.move_backward:
                dx += math.sin(angle) * MOVE_SPEED
                dz += math.cos(angle) * MOVE_SPEED
            if game.move_left:
                dx -= math.cos(angle) * MOVE_SPEED
                dz += math.sin(angle) * MOVE_SPEED
            if game.move_right:
                dx += math.cos(angle) * MOVE_SPEED
                dz -= math.sin(angle) * MOVE_SPEED
        
        new_x = game.player_x + dx
        new_z = game.player_z + dz
        
        if can_move_to(new_x, new_z):
            game.player_x = new_x
            game.player_z = new_z

def setup_camera():
    glLoadIdentity()
    
    if game.camera_mode == "first_person":
        eye_x = game.player_x
        eye_y = game.player_y
        eye_z = game.player_z
        
        center_x = game.player_x + 100 * math.cos(math.radians(game.player_rotation_y))
        center_y = game.player_y
        center_z = game.player_z + 100 * math.sin(math.radians(game.player_rotation_y))
        
        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0, 1, 0)
    
    else:
        angle = math.radians(game.player_rotation_y)
        cam_x = game.player_x + math.sin(angle) * game.camera_distance
        cam_z = game.player_z + math.cos(angle) * game.camera_distance
        cam_y = game.player_y + 3.0
        
        gluLookAt(cam_x, cam_y, cam_z,
                  game.player_x, game.player_y, game.player_z,
                  0, 1, 0)

def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():
    elapsed = time.time() - game.start_time
    game.time_remaining = max(0, TIME_LIMIT - int(elapsed))
    
    minutes = game.time_remaining // 60
    seconds = game.time_remaining % 60
    time_text = f"Time: {minutes:02d}:{seconds:02d}"
    draw_text(20, WINDOW_HEIGHT - 30, time_text)
    
    if game.current_room == 0:
        draw_room1_hud()
    else:
        draw_room2_hud()
    
    if game.game_completed:
        glColor3f(0.0, 1.0, 0.0)
        draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 30, f"Your Score: {game.final_score} seconds")
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 30, "Press ESC to Exit")
    
    draw_text(20, 60, "WASD: Move | Q/E: Rotate | F: Interact | C: Change Camera | ESC: Quit")

def init_opengl():
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [0, WALL_HEIGHT - 1, 0, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1])
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(75, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)
    setup_camera()
    
    draw_floor()
    draw_ceiling()
    draw_walls()
    
    if game.current_room == 0:
        for box in boxes:
            draw_box(box)
        
        for fruit in fruits:
            draw_fruit(fruit)
        
        for key in keys:
            draw_key(key)
        
        for clue in clues:
            draw_clue(clue)
    else:
        room_base_y = room_offset_y(game.current_room)
        draw_color_switches(room_base_y)
        draw_central_buzzer(room_base_y)
    
    if game.camera_mode == "third_person":
        draw_player_body(game.player_x, game.player_y, game.player_z, game.player_rotation_y)
    
    glDisable(GL_LIGHTING)
    draw_hud()
    
    glutSwapBuffers()

def update(value):
    update_player_movement()
    
    if game.current_room == 0 and game.gate_open[0]:
        if game.player_z > ROOM_SIZE/2 + 0.5:
            game.current_room = 1
            game.player_z = -ROOM_SIZE/2 + 2.0
            game.player_x = 0.0
            print("\n" + "="*60)
            print(" "*15 + "ENTERING ROOM 2")
            print("="*60)
            print("\nROOM 2: Color Sequence Puzzle")
            print("-" * 60)
            print(f"Sequence to follow: {COLOR_SEQUENCE}")
            print("  - Activate the colored switches in the correct order")
            print("  - Press F near each switch to activate it")
            print("  - After completing the sequence, activate the central buzzer")
            print("="*60 + "\n")
    
    if game.gate_open[game.current_room] and game.gate_opening_progress[game.current_room] < 1.0:
        game.gate_opening_progress[game.current_room] += 0.02
    
    if game.time_remaining <= 0 and not all(game.gate_open):
        print("\nTIME'S UP! Game Over.")
        glutLeaveMainLoop()
    
    if game.gate_open[1] and not game.game_completed:
        game.game_completed = True
        game.final_score = game.time_remaining
        print("\n" + "="*60)
        print(" "*15 + "CONGRATULATIONS!")
        print("="*60)
        print("\nYou have escaped the Puzzle Prison!")
        print("Both rooms completed successfully!")
        print(f"Your Score: {game.final_score} seconds remaining!")
        print("="*60 + "\n")
    
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
    key = key.decode('utf-8').lower()
    
    if key == '\x1b':
        glutLeaveMainLoop()
    elif key == 'w':
        game.move_forward = True
    elif key == 's':
        game.move_backward = True
    elif key == 'a':
        game.move_left = True
    elif key == 'd':
        game.move_right = True
    elif key == 'q':
        game.rotate_left = True
    elif key == 'e':
        game.rotate_right = True
    elif key == 'f':
        interact()
    elif key == 'c':
        if game.camera_mode == "first_person":
            game.camera_mode = "third_person"
        else:
            game.camera_mode = "first_person"
        print(f"Camera mode: {game.camera_mode}")

def keyboard_up(key, x, y):
    key = key.decode('utf-8').lower()
    
    if key == 'w':
        game.move_forward = False
    elif key == 's':
        game.move_backward = False
    elif key == 'a':
        game.move_left = False
    elif key == 'd':
        game.move_right = False
    elif key == 'q':
        game.rotate_left = False
    elif key == 'e':
        game.rotate_right = False

def mouse_motion(x, y):
    pass

def main():
    print("\n" + "="*60)
    print(" "*15 + "WELCOME TO THE PUZZLE PRISON")
    print("="*60)
    print("\nROOM 1: The Fruit Puzzle")
    print("-" * 60)
    print("Objective: Collect the required fruits to unlock the gate")
    print("  - Explore boxes scattered around the room")
    print("  - Some boxes are locked - find keys to open them")
    print("  - Collect: Apple, Banana, and Orange")
    print("\nROOM 2: Color Sequence Puzzle")
    print("-" * 60)
    print("Objective: Activate colored switches in the correct sequence")
    print("  - Follow the sequence shown on screen")
    print("  - Activate the central buzzer when complete")
    print("\nControls:")
    print("  WASD - Move around")
    print("  Q/E - Rotate camera left/right")
    print("  F - Interact with objects")
    print("  C - Switch camera mode")
    print("  ESC - Quit game")
    print("="*60 + "\n")
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Puzzle Prison - Two Room Escape")
    
    init_opengl()
    
    initialize_room1_objects()
    randomize_color_sequence()
    rebuild_room2_colliders()
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutPassiveMotionFunc(mouse_motion)
    glutMotionFunc(mouse_motion)
    glutTimerFunc(0, update, 0)
    
    print("Game started! Good luck!\n")
    glutMainLoop()

if __name__ == "__main__":
    main()
