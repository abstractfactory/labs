import QtQuick 2.3


Rectangle {
    id: rootAngle
    width: 360
    height: 360
    color: "#44beee"

    Rectangle {
        id: blueRec
        color: "gray"
        width: parent.width / 2
        height: parent.height / 3
        anchors.centerIn: parent

        Text {
            id: fooText
            anchors.centerIn: parent
            text: "Hello <b>World</b>"
            font.family: "Verdana"
            font.pixelSize: parent.height / 3
            width: parent.width
            wrapMode: Text.WordWrap
        }

    }

    MouseArea {
        id: blueRecMouseArea
        anchors.fill: blueRec
        hoverEnabled: true
        onEntered: {
            blueRec.color = "brown"
            blueRec.rotation = 45
        }
        onExited: {
            blueRec.color = "gray"
            blueRec.rotation = 0
        }

        onClicked: {
            Qt.quit();
        }
    }

    Rectangle {
        id: test
    }

}
