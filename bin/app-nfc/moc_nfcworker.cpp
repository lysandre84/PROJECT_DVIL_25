/****************************************************************************
** Meta object code from reading C++ file 'nfcworker.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.8)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "nfcworker.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'nfcworker.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.8. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_NFCWorker_t {
    QByteArrayData data[9];
    char stringdata0[72];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_NFCWorker_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_NFCWorker_t qt_meta_stringdata_NFCWorker = {
    {
QT_MOC_LITERAL(0, 0, 9), // "NFCWorker"
QT_MOC_LITERAL(1, 10, 8), // "nfcError"
QT_MOC_LITERAL(2, 19, 0), // ""
QT_MOC_LITERAL(3, 20, 3), // "msg"
QT_MOC_LITERAL(4, 24, 14), // "nfcInitialized"
QT_MOC_LITERAL(5, 39, 11), // "nfcDetected"
QT_MOC_LITERAL(6, 51, 3), // "uid"
QT_MOC_LITERAL(7, 55, 10), // "nfcRemoved"
QT_MOC_LITERAL(8, 66, 5) // "setup"

    },
    "NFCWorker\0nfcError\0\0msg\0nfcInitialized\0"
    "nfcDetected\0uid\0nfcRemoved\0setup"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_NFCWorker[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       4,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    1,   39,    2, 0x06 /* Public */,
       4,    0,   42,    2, 0x06 /* Public */,
       5,    1,   43,    2, 0x06 /* Public */,
       7,    0,   46,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       8,    0,   47,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void, QMetaType::QString,    3,
    QMetaType::Void,
    QMetaType::Void, QMetaType::QString,    6,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void,

       0        // eod
};

void NFCWorker::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<NFCWorker *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->nfcError((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 1: _t->nfcInitialized(); break;
        case 2: _t->nfcDetected((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 3: _t->nfcRemoved(); break;
        case 4: _t->setup(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (NFCWorker::*)(const QString & );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&NFCWorker::nfcError)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (NFCWorker::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&NFCWorker::nfcInitialized)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (NFCWorker::*)(const QString & );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&NFCWorker::nfcDetected)) {
                *result = 2;
                return;
            }
        }
        {
            using _t = void (NFCWorker::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&NFCWorker::nfcRemoved)) {
                *result = 3;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject NFCWorker::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_NFCWorker.data,
    qt_meta_data_NFCWorker,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *NFCWorker::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *NFCWorker::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_NFCWorker.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int NFCWorker::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
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

// SIGNAL 0
void NFCWorker::nfcError(const QString & _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void NFCWorker::nfcInitialized()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}

// SIGNAL 2
void NFCWorker::nfcDetected(const QString & _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}

// SIGNAL 3
void NFCWorker::nfcRemoved()
{
    QMetaObject::activate(this, &staticMetaObject, 3, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
