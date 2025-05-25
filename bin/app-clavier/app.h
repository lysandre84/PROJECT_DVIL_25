#ifndef APP_H
#define APP_H

#include <QObject>
#include <QTimer>
#include <QNetworkAccessManager>

#include "centrenotifications.h"
#include "clavier.h"

class App : public QObject
{
    Q_OBJECT
public:
    explicit App(QObject *parent = nullptr);
    ~App();

    void run();

private:
    Clavier _clavierMatriciel;
    QTimer _timer;
    CentreNotifications _centreNotifs;

    QNetworkAccessManager _manager;     // Pour les requêtes HTTP POST

    QString _dernierCodeLu;

    const QString CODE_PAS_PRET = "----";

signals:

private slots:
    void onsigCentreNotificationsReady();
    void onTimerTimeOut();
};

#endif // APP_H
