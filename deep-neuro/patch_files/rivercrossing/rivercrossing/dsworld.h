#ifndef DSWORLD_H
#define DSWORLD_H

#include <iostream>
#include <vector>

#include "tools/random.h"
#include "tools/defines.h"

using namespace std;

class dsWorld {
private:
  int river = 0;
  void build(int riverWidth);
  double heatmap[world::x][world::y];

public:
  dsWorld();
  dsWorld(int riverWidth);
  dsWorld(int riverWidth, int seed);
  int cell[world::x][world::y];
  int getCell(int x, int y) { return cell[x][y]; };
  int getRiverWidth() { return river; };

  double getIota(vector<double> iota, int x, int y, bool isObject = false);
  void getRGB(int object, vector<float> &RGB);
  float getRGB(int object, int colour);
  float getGreyscale(int object);

  void printAnimat(int location_x, int location_y);
  void print() { printAnimat(-1,-1); }

  void updateHeatmap(int x, int y) { heatmap[x][y]+=0.1; };
  void printHeatmap();

};

#endif // DSWORLD_H
