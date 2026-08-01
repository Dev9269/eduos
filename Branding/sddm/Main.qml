import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0A1628"

    // Background gradient
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0F2044" }
            GradientStop { position: 1.0; color: "#0A1628" }
        }
    }

    // SDDM data models
    TextConstants { id: textConstants }

    // Login panel
    Rectangle {
        id: loginPanel
        width: 420
        height: 480
        anchors.centerIn: parent
        color: "#0D1B2E"
        radius: 16
        border.color: "#1E3A5F"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 20

            // Logo / Title
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "EduOS"
                font.pixelSize: 36
                font.bold: true
                color: "#4A9EFF"
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Engineering Education Platform"
                font.pixelSize: 13
                color: "#8BA3C0"
            }

            // Divider
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#1E3A5F"
            }

            // Username field
            TextField {
                id: userField
                Layout.fillWidth: true
                height: 48
                placeholderText: "Username"
                text: userModel.lastUser
                font.pixelSize: 14
                color: "#E8F0FE"
                background: Rectangle {
                    color: "#162030"
                    radius: 8
                    border.color: userField.activeFocus ? "#4A9EFF" : "#1E3A5F"
                    border.width: 1
                }
                leftPadding: 16
                Keys.onTabPressed: passwordField.forceActiveFocus()
                Keys.onReturnPressed: passwordField.forceActiveFocus()
            }

            // Password field
            TextField {
                id: passwordField
                Layout.fillWidth: true
                height: 48
                placeholderText: "Password"
                echoMode: TextInput.Password
                font.pixelSize: 14
                color: "#E8F0FE"
                background: Rectangle {
                    color: "#162030"
                    radius: 8
                    border.color: passwordField.activeFocus ? "#4A9EFF" : "#1E3A5F"
                    border.width: 1
                }
                leftPadding: 16
                Keys.onReturnPressed: loginBtn.clicked()
            }

            // Error message
            Text {
                id: errorMsg
                Layout.fillWidth: true
                text: ""
                color: "#FF6B6B"
                font.pixelSize: 12
                wrapMode: Text.WordWrap
                visible: text !== ""
            }

            // Login button
            Button {
                id: loginBtn
                Layout.fillWidth: true
                height: 48
                text: "Login"
                font.pixelSize: 15
                font.bold: true

                background: Rectangle {
                    color: loginBtn.pressed ? "#2563EB" :
                           loginBtn.hovered ? "#3B82F6" : "#4A9EFF"
                    radius: 8
                }
                contentItem: Text {
                    text: loginBtn.text
                    font: loginBtn.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: {
                    errorMsg.text = ""
                    if (userField.text === "") {
                        errorMsg.text = "Please enter your username"
                        return
                    }
                    sddm.login(userField.text, passwordField.text, sessionModel.index(0, 0))
                }
            }

            // Session selector
            ComboBox {
                id: sessionSelect
                Layout.fillWidth: true
                height: 36
                model: sessionModel
                textRole: "name"
                font.pixelSize: 12
                background: Rectangle {
                    color: "#162030"
                    radius: 6
                    border.color: "#1E3A5F"
                }
                contentItem: Text {
                    leftPadding: 12
                    text: sessionSelect.displayText
                    color: "#8BA3C0"
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    // Bottom info bar
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        color: "#060E1A"

        Row {
            anchors.centerIn: parent
            spacing: 20

            Text {
                text: "EduOS v2.0 — FreeBSD Edition"
                color: "#4A7A9B"
                font.pixelSize: 11
            }

            Text {
                text: "©2025 EduOS Project"
                color: "#4A7A9B"
                font.pixelSize: 11
            }
        }
    }

    // Handle login result
    Connections {
        target: sddm
        function onLoginFailed() {
            errorMsg.text = "Invalid username or password"
            passwordField.text = ""
            passwordField.forceActiveFocus()
        }
    }

    Component.onCompleted: {
        if (userField.text === "") {
            userField.forceActiveFocus()
        } else {
            passwordField.forceActiveFocus()
        }
    }
}
