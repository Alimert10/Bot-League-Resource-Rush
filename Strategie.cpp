#include "Strategie.h"

#include <queue>
#include <vector>

Strategie::Strategie() : m_Drum()
{
}

void Strategie::init(const Simulare &sim)
{
    m_Drum.calc(sim); // calculare distante pana la final
}

int Strategie::deplasare(const Poz &a, const Poz &b) const
{
    int difx = std::abs(a.getX() - b.getX());
    int dify = std::abs(a.getY() - b.getY());

    return difx + dify;
}

// verificare daca mutarea e posibila
Comanda Strategie::safeMoveOrWait(const Simulare &sim, const Poz &poz1, const Poz &poz2) const 
{
    int dist = deplasare(poz1, poz2);

    if (!sim.getMe().jump()) // fara jump
    {
        if (dist != 1)
        {
            return Comanda(); // wait
        }
    }
    else
    {
        if (dist == 1 || dist == 2) // cu jump
        {
            return Comanda(); // wait
        }
    }

    return Comanda(poz2); // move
}

// verificare daca mutarea e periculoasa adica daca e adversarul in apropiere
bool Strategie::risk(const Simulare &sim, const Poz &target) const
{
    const Poz &inamic = sim.getEnemyPoz();

    int distInamic = deplasare(inamic, target);

    if (distInamic <= 2) // daca adversarul e la distanta mai mica de 2 pasi
        return true;     // e periculos, deoarece poate ajunge pe caseta si se poate pierde resursa

    return false;
}

int Strategie::getDistFinal(const Simulare &sim, const Poz &Poz) const 
{
    if (sim.getMe().jump())
    {
        return m_Drum.getDistWithJump(Poz);
    }

    return m_Drum.getDistNoJump(Poz);
}

int Strategie::punctajCaseta(const Simulare &sim, const Poz &Poz) const
{
    const Caseta &c = sim.getMap().getCaseta(Poz);
    int scor = 0, multiplicator = 1;

    if (c.getTip() == 'R')
    {
        scor = c.getVal();
        multiplicator = sim.getMe().getMultiplier(); 
    }

    return scor * multiplicator;
}

bool Strategie::casetaUtila(const Simulare &sim, const Poz &Poz) const
{
    const Caseta &c = sim.getMap().getCaseta(Poz);
    char tip = c.getTip();

    if (tip == 'R' || tip == 'D' || tip == 'T')
        return true;

    if (tip == 'J' && !sim.getMe().jump())
        return true;

    return false;
}

Comanda Strategie::decide(const Simulare &sim) // decidere mutare la fiecare tick (baza strategiei)
{
    Poz juc = sim.getMe().getPoz();
    if (juc == sim.getFinalPoz()) // daca jucatorul e deja la final
    {
        return Comanda(); // wait
    } 

    m_Drum.calc(sim); // recalculare distante
    int distFinal = getDistFinal(sim, juc);

    if (distFinal == -1) // daca nu se poate ajunge la caseta finala
    {
        if (sim.getMe().jump()) // cautare jump
        {
            return Comanda();
        }
        // aplicare bfs pentru a gasi cel mai bun J
        int lin = sim.getMap().getLin();
        int col = sim.getMap().getCol();

        std::vector<std::vector<int>> d1(lin, std::vector<int>(col, -1)); // nr min de pasi
        std::vector<std::vector<Poz>> prev2(lin, std::vector<Poz>(col, Poz(-1, -1))); // pozitia anterioara
        std::queue<Poz> q;

        d1[juc.getX()][juc.getY()] = 0;
        q.push(juc); // adaugare jucator in coada

        Poz bestJump(-1, -1);
        int pasiJump = 0;
        bool jumpRisk = true; // jump riscant (adversarul e apropiat)
 
        while (!q.empty())
        {
            Poz curent = q.front();
            q.pop();
            if (sim.getMap().getCaseta(curent).getTip() == 'J') // pozitia curenta e J
            {
                bool risc = risk(sim, curent);
                int pasi = d1[curent.getX()][curent.getY()];
                // verificare daca nu s-a gasit un j pana acum sau e mai aproape si nu e riscant
                if (bestJump.getX() == -1 || pasi < pasiJump || (pasi == pasiJump && jumpRisk && !risc)) 
                {
                    bestJump = curent; // actualizare cel mai bun J
                    pasiJump = pasi; 
                    jumpRisk = risc;
                }
            }

            int dx[] = {-1, 1, 0, 0}; // directii (sus, jos, stanga dreapta)
            int dy[] = {0, 0, -1, 1};
            for (int i = 0; i < 4; i++)
            {
                Poz v(curent.getX() + dx[i], curent.getY() + dy[i]); // vecin
                if (sim.getMap().exist(v) && d1[v.getX()][v.getY()] == -1 // verificare daca exista pe harta
                && sim.getMap().miscareValida(curent, v, sim.getMe().jump())) // a fost vizitat sau mutarea e posibila
                {
                    d1[v.getX()][v.getY()] = d1[curent.getX()][curent.getY()] + 1;
                    prev2[v.getX()][v.getY()] = curent;
                    q.push(v);
                }
            }
        }

        if (bestJump.getX() != -1) // daca am gasit un J mai bun reconstruim drumul pana la el
        {
            Poz pas = bestJump;
            while (!(prev2[pas.getX()][pas.getY()] == juc))
            {
                pas = prev2[pas.getX()][pas.getY()];
            }
            return Comanda(pas);
        }
        return Comanda();
    }

    int rundeRamase = sim.getMaxRounds() - sim.getTick() + 1;
    if (rundeRamase - distFinal <= 0) // daca am ajuns la final nu se mai culege nimic si se merge direct acolo
    {
        bool ok = false;
        Poz pasFinal = m_Drum.pasUrmator(sim, juc, sim.getMe().jump(), ok);

        if (ok)
        {
            return Comanda(pasFinal);
        }
        else
        {
            return Comanda();
        }
    }

    int R = sim.getMap().getLin(); 
    int C = sim.getMap().getCol();
    std::vector<std::vector<int>> d2(R, std::vector<int>(C, -1));
    std::vector<std::vector<Poz>> p2(R, std::vector<Poz>(C, Poz(-1, -1)));
    std::queue<Poz> q2;

    d2[juc.getX()][juc.getY()] = 0;
    q2.push(juc);

    Poz bestTarget = juc; // caseta cea mai buna, initial fiind jucatorul
    bool gasit = false;
    int scorMaxim = -1; // cel mai bun scor la o resursa

    while (!q2.empty())
    {
        Poz curent = q2.front();
        q2.pop();
        int stepsCur = d2[curent.getX()][curent.getY()]; // nr pasi pentru a ajunge la caseta scoasa

        if (stepsCur >= rundeRamase) 
            continue;

        int df = getDistFinal(sim, curent); // distanta minima din caseta curenta la final
        if (df != -1 && (stepsCur + df <= rundeRamase))
        {
            if (casetaUtila(sim, curent))
            {
                bool res = (sim.getMap().getCaseta(curent).getTip() == 'R'); 

                int scorCur;
                if (res)
                {
                    scorCur = punctajCaseta(sim, curent); // daca e resursa se calculeaza scorul
                }
                else
                {
                    scorCur = 0;
                }
                
                bool better = false;
                if (res)
                {
                    if (scorCur > scorMaxim)
                        better = true;
                }

                if (better)
                {
                    gasit = true;
                    bestTarget = curent;
                    scorMaxim = scorCur;
                }
            }
        }

        int dx[] = {-1, 1, 0, 0};
        int dy[] = {0, 0, -1, 1};
        for (int i = 0; i < 4; i++)
        {
            Poz v1(curent.getX() + dx[i], curent.getY() + dy[i]); // vecin fara jumo
            if (sim.getMap().exist(v1))
            {
                if (d2[v1.getX()][v1.getY()] == -1)
                {
                    if (sim.getMap().miscareValida(curent, v1, sim.getMe().jump()))
                    {
                        d2[v1.getX()][v1.getY()] = stepsCur + 1;
                        p2[v1.getX()][v1.getY()] = curent;
                        q2.push(v1);
                    }
                }
            }
            if (sim.getMe().jump())
            {
                Poz v2(curent.getX() + 2 * dx[i], curent.getY() + 2 * dy[i]); // vecin cu jump
                if (sim.getMap().exist(v2))
                {
                    if (d2[v2.getX()][v2.getY()] == -1)
                    {
                        if (sim.getMap().miscareValida(curent, v2, sim.getMe().jump()))
                        {
                            d2[v2.getX()][v2.getY()] = stepsCur + 1;
                            p2[v2.getX()][v2.getY()] = curent;
                            q2.push(v2);
                        }
                    }
                }
            }
        }

        if (gasit && !(bestTarget == juc)) // daca am gasit o resursa utila merg spre ea
        {
            Poz p = bestTarget;
            while (!(p2[p.getX()][p.getY()] == juc))
            {
                p = p2[p.getX()][p.getY()];
            }
            return Comanda(p);
        }
    }
    // daca nu am gasit nimic, merg direct la final
    bool ok2 = false;
    Poz pasF = m_Drum.pasUrmator(sim, juc, sim.getMe().jump(), ok2);

    if (ok2)
    {
        return Comanda(pasF);
    }
    else
    {
        return Comanda();
    }
}