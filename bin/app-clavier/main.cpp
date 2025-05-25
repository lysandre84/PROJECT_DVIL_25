#include <csignal>
#include <cstring>
#include <QDebug>

#include <QCoreApplication>

#include "app.h"


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
