#pragma once

class Poz
{

private: // coordonate
    int m_x; // linie
    int m_y; // coloana
    
public:
    Poz();
    Poz(int x, int y);
    int getX() const;
    int getY() const;
    void setX(int x);
    void setY(int y);
    bool operator==(const Poz& other) const;
    bool operator!=(const Poz& other) const;
};
