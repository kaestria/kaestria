import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.boot.Boot import run as bootRun
from kernel.user.Session import Session
from kernel.command.Dispatcher import dispatch
from ipc.Server import run as apiRun
from PySide6.QtGui import QGuiApplication, QFontDatabase, QCursor
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtWebEngineCore import QWebEngineProfile
CLEAR_SEQUENCE = "\033[2J\033[H"
class VistroBridge(QObject):
    sendOutput = Signal(str)
    sendPrompt = Signal(str)
    sendClear = Signal()
    def __init__(self, session):
        super().__init__()
        self._session = session
    @Slot(str)
    def runCommand(self, line):
        line = line.strip()
        if line.lower() in ("exit", "quit"):
            QGuiApplication.quit()
            return
        result = dispatch(line, self._session)
        if result == CLEAR_SEQUENCE:
            self.sendClear.emit()
        elif result:
            self.sendOutput.emit(result)
        self.sendPrompt.emit(self._session.getPrompt())
    @Slot(result=str)
    def getPrompt(self):
        return self._session.getPrompt()
class VistroApp:
    BASE_DIR = Path(__file__).parent
    ROOT_DIR = BASE_DIR.parent.parent
    QML_FILE = ROOT_DIR / "cli" / "Main.qml"
    FONT_FILE = ROOT_DIR / "assets" / "perfectdosvga.ttf"
    APP_NAME = "Vistro Virtual Machine"
    def __init__(self):
        self._app = QGuiApplication(sys.argv)
        self._engine = QQmlApplicationEngine()
        self._session = Session()
        self._bridge = VistroBridge(self._session)
    def loadFont(self):
        QFontDatabase.addApplicationFont(str(self.FONT_FILE))
    def hideCursor(self):
        self._app.setOverrideCursor(QCursor(Qt.BlankCursor))
    def run(self):
        self._app.setApplicationName(self.APP_NAME)
        bootRun()
        import threading
        t = threading.Thread(target=apiRun, daemon=True)
        t.start()
        self.loadFont()
        self.hideCursor()
        self._engine.rootContext().setContextProperty("vistroBridge", self._bridge)
        self._engine.load(str(self.QML_FILE))
        download_dir = str(Path.home() / "vistro" / "root" / "data" / "browser")
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile.defaultProfile()
        profile.setDownloadPath(download_dir)
        profile.downloadRequested.connect(lambda item: item.accept())
        if not self._engine.rootObjects():
            return 1
        return self._app.exec()
def run():
    dos = VistroApp()
    sys.exit(dos.run())
