import QtQuick 2.3 as QtQuick
import QtQuick.Window 2.2 as QtQuickWindow

import "js/spa.js" as Spa
import "js/spa.util.js" as SpaUtil
import "components" as Components


QtQuickWindow.Window {
    id: root
    title: "SPA"
    width: 800
    height: 600


    QtQuick.Component.onCompleted: {
        Spa.initModule();

        root.x = (QtQuickWindow.Screen.width - root.width) / 2
        root.y = (QtQuickWindow.Screen.height - root.height) / 2

    }

    Components.SpaShellHead {
        id: spaShellHead

        Components.SpaShellHeadLogo {
            id: spaShellHeadLogo

            QtQuick.MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: spaShellMainNav.toggle()
            }
        }

        Components.SpaShellHeadAcc {
            id: spaShellHeadAcct
             anchors.right: parent.right
         }

        Components.SpaShellHeadSearch {
            id: spaShellHeadSearch
             anchors.right: spaShellHeadAcct.left
         }
    }

    Components.SpaShellMain {
        id: spaShellMain
        anchors.fill: parent
        anchors.topMargin: 40
        anchors.bottomMargin: 40

        Components.SpaShellMainNav {
            id: spaShellMainNav
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }

        Components.SpaShellMainContent {
            id: spaShellMainContent
            anchors.fill: parent
            anchors.leftMargin: 250
        }
    }

    Components.SpaShellFoot {
        id: spaShellFoot
        anchors.bottom: parent.bottom
    }
    Components.SpaShellChat {
        id: spaShellChat
        anchors.bottom: parent.bottom
        anchors.right: parent.right
    }

    Components.SpaShellModal {
        id: spaShellModal
        visible: false
    }
}