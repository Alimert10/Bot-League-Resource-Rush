#pragma once

#include "Pozitie.h"

#include <string>

class Comanda
{
private:
    char m_tip;     
    Poz m_target; // destinatia (cand avem MOVE)   

public:
    Comanda();                 
    Comanda(const Poz& target); 
    bool wait() const;
    bool move() const;
    const Poz& getTarget() const;
    std::string outString() const;  
};
