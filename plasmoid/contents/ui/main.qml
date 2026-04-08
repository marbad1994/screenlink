import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtWebSockets
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root

    property string currentMode: "extended"
    property bool wsConnected: false
    property string projectDir: "/home/marcus/Documents/repos/local-remote-workspace"

    preferredRepresentation: compactRepresentation

    compactRepresentation: MouseArea {
        Layout.minimumWidth: row.implicitWidth + 16
        Layout.preferredHeight: Kirigami.Units.iconSizes.medium
        hoverEnabled: true

        RowLayout {
            id: row
            anchors.centerIn: parent
            spacing: 6

            Kirigami.Icon {
                source: root.currentMode === "extended" ? "video-display" : "input-gaming"
                Layout.preferredWidth: Kirigami.Units.iconSizes.small
                Layout.preferredHeight: Kirigami.Units.iconSizes.small
            }

            PlasmaComponents.Label {
                text: root.currentMode === "extended" ? "Ext" : "Rmt"
                font.pointSize: 9
            }

            Rectangle {
                width: 8; height: 8; radius: 4
                color: root.wsConnected ? "#4f4" : "#f44"
            }
        }

        onClicked: {
            root.expanded = !root.expanded
        }
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: 230
        Layout.preferredHeight: 280
        spacing: 6

        PlasmaComponents.Label {
            text: "ScreenLink"
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: Qt.rgba(1,1,1,0.1) }

        QQC2.Button {
            text: "Extended Screen"
            icon.name: "video-display"
            Layout.fillWidth: true
            highlighted: root.currentMode === "extended"
            onClicked: sendMode("extended")
        }

        QQC2.Button {
            text: "Remote Desktop"
            icon.name: "input-gaming"
            Layout.fillWidth: true
            highlighted: root.currentMode === "remote"
            onClicked: sendMode("remote")
        }

        QQC2.Button {
            text: "Console"
            icon.name: "utilities-terminal"
            Layout.fillWidth: true
            onClicked: Qt.openUrlExternally("http://localhost:8083/control.html")
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: Qt.rgba(1,1,1,0.1) }

        RowLayout {
            Layout.fillWidth: true
            spacing: 4

            QQC2.Button {
                text: "Start"
                icon.name: "media-playback-start"
                Layout.fillWidth: true
                onClicked: runCmd("bash " + root.projectDir + "/start.sh &")
            }

            QQC2.Button {
                text: "Stop"
                icon.name: "media-playback-stop"
                Layout.fillWidth: true
                onClicked: runCmd("bash " + root.projectDir + "/stop.sh")
            }

            QQC2.Button {
                text: "Restart"
                icon.name: "view-refresh"
                Layout.fillWidth: true
                onClicked: runCmd("bash " + root.projectDir + "/stop.sh && sleep 2 && bash " + root.projectDir + "/start.sh &")
            }
        }

        Item { Layout.fillHeight: true }

        PlasmaComponents.Label {
            text: root.wsConnected ? "Connected" : "Disconnected"
            color: root.wsConnected ? "#4f4" : "#f44"
            font.pointSize: 8
            Layout.alignment: Qt.AlignHCenter
        }
    }

    WebSocket {
        id: ws
        url: "ws://localhost:8085"
        active: true

        onStatusChanged: function() {
            if (ws.status === WebSocket.Open) {
                root.wsConnected = true
            } else if (ws.status === WebSocket.Closed || ws.status === WebSocket.Error) {
                root.wsConnected = false
                reconnectTimer.start()
            }
        }

        onTextMessageReceived: function(message) {
            var data = JSON.parse(message)
            if (data.mode) root.currentMode = data.mode
        }
    }

    Timer {
        id: reconnectTimer
        interval: 3000
        onTriggered: { ws.active = false; ws.active = true }
    }

    P5Support.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []
        onNewData: function(source, data) {
            disconnectSource(source)
        }
    }

    function sendMode(mode) {
        if (ws.status === WebSocket.Open) {
            ws.sendTextMessage(JSON.stringify({ mode: mode }))
        }
    }

    function runCmd(cmd) {
        executable.connectSource(cmd)
    }
}
