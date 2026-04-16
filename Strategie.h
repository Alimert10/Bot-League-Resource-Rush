#pragma once

#include "Comanda.h"
#include "Simulare.h"
#include "Drum.h"

class Strategie
{
private:
    Drum m_Drum; // harta de distante

public:
    Strategie();
    void init(const Simulare& sim);
    Comanda decide(const Simulare& sim);
    int deplasare(const Poz& a, const Poz& b) const;
    Comanda safeMoveOrWait(const Simulare& sim, const Poz& poz1, const Poz& poz2) const;
    bool risk(const Simulare& sim, const Poz& target) const;
    int getDistFinal(const Simulare& sim, const Poz& Poz) const;
    int punctajCaseta(const Simulare& sim, const Poz& Poz) const;
    bool casetaUtila(const Simulare& sim, const Poz& Poz) const;
};
