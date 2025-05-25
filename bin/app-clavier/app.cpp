#include <QJsonObject>
#include <QJsonDocument>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QDebug>

#include "app.h"

App::App(QObject *parent)
    : QObject{parent}, _manager(this)
{
    connect(&_centreNotifs, &CentreNotifications::sigReady, this, &App::onsigCentreNotificationsReady);
    connect(&_timer, &QTimer::timeout, this, &App::onTimerTimeOut);

    _timer.setInterval(500);
    _dernierCodeLu = "";
}

App::~App()
{
}

void App::run()
{
    _timer.start();
    // Tout est orchestré par signaux/slots Qt
}

void App::onsigCentreNotificationsReady()
{
    qDebug() << "Connecté au broker";
}

void App::onTimerTimeOut()
{
    QString codeClavier;
    if (_clavierMatriciel.lireCode(codeClavier)) {
        // Logger toute saisie différente (pour ne pas spammer les logs avec ---- répété)
        if (codeClavier != _dernierCodeLu) {
            QNetworkRequest rawRequest(QUrl("http://localhost:5000/api/log_keypad_raw"));
            rawRequest.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
            QJsonObject rawJson;
            rawJson["raw"] = codeClavier;
            _manager.post(rawRequest, QJsonDocument(rawJson).toJson());

            _dernierCodeLu = codeClavier;
        }

        // Gère la saisie complète (ex: 1234, sans #)
        if (codeClavier.length() == 4 && codeClavier.contains(QRegExp("^[0-9]{4}$"))) {
            QString pinSansHash = codeClavier;
            qDebug() << "[DEBUG] PIN à vérifier : " << pinSansHash;

            // Vérifie le code via l'API
            QNetworkRequest request(QUrl("http://localhost:5000/verify_pin"));
            request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
            request.setRawHeader("X-Api-Key", "secret");
            QJsonObject json;
            json["pin_code"] = pinSansHash;

            QNetworkReply* reply = _manager.post(request, QJsonDocument(json).toJson());

            connect(reply, &QNetworkReply::finished, this, [=]() {
                QByteArray response_data = reply->readAll();
                QJsonDocument json_doc = QJsonDocument::fromJson(response_data);
                bool authorized = json_doc.object().value("authorized").toBool();
                QString username = json_doc.object().value("username").toString();
 		qDebug() << "[DEBUG] authorized? " << authorized << "username:" << username << "response:" << response_data;

                // Log l'événement (toujours)
                QNetworkRequest logRequest(QUrl("http://localhost:5000/api/log_event"));
                logRequest.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
                QJsonObject logJson;
                logJson["event"] = "KEYPAD_UNLOCK";
                logJson["pin_code"] = pinSansHash;
                logJson["username"] = username;
                logJson["details"] = authorized
                    ? QString("Ouverture par clavier matriciel (utilisateur : %1)").arg(username)
                    : "Tentative d'ouverture échouée (clavier)";
                logJson["authorized"] = authorized;
                _manager.post(logRequest, QJsonDocument(logJson).toJson());

                if (authorized) {
                    _clavierMatriciel.signalerEtat(Clavier::OK);
                    _centreNotifs.publier(CentreNotifications::CLAVIER, "deverouillage");
                    _centreNotifs.publier(CentreNotifications::SERRURE, "deverouillage");
                } else {
                    _clavierMatriciel.signalerEtat(Clavier::NOK);
                }

                reply->deleteLater();
            });
        }
    }
}
