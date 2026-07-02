# UPDATE: 260702

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import Qt, QUrl, QPoint, QTimer
from PyQt5.QtGui import QIcon
import os


# ======================
# TAB
# ======================
class BrowserTab(QWidget):
    def __init__(self, url="https://duckduckgo.com/"):
        super().__init__()

        if not isinstance(url, str) or not url:
            url = "https://duckduckgo.com/"

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

        self.setStyleSheet("""
            QWidget {
                background: #2b2b2b;
            }
        """)


# ======================
# MAIN BROWSER
# ======================
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        QWebEngineProfile.defaultProfile().downloadRequested.connect(
            self.download_requested
        )

        self.setWindowTitle("Orangewolf Browser")
        self.setWindowIcon(QIcon("orangewolf_icon.png"))
        self.resize(1200, 800)
        self.showMaximized()

        # ❗ Frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.old_pos = None

        # ======================
        # TITLE BAR
        # ======================
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 0, 5, 0)

        self.title_label = QLabel("Orangewolf Browser")

        btn_min = QPushButton("↧")
        btn_max = QPushButton("↹")
        btn_close = QPushButton("✕")

        btn_min.setFixedSize(35, 35)
        btn_max.setFixedSize(35, 35)
        btn_close.setFixedSize(35, 35)

        btn_min.clicked.connect(self.showMinimized)
        btn_max.clicked.connect(self.toggle_maximize)
        btn_close.clicked.connect(self.close)

        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(btn_min)
        title_layout.addWidget(btn_max)
        title_layout.addWidget(btn_close)

        self.title_bar.setLayout(title_layout)

        # ======================
        # NAV BAR
        # ======================
        nav_bar = QHBoxLayout()

        back_btn = QPushButton("←")
        forward_btn = QPushButton("→")
        reload_btn = QPushButton("⟳")

        back_btn.setFixedSize(40, 40)
        forward_btn.setFixedSize(40, 40)
        reload_btn.setFixedSize(40, 40)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)

        back_btn.clicked.connect(lambda: self.safe_action("back"))
        forward_btn.clicked.connect(lambda: self.safe_action("forward"))
        reload_btn.clicked.connect(lambda: self.safe_action("reload"))

        nav_bar.addWidget(back_btn)
        nav_bar.addWidget(forward_btn)
        nav_bar.addWidget(reload_btn)
        nav_bar.addWidget(self.url_bar)

        # ======================
        # TABS
        # ======================
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(35, 35)
        self.new_tab_btn.clicked.connect(self.add_tab)

        tab_container = QWidget()
        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)

        tab_layout.addWidget(self.tabs)
        tab_layout.addWidget(self.new_tab_btn)

        tab_container.setLayout(tab_layout)

        # ======================
        # MAIN LAYOUT
        # ======================
        layout = QVBoxLayout()
        layout.addWidget(self.title_bar)
        layout.addLayout(nav_bar)
        layout.addWidget(tab_container)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 🔥 első tab
        self.add_tab()

        # ======================
        # DESIGN
        # ======================
        self.setStyleSheet("""
            QWidget {
                background: #353535;
                color: white;
            }

            QLineEdit {
                background: #1e1e1e;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }

            QPushButton {
                background: #505050;
                border-radius: 6px;
                font-size: 16px;
            }

            QPushButton:hover {
                background: #656565;
            }

            QTabWidget::pane {
                border: none;
            }

            QTabBar::tab {
                background: #2a2a2a;
                padding: 6px;
                margin: 2px;
                border-radius: 6px;
            }

            QTabBar::tab:selected {
                background: #444;
            }
        """)

    def download_requested(self, download):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select download folder"
        )

        if not folder:
            download.cancel()
            return

        path = os.path.join(folder, download.downloadFileName())

        download.setPath(path)
        download.accept()

        download.finished.connect(
            lambda: QMessageBox.information(
                self,
                "Download",
                f"Download completed:\n{path}"
            )
        )

    # ======================
    # TAB LOGIKA
    # ======================
    def add_tab(self, url="https://duckduckgo.com/"):
        if not isinstance(url, str) or not url:
            url = "https://duckduckgo.com/"

        tab = BrowserTab(url)

        i = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(i)

        tab.browser.urlChanged.connect(
            lambda q, t=tab: self.update_tab_title(t, q)
        )

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_browser(self):
        tab = self.tabs.currentWidget()
        if tab and hasattr(tab, "browser"):
            return tab.browser
        return None

    # ======================
    # SAFE ACTIONS
    # ======================
    def safe_action(self, action):
        browser = self.current_browser()
        if not browser:
            return

        if action == "back":
            browser.back()
        elif action == "forward":
            browser.forward()
        elif action == "reload":
            browser.reload()

    # ======================
    # URL
    # ======================
    def load_url(self):
        browser = self.current_browser()
        if not browser:
            return

        url = self.url_bar.text().strip()

        if not url:
            return

        if not url.startswith("http"):
            url = "https://" + url

        browser.setUrl(QUrl(url))

    # ======================
    # TAB CHANGE
    # ======================
    def on_tab_changed(self):
        QTimer.singleShot(0, self.sync_url_bar)

    def sync_url_bar(self):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())

    def update_tab_title(self, tab, url):
        i = self.tabs.indexOf(tab)
        if i != -1:
            self.tabs.setTabText(i, url.host() if url.host() else "Tab")

    # ======================
    # WINDOW MOVE
    # ======================
    def mousePressEvent(self, event):
        if not self.isMaximized():
            if event.button() == Qt.LeftButton:
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    # ======================
    # MAXIMIZE
    # ======================
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


def restart_program():
    """Restart the current program."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

# ======================
# RUN
# ======================
app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())
