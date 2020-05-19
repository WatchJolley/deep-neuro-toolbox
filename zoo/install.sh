#!/bin/bash

# move to patch file
cd patch_files

# get atari zoo files
git clone https://github.com/uber-research/atari-model-zoo.git

# move files to atari zoo dir
cp *.py atari-model-zoo/
cp *.patch atari-model-zoo/
cd atari-model-zoo/

# apply patch
patch -s -p0 < localzoo.patch

# move file to appropriate places
mv generate_video.py atari_zoo/

# move deep neuroevolution dir
cd ../
mv atari-model-zoo ../