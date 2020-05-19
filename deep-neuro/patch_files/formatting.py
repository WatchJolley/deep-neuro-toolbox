#!/usr/bin/env python
import os, inspect, re

# Methods --------------------------------------------------------

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def varname(p):
  for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
    m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
    if m:
      return m.group(1)

def csvString(args):
    string = ""
    for word in args:
        string = string + str(word) + ","
    string = string[:-1] + "\r\n"
    return string

# Parameters to change ---------------------------------------------
root_directory = "./runs/"

bool_PopulationEpRewMax                = 1
bool_PopulationEpRewMean               = 1
bool_PopulationTimesteps               = 1
bool_TruncatedPopulationRewMean        = 1
bool_tedPopulationValidationRewMean    = 1
bool_pulationEliteValidationRewMean    = 1
bool_atedPopulationEliteTestRewMean    = 1
bool_tedPopulationEliteTestEpLenSum    = 1
bool_ValidationTimestepsThisIter       = 1
bool_ValidationTimestepsSoFar          = 1
bool_TimestepsThisIter                 = 1
bool_TimestepsPerSecondThisIter        = 1
bool_TimestepsComputed                 = 1
bool_TimestepsSoFar                    = 1
bool_TimeElapsedThisIter               = 1
bool_TimeElapsedThisIterTotal          = 1
bool_TimeElapsed                       = 1
bool_TimeElapsedTotal                  = 1

# ------------------------------------------------------------------

keywords = []
titles = []

# ------------------------------------------------------------------
titles.append("Runs")

keywords.append(" Iteration ")
titles.append("Iteration") 

if (bool_PopulationEpRewMax):
	keywords.append(" PopulationEpRewMax ")
	titles.append("Population Episode Reward Max")
if (bool_PopulationEpRewMean):
	keywords.append(" PopulationEpRewMean ")
	titles.append("Population Episode Reward Mean")
if (bool_PopulationTimesteps):
	keywords.append(" PopulationTimesteps ")
	titles.append("Population Timesteps")
if (bool_TruncatedPopulationRewMean):
	keywords.append(" TruncatedPopulationRewMean ")
	titles.append("Truncated Population Reward Mean")
if (bool_tedPopulationValidationRewMean):
	keywords.append(" ...tedPopulationValidationRewMean ")
	titles.append("Truncated Population Validation Reward Mean")
if (bool_pulationEliteValidationRewMean):
	keywords.append(" ...pulationEliteValidationRewMean ")
	titles.append("Truncated Population Elite Validation Reward Mean")
if (bool_atedPopulationEliteTestRewMean):
	keywords.append(" ...atedPopulationEliteTestRewMean ")
	titles.append("Truncated Population Elite Test Reward Mean")
if (bool_tedPopulationEliteTestEpLenSum):
	keywords.append(" ...tedPopulationEliteTestEpLenSum ")
	titles.append("Truncated Population Elite Test Episode Len Sum")
if (bool_ValidationTimestepsThisIter):
	keywords.append(" ValidationTimestepsThisIter ")
	titles.append("Validation Timesteps This Iteration")
if (bool_ValidationTimestepsSoFar):
	keywords.append(" ValidationTimestepsSoFar ")
	titles.append("Validation Timesteps So Far")
if (bool_TimestepsThisIter):
	keywords.append(" TimestepsThisIter " )
	titles.append("Timesteps This Iteration" )
if (bool_TimestepsPerSecondThisIter):
	keywords.append(" TimestepsPerSecondThisIter" )
	titles.append("Timesteps Per Second This Iteration" )
if (bool_TimestepsComputed):
	keywords.append(" TimestepsComputed " )
	titles.append("Timesteps Computed" )
if (bool_TimestepsSoFar):
	keywords.append(" TimestepsSoFar ")
	titles.append("TimestepsSoFar ")
if (bool_TimeElapsedThisIter):
	keywords.append(" TimeElapsedThisIter ")
	titles.append("Time Elapsed This Iteration")
if (bool_TimeElapsedThisIterTotal):
	keywords.append(" TimeElapsedThisIterTotal ")
	titles.append("Time Elapsed This Iteration Total ")
if (bool_TimeElapsed):
	keywords.append(" TimeElapsed ")
	titles.append("Time Elapsed")
if (bool_TimeElapsedTotal):
	keywords.append(" TimeElapsedTotal ")
	titles.append("Time Elapsed Total")

title = csvString(titles)

# Functions---------------------------------------------------------

def sortListDir(directory):
    dir =[]
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)) == 0:
            dir.append(item)
    dir.sort(key=natural_keys)
    return dir

# return true if completed numOfGens, false if not
def writeToCSV(file, run):
    # loop through file line by line
    stringArgs = []
    if os.path.isfile(file):
        file = open(file)
        for line in file:
            if ((line.find( "Iteration " )) > 0):  # filter out only lines with data
                if(len(stringArgs) > 0):
                    stringArgs.insert(0, run)
                    f.write(csvString(stringArgs))
                stringArgs = []
            for word in keywords:
                if ((line.find( word )) > 0):  # filter out only lines with data
                    value = line[(line.find( word ) + len( word )): -1]
                    value = value.replace("|", "")
                    value = value.replace(" ", "")
                    value = float(value)
                    stringArgs.append(value)
# ------------------------------------------------------------------

# for each name in 'names' list
names = sortListDir(root_directory)
for name in names:
    # create Files
    f = open(root_directory + name + "-all.csv", 'w')
    f.write(title)

    completetionRanges = []
    directory = root_directory + name
    # sort directory names
    dir = sortListDir(directory)
    # for each run directory within the experiment name
    for item in dir:
        complete = "false"
        while True:
            if os.path.isdir(os.path.join(directory, item)):

                # setting Up Parameters
                run = ''.join(c for c in item if c.isdigit())
                pathTrain    = directory + "/" + item
                sofarDir     = pathTrain + "/so-far"
                file_name    = "ga.out"

                # if there are archived data files
                if (os.path.isdir(sofarDir)):

                    dir = sortListDir(sofarDir)

                    for root in dir:
                        # loop through file line by line
                        if(writeToCSV( sofarDir + "/" + root + "/" + file_name, run) == "true"):
                            complete = "true"
                            break

                if (complete == "false"):
                    writeToCSV( pathTrain + "/" + file_name, run )
                break

# ------------------------------------------------------------------
# close files
f.close()