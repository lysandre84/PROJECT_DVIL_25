#ifndef CENTRENOTIFICATIONS_H
#define CENTRENOTIFICATIONS_H

#include <QObject>
#include <QMqttClient>

const QString TOPIC_SERRURE = QString("DVIL/Serrure");
const QString TOPIC_CLAVIER = QString("DVIL/Clavier");

class CentreNotifications : public QObject
{
    Q_OBJECT
public:
    explicit CentreNotifications(QObject *parent = nullptr);

    typedef enum : int {
    SERRURE,       // 0
    CLAVIER,       // 1     
    CODE_CLAVIER,  // 2
    CODE_NFC,      // 3
    CODE_ADMIN
    } notification_t;
    void abonner(notification_t notif);
    void publier(notification_t notif, QString data);
    void publier(notification_t notif, QJsonObject data);

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
