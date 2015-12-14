#Class for bonus object, which displays symbols below the fortress
import object as obj
import random
from timer import Timer

BONUS_POINTS=0
BONUS_SHOTS=1

class Bonus(object):
    """bonus symbol"""
    def __init__(self,app,config):
        super(Bonus, self).__init__()
        self.up_time = int(config["symbol_up_time"])
        self.down_time = int(config["symbol_down_time"])
        self.x = 355
        self.y = 390
        self.visible = False
        if config.has_key("bonus_symbols"):
            self.symbols = map(lambda s:unicode(s,'utf-8'),config["bonus_symbols"])
            self.match_any_symbol = True
        else:
            self.symbols = config["non_bonus_symbols"]
            self.bonus_symbol = config["bonus_symbol"]
            self.match_any_symbol = False
        if config.has_key('bonus_types'): # JPB120327
            self.bonus_types = config['bonus_types']
            if not isinstance(self.bonus_types,list):
                self.bonus_types = [self.bonus_types]
            #self.bonus_types = map(int,self.bonus_types)
        else:
            self.bonus_types = None
        if config.has_key('bonus_symbols_game'): # JPB120327
            self.bonus_symbols_game = config['bonus_symbols_game']
            if not isinstance(self.bonus_symbols_game,list):
                self.bonus_symbols_game = [self.bonus_symbols_game]
            #self.bonus_types = map(int,self.bonus_types)
        else:
            self.bonus_symbols_game = None
        self.text = ''
        self.prior_symbols = []
        self.nback = int(config["bonus_nback"])
        self.flag = True
        self.disable_firing = int(config["bonus_disable_firing"]) == 1
        self.probability = float(config["bonus_probability"])
        self.auto_select = int(config["bonus_select"]) == 1
	self.exists = int(config["bonus_enable"]) == 1
        self.app = app
        self.timer = Timer()

    def get_nback_symbol(self):
        if len(self.prior_symbols) <= self.nback:
            return ''
        else:
            return self.prior_symbols[self.nback]

    def current_symbol(self):
        return self.prior_symbols[0]

    def get_new_symbol(self):
        """assigns new bonus symbol"""
        
        if isinstance(self.bonus_symbols_game,list) and len(self.bonus_symbols_game) > 0:
            new_symbol = self.bonus_symbols_game.pop(0)
            #print new_symbol
            if (self.bonus_types.pop(0) == "non-bonus"):
                self.flag = True
        else:
            if self.match_any_symbol:
                if random.random() < self.probability and self.get_nback_symbol():
                    new_symbol = self.get_nback_symbol()
                else:
                    # ensure that we don't accidentally pick a match
                    choices = self.symbols[:]
                    if self.get_nback_symbol() in choices:
                        choices.remove(self.get_nback_symbol())
                    new_symbol = random.choice(choices)
                    self.flag = True
            else:
                if random.random() < self.probability:
                    new_symbol = self.bonus_symbol
                else:
                    new_symbol = random.choice(self.symbols)
                    self.flag = True
        self.prior_symbols.insert(0,new_symbol)
        #print new_symbol
        if (len(self.prior_symbols) > self.nback+1):
            self.prior_symbols = self.prior_symbols[:self.nback+1]

    def update(self):
        if (self.visible == False) and (self.timer.elapsed() >= self.down_time):
            self.visible = True
            self.timer.reset()
            self.get_new_symbol()
            self.text = "%s"%self.current_symbol()
            #self.app.log.write("# new symbol %s\n"%self.current_symbol)
	    if self.match_any_symbol or self.current_symbol() == self.bonus_symbol:
                self.app.log.add_event('new-symbol-bonus')
                if self.current_symbol() == self.get_nback_symbol():
                    self.app.log.add_event('bonus-available')
	    else:
                self.app.log.add_event('new-symbol-non-bonus')
            #self.app.log.add_event('new-symbol-%s'%self.current_symbol)
        elif (self.visible == True) and (self.timer.elapsed() >= self.up_time):
            # piggyback off the fact that text = 'Bonus' when they ID a symbol
            if self.disable_firing and self.current_symbol() == self.get_nback_symbol() == self.text:
                self.app.log.add_event('firing-disabled')
                self.app.ship.firing_disabled = True
            self.visible = False
            self.app.log.add_event('symbol-disappeared')
            self.timer.reset()

    def add_points(self):
        self.app.log.add_event('got-bonus-pnts')
        self.app.score.reward('pnts', 'bonus_pnts')

    def add_shots(self):
        self.app.log.add_event('got-bonus-shots')
        self.app.score.reward('shots', 'bonus_shots')
        if self.app.score.shots > 100:
            self.app.score.shots = 100

    def add_bonus(self,bonus_type):
        if self.disable_firing:
            self.app.log.add_event('firing-enabled')
            self.app.ship.firing_disabled = False
        self.text = "Bonus"
        if self.auto_select:
            if self.app.score.shots > 50:
                self.add_points()
            else:
                self.add_shots()
        elif bonus_type == BONUS_POINTS:
            self.add_points()
        elif bonus_type == BONUS_SHOTS:
            self.add_shots()
        else:
            raise Exception("Invalid bonus type: %s" % bonus_type)

    def mismatch(self):
        self.app.log.add_event('prior-symbol-mismatch')
        if self.disable_firing:
            self.app.log.add_event('firing-disabled')
            self.app.ship.firing_disabled = True
        else:
            self.flag = False

    def check_for_match(self,bonus_type):
        if self.match_any_symbol:
            if self.current_symbol() == self.get_nback_symbol() and self.flag:
                self.add_bonus(bonus_type)
            elif self.current_symbol() != self.get_nback_symbol():
                self.mismatch()
        else:
            if self.current_symbol() == self.bonus_symbol == self.get_nback_symbol() and self.flag:
                self.add_bonus(bonus_type)
            elif self.current_symbol() == self.bonus_symbol != self.get_nback_symbol():
                self.mismatch()
