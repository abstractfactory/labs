import QtQuick 2.3
import QtQuick.Window 2.0
import QtQuick.Controls 1.2


Window {
    id: main
    width: Screen.width / 5
    height: Screen.height / 3
    x: Screen.width / 2 - main.width
    y: Screen.height / 2 - main.height

    ListView {
        id: pyblishList
        anchors.fill: parent
        spacing: 10
        delegate: Button {
            width: parent.width
            text: pyblishList.model[index]['instance']
        }
    }

    Component.onCompleted: {
        // Create a request, and tell it where the JSON is
        var req = new XMLHttpRequest(),
            location = "http://event.pyblish.com/api";

        // Tell the request to go and get the JSON
        req.open("GET", location, true);
        req.send();

        // Wait until the readyState is 4, which means it's ready.
        req.onreadystatechange = function () {
            if (req.readyState == 4) {
                // Convert text from response to JSON
                console.log(req.responseText);
                pyblishList.model = JSON.parse(req.responseText);
            }
        };
    }
}

