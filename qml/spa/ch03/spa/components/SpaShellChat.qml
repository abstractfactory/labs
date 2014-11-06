import QtQuick 2.3
import "../components" as Components


Components.Rectangle {
    id: root
    width: 300
    height: 450
    clip: true
    color: "white"

    property int chat_extend_time: 1000
    property int chat_retract_time: 300
    property int chat_extend_height: 450
    property int chat_retract_height: 20
    property color chat_default_color: "white"
    property color chat_hovered_color: "lightgrey"

    signal toggle

    onToggle: {
        if (root.state == "off") {
            root.state = "on";
        } else {
            root.state = "off";
        }
    }

    states: [
        State {
            name: "on"
            PropertyChanges { target: root; height: root.chat_retract_height }
        },
        State {
            name: "off"
            PropertyChanges { target: root; height: root.chat_extend_height }
        }
    ]

    transitions: Transition {
        NumberAnimation {
            properties: "height"
            easing.type: Easing.InOutQuad
            duration: 300
        }
    }

    Component.onCompleted: toggle();

    Components.Rectangle {
        id: spaChatHead
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: parent.chat_retract_height
        z: 1

        Components.Button {
            id: spaChatHeadCloser
            text: "X"
            width: 25
            defaultColor: "lightgrey"
            hoverColor: "grey"
            height: parent.height
            anchors.top: parent.top
            anchors.left: parent.left

        }

        Components.Button {
            id: spaChatHeadTitle
            text: "Chat"
            defaultColor: "lightgrey"
            hoverColor: "grey"
            height: parent.height
            anchors.top: parent.top
            anchors.left: spaChatHeadCloser.right
            anchors.right: spaChatHeadToggle.left
            onClicked: root.toggle()
        }

        Components.Button {
            id: spaChatHeadToggle
            text: "-"
            width: 25
            defaultColor: "lightgrey"
            hoverColor: "grey"
            height: parent.height
            anchors.top: parent.top
            anchors.right: parent.right
        }
    }

    Components.Rectangle {
        id: spaChatSizer
        anchors.top: spaChatHead.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: spaChatBox.top
        anchors.margins: 10
        height: 200
        color: "white"
        border.width: 1
        border.color: "grey"

        TextEdit {
            id: spaChatMsgs
            anchors.fill: parent
            focus: true
            textMargin: 10
        }
    }

    Components.Rectangle {
        id: spaChatBox
        anchors.bottom: parent.bottom
        anchors.topMargin: 3
        anchors.bottomMargin: 3
        width: parent.width
        height: 30
        color: "white"

        Components.Rectangle {
            id: spaChatBoxInput
            height: parent.height
            anchors.left: parent.left
            anchors.right: spaChatBoxSend.left
            anchors.margins: 3
            border.width: 1
            border.color: "lightgrey"

            Components.Rectangle {
                anchors.fill: parent
                anchors.margins: 5

                TextInput {
                    width: parent.width - 50
                    height: parent.height
                    anchors.fill: parent
                    verticalAlignment: TextInput.AlignVCenter
                }
            }
        }

        Components.Button {
            id: spaChatBoxSend
            width: 50
            text: "Send"
            defaultColor: "lightgrey"
            hoverColor: "grey"
            height: parent.height
            anchors.right: parent.right
            anchors.rightMargin: 3           
        }
    }
}
