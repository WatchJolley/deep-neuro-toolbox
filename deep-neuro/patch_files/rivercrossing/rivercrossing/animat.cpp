#include "rivercrossing/animat.h"

#include <mutex>
std::mutex r_mutex;  // protects g_i


animat::animat()
{
  this->age = 0;
  this->x = 1;
  this->carrying = false;

  #ifdef DETERMINISTIC 
  r_mutex.lock();
  	randomise(123);
  	this->y = random( 20 );
  r_mutex.unlock();
  #else 
  	this->y = random( 20 );
  #endif
}
