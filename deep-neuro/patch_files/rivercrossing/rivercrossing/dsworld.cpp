#include "rivercrossing/dsworld.h"

#include <mutex>
std::mutex w_mutex;  // protects g_i

dsWorld::dsWorld() { build(0); }

dsWorld::dsWorld(int riverWidth) { build(riverWidth); }

dsWorld::dsWorld(int riverWidth, int worldseed) {
  int seed = worldseed + (riverWidth * worldseed);
  randomise(seed);
  build(riverWidth);
}

void dsWorld::build(int riverWidth) {
  int c; 
  int riverPosition = ((world::x / 2) + (((world::x / 2) - 2) / 2));
  float trapRatio  = int((world::x * world::y) * 0.0175);
  float stoneRatio = int((world::x * world::x) * 0.0425) + riverWidth;
  int resourcePos = ( (world::x - 1) - (riverPosition + (riverWidth)) )/2;
  int numTraps = (trapRatio < 1) ? 1 : int(trapRatio);

  // init heatmaps
  for (int x = 0; x < world::x; x++) for (int y = 0; y < world::y; y++) heatmap[x][y] = 0.0;

  // init cells
  for (int x = 0; x < world::x; x++) for (int y = 0; y < world::y; y++) cell[x][y] = EMPTYCELL;
  
  // water
  for (int x = riverPosition; x < riverPosition + (riverWidth); x++) for (int y = 0; y < world::y; y++) cell[x][y] = WATER;

  #ifdef DETERMINISTIC
    w_mutex.lock();
    randomise(123);
  #endif // DETERMINISTIC

  // traps
  for (int n = 0; n < numTraps; n++) {
    int x,y;
    do {
      x = random(world::x);
      y = random(world::y);
      c = cell[x][y];
    } while (c & RESOURCE || c & WATER);
    cell[x][y] = TRAP;
  }

  // place stones
  for (int n = 0; n < stoneRatio; n++) {
    int x,y;
    do {
      x = random(world::x);
      y = random(world::y);
      c = cell[x][y];
    } while (x > riverPosition || c & WATER || c & TRAP);
    cell[x][y] = STONE;
  }

  #ifdef DETERMINISTIC
    w_mutex.unlock();
  #endif // DETERMINISTIC

  // place resouce
  cell[ (world::x-1) - resourcePos ][ int(world::y / 2) ] = RESOURCE;

  // w_mutex.lock();
  //   print();
  // w_mutex.unlock();

}

void dsWorld::printAnimat(int location_x, int location_y) {
  cout << "RIVER CROSSING WORLD: " << endl;
  for (int y = 0; y < world::x; y++) {
    for (int x = 0; x < world::y; x++) {
      if (x == location_x && (y == location_y)) {
          cout << "A";
        } else {
          cout << cell[x][y];
        }
      cout << ",";
    }
    cout << " " << endl;
  }
  cout << " " << endl;
}

double dsWorld::getIota(vector<double> iota, int x, int y, bool isObject) {
    int cell = getCell(x, y);
    double cellIota = iota.at(cell);

    // if using object DN , first input is not used
    if (isObject)
        if (cell == 0) return 0.0;

    return cellIota;
}

void dsWorld::getRGB(int object, vector<float> &RGB) {
    float R,G,B;
    switch(object) {
        case EMPTYCELL :
            R = 0.0;
            G = 0.0;
            B = 0.0;
            break;
        case RESOURCE :
            R = 255.0;
            G = 255.0;
            B = 0.0;
            break;
        case STONE :
            R = 128.0;
            G = 128.0;
            B = 128.0;
            break;
        case WATER :
            R = 0.0;
            G = 128.0;
            B = 255.0;
            break;
        case TRAP :
            R = 255.0;
            G = 0.0;
            B = 0.0;
            break;
    }
    RGB.push_back(R/255.0);
    RGB.push_back(G/255.0);
    RGB.push_back(B/255.0);
}

float dsWorld::getRGB(int object, int colour) {
    vector<float> RGB;
    getRGB(object, RGB);
    return RGB.at(colour);
}

float dsWorld::getGreyscale(int object) {
    float greyscaleLum[] = { 0.2989, 0.587, 0.1140 };
    vector<float> RGB;
    float greyVal = 0.0;
    
    getRGB(object, RGB);
    for (int c = 0; c < RGB.size(); c++)
      greyVal += RGB.at(c) * greyscaleLum[c];

    return greyVal;
}

void dsWorld::printHeatmap() {
  cout << "HEATMAP: " << endl;
  for (int y = 0; y < world::y; y++) {
    for (int x = 0; x < world::x; x++) {
        cout << heatmap[x][y] * 10;
      if (x != world::x-1.0) cout << ",";
    }
    cout << " " << endl;
  }
  cout << " " << endl;

}
