#ifndef CENTRENOTIFICATIONS_H
#define CENTRENOTIFICATIONS_H

#include <QObject>
#include <QMqttClient>

const QString TOPIC_SERRURE = QString("DVIL/Serrure");

class CentreNotifications : public QObject
{
    Q_OBJECT
public:
    explicit CentreNotifications(QObject *parent = nullptr);

    typedef enum : int {
        SERRURE
        , CODE_CLAVIER
        , CODE_NFC
        , CODE_ADMIN
    } notification_t;
    void abonner(notification_t notif);

private:
    QMqttClient * _client;

signals:
    void sigReady();
    void sigDeverouillage();
    void sigCodeClavier(uint32_t code);
    void sigCodeNfc(uint32_t code);
    void sigCodeAdmin(uint32_t code);

private slots :
    void onClientConnected();
    void onMqttMsgReceived(const QByteArray &message, const QMqttTopicName &topic);

};

#endif // CENTRENOTIFICATIONS_H
