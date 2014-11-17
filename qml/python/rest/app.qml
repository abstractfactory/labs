import QtQuick 2.3
import QtQuick.Controls 1.2

import "peopleservice.js" as Service
import "components" as Components


ApplicationWindow {
    title: "Rest"
    width: 400; height: 600

    ListModel {
        id: peopleModel
    }

    ListView {
        id: peopleView
        anchors.fill: parent
        model: peopleModel
        delegate: Components.Delegate {}
    }

    Button {
        id: loadButton
        text: "Load"
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        onClicked: {
            Service.get_people(function (people) {
                people.result.forEach(function (person) {
                    peopleModel.append(person);
                });
            });
        }
    }
}