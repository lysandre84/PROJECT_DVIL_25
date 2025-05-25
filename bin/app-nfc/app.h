#ifndef APP_H
#define APP_H

#include <QObject>
#include <QTimer>
#include <QThread>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>
#include <QUrl>

#include "centrenotifications.h"
#include "nfcworker.h"

class App : public QObject
{
    Q_OBJECT
public:
    void onBadgeNfcLu(QString nfc_uid); 
    explicit App(QObject *parent = nullptr);
    ~App();

    void run();

private :
    QNetworkAccessManager _manager;
    NFCWorker _badgeNFC;
    CentreNotifications _centreNotifs;
    QThread * _nfcWorkerThread;
    NFCWorker* _worker;
    // UIDs des badges qui permettent de déverrouiller la serrure
    const QList<QString> _authorized_uid = {
        "04:9E:BB:AA:A2:48:80"
        , "16:84:2C:02"
	, "73:DE:3E:14"
    };

signals:

private slots:
    void onsigCentreNotificationsReady();
    void onTimerTimeOut();
    void onNfcError(const QString& msg);
    void onNfcDetected(const QString& uid);
    void onNfcRemoved();
};

#endif // APP_H
