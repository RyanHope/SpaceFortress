from __future__ import division
import sys
import os
import copy
import random

import config
import sdl_game
import screens
from experiment import exp

from wx_model_main import start_wx_model_server
from main import start_sdl_experiment

if __name__ == '__main__':
    (gc, config_path) = config.get_global_config()
    if int(gc['model']) == 1:
        start_wx_model_server()
    else:
        start_sdl_experiment()
