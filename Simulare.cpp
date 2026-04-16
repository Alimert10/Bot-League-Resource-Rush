#include "Simulare.h"

Simulare::Simulare(): m_maxRounds(0), m_tick(0),
                      m_map(Map()), m_finalPoz(Poz(0, 0)),
                      m_enemyPoz(Poz(0, 0)), m_me(Jucator())
{
}

Simulare::Simulare(int maxRounds, const Map& map, const Poz& myStart,
                   const Poz& enemyStart, const Poz& finalPoz)
: m_maxRounds(maxRounds), m_tick(0), m_map(map),
  m_finalPoz(finalPoz), m_enemyPoz(enemyStart), m_me(Jucator(myStart))
{
}

int Simulare::getMaxRounds() const
{
    return m_maxRounds;
}

int Simulare::getTick() const
{
    return m_tick;
}

void Simulare::setTick(int tick)
{
    m_tick = tick;
}

const Map& Simulare::getMap() const
{
    return m_map;
}

Map& Simulare::getMap()
{
    return m_map;
}

const Poz& Simulare::getFinalPoz() const
{
    return m_finalPoz;
}

const Jucator& Simulare::getMe() const // citire jucator
{
    return m_me;
}

Jucator& Simulare::getMe() // modificare jucator
{
    return m_me;
}

const Poz& Simulare::getEnemyPoz() const 
{
    return m_enemyPoz;
}

void Simulare::setEnemyPoz(const Poz& poz) 
{
    m_enemyPoz = poz;
}

