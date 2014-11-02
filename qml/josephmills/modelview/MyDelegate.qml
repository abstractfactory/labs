import QtQuick 2.0

Item {
    width: parent.width
    height: 100

    Rectangle {
        color: col
        anchors.fill: parent

        Text {
            text: name
            anchors.centerIn: parent
            font.pointSize: 13
        }

        Image {
            source: src
            anchors {
                verticalCenter: parent.verticalCenter
                leftMargin: 20
            }
        }
    }
}
