import os, platform
from config import Config
import config.editor

PYGAME_KEYS = ['1','2','3','4','5','6','7','8','9','0',
               'q','w','e','r','t','y','u','i','o','p',
               'a','s','d','f','g','h','j','k','l',
               'z','x','c','v','b','n','m','SPACE',
               'BACKSPACE','TAB','RETURN','COMMA','MINUS','PERIOD',
               'SLASH','SEMICOLON','QUOTE','LEFTBRACKET','RIGHTBRACKET',
               'BACKSLASH','EQUALS','BACKQUOTE','UP','DOWN','RIGHT','LEFT']

def get_config_home():
    _home = os.environ.get('HOME', '/')
    if platform.system() == 'Windows':
        config_home = os.path.join(os.environ['APPDATA'], 'SpaceFortress')
    elif platform.system() == 'Linux':
        config_home = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.join(_home, '.config')), 'spacefortress')
    elif platform.system() == 'Darwin':
        config_home = os.path.join(_home, 'Library', 'Application Support', 'SpaceFortress')
    else:
        config_home = os.path.join(_home, '.spacefortress')
    if not os.path.exists(config_home):
        os.makedirs(config_home)
    return config_home

def get_user_file():
    return os.path.join(get_config_home(),'config')

def get_config():
    
    cfg = Config()
    
    cfg.add_setting('General', 'player', True, alias='Player', options=['Human','Model'], type=config.editor.CT_COMBO, about='Will this game be played by a human or a cognitive model? Set to f to disable human control, enabling ACT-R')
    cfg.add_setting('General', 'fullscreen', False, alias='Fullscreen Mode', type=config.editor.CT_CHECKBOX, about='Run at full screen? Set to f to run in a window')
    cfg.add_setting('General', 'linewidth', 1, alias='Linewidth', about='Width of lines drawn on screen. Increase for a more "projector-friendly" game')
    cfg.add_setting('General', 'psf', False, alias='Classic Mode', type=config.editor.CT_CHECKBOX, about='Original PSF (SF4) settings? If t, *ALL* further values are ignored')
    cfg.add_setting('General', 'game_time', 30000, alias='Game Duration (ms)', about='Time in milliseconds for a game. NOTE! If you escape in the middle of a game, the log will have "short" prepended to the name')
    cfg.add_setting('General', 'games_per_session', 8, alias='Max # of Games', about='Number of games per "session"')
    cfg.add_setting('General', 'print_events', False, alias='Print Events', type=config.editor.CT_CHECKBOX, about='Print events to stdout')
    cfg.add_setting('General', 'sound', True, alias='Sound', type=config.editor.CT_CHECKBOX, about='Enable/disable sound')
    
    cfg.add_setting('Keybindings', 'thrust_key', 'w', alias='Turn Right', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'left_turn_key', 'a', alias='Turn Left', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'right_turn_key', 'd', alias='Thrust', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'fire_key', 'SPACE', alias='Fire', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'shots_key', 'k', alias='Shots Bonus', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'pnts_key', 'l', alias='Points Bonus', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'IFF_key', 'j', alias='Identify Friend or Foe', type=config.editor.CT_COMBO, options=PYGAME_KEYS)
    
    cfg.add_setting('Ship', 'ship_acceleration', 0.3, 'Ship acceleration factor')
    cfg.add_setting('Ship', 'ship_hit_points', 4, 'Number of hits ship takes before it is destroyed')
    cfg.add_setting('Ship', 'ship_max_vel', 6, "Ship's maximum velocity")
    cfg.add_setting('Ship', 'ship_orientation', 90, 'Initial ship orientation')
    cfg.add_setting('Ship', 'ship_pos_x', 245, 'Initial ship x position')
    cfg.add_setting('Ship', 'ship_pos_y', 315, 'Initial ship y position')
    cfg.add_setting('Ship', 'ship_radius', 3, 'ship collision radius.')
    cfg.add_setting('Ship', 'ship_turn_speed', 6, "Ship's turning speed")
    cfg.add_setting('Ship', 'ship_vel_x', 0, 'Initial ship velocity in x direction')
    cfg.add_setting('Ship', 'ship_vel_y', 0, 'Initial ship velocity in y direction.')
    
    cfg.add_setting('Missle', 'missile_max', 100, 'Maximum number of missiles possible')
    cfg.add_setting('Missle', 'missile_num', 100, 'Number of missiles at start of game')
    cfg.add_setting('Missle', 'missile_penalty', 3, 'Points lost when you fire a missile when none remain')
    cfg.add_setting('Missle', 'missile_radius', 5, 'Missile collision radius')
    cfg.add_setting('Missle', 'missile_speed', 20, 'Speed of missile fired from ship')
    
    cfg.add_setting('Hexagon', 'hex_pos_x', 355, 'Hex x position')
    cfg.add_setting('Hexagon', 'hex_pos_y', 315, 'Hex y position')
    cfg.add_setting('Hexagon', 'big_hex', 200, '"Radius" of large hexagon')
    cfg.add_setting('Hexagon', 'small_hex', 40, '"Radius" of small hexagon')
    cfg.add_setting('Hexagon', 'hex_shrink', False, type=config.editor.CT_CHECKBOX, about='Does the outer hex shrink over time?')
    cfg.add_setting('Hexagon', 'hex_shrink_radius', 150, 'If hex shrinks, to what minimum radius?')
    
    cfg.add_setting('Fortress', 'fortress_exists', True, type=config.editor.CT_CHECKBOX, about='Does the fortress exist?')
    cfg.add_setting('Fortress', 'fortress_lock_time', 1000, 'Time in milliseconds it takes the fortress to lock on to the ship before firing')
    cfg.add_setting('Fortress', 'fortress_pos_x', 355, 'Fortress x position')
    cfg.add_setting('Fortress', 'fortress_pos_y', 315, 'Fortress y position')
    cfg.add_setting('Fortress', 'fortress_radius', 18, 'Fortress collision radius')
    cfg.add_setting('Fortress', 'fortress_sector_size', 10, 'Fortress "sector size." Angle of tolerance before fortress turns to face ship. Bigger means fortress fires more often')
    cfg.add_setting('Fortress', 'hit_fortress_while_mine', False, type=config.editor.CT_CHECKBOX, about="Can the fortress be hit if there's a mine onscreen?")
    cfg.add_setting('Fortress', 'vlner_threshold', 10, 'Minimum vulnerability before you can destroy the fortress with a double shot. Note - keep in mind that the first shot of a "double shot" will increase VLNER')
    cfg.add_setting('Fortress', 'vlner_time', 250, 'Time in milliseconds that must pass between shots to avoid the fortress vulnerability to reset')

    cfg.add_setting('Shell', 'shell_speed', 6, 'Speed of shell fired from fortress')
    cfg.add_setting('Shell', 'shell_radius', 3, 'Shell collision radius')
    
    cfg.add_setting('Bonus', 'bonus_exists', True, type=config.editor.CT_CHECKBOX, about='Do bonuses exist?')
    cfg.add_setting('Bonus', 'bonus_system', "AX-CPT", type=config.editor.CT_LINEEDIT, about='Bonus system standard or AX-CPT?')
    cfg.add_setting('Bonus', 'randomize_bonus_pos', False, type=config.editor.CT_CHECKBOX, about='Randomize bonus position?')
    cfg.add_setting('Bonus', 'bonus_pos_x', 355, 'Bonus x position')
    cfg.add_setting('Bonus', 'bonus_pos_y', 390, 'Bonus y position')
    cfg.add_setting('Bonus', 'bonus_probability', 0.3, 'Probability that next symbol will be the bonus symbol')
    cfg.add_setting('Bonus', 'bonus_symbol', '$', type=config.editor.CT_LINEEDIT, n=1, about='Bonus symbol')
    cfg.add_setting('Bonus', 'non_bonus_symbols', '!&*%@', type=config.editor.CT_LINEEDIT, about="Non-bonus symbols. Defaults are # & * % @. Don't use '-', because that's used in the log file to represent that there's no symbol present")
    cfg.add_setting('Bonus', 'symbol_down_time', 833, '"Blank time" between symbol appearances in milliseconds**. (Seems like a weird number, but it\'s to sync with the frame-based original)')
    cfg.add_setting('Bonus', 'symbol_up_time', 2500, 'Time in milliseconds each symbol is visible**')

    cfg.add_setting('Mine', 'mine_exists', True, type=config.editor.CT_CHECKBOX, about='Do mines exists?')
    cfg.add_setting('Mine', 'mine_mode', 'standard', type=config.editor.CT_LINEEDIT, about='Set mine behavior to standard or MOT')
    cfg.add_setting('Mine', 'num_foes', 3, 'Number of foe mines')
    cfg.add_setting('Mine', 'mine_radius', 20, 'Mine collision radius')
    cfg.add_setting('Mine', 'mine_speed', 3, 'Mine speed')
    cfg.add_setting('Mine', 'minimum_spawn_distance', 200, 'Minimum spawn distance. Mine will never appear closer than this distance to the ship')
    cfg.add_setting('Mine', 'maximum_spawn_distance', 700, 'Maximum spawn distance. Mine will never appear farther away than this distance to the ship')
    cfg.add_setting('Mine', 'intrvl_min', 250, 'Minimum time between double-clicks to identify foe mine')
    cfg.add_setting('Mine', 'intrvl_max', 400, 'Maximum time between double-clicks to identify foe mine')
    cfg.add_setting('Mine', 'mine_probability', 0.3, 'Probability that next mine will be a foe')
    cfg.add_setting('Mine', 'mine_timeout', 10000, 'Time in milliseconds for a mine to timeout and disappear')
    cfg.add_setting('Mine', 'mine_spawn', 5000, 'Time in milliseconds for a mine to spawn')
    cfg.add_setting('Mine', 'fortress_resets_mine', True, type=config.editor.CT_CHECKBOX, about='Does destroying the fortress reset the mine timer?')
    
    cfg.add_setting('MOT', 'MOT_count', 5, 'Number of mines')
    cfg.add_setting('MOT', 'MOT_identification_time', 5000, 'Time to allow for MOT identification')
    cfg.add_setting('MOT', 'MOT_identification_type', 'shots', type=config.editor.CT_LINEEDIT, about='MOT identification through shots or ship? (i.e., fly into the mine)')
    cfg.add_setting('MOT', 'MOT_max_deflection', 15, 'Angle in degrees for the maximum amount a mine can change direction')
    cfg.add_setting('MOT', 'MOT_move_time', 5000, 'Time to move mines with IFF info hidden')
    cfg.add_setting('MOT', 'MOT_movement_style', 'bounce', type=config.editor.CT_LINEEDIT, about='Do MOT mines bounce off walls or warp around edges?')
    cfg.add_setting('MOT', 'MOT_off_time', 5000, 'Time in between MOT "cycles"')
    cfg.add_setting('MOT', 'MOT_onset_time', 3000, 'Time to display "frozen" MOT mines on onset')
    cfg.add_setting('MOT', 'MOT_switch_time', 1000, 'Time in between direction changes while MOT mines are moving')

    cfg.add_setting('Score', 'new_scoring', False, type=config.editor.CT_CHECKBOX, about='Use the new scoring system for Flight, Fortress, and Mines? (instead of PNTS, CNTRL, VLCTY and SPEED)')
    cfg.add_setting('Score', 'new_scoring_pos', True, type=config.editor.CT_CHECKBOX, about='New scoring position is a more "eye-tracker friendly" format that places the scores around the perimeter of the gameworld, rather than just all along the bottom. Set to f for default positioning')
    cfg.add_setting('Score', 'PNTS_pos', 1, 'Set positions for the display elements. 1 = leftmost for original scoring position for new scoring position, 1 = left item on top row, proceeds clockwise PNTS position(or Flight, for new)')
    cfg.add_setting('Score', 'CNTRL_pos', 2, 'CNTRL position(or Fortress, for new)')
    cfg.add_setting('Score', 'VLCTY_pos', 3, 'VLCTY position(or Mines, for new)')
    cfg.add_setting('Score', 'VLNER_pos', 4, 'VLNER position')
    cfg.add_setting('Score', 'IFF_pos', 5, 'IFF')
    cfg.add_setting('Score', 'INTRVL_pos', 6, 'INTRVL')
    cfg.add_setting('Score', 'SPEED_pos', 7, 'SPEED position(or Bonus, for new)')
    cfg.add_setting('Score', 'SHOTS_pos', 8, 'SHOTS')
    cfg.add_setting('Score', 'update_timer', 1000, 'How often (in milliseconds) the VLCTY and CNTRL scores update (or Flight, for new)')
    cfg.add_setting('Score', 'speed_threshold', 4, 'Speed at which you\'re considered to be going "too fast", resulting in a VLCTY point penalty (or Flight, for new)')
    cfg.add_setting('Score', 'VLCTY_increment', 7, 'VLCTY bonus/penalty for going either slow enough or too fast (or Flight, for new)')
    cfg.add_setting('Score', 'CNTRL_increment', 6, 'Number of points added to CNTRL score for staying with the hexagons (or Flight, For new). Note that half this number is added when outside the hexagons, so even is recommended.')
    cfg.add_setting('Score', 'small_hex_penalty', 5, 'Penalty for colliding with the small hexagon.')
    cfg.add_setting('Score', 'warp_penalty', 35, 'Penalty for warping around the screen')
    cfg.add_setting('Score', 'mine_timeout_penalty', 50, 'Penalty for mine timing out')
    cfg.add_setting('Score', 'mine_hit_penalty', 50, 'Penalty for mine hitting ship')
    cfg.add_setting('Score', 'shell_hit_penalty', 50, 'Penalty for shell hitting ship')
    cfg.add_setting('Score', 'ship_death_penalty', 100, 'Penalty for ship destruction')
    cfg.add_setting('Score', 'energize_friend', 20, 'Points for "energizing" a friendly mine')
    cfg.add_setting('Score', 'destroy_foe', 30, 'Points for destroying a "foe" mine.')
    cfg.add_setting('Score', 'destroy_fortress', 100, 'Points for destroying the fortress')
    cfg.add_setting('Score', 'bonus_points', 100, 'Points added for selecting points bonus')
    cfg.add_setting('Score', 'bonus_missiles', 50, 'Missiles added for selecting missile bonus')
    
    return cfg