#include <QDebug>
#include <QJsonObject>
#include <QJsonDocument>

#include "centrenotifications.h"

CentreNotifications::CentreNotifications(QObject *parent)
    : QObject{parent}
{
    _client = new QMqttClient();

    connect(_client, &QMqttClient::connected, this, &CentreNotifications::onClientConnected);
    connect(_client, &QMqttClient::messageReceived, this, &CentreNotifications::onMqttMsgReceived);

    _client->setHostname("localhost");
    _client->setPort(1883);
    _client->setUsername("admin");
    _client->setPassword("admin");

    _client->connectToHost();
}

void CentreNotifications::abonner(notification_t notif)
{
    switch (notif) {
    case SERRURE:
        _client->subscribe(TOPIC_SERRURE);
        break;
    case CODE_CLAVIER:
        _client->subscribe(TOPIC_CLAVIER);
        break;
    case CODE_NFC:
        _client->subscribe(TOPIC_NFC);
        break;
    case CODE_ADMIN:
        break;
    default:
        break;
    }
}

void CentreNotifications::publier(notification_t notif, QString data)
{
    QJsonObject jObj;
    QJsonDocument jDoc;

    switch (notif) {
    case SERRURE:
        _client->publish(TOPIC_SERRURE, "deverouillage");
        break;
    case CODE_CLAVIER:
        jObj.insert("code", data);
        jDoc.setObject(jObj);
        _client->publish(TOPIC_CLAVIER, jDoc.toJson(QJsonDocument::Indented));
        break;
    case CODE_NFC:
        jObj.insert("code", data);
        jDoc.setObject(jObj);
        _client->publish(TOPIC_CLAVIER, jDoc.toJson(QJsonDocument::Indented));
        break;
    case CODE_ADMIN:
        break;
    default:
        break;
    }
}

void CentreNotifications::publier(notification_t notif, QJsonObject data)
{
    QJsonDocument jDoc(data);
    QByteArray topicValue = jDoc.toJson(QJsonDocument::Indented);

    switch (notif) {
    case SERRURE:
        _client->publish(TOPIC_SERRURE, topicValue);
        break;
    case CODE_CLAVIER:
        _client->publish(TOPIC_CLAVIER, topicValue);
        break;
    case CODE_NFC:
        _client->publish(TOPIC_NFC, topicValue);
        break;
    case CODE_ADMIN:
        break;
    default:
        break;
    }
}


void CentreNotifications::onClientConnected()
{
    qDebug() << "Connecté au broker";
    emit sigReady();
}

void CentreNotifications::onMqttMsgReceived(const QByteArray &message, const QMqttTopicName &topic)
{
    qDebug() << QString(message) << " reçu sur " << topic.name();
    if( topic.name().contains(TOPIC_SERRURE)) {
        if (message.contains("deverouillage")) {
            emit sigDeverouillage();
        }
    }
}
