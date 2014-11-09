import QtQuick 2.3
import "../js/appController.js" as Ctrl

Component {
    Rectangle {
        id: root
        width: ListView.view.width
        height: 20
        color: Qt.darker(Ctrl.color.background)

        property alias text: text.text

        Text {
            id: text
            text: "Header"
            color: "white"
            anchors.centerIn: parent
        }
    }
}