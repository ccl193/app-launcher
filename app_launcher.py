import os
import sys
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "icon_config.json")

def load_icon_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_icon_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


FUSION_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial;
    font-size: 11px;
}
QMainWindow {
    background-color: #1e1e1e;
}
QPushButton {
    background-color: #3a3a3a;
    color: #e0e0e0;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #4a4a4a;
    border: 1px solid #666;
}
QPushButton:pressed {
    background-color: #2a2a2a;
}
QPushButton:selected {
    background-color: #0078d4;
}
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 3px;
    padding: 4px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #0078d4;
}
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}
QListWidget {
    background-color: #252525;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
}
QListWidget::item {
    background-color: transparent;
    padding: 4px;
}
QListWidget::item:selected {
    background-color: #0078d4;
    color: #fff;
}
QListWidget::item:hover {
    background-color: #3a3a3a;
}
QScrollBar:vertical {
    background: #2a2a2a;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #666;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QDialog {
    background-color: #1e1e1e;
    border: 1px solid #444;
}
QScrollBar {
    background: #2a2a2a;
}
"""


apps_dict = {
    "Blender Foundation": "Blender",
    "Autodesk": "Maya",
    "Side Effects Software": "Houdini",
    "INRIA": "Natron",
    "SilhouetteFX": "Silhouette",
    "Imagineer Systems Ltd": "Mocha",
    "Adobe": ["Adobe Photoshop", "Adobe Premiere", "Adobe After Effects"]
}


class ConfigDialog(QDialog):
    def __init__(self, app_name, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.setWindowTitle(f"启动配置 - {app_name}")
        self.setMinimumSize(450, 400)
        
        icon_config = load_icon_config()
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("自定义图标:"))
        self.icon_path = QLineEdit()
        self.icon_path.setText(icon_config.get(app_name, ""))
        self.icon_btn = QPushButton("浏览...")
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_path)
        icon_layout.addWidget(self.icon_btn)
        layout.addLayout(icon_layout)
        
        layout.addWidget(QLabel("项目路径:"))
        self.project_path = QLineEdit()
        self.project_btn = QPushButton("浏览...")
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.project_path)
        path_layout.addWidget(self.project_btn)
        layout.addLayout(path_layout)
        
        layout.addWidget(QLabel("自定义环境变量 (KEY=VALUE, 每行一个):"))
        self.env_text = QTextEdit()
        self.env_text.setPlaceholderText("PYTHONPATH=D:/pipeline/scripts\nPROJECT_DIR=D:/project1")
        self.env_text.setMaximumHeight(100)
        layout.addWidget(self.env_text)
        
        btn_layout = QHBoxLayout()
        self.launch_btn = QPushButton("启动")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.icon_btn.clicked.connect(self.browse_icon)
        self.project_btn.clicked.connect(self.browse_project)
        self.launch_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def browse_icon(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择图标", "", "Images (*.png *.ico *.jpg)")
        if file:
            self.icon_path.setText(file)

    def browse_project(self):
        folder = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if folder:
            self.project_path.setText(folder)

    def get_env(self):
        env = os.environ.copy()
        custom_env = self.env_text.toPlainText().strip()
        if custom_env:
            for line in custom_env.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
        return env

    def get_args(self):
        args = []
        project = self.project_path.text().strip()
        if project:
            if self.app_name == "Maya":
                args = ["-proj", project]
            elif self.app_name == "Houdini":
                args = ["-", project]
        return args

    def get_icon_path(self):
        return self.icon_path.text().strip()

    def save_icon_config(self):
        config = load_icon_config()
        icon_path = self.get_icon_path()
        if icon_path:
            config[self.app_name] = icon_path
            save_icon_config(config)


class ApplauncherUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Launch")
        self.setMinimumSize(400, 600)
        self.vlayout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.setStyleSheet("background-color: #1e1e1e;")
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "icons", "Launcher.ico")))
        self.app_source_path = r"C:\Program Files"
        self.all_apps_list = os.listdir(self.app_source_path)
        self.dcc_installed_apps = dict()
        self.dcc_apps_list = (
            "Nuke", "Natron", "Fusion",
        )
        self.get_dcc_apps_list()
        self.vlayout.addWidget(self.list_widget)
        self.setLayout(self.vlayout)

    def get_dcc_apps_list(self):
        for inst_app_name in self.all_apps_list:
            for dcc_app in self.dcc_apps_list:
                if inst_app_name.startswith(dcc_app):
                    self.create_app_buttons(app_name=inst_app_name, icon_name=dcc_app)

        for company_name in apps_dict.keys():
            if company_name == "Adobe":
                for adobe_app in apps_dict["Adobe"]:
                    self.get_software_versions(company_name, adobe_app)
            else:
                self.get_software_versions(company_name, apps_dict[company_name])

    def get_software_versions(self, company_name, software_name):
        for inst_app_name in self.all_apps_list:
            if inst_app_name == company_name:
                softwares_version_list = os.listdir(os.path.join(self.app_source_path, company_name))
                for software_version in softwares_version_list:
                    if software_version.startswith(software_name):
                        self.create_app_buttons(app_name=software_version, icon_name=software_name)

    def create_app_buttons(self, app_name, icon_name):
        icon_config = load_icon_config()
        custom_icon = icon_config.get(app_name, "")
        
        if custom_icon and os.path.exists(custom_icon):
            icon_path = custom_icon
        else:
            icon_path = os.path.join(BASE_DIR, "icons", "{}.png".format(icon_name))
            if not os.path.exists(icon_path):
                icon_path = os.path.join(BASE_DIR, "icons", "{}.png".format(icon_name.split()[0]))
        
        self.app_button = QPushButton("   " + app_name)
        self.app_button.setFont(QFont("consolas", 10))
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(QSize(30, 70))
        if os.path.exists(icon_path):
            self.app_button.setIcon(QIcon(icon_path))
        self.app_button.setIconSize(QSize(48, 48))
        self.list_widget.setItemWidget(item, self.app_button)
        self.list_widget.setSpacing(3)
        self.app_button.clicked.connect(lambda: self.show_config_dialog(app_name, icon_name))

    def show_config_dialog(self, app_name, icon_name):
        dialog = ConfigDialog(app_name, self)
        if dialog.exec():
            dialog.save_icon_config()
            env = dialog.get_env()
            args = dialog.get_args()
            self.launch_application(app_name, env, args)

    def launch_application(self, app_launch_name, env=None, args=None):
        cmd = None
        if env is None:
            env = os.environ.copy()
        if args is None:
            args = []
            
        if app_launch_name.startswith("Nuke"):
            nuke_exe = app_launch_name.split("v")[0]
            cmd = [fr"C:\Program Files\{app_launch_name}\{nuke_exe}.exe"] + args
        elif app_launch_name.startswith("Natron"):
            cmd = [fr"C:\Program Files\INRIA\{app_launch_name}\bin\Natron.exe"] + args
        elif app_launch_name.startswith("Maya"):
            cmd = [fr"C:\Program Files\Autodesk\{app_launch_name}\bin\maya.exe"] + args
        elif app_launch_name.startswith("Houdini"):
            cmd = [fr"C:\Program Files\Side Effects Software\{app_launch_name}\bin\houdinifx.exe"] + args
        elif app_launch_name.startswith("Blender"):
            cmd = [fr"C:\Program Files\Blender Foundation\{app_launch_name}\blender.exe"] + args
        elif app_launch_name.startswith("Mocha"):
            cmd = [fr"C:\Program Files\Imagineer Systems Ltd\{app_launch_name}\bin\mochapro.exe"] + args
        elif app_launch_name.startswith("Silhouette"):
            cmd = [fr"C:\Program Files\SilhouetteFX\{app_launch_name}\Silhouette.exe"] + args
        elif app_launch_name.startswith("Adobe Premiere"):
            cmd = [fr"C:\Program Files\Adobe\{app_launch_name}\Adobe Premiere Pro.exe"] + args
        elif app_launch_name.startswith("Adobe Photoshop"):
            cmd = [fr"C:\Program Files\Adobe\{app_launch_name}\Photoshop.exe"] + args
        elif app_launch_name.startswith("Adobe After Effects"):
            cmd = [fr"C:\Program Files\Adobe\{app_launch_name}\Support Files\AfterFX.exe"] + args
        
        if cmd:
            subprocess.Popen(cmd, env=env)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(FUSION_STYLE)
    launcher = ApplauncherUI()
    launcher.show()
    sys.exit(app.exec())