#pragma once

#include "Pozitie.h"

class Jucator
{
private:
    Poz m_poz;
    int m_scor;
    bool m_jump;
    int m_multiplier;
    
public:
    Jucator();
    Jucator(const Poz& poz);
    const Poz& getPoz() const;
    void setPoz(const Poz& poz);
    int getScor() const;
    void addScor(int s);
    bool jump() const;
    void enableJump();
    int getMultiplier() const;
    void multiply(int m);
};
