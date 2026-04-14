import os
import sys
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'app_config.json')

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


FUSION_STYLE = '''
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: Segoe UI, Arial;
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
QScrollArea {
    background-color: #1e1e1e;
    border: none;
}
QDialog {
    background-color: #1e1e1e;
    border: 1px solid #444;
}
QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 3px;
    padding: 4px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #888;
    margin-right: 5px;
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
'''


apps_dict = {
    'Blender Foundation': 'Blender',
    'Autodesk': 'Maya',
    'Side Effects Software': 'Houdini',
    'INRIA': 'Natron',
    'SilhouetteFX': 'Silhouette',
    'Imagineer Systems Ltd': 'Mocha',
    'Adobe': ['Adobe Photoshop', 'Adobe Premiere', 'Adobe After Effects']
}


class VersionDialog(QDialog):
    def __init__(self, app_name, versions, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.versions = versions
        self.selected_version = versions[0] if versions else None
        self.setWindowTitle(f'选择版本 - {app_name}')
        self.setMinimumSize(300, 200)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f'{app_name} 已安装版本:'))
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(versions)
        layout.addWidget(self.version_combo)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.launch_btn = QPushButton('启动')
        self.cancel_btn = QPushButton('取消')
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.launch_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def get_version(self):
        return self.version_combo.currentText()


class ConfigDialog(QDialog):
    def __init__(self, app_name, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.setWindowTitle(f'启动配置 - {app_name}')
        self.setMinimumSize(450, 400)
        
        icon_config = load_icon_config()
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel('自定义图标:'))
        self.icon_path = QLineEdit()
        self.icon_path.setText(icon_config.get(app_name, ''))
        self.icon_btn = QPushButton('浏览...')
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_path)
        icon_layout.addWidget(self.icon_btn)
        layout.addLayout(icon_layout)
        
        layout.addWidget(QLabel('项目路径:'))
        self.project_path = QLineEdit()
        self.project_btn = QPushButton('浏览...')
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.project_path)
        path_layout.addWidget(self.project_btn)
        layout.addLayout(path_layout)
        
        layout.addWidget(QLabel('自定义环境变量 (KEY=VALUE, 每行一个):'))
        self.env_text = QTextEdit()
        self.env_text.setPlaceholderText('PYTHONPATH=D:/pipeline/scripts\nPROJECT_DIR=D:/project1')
        self.env_text.setMaximumHeight(100)
        layout.addWidget(self.env_text)
        
        btn_layout = QHBoxLayout()
        self.launch_btn = QPushButton('启动')
        self.cancel_btn = QPushButton('取消')
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.icon_btn.clicked.connect(self.browse_icon)
        self.project_btn.clicked.connect(self.browse_project)
        self.launch_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def browse_icon(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择图标', '', 'Images (*.png *.ico *.jpg)')
        if file:
            self.icon_path.setText(file)

    def browse_project(self):
        folder = QFileDialog.getExistingDirectory(self, '选择项目目录')
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
            if self.app_name == 'Maya':
                args = ['-proj', project]
            elif self.app_name == 'Houdini':
                args = ['-', project]
        return args

    def get_icon_path(self):
        return self.icon_path.text().strip()

    def save_icon_config(self):
        config = load_icon_config()
        icon_path = self.get_icon_path()
        if icon_path:
            config[self.app_name] = icon_path
            save_icon_config(config)


class ApplauncherUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cgorun_Launcher')
        self.setMinimumSize(400, 500)
        
        icon_config = load_icon_config()
        self.app_source_path = r'C:\\Program Files'
        
        self.dcc_apps_list = ('Nuke', 'Natron', 'Fusion')
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; }')
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_widget.setLayout(self.grid_layout)
        
        scroll.setWidget(self.grid_widget)
        main_layout.addWidget(scroll)
        
        self.setStyleSheet('background-color: #1e1e1e;')
        self.setWindowIcon(QIcon('./icons/Launcher.ico'))
        
        self.app_data = self.collect_apps()
        self.create_app_icons()
        
    def collect_apps(self):
        app_data = {}
        
        if not os.path.exists(self.app_source_path):
            return app_data
            
        all_apps_list = os.listdir(self.app_source_path)
        
        for inst_app_name in all_apps_list:
            for dcc_app in self.dcc_apps_list:
                if inst_app_name.startswith(dcc_app):
                    if dcc_app not in app_data:
                        app_data[dcc_app] = []
                    app_data[dcc_app].append(inst_app_name)
        
        for company_name, software_name in apps_dict.items():
            if company_name not in all_apps_list:
                continue
                
            if company_name == 'Adobe':
                for adobe_app in software_name:
                    versions = self.get_software_versions(company_name, adobe_app)
                    if versions:
                        key = adobe_app.split()[1] if ' ' in adobe_app else adobe_app
                        if key not in app_data:
                            app_data[key] = []
                        app_data[key].extend(versions)
            else:
                versions = self.get_software_versions(company_name, software_name)
                if versions:
                    if software_name not in app_data:
                        app_data[software_name] = []
                    app_data[software_name].extend(versions)
        
        return app_data
    
    def get_software_versions(self, company_name, software_name):
        versions = []
        try:
            software_path = os.path.join(self.app_source_path, company_name)
            if os.path.exists(software_path):
                for item in os.listdir(software_path):
                    if item.startswith(software_name):
                        versions.append(item)
        except:
            pass
        return versions
    
    def create_app_icons(self):
        icon_config = load_icon_config()
        row, col = 0, 0
        max_cols = 5
        
        for app_name, versions in self.app_data.items():
            if not versions:
                continue
                
            default_version = versions[-1]
            custom_icon = icon_config.get(app_name, '')
            
            if custom_icon and os.path.exists(custom_icon):
                icon_path = custom_icon
            else:
                icon_path = os.path.join('./icons', f'{app_name}.png')
                if not os.path.exists(icon_path):
                    icon_path = os.path.join('./icons', f'{app_name.split()[0]}.png')
            
            widget = QWidget()
            widget.setFixedSize(90, 105)
            layout = QVBoxLayout()
            layout.setContentsMargins(5, 3, 5, 3)
            layout.setSpacing(2)
            widget.setLayout(layout)
            
            icon_btn = QPushButton()
            icon_btn.setFixedSize(64, 64)
            icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if os.path.exists(icon_path):
                icon_btn.setIcon(QIcon(icon_path))
                icon_btn.setIconSize(QSize(60, 60))
            icon_btn.setStyleSheet('''
                QPushButton {
                    background-color: #2d2d2d;
                    border: 2px solid #444;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border: 2px solid #0078d4;
                }
            ''')
            
            name_label = QLabel(app_name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet('color: #e0e0e0; font-weight: bold; font-size: 11px; background: transparent;')
            name_label.setWordWrap(True)
            
            version_label = QLabel(default_version)
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            version_label.setStyleSheet('color: #888; font-size: 9px;')
            
            layout.addWidget(icon_btn, 0, Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(name_label, 0, Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(version_label, 0, Qt.AlignmentFlag.AlignHCenter)
            
            icon_btn.clicked.connect(lambda checked, n=app_name, v=versions: self.on_app_click(n, v))
            
            self.grid_layout.addWidget(widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def on_app_click(self, app_name, versions):
        if len(versions) == 1:
            self.launch_with_config(versions[0])
        else:
            dialog = VersionDialog(app_name, versions, self)
            if dialog.exec():
                selected = dialog.get_version()
                self.launch_with_config(selected)
    
    def launch_with_config(self, app_version):
        config_dialog = ConfigDialog(app_version, self)
        if config_dialog.exec():
            config_dialog.save_icon_config()
            env = config_dialog.get_env()
            args = config_dialog.get_args()
            self.launch_application(app_version, env, args)
    
    def launch_application(self, app_launch_name, env=None, args=None):
        cmd = None
        if env is None:
            env = os.environ.copy()
        if args is None:
            args = []
            
        if app_launch_name.startswith('Nuke'):
            nuke_exe = app_launch_name.split('v')[0]
            cmd = [fr'C:\\Program Files\\{app_launch_name}\\{nuke_exe}.exe'] + args
        elif app_launch_name.startswith('Natron'):
            cmd = [fr'C:\\Program Files\\INRIA\\{app_launch_name}\\bin\\Natron.exe'] + args
        elif app_launch_name.startswith('Maya'):
            cmd = [fr'C:\\Program Files\\Autodesk\\{app_launch_name}\\bin\\maya.exe'] + args
        elif app_launch_name.startswith('Houdini'):
            cmd = [fr'C:\\Program Files\\Side Effects Software\\{app_launch_name}\\bin\\houdinifx.exe'] + args
        elif app_launch_name.startswith('Blender'):
            cmd = [fr'C:\\Program Files\\Blender Foundation\\{app_launch_name}\\blender.exe'] + args
        elif app_launch_name.startswith('Mocha'):
            cmd = [fr'C:\\Program Files\\Imagineer Systems Ltd\\{app_launch_name}\\bin\\mochapro.exe'] + args
        elif app_launch_name.startswith('Silhouette'):
            cmd = [fr'C:\\Program Files\\SilhouetteFX\\{app_launch_name}\\Silhouette.exe'] + args
        elif app_launch_name.startswith('Adobe Premiere'):
            cmd = [fr'C:\\Program Files\\Adobe\\{app_launch_name}\\Adobe Premiere Pro.exe'] + args
        elif app_launch_name.startswith('Adobe Photoshop'):
            cmd = [fr'C:\\Program Files\\Adobe\\{app_launch_name}\\Photoshop.exe'] + args
        elif app_launch_name.startswith('Adobe After Effects'):
            cmd = [fr'C:\\Program Files\\Adobe\\{app_launch_name}\\Support Files\\AfterFX.exe'] + args
        
        if cmd:
            subprocess.Popen(cmd, env=env)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(FUSION_STYLE)
    launcher = ApplauncherUI()
    launcher.show()
    sys.exit(app.exec())