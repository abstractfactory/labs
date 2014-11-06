import QtQuick 2.3 as QtQuick


QtQuick.Rectangle {
    id: root
    width: 250
    color: "#eee"

    signal toggle

    onToggle: {
        if (root.state == "off") {
            root.state = "on";
        } else {
            root.state = "off";
        }
    }

    states: [
        QtQuick.State {
            name: "on"
            QtQuick.PropertyChanges { target: root; x: 0 }
        },
        QtQuick.State {
            name: "off"
            QtQuick.PropertyChanges { target: root; x: -250 }
        }
    ]

    transitions: QtQuick.Transition {
        QtQuick.NumberAnimation {
            properties: "x"
            easing.type: QtQuick.Easing.InOutQuad
            duration: 200
        }
    }
}