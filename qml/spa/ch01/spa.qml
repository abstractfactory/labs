import QtQuick 2.3
import QtQuick.Window 2.2

import "spa.js" as Js


Window {
    id: window
    width: 500
    height: 600
    color: "brown"

    Component.onCompleted: {
        // Center window
        window.x = (Screen.width - window.width) / 2;
        window.y = (Screen.height - window.height) / 2;
    }

    Rectangle {
        id: spa
        anchors.fill: parent

        Loader {
            id: spaSliderLoader
            anchors.bottom: parent.bottom
        }

        Component.onCompleted: {
            Js.initModule();
        }
    }
}

