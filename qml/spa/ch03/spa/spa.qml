import QtQuick 2.3
import QtQuick.Window 2.2

import "js/spa.js" as Spa


Window {
    id: window
    title: "SPA"
    width: 800
    height: 600

    Component.onCompleted: {
        Spa.initModule();
    }

    Rectangle {
        id: spaShellHead

        height: 40
        width: parent.width

        Rectangle {
            id: spaShellHeadLogo
            x: 4
            y: 4
            height: 32
            width: 128
            color: "orange"
        }

        Rectangle {
            id: spaShellHeadAcct
            y: 4
            width: 64
            height: 32
            anchors.right: parent.right
            color: "green"

        }

        Rectangle {
            id: spaShellHeadSearch
            y: 4
            anchors.right: spaShellHeadAcct.left
            width: 248
            height: 32
            color: "blue"
        }
    }

    Rectangle {
        id: spaShellMain

        anchors.fill: parent
        anchors.topMargin: 40
        anchors.bottomMargin: 40

        Rectangle {
            id: spaShellMainNav 
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 250
            color: "#eee"
        }
        
        Rectangle {
            id: spaShellMainContent
            anchors.fill: parent
            anchors.leftMargin: 250
            color: "#ccc"
        }
    }

    Rectangle {
        id: spaShellFoot
        anchors.bottom: parent.bottom
        height: 40
        width: parent.width
    }

    Rectangle {
        id: spaShellChat
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: 300
        height: 15
        color: "red"
        z: 1
    }

    Rectangle {
        id: spaShellModal
        anchors.leftMargin: -200
        y: parent.height / 2 - 200
        x: parent.width / 2 - 200
        width: 400
        height: 400
        radius: 3
        z: 2
    }

}