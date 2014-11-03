import QtQuick 2.3


Rectangle {
    id: button
    anchors.fill: parent
    color: "brown"

    signal clicked

    Text {
        id: rootText
        text: "Click me"
        anchors.centerIn: parent
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            button.clicked();
        }
    }
}