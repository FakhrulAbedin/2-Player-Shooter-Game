from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

# Game variables
player1_pos = [200, 50, 0]
player2_pos = [400, 550, 0]
player1_angle = 0
player2_angle = 180
player1_health = 10
player2_health = 10
player1_speed = 1
player2_speed = 1

bullets = []
round_number = 1
round_start_time = time.time()
maze_walls = True
game_over = False
round_wins = {"player1": 0, "player2": 0}  



# Powerup variables
POWERUP_TYPES = {
    'health': {'color': (0, 1, 0), 'shape': 'cube', 'size': 15}, 
    'speed': {'color': (1, 0, 0), 'shape': 'cylinder', 'size': 15}
} 

max_health = 10
max_speed = 2

current_powerup = None
powerup_spawn_time = 0
powerup_spawn_cooldown_timer = 10  
powerup_duration = 5  


player1_speed_boost_end = 0
player2_speed_boost_end = 0

# Camera position variables
camera_pos = [325, 0, 325]  
camera_look_at = [325, 325, 0] 






key_states = {
    b'w': False, b's': False, b'a': False, b'd': False, b'e': False,  # Player 1 movement and fire
    b'm': False, # Player 2 fire
}

special_key_states = {
    GLUT_KEY_UP: False, GLUT_KEY_DOWN: False,  # Player 2 movement
    GLUT_KEY_LEFT: False, GLUT_KEY_RIGHT: False,
    
}

# Maze configurations
mazes = [
    [  # Round 1 maze 
        ((0, 0), (600, 20)),  # Bottom boundary
        ((0, 580), (600, 600)),  # Top boundary
        ((0, 0), (20, 600)),  # Left boundary
        ((580, 0), (600, 600)),  # Right boundary
        ((150, 150), (450, 170)),  # Horizontal wall 1
        ((150, 420), (450, 450)),  # Horizontal wall 2
        ((300, 170), (320, 420))   # Vertical wall in the center
    ],
    [  # Round 2 maze 
        ((0, 0), (600, 20)),  # Bottom boundary
        ((0, 580), (600, 600)),  # Top boundary
        ((0, 0), (20, 600)),  # Left boundary
        ((580, 0), (600, 600)),  # Right boundary      
        ((250, 250), (350, 350)),  # small square center obstacle
        ((100, 100), (200, 200)),  # Small square obstacle 1
        ((400, 400), (500, 500)),  # Small square obstacle 2
        ((100, 400), (200, 500)),  # Small square obstacle 3
        ((375, 100), (500, 200))   # Small square obstacle 4
    ],
    [  # Round 3 maze 
        ((0, 0), (600, 20)),      # Bottom boundary
        ((0, 580), (600, 600)),   # Top boundary
        ((0, 0), (20, 600)),      # Left boundary
        ((580, 0), (600, 600)),   # Right boundary
    
        # Top horizontal walls with gap
        ((150, 150), (280, 170)),
        ((320, 150), (450, 170)),
        
        # Bottom horizontal walls with gap
        ((150, 430), (280, 450)),
        ((320, 430), (450, 450)),
        
        # Left vertical walls with gap
        ((150, 150), (170, 280)),
        ((150, 320), (170, 450)),
        
        # Right vertical walls with gap
        ((430, 150), (450, 280)),
        ((430, 320), (450, 450)),
        
        # Center obstacle
        ((225, 225), (375, 375))
    ]
]

RESTART_BUTTON_X = 800
RESTART_BUTTON_Y = 750
RESTART_BUTTON_WIDTH = 150
RESTART_BUTTON_HEIGHT = 30

def draw_player(x, y, angle, color):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(angle, 0, 0, 1)

    #Tank Body 
    glColor3f(*color)
    glPushMatrix()
    glScalef(1.5, 1, 0.5)
    glutSolidCube(20)
    glPopMatrix()

    #Turret 
    glPushMatrix()
    glTranslatef(0, 0, 10)  # On top of the body
    glColor3f(0.2, 0.2, 0.2)
    gluSphere(gluNewQuadric(), 7, 20, 20)

    #Barrel
    glPushMatrix()
    glTranslatef(7, 0, 0)  #  front edge of turret 
    glRotatef(90, 0, 1, 0)  # point forward
    glColor3f(0.2, 0.2, 0.2)
    quad = gluNewQuadric()
    gluCylinder(quad, 2, 2, 15, 20, 5)
    glPopMatrix()

    glPopMatrix()  

    glPopMatrix()  



def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet['x'], bullet['y'], 0)
    glColor3f(1, 1, 0)
    gluSphere(gluNewQuadric(), 5, 25, 5)
    glPopMatrix()

def draw_maze():
    if maze_walls and 1 <= round_number <= len(mazes):  
        glColor3f(0.4, 0.3, 0.5)  
        for wall in mazes[round_number - 1]:
            x1, y1 = wall[0]
            x2, y2 = wall[1]
            wall_height = 30
            
            
            glBegin(GL_QUADS)
            # Front face
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y1, wall_height)
            glVertex3f(x1, y1, wall_height)
            
            # Back face
            glVertex3f(x1, y2, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x2, y2, wall_height)
            glVertex3f(x1, y2, wall_height)
            
            # Left face
            glVertex3f(x1, y1, 0)
            glVertex3f(x1, y2, 0)
            glVertex3f(x1, y2, wall_height)
            glVertex3f(x1, y1, wall_height)
            
            # Right face
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x2, y2, wall_height)
            glVertex3f(x2, y1, wall_height)
            
            # Top face
            glVertex3f(x1, y1, wall_height)
            glVertex3f(x2, y1, wall_height)
            glVertex3f(x2, y2, wall_height)
            glVertex3f(x1, y2, wall_height)
            glEnd()

def is_collision(bullet, player_pos):
    return math.hypot(bullet['x'] - player_pos[0], bullet['y'] - player_pos[1]) < 20

def is_player_collision(player1_pos, player2_pos):
    distance = math.hypot(player1_pos[0] - player2_pos[0], player1_pos[1] - player2_pos[1])
    
    collision_radius = 25  
    
    return distance < collision_radius



def is_within_boundaries(x, y):
    
    if not maze_walls: 
        return 0 <= x <= 600 and 0 <= y <= 600  # Only check platform boundaries
    if x < 30 or x > 570 or y < 30 or y > 570:  # Check against outer boundaries
        return False
    for wall in mazes[round_number - 1]:
        if wall[0][0] <= x <= wall[1][0] and wall[0][1] <= y <= wall[1][1]:  # Check against walls
            return False
    return True






def keyboardListener(key, x, y):
    global key_states
    key = key.lower()
    if key in key_states:
        key_states[key] = True

def keyboardUpListener(key, x, y):
    global key_states
    key = key.lower()
    if key in key_states:
        key_states[key] = False

def specialKeyListener(key, x, y):
    global special_key_states
    if key in special_key_states:
        special_key_states[key] = True

def specialKeyUpListener(key, x, y):
    global special_key_states
    if key in special_key_states:
        special_key_states[key] = False

def mouseListener(button, state, x, y):
    global game_over
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        gl_x = x
        gl_y = 800 - y  
        
        if game_over and round_number > 3:
            if (RESTART_BUTTON_X <= gl_x <= RESTART_BUTTON_X + RESTART_BUTTON_WIDTH and
                RESTART_BUTTON_Y <= gl_y <= RESTART_BUTTON_Y + RESTART_BUTTON_HEIGHT):
                reset_game()
                glutPostRedisplay()




def fire_bullet(player_pos, angle, owner):
    dx = math.cos(math.radians(angle)) 
    dy = math.sin(math.radians(angle)) 
    bullets.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx, 'dy': dy, 'owner': owner})

def update_bullets():
    global bullets, player1_health, player2_health, game_over
    
    for bullet in bullets[:]:
        bullet['x'] += bullet['dx']
        bullet['y'] += bullet['dy']
        if not is_within_boundaries(bullet['x'], bullet['y']):
            bullets.remove(bullet)
        elif bullet['owner'] == 'player1' and is_collision(bullet, player2_pos):
            player2_health -= 1
            bullets.remove(bullet)
            if player2_health <= 0:
                game_over = True
        elif bullet['owner'] == 'player2' and is_collision(bullet, player1_pos):
            player1_health -= 1
            bullets.remove(bullet)
            if player1_health <= 0:
                game_over = True


def update_players():
    global player1_pos, player1_angle, player2_pos, player2_angle, bullets
    
    # Player 1 movement
    angle_in_radians = math.radians(player1_angle)
    dx = math.cos(angle_in_radians) * (player1_speed * 0.5)  
    dy = math.sin(angle_in_radians) * (player1_speed * 0.5)
    new_x, new_y = player1_pos[0], player1_pos[1]
    
    if key_states.get(b'w', False):  # Move forward
        new_x += dx
        new_y += dy
    if key_states.get(b's', False):  # Move backward
        new_x -= dx
        new_y -= dy
    if key_states.get(b'a', False):  # Rotate left
        player1_angle = (player1_angle + 1) % 360 
    if key_states.get(b'd', False):  # Rotate right
        player1_angle = (player1_angle - 1) % 360
    if key_states.get(b'e', False):  # Fire bullet
        key_states[b'e'] = False  
        fire_bullet(player1_pos, player1_angle, 'player1')
    

    
    if not is_player_collision([new_x, new_y], player2_pos) and is_within_boundaries(new_x, new_y):
        player1_pos[0], player1_pos[1] = new_x, new_y


    # Player 2 movement
    angle_in_radians = math.radians(player2_angle)
    dx = math.cos(angle_in_radians) * (player2_speed * 0.5)  
    dy = math.sin(angle_in_radians) * (player2_speed * 0.5)
    new_x, new_y = player2_pos[0], player2_pos[1]
    
    if special_key_states.get(GLUT_KEY_UP, False):  # Move forward
        new_x += dx
        new_y += dy
    if special_key_states.get(GLUT_KEY_DOWN, False):  # Move backward
        new_x -= dx
        new_y -= dy
    if special_key_states.get(GLUT_KEY_LEFT, False):  # Rotate left
        player2_angle = (player2_angle + 1) % 360  
    if special_key_states.get(GLUT_KEY_RIGHT, False):  # Rotate right
        player2_angle = (player2_angle - 1) % 360 
    if key_states.get(b'm', False):  # Fire bullet
        key_states[b'm'] = False  
        fire_bullet(player2_pos, player2_angle, 'player2')
    


    if not is_player_collision([new_x, new_y], player1_pos) and is_within_boundaries(new_x, new_y):
        player2_pos[0], player2_pos[1] = new_x, new_y



  

def check_round_timer():
    global maze_walls, round_start_time
    if time.time() - round_start_time > 60:
        maze_walls = False

def reset_game():
    global round_number, round_wins, game_over, current_powerup
    global player1_pos, player2_pos, player1_angle, player2_angle
    global player1_health, player2_health, player1_speed, player2_speed
    
    # Reset game state
    round_number = 1
    round_wins = {"player1": 0, "player2": 0}
    game_over = False
    current_powerup = None
    
    # Reset players
    player1_pos = [200, 50, 0]
    player2_pos = [400, 550, 0]
    player1_angle = 0
    player2_angle = 180
    player1_health = 10
    player2_health = 10
    player1_speed = 1
    player2_speed = 1
    
    bullets.clear()
    reset_round()

def reset_round():
    global player1_pos, player2_pos, player1_angle, player2_angle, player1_health, player2_health
    global bullets, round_start_time, maze_walls, game_over, current_powerup
    global player1_speed, player2_speed
    
    player1_pos = [200, 50, 0]
    player2_pos = [400, 550, 0]
    player1_angle = 0
    player2_angle = 180
    player1_health = 10
    player2_health = 10
    player1_speed = 1  
    player2_speed = 1 
    bullets.clear()
    round_start_time = time.time()
    maze_walls = True
    game_over = False
    current_powerup = None


def showScreen():
    global round_number, round_start_time, maze_walls, game_over
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 950, 800)
    setupCamera()

    # platform
    if round_number == 1:
        glColor3f(0.6, 0.4, 0.95)
    elif round_number == 2:
        glColor3f(0.7, 0.4, 0.95)
    elif round_number == 3:
        glColor3f(0.8, 0.4, 0.8)
    elif round_number > 3:
        glColor3f(0, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(600, 0, 0)
    glVertex3f(600, 600, 0)
    glVertex3f(0, 600, 0)
    glEnd()
    draw_maze()
    draw_powerup()
    draw_player(player1_pos[0], player1_pos[1], player1_angle, (1, 0, 0))
    draw_player(player2_pos[0], player2_pos[1], player2_angle, (0, 0, 1))

    for bullet in bullets:
        draw_bullet(bullet)


    draw_text(10, 770, f"Player1 Health: {player1_health}")
    draw_text(10, 740, f"Player2 Health: {player2_health}")

    if round_number <= 3:
        draw_text(450, 770, f"Round {round_number}")
    else:
        draw_text(450, 770, f"Game Over!")
        if round_wins["player1"] > round_wins["player2"]:
            draw_text(450, 740, f"Player1 Wins!")
        elif round_wins["player1"] < round_wins["player2"]:
            draw_text(450, 740, f"Player2 Wins!")
        else:
            draw_text(450, 740, f"It's a Tie!")
        
        draw_text(RESTART_BUTTON_X, RESTART_BUTTON_Y, "Click to Restart")

    if game_over:
        if round_number > 3:
            winner = "Player1" if round_wins["player1"] > round_wins["player2"] else "Player2"
            if round_wins["player1"] == round_wins["player2"]:
                winner = "It's a Tie!"
            draw_text(400, 400, f"GAME OVER! {winner} Wins!")
        else:
            draw_text(400, 400, "Round Over! Starting Next Round...")
    check_round_timer()

    glutSwapBuffers()

def idle():
    global round_number, round_start_time, maze_walls, game_over, round_wins
    if game_over:
        if round_number <= 3:
            reset_round()
        return
    
    update_players()  
    update_bullets()
    update_powerups()
    
    check_powerup_collision()
    
    if player1_health <= 0 or player2_health <= 0:
        if player1_health > player2_health:
            round_wins["player1"] += 1
        elif player2_health > player1_health:
            round_wins["player2"] += 1
        round_number += 1
        if round_number > 3:
            game_over = True
        else:
            reset_round()
    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(110, 1.2, 0.1, 1500)   
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_look_at[0], camera_look_at[1], camera_look_at[2],
              0, 0, 1)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 950, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def is_valid_powerup_position(x, y):

    if not is_within_boundaries(x, y):
        return False
    
    margin = 60
    return (margin <= x <= 600 - margin and 
            margin <= y <= 600 - margin)

def spawn_powerup():
    global current_powerup, powerup_spawn_time
    if current_powerup is None and time.time() - powerup_spawn_time >= powerup_spawn_cooldown_timer:
       
        max_attempts = 50
        for _ in range(max_attempts):
            x = random.randint(50, 550)
            y = random.randint(50, 550)
            if is_valid_powerup_position(x, y):
                powerup_type = random.choice(list(POWERUP_TYPES.keys()))
                current_powerup = {
                    'type': powerup_type,
                    'x': x,
                    'y': y,
                    'spawn_time': time.time()
                }
                break

def draw_powerup():
    if current_powerup is None:
        return
    powerup_info = POWERUP_TYPES[current_powerup['type']]
    glPushMatrix()
    glTranslatef(current_powerup['x'], current_powerup['y'], powerup_info['size']/2)
    glColor3f(*powerup_info['color']) 
    if powerup_info['shape'] == 'cube':
        glutSolidCube(powerup_info['size'])
    else:
        quad = gluNewQuadric()
        glRotatef(90, 1, 0, 0)
        gluCylinder(quad, powerup_info['size']/2, powerup_info['size']/2, powerup_info['size'], 32, 1)

    glPopMatrix()


def check_powerup_collision():
    global current_powerup, player1_health, player2_health, player1_speed, player2_speed
    
    if current_powerup is None:
        return
    
    #collision with player 1
    if math.hypot(current_powerup['x'] - player1_pos[0], current_powerup['y'] - player1_pos[1]) < 30:
        apply_powerup('player1', current_powerup['type'])
        current_powerup = None
        return
    
    #collision with player 2
    if math.hypot(current_powerup['x'] - player2_pos[0], current_powerup['y'] - player2_pos[1]) < 30:
        apply_powerup('player2', current_powerup['type'])
        current_powerup = None


def apply_powerup(player, powerup_type):
    global player1_health, player2_health, player1_speed, player2_speed, max_health, max_speed
    global player1_speed_boost_end, player2_speed_boost_end
    current_time = time.time()
    
    if player == 'player1':
        if powerup_type == 'health':
            player1_health = min(player1_health + 5, max_health)
            print(f"Player 1 collected {powerup_type}! Health: {player1_health}")
        elif powerup_type == 'speed':
            player1_speed = max_speed
            player1_speed_boost_end = current_time + 10  # Speed boost lasts 20 seconds
            print(f"Player 1 collected {powerup_type}! Speed increased for 20 seconds!")
    else:
        if powerup_type == 'health':
            player2_health = min(player2_health + 5, max_health)
            print(f"Player 2 collected {powerup_type}! Health: {player2_health}")
        elif powerup_type == 'speed':
            player2_speed = max_speed
            player2_speed_boost_end = current_time + 10  # Speed boost lasts 20 seconds
            print(f"Player 2 collected {powerup_type}! Speed increased for 20 seconds!")

def update_powerups():
    global current_powerup, powerup_spawn_time, player1_speed, player2_speed
    current_time = time.time()
    
    if current_time >= player1_speed_boost_end and player1_speed == max_speed:
        player1_speed = 1

    if current_time >= player2_speed_boost_end and player2_speed == max_speed:
        player2_speed = 1
    
    if current_powerup is None and time.time() - powerup_spawn_time >= powerup_spawn_cooldown_timer:
        spawn_powerup()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(950, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"423 rivalz")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutSpecialUpFunc(specialKeyUpListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()