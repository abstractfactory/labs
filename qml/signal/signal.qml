import QtQuick 2.3
import QtQuick.Window 2.2


Window {
    id: window
    width: 300; height: 300


    Loader {
        id: buttonLoader
        source: "Button.qml"
        anchors.fill: parent
    }

    Connections {
        property variant item: buttonLoader.item

        target: item
        onClicked: {
            item.color = Qt.rgba(Math.random(), Math.random(), Math.random(), 1);
        }
    }
}