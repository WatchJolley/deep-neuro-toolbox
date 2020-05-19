__copyright__ = """
Copyright (c) 2018 Uber Technologies, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys
# enter the dir for the gym_tensorflow.so for 'import gym_tensorflow'
sys.path.append('...')

import time
import os
import tensorflow as tf
import numpy as np
import gym_tensorflow

from lucid.modelzoo.vision_base import Model as lucid_model
from tensorflow.python.tools import optimize_for_inference_lib
from lucid.optvis.render import import_model

# command line arguments provides game, learning style and run id
game = str(sys.argv[1])
learning = str(sys.argv[2])
run = sys.argv[3]

# hashmap of human readable game names with the appropriate classification 
game_names = {'demon_attack' : 'DemonAttackNoFrameskip-v4','bowling' : 'BowlingNoFrameskip-v4','qbert' : 'QbertNoFrameskip-v4','gopher' : 'GopherNoFrameskip-v4','pong' : 'PongNoFrameskip-v4','battle_zone' : 'BattleZoneNoFrameskip-v4','video_pinball' : 'VideoPinballNoFrameskip-v4','frostbite' : 'FrostbiteNoFrameskip-v4','beam_rider' : 'BeamRiderNoFrameskip-v4','yars_revenge' : 'YarsRevengeNoFrameskip-v4','road_runner' : 'RoadRunnerNoFrameskip-v4','james_bond' : 'JamesbondNoFrameskip-v4','gravitar' : 'GravitarNoFrameskip-v4','ice_hockey' : 'IceHockeyNoFrameskip-v4','fishing_derby' : 'FishingDerbyNoFrameskip-v4','berzerk' : 'BerzerkNoFrameskip-v4','crazy_climber' : 'CrazyClimberNoFrameskip-v4','chopper_command' : 'ChopperCommandNoFrameskip-v4','wizard_of_wor' : 'WizardOfWorNoFrameskip-v4','zaxxon' : 'ZaxxonNoFrameskip-v4','alien' : 'AlienNoFrameskip-v4','pitfall' : 'PitfallNoFrameskip-v4','krull' : 'KrullNoFrameskip-v4','kangaroo' : 'KangarooNoFrameskip-v4','bank_heist' : 'BankHeistNoFrameskip-v4','space_invaders' : 'SpaceInvadersNoFrameskip-v4','robotank' : 'RobotankNoFrameskip-v4','amidar' : 'AmidarNoFrameskip-v4','enduro' : 'EnduroNoFrameskip-v4','asterix' : 'AsterixNoFrameskip-v4','montezuma_revenge' : 'MontezumaRevengeNoFrameskip-v4','venture' : 'VentureNoFrameskip-v4','double_dunk' : 'DoubleDunkNoFrameskip-v4','kung_fu_master' : 'KungFuMasterNoFrameskip-v4','time_pilot' : 'TimePilotNoFrameskip-v4','centipede' : 'CentipedeNoFrameskip-v4','breakout' : 'BreakoutNoFrameskip-v4','seaquest' : 'SeaquestNoFrameskip-v4','phoenix' : 'PhoenixNoFrameskip-v4','freeway' : 'FreewayNoFrameskip-v4','atlantis' : 'AtlantisNoFrameskip-v4','private_eye' : 'PrivateEyeNoFrameskip-v4','name_this_game' : 'NameThisGameNoFrameskip-v4','tutankham' : 'TutankhamNoFrameskip-v4','tennis' : 'TennisNoFrameskip-v4','assault' : 'AssaultNoFrameskip-v4','solaris' : 'SolarisNoFrameskip-v4','starGunner' : 'StarGunnerNoFrameskip-v4','asteroids' : 'AsteroidsNoFrameskip-v4','skiing' : 'SkiingNoFrameskip-v4','hero' : 'HeroNoFrameskip-v4','boxing' : 'BoxingNoFrameskip-v4','ms_pacman' : 'MsPacmanNoFrameskip-v4','up_n_down' : 'UpNDownNoFrameskip-v4', 'riverraid' : 'RiverraidNoFrameskip-v4'}

# for logging the rollout file
game_folder = game_names[game]
root_folder = '/home/ben/space/rlzoo/'
LOGDIR= root_folder + learning + '/' + game_folder + '/'
file_name = 'model' + str(run) + '_final'

# these parameters should map the output name for the last layer and input tensor
OUTPUT='ga/Reshape_1'
image_shape = [84, 84, 4]

def main():
    env = gym_tensorflow.make(game,1)

    # loading frozen model
    model = lucid_model()
    model.model_path = LOGDIR + file_name + '.pb'
    model.image_shape = image_shape
    model.input_scale = 1.0
    model.image_value_range = (0, 1) 
    model.input_name = 'X_t'
    model.ph_type = 'float32'
    model.layers =  layers = [ # names here must correlate to the frozens models layer names
     {'type': 'conv', 'name': 'ga/Relu', 'size': 32},
     {'type': 'conv', 'name': 'ga/Relu_1', 'size': 64},
     {'type': 'conv', 'name': 'ga/Relu_2', 'size': 64},
     {'type': 'dense', 'name': 'ga/Relu_3', 'size': 512},
     {'type': 'dense', 'name': 'ga/Reshape_1', 'size':18}
   ]
    model.load_graphdef()
    model.save(LOGDIR + file_name + "2.pb")
    # ----------------------------------------------------------------
    obs_op = env.observation()
    reset_op = env.reset()

    T = import_model(model,obs_op,obs_op)
    action_op = T(model.layers[-1]['name'])
    # ----------------------------------------------------------------

    if env.discrete_action:
        action_op = tf.argmax(action_op, axis=-1, output_type=tf.int32)
    rew_op, done_op = env.step(action_op)

    # viewer = rendering.SimpleImageViewer()
    if hasattr(env.unwrapped, 'render'):
        obs_op = env.unwrapped.render()
        def display_obs(im):
            im = im[0, 0, ...]
            # viewer.imshow(im)
    else:
        def display_obs(im):
            im = im[0, :, :, -1]
            im = np.stack([im] * 3, axis=-1)
            im = (im * 255).astype(np.uint8)

            im = np.array(Image.fromarray(im).resize((256, 256), resample=Image.BILINEAR), dtype=np.uint8)
            # viewer.imshow(im)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        sess.run(reset_op)
        display_obs(sess.run(obs_op))

        # for debugging purposes create graph of frozen model
        # train_writer = tf.summary.FileWriter(LOGDIR)
        # train_writer.add_graph(sess.graph.as_graph_def())

        total_rew = 0
        num_frames = 0


        # get intermediate level representations
        activations = [T(layer['name']) for layer in model.layers]
        print(activations)
        high_level_rep = activations[-2] #not output layer, but layer before

        sample_observations = []   #(84, 84, 4)
        sample_frames = [] 		   #(210, 160, 3)
        sample_ram = [] 		   #(128,)
        sample_representation = [] #(1, 512)
        sample_score = [] 
        rewards = []

        # run through each frame a record; observations, frames, ram, and representation
        while True:
            rew, done = sess.run([rew_op, done_op])
            num_frames += 1
            total_rew += rew[0]
            obs = sess.run(obs_op)
            display_obs(obs)

            # sample_observations
            wrapped = sess.run(env.observation())
            wrapped = np.reshape(wrapped,
                       (wrapped.shape[1], wrapped.shape[2], wrapped.shape[3]))
            sample_observations.append(wrapped)

            # sample_frames 
            frame = obs[0, 0, :, :, :,]
            sample_frames.append(frame)

            # sample_ram
            # sample_ram.append(env.unwrapped._get_ram())

            # sample_representation
            representation = sess.run(high_level_rep)
            representation = np.reshape(representation,
                       (representation.shape[1], representation.shape[2]))
            sample_representation.append(representation)

            time.sleep(1/240)

            # when complete, write to file
            if done[0]:
                print('Final reward: ', total_rew, 'after', num_frames, 'steps')
                results = {'observations':sample_observations,'frames':sample_frames,'ram':sample_ram,'representation':sample_representation,'score':sample_score,'ep_rewards':rewards}
                np.savez_compressed(LOGDIR + file_name + "_rollout",**results)
                break
if __name__ == "__main__":
    main()