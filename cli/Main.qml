import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtWebEngine

Window {
    id: root
    visible: true
    visibility: Window.FullScreen
    title: "Vistro Virtual Machine"
    color: "#000000"

    FontLoader {
        id: dosFont
        source: Qt.resolvedUrl("../assets/perfectdosvga.ttf")
    }

    property string promptText: "admin@vistro:~/vistro/root> "
    property var    lines:      []
    property string inputText:  ""
    property bool   browserOpen: false

    function ansiToHtml(raw) {
        var s = raw
        s = s.replace(/&/g, "&amp;")
        s = s.replace(/</g, "&lt;")
        s = s.replace(/>/g, "&gt;")
        s = s.replace(/\x1b\[31m/g, '<font color="#ff0000">')
        s = s.replace(/\x1b\[0m/g,  "</font>")
        s = s.replace(/\x1b\[[0-9;]*m/g, "")
        s = s.replace(/ /g, "&#32;")
        return '<span style="white-space:pre">' + s + '</span>'
    }

    function appendOutput(raw) {
        var newLines = lines.slice()
        var rawLines = raw.split("\n")
        for (var i = 0; i < rawLines.length; i++) {
            newLines.push(ansiToHtml(rawLines[i]))
        }
        lines = newLines
        flickable.contentY = Math.max(0, flickable.contentHeight - flickable.height)
    }

    function submitCommand() {
        var trimmed = inputText.trim()
        if (trimmed === "discord") {
            browserOpen = true
            inputText = ""
            return
        }
        var newLines = lines.slice()
        newLines.push(promptText + trimmed)
        lines = newLines
        inputText = ""
        if (trimmed !== "")
            vistroBridge.runCommand(trimmed)
        flickable.contentY = Math.max(0, flickable.contentHeight - flickable.height)
    }

    Connections {
        target: vistroBridge
        function onSendOutput(output) { root.appendOutput(output) }
        function onSendPrompt(p)      { root.promptText = p }
        function onSendClear()        { root.lines = []; flickable.contentY = 0 }
    }

    Component.onCompleted: {
        vistroBridge.getPrompt(function(p) { root.promptText = p })
        inputField.forceActiveFocus()
    }

    MouseArea {
        anchors.fill: parent
        onClicked: inputField.forceActiveFocus()
    }

    Flickable {
        id: flickable
        anchors.fill: parent
        visible: !root.browserOpen
        contentWidth:  parent.width
        contentHeight: contentCol.implicitHeight
        clip: true

        Column {
            id: contentCol
            width:         flickable.width
            spacing:       0
            topPadding:    4
            leftPadding:   8
            rightPadding:  8
            bottomPadding: 4

            Repeater {
                model: root.lines
                Text {
                    width:          contentCol.width - 16
                    text:           modelData
                    textFormat:     Text.RichText
                    color:          "#ffffff"
                    font.family:    dosFont.name
                    font.pixelSize: 16
                    lineHeight:     1.2
                }
            }

            Row {
                id: inputRow
                width:   contentCol.width - 16
                spacing: 0

                Text {
                    id:             promptLabel
                    text:           root.promptText
                    color:          "#ffffff"
                    font.family:    dosFont.name
                    font.pixelSize: 16
                    lineHeight:     1.2
                }

                Row {
                    spacing: 0

                    Text {
                        id:             displayInput
                        text:           root.inputText
                        color:          "#ffffff"
                        font.family:    dosFont.name
                        font.pixelSize: 16
                        lineHeight:     1.2
                    }

                    Rectangle {
                        id:     cursor
                        width:  8
                        height: 2
                        color:  "#ffffff"
                        anchors.verticalCenter:       displayInput.verticalCenter
                        anchors.verticalCenterOffset: 7

                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            PropertyAnimation { to: 1; duration: 0 }
                            PauseAnimation    { duration: 500 }
                            PropertyAnimation { to: 0; duration: 0 }
                            PauseAnimation    { duration: 500 }
                        }
                    }
                }

                TextInput {
                    id:      inputField
                    width:   1
                    height:  1
                    opacity: 0
                    focus:   true
                    font.family:    dosFont.name
                    font.pixelSize: 16

                    onTextChanged: { root.inputText = text }

                    Keys.onReturnPressed: { root.submitCommand(); text = "" }
                    Keys.onEnterPressed:  { root.submitCommand(); text = "" }
                }
            }
        }
    }

    Rectangle {
        id: browserContainer
        anchors.fill: parent
        visible: root.browserOpen
        color: "#000000"

        Rectangle {
            id: browserBar
            anchors.top:   parent.top
            anchors.left:  parent.left
            anchors.right: parent.right
            height: 36
            color: "#1a1a1a"

            Row {
                anchors.fill:    parent
                anchors.margins: 4
                spacing: 8

                Rectangle {
                    width:  80
                    height: 28
                    color:  closeBarArea.containsMouse ? "#333333" : "#222222"
                    radius: 4

                    Text {
                        anchors.centerIn: parent
                        text:  "â† Fechar"
                        color: "#ffffff"
                        font.pixelSize: 13
                    }

                    MouseArea {
                        id: closeBarArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            root.browserOpen = false
                            inputField.forceActiveFocus()
                        }
                    }
                }

                Rectangle {
                    width:  browserBar.width - 108
                    height: 28
                    color:  "#111111"
                    radius: 4

                    Text {
                        anchors.centerIn: parent
                        text:  webView.url
                        color: "#aaaaaa"
                        font.pixelSize: 12
                        elide: Text.ElideMiddle
                        width: parent.width - 8
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }

        WebEngineView {
            id: webView
            anchors.top:    browserBar.bottom
            anchors.left:   parent.left
            anchors.right:  parent.right
            anchors.bottom: parent.bottom
            url: root.browserOpen ? "https://discord.com/app" : ""

            profile.httpUserAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
    }
}
