#pragma once

#include "Simulare.h"
#include "Strategie.h"
#include "Comanda.h"

#include <iostream>

class Motor // executie simulare
{
public:
    Motor();
    void procesareTick(Simulare& sim, Strategie& s, int tick,
                       bool enemyMoved, const Poz& enemyPoz, std::ostream& out);            
    void aplicareSuperputere(Simulare& sim, const Poz& poz);
    void curatareHarta(Map& map, const Poz& poz);
};
