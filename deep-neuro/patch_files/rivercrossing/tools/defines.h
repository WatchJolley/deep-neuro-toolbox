#ifndef DEFINES_H
#define DEFINES_H


// #define DETERMINISTIC

// this is used for debugging by only allowing 'update' to run single threaded so
// printed statements still operate
// #define LOCK_SIMULATION 

enum CellContent {
  EMPTYCELL = 0,
  RESOURCE = 1,
  STONE = 2,
  WATER = 3,
  TRAP = 4,
  AGENT = 10
};

namespace world
{
  const int x = 20;
  const int y = 20;
}

#endif // DEFINES_H
