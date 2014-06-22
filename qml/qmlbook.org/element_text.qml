import QtQuick 2.0

Rectangle {
    id: root
    width: 400

    Text {
        id: outer
        text: "The quick brown fox"
        color: "#303030"
        font.family: "Ubuntu"
        font.pixelSize: 28

        Text {
            id: inner
            anchors.left: parent.right
            anchors.margins: 10
            font.pixelSize: 20
            color: "lightsteelblue"
            text: "A very long text"
            height: 120

            // Elide text based on window width
            width: root.width - outer.width
            elide: Text.ElideMiddle
            style: Text.Sunken
            styleColor: Qt.darker(inner.color, 1.3)

            verticalAlignment: Text.AlignTop
        }
    }

}