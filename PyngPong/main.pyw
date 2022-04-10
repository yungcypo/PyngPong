import sys
import pygame
import random



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
# M - MULTIPLAYER
# S - SINGLEPLAYER


MM_title = Text("PYNGPONG", 72, center = (W/2, H/24*7))
MM_S = Button("Singleplayer", 32, midtop = (MM_title.rect.centerx, MM_title.rect.bottom + 32))
MM_M = Button("Multiplayer", 32, midtop = (MM_S.rect.centerx, MM_S.rect.bottom + 32))
MM_settings = Button("Settings", 20, topright = (MM_M.rect.centerx - 16, MM_M.rect.bottom + 24))
MM_E = Button("Exit", 20, topleft = (MM_M.rect.centerx + 16, MM_M.rect.bottom + 24))
MM_I = Button("i", 20, topleft = (MM_E.rect.right + 22, MM_M.rect.bottom + 24))
MM_info = Text("By Cypo :) ", 20, midbottom = (W/2, H - 10))

MM_info_trigger = False

MM_E.outline_color = colors["red"]

MM_buttons = [MM_S, MM_M, MM_settings]



PM_title = Text("Paused", 72, center = (W/2, H/24*7))
PM_C = Button("Continue", 32, midtop = (PM_title.rect.centerx, PM_title.rect.bottom + 32))
PM_M = Button("Main Menu", 32, midtop = (PM_C.rect.centerx, PM_C.rect.bottom + 28))
PM_S = Button("Settings", 20, topleft = (PM_M.rect.left + 16, PM_M.rect.bottom + 24))
PM_E = Button("Exit", 20, topright = (PM_M.rect.right - 16, PM_M.rect.bottom + 24))
PM_E.outline_color = colors["red"]


PM_buttons = [PM_C, PM_M, PM_S, PM_E]



EM_title = Text("Are you sure you want to exit?", 32, midbottom = (W/2, H/2 - 24))
EM_E = Button("Exit", 24, topright = (EM_title.rect.centerx - 20, EM_title.rect.bottom + 24))
EM_C = Button("Cancel", 24, topleft = (EM_title.rect.centerx + 20, EM_title.rect.bottom + 24))
EM_E.outline_color = colors["red"]

EM_buttons = [EM_E, EM_C]



SM_title = Text("Under construction", 32, midbottom = (W/2, H/2 - 16))
SM_return = Button("Return", 20, midtop = (SM_title.rect.centerx, SM_title.rect.bottom + 16))



M_title = Text("Multiplayer", 32, midtop = (W/2, 16))
M_press_key_text = Text("Press any key to begin", 24, center = (W/2, H/2))
M_press_key_var = True
M_W = Button("W", 20, midbottom = (W/5, H/2 - 16))
M_S = Button("S", 20, midtop = (W/5, H/2 + 16 ))
M_U = Button("↑", 20, midbottom = (W/5*4, H/2 - 16))
M_D = Button("↓", 20, midtop = (W/5*4, H/2 + 16))

M_buttons = [M_W, M_S, M_U, M_D] 

M_PW, M_PH = 4, 100  # width, height
M_PX, M_PY = 12, H/2  # X, Y
M_PS = 4  # speed
M_P1 = Player(M_PW, M_PH, M_PS, "vertical", center = (M_PX, M_PY))
M_P2 = Player(M_PW, M_PH, M_PS, "vertical", center = (W - M_PX, M_PY))

M_BR = 12  # radius
M_BS = 5  # speed; changes to 5 later
M_BSplus = 0.3  # adding speed
M_B = Ball(M_BR, M_BS)

M_S1 = Score(M_P1.score, topleft = (10, 10))
M_S2 = Score(M_P2.score, topright = (W - 10, 10))



S_title = Text("Singleplayer", 32, midtop = (W/2, 16))
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


# ===== FUNCTIONS 1 ===== #

def update():
    #print("FPS: " + str(round(CLOCK.get_fps(), 2)))
    CLOCK.tick(FPS)
    pygame.display.update()


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
    PM_M.draw()
    PM_S.draw()
    PM_E.draw()


def EM_draw():
    EM_title.draw()
    EM_E.draw()
    EM_C.draw()


def SM_draw():
    SM_title.draw()
    SM_return.draw()


def M_reset():
    M_B.rect.center = W/2, H/2

    M_B.x = random.choice((True, False))
    M_B.y = random.choice((True, False))
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
        M_reset()
    if M_B.rect.left > W:
        M_P1.score += 1
        M_reset()
    
    M_S1.update(M_P1.score)

def M_press_key():
    M_B.rect.center = (W/2, H/2)

    for i in M_buttons:
        i.disabled = True
        i.draw()
    
    pygame.draw.polygon(SCREEN, colors["background"], 
        ((M_press_key_text.rect.left - 10, M_press_key_text.rect.top - 10),
        (M_press_key_text.rect.right + 10, M_press_key_text.rect.top - 10),
        (M_press_key_text.rect.right + 10, M_press_key_text.rect.bottom + 10),
        (M_press_key_text.rect.left - 10, M_press_key_text.rect.bottom + 10)))

    M_press_key_text.draw()
    M_reset()

def M_draw():
    pygame.draw.aaline(SCREEN, colors["foreground"], (W/2, M_title.rect.bottom + 16), (W/2, H))
    M_collide()

    M_title.draw()
    M_P1.draw()
    M_P2.draw()
    M_B.draw()
    M_S1.draw()
    M_S2.draw()



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
    if S_B.rect.top <= 0:
        S_B.y = True
    if S_B.rect.left <= 0:
        S_B.x = True
    if S_B.rect.right >= W:
        S_B.x = False

    if S_B.rect.colliderect(S_P1) and S_B.y:
        S_B.y = False
        S_B.speed = round(S_B.speed + S_BSplus, 2)
        S_P1.score += 1
        

    if S_B.rect.top >= H:
        S_P1.score -= 1
        S_reset()
    
    S_S1.update(S_P1.score)
        
def S_draw():
    S_collide()

    S_title.draw()
    S_P1.draw()
    S_B.draw()
    S_S1.draw()

# ===== FUNCTIONS 2 ===== #

def MAINMENU():
    global MM_info_trigger
    M_P1.score = 0
    M_P2.score = 0
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

def MULTIPLAYER():
    global M_press_key_var
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXITMENU()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    M_P1.moving1 = True
                if event.key == pygame.K_s:
                    M_P1.moving2 = True
                if event.key == pygame.K_UP:
                    M_P2.moving1 = True
                if event.key == pygame.K_DOWN:
                    M_P2.moving2 = True
                if event.key == pygame.K_ESCAPE:
                    PAUSEMENU()
                if M_press_key_var and event.key != pygame.K_ESCAPE:
                    M_press_key_var = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    M_P1.moving1 = False
                if event.key == pygame.K_s:
                    M_P1.moving2 = False
                if event.key == pygame.K_UP:
                    M_P2.moving1 = False
                if event.key == pygame.K_DOWN:
                    M_P2.moving2 = False


        SCREEN.fill(colors["background"])

        M_draw()

        if M_press_key_var:
            M_press_key()
            
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
                if SM_return.hover:
                    return

        SCREEN.fill(colors["background"])

        SM_draw()

        update()


MAINMENU()
