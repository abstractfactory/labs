import QtQuick 2.3

Rectangle {
    width: 360
    height: 360
    color: "black"

    TextInput {
        id: textInput
        color: "white"
        font.family: "Verdana"
        font.pointSize: 14
        anchors.fill: parent
        anchors.bottomMargin: 50
        wrapMode: Text.WordWrap
        text: "# "

        onAccepted: {
            console.log("Entered!");
            resultText.text = text
        }
    }

    Text {
        id: resultText
        color: "white"
        text: ""
        anchors {
            top: textInput.bottom
            topMargin: 20
        }
    }
}

