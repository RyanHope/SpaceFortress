# read input from a pygame screen
from __future__ import division
import math
import sys
import pygame
import string

def read_string(prompt, screen, font, only_nums=False):
    answer = ""
    pygame.event.clear()
    r = screen.get_rect()
    question = font.render(prompt, True, (255,255,0))
    qrect = question.get_rect()
    qrect.centerx = r.width//2
    qrect.centery = r.height//2
    while True:
        answer_surf = font.render(answer, True, (255,255,255))
        arect = answer_surf.get_rect()
        arect.centerx = r.width//2
        arect.centery = r.height//2 + 100
        screen.fill((0,0,0))
        screen.blit (question, qrect)
        screen.blit(answer_surf, arect)
        pygame.display.flip()
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_BACKSPACE:
                answer = answer[:-1]
            elif event.key == pygame.K_RETURN and len(answer) > 0:
                return answer
            elif (only_nums and pygame.K_0 <= event.key <= pygame.K_9) or (not only_nums and pygame.K_0 <= event.key <= pygame.K_z):
                answer += "%c" % event.key

def read_int (prompt, screen, font):
    return int(read_string (prompt, screen, font, only_nums=True))

def read_from_list (prompt, screen, font, options,current=0):
    """Interactively select an item from a list. Return the index of the item."""
    options = map(lambda o: string.capwords(o.replace('_',' ')),options)
    pygame.event.clear()
    srect = screen.get_rect()
    question = font.render(prompt, True, (255,255,0))
    qrect = question.get_rect()
    qrect.centerx = srect.width//2
    qrect.centery = srect.height//2
    height = sum(map (lambda o: font.size(o)[1]+10,options))
    if qrect.bottom + height > srect.height:
        qrect.bottom = srect.bottom - height - 30
    while True:
        render = []
        for o in xrange(len(options)):
            render.append(font.render(options[o],True,(0,0,0) if o==current else (255,255,255)))
            
        screen.fill((0,0,0))
        screen.blit (question, qrect)
        x = qrect.x + 10
        y = qrect.bottom+20
        for r in xrange(len(render)):
            rect = render[r].get_rect()
            rect.x = x
            rect.y = y
            y = rect.bottom + 10
            if current==r:
                pygame.draw.rect(screen,(255,255,255),rect)
            screen.blit(render[r], rect)
        pygame.display.flip()
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_UP:
                current -= 1
                if current<0:
                    current = len(options)-1
            elif event.key == pygame.K_DOWN:
                current += 1
                if current>=len(options):
                    current = 0
            elif event.key == pygame.K_RETURN:
                return current

def choose_from_list (prompt, screen, font, options,current=0):
    """Using the mouse, interactively select an item from a list. Return the index of the item."""
    pygame.event.clear()
    srect = screen.get_rect()
    question = font.render(prompt, True, (255,255,0))
    qrect = question.get_rect()
    width = font.size(max(options, key=lambda o: font.size(o)[0] + 10))[0] + 20
    height = font.size(max(options, key=lambda o: font.size(o)[1]+10))[1] + 20
    cols = int(math.sqrt(len(options))) # min(5,int(srect.height * 2 / 3) // height)
    rows = int(math.ceil(len(options) / cols))
    orect = pygame.Rect(0, 0, cols * width, rows * height)
    orect.centerx = srect.centerx
    orect.centery = srect.centery
    qrect.centerx = orect.centerx
    qrect.bottom = orect.y - 10
    while True:
        screen.fill((0,0,0))
        screen.blit (question, qrect)
        for col in xrange(cols):
            for row in xrange(rows):
                i = row*cols+col
                if i >= len(options):
                    break
                area = pygame.Rect(orect.x + col * width, orect.y + row * height, width+1, height+1)
                r = font.render(options[i],True,(0,0,0) if i == current else (255,255,255))
                rect = r.get_rect()
                rect.centerx = area.centerx
                rect.centery = area.centery
                pygame.draw.rect(screen,(0,255,0),area, 1)
                area.x += 3
                area.y += 3
                area.width -= 6
                area.height -= 6
                if current == i:
                    pygame.draw.rect(screen,(255,255,255), area, 0)
                screen.blit(r, rect)
        pygame.display.flip()
        event = pygame.event.wait()
        if event.type == pygame.MOUSEMOTION:
            if orect.collidepoint(event.pos):
                col = (event.pos[0] - orect.x) // width
                row = (event.pos[1] - orect.y) // height
                current = row * cols + col
                if current > len(options):
                    current = None
        elif event.type == pygame.MOUSEBUTTONUP:
            if orect.collidepoint(event.pos):
                return current
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if current-cols >= 0:
                    current -= cols
            elif event.key == pygame.K_DOWN:
                if current+cols < len(options):
                    current += cols
            elif event.key == pygame.K_RIGHT:
                if current%cols < (current+1)%cols and current+1 < len(options):
                    current += 1
            elif event.key == pygame.K_LEFT:
                if current%cols > (current-1)%cols and current-1 >= 0:
                    current -= 1
            elif event.key == pygame.K_RETURN:
                return current
            if event.key == pygame.K_ESCAPE:
                return None
        elif event.type == pygame.QUIT:
            sys.exit(0)
