import QtQuick 2.0

Text {
    id: thisLabel
    text: "Greetings " + times

    x: 24
    y: 16

    height: 2 * width
    property int times: 24
    property alias anotherTimes: thisLabel.times

    font.family: "Ubuntu"
    font.pixelSize: 24

    KeyNavigation.tab: otherTimes

    onHeightChanged: console.log('height:', height)

    color: focus?"red":"black"
}