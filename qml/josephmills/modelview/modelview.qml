import QtQuick 2.3
import QtQuick.Window 2.0


Window {
    id: main
    width: Screen.width / 5
    height: Screen.height / 3
    x: Screen.width / 2 - main.width
    y: Screen.height / 2 - main.height

    ListView {
        anchors.fill: parent
        model: mod
        spacing: 10
        delegate: MyDelegate {}
        header: Header {}
    }

    MyModel {id:mod}
}

