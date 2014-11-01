import QtQuick 2.3
import QtQuick.Controls 1.2

import "componentCreation.js" as MyScript


ApplicationWindow {
    id: appWindow
    minimumWidth: 300
    minimumHeight: 400

    property int buttonHeight: 30
    property int padding: 5

    ListModel {
        id: libraryModel
    }

    TableView {
        id: table
        model: libraryModel

        TableViewColumn {
            role: "name"
            title: "Name"
        }

        width: appWindow.width
        height: appWindow.height - appWindow.buttonHeight
    }

    Button {
        height: appWindow.buttonHeight
        text: "Add Item"
        anchors.top: table.bottom
        anchors.left: table.left
        width: table.width

        onClicked: MyScript.createSpriteObjects();
    }
}
