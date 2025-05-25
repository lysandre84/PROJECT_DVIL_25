#include <csignal>
#include <cstring>
#include <QDebug>

#include <QCoreApplication>

#include "app.h"
#define APP_VERSION "1.0.0"
 


int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    signal(SIGTERM, [](int sig) {
        qDebug().nospace() << "signal SIG" << sigabbrev_np(sig) << " => Bye !";
        qApp->quit();
        });

    App app;

    app.run();

    return a.exec();
}
