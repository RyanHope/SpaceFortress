import timer

class Score(object):
    """collection of game scores"""
    def __init__(self, app, config):
        self.app = app
        self.pnts = 0
        self.raw_pnts = 0
        self.cntrl = 0
        self.vlcty = 0
        self.vlner = 0
        self.iff = ''
        self.intrvl = 0
        self.speed = 0
        self.shots = float('inf') if config["shots"] == "inf" else int(config["shots"])
        self.crew_members = int(config['crew_members'])
        #score labels
        self.labels = config['score_labels']
        self.updatetimer = timer.Timer()
        # FIXME: state used for drawing
        self.label_width = 89
        self.label_surfs = []
        self.label_rects = []
        self.dashboard_width = len(self.labels)*self.label_width

    def penalize (self, label, config_var):
        val = int(self.app.config[config_var])
        if label == "pnts":
            self.raw_pnts -= val
            self.pnts -= val
            if self.app.config['negative_pnts'] == 'prohibited' and self.pnts < 0:
                self.pnts = 0
        elif label == "cntrl":
            self.cntrl -= val
        elif label == "vlcty":
            self.vlcty -= val
        elif label == "speed":
            self.speed -= val
        else:
            raise Exception ('unknown score label: %s'%label)

    def reward_amt(self, label, val):
        if label == "pnts":
            self.raw_pnts += val
            self.pnts += val
        elif label == "cntrl":
            self.cntrl += val
        elif label == "vlcty":
            self.vlcty += val
        elif label == "speed":
            self.speed += val
        elif label == "shots":
            self.speed += val
        else:
            raise Exception ('unknown score label: %s'%label)

    def reward (self, label, config_var):
        val = int(self.app.config[config_var])
        self.reward_amt(label, val)

    def get_value(self, label):
        if label == "pnts":
            val = "%d"%self.pnts
        elif label == "cntrl":
            val = "%d"%self.cntrl
        elif label == "vlcty":
            val = "%d"%self.vlcty
        elif label == "vlner":
            val = "%d"%self.vlner
        elif label == "iff":
            val = "%s"%self.iff
        elif label == "intrvl":
            if self.app.mine.exists and self.intrvl != 0:
                val = "%d"%self.intrvl
            else:
                val = ""
        elif label == "speed":
            val = "%d"%self.speed
        elif label == "shots":
            if self.shots == float('inf'):
                val = ""
            else:
                val = "%d"%self.shots
        elif label == "crew":
            val = "%d"%self.crew_members
        else:
            val = ""
        return val
