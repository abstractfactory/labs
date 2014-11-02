import QtQuick 2.3
import QtQuick.Window 2.0

Item {
    width: Screen.width
    height: Screen.height - 10
    focus: true

    Keys.onPressed: {
        if (event.key === Qt.Key_Up) {
            event.accepted = true;
            player.y -= 10
        }
    }

    Flickable {
        width: parent.width
        height: parent.height
        contentHeight: parent.height * 2
        contentWidth: parent.width

        interactive: true
        boundsBehavior: Flickable.StopAtBounds

        Image {
            id: field
            anchors.fill: parent
            sourceSize.width: parent.width
            sourceSize.height: parent.height * 2
        }

        Image {
            id: player
            x: parent.width / 2
            y: parent.height / 4
            source: "http://placehold.it/200"
        }
    }
}
