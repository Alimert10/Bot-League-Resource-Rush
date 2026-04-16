#include "Drum.h"

#include "Harta.h"

#include <queue>
#include <cmath>

Drum::Drum() : m_distNoJump(), m_distWithJump()
{
}

void Drum::calc(const Simulare &sim) // calculare distante
{
    calcDist(sim, false, m_distNoJump);
    calcDist(sim, true, m_distWithJump);
}

int Drum::getDistNoJump(const Poz &p) const
{
    return m_distNoJump[p.getX()][p.getY()];
}

int Drum::getDistWithJump(const Poz &p) const
{
    return m_distWithJump[p.getX()][p.getY()];
}

bool Drum::PozValid(const Poz &p, const std::vector<std::vector<int>> &m) const // verificare daca coordonatele se afla in matrice
{
    if (p.getX() >= 0 && p.getX() < (int)m.size() && p.getY() >= 0 && p.getY() < (int)m[0].size())
        return true;

    return false;
}

void Drum::calcDist(const Simulare &sim, bool hasJump, // aplicam BFS de la final pentru a calcula distanta
                    std::vector<std::vector<int>> &dist)
{
    int lin = sim.getMap().getLin();
    int col = sim.getMap().getCol();

    dist.clear(); // stergere matrice veche
    dist.resize(lin);

    for (int i = 0; i < lin; i++)
    {
        dist[i].resize(col);
        for (int j = 0; j < col; j++)
        {
            dist[i][j] = -1; // pentru a nu fi accesibil
        }
    }

    std::queue<Poz> q; // coada BFS

    // incepere de la final

    Poz finalPoz = sim.getFinalPoz();
    dist[finalPoz.getX()][finalPoz.getY()] = 0;
    q.push(finalPoz);

    int dx1[4] = {-1, 1, 0, 0}; // directii (sus, jos, stanga, dreapta)
    int dy1[4] = {0, 0, -1, 1};

    while (!q.empty())
    {
        Poz cur = q.front();
        q.pop(); // scoatere celula curenta din coada

        int curD = dist[cur.getX()][cur.getY()]; // distanta celulei curente pana la final

        for (int k = 0; k < 4; k++) // aflare cine poate ajunge in celula curenta
        {
            Poz v1(cur.getX() + dx1[k], cur.getY() + dy1[k]); // fara jump

            if (sim.getMap().exist(v1))
            {
                if (dist[v1.getX()][v1.getY()] == -1)
                {
                    if (sim.getMap().miscareValida(v1, cur, hasJump))
                    {
                        dist[v1.getX()][v1.getY()] = curD + 1;
                        q.push(v1);
                    }
                }
            }

            if (hasJump)
            {
                Poz v2(cur.getX() + 2 * dx1[k], cur.getY() + 2 * dy1[k]); // cu jump

                if (sim.getMap().exist(v2))
                {
                    if (dist[v2.getX()][v2.getY()] == -1)
                    {
                        if (sim.getMap().miscareValida(v2, cur, true))
                        {
                            dist[v2.getX()][v2.getY()] = curD + 1;
                            q.push(v2);
                        }
                    }
                }
            }
        }
    }
}

// alegere pasul urmator pentru a scadea distanta

Poz Drum::pasUrmator(const Simulare &sim, const Poz &start, bool jump, bool &gasit) const
{
    gasit = false;                                    // presupunere ca nu am gasit pas potrivit
    const std::vector<std::vector<int>> *m = nullptr; // matrice de distante
    if (jump)
        m = &m_distWithJump;
    else
        m = &m_distNoJump;

    if (m->empty())
        return start;

    int x = start.getX();
    int y = start.getY();
    if ((*m)[x][y] == -1) // ramanere pe loc
        return start;

    int distBuna = (*m)[x][y];
    Poz pasOptim = start;

    int dx[] = {-1, 1, 0, 0}; // directii (sus, jos, stanga, dreapta)
    int dy[] = {0, 0, -1, 1};

    for (int i = 0; i < 4; i++)
    {
        Poz n1(x + dx[i], y + dy[i]); // construire vecin
        if (sim.getMap().miscareValida(start, n1, jump))
        {
            int d = (*m)[n1.getX()][n1.getY()];
            if (d != -1 && d < distBuna) // daca scade distanta pana la final devine mai buna si o aleg
            {
                distBuna = d;
                pasOptim = n1;
                gasit = true;
            }
        }
        if (jump) // cu jump
        {
            Poz n2(x + 2 * dx[i], y + 2 * dy[i]);
            if (sim.getMap().miscareValida(start, n2, true))
            {
                int d = (*m)[n2.getX()][n2.getY()];
                if (d != -1 && d < distBuna)
                {
                    distBuna = d;
                    pasOptim = n2;
                    gasit = true;
                }
            }
        }
    }
    return pasOptim;
}
