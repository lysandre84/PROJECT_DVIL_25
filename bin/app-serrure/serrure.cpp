#include "QThread"

#include "serrure.h"

Serrure::Serrure(QObject *parent)
    : QObject{parent}, _gpioSerrure(17, GpioDev::mode_t::OUTPUT_PUSHPULL, false)
{
    connect(&_centreNotifs, &CentreNotifications::sigReady, this, &Serrure::onsigCentreNotificationsReady);
    connect(&_centreNotifs, &CentreNotifications::sigDeverouillage, this, &Serrure::onSigDeverouillage);

}

void Serrure::onsigCentreNotificationsReady()
{
    _centreNotifs.abonner(CentreNotifications::SERRURE);
}

void Serrure::onSigDeverouillage()
{
    qDebug() << "Déverouillage demandé";
    _gpioSerrure.digitalWrite(GpioDev::HIGH);
    QThread::msleep(500);
    _gpioSerrure.digitalWrite(GpioDev::LOW);

}
