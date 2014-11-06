import QtQuick 2.3
import "../components" as Components

Components.Rectangle {
    id: root
    color: root.defaultColor

    property color defaultColor: "#CBCBCB"
    property color hoverColor: "#D9D9D9"

    signal clicked
    property string text

    Text {
        id: text
        text: root.text
        anchors.centerIn: parent
    }

    Behavior on color { ColorAnimation { duration: 50 } }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true

        onClicked: root.clicked()
        onEntered: root.color = root.hoverColor
        onExited: root.color = root.defaultColor
    }
}