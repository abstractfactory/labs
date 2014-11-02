//Move keys (left and right) to switch which rectangle has focus

import QtQuick 2.3

Rectangle {
    width: 360
    height: 360
    color: "purple"

    Row {
        width: parent.width
        spacing: 10

        Rectangle {
            id: blueRec
            width: parent.width / 3
            height: 300
            color: activeFocus ? "yellow": "gray"

            focus: true
            KeyNavigation.left: greenRec
            KeyNavigation.right: yellowRec
        }
        Rectangle {
            id: yellowRec
            width: parent.width / 3
            height: 300
            color: activeFocus ? "yellow": "gray"
            KeyNavigation.left: blueRec
            KeyNavigation.right: greenRec
        }
        Rectangle {
            id: greenRec
            width: parent.width / 3
            height: 300
            color: activeFocus ? "yellow": "gray"

            KeyNavigation.left: yellowRec
            KeyNavigation.right: blueRec
        }
    }
}

