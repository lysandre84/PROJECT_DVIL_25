QT -= gui

QT += network

QT += mqtt

CONFIG += c++17 console
CONFIG -= app_bundle

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
        ../rasp-io-libs/src/gpiodev.cpp \
        ../rasp-io-libs/src/spidev.cpp \
        app.cpp \
        centrenotifications.cpp \
        main.cpp \
        nfcworker.cpp \
        pn532.cpp

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

HEADERS += \
    ../rasp-io-libs/src/gpiodev.h \
    ../rasp-io-libs/src/spidev.h \
    app.h \
    centrenotifications.h \
    nfcworker.h \
    pn532.h

unix:!macx: LIBS += -lgpiod
