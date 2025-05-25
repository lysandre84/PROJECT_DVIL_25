#ifndef APP_H
#define APP_H

#include <QObject>

#include "serrure.h"

class App : public QObject
{
    Q_OBJECT
public:
    explicit App(QObject *parent = nullptr);
    ~App();

    void run();

private :
    Serrure _serrure;

signals:

};

#endif // APP_H
