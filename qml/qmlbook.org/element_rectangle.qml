import QtQuick 2.0


Rectangle {
    width: 200
    height: 200

    Rectangle {
        id: rect1
        anchors.fill: parent
        anchors.margins: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "lightsteelblue" }
            GradientStop { position: 1.0; color: "slategray" }
        }
        border.color: "slategray"
        
        Rectangle {
            id: rect2
            x: 112
            y: 12
            anchors.right: parent.right
            anchors.margins: 5
            width: 76
            height: 96
            border.color: "green"
            border.width: 1
            radius: 8
        }
    }

}