#pragma once

#include "Simulare.h"
#include "Pozitie.h"

#include <string>

class Procesare
{
public:
    Procesare();
    bool procesareArena(Simulare& s);
    bool readNextTick(int& outTick, bool& outEnemyMove, Poz& outEnemyPoz);
    bool readLinie(std::string& l);
    bool procesareInt(const std::string& s, int& val);
    bool splitCuv(const std::string& l, std::string cuv[], int& nr, int max);
};
