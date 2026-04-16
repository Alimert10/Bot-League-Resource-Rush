#include "Harta.h"

Caseta::Caseta(): m_tip('0'), m_val(0)
{
}

Caseta::Caseta(char tip, int val): m_tip(tip), m_val(val)
{
}

char Caseta::getTip() const
{
    return m_tip;
}

int Caseta::getVal() const
{
    return m_val;
}

void Caseta::setTip(char tip)
{
    m_tip = tip;
}

void Caseta::setVal(int val)
{
    m_val = val;
}

bool Caseta::resursa() const // verificare daca caseta e tip R
{
    if(m_tip == 'R')
    {
        return true;
    }

    return false;
}

Map::Map(): m_lin(0), m_col(0), m_grid()
{
}

Map::Map(int lin, int col): m_lin(lin), m_col(col) // creare harta prin matrice
{
    m_grid.resize(lin);
        for (int i = 0; i < lin; i++) 
        {
            m_grid[i].resize(col, Caseta());
        }
}

int Map::getLin() const
{
    return m_lin;
}

int Map::getCol() const
{
    return m_col;
}

bool Map::exist(const Poz& poz) const // verificare daca pozitia exista pe harta
{
    int x = poz.getX();
    int y = poz.getY();

    if(x >= 0 && x < m_lin && y >= 0 && y < m_col)
    {
        return true;
    }
    
    return false;
}

const Caseta& Map::getCaseta(const Poz& poz) const 
{
    return m_grid[poz.getX()][poz.getY()];
}

Caseta& Map::getCasetaMod(const Poz& poz) // se poate modifica caseta
{
    return m_grid[poz.getX()][poz.getY()];
}


bool Map::stringToInt(const std::string& s, int& outval) const // transformare string in numar 
{
    if (s.empty())
    {
        return false;
    }

    int val = 0;
    for (int i = 0; i < (int)s.size(); i++)
    {
        char c = s[i];
        if (!(c >= '0' && c <= '9'))
        {
            return false;
        }

        val = val * 10 + (c - '0'); // construire numar
    }

    outval = val;
    return true;
}

bool Map::createCaseta(const std::string& caseta,  Caseta& outcaseta) const
{
    if (caseta == "0" || caseta == "E" || caseta == "W"
       || caseta == "F" || caseta == "J" || caseta == "D" || caseta == "T") 
    {
        outcaseta = Caseta(caseta[0], 0); // se creeaza caseta daca aceasta e de tipurile acceptate in problema
                                          // si e initializata cu 0
        return true;
    }

    int val = 0;
    if (stringToInt(caseta, val))
    {
        if (val >= 1 && val <= 99)
        {
            outcaseta = Caseta('R', val); // se creeaza caseta de tip R
            return true;
        }
        return false;
    }

    return false;
}

bool Map::accesible(const Caseta& caseta) const
{
    char t = caseta.getTip();
    if(t == '0' || t == 'R' || t == 'J' || t == 'D' || t == 'T') // celule acceptate pentru a ajunge la ele
    {
        return true; 
    }

    return false;
}

bool Map::foc(const Caseta& caseta) const // verificare daca , caseta este foc
{
    if(caseta.getTip() == 'F')
    {
        return true;
    }

    return false;
}

bool Map::miscareValida(const Poz& poz1, const Poz& poz2, bool jump) const
{
    if (!exist(poz2)) 
    {
        return false;
    }

    int dx = std::abs(poz2.getX() - poz1.getX());
    int dy = std::abs(poz2.getY() - poz1.getY());
    int distanta = dx + dy;
    const Caseta& dest = getCaseta(poz2);

    if (foc(dest)) // interzis sa ajungi la foc
    {
        return false;
    }

    if (distanta == 1) // pas normal
    {
        return accesible(dest);
    }

    if (jump && distanta == 2 && (dx == 0 || dy == 0)) // pas de 2 salturi daca ai jump
    {
        int mijX = (poz1.getX() + poz2.getX()) / 2;
        int mijY = (poz1.getY() + poz2.getY()) / 2;
        
        if (foc(getCaseta(Poz(mijX, mijY)))) // daca celula din mijloc e foc nu avem voie
        {
            return false;
        }

        return accesible(dest);
    }

    return false;
}
