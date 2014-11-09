import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Window 2.2
import Os 1.0

import "components" as Components
import "js/appController.js" as Ctrl


ApplicationWindow {
    id: window
    width: 500
    height: 300
    color: Ctrl.color.background

    Filesystem { id: fs }
    ListModel { id: model }
    Components.ItemDelegate { id: itemDelegate }
    

    ListView {
        id: listview
        model: model
        delegate: Components.ItemDelegate {}
        header: Components.HeaderDelegate {}
        highlight: Components.HighlightComponent { id: highlightComponent }
        focus: true
        currentIndex: 1

        width: 200
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 5

        // Eliminate visible creation and destruction
        // when scrolling.
        displayMarginBeginning: 20
        displayMarginEnd: 20
    }

    Component.onCompleted: {
        window.x = (Screen.width - window.width) / 2;
        window.y = (Screen.height - window.height) / 2;

        Ctrl.init();
    }

}
