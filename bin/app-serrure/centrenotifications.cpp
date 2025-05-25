#include <QDebug>

#include "centrenotifications.h"

CentreNotifications::CentreNotifications(QObject *parent)
    : QObject{parent}
{
    _client = new QMqttClient();

    connect(_client, &QMqttClient::connected, this, &CentreNotifications::onClientConnected);
    connect(_client, &QMqttClient::messageReceived, this, &CentreNotifications::onMqttMsgReceived);

    _client->setHostname("localhost");
    _client->setUsername("admin");
    _client->setPassword("admin");  
    _client->setPort(1883);

    _client->connectToHost();
}

void CentreNotifications::abonner(notification_t notif)
{
    switch (notif) {
    case SERRURE:
        _client->subscribe(TOPIC_SERRURE);
        break;
    case CODE_CLAVIER:
        break;
    case CODE_NFC:
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
