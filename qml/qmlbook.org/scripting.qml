import QtQuick 2.0

Text {
    id: label

    x: 24
    y: 24
    focus:true

    property int spacePresses: 0

    text: "Space pressed: " + spacePresses + " times"

    onTextChanged: console.log("text changed to:", text)

    Keys.onSpacePressed: {
        increment()
    }

    Keys.onEscapePressed: {
        spacePresses = 0
    }

    function increment() {
        spacePresses = spacePresses + 1
    }
}