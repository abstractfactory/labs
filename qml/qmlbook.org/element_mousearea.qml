import QtQuick 2.0

Rectangle {
    id: root
    width: 500
    height: 300


    Rectangle {
        id: rect1
        x: 12
        y: 12
        width: 76
        height: 96
        color: "lightsteelblue"
        
        MouseArea {
            id: area
            anchors.fill: parent
            onClicked: rect2.visible = !rect2.visible
        }
    }

    Rectangle {
        id: rect2
        x: 112
        y: 12
        width: 76
        height: 96
        border.color: "blue"
        border.width: 4
        radius: 8
    }

}