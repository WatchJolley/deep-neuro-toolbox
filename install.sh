#!/bin/bash

# install deep neuro
cd deep-neuro
bash install.sh
mv deep-neuroevolution ../
cd ../

# install atari zoo
cd zoo
bash install.sh
mv atari-model-zoo ../
cd ../

# clean up folder structure
mkdir misc
mv deep-neuro misc
mv zoo misc