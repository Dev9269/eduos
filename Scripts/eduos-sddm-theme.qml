import QtQuick 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#1a1a2e"

    TextConstants { id: textConstants }

    // ─── Background ────────────────────────────────────────────
    Item {
        anchors.fill: parent

        Image {
            id: bgImage
            anchors.fill: parent
            source: "file:///usr/share/wallpapers/eduos-wallpaper.png"
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
            cache: true
        }

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#cc1a1a2e" }
                GradientStop { position: 0.4; color: "#bb1a1a2e" }
                GradientStop { position: 0.7; color: "#991a1a2e" }
                GradientStop { position: 1.0; color: "#dd0d0d1a" }
            }
        }
    }

    // ─── Top Bar ───────────────────────────────────────────────
    Item {
        anchors { left: parent.left; right: parent.right; top: parent.top; topMargin: 20 }
        height: 56

        Row {
            anchors { left: parent.left; leftMargin: 28; verticalCenter: parent.verticalCenter }
            spacing: 10
            Rectangle {
                width: 30; height: 30; radius: 6
                color: "#c8913e"
                Text { anchors.centerIn: parent; text: "E"; font { pixelSize: 16; bold: true }; color: "white" }
            }
            Column {
                spacing: 0
                anchors.verticalCenter: parent.verticalCenter
                Text { text: "EduOS"; font { pixelSize: 16; bold: true }; color: "white"; opacity: 0.9 }
                Text { text: "Engineering Education Edition"; font.pixelSize: 9; color: "white"; opacity: 0.35 }
            }
        }

        Column {
            anchors { right: parent.right; rightMargin: 28; verticalCenter: parent.verticalCenter }
            horizontalAlignment: Text.AlignRight
            spacing: 0
            Text {
                id: timeLabel
                text: Qt.formatTime(new Date(), "hh:mm")
                font { pixelSize: 26; weight: Font.Light }
                color: "white"; opacity: 0.85
            }
            Timer { interval: 1000; running: true; repeat: true; onTriggered: timeLabel.text = Qt.formatTime(new Date(), "hh:mm") }
            Text {
                text: Qt.formatDate(new Date(), "dddd, MMMM d")
                font.pixelSize: 10; color: "white"; opacity: 0.4
            }
        }
    }

    // ─── Main Content ──────────────────────────────────────────
    Column {
        id: mainContent
        anchors.centerIn: parent
        width: 360
        spacing: 0

        NumberAnimation on opacity { from: 0; to: 1; duration: 500; easing.type: Easing.OutCubic }

        // Welcome text
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Welcome"
            font { pixelSize: 22; weight: Font.Light }
            color: "white"; opacity: 0.7
            bottomPadding: 24
        }

        // ─── User Selection Row ────────────────────────────────
        Item {
            id: userRow
            width: parent.width
            height: 100

            ListView {
                id: userList
                anchors.fill: parent
                orientation: ListView.Horizontal
                spacing: 16
                clip: true
                model: userModel
                currentIndex: userModel.lastIndex
                focus: true

                delegate: Item {
                    width: 76; height: 100

                    Column {
                        anchors.centerIn: parent
                        spacing: 8

                        Rectangle {
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: 56; height: 56; radius: 28
                            color: (userList.currentIndex === index) ? "#c8913e" : "#2a2a4e"
                            border {
                                color: (userList.currentIndex === index) ? "#e8b84b" : "#4a4a6e"
                                width: (userList.currentIndex === index) ? 3 : 1
                            }

                            Image {
                                id: userIcon
                                anchors.fill: parent
                                anchors.margins: 4
                                source: model.icon
                                sourceSize { width: 48; height: 48 }
                                fillMode: Image.PreserveAspectCrop
                                asynchronous: true
                                layer.enabled: true
                                layer.effect: OpacityMask {
                                    maskSource: Rectangle {
                                        width: 48; height: 48; radius: 24
                                    }
                                }
                                onStatusChanged: {
                                    if (status === Image.Error) {
                                        source = ""
                                    }
                                }
                            }

                            Text {
                                anchors.centerIn: parent
                                text: model.icon && model.icon.length > 0 ? "" : model.name.charAt(0).toUpperCase()
                                font { pixelSize: 22; weight: Font.Bold }
                                color: "white"
                                visible: userIcon.status !== Image.Ready
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    userList.currentIndex = index
                                    userList.focus = true
                                    selectedUser = model.name
                                    showOther = false
                                    errorMessage.text = ""
                                    passwordInput.focus = true
                                    passwordInput.text = ""
                                }
                            }
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: model.realName !== "" ? model.realName : model.name
                            font.pixelSize: 11
                            color: (userList.currentIndex === index) ? "#e8b84b" : "white"
                            opacity: (userList.currentIndex === index) ? 1.0 : 0.5
                            elide: Text.ElideRight
                            maximumLineCount: 1
                        }
                    }
                }
            }
        }

        // ─── Other User Button ────────────────────────────────
        Item {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 100; height: 80

            Column {
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 52; height: 52; radius: 26
                    color: showOther ? "#c8913e" : "#2a2a4e"
                    border {
                        color: showOther ? "#e8b84b" : "#4a4a6e"
                        width: showOther ? 3 : 1
                    }

                    Text {
                        anchors.centerIn: parent
                        text: "…"
                        font { pixelSize: 24; weight: Font.Bold }
                        color: "white"; opacity: 0.8
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            showOther = true
                            selectedUser = ""
                            userList.currentIndex = -1
                            errorMessage.text = ""
                            userNameInput.focus = true
                            userNameInput.text = ""
                            passwordInput.text = ""
                        }
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Other"
                    font.pixelSize: 10
                    color: showOther ? "#e8b84b" : "white"
                    opacity: showOther ? 1.0 : 0.4
                }
            }
        }

        // Spacer
        Item { width: 1; height: 20 }

        // ─── Login Fields ─────────────────────────────────────
        Column {
            id: loginFields
            width: parent.width
            spacing: 10

            TextBox {
                id: userNameInput
                width: parent.width; height: 44
                font.pixelSize: 14
                textColor: "white"
                color: "#2a2a4e"
                borderColor: showOther ? "#c8913e" : "#3a3a5e"
                focusColor: "#c8913e"
                hoverColor: "#3a3a5e"
                radius: 8
                placeholderText: "Username"
                visible: showOther
                text: ""

                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                        passwordInput.focus = true; event.accepted = true
                    }
                }
            }

            PasswordBox {
                id: passwordInput
                width: parent.width; height: 44
                font.pixelSize: 14
                textColor: "white"
                radius: 8
                focus: true
                placeholderText: "Password"

                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                        doLogin(); event.accepted = true
                    }
                }
            }

            Button {
                id: loginButton
                width: parent.width; height: 46
                text: "Sign In"
                color: "#c8913e"
                activeColor: "#d4a04a"
                pressedColor: "#b07a2e"
                font.pixelSize: 15
                radius: 8

                onClicked: doLogin()
                Keys.onReturnPressed: doLogin()
            }

            Text {
                id: errorMessage
                width: parent.width
                wrapMode: Text.WordWrap
                color: "#ef4444"
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                visible: text.length > 0
                height: visible ? implicitHeight : 0
            }
        }
    }

    // ─── Bottom Bar ────────────────────────────────────────────
    Rectangle {
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 42
        color: "#0d0d1a"
        opacity: 0.85

        RowLayout {
            anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter }
            anchors.leftMargin: 20; anchors.rightMargin: 20
            spacing: 6

            Text {
                text: "EduOS v1.0 Prototype"
                font.pixelSize: 10; color: "white"; opacity: 0.3
            }

            Item { Layout.fillWidth: true }

            ComboBox {
                id: sessionCombo
                Layout.preferredWidth: 110; Layout.preferredHeight: 24
                font.pixelSize: 10
                color: "#2a2a4e"
                textColor: "white"
                borderColor: "#3a3a5e"
                focusColor: "#c8913e"
                hoverColor: "#c8913e"
                model: sessionModel
                index: sessionModel.lastIndex
            }

            LayoutBox {
                Layout.preferredWidth: 50; Layout.preferredHeight: 24
                font.pixelSize: 10
            }

            Rectangle {
                Layout.preferredWidth: 1; Layout.preferredHeight: 16
                color: "#3a3a5e"
            }

            Button {
                Layout.preferredWidth: 28; Layout.preferredHeight: 24
                text: "⏾"; font.pixelSize: 11
                color: "#2a2a4e"; activeColor: "#c8913e"; pressedColor: "#b07a2e"
                radius: 4
                enabled: sddm.canSuspend
                onClicked: sddm.suspend()
            }
            Button {
                Layout.preferredWidth: 28; Layout.preferredHeight: 24
                text: "⟳"; font.pixelSize: 11
                color: "#2a2a4e"; activeColor: "#c8913e"; pressedColor: "#b07a2e"
                radius: 4
                enabled: sddm.canReboot
                onClicked: sddm.reboot()
            }
            Button {
                Layout.preferredWidth: 28; Layout.preferredHeight: 24
                text: "⏻"; font.pixelSize: 12
                color: "#4a2a2a"; activeColor: "#c8913e"; pressedColor: "#b07a2e"
                radius: 4
                enabled: sddm.canPowerOff
                onClicked: sddm.powerOff()
            }
        }
    }

    // ─── State ─────────────────────────────────────────────────
    property string selectedUser: ""
    property bool showOther: false

    function doLogin() {
        var username = showOther ? userNameInput.text : selectedUser
        var password = passwordInput.text

        if (username === "") {
            errorMessage.text = textConstants.promptUser
            if (showOther) userNameInput.focus = true
            return
        }
        if (password === "") {
            errorMessage.text = textConstants.emptyPassword
            passwordInput.focus = true
            return
        }
        errorMessage.text = ""
        loginButton.enabled = false
        sddm.login(username, password, sessionCombo ? sessionCombo.index : 0)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            errorMessage.text = textConstants.loginFailed
            passwordInput.text = ""
            passwordInput.focus = true
            loginButton.enabled = true
            shakeAnimation.start()
        }
        function onLoginSucceeded() {
            root.opacity = 0
        }
    }

    SequentialAnimation {
        id: shakeAnimation
        property Item target: loginFields
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: -6; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: 6; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: -4; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: 4; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: 0; duration: 40 }
    }
}
