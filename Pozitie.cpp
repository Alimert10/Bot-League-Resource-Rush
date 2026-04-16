#include "Pozitie.h"

Poz::Poz(): m_x(0), m_y(0)
{
}

Poz::Poz(int x, int y): m_x(x), m_y(y)
{
}

int Poz::getX() const
{
    return m_x;
}

int Poz::getY() const
{
    return m_y;
}

void Poz::setX(int x)
{
    m_x = x;
}

void Poz::setY(int y)
{
    m_y = y;
}

bool Poz::operator==(const Poz& other) const
{
    if(m_x == other.m_x && m_y == other.m_y)
    {
        return true;
    }

    return false;
}

bool Poz::operator!=(const Poz& other) const
{
    if(!(*this == other))
    {
        return true;
    }

    return false;
}
