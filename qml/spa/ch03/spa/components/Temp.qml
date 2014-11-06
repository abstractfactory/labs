import QtQuick 2.3
import QtQuick.Controls 1.2


Rectangle {
    id: root
    width: 500
    height: 500
    color: "brown"
    z: 20

    Row {
        width: parent.width

        Button {
            id: spaChatHeadCloser
            text: "X"
        }

        Rectangle {
            id: spaChatHeadTitle
            color: "blue"
            width: 200
            height: 10
        }

        Button {
            id: spaChatHeadToggle
            text: "-"
        }
    }
}