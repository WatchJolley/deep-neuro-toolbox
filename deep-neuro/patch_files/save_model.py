import sys
import tensorflow as tf
import tabular_logger as tlogger
from neuroevolution.helper import SharedNoiseTable
from neuroevolution.models import *
from tensorflow.python.framework import graph_util
from tensorflow.python.tools import optimize_for_inference_lib

# command line arguments provides game, learning style and run id
game        = str(sys.argv[1])
learning    = str(sys.argv[2])
run         = sys.argv[3]

# hashmap of human readable game names with the appropriate classification 
game_action = {'demon_attack': 6, 'bowling': 6, 'qbert': 6, 'gopher': 8, 'pong': 6, 'battle_zone': 18, 'video_pinball': 9, 'frostbite': 18, 'beam_rider': 9, 'yars_revenge': 18, 'road_runner': 18, 'james_bond': 18, 'gravitar': 18, 'ice_hockey': 18, 'fishing_derby': 18, 'berzerk': 18, 'crazy_climber': 9, 'chopper_command': 18, 'wizard_of_wor': 10, 'zaxxon': 18, 'alien': 18, 'pitfall': 18, 'krull': 18, 'kangaroo': 18, 'bank_heist': 18, 'space_invaders': 6, 'robotank': 18, 'amidar': 10, 'enduro': 9, 'asterix': 9, 'montezuma_revenge': 18, 'venture': 18, 'double_dunk': 18, 'kung_fu_master': 14, 'time_pilot': 10, 'centipede': 18, 'breakout': 4, 'seaquest': 18, 'phoenix': 8, 'freeway': 3, 'atlantis': 4, 'private_eye': 18, 'name_this_game': 6, 'tutankham': 8, 'tennis': 18, 'assault': 7, 'solaris': 18, 'starGunner': 18, 'asteroids': 14, 'skiing': 3, 'hero': 18, 'boxing': 18, 'ms_pacman': 9, 'up_n_down': 6, 'riverraid': 18}
game_names = {'demon_attack' : 'DemonAttackNoFrameskip-v4','bowling' : 'BowlingNoFrameskip-v4','qbert' : 'QbertNoFrameskip-v4','gopher' : 'GopherNoFrameskip-v4','pong' : 'PongNoFrameskip-v4','battle_zone' : 'BattleZoneNoFrameskip-v4','video_pinball' : 'VideoPinballNoFrameskip-v4','frostbite' : 'FrostbiteNoFrameskip-v4','beam_rider' : 'BeamRiderNoFrameskip-v4','yars_revenge' : 'YarsRevengeNoFrameskip-v4','road_runner' : 'RoadRunnerNoFrameskip-v4','james_bond' : 'JamesbondNoFrameskip-v4','gravitar' : 'GravitarNoFrameskip-v4','ice_hockey' : 'IceHockeyNoFrameskip-v4','fishing_derby' : 'FishingDerbyNoFrameskip-v4','berzerk' : 'BerzerkNoFrameskip-v4','crazy_climber' : 'CrazyClimberNoFrameskip-v4','chopper_command' : 'ChopperCommandNoFrameskip-v4','wizard_of_wor' : 'WizardOfWorNoFrameskip-v4','zaxxon' : 'ZaxxonNoFrameskip-v4','alien' : 'AlienNoFrameskip-v4','pitfall' : 'PitfallNoFrameskip-v4','krull' : 'KrullNoFrameskip-v4','kangaroo' : 'KangarooNoFrameskip-v4','bank_heist' : 'BankHeistNoFrameskip-v4','space_invaders' : 'SpaceInvadersNoFrameskip-v4','robotank' : 'RobotankNoFrameskip-v4','amidar' : 'AmidarNoFrameskip-v4','enduro' : 'EnduroNoFrameskip-v4','asterix' : 'AsterixNoFrameskip-v4','montezuma_revenge' : 'MontezumaRevengeNoFrameskip-v4','venture' : 'VentureNoFrameskip-v4','double_dunk' : 'DoubleDunkNoFrameskip-v4','kung_fu_master' : 'KungFuMasterNoFrameskip-v4','time_pilot' : 'TimePilotNoFrameskip-v4','centipede' : 'CentipedeNoFrameskip-v4','breakout' : 'BreakoutNoFrameskip-v4','seaquest' : 'SeaquestNoFrameskip-v4','phoenix' : 'PhoenixNoFrameskip-v4','freeway' : 'FreewayNoFrameskip-v4','atlantis' : 'AtlantisNoFrameskip-v4','private_eye' : 'PrivateEyeNoFrameskip-v4','name_this_game' : 'NameThisGameNoFrameskip-v4','tutankham' : 'TutankhamNoFrameskip-v4','tennis' : 'TennisNoFrameskip-v4','assault' : 'AssaultNoFrameskip-v4','solaris' : 'SolarisNoFrameskip-v4','starGunner' : 'StarGunnerNoFrameskip-v4','asteroids' : 'AsteroidsNoFrameskip-v4','skiing' : 'SkiingNoFrameskip-v4','hero' : 'HeroNoFrameskip-v4','boxing' : 'BoxingNoFrameskip-v4','ms_pacman' : 'MsPacmanNoFrameskip-v4','up_n_down' : 'UpNDownNoFrameskip-v4', 'riverraid' : 'RiverraidNoFrameskip-v4'}

# for logging the frozen model
game_folder = game_names[game]
game_action_counts = game_action[game]
root_folder = '~/space/rlzoo/'
LOGDIR= root_folder + learning + '/' + game_folder + '/'
file_name = 'model' + str(run) + '_final'

# parameter should map to input tensor
image_shape = [84, 84, 4]

# seeds are saved in txt files in the log dir, they are used to generate the weights for the network
seedsfile = LOGDIR + str(game) + '_' + str(file_name) + '.txt'
print(seedsfile)
with open(seedsfile, 'r') as file:
    seeds = file.read().replace('\n', '')
    seeds = eval(seeds)

print(seeds)

def main():
    model = None
    if (learning == 'recurrent'): model = RecurrentLargeModel()
    if (learning == 'ga'): model = LargeModel()

    X_t = tf.placeholder(tf.float32, [None] + image_shape, name='X_t')
    action_op = model.make_net(tf.expand_dims(X_t, axis=1), game_action_counts, batch_size=1)

    all_saver = tf.train.Saver() 

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        model.initialize()
        tlogger.info(model.description)
        noise = SharedNoiseTable()
        weights = model.compute_weights_from_seeds(noise, seeds)
        model.load(sess, 0, weights, seeds)

        # -----------------------------------------------------------------
        node_names = [node.name for node in tf.get_default_graph().as_graph_def().node]
        new_node = []

        for i in node_names:
            if "ga" in i:
                new_node.append(i)
                pass

        graph_const = tf.graph_util.convert_variables_to_constants(sess,
                                                     sess.graph.as_graph_def(),
                                                     ['ga/Reshape_1'])

    outgraph = optimize_for_inference_lib.optimize_for_inference(
                    graph_const,
                    ['X_t'], # an array of the input node(s)
                    ['ga/Reshape_1'], # an array of output nodes
                    tf.float32.as_datatype_enum)

    # write frozen model to LOGDIR
    tf.train.write_graph(outgraph, LOGDIR, file_name +'.pb', as_text=False)

    # human readable format
    # tf.train.write_graph(outgraph, LOGDIR, file_name + '.pbtxt', as_text=True)

    print("Freezed graph for {} with {} game actions to {}{}.pb.".format(game,game_action_counts,LOGDIR,file_name))

if __name__ == "__main__":
    main()