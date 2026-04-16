#include "ProcesareDate.h"
#include "Strategie.h"
#include "MotorSimulare.h"

#include <iostream>
#include <string>

int main()
{
    Simulare sim;
    Procesare p;
    Strategie s;
    Motor motor;
    std::string error;

    if (!p.procesareArena(sim)) // citire arena
    {
        std::cerr << error << "\n";
        return 0;
    }

    s.init(sim); // pregatire strategie

    int tick;
    bool enemyMoved;
    Poz enemyPoz(0, 0); // initializare pozitie adversar

    while (p.readNextTick(tick, enemyMoved, enemyPoz)) // citire ticuri
    {
        motor.procesareTick(sim, s, tick, enemyMoved, enemyPoz, std::cout); // realizeaza toata executia simularii 
    }

    return 0;
}
