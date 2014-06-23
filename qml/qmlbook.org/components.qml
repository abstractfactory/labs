import QtQuick 2.0

Rectangle {
    id: root
    width: 500
    height: 300

    Button {
        id: button
        x: 12
        y: 12
        text: "Start"
        onClicked: {
            status.text = "Button clicked!"
        }
    }

    Text {
        id: status
        x: 12
        y: 76
        width: 116
        height: 26
        text: "waiting.."
        horizontalAlignment: Text.AlignHCenter
    }
}