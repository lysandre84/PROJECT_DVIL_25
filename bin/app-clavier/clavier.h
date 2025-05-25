#ifndef CLAVIER_H
#define CLAVIER_H

#include <QObject>
#include <QTimer>

#include "../rasp-io-libs/src/i2cdev.h"

#include "centrenotifications.h"

class Clavier : public QObject
{
    Q_OBJECT
public:
    typedef enum {OK, NOK} status_t;
    explicit Clavier(QObject *parent = nullptr);
    bool lireCode(QString& code);
    void signalerEtat(status_t etat);

private:

    std::shared_ptr<I2cDev> _clavier;

    const int ADR_I2C_CLAVIER = 0x09;
    const int TAILLE_CODE_CLAVIER = 4;

signals:

};

#endif // CLAVIER_H
