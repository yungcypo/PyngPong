import sys
import pygame
import random
import json


# ===== INIT STUFF ===== #

pygame.init()
CLOCK = pygame.time.Clock()
FPS = 60
W, H = 850, 600
SCREEN = pygame.display.set_mode((W, H))
TITLE = pygame.display.set_caption("PyngPong")
ICON = pygame.image.load("assets\images\icon.png")
pygame.display.set_icon(ICON)

pygame.mixer.init()
sound1 = pygame.mixer.Sound("assets\sounds\hit1.wav")  # ball bounce
sound2 = pygame.mixer.Sound("assets\sounds\hit2.wav")  # goal 
sound3 = pygame.mixer.Sound("assets\sounds\hit3.wav")  # button hover
sound4 = pygame.mixer.Sound("assets\sounds\hit4.wav")  # button click
sound_list = [sound1, sound2, sound3, sound4]
for i in sound_list:
    i.set_volume(0.75)
sound4.set_volume(0.25)

with open ("assets\JSON\settings.json", "r") as json_file:
    game_settings = json.load(json_file)
with open ("assets\JSON\stats.json", "r") as json_file:
    game_stats = json.load(json_file)

# used for stats
current_FPS = 0
current_time = 0
total_score = 0


colors = {
    "white" : (255, 255, 255),
    "gray" : (20, 20, 20),
    "lightgray" : (50, 50, 50),
    "red" : (255, 0, 0),
    "green" : (0, 255, 0),
    "hover" : (50, 50, 50),
    "clicked" : (100, 100, 100)}

theme = game_settings["theme"]

if theme == "black":
    colors["foreground"] = colors["white"]
    colors["background"] = colors["gray"]
    colors["exitcolor"] = colors["red"]
else:
    colors["foreground"] = colors["white"]
    colors["background"] = colors["gray"]
    colors["exitcolor"] = colors["red"]


def getfont(size):
    return pygame.font.Font("assets\\fonts\consolas.ttf", size)


# ===== CLASSES ===== #

class Text:
    def __init__(self, text, size, **kwargs):
        self.text = text
        self.size = size
        self.kwargs = kwargs
        self.surf = getfont(self.size).render(str(self.text), True, colors["foreground"])
        self.rect = self.surf.get_rect(**self.kwargs)
    
    def draw(self):
        SCREEN.blit(self.surf, self.rect)


class Button:
    def __init__(self, text, fontsize, **kwargs):
        self.text = str(text)
        self.fontsize = fontsize
        self.kwargs = kwargs
        self.padding = self.fontsize/2
        self.text_surf = getfont(self.fontsize).render(self.text, True, colors["foreground"])
        self.text_rect = self.text_surf.get_rect(**self.kwargs)
        self.surf = pygame.surface.Surface((self.text_rect.width + self.padding * 2, self.text_rect.height + self.padding * 2))
        self.rect = self.surf.get_rect(center = self.text_rect.center)
        self.outline_width = 2
        self.outline_surf = pygame.surface.Surface((self.text_rect.width + self.padding * 2 + self.outline_width, self.text_rect.height + self.padding * 2 + self.outline_width))
        self.outline_rect = self.outline_surf.get_rect(center = self.text_rect.center)
        self.border_radius = int(self.fontsize/7)
        self.color = colors["background"]
        self.outline_color = colors["foreground"]
        self.disabled = False
        self.hover = False
        self.clicked = False
        self.play_hoversound = True
        self.play_clicksound = True

    def check(self):  # check hover and clicked
        if not self.disabled:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.hover = True
                if self.play_hoversound:
                    playsound(4)
                    self.play_hoversound = False
                if pygame.mouse.get_pressed()[0]:
                    self.clicked = True
                    if self.play_clicksound:
                        playsound(3)
                        self.play_clicksound = False
                else:
                    self.clicked = False
                    self.play_clicksound = True
            else:
                self.hover = False
                self.play_hoversound = True

    def draw(self):
        self.check()
        if self.hover and not self.disabled:
            self.color = (colors["hover"])
            if self.clicked:
                self.color = (colors["clicked"])                
        else:
            self.color = (colors["background"])
        '''
        pygame.draw.polygon(SCREEN, self.color,
            (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft))
        pygame.draw.aalines(SCREEN, self.outline_color, True,
            (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft))
        '''
        pygame.draw.rect(SCREEN, self.outline_color, self.outline_rect, border_radius = self.border_radius)
        pygame.draw.rect(SCREEN, self.color, self.rect, border_radius = self.border_radius)
        SCREEN.blit(self.text_surf, self.text_rect)

        
class Player:
    def __init__(self, w, h, s, direction, **kwargs):
        self.w = w
        self.h = h 
        self.speed = s
        self.direction = direction
        self.kwargs = kwargs
        self.surf = pygame.surface.Surface((self.w, self.h))
        self.rect = self.surf.get_rect(**self.kwargs)
        self.surf.fill(colors["foreground"])
        self.moving1 = False
        self.moving2 = False
        self.score = 0
    
    def draw(self):  
        self.move()
        SCREEN.blit(self.surf, self.rect)

    def move(self):
        if self.direction == "vertical":
            if self.moving1:
                self.rect.centery -= self.speed
            if self.moving2:
                self.rect.centery += self.speed
        if self.direction == "horizontal":
            if self.moving1:
                self.rect.centerx += self.speed
            if self.moving2:
                self.rect.centerx -= self.speed
        


        if self.direction == "vertical":
            if self.rect.top < self.w:
                self.rect.top = self.w
            if self.rect.bottom > H - self.w:
                self.rect.bottom = H - self.w
            
        if self.direction == "horizontal":
            if self.rect.left < self.h:
                self.rect.left = self.h
            if self.rect.right > W - self.h:
                self.rect.right = W - self.h


class Ball:
    def __init__(self, radius, speed):
        self.radius = radius
        self.speed = speed
        self.rect = pygame.rect.Rect(0, 0, radius*2, radius*2)
        self.rect.center = (W/2, H/2)
        self.x = random.choice((True, False))
        self.y = random.choice((True, False))
        self.disabled = False
        self.distance = 0

    def draw(self):
        self.move()
        pygame.draw.circle(SCREEN, colors["foreground"], self.rect.center, self.radius)

    def move(self):
        if not self.disabled:
            if self.x:
                self.rect.centerx += self.speed
            if not self.x:
                self.rect.centerx -= self.speed
            if self.y:
                self.rect.centery += self.speed
            if not self.y:
                self.rect.centery -= self.speed
            self.distance += int(self.speed)


class Score:
    def __init__(self, value, **kwargs):
        self.value = value
        self.kwargs = kwargs
        self.font = getfont(32)

    def draw(self):
        self.surf = self.font.render(str(self.value), True, colors["foreground"])
        self.rect = self.surf.get_rect(**self.kwargs)
        SCREEN.blit(self.surf, self.rect)

    def update(self, value):
        self.value = value




# ===== OBJECTS + ===== #

# MM - MAINMENU
# PM - PAUSEMENU
# EM - EXITMENU
# SM - SETTINGSMENU
# D - DUO
# S - SOLO
# Q - QUAD

MM_title = Text("PYNGPONG", 72, center = (W/2, H/24*7))
MM_S = Button("Solo", 32, topright = (MM_title.rect.centerx - 20, MM_title.rect.bottom + 32))
MM_D = Button("Duo", 32, topleft = (MM_title.rect.centerx + 20, MM_title.rect.bottom + 32))
MM_Q = Button("  Quad  ", 32, midtop = ((MM_S.rect.left + MM_D.rect.right) / 2, MM_D.rect.bottom + 32))
MM_settings = Button("Settings", 20, topright = (MM_Q.rect.centerx - 16, MM_Q.rect.bottom + 24))
MM_E = Button("Exit", 20, topleft = (MM_Q.rect.centerx + 16, MM_Q.rect.bottom + 24))
MM_I = Button("i", 20, topleft = (MM_E.rect.right + 22, MM_Q.rect.bottom + 24))
MM_info = Text("By Cypo :) ", 20, midbottom = (W/2, H - 10))

MM_S.rect

MM_info_trigger = False

MM_E.outline_color = colors["exitcolor"]

MM_buttons = [MM_S, MM_D, MM_Q, MM_settings, MM_E, MM_I]



PM_title = Text("Paused", 72, center = (W/2, H/24*7))
PM_C = Button("Continue", 32, midtop = (PM_title.rect.centerx, PM_title.rect.bottom + 32))
PM_M = Button("Main Menu", 32, midtop = (PM_C.rect.centerx, PM_C.rect.bottom + 28))
PM_S = Button("Settings", 20, topleft = (PM_M.rect.left + 16, PM_M.rect.bottom + 24))
PM_E = Button("Exit", 20, topright = (PM_M.rect.right - 16, PM_M.rect.bottom + 24))
PM_E.outline_color = colors["exitcolor"]

PM_buttons = [PM_C, PM_M, PM_S, PM_E]



EM_title = Text("Are you sure you want to exit?", 32, midbottom = (W/2, H/2 - 24))
EM_E = Button("Exit", 24, topright = (EM_title.rect.centerx - 20, EM_title.rect.bottom + 24))
EM_C = Button("Cancel", 24, topleft = (EM_title.rect.centerx + 20, EM_title.rect.bottom + 24))
EM_E.outline_color = colors["exitcolor"]

EM_buttons = [EM_E, EM_C]


SM_title = Text("Settings", 32, topleft = (24, 24))
SM_under_construction = Text("Under construction", 32, center = (W/2, H/2))
SM_return = Button("Return", 20, midtop = (SM_under_construction.rect.centerx, SM_under_construction.rect.bottom + 16))
SM_sound = Button("Sound", 20, topleft = (32, SM_title.rect.bottom + 32))
SM_cancel = Button("Cancel", 20, bottomright = (W - 32, H - 32))
SM_save = Button("Save", 20, bottomright = (SM_cancel.rect.left - 24, H - 32))



D_title = Text("Duo", 32, midtop = (W/2, 16))
D_press_key_text = Text("Press any key to begin", 24, center = (W/2, H/2))
D_press_key_var = True
D_W = Button("W", 20, midbottom = (W/5, H/2 - 16))
D_S = Button("S", 20, midtop = (W/5, H/2 + 16 ))
D_U = Button("↑", 20, midbottom = (W/5*4, H/2 - 16))
D_D = Button("↓", 20, midtop = (W/5*4, H/2 + 16))

D_buttons = [D_W, D_S, D_U, D_D] 

D_PW, D_PH = 4, 100  # width, height
D_PX, D_PY = 12, H/2  # X, Y
D_PS = 4  # speed
D_P1 = Player(D_PW, D_PH, D_PS, "vertical", center = (D_PX, D_PY))
D_P2 = Player(D_PW, D_PH, D_PS, "vertical", center = (W - D_PX, D_PY))

D_BR = 12  # radius
D_BS = 5  # speed; changes to 5 later
D_BSplus = 0.3  # adding speed
D_B = Ball(D_BR, D_BS)

D_S1 = Score(D_P1.score, topleft = (10, 10))
D_S2 = Score(D_P2.score, topright = (W - 10, 10))



S_title = Text("Solo", 32, midtop = (W/2, 16))
S_press_key_text = Text("Press any key to begin", 24, center = (W/2, H/2))
S_press_key_var = True
S_A = Button("A", 20, bottomright = (W/2 - 14, H/4*3 - 24))
S_D = Button("D", 20, bottomleft = (W/2 + 14, H/4*3 - 24))
S_L = Button("←", 20, bottomright = (W/2 - 14, H/4*3 + 24))
S_R = Button("→", 20, bottomleft = (W/2 + 14, H/4*3 + 24))

S_buttons = [S_A, S_D, S_L, S_R]

S_PW, S_PH = 160, 4
S_PX, S_PY = W/2, H - 12
S_PS = 4
S_P1 = Player(S_PW, S_PH, S_PS, "horizontal", center = (S_PX, S_PY))

S_BR = 12
S_BS = 5
S_BSplus = 0.3
S_B = Ball(S_BR, S_BS)
S_B.y = True

S_S1 = Score(S_P1.score, midtop = (W/2, S_title.rect.bottom + 12))



Q_title = Text("Quad", 24, center = (W/2, H/2))
Q_press_key_text = Text("Press any key to begin", 24, center = (W/2, H/2))
Q_press_key_var = True
Q_W = Button("W", 16, bottomleft = (32, H/2 - 12))
Q_S = Button("S", 16, topleft = (32, H/2 + 12))
Q_V = Button("V", 16, bottomright = (W/2 - 12, H - 32))
Q_B = Button("B", 16, bottomleft = (W/2 + 12, H - 32))
Q_L = Button("←", 16, topright = (W/2 - 12, 32))
Q_R = Button("→", 16, topleft = (W/2 + 12, 32))
Q_6 = Button("6", 16, bottomright = (W - 32, H/2 - 12))
Q_9 = Button("9", 16, topright = (W - 32, H/2 + 12))

Q_buttons = [Q_W, Q_S, Q_V, Q_B, Q_L, Q_R, Q_6, Q_9]
for i in Q_buttons:
    i.disabled = True

Q_PW, Q_PH = 4, 160
Q_PX, Q_PY = 12, H/2
Q_PS = 4
Q_P1 = Player(Q_PW, Q_PH, Q_PS, "vertical", center = (Q_PX, Q_PY))
Q_P2 = Player(Q_PH, Q_PW, Q_PS*1.5, "horizontal", center = (W/2, H - Q_PX))
Q_P3 = Player(Q_PH, Q_PW, Q_PS*1.5, "horizontal", center = (W/2, Q_PX))
Q_P4 = Player(Q_PW, Q_PH, Q_PS, "vertical", center = (W - Q_PX, Q_PY))

Q_BR = 12
Q_BS = 5
Q_BSplus = 0.3
Q_B = Ball(Q_BR, Q_BS)

Q_S1 = Score(Q_P1.score, midright = (Q_title.rect.left - 16, Q_title.rect.centery))
Q_S2 = Score(Q_P2.score, midtop = (Q_title.rect.centerx, Q_title.rect.bottom + 16))
Q_S3 = Score(Q_P3.score, midbottom = (Q_title.rect.centerx, Q_title.rect.top - 16))
Q_S4 = Score(Q_P4.score, midleft = (Q_title.rect.right + 16, Q_title.rect.centery))


allpress_key_var = [S_press_key_var, D_press_key_var, Q_press_key_var]
allplayers = [S_P1, D_P1, D_P2, Q_P1, Q_P2, Q_P3, Q_P4]
allballs = [S_B, D_B, Q_B]
allscore = [S_S1, D_S1, D_S2, Q_S1, Q_S2, Q_S3, Q_S4]

# ===== FUNCTIONS 1 ===== #

def update():
    global current_FPS, current_time
    current_FPS += 1
    if current_FPS >= 60:
        current_FPS = 0
        current_time += 1
    #print("FPS: " + str(round(CLOCK.get_fps(), 2)))
    CLOCK.tick(FPS)
    pygame.display.update()
def reset_score():
    for i in allpress_key_var:
        i = True
    for i in allplayers:
        i.score = 0
    for i in allballs:
        i.rect.center = (W/2, H/2)
    for i in allscore:
        i.update(0)
def save_stats():
    global total_score
    game_stats["time_spent"] += current_time
    game_stats["distance_ball"] += S_B.distance
    game_stats["distance_ball"] += D_B.distance
    game_stats["distance_ball"] += Q_B.distance
    game_stats["total_score"] += total_score
    with open ("assets\JSON\stats.json", "w") as json_file:
        json.dump(game_stats, json_file, indent=4)
def playsound(value):
    if game_settings["sound"]:
        sound_list[value - 1].play()

def MM_draw():
    MM_title.draw()
    MM_S.draw()
    MM_D.draw()
    MM_Q.draw()
    MM_settings.draw()
    MM_E.draw()
    MM_I.draw()
    if MM_info_trigger:
        MM_info.draw()


def PM_draw():
    PM_title.draw()
    PM_C.draw()
    PM_M.draw()
    PM_S.draw()
    PM_E.draw()


def EM_draw():
    EM_title.draw()
    EM_E.draw()
    EM_C.draw()


def SM_sound_f(value):
    if value:
        SM_sound.outline_color = colors["green"]
    if not value:
        SM_sound.outline_color = colors["red"] 

def SM_draw():
    SM_title.draw()
    pygame.draw.aaline(SCREEN, colors["foreground"], 
        (SM_title.rect.left - 8, SM_title.rect.bottom + 8),
        (SM_title.rect.right + 32, SM_title.rect.bottom + 8))
    SM_sound_f(game_settings["sound"])
    SM_sound.draw()
    SM_under_construction.draw()
    SM_save.draw()
    SM_cancel.draw()


def D_reset():
    D_B.rect.center = W/2, H/2
    D_B.x = random.choice((True, False))
    D_B.y = random.choice((True, False))
    D_B.speed = round((D_B.speed + D_BS) / 2.25, 2)

def D_collide():
    global total_score
    if D_B.rect.top <= 0:
        D_B.y = True
        playsound(1)
    if D_B.rect.bottom >= H:
        D_B.y = False
        playsound(1)

    if D_B.rect.colliderect(D_P1.rect):
        D_B.x = True
        playsound(1)
        D_B.speed = round(D_B.speed + D_BSplus, 2)
    if D_B.rect.colliderect(D_P2.rect):
        D_B.x = False
        playsound(1)
        D_B.speed = round(D_B.speed + D_BSplus, 2)
    
    if D_B.rect.right < 0:
        playsound(2)
        total_score += 1
        D_P2.score += 1
        D_S2.update(D_P2.score)
        D_reset()
    if D_B.rect.left > W:
        playsound(2)
        total_score += 1
        D_P1.score += 1
        D_S1.update(D_P1.score)
        D_reset()
    
def D_press_key():
    D_B.rect.center = (W/2, H/2)

    for i in D_buttons:
        i.disabled = True
        i.draw()
    
    pygame.draw.polygon(SCREEN, colors["background"], 
        ((D_press_key_text.rect.left - 10, D_press_key_text.rect.top - 10),
        (D_press_key_text.rect.right + 10, D_press_key_text.rect.top - 10),
        (D_press_key_text.rect.right + 10, D_press_key_text.rect.bottom + 10),
        (D_press_key_text.rect.left - 10, D_press_key_text.rect.bottom + 10)))

    D_press_key_text.draw()
    D_reset()

def D_draw():
    pygame.draw.aaline(SCREEN, colors["foreground"], (W/2, D_title.rect.bottom + 16), (W/2, H))
    D_collide()

    D_title.draw()
    D_P1.draw()
    D_P2.draw()
    D_B.draw()
    D_S1.draw()
    D_S2.draw()



def S_press_key():
    S_B.rect.center = (W/2, H/2)

    for i in S_buttons:
        i.disabled = True
        i.draw()
    
    pygame.draw.polygon(SCREEN, colors["background"],
        ((S_press_key_text.rect.left - 10, S_press_key_text.rect.top - 10),
        (S_press_key_text.rect.right + 10, S_press_key_text.rect.top - 10),
        (S_press_key_text.rect.right + 10, S_press_key_text.rect.bottom + 10),
        (S_press_key_text.rect.left - 10, S_press_key_text.rect.bottom + 10)))
    
    S_press_key_text.draw()
    
def S_reset():
    S_B.rect.centerx = random.randint(int(W/8), int(W/8*7))
    S_B.rect.centery = random.randint(int(H/8), int(H/4))
    S_B.x = random.choice((True, False))

    S_B.speed = round((S_B.speed + S_BS) / 2.25, 2)

def S_collide():
    global total_score
    if S_B.rect.top <= 0:
        S_B.y = True
        playsound(1)
    if S_B.rect.left <= 0:
        S_B.x = True
        playsound(1)
    if S_B.rect.right >= W:
        S_B.x = False
        playsound(1)

    if S_B.rect.colliderect(S_P1) and S_B.y:
        total_score += 1
        S_B.y = False
        playsound(1)
        S_B.speed = round(S_B.speed + S_BSplus, 2)
        S_P1.score += 1

        
    if S_B.rect.top >= H:
        playsound(2)
        total_score -= 1
        S_P1.score -= 1
        S_reset()
    
    S_S1.update(S_P1.score)
        
def S_draw():
    S_collide()

    S_title.draw()
    S_P1.draw()
    S_B.draw()
    S_S1.draw()


def Q_reset():
    Q_B.rect.center = W/2, H/2

    Q_B.x = random.choice((True, False))
    Q_B.y = random.choice((True, False))
    Q_B.speed = round((Q_B.speed + Q_BS) / 2.25, 2)

def Q_collide():
    global total_score
    if Q_B.rect.right < 0:
        playsound(2)
        total_score += 1
        Q_P1.score += 1 
        Q_S1.update(Q_P1.score)
        Q_reset()
    if Q_B.rect.top > H:
        playsound(2)
        total_score += 1
        Q_P2.score += 1 
        Q_S2.update(Q_P2.score)
        Q_reset()
    if Q_B.rect.bottom < 0:
        playsound(2)
        total_score += 1
        Q_P3.score += 1 
        Q_S3.update(Q_P3.score)
        Q_reset()
    if Q_B.rect.left > W:
        playsound(2)
        total_score += 1
        Q_P4.score += 1 
        Q_S4.update(Q_P4.score)
        Q_reset()

    if Q_P1.rect.colliderect(Q_B.rect):
        Q_B.x = True
        playsound(1)
    if Q_P2.rect.colliderect(Q_B.rect):
        Q_B.y = False
        playsound(1)
    if Q_P3.rect.colliderect(Q_B.rect):
        Q_B.y = True
        playsound(1)
    if Q_P4.rect.colliderect(Q_B.rect):
        Q_B.x = False
        playsound(1)
    

def Q_press_key():
    Q_B.rect.center = (W/2, H/2)
    for i in Q_buttons:
        # i.disabled = True  # already are disabled 
        i.draw()
    
    pygame.draw.polygon(SCREEN, colors["background"], 
        ((Q_press_key_text.rect.left - 10, Q_press_key_text.rect.top - 10),
        (Q_press_key_text.rect.right + 10, Q_press_key_text.rect.top - 10),
        (Q_press_key_text.rect.right + 10, Q_press_key_text.rect.bottom + 10),
        (Q_press_key_text.rect.left - 10, Q_press_key_text.rect.bottom + 10)))

    Q_press_key_text.draw()
    Q_reset()

def Q_draw():
    Q_collide()

    Q_title.draw()
    Q_P1.draw()
    Q_P2.draw()
    Q_P3.draw()
    Q_P4.draw()
    Q_B.draw()

    if not Q_press_key_var:
        Q_S1.draw()
        Q_S2.draw()
        Q_S3.draw()
        Q_S4.draw()

# ===== FUNCTIONS 2 ===== #

def MAINMENU():
    reset_score()
    global MM_info_trigger, allpress_key_var
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    EXITMENU()
            if event.type == pygame.MOUSEBUTTONUP:
                if MM_S.hover:
                    SOLO()
                if MM_D.hover:
                    DUO()
                if MM_Q.hover:
                    QUAD()
                if MM_settings.hover:
                    SETTINGS()
                if MM_E.hover:
                    EXITMENU()
                if MM_I.hover:
                    MM_info_trigger = not MM_info_trigger

        SCREEN.fill(colors["background"])
        MM_draw()
        
        update()
    
def PAUSEMENU():
    for i in allplayers:
        i.moving1 = False
        i.moving2 = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONUP:
                if PM_C.hover:
                    return
                if PM_M.hover:
                    MAINMENU()
                if PM_S.hover:
                    SETTINGS()
                if PM_E.hover:
                    EXITMENU()

        SCREEN.fill(colors["background"])
        
        PM_draw()

        update()

def EXITMENU():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN:
                    save_stats()
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:        
                if EM_E.hover:
                    save_stats()
                    pygame.quit()
                    sys.exit()
                if EM_C.hover:
                    return


        

        SCREEN.fill(colors["background"])

        EM_draw()

        update()


def SOLO():
    global S_press_key_var
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    S_P1.moving1 = True
                if event.key == pygame.K_RIGHT:
                    S_P1.moving1 = True
                if event.key == pygame.K_a:
                    S_P1.moving2 = True
                if event.key == pygame.K_LEFT:
                    S_P1.moving2 = True
                if event.key == pygame.K_ESCAPE:
                    PAUSEMENU()
                if S_press_key_var and event.key != pygame.K_ESCAPE:
                    S_press_key_var = False
                
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    S_P1.moving1 = False
                if event.key == pygame.K_RIGHT:
                    S_P1.moving1 = False
                if event.key == pygame.K_a:
                    S_P1.moving2 = False
                if event.key == pygame.K_LEFT:
                    S_P1.moving2 = False
                    
        SCREEN.fill(colors["background"])

        S_draw()

        if S_press_key_var:
            S_press_key()

        update()

def DUO():
    global D_press_key_var
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    D_P1.moving1 = True
                if event.key == pygame.K_s:
                    D_P1.moving2 = True
                if event.key == pygame.K_UP:
                    D_P2.moving1 = True
                if event.key == pygame.K_DOWN:
                    D_P2.moving2 = True
                if event.key == pygame.K_ESCAPE:
                    PAUSEMENU()
                if D_press_key_var and event.key != pygame.K_ESCAPE:
                    D_press_key_var = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    D_P1.moving1 = False
                if event.key == pygame.K_s:
                    D_P1.moving2 = False
                if event.key == pygame.K_UP:
                    D_P2.moving1 = False
                if event.key == pygame.K_DOWN:
                    D_P2.moving2 = False


        SCREEN.fill(colors["background"])

        D_draw()

        if D_press_key_var:
            D_press_key()
            
        update()
    

def QUAD():
    global Q_press_key_var
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    PAUSEMENU()
                if Q_press_key_var and event.key != pygame.K_ESCAPE:
                    Q_press_key_var = False
                if event.key == pygame.K_w:
                    Q_P1.moving1 = True
                if event.key == pygame.K_s:
                    Q_P1.moving2 = True
                if event.key == pygame.K_b:
                    Q_P2.moving1 = True   
                if event.key == pygame.K_v:
                    Q_P2.moving2 = True
                if event.key == pygame.K_RIGHT:
                    Q_P3.moving1 = True
                if event.key == pygame.K_LEFT:
                    Q_P3.moving2 = True
                if event.key == pygame.K_KP9:
                    Q_P4.moving1 = True
                if event.key == pygame.K_KP6:
                    Q_P4.moving2 = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    Q_P1.moving1 = False
                if event.key == pygame.K_s:
                    Q_P1.moving2 = False
                if event.key == pygame.K_b:
                    Q_P2.moving1 = False   
                if event.key == pygame.K_v:
                    Q_P2.moving2 = False
                if event.key == pygame.K_RIGHT:
                    Q_P3.moving1 = False
                if event.key == pygame.K_LEFT:
                    Q_P3.moving2 = False
                if event.key == pygame.K_KP9:
                    Q_P4.moving1 = False
                if event.key == pygame.K_KP6:
                    Q_P4.moving2 = False

        SCREEN.fill(colors["background"])

        Q_draw()

        if Q_press_key_var:
            Q_press_key()
        
        update()


def SETTINGS():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    EXITMENU()
            if event.type == pygame.MOUSEBUTTONUP:
                if SM_sound.hover:
                    game_settings["sound"] = not game_settings["sound"]
                if SM_save.hover:
                    with open ("assets\JSON\settings.json", "w") as json_file:
                        json.dump(game_settings, json_file, indent=4)
                    return
                if SM_cancel.hover:
                    return

        SCREEN.fill(colors["background"])

        SM_draw()

        update()


MAINMENU()
