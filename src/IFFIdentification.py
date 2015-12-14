import math
from timer import Timer

class IFFData():
    def __init__(self,foe,hit,response,keyflag):
        self.foe = foe
        self.hit = hit
        self.response = response
        self.keyflag = keyflag

    def __cmp__(self,other):
        return self.response.__cmp__(other.response)

class IFFIdentification():
    def __init__(self,config):
        self.mines = []
        self.intervalflag = False
        self.timer = Timer()
        self.feedback_enabled = int(config["IFF_feedback"]) == 1
        self.feedback_checking = False
        self.max_number_of_tries = int(config["IFF_tries"])
        self.number_of_tries = 0

    def add_mine(self,foe,response,hit=False):
        self.number_of_tries = 0
        self.mines.append(IFFData(foe,hit,response,self.intervalflag))

    def keypress (self,log,score):
        """Call when the IFF key is pressed. Returns the value to be stored in the score's interval slot."""
        if self.intervalflag:
            self.intervalflag = False
            score.intrvl = int(self.timer.elapsed())
        else:
            if self.max_number_of_tries == 0 or self.number_of_tries < self.max_number_of_tries:
                self.number_of_tries += 1
                self.intervalflag = True
                self.timer.reset()
                self.feedback_checking = True
                score.intrvl = 0
            else:
                log.add_event('IFF-too-many-ids')

    def check_for_timeout(self,log,score):
        if self.intervalflag and self.timer.elapsed() > 5000:
            self.intervalflag = False
            log.add_event('IFF-id-timeout')
            score.intrvl = 0

    def update(self, world):
        if self.feedback_enabled and world.mine.alive and self.feedback_checking and world.mine.is_foe():
            # Pressed IFF key too soon
            if not self.intervalflag and 0 < world.score.intrvl < int(world.config["intrvl_min"]) and self.timer.elapsed() >= int(world.config["intrvl_min"]):
                world.log.add_event('IFFFeedback-too-soon')
                world.sounds.beep_high.play()
                self.feedback_checking = False
            # Pressed IFF key in the interval window
            elif not self.intervalflag and world.mine.is_tagged():
                world.log.add_event('IFFFeedback-just-right')
                self.feedback_checking = False
            # Didn't press IFF key before interval timeout
            elif self.intervalflag and self.timer.elapsed() >= int(world.config["intrvl_max"]):
                world.log.add_event('IFFFeedback-too-late')
                world.sounds.beep_low.play()
                self.feedback_checking = False
        else:
            self.feedback_checking = False

    def summarize_dict(self,world):
        num_foes = 0
        num_no_resp = 0
        num_single_key = 0
        num_early = 0
        num_correct = 0
        num_late = 0
        for i in self.mines:
            if i.foe:
                num_foes+=1
                if i.response:
                    if i.response < int(world.config["intrvl_min"]):
                        num_early+=1
                    elif i.response <= int(world.config["intrvl_max"]):
                        num_correct+=1
                    else:
                        num_late+=1
                elif i.keyflag:
                    num_single_key+=1
                else:
                    num_no_resp+=1
        return {'iff-num-foes':num_foes,
                'iff-no-response':num_no_resp,
                'iff-single-key':num_single_key,
                'iff-too-early':num_early,
                'iff-correct':num_correct,
                'iff-too-late':num_late}
