import os
import sys
import subprocess
import json
import datetime

# Qt平台插件修复
import glob

def find_qt_plugin():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        pattern = os.path.join(exe_dir, '**', 'platforms')
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if os.path.isdir(match):
                return match
    else:
        return os.path.join(os.path.dirname(sys.executable), 'lib', 'site-packages', 'PyQt6', 'Qt6', 'plugins', 'platforms')
    return ''

qt_plugin_path = find_qt_plugin()
if qt_plugin_path and os.path.exists(qt_plugin_path):
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'app_config.json')
ICON_CONFIG_FILE = os.path.join(CONFIG_DIR, 'icon_names.json')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
ICONS_DIR = os.path.join(BASE_DIR, 'icons')
LOG_FILE = os.path.join(LOG_DIR, datetime.datetime.now().strftime('%Y%m%d') + '.log')
ORDER_FILE = os.path.join(CONFIG_DIR, 'icon_order.json')

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

def write_log(message):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    log_line = f'[{timestamp}] {message}\n'
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)

def load_icon_config():
    if os.path.exists(ICON_CONFIG_FILE):
        with open(ICON_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_icon_config(config):
    with open(ICON_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_last_version():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_last_versions(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_icon_order():
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_icon_order(order):
    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        json.dump(order, f, ensure_ascii=False, indent=2)

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
QComboBox::down-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #888;
}
QScrollBar:vertical {
    background: #2a2a2a;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 5px;
}
'''

class ApplauncherUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cgorun_Launcher')
        self.setMinimumSize(400, 500)
        self.icon_items = []
        self.last_versions = load_last_version()
        self.custom_app_paths = {}
        self.app_data = self.collect_apps()
        self.icon_order = load_icon_order()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15,15,15,15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_widget)
        main_layout.addWidget(scroll, 1)

        self.setAcceptDrops(True)
        self.grid_widget.setAcceptDrops(True)

        toolbar = QHBoxLayout()
        self.log_btn = QPushButton('ℹ️')
        self.log_btn.setFixedHeight(25)
        self.log_btn.clicked.connect(self.toggle_log)
        self.add_btn = QPushButton('+')
        self.add_btn.setFixedSize(35,25)
        self.add_btn.clicked.connect(self.on_add_app)
        self.top_btn = QPushButton('📌')
        self.top_btn.setCheckable(True)
        self.top_btn.setChecked(True)
        self.top_btn.setFixedSize(35,25)
        self.top_btn.setStyleSheet('''
            QPushButton { background-color: #3a3a3a; border: 1px solid #555; border-radius: 4px; }
            QPushButton:checked { background-color: #4a5a6a; border: 1px solid #5a6a7a; }
        ''')
        self.top_btn.clicked.connect(self.toggle_top)
        toolbar.addWidget(self.log_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.top_btn)
        main_layout.addLayout(toolbar)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setVisible(False)
        main_layout.addWidget(self.log_widget)

        self.create_app_icons()
        self.setStyleSheet(FUSION_STYLE)
        
        icon_path = os.path.join(ICONS_DIR, 'Launcher.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def collect_apps(self):
        import uuid
        data = {}
        for app_id, exe_path in self.last_versions.items():
            if os.path.isabs(exe_path) and os.path.exists(exe_path):
                if not app_id.startswith('app_'):
                    new_id = f"app_{uuid.uuid4().hex[:8]}"
                    
                    old_cfg = load_icon_config()
                    old_name = old_cfg.get(app_id, None)
                    if old_name:
                        old_cfg.pop(app_id, None)
                        old_cfg[f"{new_id}_name"] = old_name
                        save_icon_config(old_cfg)
                    
                    del self.last_versions[app_id]
                    self.last_versions[new_id] = exe_path
                    app_id = new_id
                    
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(self.last_versions, f, ensure_ascii=False, indent=2)
                
                self.custom_app_paths[app_id] = exe_path
                ext = os.path.splitext(exe_path)[1].lower()
                data[app_id] = ['.cmd'] if ext == '.cmd' else ['']
        return data

    def create_app_icons(self):
        while self.grid_layout.count():
            self.grid_layout.takeAt(0).widget().deleteLater()
        self.icon_items = []

        all_apps = list(self.app_data.keys())
        ordered = [a for a in self.icon_order if a in all_apps]
        unordered = [a for a in all_apps if a not in ordered]
        final_list = ordered + unordered

        max_col = 4
        row = 0
        col = 0

        for app in final_list:
            vers = self.app_data.get(app, [])
            w = QWidget()
            w.setFixedSize(90, 105)
            w.app_name = app
            lay = QVBoxLayout(w)
            lay.setContentsMargins(5,3,5,3)

            btn = QPushButton()
            btn.setFixedSize(64,64)
            ico = ''
            if app in self.custom_app_paths:
                exe_name = os.path.splitext(os.path.basename(self.custom_app_paths[app]))[0]
                exe_name_lower = exe_name.lower()
            else:
                exe_name = app
                exe_name_lower = app.split('.')[0].lower()
            
            if os.path.exists(ICONS_DIR):
                for icon_file in os.listdir(ICONS_DIR):
                    if icon_file.lower().endswith('.png'):
                        icon_base = os.path.splitext(icon_file)[0].lower()
                        if exe_name_lower in icon_base or icon_base in exe_name_lower:
                            ico = os.path.join(ICONS_DIR, icon_file)
                            break
            
            icon_cfg = load_icon_config()
            display_name = icon_cfg.get(f"{app}_name", exe_name)
            
            if os.path.exists(ico):
                btn.setIcon(QIcon(ico))
                btn.setIconSize(QSize(60,60))
            else:
                btn.setText(display_name[:6])

            btn.setStyleSheet('''
                QPushButton {background:#2d2d2d; border:2px solid #444; border-radius:12px; color:#eee;}
                QPushButton:hover {background:#3a4a5a; border-color:#5a6a7a;}
                QPushButton:pressed {background:#4a5a6a; border-color:#0078d4;}
            ''')

            btn.mousePressEvent = lambda e, a=app, b=btn: self.on_btn_press(e, a, b)
            btn.mouseMoveEvent = lambda e, a=app, b=btn: self.on_btn_move(e, a, b)
            btn.mouseReleaseEvent = lambda e, a=app, b=btn: self.on_btn_release(e, a)
            btn.enterEvent = lambda e, b=btn: self.on_btn_enter(b)
            btn.leaveEvent = lambda e, b=btn: self.on_btn_leave(b)
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, a=app, b=btn: self.show_version_menu(pos, a, b))

            name_lbl = QLabel(display_name)
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet('color:#eee; font-weight:bold;')

            lay.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
            lay.addWidget(name_lbl, 0, Qt.AlignmentFlag.AlignCenter)

            self.icon_items.append(w)
            self.grid_layout.addWidget(w, row, col)

            col += 1
            if col >= max_col:
                col = 0
                row += 1

    # ========== 右键菜单 ==========
    def show_version_menu(self, pos, app_name, btn):
        menu = QMenu()
        
        if app_name in self.custom_app_paths:
            config_act = menu.addAction('配置')
            config_act.triggered.connect(lambda checked, a=app_name: self.config_custom_app(a))
            menu.addSeparator()
            del_act = menu.addAction('删除')
            del_act.triggered.connect(lambda checked, a=app_name: self.delete_custom_app(a))
        else:
            add_act = menu.addAction('添加应用')
            add_act.triggered.connect(lambda checked, a=app_name: self.on_add_app())
        
        menu.exec(btn.mapToGlobal(pos))
    
    def config_custom_app(self, app_id):
        if app_id not in self.custom_app_paths:
            return
        current_path = self.custom_app_paths[app_id]
        exe_name = os.path.splitext(os.path.basename(current_path))[0]
        current_name = load_icon_config().get(f"{app_id}_name", exe_name)
        
        dlg = QDialog(self)
        dlg.setWindowTitle('配置')
        dlg.setMinimumSize(400, 180)
        lay = QVBoxLayout(dlg)
        
        lay.addWidget(QLabel('显示名称:'))
        name_edit = QLineEdit(current_name)
        lay.addWidget(name_edit)
        
        lay.addWidget(QLabel('程序路径:'))
        path_layout = QHBoxLayout()
        path_edit = QLineEdit(current_path)
        path_layout.addWidget(path_edit)
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(lambda: self.browse_exe(path_edit))
        path_layout.addWidget(browse_btn)
        lay.addLayout(path_layout)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton('保存')
        ok_btn.clicked.connect(lambda: self.save_config_path(app_id, name_edit.text(), path_edit.text(), dlg))
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        lay.addLayout(btn_layout)
        
        dlg.exec()
    
    def browse_exe(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序", "", "程序文件 (*.exe *.cmd)")
        if path:
            line_edit.setText(path)
    
    def save_config_path(self, app_id, new_name, new_path, dlg):
        if not new_path or not os.path.exists(new_path):
            return
        self.custom_app_paths[app_id] = new_path
        self.last_versions[app_id] = new_path
        save_last_versions(self.last_versions)
        
        icon_cfg = load_icon_config()
        icon_cfg[f"{app_id}_name"] = new_name
        save_icon_config(icon_cfg)
        
        self.create_app_icons()
        self.save_order()
        dlg.accept()
        self.log(f'已更新: {new_path}')

    def delete_custom_app(self, app_id):
        if app_id in self.custom_app_paths:
            del self.custom_app_paths[app_id]
        if app_id in self.last_versions:
            del self.last_versions[app_id]
        save_last_versions(self.last_versions)
        if app_id in self.app_data:
            del self.app_data[app_id]
        
        icon_cfg = load_icon_config()
        icon_cfg.pop(f"{app_id}_name", None)
        save_icon_config(icon_cfg)
        
        if hasattr(self, 'icon_order') and app_id in self.icon_order:
            self.icon_order.remove(app_id)
            self.save_order()
        self.create_app_icons()
        self.log(f"已删除应用")

    def start_drag(self, event, app_name, btn_widget):
        self.drag_start_app = app_name
        pix = btn_widget.grab()
        drag = QDrag(btn_widget)
        mime = QMimeData()
        mime.setText(app_name)
        drag.setMimeData(mime)
        drag.setPixmap(pix.scaled(64,64))
        drag.setHotSpot(QPoint(32,32))
        drag.exec(Qt.DropAction.MoveAction)

    def on_btn_press(self, e, app_name, btn):
        if e.button() == Qt.MouseButton.LeftButton:
            self.btn_press_pos = e.globalPosition().toPoint()
            self.btn_press_app = app_name
            self.btn_press_btn = btn
            if btn:
                btn.setStyleSheet('''
                    QPushButton {background:#3a4a5a; border:2px solid #0078d4; border-radius:12px; color:#eee;}
                ''')
    
    def on_btn_move(self, e, app_name, btn):
        if hasattr(self, 'btn_press_pos') and self.btn_press_pos and e.buttons() == Qt.MouseButton.LeftButton:
            cur_pos = e.globalPosition().toPoint()
            dist = (cur_pos - self.btn_press_pos).manhattanLength()
            if dist > 10:
                self.btn_press_pos = None
                self.start_drag(e, app_name, btn)

    def on_btn_release(self, e, app_name, btn=None):
        if e.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'btn_press_pos') and self.btn_press_pos and hasattr(self, 'btn_press_btn') and self.btn_press_btn:
                cur_pos = e.globalPosition().toPoint()
                dist = (cur_pos - self.btn_press_pos).manhattanLength()
                if dist < 10:
                    pressed_btn = self.btn_press_btn
                    QTimer.singleShot(100, lambda: self.reset_btn_style(pressed_btn))
                    self.quick_launch(app_name)
    
    def on_btn_leave(self, btn):
        if btn:
            btn.setStyleSheet('''
                QPushButton {background:#2d2d2d; border:2px solid #444; border-radius:12px; color:#eee;}
                QPushButton:hover {background:#3a4a5a; border-color:#5a6a7a;}
            ''')

    def on_btn_enter(self, btn):
        if btn:
            btn.setStyleSheet('''
                QPushButton {background:#3a4a5a; border:2px solid #5a6a7a; border-radius:12px; color:#eee;}
            ''')

    def reset_btn_style(self, btn):
        if btn:
            btn.setStyleSheet('''
                QPushButton {background:#2d2d2d; border:2px solid #444; border-radius:12px; color:#eee;}
                QPushButton:hover {border-color:#0078d4;}
            ''')
            self.btn_press_pos = None
            self.btn_press_app = None
            self.btn_press_btn = None

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e):
        source_app = e.mimeData().text()
        pos = e.position().toPoint()
        target_widget = self.childAt(pos)
        while target_widget and not hasattr(target_widget, 'app_name'):
            target_widget = target_widget.parent()

        if target_widget:
            target_app = target_widget.app_name
            self.swap_apps(source_app, target_app)
        e.acceptProposedAction()

    def swap_apps(self, app_a, app_b):
        if app_a == app_b:
            return
        idx_a = next((i for i, w in enumerate(self.icon_items) if w.app_name == app_a), None)
        idx_b = next((i for i, w in enumerate(self.icon_items) if w.app_name == app_b), None)
        if idx_a is not None and idx_b is not None:
            self.icon_items[idx_a], self.icon_items[idx_b] = self.icon_items[idx_b], self.icon_items[idx_a]
            self.refresh_grid()
            self.save_order()

    def refresh_grid(self):
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.takeAt(i)
        max_col = 4
        row = 0
        col = 0
        for w in self.icon_items:
            self.grid_layout.addWidget(w, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1

    def save_order(self):
        order = [w.app_name for w in self.icon_items]
        save_icon_order(order)

    def on_add_app(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序", "", "程序文件 (*.exe *.cmd)")
        if path:
            self.add_custom_app(path)

    def add_custom_app(self, exe_path):
        import uuid
        app_id = f"app_{uuid.uuid4().hex[:8]}"
        name = os.path.splitext(os.path.basename(exe_path))[0]
        dlg = QInputDialog(self)
        dlg.setWindowTitle('设置名称')
        dlg.setLabelText('显示名称:')
        dlg.setTextValue(name)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            display_name = dlg.textValue()
        else:
            display_name = name
        
        ext = os.path.splitext(exe_path)[1].lower()
        if ext == '.cmd':
            self.custom_app_paths[app_id] = exe_path
            self.last_versions[app_id] = exe_path
            save_last_versions(self.last_versions)
            self.app_data[app_id] = ['.cmd']
        else:
            self.custom_app_paths[app_id] = exe_path
            self.last_versions[app_id] = exe_path
            save_last_versions(self.last_versions)
            self.app_data[app_id] = ['']
        
        icon_cfg = load_icon_config()
        icon_cfg[f"{app_id}_name"] = display_name if display_name else name
        save_icon_config(icon_cfg)
        
        self.create_app_icons()
        self.save_order()

    def toggle_log(self):
        v = not self.log_widget.isVisible()
        self.log_widget.setVisible(v)
        self.log_btn.setText('▲' if v else 'ℹ️')

    def toggle_top(self):
        is_checked = self.top_btn.isChecked()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, is_checked)
        QTimer.singleShot(0, self.show)

    def log(self, msg):
        self.log_widget.append(msg)
        write_log(msg)

    def quick_launch(self, app_name):
        if app_name in self.custom_app_paths:
            exe = self.custom_app_paths[app_name]
            ext = os.path.splitext(exe)[1].lower()
            if ext == '.cmd':
                subprocess.Popen(['cmd', '/c', exe], shell=True)
            else:
                subprocess.Popen([exe], shell=True)
            self.log(f"启动: {exe}")
        else:
            self.log(f"❌ 应用不存在: {app_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = ApplauncherUI()
    w.show()
    sys.exit(app.exec())