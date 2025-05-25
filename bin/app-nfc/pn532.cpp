#include <chrono>
#include <thread>

#include "pn532.h"

PN532::PN532(QObject *parent)
    : QObject{parent}
{
    init();
}

int PN532::getFirmwareVersion(uint8_t *version)
{
    int ret;

    ret = callFunction(
        COMMAND::GETFIRMWAREVERSION
        , NULL
        , 0
        , version
        , 4
        , 500
        );

    if ( ret == -1 ) {
        log("Echec de détection du PN532");
        return -1;
    }

    return 0;
}

int PN532::SAMconfiguration()
{
    uint8_t params[] = {
        0x01    // Normal Mode
        , 0x14  // Timeout = 20 * 50ms = 1s
        , 0x00  // IRQ non utilisée
    };

    int length = callFunction(
        COMMAND::SAMCONFIGURATION
        , params
        , sizeof(params)
        , nullptr
        , 0
        , 1000 // Timeout 1s
        );

    if (length < 0) {
        return -1; // Pas de carte détectée
    }
    return 0;

}

int PN532::listPassiveTarget(card_type_t type, uint8_t *targetData, uint32_t timeout)
{
    uint8_t buff[19];
    // Détecter 1 badge au maximum
    uint8_t params[] = {0x01, static_cast<uint8_t>(type)};

    // Lancer la commande
    int length = callFunction(
        COMMAND::INLISTPASSIVETARGET
        , params
        , sizeof(params)
        , buff
        , sizeof(buff)
        , timeout
        );

    if (length < 0) {
        return -1; // Pas de carte détectée
    }

    // Vérifier Check only 1 card with up to a 7 byte UID is present.
    if (buff[ 0 ] != 0x01) {
        log("Plusieurs cartes détectées !");
        return -1;
    }
    if (buff[ 5 ] > 7) {
        log("Découverte d'une carte avec UID trop long !");
        return -1;
    }
    for (uint8_t i = 0; i < buff[ 5 ]; i++) {
        targetData[ i ] = buff[ 6+i ];
    }
    return buff[ 5 ];
}

bool PN532::init()
{
    // SPI setup
    spidev_cfg_t spiConfig;
    const char spiDevice[] = "/dev/spidev0.0";
    spiConfig.mode=0;
    spiConfig.speed=100000;
    spiConfig.delay=0;
    spiConfig.bits_per_word=8;

    _pn532 = new SpiDev(spiDevice, &spiConfig);

    bool isOK = _pn532->begin();
    if( isOK ) {
        wakeUp();
    };

    return isOK;

}

void PN532::log(const char* msg)
{
    printf("%s\n", msg);
}

void PN532::wakeUp()
{
    // Envoi octet quelconque pour réveiller le PN532
    uint8_t txBuffer[] = {0x00};

    std::this_thread::sleep_for(std::chrono::nanoseconds(500));

    _pn532->write(
        txBuffer
        , sizeof(txBuffer)
        );

    std::this_thread::sleep_for(std::chrono::nanoseconds(500));
}

void PN532::writeData(uint8_t *data, uint8_t len)
{
    uint8_t txBuffer[ len+1 ];

    txBuffer[0] = _reverse_bits_lookup_table[ PN532::SPI_OPERATION::DW ];
    for (uint8_t i = 0; i < len; i++) {
        txBuffer[ i+1 ] = _reverse_bits_lookup_table[ data[ i ] ];
    }
    _pn532->write(
      txBuffer
      , len+1
                );
}

void PN532::readData(uint8_t *data, uint8_t len)
{
    uint8_t txBuffer[len + 1];
    uint8_t rxBuffer[len + 1];

    txBuffer[0] = _reverse_bits_lookup_table[ PN532::SPI_OPERATION::DR ];
    _pn532->xfer(
      txBuffer
      , rxBuffer
      , len+1
      );
    for (uint8_t i = 0; i < len; i++) {
        data[i] = _reverse_bits_lookup_table[ rxBuffer[ i+1 ] ];
    }
}

bool PN532::waitReady(uint32_t timeout)
{
    uint8_t txBuffer[] = {_reverse_bits_lookup_table[ SPI_OPERATION::SR ], 0x00};
    uint8_t rxBuffer[ 2 ];

    const auto timestart = std::chrono::steady_clock::now();

    while (1) {   // compare ns to ms
        std::this_thread::sleep_for(std::chrono::milliseconds(10));

        _pn532->xfer(
          txBuffer
          , rxBuffer
          , sizeof(txBuffer)
          );

        if (rxBuffer[ 1 ] == _reverse_bits_lookup_table[ _SPI_RDY ]) {
            return true;
        } else {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }

        const auto timenow = std::chrono::steady_clock::now();
        const auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(timenow - timestart);
        if (duration > std::chrono::milliseconds(timeout)) {
            break;
        }
    }
    return false;
}

int PN532::writeFrame(uint8_t *data, uint8_t len)
{
    if (len > _FRAME_MAX_LENGTH || len < 1) {
        return -1;
    }

    // Construire la trame
    // - Preamble (0x00)
    // - Start code  (0x00, 0xFF)
    // - Command length (1 byte)
    // - Command length checksum
    // - Command bytes
    // - Checksum
    // - Postamble (0x00)

    uint8_t frame[ _FRAME_MAX_LENGTH + 7 ];
    uint8_t checksum = 0;

    frame[ 0 ] = _PREAMBLE;

    frame[ 1 ] = _START_CODE_1;
    frame[ 2 ] = _START_CODE_2;

    // LEN
    frame[ 3 ] = len & 0xFF;

    // LCS
    frame[ 4 ] = (~len+1) & 0xFF;

    // Command
    for (uint8_t i = 0; i < len; i++) {
        frame[ 5+i] = data[ i ];
        checksum += data[ i ];
    }

    // CHKS
    frame[ len+5 ] = (~checksum+1) & 0xFF;
    frame[ len+6 ] = _POSTAMBLE;

    // Envoyer la trame
    writeData(frame, len+7);

    return 0;
}

int PN532::readFrame(uint8_t *data, uint8_t len)
{
    uint8_t buff[ _FRAME_MAX_LENGTH+7 ];
    uint8_t checksum = 0;

    // Lire la trame provenant du PN532
    readData(buff, len+7);

    // Eliminer tout les 0 de début de trame
    uint8_t offset = 0;
    while (buff[ offset ] == 0x00) {
        offset += 1;
        if (offset >= len+8){
            log("Trame de réponse non conforme ! (constituée uniquement de 0)");
            return -1;
        }
    }
    if (buff[ offset ] != 0xFF) {
        log("Trame de réponse non conforme ! (pas de START CODE : 0x00FF)");
        return -1;
    }

    offset += 1;

    if (offset >= len+8) {
        log("Trame de réponse non conforme ! (aucune données)");
        return -1;
    }

    // Vérifier LEN+LCS
    uint8_t frameLen = buff[ offset ];
    if (((frameLen + buff[ offset+1 ]) & 0xFF) != 0) {
        log("Erreur checksum ! (LCS NOK)");
        return -1;
    }

    // Vérifier checksum trame
    for (uint8_t i = 0; i < frameLen+1; i++) {
        checksum += buff[ offset+2+i ];
    }
    checksum &= 0xFF;
    if (checksum != 0) {
       log("Erreur checksum ! (DCS NOK)");
        return -1;
    }

    // Retourner la trame et sa longueur
    for (uint8_t i = 0; i < frameLen; i++) {
        data[ i ] = buff[ offset+2+i ];
    }
    return frameLen;
}

int PN532::callFunction(
    uint8_t command
    , uint8_t *args
    , uint8_t argsLen
    , uint8_t *response
    , uint8_t responseLen
    , uint32_t timeout
    )
{
    // Construire la trame
    uint8_t buff[ _FRAME_MAX_LENGTH ];

    buff[ 0 ] = TFI::TO_PN532;

    buff[ 1 ] = command & 0xFF;

    for (uint8_t i = 0; i < argsLen; i++) {
        buff[ 2+i ] = args[ i ];
    }

    // Envoyer la trame et attendre son accusé de réception
    if (writeFrame(buff, argsLen+2) != 0) {
        wakeUp();
        log("Tentative de réveil");
        return -1;
    }
    if ( !waitReady(timeout) ) {
        return -1;
    }

    // Vérifier l'accusé de réception et attendre la disponibilité de la réponse
    readData(buff, sizeof(_ACK_FRAME));
    for (uint8_t i = 0; i < sizeof(_ACK_FRAME); i++) {
        if (_ACK_FRAME[ i ] != buff[ i ]) {
            log("ACK PN532 non conforme !");
            return -1;
        }
    }
    if ( !waitReady(timeout) ) {
        return -1;
    }

    // Lire la réponse
    int frameLen = readFrame(buff, responseLen+2);

    // Check that response is for the called function.
    if (! ((buff[ 0 ] == TFI::TO_HOST) && (buff[ 1 ] == (command+1)))) {
        log("Réponse PN532 non conforme !");
        return -1;
    }

    // Retourner les données de la réponse et leur nombre
    for (uint8_t i = 0; i < responseLen; i++) {
        response[ i ] = buff[ i+2 ];
    }
    return frameLen-2;
}
