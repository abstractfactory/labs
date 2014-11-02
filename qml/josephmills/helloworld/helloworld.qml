import QtQuick 2.2

Rectangle {
    id: rectangle1
    width: 360
    height: 360

    MouseArea {
        anchors.fill: parent
        onClicked: {
            Qt.quit();
        }
    }

    Text {
        width: 113
        height: 27
        color: "#93b5f9"
        text: "My World"
        clip: false
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        style: Text.Raised
        font.pointSize: 16
        font.bold: true
        font.family: "Tahoma"
    }
}

