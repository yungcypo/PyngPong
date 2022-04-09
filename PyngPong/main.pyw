from asyncore import ExitNow
from re import S
from tkinter import Toplevel
import pygame, sys, random

# credits - cypo


# ===== INIT STUFF ===== #

pygame.init()
CLOCK = pygame.time.Clock()
FPS = 60
W, H = 900, 600
SCREEN = pygame.display.set_mode((W, H))
TITLE = pygame.display.set_caption("PyngPong")
ICON = pygame.image.load("assets\images\icon.png")
pygame.display.set_icon(ICON)

pygame.mixer.init()
sound = pygame.mixer.Sound("assets\sounds\hit1.wav")
sound.set_volume(0.25)


colors = {
    "white" : (255, 255, 255),
    "gray" : (20, 20, 20),
    "lightgray" : (50, 50, 50),
    "red" : (255, 0, 0),
    "hover" : (50, 50, 50),
    "clicked" : (100, 100, 100)}


colors["foreground"] = colors["white"]
colors["background"] = colors["gray"]

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
        self.color = colors["background"]
        self.outline_color = colors["foreground"]
        self.disabled = False
        self.hover = False
        self.clicked = False

    def check(self):  # check hover and clicked
        if not self.disabled:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.hover = True
                if pygame.mouse.get_pressed()[0]:
                    self.clicked = True
                else:
                    self.clicked = False
            else:
                self.hover = False

    def draw(self):
        self.check()
        if self.hover and not self.disabled:
            self.color = (colors["hover"])
            if self.clicked:
                self.color = (colors["clicked"])                
        else:
            self.color = (colors["background"])

        pygame.draw.polygon(SCREEN, self.color,
            (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft))
        pygame.draw.aalines(SCREEN, self.outline_color, True,
            (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft))
        SCREEN.blit(self.text_surf, self.text_rect)

        
class Player:
    def __init__(self, w, h, **kwargs):
        self.w = w
        self.h = h 
        self.kwargs = kwargs
        self.surf = pygame.surface.Surface((self.w, self.h))
        self.rect = self.surf.get_rect(**self.kwargs)
        self.surf.fill(colors["foreground"])
        self.speed = M_PS
        self.moving = ""
        self.score = 0
    
    def draw(self):  
        self.move()
        SCREEN.blit(self.surf, self.rect)

    def move(self):
        if self.moving == "up":
            self.rect.centery -= self.speed
        if self.moving == "down":
            self.rect.centery += self.speed
            
        if self.rect.top < M_PX:
            self.rect.top = M_PX
        if self.rect.bottom > H - M_PX:
            self.rect.bottom = H - M_PX


class Ball:
    def __init__(self, radius, speed):
        self.radius = radius
        self.speed = speed
        self.rect = pygame.rect.Rect(0, 0, radius*2, radius*2)
        self.rect.center = (W/2, H/2)
        self.x = random.choice((True, False))
        self.y = random.choice((True, False))

    def draw(self):
        self.move()
        pygame.draw.circle(SCREEN, colors["foreground"], self.rect.center, self.radius)

    def move(self):
        if self.x:
            self.rect.centerx += self.speed
        if not self.x:
            self.rect.centerx -= self.speed
        if self.y:
            self.rect.centery += self.speed
        if not self.y:
            self.rect.centery -= self.speed


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
# M - MULTIPLAYER
# S - SINGLEPLAYER
# P - PAUSEMENU

MM_title = Text("PYNGPONG", 72, center = (W/2, H/24*7))
MM_S = Button("Singleplayer", 32, midtop = (MM_title.rect.centerx, MM_title.rect.bottom + 32))
MM_M = Button("Multiplayer", 32, midtop = (MM_S.rect.centerx, MM_S.rect.bottom + 32))
MM_settings = Button("Settings", 20, topright = (MM_M.rect.centerx - 16, MM_M.rect.bottom + 24))
MM_E = Button("Exit", 20, topleft = (MM_M.rect.centerx + 16, MM_M.rect.bottom + 24))
MM_I = Button("i", 20, topleft = (MM_E.rect.right + 22, MM_M.rect.bottom + 24))
MM_info = Text("By Cypo :) ", 20, midbottom = (W/2, H - 10))

MM_info_trigger = False

MM_S.disabled = True
MM_S.outline_color = colors["lightgray"]
MM_E.outline_color = colors["red"]
MM_buttons = [MM_S, MM_M, MM_settings]



PM_title = Text("Paused", 72, center = (W/2, H/24*7))
PM_C = Button("Continue", 32, midtop = (PM_title.rect.centerx, PM_title.rect.bottom + 32))
PM_S = Button("Settings", 32, midtop = (PM_C.rect.centerx, PM_C.rect.bottom + 28))
PM_E = Button("Exit", 20, midtop = (PM_S.rect.centerx, PM_S.rect.bottom + 24))
PM_E.outline_color = colors["red"]


EM_title = Text("Are you sure you want to exit?", 32, midbottom = (W/2, H/2 - 24))
EM_E = Button("Exit", 24, topright = (EM_title.rect.centerx - 20, EM_title.rect.bottom + 24))
EM_C = Button("Cancel", 24, topleft = (EM_title.rect.centerx + 20, EM_title.rect.bottom + 24))
EM_E.outline_color = colors["red"]


M_title = Text("Multiplayer", 32, midtop = (W/2, 16))
M_press_key = Text("Press any key to begin", 24, center = (W/2, H/2))
M_press_key_var = True

M_PW, M_PH = 4, 100  # width, height
M_PX, M_PY = 12, H/2  # X, Y
M_PS = 4  # speed
M_P1 = Player(M_PW, M_PH, center = (M_PX, M_PY))
M_P2 = Player(M_PW, M_PH, center = (W - M_PX, M_PY))

M_BR = 12  # radius
M_BS = 5  # speed; changes to 5 later
M_BSplus = 0.3  # adding speed
M_B = Ball(M_BR, M_BS)

M_S1 = Score(M_P1.score, topleft = (10, 10))
M_S2 = Score(M_P2.score, topright = (W - 10, 10))


S_title = Text("Under construction", 32, midbottom = (W/2, H/2 - 16))
S_return = Button("Return", 20, midtop = (S_title.rect.centerx, S_title.rect.bottom + 16))


# ===== FUNCTIONS 1 ===== #

def controls():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    SCREEN.fill(colors["background"])
def update():
    CLOCK.tick(FPS)
    pygame.display.update()

def enable(list):
    for i in list:
        i.disabled = False
def disable(list):
    for i in list:
        i.disabled = True


def MM_draw():
    MM_title.draw()
    MM_S.draw()
    MM_M.draw()
    MM_settings.draw()
    MM_E.draw()
    MM_I.draw()
    if MM_info_trigger:
        MM_info.draw()


def PM_draw():
    PM_title.draw()
    PM_C.draw()
    PM_S.draw()
    PM_E.draw()


def EM_draw():
    EM_title.draw()
    EM_E.draw()
    EM_C.draw()



def M_reset():
    M_B.x = random.choice((True, False))
    M_B.y = random.choice((True, False))
    M_B.rect.center = W/2, H/2
    M_B.speed = round((M_B.speed + M_BS) / 2.25, 2)
    

def M_collide():
    if M_B.rect.top <= 0:
        M_B.y = True
    if M_B.rect.bottom >= H:
        M_B.y = False

    if M_B.rect.colliderect(M_P1.rect):
        M_B.x = True
        M_B.speed = round(M_B.speed + M_BSplus, 2)
    if M_B.rect.colliderect(M_P2.rect):
        M_B.x = False
        M_B.speed = round(M_B.speed + M_BSplus, 2)
    
    if M_B.rect.right < 0:
        M_P2.score += 1
        M_S2.update(M_P2.score)
        M_reset()
    if M_B.rect.left > W:
        M_P1.score += 1
        M_S1.update(M_P1.score)
        M_reset()

def M_draw():
    SCREEN.fill(colors["background"])
    pygame.draw.aaline(SCREEN, colors["foreground"], (W/2, M_title.rect.bottom + 16), (W/2, H))
    M_collide()

    M_title.draw()
    M_P1.draw()
    M_P2.draw()
    M_B.draw()
    M_S1.draw()
    M_S2.draw()

    if M_press_key_var:
        pygame.draw.polygon(SCREEN, colors["background"], 
            ((M_press_key.rect.left - 10, M_press_key.rect.top - 10),
                (M_press_key.rect.right + 10, M_press_key.rect.top - 10),
                (M_press_key.rect.right + 10, M_press_key.rect.bottom + 10),
                (M_press_key.rect.left - 10, M_press_key.rect.bottom + 10)))
        M_press_key.draw()
    
        
def S_draw():
    S_title.draw()
    S_return.draw()

# ===== FUNCTIONS 2 ===== #

def MAINMENU():
    global MM_info_trigger
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    EXITMENU()
            if event.type == pygame.MOUSEBUTTONUP:
                if MM_S.hover:
                    SINGLEPLAYER()
                if MM_M.hover:
                    MULTIPLAYER()
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
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:        
                if EM_E.hover:
                    pygame.quit()
                    sys.exit()
                if EM_C.hover:
                    return

        SCREEN.fill(colors["background"])

        EM_draw()

        update()


def SINGLEPLAYER():
    while True:
        controls()
        update()

def MULTIPLAYER():
    global M_press_key_var
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    M_P1.moving = "up"
                if event.key == pygame.K_s:
                    M_P1.moving = "down"
                if event.key == pygame.K_UP:
                    M_P2.moving = "up"
                if event.key == pygame.K_DOWN:
                    M_P2.moving = "down"
                if event.key == pygame.K_ESCAPE:
                    PAUSEMENU()
                M_press_key_var = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    M_P1.moving = ""
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    M_P2.moving = ""

        SCREEN.fill(colors["background"])

        M_draw()

        if M_press_key_var:
            M_B.rect.center = (W/2, H/2)
            
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
                if S_return.hover:
                    return

        SCREEN.fill(colors["background"])

        S_draw()

        update()








        


        

MAINMENU()
