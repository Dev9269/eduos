import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    width: 1920
    height: 1080
    color: "#0a0a14"

    Column {
        anchors.centerIn: parent
        spacing: 16

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "◆"
            font.pixelSize: 64
            color: "#6c63ff"
            font.bold: true
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "EduOS"
            font.pixelSize: 36
            font.weight: Font.Bold
            color: "#e2e8f0"
            letterSpacing: -0.5
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Loading..."
            font.pixelSize: 13
            color: Qt.rgba(255/255, 255/255, 255/255, 0.5)
        }

        Item { height: 20; width: 1 }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 200
            height: 4
            radius: 2
            color: Qt.rgba(255/255, 255/255, 255/255, 0.06)

            Rectangle {
                id: progressBar
                width: parent.width * 0.3
                height: parent.height
                radius: 2
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#6c63ff" }
                    GradientStop { position: 1.0; color: "#4fc3f7" }
                }

                SequentialAnimation on width {
                    running: true
                    loops: Animation.Infinite
                    NumberAnimation {
                        from: 30; to: 180; duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                    NumberAnimation {
                        from: 180; to: 30; duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                }
            }
        }
    }
}
