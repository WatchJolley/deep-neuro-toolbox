import sys
sys.path.append("..")

import tensorflow as tf
import lucid
import numpy as np
import atari_zoo
from atari_zoo import MakeAtariModel
from atari_zoo.activation_movie import *
from atari_zoo.rollout import generate_rollout

from lucid.misc.io import show
import lucid.optvis.objectives as objectives
import lucid.optvis.param as param
import lucid.optvis.transform as transform
import lucid.optvis.render as render

from atari_zoo import game_list
from pylab import *

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# currently supported algorithms
algos = ['a2c','es','ga','apex','rainbow','dqn']

algo = 'ga' # which algorithm
env = "AlienNoFrameskip-v4" #game_list[0] # which gym environment
run_id = 1 # which run?
tag = 'final' # which checkpoint?
filename = algo + '_' + env  + '_' + str(run_id)

print('Algorithm: {} Environment: {} Run Id: {} Tag: {}'.format(algo,env,run_id,tag))

# load model
m = MakeAtariModel(algo,env,run_id,tag=tag,local=True)()

# load in graphdef & graph
m.load_graphdef()
m.import_graph()

obs = m.get_observations()
frames = m.get_frames()
ram = m.get_ram()
scores = m.get_scores()
rep = m.get_representation()
episode_rewards = m.get_episode_rewards()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import atari_zoo.utils
from atari_zoo.utils import conv_activations_to_canvas
from atari_zoo.utils import fc_activations_to_canvas
from lucid.optvis.render import import_model

# get a tf session
session = atari_zoo.utils.get_session()

# #create a placeholder input to the network
X_t = tf.placeholder(tf.float32, [None] + m.image_shape)

# now get access to a dictionary that grabs output layers from the model
T = import_model(m,X_t,X_t)
cc = MakeActivationVideo(m)
cc.write_videofile( filename + ".mp4")