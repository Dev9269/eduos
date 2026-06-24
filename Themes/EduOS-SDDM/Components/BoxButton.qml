import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: boxButton
    width: 36
    height: 36
    radius: 10
    color: mouseArea.containsMouse ? Qt.rgba(255/255, 255/255, 255/255, 0.06) : Qt.rgba(255/255, 255/255, 255/255, 0.03)
    border.width: 1
    border.color: Qt.rgba(255/255, 255/255, 255/255, 0.06)

    property alias source: icon.source
    property alias iconWidth: icon.width
    property alias iconHeight: icon.height
    signal clicked

    Behavior on color {
        ColorAnimation { duration: 150 }
    }

    Image {
        id: icon
        anchors.centerIn: parent
        width: 18
        height: 18
        fillMode: Image.PreserveAspectFit
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: boxButton.clicked()
    }
}