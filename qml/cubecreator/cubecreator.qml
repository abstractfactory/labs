import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Window 2.2


ApplicationWindow {
    id: app
    title: "Cube Creator"
    width: 640
    height: 480

    Component.onCompleted: {
        // Center window
        app.x = (Screen.width - app.width) / 2
        app.y = (Screen.height - app.height) / 2
    }

    Button {
        id: button
        text: qsTr("Hello World")
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        height: button.width
        onClicked: {
            var req = new XMLHttpRequest();
            req.open("POST", "http://127.0.0.1:6000/cmd")
            r = req.send({"cmd": "polyCube", "kwargs": {"name": "MyCube"}})
        }
    }
}
