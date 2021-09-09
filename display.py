import pygame
from math import ceil
from time import time

# Initialize pygame modules
pygame.init()

# Display settings
windowSize = (900, 500)
canvasSize = (700, 400)
sideMargin = windowSize[0]-canvasSize[0]
bottomMargin = windowSize[1]-canvasSize[1]
screen = pygame.display.set_mode(windowSize)
pygame.display.set_caption('Sorting Algorithms Visualizer')

# Font
baseFont = pygame.font.SysFont('Arial', 24)
# Used Colors
grey = (100, 100, 100)
green = (125, 240, 125)
white = (250, 250, 250)
red = (255, 50, 50)
black = (0, 0, 0)
blue = (50, 50, 255)


class Box:
    def __init__(self, rect):
        self.isActive = False
        self.rect     = pygame.Rect(rect)
    
    def update(self):
        self.mousePos = pygame.mouse.get_pos()
        self.clicked  = pygame.mouse.get_pressed() != (0, 0, 0)
        self.isActive = True if self.rect.collidepoint(self.mousePos) else False


class InputBox(Box):
    def __init__(self, name, color, rect):
        super().__init__(rect)
        self.name  = name
        self.color = color
        
    def draw(self):
        label = baseFont.render(self.name, True, self.color)
        screen.blit(label, (self.rect.x + (self.rect.w - label.get_width()) / 2, self.rect.y - 32))
        pygame.draw.rect(screen, self.color, self.rect, 3)


class TextBox(InputBox):
    def __init__(self, name, color, rect, text='100'):
        super().__init__(name, color, rect)
        self.text = text
        self.draw() # establish the correct width for initial rendering
    
    def draw(self):
        super().draw()
        surface = baseFont.render(self.text, True, self.color)
        screen.blit(surface, (self.rect.x + 10, self.rect.y + 10))
        self.rect.w = max(surface.get_width() + 20, 50)

    def update(self, event):
        super().update()
        if self.isActive and event.type == pygame.KEYDOWN:
            if   event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif event.unicode.isdigit()        : self.text += event.unicode
        

class SlideBox(InputBox):
    def __init__(self, name, color, rect):
        super().__init__(name, color, rect)
        self.start = self.rect.x + 6
        self.end   = self.rect.x + self.rect.w - 6
        self.value = self.start

    def draw(self):
        super().draw()
        pygame.draw.line(screen, self.color, (self.start, self.rect.y + 25), (self.end, self.rect.y + 25), 2)
        pygame.draw.line(screen, self.color, (self.value, self.rect.y + 5), (self.value, self.rect.y + 45), 12)

    def update(self, event):
        super().update()
        previousStart = self.start
        self.start  = self.rect.x + 6
        self.end    = self.rect.x + self.rect.w - 6
        self.value += self.start - previousStart
        
        if self.isActive:
            if self.clicked:
                if self.start <= self.mousePos[0] <= self.end: self.value = self.mousePos[0]
        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if   event.button == 4: self.value = min(self.value + 10, self.end)
                elif event.button == 5: self.value = max(self.value - 10, self.start)

class VerticalSliderBox(InputBox):
    def __init__(self, name, color, rect):
        super().__init__(name, color, rect)
        self.start = self.rect.y+6
        self.end   = self.rect.y+self.rect.h
        self.value = self.start
        self.isActive=True

    def draw(self):
        x=self.rect.x
        pygame.draw.line(screen, grey,  (x,  self.start-6),  (x,self.end), 25)
        pygame.draw.line(screen, white, (x+5,  self.value),  (x+5,self.value+20), 8)

    def update(self,event):
        super().update()
        previousStart = self.start
        self.start = self.rect.y+6
        self.end   = self.rect.y + self.rect.h
        self.value += self.start - previousStart
        if self.isActive:
            if self.clicked:
                if self.start <= self.mousePos[1] <= self.end: self.value = self.mousePos[1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if   event.button == 4: self.value = min(self.end  ,self.value + 10)
                elif event.button == 5: self.value = max(self.start,self.value - 10)

class ButtonBox(Box):
    def __init__(self, img_path, rect):
        super().__init__(rect)
        self.img = pygame.image.load(img_path)
    
    def draw(self):
        screen.blit(self.img, (self.rect.x, self.rect.y))

    def update(self):
       super().update()
       if self.isActive: self.isActive = True if self.clicked else False


class DropdownBox(InputBox):
    DEFAUTL_OPTION = 0

    def __init__(self, name, rect, font, color=grey):
        super().__init__(name, color, rect)
        self.isActive      = False
        self.font          = font
        self.options_color = white
        self.active_option = -1
        self.n_box_per_row = 1
        
    def add_options(self, options):
        self.options = options
        dropdown_x = self.rect.x+self.rect.width
        dropdown_width = windowSize[0]-dropdown_x
        self.n_box_per_row = ((len(self.options)-1)*self.rect.width)//dropdown_width
        self.dropdown_rect = pygame.Rect(dropdown_x, self.rect.y, self.n_box_per_row*self.rect.width, 400)

    def get_active_option(self):
        return self.options[self.DEFAUTL_OPTION]

    def get_option_rect(self, idx):
        row = idx // self.n_box_per_row
        col = idx % self.n_box_per_row
        return pygame.Rect(self.rect.x+self.rect.width*(col+1), self.rect.y+self.rect.height*row, self.rect.width, self.rect.height)

    def draw(self):
        super().draw()
        option_text = self.font.render(self.options[self.DEFAUTL_OPTION], 1, grey)
        screen.blit(option_text, option_text.get_rect(center=self.rect.center))

        if self.isActive:
            index = 0
            for i in range(self.DEFAUTL_OPTION+1, len(self.options)):
                rect = self.get_option_rect(index)
                index += 1
                
                options_color = black if i - 1 == self.active_option else grey
                pygame.draw.rect(screen, self.options_color, rect, 0)
                pygame.draw.rect(screen, self.color, rect, 3) # draw border
                option_text = self.font.render(self.options[i][:12], 1, options_color)
                screen.blit(option_text, option_text.get_rect(center=rect.center))

    def update(self):
        mouse_position = pygame.mouse.get_pos()
        for i in range(len(self.options)-1):
            rect = self.get_option_rect(i)
            if rect.collidepoint(mouse_position):
                self.active_option = i
        
        if pygame.mouse.get_pressed() != (0, 0, 0):
            if self.isActive and self.dropdown_rect.collidepoint(mouse_position):
                self.options[self.DEFAUTL_OPTION], self.options[self.active_option+1] =\
                     self.options[self.active_option+1], self.options[self.DEFAUTL_OPTION]
                self.active_option = -1
            self.isActive = self.rect.collidepoint(mouse_position)
        if not self.isActive:
            self.active_option = -1

# END OF MODULE #


# Global Variables
numBars = 0
delay   = 0
do_sorting = False
paused = False
timer_space_bar   = 0


# Input Boxes
algorithmBox = DropdownBox('Algorithm', (20, 100, 140, 50), baseFont)
sizeBox      = TextBox('Size', grey, (60, 200, 50, 50), '100')
delayBox     = SlideBox('Delay', grey, (30, 300, 112, 50))
playButton  = ButtonBox('images/playButton.png', (70, 400, 50, 50))
stopButton = ButtonBox('images/stopButton.png', (70, 400, 50, 50))


def updateWidgets(event):
    sizeBox.update(event)
    delayBox.update(event)
    algorithmBox.update()
    if do_sorting:
        stopButton.update()
    else:
        playButton.update()


def drawBars(array, redBar1, redBar2, blueBar1, blueBar2, greenRows = {}, **kwargs):
    '''Draw the bars and control their colors'''
    if numBars != 0:
        bar_width  = canvasSize[0] / numBars
        ceil_width = ceil(bar_width)

    for num in range(numBars):
        if   num in (redBar1, redBar2)  : color = red
        elif num in (blueBar1, blueBar2): color = blue
        elif num in greenRows           : color = green        
        else                            : color = grey
        pygame.draw.rect(screen, color, (sideMargin + num*bar_width, canvasSize[1]-array[num], ceil_width, array[num]))


def drawBottomMenu():
    '''Draw the menu below the bars'''
    algorithmBox.draw()
    sizeBox.draw()
    delayBox.draw()
    if do_sorting:
        stopButton.draw()
    else:
        playButton.draw()


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)


def drawInterface(array, redBar1, redBar2, blueBar1, blueBar2, **kwargs):
    '''Draw all the interface'''
    screen.fill(white)
    drawBars(array, redBar1, redBar2, blueBar1, blueBar2, **kwargs)
    
    if paused and (time()-timer_space_bar)<0.5:
        draw_rect_alpha(screen,(255, 255, 0, 127),[(850/2)+10, 150+10, 10, 50])
        draw_rect_alpha(screen,(255, 255, 0, 127),[(850/2)+40, 150+10, 10, 50])
        
    elif not paused and (time()-timer_space_bar)<0.5:
        x,y = (850/2),150
        draw_polygon_alpha(screen, (150, 255, 150, 127), ((x+10,y+10),(x+10,y+50+10),(x+50,y+25+10)))
        
    drawBottomMenu()
    pygame.display.update()
