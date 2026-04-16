#pragma once

#include "Simulare.h"
#include "Pozitie.h"

#include <vector>

class Drum
{
private:
    std::vector<std::vector<int>> m_distNoJump; // distanta minima pana la final fara jump
    std::vector<std::vector<int>> m_distWithJump; //distanta minima pana la final cu jump

public:
    Drum();

    void calc(const Simulare& sim);
    int getDistNoJump(const Poz& Poz) const;
    int getDistWithJump(const Poz& Poz) const;
    Poz pasUrmator(const Simulare& sim, const Poz& start,
                   bool hasJump, bool& gasit) const;
    void calcDist(const Simulare& sim, bool hasJump,
                  std::vector<std::vector<int>>& dist);
    bool PozValid(const Poz& p, const std::vector<std::vector<int>>& m) const;
};
