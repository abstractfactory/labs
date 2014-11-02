import QtQuick 2.3

Rectangle {
    width: 360
    height: 360
    color: "#520909"
    signal buttonClicked

    Rectangle {
        id: redLight
        x: 139
        y: 80
        width: 82
        height: 215
        color: "#2b0202"

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onClicked: buttonClicked();
        }
    }

    onButtonClicked: console.log("Hello");

    Rectangle {
        id: yellowLight
        x: 150
        y: 91
        width: 60
        height: 60
        color: "#f05353"
        radius: 30
        border.width: 0
    }

    Rectangle {
        id: greenLight
        x: 150
        y: 157
        width: 60
        height: 60
        color: "#ffea36"
        radius: 30
        border.width: 0
    }

    Rectangle {
        id: rectangle4
        x: 150
        y: 223
        width: 60
        height: 60
        color: "#7bc508"
        radius: 30
        border.width: 0
    }

}
