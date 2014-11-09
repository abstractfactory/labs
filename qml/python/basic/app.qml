import QtQuick 2.3
import QtQuick.Controls 1.2
import Os 1.0


ApplicationWindow {
    id: root
    width: 500
    height: 300
    color: "brown"
    
    /*
     * Python Component for file-system access
     *
    */
    Filesystem { id: fs }

    ListModel {
        id: model

        /*
         * Initiate model via Python Filesystem item
         *
        */
        Component.onCompleted: {
            fs.listdir("/home/marcus").forEach(function (item) {
                model.append({path: item});
            });
        }
    }


    /*
     * Filesystem delegate
     * This item is the box per item on a file-system
    */
    Component {
        id: delegate

        Rectangle {
            id: delegateRectangle
            height: 25
            width: ListView.view.width
            clip: true

            Rectangle {
                id: delegateHover
                anchors.fill: parent
                color: "#6CAFDE"
                opacity: 0

                Behavior on opacity {
                    NumberAnimation { duration: 200 }
                }
            }

            Text {
                text: path
                anchors.fill: parent
                anchors.margins: 10
            }

            MouseArea {
                hoverEnabled: true
                anchors.fill: parent
                onEntered: { delegateHover.opacity = 1.0 }
                onExited: { delegateHover.opacity = 0.0 }
            }
        }
    }

    ListView {
        id: listview
        height: 300
        model: model
        anchors.fill: parent
        anchors.margins: 20
        spacing: 3
        delegate: delegate

        // Eliminate visible creation and destruction
        // when scrolling.
        displayMarginBeginning: 25
        displayMarginEnd: 25
    }

}
