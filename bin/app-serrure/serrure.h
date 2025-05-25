#ifndef SERRURE_H
#define SERRURE_H

#include <QObject>

#include "../rasp-io-libs/src/gpiodev.h"

#include "centrenotifications.h"

class Serrure : public QObject
{
    Q_OBJECT
public:
    explicit Serrure(QObject *parent = nullptr);
    void deverouiller();

private:
    CentreNotifications _centreNotifs;
    GpioDev _gpioSerrure;

signals:

private slots:
    void onsigCentreNotificationsReady();
    void onSigDeverouillage();
};

#endif // SERRURE_H
