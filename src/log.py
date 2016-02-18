import os
import sys
import time
import codecs

class base(object):
    def __init__(self, id, datapath, session_name):
        self.id = id
        self.session = "1" if session_name == None else session_name
        self.datapath = datapath + "/%s/"%self.id
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

class session_log(base):
    def __init__(self, id, datapath, session_name):
        super(self.__class__, self).__init__(id, datapath, session_name)
        self.game = 0

    def open_slog(self):
        self.sessionlog = open(os.path.join(self.datapath, '%s-%s.dat'%(self.id,self.session)),'a', 0)

    def close_slog(self):
        self.sessionlog.close()

    def slog(self,string,args={}):
        """Write a string to the session-wide log file with optional key/value pairs."""
        acc = []
        for k,v in args.iteritems():
            acc.append("%s=%s"%(k,str(v).replace(' ','\ ')))
        self.sessionlog.write("%f %d %s %s\n"%(time.time(),self.game,string, " ".join(acc)))

class game_log(base):
    def __init__(self,id,datapath,session_name,game_num):
        super(self.__class__, self).__init__(id, datapath, session_name)
        self.version = "1.6"
        self.game = game_num
        self.events = []

    def write_gamelog_header(self):
	self.gamelog.write("# log version %s\n"%self.version)
	self.gamelog.write("# non-hashed line notation:\n")
	self.gamelog.write("# game_clock system_clock game_time ship_alive? ship_x ship_y ship_vel_x ship_vel_y ship_orientation mine_alive? mine_x mine_y \
fortress_alive? fortress_orientation [missile_x missile_y missile_orientation ...] [shell_x shell_y shell_orientation ...] bonus_symbol \
pnts cntrl vlcty vlner iff intervl speed shots thrust_key left_key right_key fire_key iff_key shots_key pnts_key game_active\n")

    def rename_existing_file(self, f):
        if os.path.exists(f):
            n = 1
            new_file = "%s.%d.bak"%(f,n)
            while os.path.exists(new_file):
                n += 1
                new_file = "%s.%d.bak"%(f,n)
            os.rename(f, new_file)

    def open_simulate_logs(self):
        self.sessionlog = open(os.path.join(self.datapath, '%s-%s.sim.dat'%(self.id,self.session)),'a')
        tempname = os.path.join(self.datapath,"%s-%s-%d.sim.dat"%(self.id, self.session, self.game))
        simfile = os.path.join(self.datapath,"%s-%s-%d.key"%(self.id, self.session, self.game))
        keyfile = tempname[:-3]+'key'
        evtfile = tempname[:-3]+"evt"
        self.gamelog = codecs.open(tempname,'w','utf-8')
        self.eventlog = open(evtfile,'w')
        self.keylog = open(keyfile, 'w')
        self.write_gamelog_header()
        if os.path.exists(simfile):
            self.simulate_key_stream = open(simfile)
        else:
            print('Error: Could not find key file: ' + simfile + '\n');
            sys.exit()
        self.config_filename = "unused"

    def open_gamelogs(self, config):
        tempname = os.path.join(self.datapath,"incomplete-%s-%s-%d.dat"%(self.id, self.session, self.game))
        #print tempname
        keyfile = tempname[:-3]+"key"
        evtfile = tempname[:-3]+"evt"
        # Make sure we NEVER overwrite existing data
        for f in [tempname, keyfile, evtfile]:
            self.rename_existing_file(f)
        self.gamelog = codecs.open(tempname, "w", 'utf-8', 'strict', 0)
        self.eventlog = open(evtfile,'w', 0)
        self.keylog = open(keyfile, 'w', 0)
        self.write_gamelog_header()
        self.record_config(config)

    def close_gamelogs(self):
        self.gamelog.close()
        self.eventlog.close()
        self.keylog.close()
        if hasattr(self,'simulate_key_stream'):
            self.simulate_key_stream.close()

    def record_config(self, config):
        self.config_filename = os.path.join(self.datapath, "incomplete-%s-%s-%d.config.txt"%(self.id,self.session,self.game))
        self.rename_existing_file(self.config_filename)
        with codecs.open(self.config_filename, "w", 'utf-8') as out:
            for k,v in (sorted(config.items())):
                if isinstance(v, basestring):
                    out.write('%s %s\n'%(k,v))
                else:
                    out.write('%s %s\n'%(k,' '.join(v)))

    def session_comment(self,string):
        """Add a comment to the session file."""
        self.sessionlog.write("# %s\n" % string)

    def glog(self,string):
        self.gamelog.write("# %s\n"%string)

    def add_event(self,event_id):
        self.events.append(event_id)

    def write_events(self,times):
        """Call this function every frame."""
        self.eventlog.write("%d %f "%times)
        self.eventlog.write(",".join(self.events)+"\n")
        self.events = []

    def write_random_seed(self,seed):
        self.keylog.write('# %d\n'%seed)

    def write_keys(self,keys):
        self.keylog.write(str(keys)+"\n")

    def write_game_state(self,times,state):
        self.gamelog.write("%d %f "%times)
        self.gamelog.write(" ".join(map(unicode,state))+"\n")

    def rename_logs_completed(self):
        '''When the game is done, remove the incomplete text from the
        log files.'''
        for f in [self.gamelog.name, self.eventlog.name, self.keylog.name, self.config_filename]:
            (dir,name) = os.path.split(f)
            if name.startswith('incomplete-'):
                new = os.path.join(dir,name[11:])
                # Make sure we NEVER overwrite existing data
                self.rename_existing_file(new)
                os.rename(f,new)

    def log_premature_exit(self):
        self.gamelog.write("# Escaped prematurely\n")
        self.eventlog.write("# Escaped prematurely\n")
        self.keylog.write("#ESCAPE\n");

    def simulate_next_frame(self):
        while True:
            line = self.simulate_key_stream.readline()
            if len(line) == 0:
                print('Error: keys file too short.')
                sys.exit()
            elif line[0] in ["#","\n"]:
                continue
            else:
                break
        return eval(line)
