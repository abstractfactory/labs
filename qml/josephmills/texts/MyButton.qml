import QtQuick 2.0


Rectangle {
    id: button
    width: 100
    height: 40
    color: "brown"

    property bool hoverEnabled: false

    Text {
        anchors.centerIn: parent
        text: "Hello World"
    }

    MouseArea {
        hoverEnabled: button.hoverEnabled
        anchors.fill: parent
        onClicked: {
            Qt.quit();
        }
        onEntered: {
            parent.color = "blue"
        }
    }

}
