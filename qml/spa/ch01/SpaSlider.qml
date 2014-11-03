import QtQuick 2.0

Rectangle {
    id: spaSlider
    color: "#f00"
    width: 300
    height: 16

    signal clicked

    // Whenever the height changes, animate it
    Behavior on height {
        NumberAnimation {
            duration: 200
            easing.type: Easing.OutCubic
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: spaSlider.clicked()
    }
}
