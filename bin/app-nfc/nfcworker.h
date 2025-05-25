#ifndef CLAVIER_H
#define CLAVIER_H

#include <QObject>
#include <QTimer>

#include "../rasp-io-libs/src/spidev.h"
#include "pn532.h"

class NFCWorker : public QObject
{
    Q_OBJECT
public:
    explicit NFCWorker(QObject *parent = nullptr);
    bool getVersionFW(QString& version);

public slots :
    void setup();

private:
    PN532 * _lecteurNFC;
    void loop();

signals:
    void nfcError(const QString& msg);
    void nfcInitialized();
    void nfcDetected(const QString& uid);
    void nfcRemoved();
};

#endif // CLAVIER_H
