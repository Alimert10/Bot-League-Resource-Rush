#include "Comanda.h"

Comanda::Comanda() : m_tip('W'), m_target(Poz(0, 0)) // WAIT
{
}

Comanda::Comanda(const Poz& target): m_tip('M'), m_target(target) // MOVE
{
}

bool Comanda::wait() const
{
    return m_tip == 'W';
}

bool Comanda::move() const
{
    return m_tip == 'M';
}

const Poz& Comanda::getTarget() const // destinatia comenzii
{
    return m_target;
}

std::string Comanda::outString() const // afisare WAIT sau MOVE x y
{
    if (wait())
    {
        return "WAIT"; // intoarcere WAIT
    }
    
    // construire x si y ca string-uri pentru a putea afisa

    std::string textX = "";
    int valX = m_target.getX();

    if (valX == 0)
    {
        textX = "0";
    }
    else
    {
        while (valX > 0)
        {
            char cifra = (char)('0' + (valX % 10));
            textX = cifra + textX; 
            valX /= 10;
        }
    }

    std::string textY = "";
    int valY = m_target.getY();

    if (valY == 0)
    {
        textY = "0";
    }
    else
    {
        while (valY > 0)
        {
            char cifra = (char)('0' + (valY % 10));
            textY = cifra + textY;
            valY /= 10;
        }
    }
    
    return "MOVE " + textX + " " + textY;
}
