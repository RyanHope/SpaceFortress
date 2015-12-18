# Some drawing helper functions

import math
import pygame

def blit_text (screen,font,text,x='center',y='center',color=(255,255,255),valign='top',halign='left',rect=None):
    if rect == None:
        rect = screen.get_rect()
    txt = font.render(text, True, color)
    tr = txt.get_rect()
    if x == 'center':
        tr.x = rect.centerx
    elif x < 0:
        tr.x = -x
    else:
        tr.x = x
    if y == 'center':
        tr.y = rect.centery
    elif y < 0:
        tr.y = -y
    else:
        tr.y = y
    if valign == 'bottom':
        tr.bottom = tr.y
    elif valign == 'center':
        tr.centery = tr.y
    if halign == 'right':
        tr.right = tr.x
    elif halign == 'center':
        tr.centerx = tr.x

    screen.blit(txt,tr)

def render_text(text,font,color):
    def render_region(start,end,bold,underline,invert,italics,color):
        font.set_underline(underline)
        font.set_bold(bold)
        font.set_italic(italics)
        if invert:
            surf = font.render(text[start:end],True,(0,0,0),color)
        else:
            surf = font.render(text[start:end],True,color)
        rect = surf.get_rect()
        return surf
        
    if len(text) == 0:
        return font.render(text,True,color)

    surfaces = []
    original_color = color
    start = 0
    bold = False
    underline = False
    invert = False
    italics = False
    while start < len(text):
        pos = text.find('^', start)
        if pos == -1 or pos == len(text)-1:
            pos = len(text)
            surf = render_region(start,pos,bold,underline,invert,italics,color)
        else:
            op = text[pos+1]
            if op == '^':
                pos += 1
            elif not op in '^b_iIc1234':
                pos += 2
            surf = render_region(start,pos,bold,underline,invert,italics,color)
            pos += 1
            if op == '^':
                pos -= 1
            elif op == 'b':
                bold = not bold
            elif op == '_':
                underline = not underline
            elif op == 'i':
                italics = not italics
            elif op == 'I':
                invert = not invert
            elif op == 'c':
                color = original_color
            elif op == '1':
                color = (0,0,255)
            elif op == '2':
                color = (255,0,0)
            elif op == '3':
                color = (255,255,0)
            elif op == '4':
                color = (0,255,0)
            else:
                pos -= 2

        surfaces.append(surf)
        start = pos+1
    font.set_bold(False)
    font.set_underline(False)
    font.set_italic(False)
    final = pygame.Surface((sum(map(lambda s: s.get_rect().width,surfaces)),
                            surfaces[0].get_rect().height))
    x = 0
    for s in surfaces:
        final.blit(s,(x,0))
        x += s.get_rect().width
    return final


class text():
    def __init__(self,text,font,color=(255,255,255),padding=0):
        self.surface = render_text(text,font,color)
        #self.surface = font.render(text,True,color)
        self.rect = self.surface.get_rect()
        self.padding = padding

    def draw(self,screen,y,center=True,x='center',xalign='center'):
        sr = screen.get_rect()
        rect = self.surface.get_rect()
        if center:
            rect.centery = y
        else:
            rect.y = y
        if x == 'center':
            rect.x = sr.centerx
        else:
            rect.x = x
        if xalign == 'center':
            rect.centerx = rect.x
        elif xalign == 'right':
            rect.right = rect.x
        elif xalign <> 'left':
            raise Exception("unknown value for xalign: %s" % xalign)
            
        screen.blit(self.surface,rect)
    
def fullscreen_message(screen,lines,continue_text,padding=10,offset=0):
    screen.fill((0,0,0))

    height = sum(map(lambda l:l.rect.height+l.padding*2,lines)) - lines[0].padding - lines[-1].padding + (len(lines)-1)*padding
    
    sr = screen.get_rect()
    y = (sr.height - height)/2 + offset - lines[0].padding
    for l in lines:
        y += l.padding
        l.draw(screen,y,False)
        y += l.padding+l.rect.height+padding

    if continue_text:
        continue_text.draw(screen,600)

def column(screen,lines,x,ystart,padding=0,align='left'):
    y = ystart - lines[0].padding
    for l in lines:
        y += l.padding
        l.draw(screen,y,False,x=x,xalign=align)
        y += l.rect.height + l.padding + padding

def message_from_file(screen,file):
    big_font = pygame.font.Font("fonts/freesansbold.ttf", 72)
    font = pygame.font.Font("fonts/freesansbold.ttf", 36)
    contfont = pygame.font.Font("fonts/freesansbold.ttf", 20)
    stream = open(file)
    txt = stream.readlines()
    stream.close()
    title_text = txt.pop(0).rstrip()
    continue_text = txt.pop().rstrip()
    if title_text:
        title = text(title_text,big_font,(255,255,0))
        lines = [title]
    else:
        lines = []
    for line in txt:
        lines.append(text(line.rstrip(),font))
    fullscreen_message(screen,lines,text(continue_text,contfont,(255,255,0)))

def draw_bubble_rect(screen,x,y,w,h,radius,color,filled=False):
    if filled:
        pygame.draw.rect(screen,color,(x+radius,y,w-radius*2,h))
        pygame.draw.rect(screen,color,(x,y+radius,radius,h-radius*2))
        pygame.draw.rect(screen,color,(x+w-radius,y+radius,radius,h-radius*2))
        # corners
        pygame.draw.circle(screen,color,(x+radius,y+radius),radius)
        pygame.draw.circle(screen,color,(x+radius,y+h-radius),radius)
        pygame.draw.circle(screen,color,(x+w-radius,y+h-radius),radius)
        pygame.draw.circle(screen,color,(x+w-radius,y+radius),radius)
    else:
        pygame.draw.line(screen,color,(x+radius,y),(x+w-radius,y))
        pygame.draw.line(screen,color,(x+radius-1,y+h),(x+w-radius,y+h))
        pygame.draw.line(screen,color,(x,y+radius-1),(x,y+h-radius))
        pygame.draw.line(screen,color,(x+w,y+radius),(x+w,y+h-radius))
        # corners
        pygame.draw.arc(screen,color,pygame.Rect(x,y,radius*2,radius*2),math.radians(90),math.radians(180))
        pygame.draw.arc(screen,color,pygame.Rect(x,y+h-radius*2,radius*2,radius*2),math.radians(180),math.radians(270))
        pygame.draw.arc(screen,color,pygame.Rect(x+w-radius*2,y+h-radius*2,radius*2,radius*2),math.radians(270),math.radians(360))
        pygame.draw.arc(screen,color,pygame.Rect(x+w-radius*2,y,radius*2,radius*2),math.radians(0),math.radians(90))

def draw_tag(screen,x,y,text,pressed,radius=12,font=None):
    if pressed:
        fc=(0,0,0)
    else:
        fc=(120,120,120)
    draw_bubble_rect(screen,x,y,60,30,radius,(120,120,120),pressed)
    blit_text(screen,font,text,x+30,y+15,color=fc,valign='center',halign='center')
