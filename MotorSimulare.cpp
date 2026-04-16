#include "MotorSimulare.h"

Motor::Motor() {}

void Motor::curatareHarta(Map& map, const Poz& poz)
{
    Caseta& c = map.getCasetaMod(poz);
    char t = c.getTip();
    if (t == 'R' || t == 'J' || t == 'D' || t == 'T') // verificare tip caseta
    {
        c.setTip('0');
        c.setVal(0); // facem 0 daca e R J D T - dispare
    }
}

void Motor::procesareTick(Simulare& sim, Strategie& s, int tick, bool enemyMoved, const Poz& enemyPoz, std::ostream& out)
{
    sim.setTick(tick);
    if (enemyMoved) // daca adversarul se misca
    {
        sim.setEnemyPoz(enemyPoz); // salvare in noua pozitie
        curatareHarta(sim.getMap(), enemyPoz);
    }

    Comanda com = s.decide(sim); // aplicam strategia cu deciderea daca move sau wait
    if (com.wait())
    { 
        out << "WAIT\n";
    }
    else 
    {
        out << "MOVE " << com.getTarget().getX() << " " << com.getTarget().getY() << "\n";
    }

    if (com.move()) // daca jucatorul se misca
    {
        sim.getMe().setPoz(com.getTarget());
        aplicareSuperputere(sim, com.getTarget()); 
    }
}

void Motor::aplicareSuperputere(Simulare& sim, const Poz& poz)
{
    Caseta& c = sim.getMap().getCasetaMod(poz);
    char t = c.getTip();
    if (t == 'R') 
    {
        sim.getMe().addScor(c.getVal() * sim.getMe().getMultiplier()); // resursa * multiplicator
    }
    else if (t == 'J') 
    {
        sim.getMe().enableJump(); // activare jump
    }
    else if (t == 'D') 
    {
        sim.getMe().multiply(2); // dublare multiplicator
    }
    else if (t == 'T') 
    {
        sim.getMe().multiply(3); // triplare multiplicator
    }
    
    if (t != '0' && t != 'F' && t != 'W') // daca nu e deja 0 sau F sau W
    {
        c.setTip('0');
        c.setVal(0); // stergem caseta
    }
}