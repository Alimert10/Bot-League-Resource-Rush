#include "Jucator.h"

Jucator::Jucator(): m_poz(Poz(0, 0)), m_scor(0), 
                    m_jump(false), m_multiplier(1)
{
}

Jucator::Jucator(const Poz& poz): m_poz(poz), m_scor(0), 
                                  m_jump(false), m_multiplier(1)
{
}

const Poz& Jucator::getPoz() const
{
    return m_poz;
}

void Jucator::setPoz(const Poz& poz)
{
    m_poz = poz;
}

int Jucator::getScor() const
{
    return m_scor;
}

void Jucator::addScor(int s) // adaugare punctaj la scor
{
    m_scor = m_scor + s;
}

bool Jucator::jump() const
{
    return m_jump;
}

void Jucator::enableJump() // activare jump
{
    m_jump = true;
}

int Jucator::getMultiplier() const // getter pentru multiplicator
{
    return m_multiplier;
}

void Jucator::multiply(int m) // multiplicare cu 2 (D) sau 3 (T)
{
    m_multiplier = m_multiplier * m;
}
