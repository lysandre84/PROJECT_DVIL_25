/****************************************************************************
** Meta object code from reading C++ file 'app.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.8)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "app.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'app.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.8. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_App_t {
    QByteArrayData data[9];
    char stringdata0[96];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_App_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_App_t qt_meta_stringdata_App = {
    {
QT_MOC_LITERAL(0, 0, 3), // "App"
QT_MOC_LITERAL(1, 4, 29), // "onsigCentreNotificationsReady"
QT_MOC_LITERAL(2, 34, 0), // ""
QT_MOC_LITERAL(3, 35, 14), // "onTimerTimeOut"
QT_MOC_LITERAL(4, 50, 10), // "onNfcError"
QT_MOC_LITERAL(5, 61, 3), // "msg"
QT_MOC_LITERAL(6, 65, 13), // "onNfcDetected"
QT_MOC_LITERAL(7, 79, 3), // "uid"
QT_MOC_LITERAL(8, 83, 12) // "onNfcRemoved"

    },
    "App\0onsigCentreNotificationsReady\0\0"
    "onTimerTimeOut\0onNfcError\0msg\0"
    "onNfcDetected\0uid\0onNfcRemoved"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_App[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,   39,    2, 0x08 /* Private */,
       3,    0,   40,    2, 0x08 /* Private */,
       4,    1,   41,    2, 0x08 /* Private */,
       6,    1,   44,    2, 0x08 /* Private */,
       8,    0,   47,    2, 0x08 /* Private */,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::QString,    5,
    QMetaType::Void, QMetaType::QString,    7,
    QMetaType::Void,

       0        // eod
};

void App::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<App *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->onsigCentreNotificationsReady(); break;
        case 1: _t->onTimerTimeOut(); break;
        case 2: _t->onNfcError((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 3: _t->onNfcDetected((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 4: _t->onNfcRemoved(); break;
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject App::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_App.data,
    qt_meta_data_App,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *App::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *App::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_App.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int App::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 5)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 5;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 5)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 5;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
