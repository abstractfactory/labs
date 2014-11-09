import QtQuick 2.3

import "../js/itemController.js" as ItemCtrl
import "../js/appController.js" as AppCtrl

/*
 * Filesystem delegate
 * This item is the box per item on a file-system
*/
Component {
    Item {
        id: root
        property int time: 200
        signal clicked

        height: 25
        width: ListView.view.width
        clip: true

        Rectangle {
            // Hover
            id: hoverRect
            opacity: 0
            anchors.fill: parent
            radius: 2
            color: "transparent"
            border.width: 5
            border.color: Qt.lighter(AppCtrl.color.background, 1.5)

            Behavior on opacity {
                NumberAnimation {
                    duration: 100
                    easing.type: Easing.OutQuad
                }
            }

            Behavior on border.width {
                NumberAnimation {
                    duration: 200
                }
            }
        }

        Text {
            id: text
            text: path
            anchors.fill: parent
            anchors.margins: 10
            color: "white"
        }


        MouseArea {
            hoverEnabled: true
            anchors.fill: parent
            onClicked: ItemCtrl.clickHandler(index);
            onEntered: {
                hoverRect.opacity = 0.4;
                hoverRect.border.width = 1;
            }
            onExited: {
                hoverRect.opacity = 0.0;
                hoverRect.border.width = 5;
            }
        }
    }
}