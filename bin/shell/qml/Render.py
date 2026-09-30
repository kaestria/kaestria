import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
def qmlString(value) -> str:
    text = str(value or "")
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'
def qmlNumber(value, default: int) -> str:
    try:
        return str(int(value))
    except Exception:
        return str(default)
def renderWindow(winId: str, win: dict, children: str) -> str:
    title = qmlString(win.get("title", winId))
    width = qmlNumber(win.get("width", 1280), 1280)
    height = qmlNumber(win.get("height", 720), 720)
    color = qmlString(win.get("color", "#F8F4EC"))
    return (
        'Window {\n'
        f'    id: {winId}\n'
        f'    width: {width}\n'
        f'    height: {height}\n'
        '    visible: true\n'
        '    visibility: Window.FullScreen\n'
        f'    title: {title}\n'
        f'    color: {color}\n'
        f'{children}'
        '}\n'
    )
def renderElement(eid: str, elem: dict) -> str:
    etype = str(elem.get("type", ""))
    props = dict(elem.get("props", {}))
    if etype == "image":
        src = qmlString(props.get("src", ""))
        lines = [
            '    Image {',
            f'        id: {eid}',
            '        anchors.fill: parent',
            f'        source: {src}',
            '        fillMode: Image.PreserveAspectCrop',
            '    }',
        ]
        return "\n".join(lines) + "\n"
    if etype == "rectangle" or etype == "button":
        color = qmlString(props.get("color", "#FFFFFF"))
        opacity = str(props.get("opacity", "1"))
        radius = qmlNumber(props.get("cornerradius", 0), 0)
        w = qmlNumber(props.get("width", 100), 100)
        h = qmlNumber(props.get("height", 40), 40)
        x = qmlNumber(props.get("x", 0), 0)
        y = qmlNumber(props.get("y", 0), 0)
        lines = [
            '    Rectangle {',
            f'        id: {eid}',
            f'        x: {x}',
            f'        y: {y}',
            f'        width: {w}',
            f'        height: {h}',
            f'        radius: {radius}',
            f'        color: {color}',
            f'        opacity: {opacity}',
        ]
        if str(props.get("animate", "")) == "fade":
            dur = qmlNumber(props.get("duration", 600), 600)
            lines.append(f'        NumberAnimation on opacity {{ from: 0; to: {opacity}; duration: {dur} }}')
        if etype == "button" and props.get("text"):
            lines.append(f'        Text {{ anchors.centerIn: parent; text: {qmlString(props.get("text"))} }}')
        lines.append('    }')
        return "\n".join(lines) + "\n"
    if etype == "text":
        text = qmlString(props.get("text", ""))
        color = qmlString(props.get("color", "#5A5A6E"))
        x = qmlNumber(props.get("x", 0), 0)
        y = qmlNumber(props.get("y", 0), 0)
        lines = [
            '    Text {',
            f'        id: {eid}',
            f'        x: {x}',
            f'        y: {y}',
            f'        text: {text}',
            f'        color: {color}',
            '        font.pixelSize: 14',
            '    }',
        ]
        return "\n".join(lines) + "\n"
    if etype == "blur":
        target = str(elem.get("parent", ""))
        radius = qmlNumber(props.get("radius", 40), 40)
        if "width" in props and "height" in props:
            x = qmlNumber(props.get("x", 0), 0)
            y = qmlNumber(props.get("y", 0), 0)
            w = qmlNumber(props.get("width", 100), 100)
            h = qmlNumber(props.get("height", 100), 100)
            corner = qmlNumber(props.get("cornerradius", 0), 0)
            lines = [
                '    Item {',
                f'        id: {eid}',
                f'        x: {x}',
                f'        y: {y}',
                f'        width: {w}',
                f'        height: {h}',
                '        clip: true',
            ]
            if int(corner) > 0:
                lines.append('        layer.enabled: true')
                lines.append('        layer.effect: OpacityMask {')
                lines.append(f'            maskSource: Rectangle {{ width: {w}; height: {h}; radius: {corner} }}')
                lines.append('        }')
            lines.extend([
                f'        ShaderEffectSource {{ id: {eid}Src; sourceItem: {target}; sourceRect: Qt.rect({x}, {y}, {w}, {h}); live: true }}',
                f'        FastBlur {{ anchors.fill: parent; source: {eid}Src; radius: {radius} }}',
                '    }',
            ])
            return "\n".join(lines) + "\n"
        lines = [
            '    FastBlur {',
            f'        anchors.fill: {target}',
            f'        source: {target}',
            f'        radius: {radius}',
            '    }',
        ]
        return "\n".join(lines) + "\n"
    if etype == "webview":
        url = qmlString(props.get("url", ""))
        w = qmlNumber(props.get("width", 800), 800)
        h = qmlNumber(props.get("height", 600), 600)
        lines = [
            '    Rectangle {',
            f'        id: {eid}',
            f'        width: {w}',
            f'        height: {h}',
            '        color: "#111111"',
            f'        Text {{ anchors.centerIn: parent; color: "#FFFFFF"; text: {url} }}',
            '    }',
        ]
        return "\n".join(lines) + "\n"
    return (
        '    Item {\n'
        f'        id: {eid}\n'
        '    }\n'
    )
def buildQml(shellName: str, windows: dict, elements: dict) -> str:
    header = (
        'import QtQuick\n'
        'import QtQuick.Window\n'
        'import Qt5Compat.GraphicalEffects\n'
    )
    if not windows:
        return header + renderWindow("win1", {"title": shellName}, '')
    bodies = []
    for wid, win in windows.items():
        topLevel = []
        emitted = set()
        for eid, elem in elements.items():
            if str(elem.get("parent", "")) == wid and eid not in emitted:
                topLevel.append(renderElement(eid, elem))
                emitted.add(eid)
                for subId, sub in elements.items():
                    if str(sub.get("parent", "")) == eid and subId not in emitted:
                        topLevel.append(renderElement(subId, sub))
                        emitted.add(subId)
        bodies.append(renderWindow(wid, win, "".join(topLevel)))
    return header + "\n".join(bodies)
