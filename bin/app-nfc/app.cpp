#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>
#include <QUrl>
#include <QDebug>

#include "app.h"

App::App(QObject *parent)
    : QObject{parent}
{
    // Init centre de notifications
    connect(&_centreNotifs, &CentreNotifications::sigReady, this, &App::onsigCentreNotificationsReady);

    // Init NFC
    _nfcWorkerThread = new QThread();
    _worker = new NFCWorker();
    _worker->moveToThread(_nfcWorkerThread);

    connect(_nfcWorkerThread, &QThread::started, _worker, &NFCWorker::setup);
    connect(_worker, &NFCWorker::nfcDetected, this, &App::onNfcDetected);
    connect(_worker, &NFCWorker::nfcRemoved, this, &App::onNfcRemoved);
    connect(_worker, &NFCWorker::nfcError, this, &App::onNfcError);
    
    _nfcWorkerThread->start();
}

App::~App()
{
    _nfcWorkerThread->requestInterruption();
    _nfcWorkerThread->quit();
    _nfcWorkerThread->wait();
    delete _worker;
}

void App::run()
{
    // Rien à faire d'autre : tout est orchestré par des signaux/slots Qt
}


void App::onsigCentreNotificationsReady()
{
    qDebug() << "Connecté au broker";
}

void App::onTimerTimeOut()
{
    bool isOK = true;
    if ( isOK ) {
        QJsonObject jObj = {
            {"badge", "UID"}
            , {"isOK", true}
        };
        _centreNotifs.publier(CentreNotifications::CODE_NFC, jObj);
    } else {
        QJsonObject jObj = {
            {"badge", "UID"}
            , {"isOK", false}
        };
        _centreNotifs.publier(CentreNotifications::CODE_NFC, jObj);
    }
}

void App::onNfcError(const QString &msg)
{
    qWarning() << "Erreur NFC : " << msg;
}

void App::onNfcDetected(const QString &uid)
{
    qInfo() << "Badge détecté : " << uid;

    QJsonObject jObj =  {
        {"tagUID", uid},    };

    _centreNotifs.publier(CentreNotifications::CODE_NFC, jObj);

    onBadgeNfcLu(uid);
}


void App::onNfcRemoved()
{
    qInfo() << "Badge retiré";
}

void App::onBadgeNfcLu(QString nfc_uid) {
    qDebug() << "[DEBUG][NFC] Badge lu, UID: " << nfc_uid;

    QNetworkRequest request(QUrl("http://localhost:5000/verify_nfc"));
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    QJsonObject json;
    json["nfc_code"] = nfc_uid;

    QNetworkReply* reply = _manager.post(request, QJsonDocument(json).toJson());

    connect(reply, &QNetworkReply::finished, this, [=]() {
        QByteArray response_data = reply->readAll();
        QJsonDocument json_doc = QJsonDocument::fromJson(response_data);
        bool authorized = json_doc.object().value("authorized").toBool();
        QString username = json_doc.object().value("username").toString();

        if (authorized) {
            qDebug() << "[NFC] Déverrouillage réussi, utilisateur: " << username;
            _centreNotifs.publier(CentreNotifications::SERRURE, "deverouillage");
        } else {
            qDebug() << "[NFC] Badge inconnu";
        }
        reply->deleteLater();
    });
}
