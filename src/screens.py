from __future__ import division

def show_total_score(game,pause,continue_text,total_bonus):
    """shows score for last game and waits to continue"""
    game.clear_events() #clear event list? Otherwise it skips
    total = game.get_total_score()
    if game.has_display():
        game.screen.fill((0, 0, 0))
        if game.session_name == None:
            title = "Game %d of %s"%(game.game_number, game.games_in_session)
        else:
            title = "Session %s, Game %d of %s"%(game.session_name, game.game_number, game.games_in_session)
        drawing.blit_text(game.screen,game.f24,title,y=100,valign='top',halign='center')
        drawing.blit_text(game.screen,game.f36,"You scored %d points."%total,y=320,valign='top',halign='center')
        drawing.blit_text(game.screen,game.f36,"You earned a bonus of $%s this game."%game.format_money(),y=370,valign='top',halign='center')
        drawing.blit_text(game.screen,game.f36,"So far you have earned a total of $%s."%game.format_money(total_bonus+game.money),y=420,valign='top',halign='center')
        if continue_text and not game.image:
            continue_text.draw(game.screen,700,False)
        pygame.display.flip()
    score = {'total': total, 'bonus': game.money, 'total-bonus': game.money+total_bonus, 'raw-pnts': game.score.raw_pnts}
    game.log.slog('show-total-score', score)
    score['screen-type'] = 'total-score'
    if not game.image and pause:
        game.set_objects(score)
        game.delay(1000)
    game.set_objects(score)
    game.delay_and_log(int(game.config['score_time']))
    game.log.slog('show-total-score-end')

def show_score(game,pause, continue_text, total_bonus):
    """shows score for last game and waits to continue"""
    game.clear_events() #clear event list? Otherwise it skips
    total = 0
    score = {}
    if game.has_display():
        game.screen.fill((0, 0, 0))
        if game.session_name == None:
            title = "Game %d of %s"%(game.game_number, game.games_in_session)
        else:
            title = "Session %s, Game %d of %s"%(game.session_name, game.game_number, game.games_in_session)
        drawing.blit_text(game.screen,game.f24,title,y=100,valign='top',halign='center')
        col1 = []
        col2 = []
        if 'pnts' in game.config['active_scores']:
            col1.append(drawing.text("Points",game.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%game.score.pnts,game.f24))
            total += game.score.pnts
            score['pnts'] = game.score.pnts
        if 'cntrl' in game.config['active_scores']:
            col1.append(drawing.text("CNTRL score:",game.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%game.score.cntrl,game.f24))
            total += game.score.cntrl
            score['cntrl'] = game.score.cntrl
        if 'vlcty' in game.config['active_scores']:
            col1.append(drawing.text("VLCTY score:",game.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%game.score.vlcty,game.f24))
            total += game.score.vlcty
            score['vlcty'] = game.score.vlcty
        if 'speed' in game.config['active_scores']:
            col1.append(drawing.text("SPEED score:",game.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%game.score.speed,game.f24))
            total += game.score.speed
            score['speed'] = game.score.speed
        if 'crew' in game.config['active_scores']:
            crew_score = game.score.crew_members * int(game.config['crew_member_points'])
            col1.append(drawing.text("Crew Members  x %d"%game.score.crew_members,game.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%crew_score,game.f24))
            total += crew_score
            score['crew'] = crew_score
        score['total'] = total
        col1.append(drawing.text("Total score for this game",game.f24,(255, 255,0),padding=20))
        col2.append(drawing.text("%d"%total,game.f24,padding=20))
        pad = 40
        h = pad+col1[0].rect.h
        y = 200+h*(len(col1)-1)
        drawing.column(game.screen,col1,260,200,align='left',padding=pad)
        drawing.column(game.screen,col2,700,200,align='right',padding=pad)
        pygame.draw.line(game.screen, (255, 255, 255), (210, y), (810, y))
        pygame.draw.rect(game.screen, (255, 255, 255), (210, 200-pad, 601, h*len(col1)+pad), 1)
        col1 = []
        col2 = []
        col1.append(drawing.text("Bonus earned this game", game.f24, (255, 255, 0)))
        col2.append(drawing.text("$%s"%game.format_money(), game.f24))
        col1.append(drawing.text("Total bonus earned so far", game.f24, (255, 255, 0)))
        col2.append(drawing.text("$%s"%game.format_money(total_bonus+game.money), game.f24))
        score['bonus'] = game.money
        score['total-bonus'] = total_bonus+game.money
        pad = 20
        h = pad+col1[0].rect.h
        drawing.column(game.screen,col1,260,500,align='left',padding=pad)
        drawing.column(game.screen,col2,700,500,align='right',padding=pad)
        pygame.draw.rect(game.screen, (255, 255, 255), (210, 500-pad, 601, h*len(col1)+pad), 1)

        if continue_text and not game.image:
            continue_text.draw(game.screen,700,False)
        pygame.display.flip()
    game.log.slog('show-score', score)
    score['screen-type'] = 'score'
    if not game.image and pause:
        game.set_objects(score)
        game.delay(1000)
    game.set_objects(score)
    game.delay_and_log(int(game.config['score_time']))
    game.log.slog('show-score-end')

def display_bonus(game,bonus):
    if game.has_display():
        drawing.fullscreen_message(game.screen,[drawing.text("You earned a $%s bonus!"%game.format_money(bonus),game.f36,(255,255,0))],
                                   drawing.text("",game.f24))
        pygame.display.flip()
    game.clear_events()
    while True:
        if game.model:
            game.set_objects({'screen-type': 'bonus', 'bonus': bonus})
            events = game.get_event()
        else:
            events = [pygame.event.wait()]
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit()

def display_screen(game,screen,continue_text,delay=False,total_bonus=None):
    if screen == 'progress':
        game.display_progress(continue_text)
    elif screen == 'wait-for-caret':
        game.display_wait()
    elif screen == 'fixation':
        game.display_fixation()
    elif screen == 'instructions':
        game.display_instructions(continue_text)
    elif screen == 'foe-mines':
        game.display_foe_mines(continue_text)
    elif screen == 'fmri-task':
        game.display_fmri_task(continue_text)
    elif screen == 'incremental-task':
        game.display_inc_task(continue_text)
    elif screen == 'basic-task':
        game.display_basic_task(continue_text)
    elif screen == 'transfer-task':
        game.display_transfer_task(continue_text)
    elif screen == 'score':
        game.show_score(delay, continue_text, total_bonus)
    elif screen == 'total-score':
        game.show_total_score(delay,continue_text, total_bonus)
    elif screen == 'fixation':
        game.display_fixation()
    elif screen != 'none':
        game.display_screen_from_file(screen)


def pre_game_continue_text(game,last):
    if last:
        return game.continue_text("begin")
    else:
        return game.continue_text("continue")

def display_pre_game_screens(game):
    for n in xrange(len(game.pre_game_screens)):
        screen = game.pre_game_screens[n]
        last = n == len(game.pre_game_screens)-1
        continue_text = game.pre_game_continue_text(last)
        game.display_screen(screen,continue_text)

def post_game_continue_text(game,last,end):
    if game.image:
        return None
    elif end:
        if game.has_display():
            return drawing.text("You're done! Press any key to exit",game.f24,(0,255,0))
    elif last:
        return game.continue_text('continue to next game')
    else:
        return game.continue_text('continue')

def display_post_game_screens(game, total_bonus):
    end = game.game_number == game.games_in_session
    for n in xrange(len(game.post_game_screens)):
        screen = game.post_game_screens[n]
        delay = n == 0
        last = n == len(game.post_game_screens)-1
        continue_text = game.post_game_continue_text(last,end)
        game.display_screen(screen,continue_text,delay,total_bonus)

def display_block_start_screens(game):
    for screen in game.block_start_screens:
        game.display_screen(screen,game.continue_text('continue'))

def display_block_end_screens(game):
    for screen in game.block_end_screens:
        game.display_screen(screen,game.continue_text('continue'))

def display_session_screens(game):
    for screen in game.session_start_screens:
        game.display_screen(screen,game.continue_text('continue'))

def pre_game(game):
    if not game.simulate:
        # pre game screens
        if game.game_number == 1:
            game.display_session_screens()
        if game.games_per_block > 0 and game.game_number % game.games_per_block == 1:
            display_block_start_screens(game)
            game.log.slog('block-start',{'block':game.game_number//game.games_per_block+1})
        display_pre_game_screens(game)

def post_game(game, total_bonus):
    '''Call this once the game is done.'''
    if game.sounds_enabled:
        pygame.mixer.stop()
    # display screens
    if not game.simulate:
        display_post_game_screens(game, total_bonus)
        if game.games_per_block > 0 and game.game_number % game.games_per_block == 0:
            game.log.slog('block-end',{'block':game.game_number//game.games_per_block})
            game.display_block_end_screens()
