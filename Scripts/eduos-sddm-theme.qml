import QtQuick 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0a0a14"

    TextConstants { id: textConstants }

    // ─── Background (blurred wallpaper) ────────────────────────
    Item {
        id: backgroundLayer
        anchors.fill: parent

        Image {
            id: bgImage
            anchors.fill: parent
            source: "file:///usr/share/wallpapers/eduos-wallpaper-default.png"
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
            cache: true
            visible: false
        }

        FastBlur {
            anchors.fill: bgImage
            source: bgImage
            radius: 48
            transparentBorder: false
        }

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#880a0a14" }
                GradientStop { position: 0.5; color: "#660a0a14" }
                GradientStop { position: 1.0; color: "#cc08080e" }
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

    // ─── Glass Panel (centered card) ───────────────────────────
    Item {
        anchors.centerIn: parent
        width: 380
        height: 400

        // Frosted glass background
        Rectangle {
            id: glassPanel
            anchors.fill: parent
            radius: 20
            color: Qt.rgba(15, 15, 30, 0.35)
            border { color: Qt.rgba(255, 255, 255, 0.12); width: 1 }

            layer.enabled: true
            layer.effect: GaussianBlur {
                source: backgroundLayer
                radius: 16
                samples: 16
                transparentBorder: true
            }

            // Inner glass highlight
            Rectangle {
                anchors { top: parent.top; left: parent.left; right: parent.right }
                height: 1
                color: Qt.rgba(255, 255, 255, 0.15)
            }
        }

        // Content on top of glass
        Column {
            anchors { fill: parent; margins: 28 }
            spacing: 0

            NumberAnimation on opacity { from: 0; to: 1; duration: 600; easing.type: Easing.OutCubic }

            // Welcome text
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Welcome"
                font { pixelSize: 20; weight: Font.Light }
                color: "white"; opacity: 0.8
                bottomPadding: 20
            }

            // ─── User Selection ────────────────────────────────
            Item {
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

                            // Glass avatar circle
                            Rectangle {
                                anchors.horizontalCenter: parent.horizontalCenter
                                width: 56; height: 56; radius: 28
                                color: (userList.currentIndex === index)
                                    ? Qt.rgba(200, 145, 62, 0.6)
                                    : Qt.rgba(255, 255, 255, 0.08)
                                border {
                                    color: (userList.currentIndex === index)
                                        ? Qt.rgba(232, 184, 75, 0.8)
                                        : Qt.rgba(255, 255, 255, 0.15)
                                    width: (userList.currentIndex === index) ? 2 : 1
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
                                color: (userList.currentIndex === index) ? "#e8b84b" : Qt.rgba(255, 255, 255, 0.7)
                                opacity: (userList.currentIndex === index) ? 1.0 : 0.6
                                elide: Text.ElideRight
                                maximumLineCount: 1
                            }
                        }
                    }
                }
            }

            // ─── Other User ────────────────────────────────────
            Item {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 100; height: 70

                Column {
                    anchors.centerIn: parent
                    spacing: 6

                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 48; height: 48; radius: 24
                        color: showOther
                            ? Qt.rgba(200, 145, 62, 0.6)
                            : Qt.rgba(255, 255, 255, 0.08)
                        border {
                            color: showOther
                                ? Qt.rgba(232, 184, 75, 0.8)
                                : Qt.rgba(255, 255, 255, 0.15)
                            width: showOther ? 2 : 1
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "\u2026"
                            font { pixelSize: 22; weight: Font.Bold }
                            color: "white"; opacity: 0.7
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
                        color: showOther ? "#e8b84b" : Qt.rgba(255, 255, 255, 0.6)
                        opacity: showOther ? 1.0 : 0.5
                    }
                }
            }

            // Spacer
            Item { width: 1; height: 16 }

            // ─── Glass Input Fields ────────────────────────────
            Column {
                id: loginFields
                width: parent.width
                spacing: 10

                Rectangle {
                    width: parent.width; height: 44; radius: 8
                    visible: showOther
                    color: Qt.rgba(255, 255, 255, 0.06)
                    border { color: showOther ? Qt.rgba(200, 145, 62, 0.5) : Qt.rgba(255, 255, 255, 0.1); width: 1 }

                    TextBox {
                        id: userNameInput
                        anchors.fill: parent
                        anchors.margins: 0
                        font.pixelSize: 14
                        textColor: "white"
                        color: "transparent"
                        borderColor: "transparent"
                        focusColor: "transparent"
                        hoverColor: "transparent"
                        radius: 8
                        placeholderText: "Username"
                        text: ""
                        background: null

                        Keys.onPressed: function(event) {
                            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                passwordInput.focus = true; event.accepted = true
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width; height: 44; radius: 8
                    color: Qt.rgba(255, 255, 255, 0.06)
                    border { color: Qt.rgba(255, 255, 255, 0.1); width: 1 }

                    PasswordBox {
                        id: passwordInput
                        anchors.fill: parent
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
                }

                Rectangle {
                    width: parent.width; height: 46; radius: 8
                    color: Qt.rgba(200, 145, 62, 0.5)
                    border { color: Qt.rgba(200, 145, 62, 0.3); width: 1 }

                    Button {
                        id: loginButton
                        anchors.fill: parent
                        text: "Sign In"
                        color: "transparent"
                        activeColor: "transparent"
                        pressedColor: "transparent"
                        font.pixelSize: 15
                        radius: 8

                        onClicked: doLogin()
                        Keys.onReturnPressed: doLogin()
                    }
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
    }

    // ─── Bottom Bar ────────────────────────────────────────────
    Rectangle {
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 42
        color: Qt.rgba(0, 0, 0, 0.25)
        opacity: 0.9

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
                color: Qt.rgba(255, 255, 255, 0.06)
                textColor: "white"
                borderColor: Qt.rgba(255, 255, 255, 0.1)
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
                color: Qt.rgba(255, 255, 255, 0.1)
            }

            Button {
                Layout.preferredWidth: 28; Layout.preferredHeight: 24
                text: "\u23FE"; font.pixelSize: 11
                color: Qt.rgba(255, 255, 255, 0.06)
                activeColor: "#c8913e"
                pressedColor: Qt.rgba(200, 145, 62, 0.3)
                radius: 4
                enabled: sddm.canSuspend
                onClicked: sddm.suspend()
            }
            Button {
                Layout.preferredWidth: 28; Layout.preferredHeight: 24
                text: "\u27F3"; font.pixelSize: 11
                color: Qt.rgba(255, 255, 255, 0.06)
                activeColor: "#c8913e"
                pressedColor: Qt.rgba(200, 145, 62, 0.3)
                radius: 4
                enabled: sddm.canReboot
                onClicked: sddm.reboot()
            }
            Button {
                Layout.preferredWidth: 28; Layout.preferredHeight: 24
                text: "\u23FB"; font.pixelSize: 12
                color: Qt.rgba(200, 60, 60, 0.2)
                activeColor: "#c8913e"
                pressedColor: Qt.rgba(200, 145, 62, 0.3)
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
