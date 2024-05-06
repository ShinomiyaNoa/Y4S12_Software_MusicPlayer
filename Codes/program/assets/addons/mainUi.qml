

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 6.5
import QtQuick.Controls 6.5

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height

    color: Constants.backgroundColor

    Column {
        id: column
        visible: true
        anchors.fill: parent
        anchors.rightMargin: 0
        anchors.leftMargin: 10
        anchors.bottomMargin: 5
        anchors.topMargin: 5
        spacing: 0

        Row {
            id: menuAndWidgetRow
            height: 40
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.leftMargin: 0

            ToolBar {
                id: menuBar
                width: 360
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
            }

            Row {
                id: toolsRow
                anchors.left: menuBar.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0
            }
        }

        Row {
            id: controlRow
            height: 50
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: menuAndWidgetRow.bottom
            anchors.topMargin: 0

            ToolBar {
                id: controlBar
                width: 360
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
                anchors.topMargin: 0
            }

            Row {
                id: row
                anchors.left: controlBar.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0
                anchors.topMargin: 0
            }
        }

        Row {
            id: playlistRow
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: controlRow.bottom
            anchors.bottom: infoAndVolumnRow.top
            anchors.rightMargin: 0
            anchors.leftMargin: 0
            anchors.bottomMargin: 0
            anchors.topMargin: 0

            Row {
                id: playlistSelect
                width: 200
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0
                anchors.bottomMargin: 0
                anchors.topMargin: 0
            }

            Row {
                id: playlist
                anchors.left: playlistSelect.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.rightMargin: 0
                anchors.leftMargin: 0
                anchors.bottomMargin: 0
                anchors.topMargin: 0
            }
        }

        Row {
            id: infoAndVolumnRow
            height: 60
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.rightMargin: 0
            anchors.leftMargin: 0
        }
    }
    states: [
        State {
            name: "clicked"
        }
    ]
}
