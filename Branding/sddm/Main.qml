import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920; height: 1080
    color: "#0A1628"
    
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0F2044" }
            GradientStop { position: 1.0; color: "#0A1628" }
        }
    }
    
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 80
        text: new Date().toLocaleTimeString(Qt.locale(), "hh:mm AP")
        font.pixelSize: 64; font.weight: Font.Light
        color: "#E8F4FD"
    }
    
    Image {
        source: "logo.png"
        width: 96; height: 96
        anchors.horizontalCenter: parent.horizontalCenter
        y: 200
    }
    
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 310
        text: "EduOS v3.0"
        font.pixelSize: 18; font.weight: Font.Bold
        color: "#2563EB"
    }
    
    Rectangle {
        width: 360; height: 200
        radius: 12; color: "#1C2541"
        anchors.horizontalCenter: parent.horizontalCenter
        y: 400
        border.color: "#2563EB"; border.width: 1
        
        TextField {
            id: username
            anchors.top: parent.top; anchors.topMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            width: 300; height: 40
            placeholderText: "Username"
            color: "#E8F4FD"
            background: Rectangle {
                color: "#0A1628"; radius: 8
                border.color: "#152A55"
            }
        }
        
        TextField {
            id: password
            anchors.top: username.bottom; anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: 300; height: 40
            placeholderText: "Password"
            echoMode: TextInput.Password
            color: "#E8F4FD"
            background: Rectangle {
                color: "#0A1628"; radius: 8
                border.color: "#152A55"
            }
        }
        
        Button {
            anchors.top: password.bottom; anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            width: 300; height: 40
            text: "Sign In"
            font.pixelSize: 14; font.weight: Font.Bold
            contentItem: Text {
                text: parent.text; color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                color: "#2563EB"; radius: 8
                border.color: "#3B82F6"
            }
        }
    }
}
