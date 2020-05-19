#!/bin/bash

# note: deep neuroevolution does not have a release version yet
#       code may change and the patches may not work

# move to patch file
cd patch_files

# clone deep neuroevolution code
git clone https://github.com/uber-research/deep-neuroevolution.git

# move files to correct positions
cp formatting.py deep-neuroevolution/gpu_implementation
cp -r rivercrossing/ deep-neuroevolution/gpu_implementation/gym_tensorflow/
cp save_model.py deep-neuroevolution/gpu_implementation/neuroevolution 
cp scheduled_run.sge deep-neuroevolution/gpu_implementation
cp *.patch deep-neuroevolution/

# move to deep neuroevolution dir
cd deep-neuroevolution/

# apply patches
patch -s -p0 < river_patch.patch
patch -s -p0 < threads_patch.patch

# move deep neuroevolution dir
cd ../
mv deep-neuroevolution ../