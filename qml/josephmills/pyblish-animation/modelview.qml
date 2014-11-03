import QtQuick 2.3
import QtQuick.Window 2.0
import QtQuick.Controls 1.2


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
            id: button
            width: parent.width
            text: instance

            onPressedChanged: scale = 2;

            Behavior on scale {
                NumberAnimation {
//                    target: button.onPressedChanged
//                    property: "opacity"
//                    from: 1
//                    to: 0
                    easing.type: Easing.OutBounce
                    duration: 1000
                }
            }
        }
    }

    Component.onCompleted: {
        // Create a request, and tell it where the JSON is
        var req = new XMLHttpRequest();

        // Tell the request to go and get the JSON
        req.open("GET", location, true);
        req.send();

        // Wait until the readyState is 4, which means it's ready.
        req.onreadystatechange = function () {
            if (req.readyState == 4) {
                // Append each item to the ListModel
                JSON.parse(req.responseText).forEach(function (item) {
                    pyblishList.model.append(item);
                });
            }
        };
    }
}

