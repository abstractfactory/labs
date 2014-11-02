import QtQuick 2.3

Item {
    width: 360
    height: 360

    Image {
        id: myImage
        source: "200.gif"
        sourceSize.width: parent.width / 2
        sourceSize.height: parent.height / 2
        anchors {
            horizontalCenter: parent.horizontalCenter
        }

        Text {
            id: testing
            text: ""
            anchors {
                top: parent.bottom
                topMargin: 10
                horizontalCenter: parent.horizontalCenter
            }
        }
    }
}

