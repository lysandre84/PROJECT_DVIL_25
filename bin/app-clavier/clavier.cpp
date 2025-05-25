#include "QThread"

#include "clavier.h"

Clavier::Clavier(QObject *parent)
    : QObject{parent}
{
    _clavier = I2cDev::getInstance(1);

}

bool Clavier::lireCode(QString& code)
{
    uint8_t rBuf[ TAILLE_CODE_CLAVIER+1 ];

    _clavier->read(ADR_I2C_CLAVIER, rBuf, TAILLE_CODE_CLAVIER);

    // Tester si les caractères reçus sont soit des chiffres soit des '-'
    bool isOK = true;
    for(int i = 0; i < TAILLE_CODE_CLAVIER; i++) {
        if (!isdigit(rBuf[ i ]) && (rBuf[ i ] != '-')) {
           isOK = false;
           break;
        } else {
            code.append(rBuf[ i ]);
        }
    }

    return isOK;
}

void Clavier::signalerEtat(status_t etat)
{
    uint8_t tBuf[1];

    if( etat == OK) {
        tBuf[ 0 ] = '#';
    } else {
        tBuf[ 0 ] = '!';

    }
    _clavier->write(0x09, tBuf, 1);

}

