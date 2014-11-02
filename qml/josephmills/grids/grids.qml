import QtQuick 2.3

Rectangle {
    width: 360
    height: 360

    Grid {
        spacing: 10
        columns: 2
        rows: 4
        Repeater {
            model: 12
            Rectangle {width: 360 / 4; height: 360 / 4; color: "blue"}
        }
    }
}

