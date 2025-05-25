#include "QThread"

#include "nfcworker.h"

NFCWorker::NFCWorker(QObject *parent)
    : QObject{parent}
{

}

bool NFCWorker::getVersionFW(QString& version)
{
    bool isOK = false;
    uint8_t response[ 4 ];

    if( _lecteurNFC->getFirmwareVersion(response) != -1) {
        version = QString("v%1.%2").arg(response[ 1 ]).arg(response[ 2 ]);
        isOK= true;
    } else {
        version.clear();
    }
    return isOK;
}

void NFCWorker::setup()
{
    _lecteurNFC = new PN532();

    if ( !_lecteurNFC->init() ) {
        emit nfcError("Echec initialisation PN532");
        return;
    }

    _lecteurNFC->SAMconfiguration();

    emit nfcInitialized();

    loop();
}

void NFCWorker::loop()
{
    static bool isBadgePresent = false;

    while( !QThread::currentThread()->isInterruptionRequested() ) {
        uint8_t uid[ PN532::UID_MAX_LENGTH ];
        int uidLen;

        uidLen = _lecteurNFC->listPassiveTarget(
            PN532::CARD_TYPE::ISO_14443_A
            , uid
            , 500
            );

        QString badgeUID;
        if( uidLen != -1) {
            // Construire une chaine qui représente l'UID (xx:yy:zz:tt:uu:vv::ww)
            for (int i = 0; i < uidLen; i++) {
                badgeUID += QString("%1:").arg(uid[ i ], 2, 16, QChar('0')).toUpper();
            }
            badgeUID.chop(1); // Retire le dernier ':'
            if( ! isBadgePresent ) {
                emit nfcDetected(badgeUID);
                isBadgePresent = true;
            }
        } else {
            if( isBadgePresent ) {
                isBadgePresent = false;
                emit nfcRemoved();
            }
        }

        QThread::msleep(500);
    }
}
