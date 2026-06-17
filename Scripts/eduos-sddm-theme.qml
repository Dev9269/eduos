import QtQuick 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#080e1a"

    TextConstants { id: textConstants }

    // ─── Background Layers ─────────────────────────────────────────
    Item {
        id: backgroundLayer
        anchors.fill: parent

        // Base gradient
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#0a1628" }
                GradientStop { position: 0.3; color: "#0d1b2a" }
                GradientStop { position: 0.6; color: "#111827" }
                GradientStop { position: 1.0; color: "#080e1a" }
            }
        }

        // Subtle dot grid pattern
        Row {
            anchors.fill: parent
            spacing: 48
            Repeater {
                model: Math.ceil(root.width / 48) + 1
                Column {
                    spacing: 48
                    Repeater {
                        model: Math.ceil(root.height / 48) + 1
                        Rectangle {
                            width: 2; height: 2; radius: 1
                            color: "#55688b"; opacity: 0.08
                        }
                    }
                }
            }
        }

        // Decorative curves — top right
        Canvas {
            x: parent.width - 400; y: -100
            width: 500; height: 500
            contextType: "2d"
            onPaint: {
                context.strokeStyle = Qt.rgba(37/255, 99/255, 235/255, 0.06)
                context.lineWidth = 2
                for (let i = 0; i < 5; i++) {
                    context.beginPath()
                    context.arc(250, 250, 60 + i * 40, 0, Math.PI * 2)
                    context.stroke()
                }
            }
        }

        // Decorative curves — bottom left
        Canvas {
            x: -200; y: parent.height - 400
            width: 500; height: 500
            contextType: "2d"
            onPaint: {
                context.strokeStyle = Qt.rgba(124/255, 58/255, 237/255, 0.06)
                context.lineWidth = 2
                for (let i = 0; i < 5; i++) {
                    context.beginPath()
                    context.arc(250, 250, 60 + i * 40, 0, Math.PI * 2)
                    context.stroke()
                }
            }
        }

        // Accent glow behind login card
        Rectangle {
            x: parent.width / 2 - 250
            y: parent.height / 2 - 200
            width: 500; height: 400
            radius: 250
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(37/255, 99/255, 235/255, 0.08) }
                GradientStop { position: 0.5; color: Qt.rgba(124/255, 58/255, 237/255, 0.04) }
                GradientStop { position: 1.0; color: "transparent" }
            }
            opacity: 0
            NumberAnimation on opacity { from: 0; to: 1; duration: 2000; easing.type: Easing.InQuad }
        }
    }

    // ─── Top Bar ───────────────────────────────────────────────────
    Item {
        anchors { left: parent.left; right: parent.right; top: parent.top; topMargin: 24 }
        height: 60

        // Branding — top left
        Column {
            anchors { left: parent.left; leftMargin: 36; verticalCenter: parent.verticalCenter }
            spacing: 2
            Row {
                spacing: 10
                Rectangle {
                    width: 32; height: 32; radius: 6
                    color: "#2563eb"
                    Text { anchors.centerIn: parent; text: "E"; font { pixelSize: 18; bold: true }; color: "white" }
                }
                Column {
                    spacing: 1
                    anchors.verticalCenter: parent.verticalCenter
                    Text { text: "EduOS"; font { pixelSize: 18; bold: true }; color: "white"; opacity: 0.9 }
                    Text { text: "Engineering Education Edition"; font.pixelSize: 10; color: "white"; opacity: 0.4 }
                }
            }
        }

        // Clock — top right
        Column {
            anchors { right: parent.right; rightMargin: 36; verticalCenter: parent.verticalCenter }
            horizontalAlignment: Text.AlignRight
            spacing: 0
            Text {
                id: timeLabel
                text: Qt.formatTime(new Date(), "hh:mm")
                font { pixelSize: 28; weight: Font.Light }
                color: "white"; opacity: 0.85
            }
            Timer { interval: 1000; running: true; repeat: true; onTriggered: timeLabel.text = Qt.formatTime(new Date(), "hh:mm") }
            Text {
                text: Qt.formatDate(new Date(), "dddd, MMMM d")
                font.pixelSize: 11
                color: "white"; opacity: 0.45
            }
            Text {
                text: sddm.hostName
                font.pixelSize: 10
                color: "white"; opacity: 0.3
            }
        }
    }

    // ─── Login Card Container (glassmorphism) ──────────────────────
    Item {
        anchors.centerIn: parent
        width: 380; height: cardContent.height + 80

        // Drop shadow
        RectangularGlow {
            anchors.fill: cardBackground
            anchors.topMargin: 4
            glowRadius: 40
            spread: 0.2
            color: "#1a000000"
        }

        // Glass background
        Rectangle {
            id: cardBackground
            anchors.fill: parent
            radius: 20
            color: "#1a152842"
            border { color: "#30ffffff"; width: 1 }

            // Inner gradient overlay for glass depth
            Rectangle {
                anchors.fill: parent; radius: parent.radius
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.rgba(255/255, 255/255, 255/255, 0.05) }
                    GradientStop { position: 1.0; color: Qt.rgba(0/255, 0/255, 0/255, 0.1) }
                }
            }
        }

        // Fade-in entrance animation
        NumberAnimation on opacity { from: 0; to: 1; duration: 600; easing.type: Easing.OutCubic }
        NumberAnimation on y { from: parent ? parent.height * 0.05 : 0; to: 0; duration: 600; easing.type: Easing.OutCubic }
    }

    // ─── Card Content ──────────────────────────────────────────────
    Column {
        id: cardContent
        anchors.centerIn: parent
        width: 320
        spacing: 20

        // Spacer
        Item { width: 1; height: 8 }

        // Avatar circle
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 72; height: 72; radius: 36
            color: "#1a2744"
            border { color: "#40ffffff"; width: 2 }

            Text {
                anchors.centerIn: parent; text: "👤"; font.pixelSize: 32
            }

            // Subtle ring glow
            Rectangle {
                anchors.centerIn: parent
                width: 80; height: 80; radius: 40
                color: "transparent"
                border { color: Qt.rgba(37/255, 99/255, 235/255, 0.25); width: 1 }
            }
        }

        // Welcome text
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Welcome back"
            font { pixelSize: 20; weight: Font.Light }
            color: "white"; opacity: 0.8
        }

        // Username field
        TextBox {
            id: userNameInput
            width: parent.width; height: 44
            font.pixelSize: 14
            textColor: "white"
            color: "#1a1a32"
            borderColor: "#2a2a4e"
            focusColor: "#2563eb"
            hoverColor: "#3a7bc8"
            radius: 10
            text: sddm.lastUser || ""

            Keys.onPressed: function(event) {
                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                    passwordInput.focus = true; event.accepted = true
                }
            }
        }

        // Password field
        PasswordBox {
            id: passwordInput
            width: parent.width; height: 44
            font.pixelSize: 14
            textColor: "white"
            radius: 10
            focus: true

            Keys.onPressed: function(event) {
                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                    doLogin(); event.accepted = true
                }
            }
        }

        // Sign In button
        Button {
            id: loginButton
            width: parent.width; height: 46
            text: "Sign In →"
            color: "#2563eb"
            activeColor: "#3b82f6"
            pressedColor: "#1d4ed8"
            font.pixelSize: 15

            radius: 10

            onClicked: doLogin()
            Keys.onReturnPressed: doLogin()
        }

        // Error message
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

        // Spacer
        Item { width: 1; height: 4 }
    }

    // ─── Bottom Bar ────────────────────────────────────────────────
    Rectangle {
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 44
        color: "#080e1a"
        opacity: 0.8

        RowLayout {
            anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter }
            anchors.leftMargin: 24; anchors.rightMargin: 24
            spacing: 8

            // System version
            Text {
                text: "EduOS v1.0 Prototype"
                font.pixelSize: 11
                color: "white"; opacity: 0.35
            }

            Item { Layout.fillWidth: true }

            // Accessibility/VKB indicator (hidden unless keyboard is available)
            Text {
                text: "⌨"
                font.pixelSize: 14
                color: "white"; opacity: 0.3
                visible: false  // Could be used as keyboard toggle in future
            }

            // Session selector
            ComboBox {
                id: sessionCombo
                Layout.preferredWidth: 120; Layout.preferredHeight: 26
                font.pixelSize: 11
                color: "#1a1a32"
                textColor: "white"
                borderColor: "#2a2a4e"
                focusColor: "#2563eb"
                hoverColor: "#3b82f6"
                model: sessionModel
                index: sessionModel.lastIndex
            }

            // Keyboard layout
            LayoutBox {
                Layout.preferredWidth: 60; Layout.preferredHeight: 26
                font.pixelSize: 11
            }

            // Separator
            Rectangle {
                Layout.preferredWidth: 1; Layout.preferredHeight: 18
                color: "#2a2a4e"
            }

            // Power buttons
            Button {
                Layout.preferredWidth: 30; Layout.preferredHeight: 26
                text: "⏾"; font.pixelSize: 12
                color: "#1a1a32"; activeColor: "#3b82f6"; pressedColor: "#1d4ed8"
                radius: 4
                enabled: sddm.canSuspend
                onClicked: sddm.suspend()
            }
            Button {
                Layout.preferredWidth: 30; Layout.preferredHeight: 26
                text: "⟳"; font.pixelSize: 12
                color: "#1a1a32"; activeColor: "#3b82f6"; pressedColor: "#1d4ed8"
                radius: 4
                enabled: sddm.canReboot
                onClicked: sddm.reboot()
            }
            Button {
                Layout.preferredWidth: 30; Layout.preferredHeight: 26
                text: "⏻"; font.pixelSize: 13
                color: "#1a1a32"; activeColor: "#ef4444"; pressedColor: "#dc2626"
                radius: 4
                enabled: sddm.canPowerOff
                onClicked: sddm.powerOff()
            }
        }
    }

    // ─── Functions ─────────────────────────────────────────────────
    function doLogin() {
        var username = userNameInput.text
        var password = passwordInput.text
        if (username === "") {
            errorMessage.text = textConstants.promptUser
            userNameInput.focus = true
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

    // ─── Shake animation on login failure ──────────────────────────
    SequentialAnimation {
        id: shakeAnimation
        property Item target: cardContent
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: -8; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: 8; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: -5; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: 5; duration: 40 }
        NumberAnimation { target: shakeAnimation.target; property: "x"; to: 0; duration: 40 }
    }
}
