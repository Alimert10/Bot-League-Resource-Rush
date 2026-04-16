# Tema 3 - Liga Botilor

Nume : Ozdemir Ali Mert
Grupa : 334AB

# Descrierea programului

Tema presupune construirea unui motor de simulare pentru jocul "Liga Botilor", un joc in care se colecteaza resurse pe o harta rectangulara cu obstacole si power-upuri.
Programul implementat primeste ca input toate detaliile despre harta, apoi la fiecare runda actiunea adversarului. Dupa fiecare tick programul decide ce comanda sa afiseze, unde in cazul nostru avem MOVE si WAIT, cu conditia ca acea comanda sa respecte regulile jocului.

Scopul jocului este sosirea la pozitia finala in timp util si obtinerea unui scor cat mai mare din resursele colectate.

# Structura codului

Codul este impartit in mai multe fisiere header si .cpp :

# Pozitie .h / .cpp

Clasa **Pozitie** retine coordonatele unei pozitii de pe harta, unde x reprezinta linia, iar y coloana

Este utilizata pentru :

- pozitia jucatorului si a adversarului
- calcularea deplasarilor si a distantelor
- pozitia finala

# Harta .h / .cpp

Clasa **Map** are rol in reprezentarea hartii jocului. Aceasta contine matricea de casete si dimensiunile acesteia.
In clasa **Map** se regasesc metode pentru :

- verificarea existentei unei pozitii pe harta
- verificarea daca o miscare este posibila sau nu
- accesarea si modificarea unei casete

Clasa **Caseta** se ocupa de gestionarea hartii jocului. Aceasta descrie o singura celula din harta si stocheaza tipul celulei (0, R, W, E, D, T, F, J) si valoarea resursei daca este de tip R.

# Jucator .h / .cpp

Clasa **Jucator** descrie toate informatiile necesare despre jucator :

- pozitia curenta pe harta
- scorul acumulat
- daca are Jump activat sau nu
- multiplicatorul activ

# Simulare .h / .cpp

Clasa **Simulare** contine starea jocului, pastreaza si actualizeaza datele jocului :

- harta
- pozitia jucatorului si a adversarului
- pozitia finala
- scorul si mutilplicatorii
- numarul maxim de runde si tick-ul curent

# ProcesareDate .h / .cpp

Clasa **Procesare** citeste inputul 

- citeste datele initiale ale arenei
- citeste fiecare linie din Tick
- proceseaza datele primite

# Comanda .h / .cpp

Clasa **Comanda** reprezinta actiunea facuta de fiecare jucator la un tick.

Comanda poate fi **MOVE** sau **WAIT**.
De asemenea, retine pozitia pe care se vrea sa se ajunga pentru comanda **MOVE**, si genereaza outputul corect pentru cele 2 mutari.

# Drum .h / .cpp

Clasa **Drum** ajuta la planificarea strategiei prin :

- calcularea distantelor minime pana la final folosind algoritmul BFS
- determinarea urmatorului pas optim
- tratarea separata a mutarilor cu JUMP sau fara JUMP

# Strategie .h / .cpp

Clasa **Strategie** este responsabila de gestionarea strategiei de joc, adica prin alegerea mutarii la fiecare tick al jocului.
Aceasta analizeaza starea curenta a simularii si, prin *functia decide*, decide ce miscare sa faca ( **MOVE** sau **WAIT**) in functie de : 

- starea curenta a jocului
- pozitia jucatorului, a adversarului
- harta
- runde ramase

**Functionalitatea deciziei**

Decizia de a face **MOVE** sau **WAIT** se realizeaza astfel :

a) Daca jucatorul este deja la pozitia finala, se returneaza **WAIT**
b) Se determina distanta minima pana la final, tinand cont daca jucatorul are **JUMP** activat sau nu
c) Se verifica numarul rundelor ramase si daca se constata ca nu mai sunt suficiente, strategia favorizeaza deplasarea directa la punctul final pentru a putea trece toate testele
d) Se parcurge harta folosind algoritmul BFS si se identifica resurse si superputeri care pot fi colectate in timp util
e) Pentru fiecare miscare se evalueaza riscul de intalnire a jucatorului cu adversarului, pentru a nu ajunge pe o caseta unde resursa a fost colectata de acesta deja.
f) Se determina cea mai buna mutare si se realizeaza pe baza scorului potential, riscului de intalnire cu adversarul, numarului de pasi precum si distanta pana la punctul final

Daca nu exista dupa parcurgerea acestor pasi o mutare utila, functia returneaza comanda **WAIT**.

# MotorSimulare .h / .cpp

Clasa **Motor**:
- gestioneaza executarea tuturor tick-urilor
- actualizeaza pozitia adversarului, curata harta (caseta devine 0) dupa mutarile adversarului
- aplica efectele mutarii
- se foloseste de strategie pentru urmatoarea mutare
- afiseaza comanda in output

# main.cpp

Fisierul **main.cpp** coordoneaza executia jocului.

- citeste configuratia initiala a arenei utilizandu-se de *ProcesareDate*
- initializeaza strategia de joc
- intra intr-o bucla care proceseaza jocul la fiecare tick

La fiecare tick se citeste actiunea adversarului, iar motorul de simulare actualizeaza starea jocului. Apoi, strategia decide urmatoarea mutare si se afiseaza mutarea aleasa **MOVE** sau **WAIT**.

