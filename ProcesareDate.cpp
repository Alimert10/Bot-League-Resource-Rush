#include "ProcesareDate.h"
#include "Harta.h"

#include <iostream>

Procesare::Procesare()
{
}

bool Procesare::readLinie(std::string& l) // citire urmatoarea linie valida
{
    while (std::getline(std::cin, l))
    {
        if (!l.empty()) 
            return true;
    }
    return false;
}

bool Procesare::procesareInt(const std::string& s, int& val)
{
    if (s.empty())
    {
        return false;
    }

    val = 0;
    for (int i = 0; i < (int)s.size(); i++)
    {
        char c = s[i];
        if (c < '0' || c > '9')
        {
            return false;
        }
        val = val * 10 + (c - '0');
    }
    
    return true;
}

bool Procesare::splitCuv(const std::string& l, std::string cuv[], int& nr, int max) // impartirea unei linii pe cuvinte
{
    nr = 0;
    std::string tmp = ""; // cuvantul curent
    for (int i = 0; i < (int)l.size(); i++)
    {
        char c = l[i];
        if (c == ' ' || c == '\t') // terminare cuvant
        {
            if (!tmp.empty()) 
            { 
                if (nr < max) 
                {
                    cuv[nr++] = tmp; // adaugare cuvant in vector
                    tmp = "";
                }
            }
        }
        else 
            tmp = tmp + c; // adaugare caracter daca nu e spatiu
    }
    if (!tmp.empty() && nr < max)  
        cuv[nr++] = tmp; // salvare ultimul cuvant

    return true;
}

bool Procesare::procesareArena(Simulare& sim) // citire input pana la "MAP"
{
    std::string line;
    std::string cuv[50];
    int cnt = 0, n = 0, m = 0, rounds = 0;
    int s1 = 0, s2 = 0, s3 = 0, s4 = 0, f1 = 0, f2 = 0;
    
    // citire linia arena

    if (!readLinie(line))
        return false;

    if (!splitCuv(line, cuv, cnt, 50))
        return false;

    if (!procesareInt(cuv[1], n) || !procesareInt(cuv[2], m) || !procesareInt(cuv[3], rounds))
        return false;
    
    // citire start jucator
    
    if (!readLinie(line))
        return false;

    if (!splitCuv(line, cuv, cnt, 50) || cnt != 2)
        return false;

    if (!procesareInt(cuv[0], s1) || !procesareInt(cuv[1], s2))
        return false;

    if (!readLinie(line))
        return false;

    if (!splitCuv(line, cuv, cnt, 50) || cnt != 2)
        return false;

    // citire start adversar

    if (!procesareInt(cuv[0], s3) || !procesareInt(cuv[1], s4))
        return false;

    if (!readLinie(line))
        return false;

    if (!splitCuv(line, cuv, cnt, 50) || cnt != 2)
        return false;
    
    // citire final

    if (!procesareInt(cuv[0], f1) || !procesareInt(cuv[1], f2))
        return false;

    if (!readLinie(line))
        return false;

    Map map(n, m); // creare harta

    for (int i = 0; i < n; i++)
    {
        if (!readLinie(line))
            return false;

        if (!splitCuv(line, cuv, cnt, 50))
            return false;

        if (cnt != m)
            return false;

        for (int j = 0; j < m; j++)
        {
            Caseta caseta;

            if (!map.createCaseta(cuv[j], caseta))
                return false;

            map.getCasetaMod(Poz(i, j)) = caseta;
        }
    }

    if (!readLinie(line)) // citire END_MAP
        return false;

    if (!readLinie(line)) // citire STREAM
        return false;

Poz myStart(s1, s2);
Poz enemyStart(s3, s4);
Poz finalPoz(f1, f2);

sim = Simulare(rounds, map, myStart, enemyStart, finalPoz); // construire simulare
sim.setTick(0);

return true;
}

bool Procesare::readNextTick(int& outTick, bool& outEnemyMove, Poz& outEnemyPoz) // citire tickul urmator WAIT sau MOVE
{
    std::string line;
    std::string cuv[50];
    int cnt = 0, t = 0;

    if (!readLinie(line))
    {
        return false; 
    }

    if (!splitCuv(line, cuv, cnt, 50))
        return false;

    if (!procesareInt(cuv[1], t))
        return false;

    outTick = t;

    if (cuv[2] == "WAIT") // daca adversarul are WAIT nu se va misca
    {
        outEnemyMove = false;
        return true;
    }

    if (cuv[2] == "MOVE") // daca adversarul are MOVE se seteaza pozitia
    {
        int x = 0;
        int y = 0;

        if (!procesareInt(cuv[3], x) || !procesareInt(cuv[4], y))
            return false;

        outEnemyMove = true;
        outEnemyPoz = Poz(x, y);
        return true;
    }
    
    return false;
}

