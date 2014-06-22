import QtQuick 2.0

Rectangle {
    id: root

    Image {
        x: 12
        y: 12
        source: "assets/rocket.png"
    }

    Image {
        x: 112
        y: 12
        width: 48
        height: 118/2
        source: "assets/rocket.png"
        fillMode: Image.PreserveAspectCrop
        clip: true
    }
}