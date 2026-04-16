#pragma once

#include "Jucator.h"
#include "Harta.h"
#include "Pozitie.h"

class Simulare // stare simulare
{
private:
    int m_maxRounds;
    int m_tick;
    Map m_map;
    Poz m_finalPoz; // pozitia finala
    Poz m_enemyPoz; // pozitia adversarului
    Jucator m_me; // jucatorul
    
public:
    Simulare();
    Simulare(int maxRounds, const Map& map, const Poz& myStart,
             const Poz& enemyStart, const Poz& finalPoz);
    int getMaxRounds() const;
    int getTick() const;
    void setTick(int tick);
    const Map& getMap() const;
    Map& getMap();
    const Poz& getFinalPoz() const;
    const Jucator& getMe() const;
    Jucator& getMe();
    const Poz& getEnemyPoz() const;
    void setEnemyPoz(const Poz& poz);
};
