#ifndef RIVERCROSSING_H
#define RIVERCROSSING_H
#include <vector>
#include <fstream>
#include <iostream>
#include <math.h>

#include "rivercrossing/dsworld.h"
#include "rivercrossing/animat.h"

#include "tools/defines.h"
#include "tools/random.h"


std::mutex mtx_1;           // mutex for critical section
using namespace std;

// directional postions of where an animat can go co-ordinates-wise. (E.g up, down, left etc)
static const int postions[][2] = {  {0,0},   {-1, 1},     {0,1},  {1,1},       {-1,0},   {1,0},  {-1,-1},   {0,-1},  {1,-1}    };
static const string actionsStr[] = {  "None","Down-Left", "Down", "Down-Right","Left",   "Right","Up-Left", "Up", "Up-Right" }; 
static const int outputsize = 18;

static const int agent_colour[] = {255, 0, 102};
static const int agent_colour_carrying[] = {102, 0, 255};

namespace river
{
    //all-encompassing environment class
    class Environment
    {
    private:
        vector<string> actionsString;
        int numOfAttempts = 10;

        int attempts = 0;
        int fitness = 0;
        bool level_complete = false;
        bool failed = false;
        int level = 0;

        bool stone_placed = false;

        int world_height = world::x;
        int world_width  = world::y;
        dsWorld worlds;
        animat agent;
        int seed;

        bool inRange(int location, int border)
        {
          if ( (0 <= location) && (location < border ) )
            return true;
          return false;
        }

        bool updatePostions(int x, int y)
        {
            // cout << "Actions X : " << x << " | Y : " << y << endl;
            // cout << "Before X : " << agent.x << " | Y : " << agent.y << endl;
            bool rtn = false;
            if ( inRange( agent.x + x, world_width ) ) {
                agent.x += x;
            } else {
                rtn = true;
            }
            if ( inRange( agent.y + y, world_height ) ) {
                agent.y += y;
            } else {
                rtn = true;
            }
            return rtn;
        }

        int getStarting()
        {
            int y, c;
            do {
              y = random(world_height);
              c = worlds.getCell(0,y);
            } while (c != 0);

           return y;
        }

    public:
        Environment() //Complete
        { }

        int height() //Complete
        { return world_height; }

        int width() //Complete
        {  return world_width; }

        // resets animat, dsWorld and Enviroment 
        void reset()
        {
            // for (int i = 0; i < actionsString.size(); ++i) cout << actionsString.at(i) << ", ";
            // cout << "" << endl;
            actionsString.clear();
            level = 0;
            fitness = 0;
            failed = 0;
            attempts = 0;
            stone_placed = false;
            updateWorld();
        }

        //resets animat and dsWorld with level
        void updateWorld()
        {
            level_complete = false;
            worlds = dsWorld(level);
            agent = animat();
            worlds.updateHeatmap(agent.x,agent.y);
        }

        // action to perfrom on stone depedning on input
        void stoneAction(bool pickUpAction)
        {
            agent.carrying = pickUpAction;
            worlds.cell[ agent.x ][ agent.y ] = EMPTYCELL;
        }

        // moves animat around dsworld
        // if animat fails ( i.e dies in trap or river)
        // then return true, else false
        bool move(int active, bool a_action)
        {
            if (updatePostions( postions[active][0], postions[active][1] )) return true;

            int cell = worlds.getCell( agent.x, agent.y );

            // if agent should take action
            if ( a_action==true )
            {
                // cout << "Action is True" << endl;
                // pick up Stone
                if ((!agent.carrying) && (cell == STONE))
                {
                    // cout << "Stone is picked up" << endl;
                    stoneAction(true);
                }

                 // place stone
                if ((agent.carrying) && (cell == WATER))
                {
                    // cout << "Stone is put down" << endl;
                    stone_placed = true;
                    stoneAction(false);
                }

                cell = worlds.getCell( agent.x, agent.y );
            }

            if ( (cell == TRAP) || (cell == WATER) ){
                // if (stone_placed)
                // {
                //     if (cell == TRAP)
                //     {
                //         cout << "Died of TRAP" << endl;
                //     } else {
                //         cout << "Died of WATER" << endl;
                //     }
                //     // worlds.printHeatmap();
                //     worlds.printAnimat(agent.x,agent.y);
                //     worlds.print();
                // }
                return true; // animat has failed here
            }

            if (cell == RESOURCE) {
                // if ( stone_placed )
                // {
                //     worlds.printHeatmap();
                //     worlds.printAnimat(agent.x,agent.y);
                //     worlds.print();
                // }
                level_complete =  true;
            }

            return false;
        }

        // run a time step of the simulation
        int Update(const int* action)
        {
            #ifdef LOCK_SIMULATION
                mtx_1.lock();
            #endif // LOCK_SIMULATION

            // if level has been complete (i.e resource has been found )
            // then update level and create new dsWorld and Animat
            if ( level_complete )
            {
                // 3 River width is the max width this task gos to
                if ( level == 3 ) {
                    // cout << "Ending Level : " << level << endl;
                    if (attempts == numOfAttempts)
                    {
                        failed = true;
                        return 150;
                    } else {
                        fitness += level;
                        attempts += 1;
                        level = -1;
                    }
                }

                // worlds.printHeatmap();
                // worlds.printAnimat(agent.x,agent.y);
                // // Print actions
                // for (int i = 0; i < actionsString.size(); ++i) cout << actionsString.at(i) << ", ";
                // cout << "" << endl;
                actionsString.clear();

                level++;
                stone_placed = false;
                updateWorld();
            }

            
            //find which output is activated
            // int active  =  0;
            // for (int i = 0; i < outputsize; i++)
            // {
            //     cout << action[i] << ", ";
            //     if ( action[active] < action[i] ) active = i;
            // }
            // cout << " " << endl;
            // cout << " ||| Largest : " << active << " - " << action[active] << " ||| action : " << a_action << endl;

            //Get action
            int active = action[0];
            //does the output use an action button
            bool a_action = (active > outputsize/2) ? true : false;
            active = (active >= outputsize/2) ? active-(outputsize/2) : active;

            // cout << " ||| Largest : " << active << " - " << action[active] << " ||| action : " << a_action << endl;

            // worlds.printHeatmap();
            if ( move( active, a_action ) )
            {
                // cout << "Attempt : " << attempts << " | Fitness : " << fitness << endl;
                worlds.updateHeatmap(agent.x,agent.y);
                // worlds.printHeatmap();
                // if (stone_placed)
                // {
                //     worlds.printAnimat(agent.x,agent.y);
                //     worlds.print();
                //     cout << " " << endl;
                // }
                // worlds.printHeatmap();
                // worlds.printAnimat(agent.x,agent.y);
                if (attempts == numOfAttempts) {
                   failed = true; 
                   return 150;
                } else {
                    actionsString.clear();
                    fitness += level;
                    attempts += 1;
                    level = 0;
                    stone_placed = false;
                    updateWorld();
                }
            }

            
            agent.age += 1;
            worlds.updateHeatmap(agent.x,agent.y);
            actionsString.push_back( actionsStr[ active ]) ;

            #ifdef LOCK_SIMULATION
                mtx_1.unlock();
            #endif // LOCK_SIMULATION

            return agent.age;
        }

        // provide debug info
        void display()
        { }

        bool has_failed() { 
            return failed; 
        }

        int return_fitness() { return fitness; }

        // create neural net inputs from sensors
        void generate_neural_inputs(float* inputs, string input_tensor)
        {
            // mtx_1.lock();

            if(!input_tensor.compare("RGB")) {
            for (int x = 0; x < world_width; x++) for (int y = 0; y < world_height; y++) {
                int position = 3 * (( x * world_height ) + y);
                int object = worlds.getCell(x, y);

                for (int colour = 0; colour < 3; colour++)
                {
                    // int fakeValue = ( colour * (world_height * world_width) ) + (( x * world_height ) + y);
                    inputs[position+colour] = (worlds.getRGB(object, colour)); 
                    // inputs[position+colour] = fakeValue; 
                }
            }

            // agent's position
            int position = 3 * ( agent.x * world_height ) + agent.y;
            for (int colour = 0; colour < 3; colour++)
            {
                int color_int = (agent.carrying) ? agent_colour_carrying[colour] : agent_colour[colour];
                float color_float = float(float(color_int)/255.0);
                inputs[position+colour] = (color_float); 
            }


            } else if(!input_tensor.compare("greyscale")) {

                for (int x = 0; x < world_width; x++) for (int y = 0; y < world_height; y++) {
                   int position = ( x * world_height ) + y;
                   int object = worlds.getCell(x, y);

                    inputs[position] = (worlds.getGreyscale(object)); 
                }

                // // agent's position
                int position =  ( agent.x * world_height ) + agent.y;
                float greyscaleLum[] = { 0.2989, 0.587, 0.1140 };
                float greyVal = 0.0;
                for (int c = 0; c < 3; c++) {
                    float col = 0.0;
                    if (agent.carrying)
                    { col = agent_colour_carrying[c]; }
                    else { col = agent_colour[c]; }
                    greyVal += col * greyscaleLum[c];
                }
                inputs[position] = greyVal/255.0; 

            } else if(!input_tensor.compare("objects")) {
                //initalise
                for (int objects = 0; objects < 6; objects++) {
                    for (int x = 0; x < world_width; x++) {
                        for (int y = 0; y < world_height; y++) {
                            int object_pos = ( objects * (world_height * world_width) );
                            int position = object_pos + ( x * world_height ) + y;
                            inputs[position] = 0.0;
                        }
                    }
                }

                // give 1.0 value to each layer where object corresponds 
                for (int x = 0; x < world_width; x++) for (int y = 0; y < world_height; y++) {
                    int object = (worlds.getCell(x, y) - 1);
                    if (object != -1) // if cell is not empty
                    {
                        int object_pos = ( object * (world_height * world_width) );

                        int position = object_pos + ( x * world_height ) + y;
                        inputs[position] = 1.0; 
                    }

                    int agent_pos = (agent.carrying == true) ? 4 : 5;
                    int object_pos = ( agent_pos * (world_height * world_width) );
                    int position = object_pos + ( agent.x * world_height ) + agent.y;
                    inputs[position] = 1.0; 
                }
           
            } else if(!input_tensor.compare("shunting")) {
               // tensor_layers = 1;
            } else {
               assert(true);
            }

             // mtx_1.unlock();

            return;
        }

        // delete animat and dsWorld
        ~Environment()
        {

        }
        
    };
}

#endif
