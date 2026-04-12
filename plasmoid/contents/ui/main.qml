import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtWebSockets
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.extras as PlasmaExtras
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root

    property string currentMode: "extended"
    property bool wsConnected: false
    property string projectDir: "/home/marcus/Documents/repos/local-remote-workspace"

    // Host info
    property string hostDevice: "Desktop PC"
    property string hostOs: "Linux"
    property string hostScreen: "1920×1080"
    property string hostConnection: "Ethernet"
    property string hostIp: "192.168.50.181"

    // Client info
    property string clientDevice: "MacBook Air"
    property string clientOs: "macOS"
    property string clientScreen: "1440×900"
    property string clientConnection: "WiFi"
    property string clientIp: "192.168.50.22"

    preferredRepresentation: compactRepresentation
    switchWidth: Kirigami.Units.gridUnit * 14
    switchHeight: Kirigami.Units.gridUnit * 12

    // Panel icon
    compactRepresentation: MouseArea {
        Layout.minimumWidth: Kirigami.Units.iconSizes.medium
        Layout.preferredHeight: Kirigami.Units.iconSizes.medium
        hoverEnabled: true

        Kirigami.Icon {
            anchors.centerIn: parent
            source: "tv"
            width: Kirigami.Units.iconSizes.smallMedium
            height: Kirigami.Units.iconSizes.smallMedium
            color: "#ffffff"
        }
        Rectangle {
            width: 7; height: 7; radius: 3.5
            color: root.wsConnected ? "#347a36" : "#8f1f17"
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 0
        }

        onClicked: root.expanded = !root.expanded
    }

    // Popup
    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 30
        Layout.minimumHeight: Kirigami.Units.gridUnit * 30
        Layout.maximumHeight: Kirigami.Units.gridUnit * 55
        spacing: 0

        // Header
        PlasmaExtras.PlasmoidHeading {
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent

                Kirigami.Heading {
                    text: "ScreenLink"
                    level: 4
                    Layout.fillWidth: true
                }

                PlasmaComponents.ToolButton {
                    icon.name: "utilities-terminal"
                    PlasmaComponents.ToolTip.text: "View Logs"
                    PlasmaComponents.ToolTip.visible: hovered
                    onClicked: runCmd("konsole -e tail -f /tmp/screenlink.log")
                }
            }
        }

        // ---- Host section ----
        Item {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.topMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
            height: hostLabel.implicitHeight

            PlasmaComponents.Label {
                id: hostLabel
                text: "Host"
                color: Kirigami.Theme.disabledTextColor
                font: Kirigami.Theme.smallFont
            }
        }

        // Host item
        QQC2.ItemDelegate {
            Layout.fillWidth: true
            highlighted: hovered

            contentItem: RowLayout {
                spacing: Kirigami.Units.mediumSpacing

                Kirigami.Icon {
                    source: "computer"
                    Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                    Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    PlasmaComponents.Label {
                        text: root.hostDevice
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    PlasmaComponents.Label {
                        text: root.hostOs + " — " + root.hostScreen + " — " + root.hostConnection
                        color: Kirigami.Theme.disabledTextColor
                        font: Kirigami.Theme.smallFont
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }

                Rectangle {
                    width: 10; height: 10; radius: 5
                    color: root.wsConnected ? "#347a36" : "#8f1f17"
                    Layout.alignment: Qt.AlignVCenter
                }

                PlasmaComponents.ToolButton {
                    icon.name: hostDetailsVisible ? "collapse" : "expand"
                    property bool hostDetailsVisible: false
                    onClicked: hostDetailsVisible = !hostDetailsVisible
                    id: hostExpandBtn
                }
            }
        }

        // Host details
        ColumnLayout {
            visible: hostExpandBtn.hostDetailsVisible
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.gridUnit * 3 + Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            Layout.topMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "OS"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.hostOs; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "Screen"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.hostScreen; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "Connection"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.hostConnection; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "IP"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.hostIp; font: Kirigami.Theme.smallFont }
            }
        }

        Kirigami.Separator { Layout.fillWidth: true; Layout.topMargin: Kirigami.Units.smallSpacing }

        // ---- Client section ----
        Item {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.topMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
            height: clientLabel.implicitHeight

            PlasmaComponents.Label {
                id: clientLabel
                text: root.wsConnected ? "Connected" : "Disconnected"
                color: Kirigami.Theme.disabledTextColor
                font: Kirigami.Theme.smallFont
            }
        }

        // Client item (online)
        QQC2.ItemDelegate {
            Layout.fillWidth: true
            visible: root.wsConnected
            highlighted: hovered

            contentItem: RowLayout {
                spacing: Kirigami.Units.mediumSpacing

                Kirigami.Icon {
                    source: "computer-laptop"
                    Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                    Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    PlasmaComponents.Label {
                        text: root.currentMode === "extended" ? "Extended Screen" : "Remote Desktop"
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    PlasmaComponents.Label {
                        text: {
                            if (root.currentMode === "extended")
                                return root.clientDevice + " — " + root.clientScreen
                            else
                                return root.clientDevice
                        }
                        color: Kirigami.Theme.disabledTextColor
                        font: Kirigami.Theme.smallFont
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }

                // Mode switch button — outlined on hover
                QQC2.AbstractButton {
                    id: modeSwitchBtn
                    implicitWidth: modeBtnRow.implicitWidth + Kirigami.Units.largeSpacing * 3
                    implicitHeight: Kirigami.Units.gridUnit * 1.8
                    

                    background: Rectangle {
                        radius: Kirigami.Units.smallSpacing
                        color: "transparent"
                        border.width: 1
                        border.color: modeSwitchBtn.hovered ? Qt.rgba(1,1,1,0.3) : Qt.rgba(1,1,1,0.1)
                        Behavior on border.color { ColorAnimation { duration: 100 } }
                    }

                    contentItem: RowLayout {
                        id: modeBtnRow
                        spacing: Kirigami.Units.small
                        Layout.leftMargin: 4

                        Kirigami.Icon {
                            Layout.leftMargin: Kirigami.Units.largeSpacing
                            source: root.currentMode === "extended" ? "osd-duplicate" : "osd-sbs-sright"
                            Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium
                            Layout.preferredHeight: Kirigami.Units.iconSizes.smallMedium
                            Layout.rightMargin: Kirigami.Units.largeSpacing * -1
                        }

                        PlasmaComponents.Label {
                            text: root.currentMode === "extended" ? "Remote" : "Extend"
                            font: Kirigami.Theme.smallFont
                        }
                    }

                    onClicked: sendMode(root.currentMode === "extended" ? "remote" : "extended")
                }

                PlasmaComponents.ToolButton {
                    icon.name: clientDetailsVisible ? "collapse" : "expand"
                    property bool clientDetailsVisible: false
                    onClicked: clientDetailsVisible = !clientDetailsVisible
                    id: clientExpandBtn
                }
            }
        }

        // Client details
        ColumnLayout {
            visible: clientExpandBtn.clientDetailsVisible && root.wsConnected
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.gridUnit * 3 + Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            Layout.topMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "Device"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.clientDevice; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "OS"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.clientOs; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "Screen"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.clientScreen; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "Connection"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.clientConnection; font: Kirigami.Theme.smallFont }
            }
            RowLayout { spacing: Kirigami.Units.largeSpacing
                PlasmaComponents.Label { text: "IP"; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; Layout.preferredWidth: 80 }
                PlasmaComponents.Label { text: root.clientIp; font: Kirigami.Theme.smallFont }
            }
        }

        // Offline item
        QQC2.ItemDelegate {
            Layout.fillWidth: true
            visible: !root.wsConnected
            highlighted: hovered

            contentItem: RowLayout {
                spacing: Kirigami.Units.mediumSpacing

                Kirigami.Icon {
                    source: "computer-laptop"
                    Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                    Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                    opacity: 0.4
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    PlasmaComponents.Label {
                        text: root.clientDevice
                        opacity: 0.4
                        Layout.fillWidth: true
                    }

                    PlasmaComponents.Label {
                        text: "Service not running"
                        color: Kirigami.Theme.disabledTextColor
                        font: Kirigami.Theme.smallFont
                        Layout.fillWidth: true
                    }
                }

                PlasmaComponents.ToolButton {
                    icon.name: "view-refresh"
                    PlasmaComponents.ToolTip.text: "Reconnect"
                    PlasmaComponents.ToolTip.visible: hovered
                    onClicked: { ws.active = false; ws.active = true }
                }
            }
        }

        Item { Layout.fillHeight: true }

        // Footer
        Kirigami.Separator { Layout.fillWidth: true }

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            PlasmaComponents.ToolButton {
                icon.name: "media-playback-start"
                PlasmaComponents.ToolTip.text: "Start"
                PlasmaComponents.ToolTip.visible: hovered
                onClicked: runCmd(root.projectDir + "/ctl.sh start")
            }

            PlasmaComponents.ToolButton {
                icon.name: "media-playback-stop"
                PlasmaComponents.ToolTip.text: "Stop"
                PlasmaComponents.ToolTip.visible: hovered
                onClicked: runCmd(root.projectDir + "/ctl.sh stop")
            }

            PlasmaComponents.ToolButton {
                icon.name: "view-refresh"
                PlasmaComponents.ToolTip.text: "Restart"
                PlasmaComponents.ToolTip.visible: hovered
                onClicked: runCmd(root.projectDir + "/ctl.sh restart")
            }

            Item { Layout.fillWidth: true }
        }
    }

    WebSocket {
        id: ws
        url: "ws://localhost:8085"
        active: true

        onStatusChanged: function() {
            if (ws.status === WebSocket.Open) root.wsConnected = true
            else if (ws.status === WebSocket.Closed || ws.status === WebSocket.Error) root.wsConnected = false
        }

        onTextMessageReceived: function(message) {
            var data = JSON.parse(message)
            if (data.mode) root.currentMode = data.mode
        }
    }

    Timer {
        id: pollTimer
        interval: 5000
        running: true
        repeat: true
        onTriggered: {
            if (ws.status !== WebSocket.Open) { ws.active = false; ws.active = true }
        }
    }

    P5Support.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []
        onNewData: function(source, data) { disconnectSource(source) }
    }

    function sendMode(mode) {
        if (ws.status === WebSocket.Open) ws.sendTextMessage(JSON.stringify({ mode: mode }))
    }

    function runCmd(cmd) { executable.connectSource(cmd) }
}
