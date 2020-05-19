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
import tensorflow as tf
from gym_tensorflow.tf_env import TensorFlowEnv, gym_tensorflow_module
import numpy as np

types_of_tensor = ['RGB','objects','greyscale']
tensor_layer_size = [3,6,1]
RC_size_x = 20
RC_size_y = 20

class RivercrossingEnv(TensorFlowEnv):
    def __init__(self, input_tensor, batch_size, name=None, env_size=(RC_size_x, RC_size_y) ):
        assert input_tensor in types_of_tensor, "{} is not part of the available River Crossing Tensors".format(input_tensor)

        self.input_tensor = input_tensor
        self.batch_size = batch_size
        self.env_size = env_size

        # choose the apprioate number of layers 
        for i in range(len(types_of_tensor)):
             if (self.input_tensor ==    types_of_tensor[i]):
                self.num_stacked_frames = tensor_layer_size[i]

        with tf.variable_scope(name, default_name='RiverInstance'):
            self.instances = gym_tensorflow_module.rivercrossing_make(input_tensor=input_tensor, num_layers=self.num_stacked_frames, batch_size=batch_size)
        self.obs_variable = tf.Variable(tf.zeros(shape=self.observation_space, dtype=tf.int32), trainable=False)

    @property
    def observation_space(self):
        return (self.batch_size, ) + self.env_size + (self.num_stacked_frames,)

    @property
    def env_default_timestep_cutoff(self):
        return 20000000

    """
    Amount of output from network
    """
    @property 
    def action_space(self):
        return 18

    @property
    def discrete_action(self):
        return True

    def step(self, action, indices=None, name=None):
        if indices is None:
            indices = np.arange(self.batch_size)
        with tf.variable_scope(name, default_name='RivercrossingStep'):
            rew, done = gym_tensorflow_module.environment_step(self.instances, indices, action)
            return rew, done

    def reset(self, indices=None, max_frames=None, name=None):
        '''Resets River Crossing instances with a random noop start (1-30) and set the maximum number of frames for the episode (default 100,000 * frameskip)
        '''
        if indices is None:
            indices = np.arange(self.batch_size)

        with tf.variable_scope(name, default_name='RivercrossingReset'):
            noops = tf.random_uniform(tf.shape(indices), minval=1, maxval=31, dtype=tf.int32)
            if max_frames is None:
                max_frames = self.env_default_timestep_cutoff
            return gym_tensorflow_module.environment_reset(self.instances, indices, noops=noops, max_frames=max_frames)

    def observation(self, indices=None, name=None):
        if indices is None:
            indices = np.arange(self.batch_size)
        with tf.variable_scope(name, default_name='RivercrossingObservation'):
            with tf.device('/cpu:0'):
                obs = gym_tensorflow_module.environment_observation(self.instances, indices, T=tf.float32)
            obs.set_shape((None,) + self.env_size + (self.num_stacked_frames,))
        return obs


    def close(self):
        pass