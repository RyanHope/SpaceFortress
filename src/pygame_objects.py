from __future__ import division
import math
import pygame
import fortress
import ship
import hexagon
import missile
import shell

def rotate(ship, x, y):
    x1 = x * ship.cosphi - y * ship.sinphi + ship.position.x
    y1 = -1*(x * ship.sinphi + y * ship.cosphi) + ship.position.y
    return (x1, y1)

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

def draw_fortress(fortress, worldsurf):
    """draws fortress to worldsurf"""
    #photoshop measurement shows 36 pixels long, and two wings 18 from center and 18 long
    #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
    fortress.sinphi = math.sin(math.radians((fortress.orientation) % 360))
    fortress.cosphi = math.cos(math.radians((fortress.orientation) % 360))
    x1 = fortress.position.x
    y1 = fortress.position.y
    x2 = 36 * fortress.cosphi + fortress.position.x
    y2 = -(36 * fortress.sinphi) + fortress.position.y
    #x3, y3 = 18, -18
    x3 = 18 * fortress.cosphi - -18 * fortress.sinphi + fortress.position.x
    y3 = -(-18 * fortress.cosphi + 18 * fortress.sinphi) + fortress.position.y
    #x4, y4 = 0, -18
    x4 = -(-18 * fortress.sinphi) + fortress.position.x
    y4 = -(-18 * fortress.cosphi) + fortress.position.y
    #x5, y5 = 18, 18
    x5 = 18 * fortress.cosphi - 18 * fortress.sinphi + fortress.position.x
    y5 = -(18 * fortress.cosphi + 18 * fortress.sinphi) + fortress.position.y
    #x6, y6 = 0, 18
    x6 = - (18 * fortress.sinphi) + fortress.position.x
    y6 = -(18 * fortress.cosphi) + fortress.position.y

    pygame.draw.line(worldsurf, (255,255,0), (x1,y1), (x2, y2))
    pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x5, y5))
    pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x4, y4))
    pygame.draw.line(worldsurf, (255,255,0), (x5,y5), (x6, y6))

def draw_ship(ship, worldsurf):
    """draw ship to worldsurf"""
    #ship's nose is x+18 to x-18, wings are 18 back and 18 to the side of 0,0
    #NewX = (OldX*Cos(Theta)) - (OldY*Sin(Theta))
    #NewY = -((OldY*Cos(Theta)) + (OldX*Sin(Theta))) - taking inverse because +y is down
    #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
    if ship.auto_thrust_debug:
        ship.draw_autothrust(worldsurf)

    ship.sinphi = math.sin(math.radians((ship.orientation) % 360))
    ship.cosphi = math.cos(math.radians((ship.orientation) % 360))
    #old x1 = -18
    x1 = -18 * ship.cosphi + ship.position.x
    y1 = -(-18 * ship.sinphi) + ship.position.y
    #old x2 = + 18
    x2 = 18 * ship.cosphi + ship.position.x
    y2 = -(18 * ship.sinphi) + ship.position.y
    #x3 will be center point
    x3 = ship.position.x
    y3 = ship.position.y
    #x4, y4 = -18, 18
    x4 = -18 * ship.cosphi - 18 * ship.sinphi + ship.position.x
    y4 = -((18 * ship.cosphi) + (-18 * ship.sinphi)) + ship.position.y
    #x5, y5 = -18, -18
    x5 = -18 * ship.cosphi - -18 * ship.sinphi + ship.position.x
    y5 = -((-18 * ship.cosphi) + (-18 * ship.sinphi)) + ship.position.y

    pygame.draw.line(worldsurf, (255,255,0), (x1,y1), (x2,y2))
    pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x4,y4))
    pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x5,y5))

    if ship.thrust_flag:
        thrust = [[[-20,0], [-29,0]],
                  [[-20,0], [-29,5]],
                  [[-20,0], [-29,-5]]]
        # if random.uniform(0,100)<75:
        #     c = (255,0,0)
        # else:
        #     c = (255,200,0)
        c = (255,0,0)
        for l in thrust:
            pygame.draw.line(worldsurf, c,
                             rotate(ship, l[0][0], l[0][1]),
                             rotate(ship, l[1][0], l[1][1]))

def old_draw_autothrust (ship, worldsurf):
    tmp = ship.detect_thrustable_conditions()
    if len(tmp)>2:
        (thrust, a, t, top, bot, tangent_a, vel_a) = tmp


        if a:
            ac = (0,255,0)
        else:
            ac = (255,0,0)
        if t:
            tc = (255,0,0)
        else:
            tc = (0,255,0)
        pygame.draw.line(worldsurf, ac, (ship.position.x, ship.position.y), (top.x, top.y))
        pygame.draw.line(worldsurf, ac, (ship.position.x, ship.position.y), (bot.x, bot.y))
        tx = math.cos(math.radians(tangent_a))*50+ship.position.x
        ty = math.sin(math.radians(tangent_a))*50+ship.position.y
        pygame.draw.line(worldsurf, tc, (ship.position.x, ship.position.y), (tx, ty))
        vx = math.cos(math.radians(vel_a))*50+ship.position.x
        vy = math.sin(math.radians(vel_a))*50+ship.position.y
        pygame.draw.line(worldsurf, (255,255,255), (ship.position.x, ship.position.y), (vx, vy))

def draw_autothrust (ship, worldsurf):
    ship.detect_thrustable_conditions()

    if ship.both:
        blit_text(worldsurf, ship.app.f, "both", 100, 50)
    if ship.between:
        blit_text(worldsurf, ship.app.f, "between", 150, 50)

    if ship.d_after < ship.d_before:
        blit_text(worldsurf, ship.app.f, "closer", 240, 50)

    pygame.draw.circle(worldsurf, (255,0,0), (ship.app.fortress.position.x, ship.app.fortress.position.y), ship.auto_thrust_min_radius, 1)
    pygame.draw.circle(worldsurf, (255,255,0), (ship.app.fortress.position.x, ship.app.fortress.position.y), ship.auto_thrust_max_radius, 1)
    min_h = math.sqrt(ship.distance_to_fortress()**2+ship.auto_thrust_min_radius**2)
    max_h = math.sqrt(ship.distance_to_fortress()**2+ship.auto_thrust_max_radius**2)
    pygame.draw.line(worldsurf, (255,0,0), (ship.position.x, ship.position.y),
                     (ship.position.x + math.cos(math.radians(ship.min_angle))*min_h,
                      ship.position.y + math.sin(math.radians(ship.min_angle))*min_h))
    # pygame.draw.line(worldsurf, (255,0,0), (ship.app.fortress.position.x, ship.app.fortress.position.y),
    #                  (ship.position.x + math.cos(math.radians(ship.min_angle))*min_h,
    #                   ship.position.y - math.sin(math.radians(ship.min_angle))*min_h))

    pygame.draw.line(worldsurf, (255,255,0), (ship.position.x, ship.position.y),
                     (ship.position.x + math.cos(math.radians(ship.max_angle))*max_h,
                      ship.position.y + math.sin(math.radians(ship.max_angle))*max_h))
    pygame.draw.line(worldsurf, (255,255,0), (ship.position.x, ship.position.y),
                     (ship.position.x + math.cos(math.radians(ship.vel_angle))*50,
                      ship.position.y + math.sin(math.radians(ship.vel_angle))*50))
    pygame.draw.line(worldsurf, (255,255,255), (ship.position.x, ship.position.y),
                     (ship.position.x + math.cos(math.radians(ship.after_thrust_angle))*50,
                      ship.position.y + math.sin(math.radians(ship.after_thrust_angle))*50))

    # pygame.draw.line(worldsurf, (0,0,255), (ship.position.x, ship.position.y),
    #                  (ship.position.x + math.cos(math.radians(0))*50,
    #                   ship.position.y + math.sin(math.radians(0))*50))

    # pygame.draw.line(worldsurf, (100,100,255), (ship.position.x, ship.position.y),
    #                  (ship.position.x + math.cos(math.radians(270))*50,
    #                   ship.position.y + math.sin(math.radians(270))*50))

def draw_shell(shell, worldsurf):
    """draws shell to worldsurf"""
    #photoshop measurement shows, from center, 16 points ahead, 8 points behind, and 6 points to either side
    #NewX = (OldX*Cos(Theta)) - (OldY*Sin(Theta))
    #NewY = -((OldY*Cos(Theta)) + (OldX*Sin(Theta))) flip 'cause +y is down
    #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
    shell.sinphi = math.sin(math.radians((shell.orientation) % 360))
    shell.cosphi = math.cos(math.radians((shell.orientation) % 360))

    x1 = -8 * shell.cosphi + shell.position.x
    y1 = -(-8 * shell.sinphi) + shell.position.y
    x2 = -(-6 * shell.sinphi) + shell.position.x
    y2 = -(-6 * shell.cosphi) + shell.position.y
    x3 = 16 * shell.cosphi + shell.position.x
    y3 = -(16 * shell.sinphi) + shell.position.y
    x4 = -(6 * shell.sinphi) + shell.position.x
    y4 = -(6 * shell.cosphi) + shell.position.y

    pygame.draw.line(worldsurf, (255,0,0), (x1, y1), (x2, y2))
    pygame.draw.line(worldsurf, (255,0,0), (x2, y2), (x3, y3))
    pygame.draw.line(worldsurf, (255,0,0), (x3, y3), (x4, y4))
    pygame.draw.line(worldsurf, (255,0,0), (x4, y4), (x1, y1))


def draw_missile(missile, worldsurf):
    """draws ship's missile to worldsurf"""
    color = (255,255,255)
    #photoshop measurement shows 25 pixels long, and two wings at 45 degrees to the left and right, 7 pixels long
    #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
    missile.sinphi = math.sin(math.radians((missile.orientation) % 360))
    missile.cosphi = math.cos(math.radians((missile.orientation) % 360))
    missile.x1 = missile.position.x
    missile.y1 = missile.position.y
    #x2 is -25
    missile.x2 = -25 * missile.cosphi + missile.position.x
    missile.y2 = -(-25 * missile.sinphi) + missile.position.y
    #x3, y3 is -5, +5
    missile.x3 = (-5 * missile.cosphi) - (5 * missile.sinphi) + missile.position.x
    missile.y3 = -((5 * missile.cosphi) + (-5 * missile.sinphi)) + missile.position.y
    #x4, y4 is -5, -5
    missile.x4 = (-5 * missile.cosphi) - (-5 * missile.sinphi) + missile.position.x
    missile.y4 = -((-5 * missile.cosphi) + (-5 * missile.sinphi)) + missile.position.y

    pygame.draw.line(worldsurf, color, (missile.x1, missile.y1), (missile.x2, missile.y2))
    pygame.draw.line(worldsurf, color, (missile.x1, missile.y1), (missile.x3, missile.y3))
    pygame.draw.line(worldsurf, color, (missile.x1, missile.y1), (missile.x4, missile.y4))

def draw_hex(hex, worldsurf):
    """draws hex"""
    for i in range(6):
        pygame.draw.line(worldsurf, (0,255,0), (hex.points_x[i], hex.points_y[i]), (hex.points_x[(i + 1) % 6], hex.points_y[(i + 1) % 6]))

def draw_bonus(bonus, worldsurf):
        """draws bonus symbol to screen"""
        surf = bonus.app.f28.render(bonus.text, 1, (255, 255, 0))
        rect = surf.get_rect()
        #worldsurf.blit(surf, pygame.Rect(bonus.x, bonus.y, 150, 30))
        worldsurf.blit(surf, (bonus.x-rect.width//2, bonus.y))

def draw_mine(mine, worldsurf):
    """draws mine to worldsurf"""
    pygame.draw.line(worldsurf, (0,255,255), (mine.position.x - 16, mine.position.y), (mine.position.x, mine.position.y - 24))
    pygame.draw.line(worldsurf, (0,255,255), (mine.position.x, mine.position.y - 24), (mine.position.x + 16, mine.position.y))
    pygame.draw.line(worldsurf, (0,255,255), (mine.position.x + 16, mine.position.y), (mine.position.x, mine.position.y + 24))
    pygame.draw.line(worldsurf, (0,255,255), (mine.position.x, mine.position.y + 24), (mine.position.x - 16, mine.position.y))


def draw_score(score, scoresurf):
    if len(score.label_surfs) == 0:
        # build label cache
        x = (score.app.WORLD_WIDTH - score.dashboard_width)/2
        for l in score.labels:
            surf = score.app.f.render(l.upper(),0, (0,255,0))
            rect = surf.get_rect()
            rect.centery = 16
            rect.centerx = x + score.label_width/2
            score.label_surfs.append(surf)
            score.label_rects.append(rect)
            x += score.label_width
    # draw
    start = (score.app.WORLD_WIDTH - score.dashboard_width)/2
    end = start + score.dashboard_width - 1
    pygame.draw.rect(scoresurf, (0,255,0), (start, 0, score.dashboard_width, 63), 1) #bottom box to hold scores
    pygame.draw.line(scoresurf, (0,255,0), (start,32), (end,32)) #divides bottom box horizontally into two rows
    #the following lines divides the bottom box vertically into columns
    x = start + score.label_width
    h = 64
    for i in range(len(score.labels)-1):
        pygame.draw.line(scoresurf, (0,255,0), (x, 0), (x, h))
        x += score.label_width
    #score labels
    x = start
    for i in range(len(score.labels)):
        scoresurf.blit(score.label_surfs[i], score.label_rects[i])
        surf = score.app.f.render(score.get_value(score.labels[i]), 0, (255,255,0))
        rect = surf.get_rect()
        rect.centery = 48
        rect.centerx = x + score.label_width/2
        scoresurf.blit(surf, rect)
        x += score.label_width
