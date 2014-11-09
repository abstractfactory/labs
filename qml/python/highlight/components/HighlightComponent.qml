import QtQuick 2.3

import "../js/appController.js" as Ctrl

Component {
    Rectangle {
        id: root
        height: parent.height
        width: parent.width
        color: Qt.lighter(Ctrl.color.background, 1.2)
        radius: 3
    }
}