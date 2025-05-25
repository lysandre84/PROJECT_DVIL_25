#include "app.h"

App::App(QObject *parent)
    : QObject{parent}
{
}

App::~App()
{
}

void App::run()
{
    // Rien à faire : tout est géré par des signaux/slots Qt
}
