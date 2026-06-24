import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0a0a14"

    property color accentPrimary: "#6c63ff"
    property color accentSecondary: "#4fc3f7"
    property color glassCard: Qt.rgba(255/255, 255/255, 255/255, 0.04)
    property color glassBorder: Qt.rgba(255/255, 255/255, 255/255, 0.08)
    property color textPrimary: Qt.rgba(255/255, 255/255, 255/255, 0.92)
    property color textSecondary: Qt.rgba(255/255, 255/255, 255/255, 0.65)
    property string backgroundImage: config.background || ""

    // ── Animated gradient background ──
    Rectangle {
        id: bgCanvas
        anchors.fill: parent
        color: "#0a0a14"

        AnimatedGradient {
            anchors.fill: parent
            color1: "#0a0a14"
            color2: "#0f0f1e"
            color3: "#151530"
            duration: 8000
        }
    }

    // ── Background image overlay if set ──
    Image {
        id: bgImage
        anchors.fill: parent
        source: backgroundImage
        fillMode: Image.PreserveAspectCrop
        opacity: 0.3
        visible: backgroundImage !== ""
    }

    // ── Glass blur overlay ──
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(10/255, 10/255, 20/255, 0.3)
    }

    // ── Login card (centered) ──
    Item {
        anchors.centerIn: parent
        width: 420
        height: mainColumn.height + 80

        RectangularGlow {
            anchors.fill: loginCard
            glowRadius: 40
            spread: 0.1
            color: Qt.rgba(108/255, 99/255, 255/255, 0.08)
            cornerRadius: 24
        }

        Rectangle {
            id: loginCard
            anchors.centerIn: parent
            width: 420
            height: mainColumn.height + 80
            radius: 24
            color: Qt.rgba(15/255, 15/255, 30/255, 0.95)

            Rectangle {
                anchors.fill: parent
                radius: 24
                color: "transparent"
                border.width: 1
                border.color: Qt.rgba(108/255, 99/255, 255/255, 0.15)
            }

            ColumnLayout {
                id: mainColumn
                anchors.centerIn: parent
                width: parent.width - 80
                spacing: 20

                // ── Logo area ──
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "◆"
                        font.pixelSize: 48
                        color: accentPrimary
                        font.bold: true
                    }

                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "EduOS"
                        font.pixelSize: 28
                        font.weight: Font.Bold
                        color: textPrimary
                        letterSpacing: -0.5
                    }

                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: config.institution || "Educational Operating System"
                        font.pixelSize: 12
                        color: textSecondary
                        visible: true
                    }
                }

                // ── Spacing ──
                Item { height: 8; width: 1 }

                // ── Username field ──
                TextField {
                    id: userField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    placeholderText: "Username"
                    font.pixelSize: 14
                    color: textPrimary
                    leftPadding: 16
                    rightPadding: 16

                    background: Rectangle {
                        radius: 12
                        color: Qt.rgba(255/255, 255/255, 255/255, 0.04)
                        border.width: 1
                        border.color: userField.activeFocus ? accentPrimary : glassBorder

                        Behavior on border.color {
                            ColorAnimation { duration: 200 }
                        }
                    }
                }

                // ── Password field ──
                TextField {
                    id: passField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    placeholderText: "Password"
                    font.pixelSize: 14
                    color: textPrimary
                    echoMode: TextInput.Password
                    leftPadding: 16
                    rightPadding: 16

                    background: Rectangle {
                        radius: 12
                        color: Qt.rgba(255/255, 255/255, 255/255, 0.04)
                        border.width: 1
                        border.color: passField.activeFocus ? accentPrimary : glassBorder

                        Behavior on border.color {
                            ColorAnimation { duration: 200 }
                        }
                    }

                    Keys.onReturnPressed: loginAction()
                }

                // ── Login button ──
                Button {
                    id: loginBtn
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    text: "Sign In"

                    contentItem: Text {
                        text: parent.text
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 12
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: accentPrimary }
                            GradientStop { position: 1.0; color: accentSecondary }
                        }

                        Rectangle {
                            anchors.fill: parent
                            radius: 12
                            color: Qt.rgba(255/255, 255/255, 255/255, 0.1)
                            opacity: parent.parent.hovered ? 1.0 : 0.0

                            Behavior on opacity {
                                NumberAnimation { duration: 200 }
                            }
                        }
                    }

                    onClicked: loginAction()
                }

                // ── Session selector ──
                ComboBox {
                    id: sessionSelect
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    model: sessionModel
                    currentIndex: sessionModel.lastIndex
                    textRole: "name"
                    visible: sessionModel.count > 1

                    background: Rectangle {
                        radius: 10
                        color: Qt.rgba(255/255, 255/255, 255/255, 0.03)
                        border.width: 1
                        border.color: glassBorder
                    }

                    contentItem: Text {
                        text: sessionSelect.currentText
                        font.pixelSize: 12
                        color: textSecondary
                        leftPadding: 12
                        verticalAlignment: Text.AlignVCenter
                    }

                    indicator: Text {
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: "▼"
                        font.pixelSize: 8
                        color: textSecondary
                    }
                }

                // ── Virtual keyboard toggle (hidden by default) ──
                Item { height: 1; width: 1; visible: false }
            }
        }
    }

    // ── Clock ──
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height - 60
        text: Qt.formatDateTime(new Date(), "hh:mm AP")
        font.pixelSize: 16
        font.weight: Font.Medium
        color: textSecondary
        font.letterSpacing: 2
    }

    // ── Functions ──
    function loginAction() {
        sddm.login(userField.text, passField.text, sessionSelect.currentIndex);
    }
}

// ── AnimatedGradient component ──
Item {
    id: animatedGradient
    property color color1: "#0a0a14"
    property color color2: "#0f0f1e"
    property color color3: "#151530"
    property int duration: 6000

    ShaderEffect {
        anchors.fill: parent
        property color fromColor: animatedGradient.color1
        property color toColor: animatedGradient.color2
        property color accentColor: animatedGradient.color3
        property real time: 0.0

        NumberAnimation on time {
            from: 0; to: 1.0; duration: animatedGradient.duration
            loops: Animation.Infinite
        }

        fragmentShader: "
            varying highp vec2 qt_TexCoord0;
            uniform highp float time;
            uniform highp vec4 fromColor;
            uniform highp vec4 toColor;
            uniform highp vec4 accentColor;
            void main() {
                highp vec2 uv = qt_TexCoord0;
                highp float t = sin(time * 3.14159 * 2.0) * 0.5 + 0.5;
                highp float t2 = sin(time * 3.14159 * 2.0 + 1.5) * 0.5 + 0.5;
                highp vec3 color1 = mix(fromColor.rgb, toColor.rgb, uv.y * 0.6 + t * 0.4);
                highp vec3 color2 = mix(toColor.rgb, accentColor.rgb, uv.x * 0.3 + t2 * 0.3);
                highp vec3 finalColor = mix(color1, color2, 0.3 + uv.x * 0.2);
                gl_FragColor = vec4(finalColor, 1.0);
            }
        "
    }
}
