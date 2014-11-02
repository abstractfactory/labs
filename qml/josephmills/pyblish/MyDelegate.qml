import QtQuick 2.0

Item {
    width: parent.width
    height: 100

    Rectangle {
        color: "brown"
        anchors.fill: parent

        Text {
            text: instance
            anchors.centerIn: parent
            font.pointSize: 13
        }
    }
}
