import QtQuick 2.3
import QtQuick.Window 2.0
import QtQuick.Controls 1.2

import "js/utils.js" as Utils


Window {
    id: main
    width: Screen.width / 5
    height: Screen.height / 3
    x: Screen.width / 2 - main.width
    y: Screen.height / 2 - main.height

    // Location of where to fetch information from
    property string location: "http://event.pyblish.com/event"

    ListView {
        id: pyblishList
        anchors.fill: parent
        spacing: 10
        model: ListModel {}

        delegate: Button {
            width: parent.width
            text: instance
        }
    }

    Component.onCompleted: {
        Utils.loadModel(pyblishList.model);
    }
}

