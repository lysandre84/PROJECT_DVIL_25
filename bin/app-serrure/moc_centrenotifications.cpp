/****************************************************************************
** Meta object code from reading C++ file 'centrenotifications.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.8)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "centrenotifications.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'centrenotifications.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.8. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_CentreNotifications_t {
    QByteArrayData data[14];
    char stringdata0[165];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_CentreNotifications_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_CentreNotifications_t qt_meta_stringdata_CentreNotifications = {
    {
QT_MOC_LITERAL(0, 0, 19), // "CentreNotifications"
QT_MOC_LITERAL(1, 20, 8), // "sigReady"
QT_MOC_LITERAL(2, 29, 0), // ""
QT_MOC_LITERAL(3, 30, 16), // "sigDeverouillage"
QT_MOC_LITERAL(4, 47, 14), // "sigCodeClavier"
QT_MOC_LITERAL(5, 62, 8), // "uint32_t"
QT_MOC_LITERAL(6, 71, 4), // "code"
QT_MOC_LITERAL(7, 76, 10), // "sigCodeNfc"
QT_MOC_LITERAL(8, 87, 12), // "sigCodeAdmin"
QT_MOC_LITERAL(9, 100, 17), // "onClientConnected"
QT_MOC_LITERAL(10, 118, 17), // "onMqttMsgReceived"
QT_MOC_LITERAL(11, 136, 7), // "message"
QT_MOC_LITERAL(12, 144, 14), // "QMqttTopicName"
QT_MOC_LITERAL(13, 159, 5) // "topic"

    },
    "CentreNotifications\0sigReady\0\0"
    "sigDeverouillage\0sigCodeClavier\0"
    "uint32_t\0code\0sigCodeNfc\0sigCodeAdmin\0"
    "onClientConnected\0onMqttMsgReceived\0"
    "message\0QMqttTopicName\0topic"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_CentreNotifications[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       7,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       5,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   49,    2, 0x06 /* Public */,
       3,    0,   50,    2, 0x06 /* Public */,
       4,    1,   51,    2, 0x06 /* Public */,
       7,    1,   54,    2, 0x06 /* Public */,
       8,    1,   57,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       9,    0,   60,    2, 0x08 /* Private */,
      10,    2,   61,    2, 0x08 /* Private */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 5,    6,
    QMetaType::Void, 0x80000000 | 5,    6,
    QMetaType::Void, 0x80000000 | 5,    6,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void, QMetaType::QByteArray, 0x80000000 | 12,   11,   13,

       0        // eod
};

void CentreNotifications::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<CentreNotifications *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->sigReady(); break;
        case 1: _t->sigDeverouillage(); break;
        case 2: _t->sigCodeClavier((*reinterpret_cast< uint32_t(*)>(_a[1]))); break;
        case 3: _t->sigCodeNfc((*reinterpret_cast< uint32_t(*)>(_a[1]))); break;
        case 4: _t->sigCodeAdmin((*reinterpret_cast< uint32_t(*)>(_a[1]))); break;
        case 5: _t->onClientConnected(); break;
        case 6: _t->onMqttMsgReceived((*reinterpret_cast< const QByteArray(*)>(_a[1])),(*reinterpret_cast< const QMqttTopicName(*)>(_a[2]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        switch (_id) {
        default: *reinterpret_cast<int*>(_a[0]) = -1; break;
        case 6:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 1:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< QMqttTopicName >(); break;
            }
            break;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (CentreNotifications::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CentreNotifications::sigReady)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (CentreNotifications::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CentreNotifications::sigDeverouillage)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (CentreNotifications::*)(uint32_t );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CentreNotifications::sigCodeClavier)) {
                *result = 2;
                return;
            }
        }
        {
            using _t = void (CentreNotifications::*)(uint32_t );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CentreNotifications::sigCodeNfc)) {
                *result = 3;
                return;
            }
        }
        {
            using _t = void (CentreNotifications::*)(uint32_t );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CentreNotifications::sigCodeAdmin)) {
                *result = 4;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject CentreNotifications::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_CentreNotifications.data,
    qt_meta_data_CentreNotifications,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *CentreNotifications::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *CentreNotifications::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_CentreNotifications.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int CentreNotifications::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    }
    return _id;
}

// SIGNAL 0
void CentreNotifications::sigReady()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void CentreNotifications::sigDeverouillage()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}

// SIGNAL 2
void CentreNotifications::sigCodeClavier(uint32_t _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}

// SIGNAL 3
void CentreNotifications::sigCodeNfc(uint32_t _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 3, _a);
}

// SIGNAL 4
void CentreNotifications::sigCodeAdmin(uint32_t _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 4, _a);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
