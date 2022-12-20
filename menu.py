import pygame
import random
from chess import play

FPS = 60

def font(x):
    return pygame.font.SysFont('tahoma', x)
#text = font.render('hello', True, (0, 0, 0))

C = 80
L, R, U, D = (0.5*C, 0.5*C, 0.5*C, 0.5*C)
W, H = (L + 8*C + R, U + 8*C + D)
CENTER = (int(W//2), int(H//2))


DARK_COLOR = (140, 162, 173)
LIGHT_COLOR = (255, 255, 255)
COLORS = [LIGHT_COLOR, DARK_COLOR]

BACKGROUND_COLOR = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (120, 120, 120)
LIGHT_GRAY = (190, 190, 190)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((L + C*8 + R, U + C*8 + D))


def show_board(screen):
    for i in range (8):
        for j in range (8):
            pygame.draw.rect(screen, COLORS[(i+j)%2], (L + i*C, U + j*C, C, C))
    

class Button:
    def __init__(self, center, size, function, text, t=30, color0=DARK_GRAY, color1=LIGHT_GRAY):
        x, y = center
        w, h = size
        self.center = center
        self.t = t
        self.rect = pygame.Rect((x-w//2, y-h//2), size)
        self.color0 = color0
        self.color1 = color1
        self.highlighted = False
        self.function = function
        self.text = text
        self.scroll = False
    
    def show_yourself(self, screen, pos):
        if self.rect.collidepoint(pos):
            color = self.color1
        else:
            color = self.color0
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        TExt = Text(self.text, self.center, self.t)
        TExt.show_yourself(screen)
    
    def change_text(self):
        text = self.text
        if text == 'Белые':
            self.text = 'Чёрные'
        elif text == 'Чёрные':
            self.text = 'Случайный'
        else:
            self.text = 'Белые'


class Text:
    def __init__(self, text, center, t=30, color=WHITE):
        self.center = center
        self.text = font(t).render(text, True, color)
    
    def show_yourself(self, screen):
        text_rect = self.text.get_rect(center=self.center)
        screen.blit(self.text, text_rect)


class Menu:
    def __init__(self, background_color=BACKGROUND_COLOR):
        self.background_color = background_color
        self.texts = []
        self.buttons = []
    
    def show_yourself(self, screen, pos):
        screen.fill(self.background_color)
        for button in self.buttons:
            button.show_yourself(screen, pos)
        for text in self.texts:
            text.show_yourself(screen)
    
    def append(self, element):
        if element.__class__.__name__ == 'Text':
            self.texts.append(element)
        elif element.__class__.__name__ == 'Button':
            self.buttons.append(element)
    
    def handle(self, pos):
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                if button.scroll:
                    button.change_text()
                else:
                    main(button.function(button))


def starting_menu(button):
    menu = Menu()
    menu.append(Text('Добро пожаловать', (int(W//2), int(H//2)-200), 50))
    menu.append(Button((int(W//2), int(H//2)-80), (300, 60), against_computer, 'Против компьютера', 30))
    menu.append(Button(CENTER, (300, 60), local_game, 'Локальная игра', 30))
    menu.append(Button((int(W//2), int(H//2)+80), (300, 60), bot_vs_bot, 'Бот против бота', 30))
    return menu

def against_computer(button):
    menu = Menu()
    menu.append(Text('Выберите цвет', (int(W//2), int(H//2)-200), 50))
    scrollbutton = Button(CENTER, (200, 60), None, 'Белые', 30)
    scrollbutton.scroll = True
    menu.append(scrollbutton)
    menu.append(Button((int(W//2), int(H//2)+100), (300, 60), human_vs_bot, 'Играть', 30))
    return menu

def human_vs_bot(button):
    menu = Menu()
    if button.text == 'Белые':
        play(['bot', 'human'])
    elif button.text == 'Чёрные':
        play(['human', 'bot'])
    else:
        play(random.choice([['bot', 'human'], ['human', 'bot']]))
    return menu

def local_game(button):
    menu = Menu()
    play(['human', 'human'])
    return menu

def bot_vs_bot(button):
    menu = Menu()
    play(['bot', 'bot'])
    return menu

def main(menu):
    finished = False
    clock = pygame.time.Clock()
    while not finished:
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                menu.handle(pos)
        menu.show_yourself(screen, pos)
        clock.tick(FPS)
        pygame.display.update()
    pygame.quit()

main(starting_menu(None))