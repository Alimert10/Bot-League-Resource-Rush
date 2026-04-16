#pragma once

#include "Pozitie.h"

#include <string>
#include <vector>

class Caseta
{
private:
    char m_tip; // ce e in celula (0, R, T, D, J, W, F, E)
    int  m_val; // valoarea resursei R (0, ... , 99)
    
public:
    Caseta();
    Caseta(char tip, int val);

    char getTip() const;
    int getVal() const;

    void setTip(char tip);
    void setVal(int val);

    bool resursa() const;
};

class Map
{
private:
    int m_lin;
    int m_col;
    std::vector<std::vector<Caseta>> m_grid;

public:
    Map();
    Map(int lin, int col);
    int getLin() const;
    int getCol() const;
    bool exist(const Poz& poz) const;
    const Caseta& getCaseta(const Poz& poz) const;
    Caseta& getCasetaMod(const Poz& poz);
    bool createCaseta(const std::string& caseta, Caseta& outCaseta) const;
    bool accesible(const Caseta& caseta) const;
    bool foc(const Caseta& caseta) const;
    bool stringToInt(const std::string& s, int& outVal) const;
    bool miscareValida(const Poz& poz1, const Poz& poz2, bool areJump) const;
};
