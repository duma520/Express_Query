# Express_Query_Pro.py
import sys
import os
import hashlib
import json
import requests
import sqlite3
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
from threading import Lock
import base64
from io import BytesIO
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QListWidget,
    QListWidgetItem, QTextEdit, QScrollArea, QProgressBar, QStatusBar,
    QTabWidget, QDialog, QFileDialog, QMessageBox, QInputDialog, QCheckBox,
    QSpinBox, QDateEdit, QCalendarWidget, QMenu
)

from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSize, QByteArray, QBuffer, QIODevice,
    QDate, QUrl
)

from PySide6.QtGui import (
    QFont, QColor, QPixmap, QIcon, QImage, QPainter, QPalette, QBrush,
    QCursor, QKeySequence, QAction, QShortcut
)


# 默认窗口大小
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900

# 获取程序当前目录
def get_app_dir():
    """获取应用程序目录"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent

APP_DIR = get_app_dir()

# ==================== 项目信息元数据 ====================
class ProjectInfo:
    """项目信息元数据（集中管理所有项目相关信息）"""
    VERSION = "1.1.45"  # 更新版本号
    BUILD_DATE = "2026-04-12"
    AUTHOR = "杜玛"
    LICENSE = "GNU Affero General Public License v3.0"
    COPYRIGHT = "© 永久 杜玛"
    URL = "https://github.com/duma520/Express_Query"
    MAINTAINER_EMAIL = "不提供"
    NAME = "快递查询系统"
    NAME_ENG = "Express_Query"
    DESCRIPTION = "Express_Query 快递查询系统"
    
    @classmethod
    def get_full_name(cls) -> str:
        """获取完整的程序名称（带版本）"""
        return f"{cls.NAME} v{cls.VERSION}"
    
    @classmethod
    def get_full_title(cls, username: str = None) -> str:
        """获取完整的窗口标题"""
        base = f"{cls.get_full_name()} 构建:{cls.BUILD_DATE}"
        if username:
            return f"{base} - 当前用户: {username}"
        return base
    
    @classmethod
    def get_short_title(cls) -> str:
        """获取简短标题"""
        return f"{cls.NAME} v{cls.VERSION}"
    
    @classmethod
    def get_window_title(cls, username: str = None, tab_info: str = None) -> str:
        """获取窗口标题（支持额外信息）"""
        title = cls.get_full_title(username)
        if tab_info:
            title = f"{title} - {tab_info}"
        return title
    
    @classmethod
    def get_about_text(cls) -> str:
        """获取关于信息文本"""
        return f"""
        <h2>{cls.NAME}</h2>
        <p><b>版本:</b> {cls.VERSION}</p>
        <p><b>构建日期:</b> {cls.BUILD_DATE}</p>
        <p><b>作者:</b> {cls.AUTHOR}</p>
        <p><b>版权:</b> {cls.COPYRIGHT}</p>
        <p><b>许可证:</b> {cls.LICENSE}</p>
        <p><b>项目主页:</b> <a href='{cls.URL}'>{cls.URL}</a></p>
        <p><b>描述:</b> {cls.DESCRIPTION}</p>
        """
    
    @classmethod
    def get_about_html(cls) -> str:
        """获取关于信息的HTML格式（用于对话框）"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Microsoft YaHei', sans-serif; padding: 10px; }}
                h2 {{ color: #4A90D9; margin-bottom: 15px; }}
                p {{ margin: 8px 0; }}
                a {{ color: #4A90D9; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .copyright {{ color: #888; font-size: 12px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <h2>{cls.NAME}</h2>
            <p><b>版本:</b> {cls.VERSION}</p>
            <p><b>构建日期:</b> {cls.BUILD_DATE}</p>
            <p><b>作者:</b> {cls.AUTHOR}</p>
            <p><b>版权:</b> {cls.COPYRIGHT}</p>
            <p><b>许可证:</b> {cls.LICENSE}</p>
            <p><b>项目主页:</b> <a href='{cls.URL}'>{cls.URL}</a></p>
            <p><b>描述:</b> {cls.DESCRIPTION}</p>
            <p class='copyright'>{cls.COPYRIGHT}</p>
        </body>
        </html>
        """
    
    @classmethod
    def get_version_info(cls) -> dict:
        """获取版本信息字典"""
        return {
            'name': cls.NAME,
            'version': cls.VERSION,
            'build_date': cls.BUILD_DATE,
            'author': cls.AUTHOR,
            'copyright': cls.COPYRIGHT,
            'license': cls.LICENSE,
            'url': cls.URL
        }





# 全局常量
APP_NAME = ProjectInfo.NAME_ENG
APP_VERSION = ProjectInfo.VERSION
DB_VERSION = "1.0"
BACKUP_DIR = "backups"
MAX_BACKUP_COUNT = 30
DEBUG_MODE = False

# ==================== 马卡龙色系定义 ====================
class MacaronColors:
    """马卡龙色系完整定义"""
    # 粉色系
    PINK_SAKURA = QColor('#FFB7CE')      # 樱花粉
    PINK_ROSE = QColor('#FF9AA2')        # 玫瑰粉
    PINK_COTTON = QColor('#FFD1DC')      # 棉花粉
    PINK_BALLET = QColor('#FCC9D3')      # 芭蕾粉
    
    # 蓝色系
    BLUE_SKY = QColor('#A2E1F6')         # 天空蓝
    BLUE_MIST = QColor('#C2E5F9')        # 雾霾蓝
    BLUE_PERIWINKLE = QColor('#C5D0E6')  # 长春花蓝
    BLUE_LAVENDER = QColor('#D6EAF8')    # 薰衣草蓝
    
    # 绿色系
    GREEN_MINT = QColor('#B5EAD7')       # 薄荷绿
    GREEN_APPLE = QColor('#D4F1C7')      # 苹果绿
    GREEN_PISTACHIO = QColor('#D8E9D6')  # 开心果绿
    GREEN_SAGE = QColor('#C9DFC5')       # 鼠尾草绿
    
    # 黄色/橙色系
    YELLOW_LEMON = QColor('#FFEAA5')      # 柠檬黄
    YELLOW_CREAM = QColor('#FFF8B8')      # 奶油黄
    YELLOW_HONEY = QColor('#FCE5B4')      # 蜂蜜黄
    ORANGE_PEACH = QColor('#FFDAC1')      # 蜜桃橙
    ORANGE_APRICOT = QColor('#FDD9B5')    # 杏色
    
    # 紫色系
    PURPLE_LAVENDER = QColor('#C7CEEA')   # 薰衣草紫
    PURPLE_TARO = QColor('#D8BFD8')       # 香芋紫
    PURPLE_WISTERIA = QColor('#C9B6D9')   # 紫藤
    PURPLE_MAUVE = QColor('#E0C7D7')      # 淡紫
    
    # 中性色
    NEUTRAL_CARAMEL = QColor('#F0E6DD')   # 焦糖奶霜
    NEUTRAL_CREAM = QColor('#F7F1E5')     # 奶油白
    NEUTRAL_MOCHA = QColor('#EAD7C7')     # 摩卡
    NEUTRAL_ALMOND = QColor('#F2E4D4')    # 杏仁
    
    # 其他颜色
    RED_CORAL = QColor('#FFB3A7')          # 珊瑚红
    RED_WATERMELON = QColor('#FFC5C5')     # 西瓜红
    TEAL_MINT = QColor('#B8E2DE')          # 薄荷绿蓝
    
    # 文字颜色
    TEXT_DARK = QColor('#5A5A5A')          # 深灰色文字
    TEXT_MEDIUM = QColor('#7A7A7A')        # 中灰色文字
    TEXT_LIGHT = QColor('#9A9A9A')         # 浅灰色文字
    
    # 边框颜色
    BORDER_LIGHT = QColor('#E8E0D5')       # 浅边框
    BORDER_MEDIUM = QColor('#D4C9BD')      # 中等边框
    
    # 背景颜色
    BG_MAIN = QColor('#FDF8F5')            # 主背景色
    BG_CARD = QColor('#FFFFFF')            # 卡片背景色
    BG_HOVER = QColor('#F5F0EB')           # 悬停背景色
    
    @classmethod
    def get_color_list(cls):
        """获取所有马卡龙颜色列表"""
        return [
            cls.PINK_SAKURA, cls.PINK_ROSE, cls.PINK_COTTON, cls.PINK_BALLET,
            cls.BLUE_SKY, cls.BLUE_MIST, cls.BLUE_PERIWINKLE, cls.BLUE_LAVENDER,
            cls.GREEN_MINT, cls.GREEN_APPLE, cls.GREEN_PISTACHIO, cls.GREEN_SAGE,
            cls.YELLOW_LEMON, cls.YELLOW_CREAM, cls.YELLOW_HONEY, cls.ORANGE_PEACH,
            cls.ORANGE_APRICOT, cls.PURPLE_LAVENDER, cls.PURPLE_TARO, cls.PURPLE_WISTERIA,
            cls.PURPLE_MAUVE, cls.NEUTRAL_CARAMEL, cls.NEUTRAL_CREAM, cls.NEUTRAL_MOCHA,
            cls.NEUTRAL_ALMOND, cls.RED_CORAL, cls.RED_WATERMELON, cls.TEAL_MINT
        ]
    
    @classmethod
    def get_color_names(cls):
        """获取马卡龙颜色名称列表"""
        return [
            "樱花粉", "玫瑰粉", "棉花粉", "芭蕾粉",
            "天空蓝", "雾霾蓝", "长春花蓝", "薰衣草蓝",
            "薄荷绿", "苹果绿", "开心果绿", "鼠尾草绿",
            "柠檬黄", "奶油黄", "蜂蜜黄", "蜜桃橙",
            "杏色", "薰衣草紫", "香芋紫", "紫藤",
            "淡紫", "焦糖奶霜", "奶油白", "摩卡",
            "杏仁", "珊瑚红", "西瓜红", "薄荷绿蓝"
        ]


# ==================== 全局样式表 ====================
class MacaronStyle:
    """马卡龙风格样式表（精简版 - 无圆角，保持原始大小）"""
    
    @classmethod
    def get_main_style(cls) -> str:
        """获取主窗口样式"""
        return f"""
            QMainWindow {{
                background-color: {MacaronColors.BG_MAIN.name()};
            }}
            
            QWidget {{
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-size: 12px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                margin-top: 12px;
                padding-top: 10px;
                background-color: {MacaronColors.BG_CARD.name()};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {MacaronColors.TEXT_DARK.name()};
                background-color: transparent;
            }}
            
            /* 按钮 - 去掉圆角和多余padding */
            QPushButton {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px 8px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_SKY.name()};
            }}
            
            QPushButton:pressed {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
            
            QPushButton:disabled {{
                background-color: {MacaronColors.NEUTRAL_MOCHA.name()};
                color: {MacaronColors.TEXT_LIGHT.name()};
            }}
            
            /* 输入框 - 保持原始高度 */
            QLineEdit {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px 4px;
                background-color: white;
                selection-background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
            
            QLineEdit:focus {{
                border: 1px solid {MacaronColors.BLUE_SKY.name()};
            }}
            
            /* 下拉框 - 保持原始高度 */
            QComboBox {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px 4px;
                background-color: white;
            }}
            
            QComboBox:hover {{
                border: 1px solid {MacaronColors.BLUE_SKY.name()};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 16px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {MacaronColors.TEXT_MEDIUM.name()};
                margin-right: 4px;
            }}
            
            /* 表格 - 去掉圆角 */
            QTableWidget {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                background-color: white;
                gridline-color: {MacaronColors.BORDER_LIGHT.name()};
                alternate-background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                selection-background-color: {MacaronColors.BLUE_LAVENDER.name()};
                selection-color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QTableWidget::item {{
                padding: 2px 4px;
                border-bottom: 1px solid {MacaronColors.BORDER_LIGHT.name()};
            }}
            
            QTableWidget::item:selected {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
            
            QHeaderView::section {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                padding: 4px;
                border: none;
                border-right: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                border-bottom: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                font-weight: bold;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                background-color: {MacaronColors.BG_CARD.name()};
                padding: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                border-bottom: none;
                padding: 4px 12px;
                margin-right: 2px;
                color: {MacaronColors.TEXT_MEDIUM.name()};
            }}
            
            QTabBar::tab:selected {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                width: 10px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {MacaronColors.PINK_ROSE.name()};
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                height: 10px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {MacaronColors.PINK_ROSE.name()};
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            
            QProgressBar {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                text-align: center;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QProgressBar::chunk {{
                background-color: {MacaronColors.GREEN_MINT.name()};
            }}
            
            QStatusBar {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_MEDIUM.name()};
                border-top: 1px solid {MacaronColors.BORDER_LIGHT.name()};
            }}
            
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QTextEdit {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                background-color: white;
                selection-background-color: {MacaronColors.BLUE_LAVENDER.name()};
                padding: 2px;
            }}
            
            QTreeWidget {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                background-color: white;
                alternate-background-color: {MacaronColors.NEUTRAL_CREAM.name()};
            }}
            
            QTreeWidget::item {{
                padding: 2px;
            }}
            
            QTreeWidget::item:selected {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QListWidget {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                background-color: white;
                alternate-background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                padding: 2px;
            }}
            
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {MacaronColors.BORDER_LIGHT.name()};
            }}
            
            QListWidget::item:selected {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            
            QListWidget::item:hover {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
            
            QCheckBox {{
                spacing: 4px;
            }}
            
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {MacaronColors.BORDER_MEDIUM.name()};
                background-color: white;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                border-color: {MacaronColors.GREEN_MINT.name()};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {MacaronColors.BLUE_SKY.name()};
            }}
            
            QSpinBox {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px;
                background-color: white;
            }}
            
            QSpinBox:focus {{
                border-color: {MacaronColors.BLUE_SKY.name()};
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                border: none;
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                width: 14px;
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
            
            QDateEdit {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px;
                background-color: white;
            }}
            
            QDateEdit::drop-down {{
                border: none;
                width: 16px;
            }}
            
            QDateEdit::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {MacaronColors.TEXT_MEDIUM.name()};
            }}
            
            QCalendarWidget {{
                background-color: white;
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
            }}
            
            QCalendarWidget QToolButton {{
                background-color: transparent;
                border: none;
                padding: 2px;
            }}
            
            QCalendarWidget QToolButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
            
            QCalendarWidget QMenu {{
                background-color: white;
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
            }}
            
            QCalendarWidget QTableView {{
                alternate-background-color: {MacaronColors.NEUTRAL_CREAM.name()};
            }}
            
            QMessageBox {{
                background-color: {MacaronColors.BG_CARD.name()};
            }}
            
            QMenu {{
                background-color: white;
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px;
            }}
            
            QMenu::item {{
                padding: 4px 20px 4px 16px;
            }}
            
            QMenu::item:selected {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {MacaronColors.BORDER_LIGHT.name()};
                margin: 2px 0;
            }}
        """
    
    @classmethod
    def get_category_style(cls, color: QColor) -> str:
        """获取分类标题样式"""
        return f"""
            QWidget {{
                background-color: {color.name()};
                padding: 2px;
            }}
        """


class DatabaseManagerPro:
    """数据库管理器 - 支持多用户独立数据库"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.lock = Lock()
        self.wal_mode = True
        
    def connect(self, db_path: str = None) -> bool:
        """连接数据库"""
        try:
            if db_path:
                self.db_path = db_path
                
            if not self.db_path:
                return False
                
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            if self.wal_mode:
                self.cursor.execute("PRAGMA journal_mode=WAL")
                self.cursor.execute("PRAGMA synchronous=NORMAL")
                self.cursor.execute("PRAGMA cache_size=-64000")
                self.cursor.execute("PRAGMA temp_store=MEMORY")
                
            return True
        except Exception as e:
            if DEBUG_MODE:
                print(f"数据库连接失败: {e}")
            return False
            
    def disconnect(self):
        """断开数据库连接"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.cursor = None
        except Exception as e:
            if DEBUG_MODE:
                print(f"断开数据库连接失败: {e}")
                
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询"""
        with self.lock:
            try:
                self.cursor.execute(query, params)
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
            except Exception as e:
                if DEBUG_MODE:
                    print(f"查询执行失败: {e}")
                return []
                
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """执行更新"""
        with self.lock:
            try:
                self.cursor.execute(query, params)
                self.connection.commit()
                return True
            except Exception as e:
                if DEBUG_MODE:
                    print(f"更新执行失败: {e}")
                return False
                
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """批量执行"""
        with self.lock:
            try:
                self.cursor.executemany(query, params_list)
                self.connection.commit()
                return True
            except Exception as e:
                if DEBUG_MODE:
                    print(f"批量执行失败: {e}")
                return False
                
    def get_table_info(self) -> Dict:
        """获取数据库表信息"""
        tables = {}
        try:
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            table_rows = self.execute_query(tables_query)
            
            for row in table_rows:
                table_name = row['name']
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                count_result = self.execute_query(count_query)
                count = count_result[0]['count'] if count_result else 0
                
                tables[table_name] = {
                    'count': count,
                    'name': table_name
                }
        except Exception as e:
            if DEBUG_MODE:
                print(f"获取表信息失败: {e}")
                
        return tables
        
    def get_database_size(self) -> int:
        """获取数据库文件大小"""
        try:
            if self.db_path and os.path.exists(self.db_path):
                return os.path.getsize(self.db_path)
        except:
            pass
        return 0
        
    def vacuum(self):
        """优化数据库"""
        try:
            self.cursor.execute("VACUUM")
            self.connection.commit()
        except Exception as e:
            if DEBUG_MODE:
                print(f"数据库优化失败: {e}")

class DeliveryTimeEstimator:
    """送达时间预估器 - 基于历史数据"""
    
    def __init__(self, db_manager: DatabaseManagerPro):
        self.db_manager = db_manager
        self.init_table()
        
    def init_table(self):
        """初始化时效数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS delivery_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            company_code TEXT NOT NULL,
            company_name TEXT,
            origin_city TEXT,
            dest_city TEXT,
            pickup_time TEXT,
            sign_time TEXT,
            arrival_time TEXT,
            delivery_days INTEGER,
            arrival_days INTEGER,
            route_key TEXT,
            delivery_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tracking_number, company_code)
        )
        """
        self.db_manager.execute_update(sql)
        
        # 添加新字段（如果表已存在）
        try:
            self.db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN arrival_time TEXT")
        except:
            pass
        try:
            self.db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN arrival_days INTEGER")
        except:
            pass
        try:
            self.db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN delivery_type TEXT")
        except:
            pass
        
        # 创建索引
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_route_key ON delivery_history(route_key)",
            "CREATE INDEX IF NOT EXISTS idx_company_code ON delivery_history(company_code)"
        ]
        for sql in index_sqls:
            self.db_manager.execute_update(sql)
            
    def extract_city(self, context: str) -> str:
        """从物流信息中提取城市"""
        # 常见城市关键词
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '重庆',
                  '天津', '苏州', '西安', '郑州', '长沙', '青岛', '济南', '合肥', '福州',
                  '厦门', '宁波', '大连', '沈阳', '哈尔滨', '长春', '昆明', '南宁', '贵阳',
                  '太原', '石家庄', '南昌', '乌鲁木齐', '兰州', '呼和浩特', '银川', '西宁',
                  '海口', '三亚', '珠海', '佛山', '东莞', '惠州', '中山', '江门', '湛江',
                  '无锡', '常州', '南通', '扬州', '镇江', '徐州', '温州', '绍兴', '嘉兴',
                  '金华', '台州', '泉州', '漳州', '莆田', '龙岩', '烟台', '威海', '潍坊']
        
        for city in cities:
            if city in context:
                return city
        return ""
        
    def is_arrived_at_station(self, context: str) -> bool:
        """判断是否已到达驿站/代收点"""
        驿站_keywords = [
            '驿站', '菜鸟', '丰巢', '快递柜', '自提柜', '代收点', '妈妈驿站', 
            '兔喜', '超市', '代理点', '自提', '代收', '投柜', '出柜',
            '存局', '已送达', '便利店', '物业', '门卫', '快递点', '菜鸟驿站',
            '菜鸟裹裹', '取件码', '凭取件码', '请取件', '可取件', '待取件',
            '快递超市', '邻里驿站', '熊猫快收', '速递易', '云柜', '日日顺',
            '蜂巢', 'e栈', '收件宝', '近邻宝', '格格货栈', '乐收'
        ]
        context_lower = context.lower()
        for keyword in 驿站_keywords:
            if keyword in context_lower or keyword in context:
                return True
        return False
        
    def is_signed(self, context: str) -> bool:
        """判断是否已签收"""
        sign_keywords = ['签收', '已收', '妥投', '已签收', '本人签收', '他人签收', '快递员签收']
        context_lower = context.lower()
        for keyword in sign_keywords:
            if keyword in context_lower or keyword in context:
                return True
        return False
        
    def record_delivery(self, express_data: Dict):
        """记录已签收或已到驿站的快递时效数据"""
        tracking_num = express_data.get('nu', '')
        company_code = express_data.get('com', '')
        state = str(express_data.get('state', ''))

        # 检查是否已记录
        check_sql = "SELECT id FROM delivery_history WHERE tracking_number = ? AND company_code = ?"
        existing = self.db_manager.execute_query(check_sql, (tracking_num, company_code))
        if existing:
            return
            
        track_list = express_data.get('data', [])
        if len(track_list) < 2:
            return
            
        # 找揽收时间
        pickup_time = None
        origin_city = ""
        
        # 找签收时间或到达驿站时间
        sign_time = None
        arrival_time = None
        dest_city = ""
        delivery_type = ""
        
        for track in track_list:
            context = track.get('context', '')
            time_str = track.get('time', '')
            
            # 找揽收
            if not pickup_time and ('揽收' in context or '已揽件' in context or '收件' in context):
                pickup_time = time_str
                origin_city = self.extract_city(context)
                
            # 找签收
            if not sign_time and self.is_signed(context):
                sign_time = time_str
                dest_city = self.extract_city(context)
                delivery_type = 'signed'
                
            # 找到达驿站（如果没有签收的话）
            if not arrival_time and not sign_time and self.is_arrived_at_station(context):
                arrival_time = time_str
                dest_city = self.extract_city(context)
                delivery_type = 'arrived'
                
        if not pickup_time:
            return
            
        # 确定终点时间
        end_time = sign_time if sign_time else arrival_time
        if not end_time:
            return
            
        # 计算天数差
        try:
            pickup_dt = datetime.strptime(pickup_time, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            delivery_days = (end_dt - pickup_dt).days
            if delivery_days < 0:
                delivery_days = 0
        except:
            return
            
        # 生成线路key
        route_key = f"{origin_city}->{dest_city}" if origin_city and dest_city else "未知线路"
        
        # 获取公司名称
        company_name = ""
        company_sql = "SELECT company_name FROM express_summary WHERE tracking_number = ? LIMIT 1"
        result = self.db_manager.execute_query(company_sql, (tracking_num,))
        if result:
            company_name = result[0].get('company_name', '')
            
        # 保存记录
        sql = """
        INSERT INTO delivery_history 
        (tracking_number, company_code, company_name, origin_city, dest_city, 
         pickup_time, sign_time, arrival_time, delivery_days, arrival_days, route_key, delivery_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db_manager.execute_update(sql, (
            tracking_num, company_code, company_name, origin_city, dest_city,
            pickup_time, sign_time, arrival_time, delivery_days, delivery_days, route_key, delivery_type
        ))
        
    def estimate_delivery_days(self, company_code: str, context: str = "", delivery_type: str = None) -> Tuple[Optional[int], str]:
        """
        预估送达天数
        返回 (预估天数, 预估说明)
        """
        if not company_code:
            return None, "未知快递公司"
            
        # 查询该快递公司的历史平均时效
        sql = """
        SELECT AVG(delivery_days) as avg_days, 
               MIN(delivery_days) as min_days,
               MAX(delivery_days) as max_days,
               COUNT(*) as count
        FROM delivery_history 
        WHERE company_code = ?
        """
        params = [company_code]
        
        # 如果指定了类型，按类型筛选
        if delivery_type:
            sql += " AND delivery_type = ?"
            params.append(delivery_type)
            
        result = self.db_manager.execute_query(sql, tuple(params))
        
        if result and result[0]['count'] > 0:
            avg_days = round(result[0]['avg_days'], 1)
            count = result[0]['count']
            type_text = "签收" if delivery_type == 'signed' else ("到达驿站" if delivery_type == 'arrived' else "")
            
            if count >= 3:
                return int(avg_days) if avg_days == int(avg_days) else avg_days, \
                       f"基于{count}条{type_text}历史记录，该快递公司平均{avg_days}天送达"
            else:
                return int(avg_days) if avg_days == int(avg_days) else avg_days, \
                       f"基于{count}条{type_text}历史记录，平均{avg_days}天（数据较少，仅供参考）"
        
        # 没有历史数据，使用默认值
        default_days = {
            'shunfeng': 2,
            'jd': 2,
            'yuantong': 3,
            'zhongtong': 3,
            'yunda': 3,
            'shentong': 3,
            'ems': 4,
            'youzhengguo': 5,
        }
        
        days = default_days.get(company_code, 3)
        return days, f"无历史数据，按行业平均预估{days}天"
        
    def get_estimate_text(self, express_data: Dict) -> str:
        """获取预估送达文本"""
        state = str(express_data.get('state', ''))
        track_list = express_data.get('data', [])
        context = track_list[0].get('context', '') if track_list else ''
        
        # 已签收
        if state == '3' or self.is_signed(context):
            for track in track_list:
                if self.is_signed(track.get('context', '')):
                    return f"已于 {track.get('time', '')} 签收"
            return "已签收"
        
        # 已到驿站
        if self.is_arrived_at_station(context):
            return "已到达取件点，请尽快取件"
            
        # 派件中
        if state == '5' or '派件' in context or '派送' in context:
            return "派件中，预计今天或明天送达"
            
        # 疑难件
        if state == '2' or '疑难' in context or '问题' in context or '异常' in context:
            return "快递异常，请联系快递公司"
            
        # 在途中 - 预估
        if track_list:
            company_code = express_data.get('com', '')
            
            days, explanation = self.estimate_delivery_days(company_code, context)
            if days:
                # 计算预计到达日期
                today = datetime.now()
                arrival_date = today + timedelta(days=int(days) if isinstance(days, float) else days)
                return f"预计{arrival_date.strftime('%m月%d日')}送达 ({explanation})"
                
        return "暂无预估信息"

class ApiAccountManager:
    """API账号管理器"""
    
    def __init__(self, db_manager: DatabaseManagerPro):
        self.db_manager = db_manager
        self.current_account = None
        self.accounts = []
        self.load_accounts()
        self.check_and_reset_daily_usage()  # 初始化时检查是否需要重置
        
    def check_and_reset_daily_usage(self):
        """检查并重置每日使用次数（不重置 current_account）"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查询所有账号，检查last_used_date是否为今天
        query = "SELECT id, last_used_date FROM api_accounts WHERE is_active = 1"
        accounts = self.db_manager.execute_query(query)
        
        for account in accounts:
            last_used_date = account.get('last_used_date', '')
            if last_used_date != today:
                reset_sql = """
                UPDATE api_accounts 
                SET used_today = 0, last_used_date = NULL 
                WHERE id = ?
                """
                self.db_manager.execute_update(reset_sql, (account['id'],))
        
        # ========== 重要修改：不要在这里调用 load_accounts()，避免重置 current_account ==========
        # 只更新 accounts 列表中的数据，不改变 current_account
        self._refresh_accounts_list()

    def _refresh_accounts_list(self):
        """刷新账号列表数据，但不改变 current_account"""
        query = """
        SELECT * FROM api_accounts 
        WHERE is_active = 1 
        ORDER BY sort_order, id
        """
        new_accounts = self.db_manager.execute_query(query)
        
        # 确保所有账号的last_used_date字段存在
        for account in new_accounts:
            try:
                check_sql = "SELECT last_used_date FROM api_accounts LIMIT 1"
                self.db_manager.execute_query(check_sql)
            except:
                try:
                    alter_sql = "ALTER TABLE api_accounts ADD COLUMN last_used_date TEXT"
                    self.db_manager.execute_update(alter_sql)
                except:
                    pass
        
        # 保存当前账号ID
        current_id = self.current_account['id'] if self.current_account else None
        
        # 更新列表
        self.accounts = new_accounts
        
        # 恢复当前账号（如果还存在）
        if current_id:
            for acc in self.accounts:
                if acc['id'] == current_id:
                    self.current_account = acc
                    break
            else:
                # 如果当前账号已被删除，则使用第一个
                if self.accounts:
                    self.current_account = self.accounts[0]
        else:
            if self.accounts:
                self.current_account = self.accounts[0]

    def load_accounts(self):
        """加载所有账号（会重置 current_account 为第一个）"""
        query = """
        SELECT * FROM api_accounts 
        WHERE is_active = 1 
        ORDER BY sort_order, id
        """
        self.accounts = self.db_manager.execute_query(query)
        
        # 确保所有账号的last_used_date字段存在
        for account in self.accounts:
            try:
                check_sql = "SELECT last_used_date FROM api_accounts LIMIT 1"
                self.db_manager.execute_query(check_sql)
            except:
                try:
                    alter_sql = "ALTER TABLE api_accounts ADD COLUMN last_used_date TEXT"
                    self.db_manager.execute_update(alter_sql)
                except:
                    pass
            
            # 检查是否需要重置
            last_used_date = account.get('last_used_date', '')
            today = datetime.now().strftime('%Y-%m-%d')
            if last_used_date and last_used_date != today:
                reset_sql = """
                UPDATE api_accounts 
                SET used_today = 0, last_used_date = NULL 
                WHERE id = ?
                """
                self.db_manager.execute_update(reset_sql, (account['id'],))
                account['used_today'] = 0
                account['last_used_date'] = None
        
        if self.accounts:
            self.current_account = self.accounts[0]
            
    def get_current_account(self) -> Dict:
        """获取当前账号"""
        if not self.current_account and self.accounts:
            self.current_account = self.accounts[0]
        # 每次获取时检查是否需要重置
        self.check_and_reset_daily_usage()
        return self.current_account
        

    def switch_to_next_account(self, force_switch: bool = True) -> bool:
        """切换到下一个可用账号
        
        Args:
            force_switch: 是否强制切换（默认True，直接切换到下一个账号）
        """
        if not self.accounts:
            if DEBUG_MODE:
                print("[账号切换] 没有账号列表")
            return False
            
        # 先检查是否需要重置
        self.check_and_reset_daily_usage()
        
        # 如果不是强制切换，检查自动切换设置
        if not force_switch:
            sql = "SELECT value FROM user_settings WHERE key = 'auto_switch_account'"
            result = self.db_manager.execute_query(sql)
            if not result or result[0]['value'] != '1':
                if DEBUG_MODE:
                    print("[账号切换] 自动切换未启用")
                return False
        
        # 记录当前账号ID
        current_id = self.current_account['id'] if self.current_account else None
        current_name = self.current_account.get('account_name', '未知') if self.current_account else '无'

        current_index = self.get_current_account_index()
        total = len(self.accounts)
        
        # 只有一个账号，无法切换
        if total <= 1:
            if DEBUG_MODE:
                print(f"[账号切换] 只有 {total} 个账号，无法切换")
            return False
        
        if DEBUG_MODE:
            print(f"[账号切换] 当前账号: {current_name}, 总数: {total}, 强制切换: {force_switch}")
        
        # 记录已经尝试过的账号，避免无限循环
        tried_indices = set()
        
        for i in range(total):
            index = (current_index + i + 1) % total
            if index in tried_indices:
                continue
            tried_indices.add(index)
            
            account = self.accounts[index]
            account_name = account.get('account_name', '未知')
            
            # 强制切换：只要不是当前账号就切换
            if force_switch:
                if account['id'] != current_id:
                    self.current_account = account
                    self._refresh_single_account(account['id'])
                    if DEBUG_MODE:
                        print(f"[账号切换] 强制切换到账号: {account_name}")
                    return True
            else:
                # 正常切换：检查账号是否可用（额度未用完）
                used_today = account.get('used_today', 0)
                daily_limit = account.get('daily_limit', 100)
                
                if used_today < daily_limit:
                    self.current_account = account
                    self._refresh_single_account(account['id'])
                    if DEBUG_MODE:
                        print(f"[账号切换] 正常切换到账号: {account_name} ({used_today}/{daily_limit})")
                    return True
                else:
                    if DEBUG_MODE:
                        print(f"[账号切换] 账号 {account_name} 额度已满 ({used_today}/{daily_limit})，跳过")
        
        if DEBUG_MODE:
            print("[账号切换] 没有可切换的账号")
        return False

    def _refresh_single_account(self, account_id: int):
        """刷新单个账号的最新数据"""
        query = "SELECT * FROM api_accounts WHERE id = ?"
        result = self.db_manager.execute_query(query, (account_id,))
        if result:
            # 更新 accounts 列表中对应的账号
            for i, acc in enumerate(self.accounts):
                if acc['id'] == account_id:
                    self.accounts[i] = result[0]
                    if self.current_account and self.current_account['id'] == account_id:
                        self.current_account = result[0]
                    break

    def get_current_account_index(self) -> int:
        """获取当前账号索引"""
        if not self.current_account:
            return 0
            
        for i, account in enumerate(self.accounts):
            if account['id'] == self.current_account['id']:
                return i
        return 0
        
    def increment_usage(self, account_id: int = None):
        """增加使用次数"""
        if account_id is None and self.current_account:
            account_id = self.current_account['id']
            
        if account_id:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 先检查该账号是否需要重置
            check_sql = "SELECT last_used_date, used_today FROM api_accounts WHERE id = ?"
            result = self.db_manager.execute_query(check_sql, (account_id,))
            
            if result:
                last_used_date = result[0].get('last_used_date', '')
                current_used = result[0].get('used_today', 0)
                
                if last_used_date != today:
                    # 新的一天，从0开始计数
                    sql = """
                    UPDATE api_accounts 
                    SET used_today = 1, last_used_date = ?, last_used = ?
                    WHERE id = ?
                    """
                    self.db_manager.execute_update(sql, (today, today, account_id))
                else:
                    # 同一天，增加计数
                    sql = """
                    UPDATE api_accounts 
                    SET used_today = used_today + 1, last_used = ?
                    WHERE id = ?
                    """
                    self.db_manager.execute_update(sql, (today, account_id))
            else:
                # 账号不存在或查询失败
                sql = """
                UPDATE api_accounts 
                SET used_today = 1, last_used_date = ?, last_used = ?
                WHERE id = ?
                """
                self.db_manager.execute_update(sql, (today, today, account_id))
            
            # 重新加载账号数据
            self._refresh_accounts_list()
            
    def is_current_account_available(self) -> bool:
        """检查当前账号是否可用"""
        if not self.current_account:
            return False
        
        # 检查是否需要重置
        self.check_and_reset_daily_usage()
        
        # 重新获取当前账号的最新数据
        if self.current_account:
            account_id = self.current_account['id']
            query = "SELECT used_today, daily_limit FROM api_accounts WHERE id = ?"
            result = self.db_manager.execute_query(query, (account_id,))
            if result:
                used_today = result[0].get('used_today', 0)
                daily_limit = result[0].get('daily_limit', 100)
                return used_today < daily_limit
                
        return False
        
    def get_accounts(self) -> List[Dict]:
        """获取所有账号"""
        self.check_and_reset_daily_usage()
        return self.accounts
        
    def get_usage_info(self) -> Dict:
        """获取当前账号的使用信息"""
        if not self.current_account:
            return {'used': 0, 'limit': 100, 'remaining': 100}
        
        self.check_and_reset_daily_usage()
        
        account_id = self.current_account['id']
        query = "SELECT used_today, daily_limit FROM api_accounts WHERE id = ?"
        result = self.db_manager.execute_query(query, (account_id,))
        
        if result:
            used = result[0].get('used_today', 0)
            limit = result[0].get('daily_limit', 100)
            return {
                'used': used,
                'limit': limit,
                'remaining': limit - used
            }
        
        return {'used': 0, 'limit': 100, 'remaining': 100}


class ApiAccountDialog(QDialog):
    """API账号管理对话框"""
    
    def __init__(self, db_manager: DatabaseManagerPro, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.accounts = []
        self.init_ui()
        self.load_accounts()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle("API账号管理")
        self.setMinimumSize(950, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        info_label = QLabel("管理快递查询API账号，支持多账号自动切换。当额度用完时自动切换到下一个可用账号。")
        layout.addWidget(info_label)
        
        list_group = QGroupBox("账号列表")
        list_layout = QVBoxLayout()
        
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(8)
        self.account_table.setHorizontalHeaderLabels([
            "序号", "账号名称", "Customer", "Auth Key", "智能判断", 
            "今日已用/总额度", "状态", "操作"
        ])
        self.account_table.horizontalHeader().setStretchLastSection(True)
        self.account_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.account_table.setAlternatingRowColors(True)
        
        list_layout.addWidget(self.account_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加账号")
        add_btn.clicked.connect(self.add_account)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("编辑账号")
        edit_btn.clicked.connect(self.edit_account)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除账号")
        delete_btn.clicked.connect(self.delete_account)
        btn_layout.addWidget(delete_btn)
        
        move_up_btn = QPushButton("上移")
        move_up_btn.clicked.connect(self.move_up)
        btn_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("下移")
        move_down_btn.clicked.connect(self.move_down)
        btn_layout.addWidget(move_down_btn)
        
        btn_layout.addStretch()
    
        # 添加导入导出按钮
        export_btn = QPushButton("导出账号")
        export_btn.setToolTip("将所有账号导出到JSON文件")
        export_btn.clicked.connect(self.export_accounts)
        btn_layout.addWidget(export_btn)
        
        import_btn = QPushButton("导入账号")
        import_btn.setToolTip("从JSON文件导入账号")
        import_btn.clicked.connect(self.import_accounts)
        btn_layout.addWidget(import_btn)
        
        set_default_btn = QPushButton("设为当前使用")
        set_default_btn.clicked.connect(self.set_as_current)
        btn_layout.addWidget(set_default_btn)
        
        layout.addLayout(btn_layout)
        
        switch_group = QGroupBox("自动切换设置")
        switch_layout = QHBoxLayout()
        
        self.auto_switch_check = QCheckBox("启用额度用完自动切换账号")
        self.auto_switch_check.setToolTip("当当前账号今日额度用完时，自动切换到下一个可用账号")
        switch_layout.addWidget(self.auto_switch_check)
        
        switch_layout.addStretch()
        switch_group.setLayout(switch_layout)
        layout.addWidget(switch_group)
        
        bottom_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        bottom_layout.addWidget(save_btn)
        
        bottom_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        self.load_auto_switch_setting()
        
    def load_accounts(self):
        query = """
        SELECT * FROM api_accounts 
        WHERE is_active = 1 
        ORDER BY sort_order, id
        """
        self.accounts = self.db_manager.execute_query(query)
        self.update_table()
        
    def update_table(self):
        # 先检查是否需要重置
        today = datetime.now().strftime('%Y-%m-%d')

        self.account_table.setRowCount(len(self.accounts))
        
        for row, account in enumerate(self.accounts):
            self.account_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.account_table.setItem(row, 1, QTableWidgetItem(account.get('account_name', '')))
            
            customer = account.get('customer', '')
            display_customer = customer[:15] + '...' if len(customer) > 15 else customer
            self.account_table.setItem(row, 2, QTableWidgetItem(display_customer))
            
            auth_key = account.get('auth_key', '')
            display_key = auth_key[:15] + '...' if len(auth_key) > 15 else auth_key
            self.account_table.setItem(row, 3, QTableWidgetItem(display_key))
            
            smart_judge = "启用" if account.get('smart_judge', 1) else "禁用"
            self.account_table.setItem(row, 4, QTableWidgetItem(smart_judge))
        
            # 检查是否需要重置该账号的使用次数
            last_used_date = account.get('last_used_date', '')
            used = account.get('used_today', 0)
        
            if last_used_date != today:
                # 不是今天的记录，显示0
                used = 0
            
            limit = account.get('daily_limit', 100)
            usage_text = f"{used}/{limit}"
            item = QTableWidgetItem(usage_text)
            if used >= limit:
                item.setForeground(QColor(255, 0, 0))
            elif used >= limit * 0.8:
                item.setForeground(QColor(255, 165, 0))
            self.account_table.setItem(row, 5, item)
            
            status = "正常" if used < limit else "额度已满"
            status_item = QTableWidgetItem(status)
            if status == "额度已满":
                status_item.setForeground(QColor(255, 0, 0))
            else:
                status_item.setForeground(QColor(0, 150, 0))
            self.account_table.setItem(row, 6, status_item)
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            reset_btn = QPushButton("重置额度")
            reset_btn.clicked.connect(lambda checked, r=row: self.reset_usage(r))
            btn_layout.addWidget(reset_btn)
            
            btn_widget.setLayout(btn_layout)
            self.account_table.setCellWidget(row, 7, btn_widget)
            
        self.account_table.resizeColumnsToContents()
        
    def add_account(self):
        dialog = ApiAccountEditDialog(self.db_manager, None, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_accounts()
            
    def edit_account(self):
        row = self.account_table.currentRow()
        if row < 0 or row >= len(self.accounts):
            QMessageBox.warning(self, "提示", "请先选择要编辑的账号")
            return
            
        account = self.accounts[row]
        dialog = ApiAccountEditDialog(self.db_manager, account, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_accounts()
            
    def delete_account(self):
        row = self.account_table.currentRow()
        if row < 0 or row >= len(self.accounts):
            QMessageBox.warning(self, "提示", "请先选择要删除的账号")
            return
            
        account = self.accounts[row]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除账号 '{account.get('account_name', '')}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            sql = "UPDATE api_accounts SET is_active = 0 WHERE id = ?"
            self.db_manager.execute_update(sql, (account['id'],))
            self.load_accounts()
            
    def move_up(self):
        row = self.account_table.currentRow()
        if row <= 0 or row >= len(self.accounts):
            return
            
        account1 = self.accounts[row - 1]
        account2 = self.accounts[row]
        self.swap_order(account1['id'], account2['id'])
        self.load_accounts()
        self.account_table.selectRow(row - 1)
        
    def move_down(self):
        row = self.account_table.currentRow()
        if row < 0 or row >= len(self.accounts) - 1:
            return
            
        account1 = self.accounts[row]
        account2 = self.accounts[row + 1]
        self.swap_order(account1['id'], account2['id'])
        self.load_accounts()
        self.account_table.selectRow(row + 1)
        
    def swap_order(self, id1: int, id2: int):
        sql1 = "SELECT sort_order FROM api_accounts WHERE id = ?"
        result1 = self.db_manager.execute_query(sql1, (id1,))
        result2 = self.db_manager.execute_query(sql1, (id2,))
        
        if result1 and result2:
            order1 = result1[0]['sort_order']
            order2 = result2[0]['sort_order']
            
            sql2 = "UPDATE api_accounts SET sort_order = ? WHERE id = ?"
            self.db_manager.execute_update(sql2, (order2, id1))
            self.db_manager.execute_update(sql2, (order1, id2))
            
    def set_as_current(self):
        row = self.account_table.currentRow()
        if row < 0 or row >= len(self.accounts):
            QMessageBox.warning(self, "提示", "请先选择要设为当前的账号")
            return
            
        account = self.accounts[row]
        
        # 先将所有账号的 sort_order 重置
        sql1 = "UPDATE api_accounts SET sort_order = sort_order + 1"
        self.db_manager.execute_update(sql1)
        
        sql2 = "UPDATE api_accounts SET sort_order = 0 WHERE id = ?"
        self.db_manager.execute_update(sql2, (account['id'],))
        
        self.load_accounts()
        
        # ========== 修复：通过 QApplication 查找主窗口 ==========
        from PySide6.QtWidgets import QApplication
        
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ExpressQueryProGUI':
                main_window = widget
                break
        
        if main_window and hasattr(main_window, 'api_account_manager'):
            # 强制刷新账号管理器的数据
            main_window.api_account_manager.load_accounts()
            # 重新加载当前账号到主窗口
            main_window.load_current_api_account()
            # 更新显示
            main_window.update_api_account_display()
        # ========================================
        
        QMessageBox.information(self, "成功", f"已将 '{account['account_name']}' 设为当前使用账号，界面已更新")
        
    def reset_usage(self, row: int):
        if row < 0 or row >= len(self.accounts):
            return
            
        account = self.accounts[row]
        sql = "UPDATE api_accounts SET used_today = 0, last_used = NULL, last_used_date = NULL WHERE id = ?"
        self.db_manager.execute_update(sql, (account['id'],))
        self.load_accounts()
        
    def load_auto_switch_setting(self):
        sql = "SELECT value FROM user_settings WHERE key = 'auto_switch_account'"
        result = self.db_manager.execute_query(sql)
        if result:
            self.auto_switch_check.setChecked(result[0]['value'] == '1')
            
    def save_settings(self):
        auto_switch = '1' if self.auto_switch_check.isChecked() else '0'
        sql = "INSERT OR REPLACE INTO user_settings (key, value) VALUES ('auto_switch_account', ?)"
        self.db_manager.execute_update(sql, (auto_switch,))
        QMessageBox.information(self, "成功", "设置已保存")

    def export_accounts(self):
        """导出所有账号到JSON文件"""
        if not self.accounts:
            QMessageBox.information(self, "提示", "没有可导出的账号")
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出API账号", 
            f"api_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 准备导出数据（隐藏敏感信息的选项）
            reply = QMessageBox.question(
                self, "导出选项",
                "是否导出完整的密钥信息？\n\n"
                "点击「是」：导出完整的Customer和Auth Key（用于备份）\n"
                "点击「否」：密钥信息将部分隐藏（用于分享）",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            
            include_secrets = (reply == QMessageBox.Yes)
            
            export_data = {
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': APP_VERSION,
                'include_secrets': include_secrets,
                'accounts': []
            }
            
            for account in self.accounts:
                export_account = {
                    'account_name': account.get('account_name', ''),
                    'smart_judge': account.get('smart_judge', 1),
                    'daily_limit': account.get('daily_limit', 100),
                    'sort_order': account.get('sort_order', 0),
                }
                
                if include_secrets:
                    # 完整导出
                    export_account['customer'] = account.get('customer', '')
                    export_account['auth_key'] = account.get('auth_key', '')
                    export_account['secret'] = account.get('secret', '')
                    export_account['userid'] = account.get('userid', '')
                else:
                    # 部分隐藏
                    customer = account.get('customer', '')
                    auth_key = account.get('auth_key', '')
                    if customer:
                        export_account['customer'] = customer[:4] + '****' + customer[-4:] if len(customer) > 8 else '****'
                    else:
                        export_account['customer'] = ''
                    if auth_key:
                        export_account['auth_key'] = auth_key[:4] + '****' + auth_key[-4:] if len(auth_key) > 8 else '****'
                    else:
                        export_account['auth_key'] = ''
                    export_account['secret'] = '****' if account.get('secret') else ''
                    export_account['userid'] = account.get('userid', '')
                
                export_data['accounts'].append(export_account)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "导出成功", 
                f"已成功导出 {len(self.accounts)} 个账号到：\n{file_path}\n\n"
                f"{'包含完整密钥信息' if include_secrets else '密钥信息已部分隐藏'}")
                
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出账号时发生错误：\n{str(e)}")


    def import_accounts(self):
        """从JSON文件导入账号"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入API账号", "",
            "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 验证文件格式
            if 'accounts' not in import_data:
                QMessageBox.critical(self, "导入失败", "无效的账号文件格式")
                return
            
            accounts_to_import = import_data['accounts']
            include_secrets = import_data.get('include_secrets', False)
            
            if not accounts_to_import:
                QMessageBox.information(self, "提示", "文件中没有账号数据")
                return
            
            # 检查是否有完整密钥
            has_secrets = any('customer' in acc and 'auth_key' in acc and 
                            '****' not in str(acc.get('customer', '')) and 
                            '****' not in str(acc.get('auth_key', '')) 
                            for acc in accounts_to_import)
            
            if not has_secrets and include_secrets:
                QMessageBox.warning(self, "提示", 
                    "文件中的密钥信息已隐藏，无法导入完整账号。\n"
                    "请使用包含完整密钥的备份文件。")
                return
            
            # 选择导入模式
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("导入选项")
            msg_box.setText(f"发现 {len(accounts_to_import)} 个账号，请选择导入方式：")
            
            replace_btn = msg_box.addButton("替换现有账号", QMessageBox.YesRole)
            merge_btn = msg_box.addButton("合并到现有账号", QMessageBox.NoRole)
            cancel_btn = msg_box.addButton("取消", QMessageBox.RejectRole)
            
            msg_box.exec()
            
            clicked_btn = msg_box.clickedButton()
            
            if clicked_btn == cancel_btn:
                return
            
            replace_existing = (clicked_btn == replace_btn)
            
            # 获取现有账号名称列表（用于去重检查）
            existing_names = set()
            if not replace_existing:
                query = "SELECT account_name FROM api_accounts WHERE is_active = 1"
                existing = self.db_manager.execute_query(query)
                existing_names = {acc['account_name'] for acc in existing}
            
            import_count = 0
            skip_count = 0
            
            if replace_existing:
                # 先软删除所有现有账号
                sql = "UPDATE api_accounts SET is_active = 0"
                self.db_manager.execute_update(sql)
                
                # 重置排序
                sort_order = 0
                for account in accounts_to_import:
                    account_name = account.get('account_name', '').strip()
                    if not account_name:
                        skip_count += 1
                        continue
                    
                    # 插入账号
                    sql = """
                    INSERT INTO api_accounts 
                    (account_name, customer, auth_key, secret, userid, smart_judge, daily_limit, sort_order, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """
                    self.db_manager.execute_update(sql, (
                        account_name,
                        account.get('customer', ''),
                        account.get('auth_key', ''),
                        account.get('secret', ''),
                        account.get('userid', ''),
                        account.get('smart_judge', 1),
                        account.get('daily_limit', 100),
                        sort_order
                    ))
                    sort_order += 1
                    import_count += 1
            else:
                # 合并模式：只添加不存在的账号
                query = "SELECT MAX(sort_order) as max_order FROM api_accounts WHERE is_active = 1"
                result = self.db_manager.execute_query(query)
                max_order = result[0]['max_order'] if result and result[0]['max_order'] is not None else 0
                sort_order = max_order + 1
                
                for account in accounts_to_import:
                    account_name = account.get('account_name', '').strip()
                    if not account_name:
                        skip_count += 1
                        continue
                    
                    # 检查是否已存在
                    if account_name in existing_names:
                        # 询问是否覆盖
                        reply = QMessageBox.question(self, "账号已存在", 
                            f"账号 '{account_name}' 已存在，是否覆盖？\n"
                            "点击「是」覆盖现有账号，点击「否」跳过该账号。",
                            QMessageBox.Yes | QMessageBox.No)
                        
                        if reply == QMessageBox.Yes:
                            # 更新现有账号
                            sql = """
                            UPDATE api_accounts 
                            SET customer = ?, auth_key = ?, secret = ?, userid = ?, 
                                smart_judge = ?, daily_limit = ?, is_active = 1
                            WHERE account_name = ?
                            """
                            self.db_manager.execute_update(sql, (
                                account.get('customer', ''),
                                account.get('auth_key', ''),
                                account.get('secret', ''),
                                account.get('userid', ''),
                                account.get('smart_judge', 1),
                                account.get('daily_limit', 100),
                                account_name
                            ))
                            import_count += 1
                        else:
                            skip_count += 1
                    else:
                        # 插入新账号
                        sql = """
                        INSERT INTO api_accounts 
                        (account_name, customer, auth_key, secret, userid, smart_judge, daily_limit, sort_order, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """
                        self.db_manager.execute_update(sql, (
                            account_name,
                            account.get('customer', ''),
                            account.get('auth_key', ''),
                            account.get('secret', ''),
                            account.get('userid', ''),
                            account.get('smart_judge', 1),
                            account.get('daily_limit', 100),
                            sort_order
                        ))
                        sort_order += 1
                        import_count += 1
            
            # 重新加载账号列表
            self.load_accounts()
            
            # 显示导入结果
            result_msg = f"导入完成！\n成功导入：{import_count} 个账号"
            if skip_count > 0:
                result_msg += f"\n跳过：{skip_count} 个账号"
            
            QMessageBox.information(self, "导入完成", result_msg)
            
        except json.JSONDecodeError:
            QMessageBox.critical(self, "导入失败", "无效的JSON文件格式")
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入账号时发生错误：\n{str(e)}")

    def closeEvent(self, event):
        """关闭事件 - 通知主窗口刷新账号"""
        # 通知主窗口刷新账号
        from PySide6.QtWidgets import QApplication
        
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ExpressQueryProGUI':
                main_window = widget
                break
        
        if main_window and hasattr(main_window, 'api_account_manager'):
            main_window.api_account_manager.load_accounts()
            main_window.load_current_api_account()
            main_window.update_api_account_display()
        
        event.accept()

class ApiAccountEditDialog(QDialog):
    """API账号编辑对话框"""
    
    def __init__(self, db_manager: DatabaseManagerPro, account: Dict = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.account = account
        self.init_ui()
        
        if account:
            self.load_account_data()
        
        self.setStyleSheet(MacaronStyle.get_main_style())
            
    def init_ui(self):
        title = "编辑账号" if self.account else "添加账号"
        self.setWindowTitle(title)
        self.setMinimumSize(500, 420)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form_layout = QFormLayout()
        
        self.account_name_edit = QLineEdit()
        self.account_name_edit.setPlaceholderText("例如：主账号、备用账号1")
        form_layout.addRow("账号名称:", self.account_name_edit)
        
        self.customer_edit = QLineEdit()
        self.customer_edit.setPlaceholderText("请输入Customer ID")
        form_layout.addRow("Customer:", self.customer_edit)
        
        self.auth_key_edit = QLineEdit()
        self.auth_key_edit.setPlaceholderText("请输入Auth Key")
        form_layout.addRow("Auth Key:", self.auth_key_edit)
        
        self.secret_edit = QLineEdit()
        self.secret_edit.setPlaceholderText("可选，用于某些API")
        form_layout.addRow("Secret:", self.secret_edit)
        
        self.userid_edit = QLineEdit()
        self.userid_edit.setPlaceholderText("可选，用户ID")
        form_layout.addRow("UserID:", self.userid_edit)
        
        self.smart_judge_check = QCheckBox("启用智能判断")
        self.smart_judge_check.setChecked(True)
        self.smart_judge_check.setToolTip("根据快递单号自动识别快递公司")
        form_layout.addRow("智能判断:", self.smart_judge_check)
        
        self.daily_limit_spin = QSpinBox()
        self.daily_limit_spin.setRange(1, 10000)
        self.daily_limit_spin.setValue(100)
        self.daily_limit_spin.setSuffix(" 次")
        form_layout.addRow("每日额度:", self.daily_limit_spin)
        
        layout.addLayout(form_layout)
        
        info_label = QLabel("提示：Customer和Auth Key为必填项。\n每日额度用于判断账号是否可用，实际额度以API返回为准。")
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_account)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def load_account_data(self):
        if self.account:
            self.account_name_edit.setText(self.account.get('account_name', ''))
            self.customer_edit.setText(self.account.get('customer', ''))
            self.auth_key_edit.setText(self.account.get('auth_key', ''))
            self.secret_edit.setText(self.account.get('secret', ''))
            self.userid_edit.setText(self.account.get('userid', ''))
            self.smart_judge_check.setChecked(self.account.get('smart_judge', 1) == 1)
            self.daily_limit_spin.setValue(self.account.get('daily_limit', 100))
            
    def save_account(self):
        account_name = self.account_name_edit.text().strip()
        customer = self.customer_edit.text().strip()
        auth_key = self.auth_key_edit.text().strip()
        
        if not account_name:
            QMessageBox.warning(self, "提示", "请输入账号名称")
            return
            
        if not customer:
            QMessageBox.warning(self, "提示", "请输入Customer ID")
            return
            
        if not auth_key:
            QMessageBox.warning(self, "提示", "请输入Auth Key")
            return
            
        secret = self.secret_edit.text().strip()
        userid = self.userid_edit.text().strip()
        smart_judge = 1 if self.smart_judge_check.isChecked() else 0
        daily_limit = self.daily_limit_spin.value()
        
        if self.account:
            sql = """
            UPDATE api_accounts 
            SET account_name = ?, customer = ?, auth_key = ?, secret = ?, 
                userid = ?, smart_judge = ?, daily_limit = ?
            WHERE id = ?
            """
            self.db_manager.execute_update(sql, (
                account_name, customer, auth_key, secret, userid, 
                smart_judge, daily_limit, self.account['id']
            ))
        else:
            query = "SELECT MAX(sort_order) as max_order FROM api_accounts WHERE is_active = 1"
            result = self.db_manager.execute_query(query)
            max_order = result[0]['max_order'] if result and result[0]['max_order'] is not None else 0
            sort_order = max_order + 1
            
            sql = """
            INSERT INTO api_accounts 
            (account_name, customer, auth_key, secret, userid, smart_judge, daily_limit, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db_manager.execute_update(sql, (
                account_name, customer, auth_key, secret, userid, 
                smart_judge, daily_limit, sort_order
            ))
            
        self.accept()

class UserManagerPro:
    """用户管理器"""
    
    def __init__(self, app_data_dir: str):
        self.app_data_dir = Path(app_data_dir)
        self.users_db_path = self.app_data_dir / "users.db"
        self.db_manager = DatabaseManagerPro(str(self.users_db_path))
        self.current_user = None
        self.current_user_db = None
        
        self.init_users_database()
        
    def init_users_database(self):
        """初始化用户数据库"""
        if not self.db_manager.connect(str(self.users_db_path)):
            return
            
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            settings TEXT,
            is_active INTEGER DEFAULT 1
        )
        """
        
        self.db_manager.execute_update(create_table_sql)
        
        users = self.get_all_users()
        if not users:
            self.add_user("默认用户")
            
    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        query = "SELECT * FROM users WHERE is_active = 1 ORDER BY last_login DESC"
        return self.db_manager.execute_query(query)
        
    def add_user(self, username: str) -> Tuple[bool, str]:
        """添加用户"""
        if not username.strip():
            return False, "用户名不能为空"
            
        check_query = "SELECT id FROM users WHERE username = ?"
        existing = self.db_manager.execute_query(check_query, (username,))
        if existing:
            return False, "用户名已存在"
            
        insert_sql = "INSERT INTO users (username) VALUES (?)"
        if self.db_manager.execute_update(insert_sql, (username,)):
            user_db_path = self.app_data_dir / "user_data" / f"user_{username}.db"
            user_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            user_db = DatabaseManagerPro(str(user_db_path))
            if user_db.connect(str(user_db_path)):
                self.init_user_database(user_db)
                user_db.disconnect()
                return True, "用户添加成功"
                
        return False, "用户添加失败"
        
    def update_user(self, user_id: int, new_username: str) -> Tuple[bool, str]:
        """更新用户信息"""
        if not new_username.strip():
            return False, "用户名不能为空"
            
        check_query = "SELECT id FROM users WHERE username = ? AND id != ?"
        existing = self.db_manager.execute_query(check_query, (new_username, user_id))
        if existing:
            return False, "用户名已存在"
            
        old_user_query = "SELECT username FROM users WHERE id = ?"
        old_user = self.db_manager.execute_query(old_user_query, (user_id,))
        if not old_user:
            return False, "用户不存在"
            
        old_username = old_user[0]['username']
        
        update_sql = "UPDATE users SET username = ? WHERE id = ?"
        if self.db_manager.execute_update(update_sql, (new_username, user_id)):
            old_db_path = self.app_data_dir / "user_data" / f"user_{old_username}.db"
            new_db_path = self.app_data_dir / "user_data" / f"user_{new_username}.db"
            
            try:
                if old_db_path.exists():
                    shutil.move(str(old_db_path), str(new_db_path))
                return True, "用户更新成功"
            except Exception as e:
                if DEBUG_MODE:
                    print(f"重命名数据库文件失败: {e}")
                return False, f"更新失败: {e}"
                
        return False, "用户更新失败"
        
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """删除用户（软删除）"""
        user_query = "SELECT username FROM users WHERE id = ?"
        user = self.db_manager.execute_query(user_query, (user_id,))
        if not user:
            return False, "用户不存在"
            
        update_sql = "UPDATE users SET is_active = 0 WHERE id = ?"
        if self.db_manager.execute_update(update_sql, (user_id,)):
            return True, "用户删除成功"
            
        return False, "用户删除失败"
        
    def login_user(self, user_id: int) -> Tuple[bool, str, Optional[DatabaseManagerPro]]:
        """登录用户"""
        user_query = "SELECT * FROM users WHERE id = ? AND is_active = 1"
        user = self.db_manager.execute_query(user_query, (user_id,))
        if not user:
            return False, "用户不存在或已禁用", None
            
        user_data = user[0]
        username = user_data['username']
        
        update_sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.db_manager.execute_update(update_sql, (user_id,))
        
        user_db_path = self.app_data_dir / "user_data" / f"user_{username}.db"
        user_db = DatabaseManagerPro(str(user_db_path))
        
        if not user_db.connect(str(user_db_path)):
            return False, "无法连接用户数据库", None
            
        self.init_user_database(user_db)
        
        self.current_user = user_data
        self.current_user_db = user_db
        
        return True, "登录成功", user_db
        
    def init_user_database(self, db_manager: DatabaseManagerPro):
        """初始化用户数据库表"""
        query_history_sql = """
        CREATE TABLE IF NOT EXISTS express_query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            company_code TEXT,
            company_name TEXT,
            query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            result_data TEXT,
            quota_remaining INTEGER
        )
        """
        db_manager.execute_update(query_history_sql)
        
        express_summary_sql = """
        CREATE TABLE IF NOT EXISTS express_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            company_code TEXT,
            company_name TEXT,
            status TEXT,
            status_category TEXT,
            remark TEXT,
            screenshot TEXT,
            latest_track TEXT,
            result_data TEXT,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
        """
        db_manager.execute_update(express_summary_sql)
        
        api_accounts_sql = """
        CREATE TABLE IF NOT EXISTS api_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            auth_key TEXT,
            customer TEXT NOT NULL,
            secret TEXT,
            userid TEXT,
            smart_judge INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            daily_limit INTEGER DEFAULT 100,
            used_today INTEGER DEFAULT 0,
            last_used DATE,
            last_used_date TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sort_order INTEGER DEFAULT 0
        )
        """
        db_manager.execute_update(api_accounts_sql)
    
        # 尝试添加新字段（如果表已存在但缺少字段）
        try:
            db_manager.execute_update("ALTER TABLE api_accounts ADD COLUMN last_used_date TEXT")
        except:
            pass
        
        # 时效历史表
        delivery_history_sql = """
        CREATE TABLE IF NOT EXISTS delivery_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            company_code TEXT NOT NULL,
            company_name TEXT,
            origin_city TEXT,
            dest_city TEXT,
            pickup_time TEXT,
            sign_time TEXT,
            delivery_days INTEGER,
            route_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tracking_number, company_code)
        )
        """
        db_manager.execute_update(delivery_history_sql)
        
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_tracking_number ON express_query_history(tracking_number)",
            "CREATE INDEX IF NOT EXISTS idx_query_time ON express_query_history(query_time)",
            "CREATE INDEX IF NOT EXISTS idx_company_name ON express_query_history(company_name)",
            "CREATE INDEX IF NOT EXISTS idx_summary_tracking ON express_summary(tracking_number)",
            "CREATE INDEX IF NOT EXISTS idx_summary_category ON express_summary(status_category)",
            "CREATE INDEX IF NOT EXISTS idx_summary_update ON express_summary(last_update)",
            "CREATE INDEX IF NOT EXISTS idx_route_key ON delivery_history(route_key)",
            "CREATE INDEX IF NOT EXISTS idx_dh_company_code ON delivery_history(company_code)"
        ]
        for sql in index_sqls:
            db_manager.execute_update(sql)
            
        settings_sql = """
        CREATE TABLE IF NOT EXISTS user_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        db_manager.execute_update(settings_sql)
        
    def save_user_setting(self, key: str, value: str) -> bool:
        """保存用户设置"""
        if not self.current_user_db:
            return False
            
        sql = """
        INSERT OR REPLACE INTO user_settings (key, value, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        """
        return self.current_user_db.execute_update(sql, (key, value))
        
    def get_user_setting(self, key: str, default: str = "") -> str:
        """获取用户设置"""
        if not self.current_user_db:
            return default
            
        sql = "SELECT value FROM user_settings WHERE key = ?"
        result = self.current_user_db.execute_query(sql, (key,))
        if result:
            return result[0]['value']
        return default
        
    def save_query_history(self, tracking_number: str, company_code: str, 
                          company_name: str, status: str, result_data: str,
                          quota_remaining: int) -> bool:
        """保存查询历史"""
        if not self.current_user_db:
            return False
            
        sql = """
        INSERT INTO express_query_history 
        (tracking_number, company_code, company_name, status, result_data, quota_remaining)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.current_user_db.execute_update(
            sql, 
            (tracking_number, company_code, company_name, status, result_data, quota_remaining)
        )

class BackupManagerPro:
    """数据库备份管理器"""
    
    def __init__(self, app_data_dir: str):
        self.app_data_dir = Path(app_data_dir)
        self.backup_dir = self.app_data_dir / BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backups = MAX_BACKUP_COUNT
        
    def create_backup(self, source_db_path: str, backup_type: str = "auto", 
                     description: str = "") -> Tuple[bool, str, Optional[str]]:
        """创建数据库备份"""
        try:
            source_path = Path(source_db_path)
            if not source_path.exists():
                return False, "源数据库文件不存在", None
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{backup_type}_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(str(source_path), str(backup_path))
            
            wal_path = source_path.with_suffix('.db-wal')
            if wal_path.exists():
                wal_backup = backup_path.with_suffix('.db-wal')
                shutil.copy2(str(wal_path), str(wal_backup))
                
            metadata = {
                'backup_time': timestamp,
                'backup_type': backup_type,
                'source_file': str(source_path),
                'file_size': backup_path.stat().st_size,
                'description': description,
                'db_version': self.get_db_version(source_path)
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
            self.cleanup_old_backups(source_path.stem)
            
            return True, f"备份创建成功: {backup_name}", str(backup_path)
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"创建备份失败: {e}")
            return False, f"创建备份失败: {e}", None
            
    def restore_backup(self, backup_path: str, target_db_path: str, 
                       create_rollback: bool = True) -> Tuple[bool, str]:
        """恢复数据库备份"""
        try:
            backup_file = Path(backup_path)
            target_file = Path(target_db_path)
            
            if not backup_file.exists():
                return False, "备份文件不存在"
                
            if create_rollback and target_file.exists():
                self.create_backup(str(target_file), "rollback", "恢复前的自动备份")
                
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(str(backup_file), str(target_file))
            
            wal_backup = backup_file.with_suffix('.db-wal')
            if wal_backup.exists():
                wal_target = target_file.with_suffix('.db-wal')
                shutil.copy2(str(wal_backup), str(wal_target))
                
            return True, "数据库恢复成功"
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"恢复备份失败: {e}")
            return False, f"恢复备份失败: {e}"
            
    def get_backup_list(self, db_name: str = None) -> List[Dict]:
        """获取备份列表"""
        backups = []
        
        try:
            for file_path in self.backup_dir.glob("*.db"):
                metadata_path = file_path.with_suffix('.json')
                metadata = {}
                
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except:
                        pass
                        
                filename = file_path.stem
                parts = filename.split('_')
                
                backup_info = {
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'backup_type': metadata.get('backup_type', 'unknown'),
                    'description': metadata.get('description', ''),
                    'db_version': metadata.get('db_version', 'unknown'),
                    'metadata': metadata
                }
                
                try:
                    if len(parts) >= 3:
                        time_str = parts[-1]
                        backup_info['backup_time'] = datetime.strptime(time_str, "%Y%m%d_%H%M%S")
                    else:
                        backup_info['backup_time'] = backup_info['modified']
                except:
                    backup_info['backup_time'] = backup_info['modified']
                    
                if db_name:
                    if db_name in filename:
                        backups.append(backup_info)
                else:
                    backups.append(backup_info)
                    
            backups.sort(key=lambda x: x['backup_time'], reverse=True)
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"获取备份列表失败: {e}")
                
        return backups
        
    def cleanup_old_backups(self, db_name: str = None):
        """清理旧备份"""
        try:
            backups = self.get_backup_list(db_name)
            
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    backup_path = Path(backup['path'])
                    if backup_path.exists():
                        backup_path.unlink()
                    metadata_path = backup_path.with_suffix('.json')
                    if metadata_path.exists():
                        metadata_path.unlink()
                    wal_path = backup_path.with_suffix('.db-wal')
                    if wal_path.exists():
                        wal_path.unlink()
                        
        except Exception as e:
            if DEBUG_MODE:
                print(f"清理旧备份失败: {e}")
                
    def get_db_version(self, db_path: Path) -> str:
        """获取数据库版本信息"""
        try:
            db_manager = DatabaseManagerPro(str(db_path))
            if db_manager.connect(str(db_path)):
                result = db_manager.execute_query("PRAGMA user_version")
                if result:
                    return f"v{result[0]['user_version']}"
                db_manager.disconnect()
        except:
            pass
        return "unknown"
        
    def set_max_backups(self, count: int):
        """设置最大备份数量"""
        self.max_backups = max(1, min(100, count))
        
    def delete_backup(self, backup_path: str) -> bool:
        """删除指定备份"""
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                backup_file.unlink()
                
            metadata_file = backup_file.with_suffix('.json')
            if metadata_file.exists():
                metadata_file.unlink()
                
            wal_file = backup_file.with_suffix('.db-wal')
            if wal_file.exists():
                wal_file.unlink()
                
            return True
        except Exception as e:
            if DEBUG_MODE:
                print(f"删除备份失败: {e}")
            return False

class ExpressQueryThreadPro(QThread):
    """快递查询线程"""
    finished = Signal(dict)
    progress = Signal(int)
    
    def __init__(self, tracking_num: str, company_code: str, customer: str, key: str):
        super().__init__()
        self.tracking_num = tracking_num
        self.company_code = company_code
        self.customer = customer
        self.key = key
        
    def run(self):
        try:
            self.progress.emit(20)
            
            param = {
                'com': self.company_code,
                'num': self.tracking_num
            }
            
            self.progress.emit(40)
            
            param_str = json.dumps(param, separators=(',', ':'))
            sign_str = param_str + self.key + self.customer
            sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
            
            url = 'https://poll.kuaidi100.com/poll/query.do'
            data = {
                'customer': self.customer,
                'sign': sign,
                'param': param_str
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            self.progress.emit(60)
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            self.progress.emit(80)
            
            quota_info = self.extract_quota_info(response.headers)
            
            result = response.json()
            
            self.progress.emit(100)
            
            # ========== 修改成功判断逻辑 ==========
            # 快递100 API 返回的状态码说明：
            # 200: 查询成功，有物流轨迹
            # 0: 查询成功，但暂无物流信息（未揽件）
            # -1: 单号不存在（也可能是未揽件的情况）
            status = result.get('status', '')
            return_code = result.get('returnCode', '')
            message = result.get('message', '')
            
            # 成功的情况：
            # 1. status == '200' 或 returnCode == '200'
            # 2. 返回"暂无物流信息"、"单号不存在"等情况，说明单号有效只是还没揽件
            if status == '200' or return_code == '200':
                self.finished.emit({
                    'success': True, 
                    'data': result,
                    'quota_info': quota_info
                })
            elif message in ['暂无物流信息', '单号不存在', '暂无轨迹'] or '暂无' in message or '无物流' in message:
                # 未揽件的情况，构造一个基本的数据结构以便添加到汇总
                # 确保 data 字段存在
                if 'data' not in result:
                    result['data'] = []
                if 'state' not in result:
                    result['state'] = '0'  # 在途中/待揽件
                if 'nu' not in result:
                    result['nu'] = self.tracking_num
                if 'com' not in result:
                    result['com'] = self.company_code
                    
                self.finished.emit({
                    'success': True, 
                    'data': result,
                    'quota_info': quota_info,
                    'is_pending': True  # 标记为待揽件
                })
            elif status == '0':
                # 某些情况下 status=0 也表示暂无物流信息
                if 'data' not in result:
                    result['data'] = []
                if 'state' not in result:
                    result['state'] = '0'
                if 'nu' not in result:
                    result['nu'] = self.tracking_num
                if 'com' not in result:
                    result['com'] = self.company_code
                    
                self.finished.emit({
                    'success': True, 
                    'data': result,
                    'quota_info': quota_info,
                    'is_pending': True
                })
            else:
                # 真正的失败
                error_msg = message or '查询失败'
                self.finished.emit({
                    'success': False, 
                    'error': error_msg,
                    'quota_info': quota_info
                })
            # ========== 修改结束 ==========
            
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})
            
    def extract_quota_info(self, headers: Dict) -> Dict:
        """从响应头提取配额信息"""
        quota_info = {
            'daily_limit': 0,
            'remaining': 0,
            'reset_time': '明天0点'
        }
        
        possible_limit_fields = ['X-RateLimit-Limit', 'X-RateLimit-Request-Limit', 'X-Query-Limit']
        possible_remaining_fields = ['X-RateLimit-Remaining', 'X-RateLimit-Request-Remaining', 'X-Query-Remaining']
        possible_reset_fields = ['X-RateLimit-Reset', 'X-RateLimit-Reset-Time', 'X-Reset-Time']
        
        for field in possible_limit_fields:
            if field in headers:
                try:
                    quota_info['daily_limit'] = int(headers[field])
                except:
                    pass
                break
                
        for field in possible_remaining_fields:
            if field in headers:
                try:
                    quota_info['remaining'] = int(headers[field])
                except:
                    pass
                break
                
        for field in possible_reset_fields:
            if field in headers:
                quota_info['reset_time'] = headers[field]
                break
                
        if quota_info['daily_limit'] == 0:
            quota_info['daily_limit'] = 100
            quota_info['remaining'] = 99
            
        return quota_info

class BatchRefreshThread(QThread):
    """批量刷新快递状态线程"""
    finished = Signal(list, list)  # 修改：返回成功列表和失败列表
    progress = Signal(int, str)
    
    def __init__(self, tracking_list: List[Dict], customer: str, key: str):
        super().__init__()
        self.tracking_list = tracking_list
        self.customer = customer
        self.key = key
        
    def run(self):
        success_results = []
        failed_items = []
        total = len(self.tracking_list)
        
        for i, item in enumerate(self.tracking_list):
            tracking_num = item['tracking_number']
            company_code = item.get('company_code', '')
            
            self.progress.emit(int((i / total) * 100), f"正在刷新: {tracking_num}")
            
            try:
                param = {'com': company_code, 'num': tracking_num}
                param_str = json.dumps(param, separators=(',', ':'))
                sign_str = param_str + self.key + self.customer
                sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
                
                url = 'https://poll.kuaidi100.com/poll/query.do'
                data = {'customer': self.customer, 'sign': sign, 'param': param_str}
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                
                response = requests.post(url, data=data, headers=headers, timeout=10)
                result = response.json()
                
                if result.get('status') == '200' or result.get('returnCode') == '200':
                    success_results.append({
                        'tracking_number': tracking_num,
                        'success': True,
                        'data': result
                    })
                else:
                    failed_items.append({
                        'tracking_number': tracking_num,
                        'company_code': company_code,
                        'success': False,
                        'error': result.get('message', '查询失败')
                    })
            except Exception as e:
                failed_items.append({
                    'tracking_number': tracking_num,
                    'company_code': company_code,
                    'success': False,
                    'error': str(e)
                })
                
            time.sleep(0.5)
            
        self.progress.emit(100, "刷新完成")
        self.finished.emit(success_results, failed_items)

class BackupWorkerPro(QThread):
    """备份工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    
    def __init__(self, backup_manager: BackupManagerPro, source_db: str, 
                 backup_type: str = "auto"):
        super().__init__()
        self.backup_manager = backup_manager
        self.source_db = source_db
        self.backup_type = backup_type
        
    def run(self):
        try:
            self.progress.emit(30)
            success, message, path = self.backup_manager.create_backup(
                self.source_db, self.backup_type
            )
            self.progress.emit(100)
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"备份失败: {e}")

class RestoreWorkerPro(QThread):
    """恢复工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    
    def __init__(self, backup_manager: BackupManagerPro, backup_path: str, 
                 target_db: str):
        super().__init__()
        self.backup_manager = backup_manager
        self.backup_path = backup_path
        self.target_db = target_db
        
    def run(self):
        try:
            self.progress.emit(50)
            success, message = self.backup_manager.restore_backup(
                self.backup_path, self.target_db, True
            )
            self.progress.emit(100)
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"恢复失败: {e}")

class ImageViewerDialog(QDialog):
    """图片查看器对话框"""
    
    def __init__(self, image_data: str, tracking_num: str, parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.tracking_num = tracking_num
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle(f"截图查看 - {self.tracking_num}")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        if self.image_data:
            try:
                image_bytes = base64.b64decode(self.image_data)
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                
                scaled_pixmap = pixmap.scaled(
                    550, 450, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            except:
                self.image_label.setText("无法加载图片")
                
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

class ExpressItemWidget(QWidget):
    """快递条目组件"""
    
    remark_changed = Signal(int, str)
    screenshot_changed = Signal(int, str)
    refresh_requested = Signal(str, str)
    view_details_requested = Signal(dict)
    delete_requested = Signal(int)
    
    def __init__(self, express_data: Dict, parent=None, parent_gui=None):
        super().__init__(parent)
        self.express_data = express_data
        self.express_id = express_data.get('id', 0)
        self.parent_gui = parent_gui  # 保存主窗口引用
        self.init_ui()
        self.update_display()
        self.apply_item_style()
        
    def apply_item_style(self):
        """应用条目样式"""
        # 根据状态设置不同的背景色
        category = self.express_data.get('status_category', 'other')
        state = self.express_data.get('status', '')
        
        # 根据分类设置不同的边框颜色
        category_colors = {
            'signed': MacaronColors.GREEN_MINT,
            'arrived': MacaronColors.ORANGE_PEACH,
            'delivering': MacaronColors.BLUE_SKY,
            'transit': MacaronColors.PURPLE_LAVENDER,
            'problem': MacaronColors.RED_CORAL,
            'returned': MacaronColors.NEUTRAL_MOCHA,
            'customs': MacaronColors.YELLOW_LEMON,
            'picked': MacaronColors.GREEN_APPLE,
            'pending': MacaronColors.PINK_COTTON,
            'other': MacaronColors.NEUTRAL_CREAM
        }
        
        border_color = category_colors.get(category, MacaronColors.BORDER_LIGHT)
        
        self.setStyleSheet(f"""
            ExpressItemWidget {{
                background-color: white;
                border: 1px solid {border_color.name()};
                border-radius: 10px;
                padding: 5px;
            }}
            ExpressItemWidget:hover {{
                background-color: {MacaronColors.BG_HOVER.name()};
                border-width: 2px;
            }}
        """)
        
    def init_ui(self):
        """初始化UI"""
        self.setMinimumHeight(120)
        self.setMaximumHeight(200)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        self.image_btn = QPushButton()
        self.image_btn.setFixedSize(100, 100)
        self.image_btn.clicked.connect(self.on_image_click)
        self.image_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px dashed {MacaronColors.BORDER_LIGHT.name()};
                border-radius: 8px;
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
            }}
            QPushButton:hover {{
                border-color: {MacaronColors.BLUE_SKY.name()};
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        main_layout.addWidget(self.image_btn)
        
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.setContentsMargins(0, 0, 0, 0)
    
        # 第一行：状态标签（快递单号等）
        self.status_label = QLabel()
        self.status_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.status_label.customContextMenuRequested.connect(self.show_status_context_menu)
        font = QFont()
        font.setBold(True)
        self.status_label.setFont(font)
        info_layout.addWidget(self.status_label)
        
        # 第二行：备注按钮
        self.remark_btn = QPushButton()
        self.remark_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.remark_btn.customContextMenuRequested.connect(self.show_remark_context_menu)
        self.remark_btn.clicked.connect(self.on_remark_click)
        self.remark_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 3px 8px;
                background-color: transparent;
                color: {MacaronColors.TEXT_MEDIUM.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.YELLOW_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        info_layout.addWidget(self.remark_btn)
        
        # 第三行：物流轨迹按钮
        self.track_btn = QPushButton()
        self.track_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.track_btn.customContextMenuRequested.connect(self.show_track_context_menu)
        self.track_btn.clicked.connect(self.on_track_click)
        self.track_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 3px 8px;
                background-color: transparent;
                color: {MacaronColors.TEXT_MEDIUM.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        info_layout.addWidget(self.track_btn)
        
        info_widget.setLayout(info_layout)
        main_layout.addWidget(info_widget, 1)
        
        btn_widget = QWidget()
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(5)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.setToolTip("刷新状态")
        refresh_btn.setFixedSize(50, 30)
        refresh_btn.clicked.connect(self.on_refresh_click)
        btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.setToolTip("删除")
        delete_btn.setFixedSize(50, 30)
        delete_btn.clicked.connect(self.on_delete_click)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        btn_widget.setLayout(btn_layout)
        main_layout.addWidget(btn_widget)
        
        self.setLayout(main_layout)

    def show_status_context_menu(self, pos):
        """显示状态标签的右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(MacaronStyle.get_main_style())
        
        tracking_num = self.express_data.get('tracking_number', '')
        company_name = self.express_data.get('company_name', '')
        status = self.express_data.get('status', '')
        
        # 复制快递单号
        copy_num_action = menu.addAction(f"📋 复制单号: {tracking_num}")
        copy_num_action.triggered.connect(lambda: self.copy_to_clipboard(tracking_num, "快递单号"))
        
        # 复制快递公司
        copy_company_action = menu.addAction(f"🏢 复制公司: {company_name}")
        copy_company_action.triggered.connect(lambda: self.copy_to_clipboard(company_name, "快递公司"))
        
        # 复制状态
        copy_status_action = menu.addAction(f"📊 复制状态: {status}")
        copy_status_action.triggered.connect(lambda: self.copy_to_clipboard(status, "状态"))
        
        menu.addSeparator()
        
        # 复制完整信息
        copy_all_action = menu.addAction("📝 复制完整信息")
        copy_all_action.triggered.connect(self.copy_full_info)
        
        menu.exec(self.status_label.mapToGlobal(pos))

    def show_remark_context_menu(self, pos):
        """显示备注按钮的右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(MacaronStyle.get_main_style())
        
        remark = self.express_data.get('remark', '')
        tracking_num = self.express_data.get('tracking_number', '')
        
        if remark:
            copy_action = menu.addAction(f"📋 复制备注: {remark[:30]}{'...' if len(remark) > 30 else ''}")
            copy_action.triggered.connect(lambda: self.copy_to_clipboard(remark, "备注"))
        else:
            menu.addAction("📋 暂无备注").setEnabled(False)
        
        menu.addSeparator()
        
        # 快捷备注
        quick_menu = menu.addMenu("⚡ 快捷备注")
        quick_items = ["衣服", "鞋子", "电子产品", "食品", "日用品", "书籍", "已签收", "待取件"]
        for item in quick_items:
            action = quick_menu.addAction(item)
            action.triggered.connect(lambda checked, t=item: self.add_quick_remark_direct(t))
        
        edit_action = menu.addAction("✏️ 编辑备注")
        edit_action.triggered.connect(self.on_remark_click)
        
        menu.exec(self.remark_btn.mapToGlobal(pos))

    def show_track_context_menu(self, pos):
        """显示物流轨迹按钮的右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(MacaronStyle.get_main_style())
        
        latest_track = self.express_data.get('latest_track', '')
        tracking_num = self.express_data.get('tracking_number', '')
        
        if latest_track:
            copy_action = menu.addAction(f"📋 复制物流信息")
            copy_action.triggered.connect(lambda: self.copy_to_clipboard(latest_track, "物流信息"))
        else:
            menu.addAction("📋 暂无物流信息").setEnabled(False)
        
        menu.addSeparator()
        
        # 查看详情
        view_action = menu.addAction("🔍 查看完整轨迹")
        view_action.triggered.connect(self.on_track_click)
        
        # 刷新
        refresh_action = menu.addAction("🔄 刷新")
        refresh_action.triggered.connect(self.on_refresh_click)
        
        # 在浏览器中搜索
        search_action = menu.addAction("🌐 在网上搜索此单号")
        search_action.triggered.connect(self.search_online)
        
        menu.exec(self.track_btn.mapToGlobal(pos))

    def copy_to_clipboard(self, text: str, item_name: str = ""):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        if item_name:
            QMessageBox.information(self, "复制成功", f"{item_name}已复制到剪贴板")
        else:
            QMessageBox.information(self, "复制成功", "已复制到剪贴板")

    def copy_full_info(self):
        """复制完整信息"""
        tracking_num = self.express_data.get('tracking_number', '')
        company_name = self.express_data.get('company_name', '')
        status = self.express_data.get('status', '')
        remark = self.express_data.get('remark', '')
        latest_track = self.express_data.get('latest_track', '')
        last_update = self.express_data.get('last_update', '')
        
        full_info = f"""快递单号: {tracking_num}
    快递公司: {company_name}
    当前状态: {status}
    备注: {remark if remark else '无'}
    最新物流: {latest_track if latest_track else '暂无'}
    最后更新: {last_update}"""
        
        clipboard = QApplication.clipboard()
        clipboard.setText(full_info)
        QMessageBox.information(self, "复制成功", "完整快递信息已复制到剪贴板")

    def add_quick_remark_direct(self, text: str):
        """直接添加快捷备注"""
        current_remark = self.express_data.get('remark', '')
        if current_remark:
            new_remark = f"{current_remark}、{text}"
        else:
            new_remark = text
        
        self.remark_changed.emit(self.express_id, new_remark)
        self.express_data['remark'] = new_remark
        self.update_display()
        QMessageBox.information(self, "成功", f"已添加备注: {text}")

    def search_online(self):
        """在网上搜索快递单号"""
        import webbrowser
        tracking_num = self.express_data.get('tracking_number', '')
        if tracking_num:
            # 使用快递100搜索
            url = f"https://www.kuaidi100.com/all/{tracking_num}.shtml"
            webbrowser.open(url)
        
    def update_display(self):
        """更新显示"""
        status_text = self.express_data.get('status', '未知')
        tracking_num = self.express_data.get('tracking_number', '')
        company = self.express_data.get('company_name', '')
        last_update = self.express_data.get('last_update', '')
        created_at = self.express_data.get('created_at', '')
        
        created_display = ""
        if created_at:
            try:
                if ' ' in created_at:
                    create_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                else:
                    create_time = datetime.strptime(created_at, '%Y-%m-%d')
                created_display = f" | 添加: {create_time.strftime('%m-%d %H:%M')}"
            except:
                created_display = f" | 添加: {created_at}"
        
        update_display = ""
        if last_update:
            try:
                if ' ' in last_update:
                    update_time = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
                else:
                    update_time = datetime.strptime(last_update, '%Y-%m-%d')
                update_display = f" | 更新: {update_time.strftime('%m-%d %H:%M')}"
            except:
                update_display = f" | 更新: {last_update}"
    
        # 获取预估时间
        estimated_display = ""
        if hasattr(self, 'parent_gui') and self.parent_gui and self.parent_gui.delivery_estimator:
            result_data = self.express_data.get('result_data', '')
            if result_data:
                try:
                    full_data = json.loads(result_data)
                    state = str(full_data.get('state', ''))
                    if state != '3':  # 非签收状态才显示预估
                        estimated_text = self.parent_gui.delivery_estimator.get_estimate_text(full_data)
                        if estimated_text and estimated_text != "暂无预估信息":
                            # 简化显示
                            if '预计' in estimated_text:
                                # 提取日期部分
                                import re
                                match = re.search(r'预计(\d+月\d+日)送达', estimated_text)
                                if match:
                                    estimated_display = f" | {match.group(0)}"
                                else:
                                    estimated_display = f" | {estimated_text[:20]}"
                            elif '派件中' in estimated_text:
                                estimated_display = " | 派件中"
                            elif '已到达' in estimated_text:
                                estimated_display = " | 待取件"
                except:
                    pass

        self.status_label.setText(f"快递单号: {tracking_num} | {company} | {status_text}{created_display}{update_display}{estimated_display}")
        
        remark = self.express_data.get('remark', '')
        if remark:
            self.remark_btn.setText(f"备注: {remark}")
        else:
            self.remark_btn.setText("点击添加备注...")
            
        latest_track = self.express_data.get('latest_track', '')
        if latest_track:
            display_track = latest_track[:60] + "..." if len(latest_track) > 60 else latest_track
            self.track_btn.setText(f"最新: {display_track}")
        else:
            self.track_btn.setText("暂无物流信息")
            
        screenshot = self.express_data.get('screenshot', '')
        if screenshot:
            try:
                image_bytes = base64.b64decode(screenshot)
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                scaled_pixmap = pixmap.scaled(
                    90, 90, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_btn.setIcon(QIcon(scaled_pixmap))
                self.image_btn.setIconSize(QSize(90, 90))
                self.image_btn.setText("")
                self.image_btn.setStyleSheet(f"""
                    QPushButton {{
                        border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                        border-radius: 8px;
                        background-color: white;
                        padding: 2px;
                    }}
                    QPushButton:hover {{
                        border-color: {MacaronColors.BLUE_SKY.name()};
                    }}
                """)
            except:
                self.image_btn.setText("截图")
        else:
            self.image_btn.setText("添加截图")
            
        self.apply_item_style()
            
    def on_image_click(self):
        """点击图片 - 显示右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(MacaronStyle.get_main_style())
        
        # 查看大图（仅当有截图时可用）
        view_action = menu.addAction("🔍 查看大图")
        view_action.setIcon(QIcon.fromTheme("zoom-in"))
        if not self.express_data.get('screenshot'):
            view_action.setEnabled(False)
        
        menu.addSeparator()
        
        # 添加截图子菜单
        add_menu = menu.addMenu("➕ 添加截图")
        add_menu.setIcon(QIcon.fromTheme("list-add"))
        
        # 从文件选择
        from_file_action = add_menu.addAction("📁 从文件选择...")
        from_file_action.triggered.connect(self.add_screenshot_from_file)
        
        # 从剪贴板粘贴
        from_clipboard_action = add_menu.addAction("📋 从剪贴板粘贴")
        from_clipboard_action.triggered.connect(self.add_screenshot_from_clipboard)
        
        # 从URL下载（新增功能）
        from_url_action = add_menu.addAction("🌐 从URL下载...")
        from_url_action.triggered.connect(self.add_screenshot_from_url)
        
        menu.addSeparator()
        
        # 编辑截图子菜单（仅当有截图时可用）
        edit_menu = menu.addMenu("✏️ 编辑截图")
        edit_menu.setIcon(QIcon.fromTheme("edit"))
        if not self.express_data.get('screenshot'):
            edit_menu.setEnabled(False)
        
        # 旋转图片
        rotate_menu = edit_menu.addMenu("🔄 旋转")
        rotate_left_action = rotate_menu.addAction("↪️ 向左旋转90°")
        rotate_left_action.triggered.connect(lambda: self.rotate_screenshot(-90))
        rotate_right_action = rotate_menu.addAction("↩️ 向右旋转90°")
        rotate_right_action.triggered.connect(lambda: self.rotate_screenshot(90))
        rotate_180_action = rotate_menu.addAction("🔃 旋转180°")
        rotate_180_action.triggered.connect(lambda: self.rotate_screenshot(180))
        
        # 裁剪图片
        crop_action = edit_menu.addAction("✂️ 裁剪...")
        crop_action.triggered.connect(self.crop_screenshot)
        
        menu.addSeparator()
        
        # 导出截图
        export_menu = menu.addMenu("💾 导出截图")
        export_menu.setIcon(QIcon.fromTheme("document-save"))
        if not self.express_data.get('screenshot'):
            export_menu.setEnabled(False)
        
        export_original_action = export_menu.addAction("📷 导出原图...")
        export_original_action.triggered.connect(lambda: self.export_screenshot(False))
        export_with_info_action = export_menu.addAction("📄 导出带信息...")
        export_with_info_action.triggered.connect(lambda: self.export_screenshot(True))
        
        # 复制到剪贴板
        copy_action = menu.addAction("📋 复制到剪贴板")
        copy_action.setIcon(QIcon.fromTheme("edit-copy"))
        if not self.express_data.get('screenshot'):
            copy_action.setEnabled(False)
        copy_action.triggered.connect(self.copy_screenshot_to_clipboard)
        
        menu.addSeparator()
        
        # 删除截图
        delete_action = menu.addAction("🗑️ 删除截图")
        delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        if not self.express_data.get('screenshot'):
            delete_action.setEnabled(False)
        delete_action.triggered.connect(self.delete_screenshot)
        
        menu.addSeparator()
        
        # 截图信息
        info_action = menu.addAction("ℹ️ 截图信息")
        info_action.triggered.connect(self.show_screenshot_info)
        
        # 显示菜单
        action = menu.exec(QCursor.pos())
        
        # 处理查看大图（因为需要特殊处理）
        if action == view_action:
            if self.express_data.get('screenshot'):
                dialog = ImageViewerDialog(
                    self.express_data['screenshot'],
                    self.express_data.get('tracking_number', ''),
                    self
                )
                dialog.exec()
    
    def add_screenshot_from_url(self):
        """从URL下载截图"""
        from PySide6.QtWidgets import QInputDialog
        
        url, ok = QInputDialog.getText(
            self, "从URL下载", 
            "请输入图片URL地址：",
            QLineEdit.Normal,
            "https://"
        )
        
        if not ok or not url.strip():
            return
        
        # 显示进度提示
        progress_dialog = QProgressDialog("正在下载图片...", "取消", 0, 0, self)
        progress_dialog.setWindowTitle("下载中")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        # 使用线程下载
        class DownloadThread(QThread):
            finished = Signal(bool, str, str)  # success, image_data, error_msg
            
            def __init__(self, url):
                super().__init__()
                self.url = url
            
            def run(self):
                try:
                    response = requests.get(self.url, timeout=30, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type or self.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                            image_data = base64.b64encode(response.content).decode('utf-8')
                            self.finished.emit(True, image_data, "")
                        else:
                            self.finished.emit(False, "", "URL返回的不是图片格式")
                    else:
                        self.finished.emit(False, "", f"下载失败：HTTP {response.status_code}")
                except requests.exceptions.Timeout:
                    self.finished.emit(False, "", "下载超时，请检查网络连接")
                except requests.exceptions.ConnectionError:
                    self.finished.emit(False, "", "网络连接失败，请检查网络")
                except Exception as e:
                    self.finished.emit(False, "", f"下载失败：{str(e)}")
        
        self.download_thread = DownloadThread(url.strip())
        
        def on_download_finished(success, image_data, error_msg):
            progress_dialog.close()
            if success:
                # 验证图片是否有效
                try:
                    image_bytes = base64.b64decode(image_data)
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_bytes):
                        self.screenshot_changed.emit(self.express_id, image_data)
                        self.express_data['screenshot'] = image_data
                        self.update_display()
                        QMessageBox.information(self, "成功", "图片已成功下载并添加")
                    else:
                        QMessageBox.warning(self, "错误", "下载的文件不是有效的图片格式")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"图片处理失败：{str(e)}")
            else:
                QMessageBox.warning(self, "下载失败", error_msg)
        
        self.download_thread.finished.connect(on_download_finished)
        self.download_thread.start()
        
        # 如果用户取消
        if progress_dialog.wasCanceled():
            if self.download_thread.isRunning():
                self.download_thread.terminate()
                self.download_thread.wait()
    
    def rotate_screenshot(self, angle: int):
        """旋转截图"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            QMessageBox.warning(self, "提示", "没有可旋转的截图")
            return
        
        try:
            # 解码图片
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            # 旋转图片
            transform = QTransform().rotate(angle)
            rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
            
            # 保存旋转后的图片
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            rotated_pixmap.save(buffer, "PNG")
            
            new_image_data = base64.b64encode(byte_array.data()).decode('utf-8')
            
            # 更新
            self.screenshot_changed.emit(self.express_id, new_image_data)
            self.express_data['screenshot'] = new_image_data
            self.update_display()
            
            QMessageBox.information(self, "成功", f"图片已旋转 {angle}°")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"旋转图片失败：{str(e)}")
    
    def crop_screenshot(self):
        """裁剪截图"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            QMessageBox.warning(self, "提示", "没有可裁剪的截图")
            return
        
        try:
            # 解码图片
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            # 创建裁剪对话框
            dialog = CropImageDialog(pixmap, self)
            if dialog.exec() == QDialog.Accepted:
                cropped_pixmap = dialog.get_cropped_image()
                if cropped_pixmap:
                    # 保存裁剪后的图片
                    byte_array = QByteArray()
                    buffer = QBuffer(byte_array)
                    buffer.open(QIODevice.WriteOnly)
                    cropped_pixmap.save(buffer, "PNG")
                    
                    new_image_data = base64.b64encode(byte_array.data()).decode('utf-8')
                    
                    # 更新
                    self.screenshot_changed.emit(self.express_id, new_image_data)
                    self.express_data['screenshot'] = new_image_data
                    self.update_display()
                    
                    QMessageBox.information(self, "成功", "图片已裁剪")
                    
        except Exception as e:
            QMessageBox.warning(self, "错误", f"裁剪图片失败：{str(e)}")
    
    def export_screenshot(self, include_info: bool = False):
        """导出截图"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            return
        
        tracking_num = self.express_data.get('tracking_number', 'unknown')
        
        # 选择保存路径
        default_name = f"{tracking_num}_screenshot"
        if include_info:
            default_name += "_with_info"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存截图", 
            f"{default_name}.png",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            if include_info:
                # 创建带信息的图片
                info_pixmap = self.create_screenshot_with_info(pixmap)
                info_pixmap.save(file_path)
            else:
                pixmap.save(file_path)
            
            QMessageBox.information(self, "成功", f"截图已保存到：\n{file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存截图失败：{str(e)}")
    
    def create_screenshot_with_info(self, original_pixmap: QPixmap) -> QPixmap:
        """创建带信息的截图"""
        tracking_num = self.express_data.get('tracking_number', '')
        company_name = self.express_data.get('company_name', '')
        status = self.express_data.get('status', '')
        remark = self.express_data.get('remark', '')
        last_update = self.express_data.get('last_update', '')
        
        # 计算新图片尺寸
        info_height = 120
        new_width = max(original_pixmap.width(), 400)
        new_height = original_pixmap.height() + info_height
        
        # 创建新画布
        result_pixmap = QPixmap(new_width, new_height)
        result_pixmap.fill(Qt.white)
        
        # 绘制
        painter = QPainter(result_pixmap)
        
        # 绘制信息区域背景
        painter.fillRect(0, 0, new_width, info_height, QColor(240, 248, 255))
        
        # 绘制边框
        painter.setPen(QColor(200, 200, 200))
        painter.drawRect(0, 0, new_width - 1, info_height - 1)
        
        # 绘制文字信息
        painter.setPen(Qt.black)
        font = QFont("Microsoft YaHei", 10)
        painter.setFont(font)
        
        y = 20
        painter.drawText(10, y, f"快递单号: {tracking_num}")
        y += 20
        painter.drawText(10, y, f"快递公司: {company_name}")
        y += 20
        painter.drawText(10, y, f"当前状态: {status}")
        y += 20
        if remark:
            painter.drawText(10, y, f"备注: {remark[:30]}{'...' if len(remark) > 30 else ''}")
            y += 20
        painter.drawText(10, y, f"最后更新: {last_update}")
        
        # 绘制原图
        painter.drawPixmap(0, info_height, original_pixmap)
        
        painter.end()
        
        return result_pixmap
    
    def copy_screenshot_to_clipboard(self):
        """复制截图到剪贴板"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            QMessageBox.warning(self, "提示", "没有可复制的截图")
            return
        
        try:
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            QMessageBox.information(self, "成功", "截图已复制到剪贴板")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"复制截图失败：{str(e)}")
    
    def delete_screenshot(self):
        """删除截图"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除此截图吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.screenshot_changed.emit(self.express_id, "")
            self.express_data['screenshot'] = ""
            self.update_display()
            QMessageBox.information(self, "成功", "截图已删除")
    
    def show_screenshot_info(self):
        """显示截图信息"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            QMessageBox.information(self, "截图信息", "暂无截图")
            return
        
        try:
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            # 计算文件大小
            size_kb = len(image_bytes) / 1024
            
            info_text = f"""
截图信息：
━━━━━━━━━━━━━━━━━━━━
图片尺寸: {pixmap.width()} x {pixmap.height()} 像素
文件大小: {size_kb:.2f} KB
图片格式: PNG
是否有效: {'是' if not pixmap.isNull() else '否'}
━━━━━━━━━━━━━━━━━━━━
关联单号: {self.express_data.get('tracking_number', '')}
            """
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("截图信息")
            msg_box.setText(info_text)
            msg_box.setIcon(QMessageBox.Information)
            
            # 添加预览按钮
            preview_btn = msg_box.addButton("预览", QMessageBox.ActionRole)
            msg_box.addButton(QMessageBox.Ok)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == preview_btn:
                dialog = ImageViewerDialog(
                    screenshot,
                    self.express_data.get('tracking_number', ''),
                    self
                )
                dialog.exec()
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取截图信息失败：{str(e)}")
    

            
    def add_screenshot_from_file(self):
        """从文件添加截图"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择截图", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    
                self.screenshot_changed.emit(self.express_id, image_data)
                self.express_data['screenshot'] = image_data
                self.update_display()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载图片失败: {e}")
                
    def add_screenshot_from_clipboard(self):
        """从剪贴板添加截图"""
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        
        if pixmap.isNull():
            mime_data = clipboard.mimeData()
            if mime_data.hasImage():
                image = QImage(mime_data.imageData())
                pixmap = QPixmap.fromImage(image)
        
        if pixmap.isNull():
            QMessageBox.warning(self, "提示", "剪贴板中没有图片！")
            return
            
        try:
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, "PNG")
            
            image_data = base64.b64encode(byte_array.data()).decode('utf-8')
            
            self.screenshot_changed.emit(self.express_id, image_data)
            self.express_data['screenshot'] = image_data
            self.update_display()
            QMessageBox.information(self, "成功", "截图已从剪贴板添加")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"处理剪贴板图片失败: {e}")
                
    def on_remark_click(self):
        """点击备注"""
        dialog = RemarkEditDialog(
            self.express_data.get('tracking_number', ''),
            self.express_data.get('remark', ''),
            self
        )
        
        if dialog.exec() == QDialog.Accepted:
            new_remark = dialog.get_remark()
            self.remark_changed.emit(self.express_id, new_remark)
            self.express_data['remark'] = new_remark
            self.update_display()
            
    def on_track_click(self):
        """点击物流轨迹"""
        self.view_details_requested.emit(self.express_data)
        
    def on_refresh_click(self):
        """点击刷新"""
        self.refresh_requested.emit(
            self.express_data.get('tracking_number', ''),
            self.express_data.get('company_code', '')
        )
        
    def on_delete_click(self):
        """点击删除"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除快递 {self.express_data.get('tracking_number', '')} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_requested.emit(self.express_id)

class RemarkEditDialog(QDialog):
    """备注编辑对话框"""
    
    def __init__(self, tracking_num: str, current_remark: str, parent=None):
        super().__init__(parent)
        self.tracking_num = tracking_num
        self.current_remark = current_remark
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle(f"编辑备注 - {self.tracking_num}")
        self.setMinimumSize(400, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("请输入备注信息（如：购买的商品名称等）："))
        
        self.remark_edit = QTextEdit()
        self.remark_edit.setText(self.current_remark)
        self.remark_edit.setPlaceholderText("例如：iPhone 15手机壳、运动鞋...")
        layout.addWidget(self.remark_edit)
        
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("快捷备注:"))
        
        quick_items = ["衣服", "鞋子", "电子产品", "食品", "日用品", "书籍"]
        for item in quick_items:
            btn = QPushButton(item)
            btn.clicked.connect(lambda checked, t=item: self.add_quick_remark(t))
            quick_layout.addWidget(btn)
            
        quick_layout.addStretch()
        layout.addLayout(quick_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # 设置快捷键：Ctrl+Enter 保存
        save_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        save_shortcut.activated.connect(self.accept)
        
    def add_quick_remark(self, text: str):
        """添加快捷备注"""
        current = self.remark_edit.toPlainText()
        if current:
            self.remark_edit.setText(f"{current}、{text}")
        else:
            self.remark_edit.setText(text)
            
    def get_remark(self) -> str:
        """获取备注"""
        return self.remark_edit.toPlainText().strip()

class ExpressDetailDialog(QDialog):
    """快递详情对话框"""
    
    def __init__(self, express_id: int, tracking_num: str, parent_gui, parent=None):
        super().__init__(parent)
        self.express_id = express_id
        self.tracking_num = tracking_num
        self.parent_gui = parent_gui
        self.express_data = None
        self.query_thread = None
        self.estimator = DeliveryTimeEstimator(parent_gui.current_user_db) if parent_gui and parent_gui.current_user_db else None
        self.init_ui()
        self.load_data()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{ProjectInfo.NAME} - 快递详情 - {self.tracking_num}")
        self.setMinimumSize(750, 550)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.info_group = QGroupBox("基本信息")
        self.info_layout = QGridLayout()
        self.info_group.setLayout(self.info_layout)
        layout.addWidget(self.info_group)
        
        self.remark_group = QGroupBox("备注")
        self.remark_layout = QVBoxLayout()
        self.remark_label = QLabel()
        self.remark_label.setWordWrap(True)
        self.remark_layout.addWidget(self.remark_label)
        self.remark_group.setLayout(self.remark_layout)
        layout.addWidget(self.remark_group)
        
        self.track_group = QGroupBox("物流轨迹")
        self.track_layout = QVBoxLayout()
        self.track_text = QTextEdit()
        self.track_text.setReadOnly(True)
        self.track_layout.addWidget(self.track_text)
        self.track_group.setLayout(self.track_layout)
        layout.addWidget(self.track_group)
        
        btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新 (F5)")
        self.refresh_btn.setToolTip("刷新快递信息（调用API查询最新状态）")
        self.refresh_btn.clicked.connect(self.refresh_data)
        btn_layout.addWidget(self.refresh_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭 (Esc)")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # 设置快捷键
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        close_shortcut = QShortcut(QKeySequence("Esc"), self)
        close_shortcut.activated.connect(self.accept)
        
    def refresh_data(self):
        """刷新数据 - 主动查询API"""
        if not self.parent_gui:
            return
            
        tracking_num = self.express_data.get('tracking_number', '') if self.express_data else self.tracking_num
        company_code = self.express_data.get('company_code', '') if self.express_data else ''
        
        if not tracking_num:
            QMessageBox.warning(self, "提示", "无法获取快递单号")
            return
            
        if not self.parent_gui.customer or not self.parent_gui.key:
            reply = QMessageBox.question(
                self, "提示",
                "未配置API账号，无法查询快递。是否现在添加账号？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.parent_gui.show_settings()
            return
        
        # 检查当前账号是否可用
        if self.parent_gui.api_account_manager:
            self.parent_gui.api_account_manager.check_and_reset_daily_usage()
            
            if not self.parent_gui.api_account_manager.is_current_account_available():
                # 尝试切换到下一个账号（正常切换，不强制）
                if self.parent_gui.api_account_manager.switch_to_next_account(force_switch=False):
                    self.parent_gui.load_current_api_account()
                    usage_info = self.parent_gui.api_account_manager.get_usage_info()
                    QMessageBox.information(self, "提示", 
                        f"当前账号额度已用完，已自动切换到备用账号\n"
                        f"新账号今日剩余次数：{usage_info['remaining']}/{usage_info['limit']}")
                else:
                    QMessageBox.warning(self, "提示", "所有账号今日额度都已用完，请明天再试")
                    return
            
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("刷新中...")
        
        self.query_thread = ExpressQueryThreadPro(
            tracking_num, company_code,
            self.parent_gui.customer, self.parent_gui.key
        )
        self.query_thread.finished.connect(self.on_refresh_finished)
        self.query_thread.start()
        if hasattr(self.parent_gui, 'query_threads'):
            self.parent_gui.query_threads.append(self.query_thread)
        
    def on_refresh_finished(self, result: dict):
        """刷新完成"""
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("刷新")
        
        if result.get('success'):
            if hasattr(self.parent_gui, 'update_express_summary'):
                self.parent_gui.update_express_summary(result['data'])
            self.load_data()
            QMessageBox.information(self, "成功", "快递信息已更新")
        else:
            error_msg = result.get('error', '未知错误')
            
            if self.parent_gui.api_account_manager:
                # 尝试切换到下一个账号（强制切换）
                if self.parent_gui.api_account_manager.switch_to_next_account(force_switch=True):
                    self.parent_gui.load_current_api_account()
                    
                    reply = QMessageBox.question(
                        self, "刷新失败",
                        f"刷新失败：{error_msg}\n\n"
                        f"已自动切换到备用账号，是否重试？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.refresh_data()
                        return
                    else:
                        QMessageBox.critical(self, "刷新失败", f"错误信息：{error_msg}")
                else:
                    QMessageBox.critical(self, "刷新失败", f"错误信息：{error_msg}\n\n无备用账号可切换")
            else:
                QMessageBox.critical(self, "刷新失败", f"错误信息：{error_msg}")
        
    def load_data(self):
        """从数据库加载最新数据"""
        if self.parent_gui and self.parent_gui.user_manager.current_user_db:
            sql = "SELECT * FROM express_summary WHERE id = ? AND is_deleted = 0"
            result = self.parent_gui.user_manager.current_user_db.execute_query(sql, (self.express_id,))
            if result:
                self.express_data = result[0]
                self.update_display()
                
    def update_display(self):
        """更新显示内容"""
        if not self.express_data:
            return
            
        self.setWindowTitle(f"快递详情 - {self.express_data.get('tracking_number', '')}")
        
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        tracking_num = self.express_data.get('tracking_number', '')
        company_name = self.express_data.get('company_name', '')
        status = self.express_data.get('status', '')
        
        # 解析完整物流数据用于预估
        result_data = self.express_data.get('result_data', '')
        full_data = {}
        if result_data:
            try:
                full_data = json.loads(result_data)
            except:
                pass
        
        # 获取预估时间
        estimated_text = "暂无预估信息"
        if self.estimator and full_data:
            estimated_text = self.estimator.get_estimate_text(full_data)
    
        created_at = self.express_data.get('created_at', '')
        created_display = created_at
        if created_at:
            try:
                if ' ' in created_at:
                    create_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                else:
                    create_time = datetime.strptime(created_at, '%Y-%m-%d')
                created_display = create_time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        last_update = self.express_data.get('last_update', '')
        update_display = last_update
        if last_update:
            try:
                if ' ' in last_update:
                    update_time = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
                else:
                    update_time = datetime.strptime(last_update, '%Y-%m-%d')
                update_display = update_time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        info_items = [
            ("快递单号:", tracking_num),
            ("快递公司:", company_name),
            ("当前状态:", status),
            ("预计送达:", estimated_text),
            ("添加时间:", created_display),
            ("最后更新:", update_display),
        ]
        
        for i, (field, value) in enumerate(info_items):
            field_label = QLabel(field)
            field_label.setStyleSheet("font-weight: bold;")
            self.info_layout.addWidget(field_label, i, 0)
            
            value_label = QLabel(str(value))
            self.info_layout.addWidget(value_label, i, 1)
        
        remark = self.express_data.get('remark', '')
        if remark:
            self.remark_label.setText(remark)
            self.remark_label.setStyleSheet("")
        else:
            self.remark_label.setText("无备注")
            self.remark_label.setStyleSheet("color: #999; font-style: italic;")
        
        self.track_text.clear()
        if result_data:
            try:
                data = json.loads(result_data)
                track_list = data.get('data', [])
                
                if track_list:
                    track_display = ""
                    for track in track_list:
                        time = track.get('time', '')
                        context = track.get('context', '')
                        track_display += f"【{time}】\n"
                        track_display += f"{context}\n"
                        track_display += "-" * 50 + "\n"
                    self.track_text.setText(track_display)
                else:
                    self.track_text.setText("暂无物流信息")
            except Exception as e:
                self.track_text.setText(f"无法解析物流数据: {e}")
        else:
            self.track_text.setText("暂无物流数据")

    def closeEvent(self, event):
        """关闭事件 - 清理线程"""
        if self.query_thread and self.query_thread.isRunning():
            self.query_thread.quit()
            self.query_thread.wait()
        event.accept()

class ExpressCategoryWidget(QWidget):
    """快递分类组件"""
    
    refresh_category_requested = Signal(str)
    collapse_state_changed = Signal(str, bool)
    
    def __init__(self, category_name: str, category_key: str, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.category_key = category_key
        self.express_items = []
        self.init_ui()
        self.apply_category_style()
        
    def apply_category_style(self):
        """应用分类样式"""
        # 根据分类设置不同的标题颜色
        category_colors = {
            'signed': MacaronColors.GREEN_MINT,
            'arrived': MacaronColors.ORANGE_PEACH,
            'delivering': MacaronColors.BLUE_SKY,
            'transit': MacaronColors.PURPLE_LAVENDER,
            'problem': MacaronColors.RED_CORAL,
            'returned': MacaronColors.NEUTRAL_MOCHA,
            'customs': MacaronColors.YELLOW_LEMON,
            'picked': MacaronColors.GREEN_APPLE,
            'pending': MacaronColors.PINK_COTTON,
            'other': MacaronColors.NEUTRAL_CREAM
        }
        
        bg_color = category_colors.get(self.category_key, MacaronColors.NEUTRAL_CREAM)
        
        self.setStyleSheet(f"""
            ExpressCategoryWidget {{
                background-color: {bg_color.name()};
                border-radius: 12px;
                padding: 8px;
                margin: 3px 0;
            }}
        """)
        
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        
        self.title_label = QLabel(self.category_name)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label)
        
        self.count_label = QLabel("(0)")
        title_layout.addWidget(self.count_label)
        
        title_layout.addStretch()
        
        refresh_btn = QPushButton("刷新此类")
        refresh_btn.setToolTip("刷新此分类下所有快递状态")
        refresh_btn.clicked.connect(lambda: self.refresh_category_requested.emit(self.category_key))
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border-radius: 15px;
                padding: 4px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        title_layout.addWidget(refresh_btn)
        
        self.collapse_btn = QPushButton("▼")
        self.collapse_btn.setFixedSize(30, 30)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        self.collapse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.5);
            }}
        """)
        title_layout.addWidget(self.collapse_btn)
        
        main_layout.addWidget(title_widget)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(5)
        self.content_layout.setContentsMargins(20, 5, 0, 5)
        
        main_layout.addWidget(self.content_widget)
        
        self.setLayout(main_layout)
        self.is_collapsed = False
        
    def toggle_collapse(self):
        """切换折叠/展开"""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.collapse_btn.setText("▶" if self.is_collapsed else "▼")
        self.collapse_state_changed.emit(self.category_key, self.is_collapsed)
        
    def set_collapsed(self, collapsed: bool):
        """设置折叠状态"""
        if self.is_collapsed != collapsed:
            self.is_collapsed = collapsed
            self.content_widget.setVisible(not collapsed)
            self.collapse_btn.setText("▶" if collapsed else "▼")
        
    def add_express_item(self, widget: ExpressItemWidget):
        """添加快递条目"""
        self.content_layout.addWidget(widget)
        self.express_items.append(widget)
        self.update_count()
        
    def remove_express_item(self, widget: ExpressItemWidget):
        """移除快递条目"""
        if widget in self.express_items:
            self.express_items.remove(widget)
            self.content_layout.removeWidget(widget)
            widget.deleteLater()
            self.update_count()
            
    def clear_items(self):
        """清空所有条目"""
        for item in self.express_items:
            self.content_layout.removeWidget(item)
            item.deleteLater()
        self.express_items.clear()
        self.update_count()
        
    def update_count(self):
        """更新计数"""
        self.count_label.setText(f"({len(self.express_items)})")

class UserLoginDialogPro(QDialog):
    """用户登录对话框"""
    
    def __init__(self, user_manager: UserManagerPro, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.selected_user_id = None
        self.init_ui()
        self.load_users()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{ProjectInfo.NAME} - 选择用户")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 添加程序标题
        title_label = QLabel(ProjectInfo.get_full_name())
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #4A90D9; padding: 10px;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("请选择用户登录")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        list_group = QGroupBox("用户列表")
        list_layout = QVBoxLayout()
        
        self.user_list = QListWidget()
        self.user_list.setMinimumHeight(200)
        self.user_list.itemDoubleClicked.connect(self.login_selected_user)
        list_layout.addWidget(self.user_list)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加用户")
        self.add_btn.clicked.connect(self.add_user)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("修改用户名")
        self.edit_btn.clicked.connect(self.edit_user)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除用户")
        self.delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.delete_btn)
        
        layout.addLayout(btn_layout)
        
        action_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.login_selected_user)
        action_layout.addWidget(self.login_btn)
        
        self.cancel_btn = QPushButton("退出程序")
        self.cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(action_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def load_users(self):
        """加载用户列表"""
        self.user_list.clear()
        users = self.user_manager.get_all_users()
        
        for user in users:
            item = QListWidgetItem(f"{user['username']}")
            item.setData(Qt.UserRole, user['id'])
            
            if user['last_login']:
                last_login = datetime.strptime(user['last_login'], "%Y-%m-%d %H:%M:%S")
                item.setToolTip(f"最后登录: {last_login.strftime('%Y-%m-%d %H:%M')}")
            else:
                item.setToolTip("从未登录")
                
            self.user_list.addItem(item)
            
        if self.user_list.count() > 0:
            self.user_list.setCurrentRow(0)
            
    def add_user(self):
        """添加用户"""
        username, ok = QInputDialog.getText(
            self, "添加用户", "请输入新用户名:"
        )
        
        if ok and username.strip():
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            def add_user_thread():
                success, message = self.user_manager.add_user(username.strip())
                self.progress_bar.setVisible(False)
                
                if success:
                    QMessageBox.information(self, "成功", message)
                    self.load_users()
                else:
                    QMessageBox.warning(self, "失败", message)
                    
            QTimer.singleShot(100, add_user_thread)
            
    def edit_user(self):
        """修改用户名"""
        current_item = self.user_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要修改的用户")
            return
            
        user_id = current_item.data(Qt.UserRole)
        old_username = current_item.text()
        
        username, ok = QInputDialog.getText(
            self, "修改用户名", "请输入新用户名:", text=old_username
        )
        
        if ok and username.strip() and username.strip() != old_username:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            def edit_user_thread():
                success, message = self.user_manager.update_user(user_id, username.strip())
                self.progress_bar.setVisible(False)
                
                if success:
                    QMessageBox.information(self, "成功", message)
                    self.load_users()
                else:
                    QMessageBox.warning(self, "失败", message)
                    
            QTimer.singleShot(100, edit_user_thread)
            
    def delete_user(self):
        """删除用户"""
        current_item = self.user_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要删除的用户")
            return
            
        user_id = current_item.data(Qt.UserRole)
        username = current_item.text()
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除用户 '{username}' 吗？\n删除后该用户的所有数据将被保留但不可访问。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            def delete_user_thread():
                success, message = self.user_manager.delete_user(user_id)
                self.progress_bar.setVisible(False)
                
                if success:
                    QMessageBox.information(self, "成功", message)
                    self.load_users()
                else:
                    QMessageBox.warning(self, "失败", message)
                    
            QTimer.singleShot(100, delete_user_thread)
            
    def login_selected_user(self):
        """登录选中的用户"""
        current_item = self.user_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择用户")
            return
            
        self.selected_user_id = current_item.data(Qt.UserRole)
        self.accept()

class BackupRestoreDialogPro(QDialog):
    """备份恢复对话框"""
    
    def __init__(self, backup_manager: BackupManagerPro, current_db_path: str, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.current_db_path = current_db_path
        self.all_backups = []
        self.filtered_backups = []
        self.init_ui()
        self.load_backups()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{ProjectInfo.NAME} - 数据库备份管理")
        self.setMinimumSize(1200, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        toolbar = QHBoxLayout()
        
        filter_group = QGroupBox("筛选条件")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("时间范围:"))
        
        self.date_start = QDateEdit()
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_start.setCalendarPopup(True)
        filter_layout.addWidget(self.date_start)
        
        filter_layout.addWidget(QLabel("至"))
        
        self.date_end = QDateEdit()
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        filter_layout.addWidget(self.date_end)
        
        filter_layout.addWidget(QLabel("备份类型:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["全部", "自动备份", "手动备份", "回滚备份"])
        self.type_filter.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.type_filter)
        
        self.apply_filter_btn = QPushButton("应用筛选")
        self.apply_filter_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.apply_filter_btn)
        
        self.reset_filter_btn = QPushButton("重置")
        self.reset_filter_btn.clicked.connect(self.reset_filter)
        filter_layout.addWidget(self.reset_filter_btn)
        
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        toolbar.addWidget(filter_group)
        
        layout.addLayout(toolbar)
        
        list_group = QGroupBox("备份文件列表")
        list_layout = QVBoxLayout()
        
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(7)
        self.backup_table.setHorizontalHeaderLabels([
            "备份时间", "文件名", "备份类型", "文件大小", 
            "数据库版本", "描述", "操作"
        ])
        self.backup_table.horizontalHeader().setStretchLastSection(True)
        self.backup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        list_layout.addWidget(self.backup_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        preview_group = QGroupBox("备份详细信息")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        btn_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton("恢复选中备份")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.restore_btn.setEnabled(False)
        btn_layout.addWidget(self.restore_btn)
        
        self.manual_backup_btn = QPushButton("立即备份")
        self.manual_backup_btn.clicked.connect(self.create_manual_backup)
        btn_layout.addWidget(self.manual_backup_btn)
        
        self.delete_btn = QPushButton("删除备份")
        self.delete_btn.clicked.connect(self.delete_backup)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)
        
        self.settings_btn = QPushButton("备份设置")
        self.settings_btn.clicked.connect(self.show_backup_settings)
        btn_layout.addWidget(self.settings_btn)
        
        btn_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def load_backups(self):
        """加载备份列表"""
        self.all_backups = self.backup_manager.get_backup_list()
        self.apply_filter()
        
    def apply_filter(self):
        """应用筛选条件"""
        start_date = self.date_start.date().toPython()
        end_date = self.date_end.date().toPython()
        # 将 date 转换为 datetime
        start_date = datetime.combine(start_date, time(0, 0, 0))
        end_date = datetime.combine(end_date, time(23, 59, 59))
        
        type_filter = self.type_filter.currentText()
        type_map = {
            "自动备份": "auto",
            "手动备份": "manual",
            "回滚备份": "rollback"
        }
        
        self.filtered_backups = []
        
        for backup in self.all_backups:
            backup_time = backup['backup_time']
            if backup_time < start_date or backup_time > end_date:
                continue
                
            if type_filter != "全部":
                if backup['backup_type'] != type_map.get(type_filter, ""):
                    continue
                    
            self.filtered_backups.append(backup)
            
        self.update_table()
        
    def reset_filter(self):
        """重置筛选条件"""
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_end.setDate(QDate.currentDate())
        self.type_filter.setCurrentText("全部")
        self.apply_filter()
        
    def update_table(self):
        """更新表格"""
        self.backup_table.setRowCount(len(self.filtered_backups))
        
        for row, backup in enumerate(self.filtered_backups):
            time_item = QTableWidgetItem(backup['backup_time'].strftime("%Y-%m-%d %H:%M:%S"))
            self.backup_table.setItem(row, 0, time_item)
            
            self.backup_table.setItem(row, 1, QTableWidgetItem(backup['filename']))
            
            type_display = {
                'auto': '自动备份',
                'manual': '手动备份',
                'rollback': '回滚备份',
                'unknown': '未知'
            }
            self.backup_table.setItem(row, 2, QTableWidgetItem(type_display.get(backup['backup_type'], '未知')))
            
            size_mb = backup['size'] / (1024 * 1024)
            size_item = QTableWidgetItem(f"{size_mb:.2f} MB")
            self.backup_table.setItem(row, 3, size_item)
            
            self.backup_table.setItem(row, 4, QTableWidgetItem(backup['db_version']))
            
            self.backup_table.setItem(row, 5, QTableWidgetItem(backup['description']))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("查看")
            view_btn.setProperty("backup_data", backup)
            view_btn.clicked.connect(lambda checked, b=backup: self.view_backup_detail(b))
            btn_layout.addWidget(view_btn)
            
            btn_widget.setLayout(btn_layout)
            self.backup_table.setCellWidget(row, 6, btn_widget)
            
        self.backup_table.resizeColumnsToContents()
        
    def on_selection_changed(self):
        """选择改变时的处理"""
        selected_rows = self.backup_table.selectedItems()
        has_selection = len(selected_rows) > 0
        
        self.restore_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
        if has_selection:
            row = selected_rows[0].row()
            if row < len(self.filtered_backups):
                backup = self.filtered_backups[row]
                self.show_preview(backup)
                
    def show_preview(self, backup: Dict):
        """显示备份预览信息"""
        preview_text = f"""
备份文件: {backup['filename']}
备份时间: {backup['backup_time'].strftime('%Y-%m-%d %H:%M:%S')}
备份类型: {backup['backup_type']}
文件大小: {backup['size'] / (1024*1024):.2f} MB
数据库版本: {backup['db_version']}
描述: {backup['description']}
"""
        self.preview_text.setText(preview_text)
        
    def view_backup_detail(self, backup: Dict):
        """查看备份详情"""
        self.show_preview(backup)
        
        for row in range(self.backup_table.rowCount()):
            if self.backup_table.item(row, 1).text() == backup['filename']:
                self.backup_table.selectRow(row)
                break
                
    def create_manual_backup(self):
        """创建手动备份"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = BackupWorkerPro(
            self.backup_manager, 
            self.current_db_path, 
            "manual"
        )
        self.worker.finished.connect(self.on_backup_finished)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
        
    def on_backup_finished(self, success: bool, message: str):
        """备份完成"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.load_backups()
        else:
            QMessageBox.critical(self, "失败", message)
            
    def restore_backup(self):
        """恢复备份"""
        selected_rows = self.backup_table.selectedItems()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        if row >= len(self.filtered_backups):
            return
            
        backup = self.filtered_backups[row]
        
        reply = QMessageBox.question(
            self, "确认恢复",
            f"确定要恢复备份吗？\n\n"
            f"备份文件: {backup['filename']}\n"
            f"备份时间: {backup['backup_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"恢复前会自动创建当前数据库的备份，确保可以回滚。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        
        self.worker = RestoreWorkerPro(
            self.backup_manager,
            backup['path'],
            self.current_db_path
        )
        self.worker.finished.connect(self.on_restore_finished)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
        
    def on_restore_finished(self, success: bool, message: str):
        """恢复完成"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "成功", f"{message}\n\n请重新登录以应用更改。")
            self.load_backups()
            if hasattr(self.parent(), 'reinitialize_database'):
                self.parent().reinitialize_database()
        else:
            QMessageBox.critical(self, "失败", message)
            
    def delete_backup(self):
        """删除备份"""
        selected_rows = self.backup_table.selectedItems()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        if row >= len(self.filtered_backups):
            return
            
        backup = self.filtered_backups[row]
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除此备份吗？\n\n备份文件: {backup['filename']}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.backup_manager.delete_backup(backup['path']):
                QMessageBox.information(self, "成功", "备份已删除")
                self.load_backups()
            else:
                QMessageBox.critical(self, "失败", "删除备份失败")
                
    def show_backup_settings(self):
        """显示备份设置"""
        dialog = BackupSettingsDialogPro(self.backup_manager, self)
        if dialog.exec():
            self.backup_manager.set_max_backups(dialog.get_max_backups())
            self.load_backups()

class BackupSettingsDialogPro(QDialog):
    """备份设置对话框"""
    
    def __init__(self, backup_manager: BackupManagerPro, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{ProjectInfo.NAME} - 系统设置")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        group = QGroupBox("备份保留设置")
        group_layout = QVBoxLayout()
        
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大备份数量:"))
        
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 100)
        self.max_spin.setValue(self.backup_manager.max_backups)
        self.max_spin.setSuffix(" 个")
        max_layout.addWidget(self.max_spin)
        max_layout.addStretch()
        
        group_layout.addLayout(max_layout)
        
        info_label = QLabel("说明: 超过最大数量的旧备份将自动删除")
        group_layout.addWidget(info_label)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        dir_group = QGroupBox("备份存储位置")
        dir_layout = QVBoxLayout()
        
        dir_label = QLabel(f"备份目录: {self.backup_manager.backup_dir}")
        dir_label.setWordWrap(True)
        dir_layout.addWidget(dir_label)
        
        open_dir_btn = QPushButton("打开备份目录")
        open_dir_btn.clicked.connect(self.open_backup_dir)
        dir_layout.addWidget(open_dir_btn)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def open_backup_dir(self):
        """打开备份目录"""
        import subprocess
        backup_dir = str(self.backup_manager.backup_dir)
        
        if sys.platform == 'win32':
            os.startfile(backup_dir)
        elif sys.platform == 'darwin':
            subprocess.run(['open', backup_dir])
        else:
            subprocess.run(['xdg-open', backup_dir])
            
    def get_max_backups(self) -> int:
        """获取最大备份数量"""
        return self.max_spin.value()

class ExpressQueryProGUI(QMainWindow):
    """快递查询系统主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.query_threads = []
        self.batch_thread = None
        
        self.app_data_dir = APP_DIR / "data"
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.user_manager = UserManagerPro(str(self.app_data_dir))
        self.backup_manager = BackupManagerPro(str(self.app_data_dir))
        self.current_user_db = None
        
        self.customer = ""
        self.key = ""
        
        self.api_account_manager = None
        self.delivery_estimator = None
        
        self.company_codes = {
            "自动识别": "",
            # 国内主流快递
            "顺丰速运": "shunfeng",
            "圆通速递": "yuantong",
            "中通快递": "zhongtong",
            "韵达快递": "yunda",
            "申通快递": "shentong",
            "京东物流": "jd",
            "中国邮政": "youzhengguo",
            "EMS": "ems",
            "百世快递": "huitongkuaidi",
            "天天快递": "tiantian",
            "德邦快递": "debangwuliu",
            "极兔速递": "jtexpress",
            # 其他国内快递
            "宅急送": "zhaijisong",
            "优速快递": "youshuwuliu",
            "跨越速运": "kuayue",
            "速尔快递": "suer",
            "全峰快递": "quanfengkuaidi",
            "国通快递": "guotongkuaidi",
            "快捷快递": "kuaijiesudi",
            "龙邦快递": "longbanwuliu",
            "信丰物流": "xinfengwuliu",
            "增益快递": "zengyikuaidi",
            "联昊通": "lianhaowuliu",
            "全一快递": "quanyikuaidi",
            "如风达": "rufengda",
            "安能物流": "annengwuliu",
            "壹米滴答": "yimidida",
            "德坤物流": "dekunwuliu",
            "中铁快运": "zhongtiewuliu",
            "民航快递": "minhangkuaidi",
            "菜鸟裹裹": "cainiao",
            "丹鸟物流": "danniao",
            # 国际快递
            "联邦快递": "fedex",
            "DHL": "dhl",
            "UPS": "ups",
            "TNT": "tnt",
            "USPS": "usps",
            "亚马逊物流": "amazon",
        }
        
        self.category_widgets = {}
        
        self.quota_info = {
            'daily_limit': 0,
            'remaining': 0,
            'reset_time': ''
        }
        
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self.auto_backup)
        self.backup_timer.start(3600000)  # 每小时备份

        # 添加一个定时器，每分钟检查一次是否需要重置配额
        self.quota_reset_timer = QTimer()
        self.quota_reset_timer.timeout.connect(self.check_quota_reset)
        self.quota_reset_timer.start(60000)  # 每分钟检查一次

        if not self.show_login_dialog():
            sys.exit(0)
            
        self.init_ui()
        self.load_user_settings()
        self.load_window_geometry()
        self.load_category_collapse_states()
        self.set_window_icon()
        
        # 应用全局样式
        self.setStyleSheet(MacaronStyle.get_main_style())

    def check_quota_reset(self):
        """检查是否需要重置配额"""
        if self.api_account_manager:
            self.api_account_manager.check_and_reset_daily_usage()

    def set_window_icon(self):
        """设置窗口图标"""
        icon_path = APP_DIR / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            
    def show_login_dialog(self) -> bool:
        """显示登录对话框"""
        dialog = UserLoginDialogPro(self.user_manager, self)
        if dialog.exec() == QDialog.Accepted:
            user_id = dialog.selected_user_id
            if user_id:
                success, message, user_db = self.user_manager.login_user(user_id)
                if success:
                    self.current_user_db = user_db
                    self.api_account_manager = ApiAccountManager(self.current_user_db)
                    self.delivery_estimator = DeliveryTimeEstimator(self.current_user_db)
                    self.load_current_api_account()
                    return True
                else:
                    QMessageBox.critical(self, "登录失败", message)
                    return self.show_login_dialog()
        return False
        
    def load_current_api_account(self):
        """加载当前API账号"""
        if self.api_account_manager:
            # 先强制检查并重置每日使用次数
            self.api_account_manager.check_and_reset_daily_usage()
            # 注意：不要调用 load_accounts()，因为它会重置 current_account 为第一个账号
            
            account = self.api_account_manager.get_current_account()
            if account:
                self.customer = account.get('customer', '')
                self.key = account.get('auth_key', '')
                self.update_api_account_display()
                
                if DEBUG_MODE:
                    print(f"[账号加载] 当前账号: {account.get('account_name', '')}")
                    print(f"[账号加载] Customer: {self.customer[:10] if self.customer else 'empty'}...")
                    print(f"[账号加载] Auth Key: {self.key[:10] if self.key else 'empty'}...")
                
                return True
            else:
                self.customer = ""
                self.key = ""
                self.update_api_account_display()
                
                if DEBUG_MODE:
                    print("[账号加载] 没有可用的API账号")
                
                return False
        else:
            if DEBUG_MODE:
                print("[账号加载] api_account_manager 为 None")
        return False
        
    def check_api_accounts(self):
        """检查API账号"""
        if self.api_account_manager:
            accounts = self.api_account_manager.get_accounts()
            if not accounts:
                reply = QMessageBox.question(
                    self, "提示",
                    "未检测到API账号，是否现在添加？\n\n没有API账号将无法查询快递。",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.show_settings()
        
    def init_ui(self):
        """初始化UI"""
        # 使用 ProjectInfo 设置窗口标题
        self.setWindowTitle(ProjectInfo.get_window_title(self.user_manager.current_user['username']))
        self.setGeometry(100, 100, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.create_toolbar(main_layout)
        
        self.main_tab_widget = QTabWidget()
        
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.main_tab_widget.addTab(self.summary_tab, "📦 快递汇总")
        
        self.query_tab = QWidget()
        self.setup_query_tab()
        self.main_tab_widget.addTab(self.query_tab, "🔍 快递查询")
        
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.main_tab_widget.addTab(self.history_tab, "📋 查询历史")
        
        self.quota_tab = QWidget()
        self.setup_quota_tab()
        self.main_tab_widget.addTab(self.quota_tab, "📊 配额信息")
        
        self.database_tab = QWidget()
        self.setup_database_tab()
        self.main_tab_widget.addTab(self.database_tab, "🗄️ 数据库管理")
        
        main_layout.addWidget(self.main_tab_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        self.global_progress = QProgressBar()
        self.global_progress.setMaximumHeight(3)
        self.global_progress.setTextVisible(False)
        self.status_bar.addPermanentWidget(self.global_progress)
        self.global_progress.setVisible(False)
    
        # 设置全局快捷键
        # Ctrl+F - 聚焦到搜索框
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_global_search)
        
        # Ctrl+1-5 - 切换标签页
        for i in range(1, 6):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda idx=i-1: self.main_tab_widget.setCurrentIndex(idx))
    
        if not self.load_current_api_account():
            QTimer.singleShot(500, self.check_api_accounts)

        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_selected_content)

    def copy_selected_content(self):
        """复制当前选中的内容"""
        # 获取当前焦点控件
        focus_widget = QApplication.focusWidget()
        
        if isinstance(focus_widget, QLineEdit):
            if focus_widget.hasSelectedText():
                focus_widget.copy()
            else:
                focus_widget.selectAll()
                focus_widget.copy()
        elif isinstance(focus_widget, QTextEdit):
            if focus_widget.textCursor().hasSelection():
                focus_widget.copy()
            else:
                focus_widget.selectAll()
                focus_widget.copy()
        elif isinstance(focus_widget, QTableWidget):
            selected_items = focus_widget.selectedItems()
            if selected_items:
                text = selected_items[0].text()
                QApplication.clipboard().setText(text)
                self.status_bar.showMessage("已复制到剪贴板", 2000)

    def focus_global_search(self):
        """聚焦到全局搜索框"""
        self.global_search.setFocus()
        self.global_search.selectAll()

    def create_toolbar(self, parent_layout):
        """创建工具栏"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
    
        # 程序图标和名称
        app_label = QLabel(ProjectInfo.get_short_title())
        app_label.setStyleSheet("font-weight: bold; color: #4A90D9; font-size: 14px;")
        toolbar_layout.addWidget(app_label)
        
        toolbar_layout.addSpacing(20)
        
        user_label = QLabel(f"👤 当前用户: {self.user_manager.current_user['username']}")
        user_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()};")
        toolbar_layout.addWidget(user_label)
        
        # 保存账号标签的引用
        self.api_account_label = QLabel()
        self.api_account_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()};")
        toolbar_layout.addWidget(self.api_account_label)
        self.update_api_account_display()  # 初始化显示
        
        toolbar_layout.addStretch()
        
        search_label = QLabel("🔎 全局搜索:")
        toolbar_layout.addWidget(search_label)
        
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("输入单号、公司...")
        self.global_search.setMinimumWidth(250)
        self.global_search.textChanged.connect(self.on_global_search)
        toolbar_layout.addWidget(self.global_search)
        
        switch_user_btn = QPushButton("🔄 切换用户")
        switch_user_btn.clicked.connect(self.switch_user)
        toolbar_layout.addWidget(switch_user_btn)
        
        reset_window_btn = QPushButton("📐 重置窗口")
        reset_window_btn.setToolTip("重置窗口大小为默认值")
        reset_window_btn.clicked.connect(self.reset_window_size)
        toolbar_layout.addWidget(reset_window_btn)
    
        # 添加"关于"按钮
        about_btn = QPushButton("ℹ️ 关于")
        about_btn.clicked.connect(self.show_about)
        toolbar_layout.addWidget(about_btn)

        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.clicked.connect(self.show_settings)
        toolbar_layout.addWidget(settings_btn)
        
        parent_layout.addWidget(toolbar_widget)

    def show_about(self):
        """显示关于对话框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"关于 {ProjectInfo.NAME}")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(ProjectInfo.get_about_html())
        msg_box.setIconPixmap(self.windowIcon().pixmap(64, 64) if not self.windowIcon().isNull() else None)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def reset_window_size(self):
        """重置窗口大小"""
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.status_bar.showMessage("窗口大小已重置", 2000)
        
    def setup_summary_tab(self):
        """设置快递汇总标签页"""
        layout = QVBoxLayout(self.summary_tab)
        layout.setSpacing(10)
        
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("📝 手动添加单号:"))
        
        self.manual_tracking_input = QLineEdit()
        self.manual_tracking_input.setPlaceholderText("输入快递单号...")
        self.manual_tracking_input.setMinimumWidth(200)
        self.manual_tracking_input.returnPressed.connect(self.add_manual_express)
        toolbar.addWidget(self.manual_tracking_input)
        
        self.manual_company_combo = QComboBox()
        self.manual_company_combo.addItems(list(self.company_codes.keys()))
        toolbar.addWidget(self.manual_company_combo)
        
        add_btn = QPushButton("➕ 添加到汇总")
        add_btn.clicked.connect(self.add_manual_express)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
            }}
        """)
        toolbar.addWidget(add_btn)
    
        # 添加批量导入按钮
        batch_import_btn = QPushButton("📦 批量导入")
        batch_import_btn.setToolTip("从文件或粘贴板批量导入快递单号")
        batch_import_btn.clicked.connect(self.batch_import_express)
        batch_import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PURPLE_WISTERIA.name()};
            }}
        """)
        toolbar.addWidget(batch_import_btn)
        
        toolbar.addStretch()
        
        refresh_all_btn = QPushButton("🔄 刷新全部")
        refresh_all_btn.clicked.connect(self.refresh_all_express)
        refresh_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_SKY.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        toolbar.addWidget(refresh_all_btn)
        
        export_summary_btn = QPushButton("📤 导出汇总")
        export_summary_btn.clicked.connect(self.export_summary)
        toolbar.addWidget(export_summary_btn)
        
        layout.addLayout(toolbar)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_content = QWidget()
        self.summary_layout = QVBoxLayout(scroll_content)
        self.summary_layout.setSpacing(10)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        
        categories = [
            ('arrived', '📍 已到驿站'),
            ('delivering', '🚚 派件中'),
            ('transit', '✈️ 在途中'),
            ('problem', '⚠️ 疑难件'),
            ('returned', '↩️ 退件'),
            ('customs', '🛃 清关中'),
            ('other', '📦 其他'),
            ('picked', '📮 已揽收'),
            ('pending', '⏳ 待揽件'),
            ('signed', '✅ 已签收')
        ]
        
        for key, name in categories:
            widget = ExpressCategoryWidget(name, key)
            widget.refresh_category_requested.connect(self.refresh_category)
            widget.collapse_state_changed.connect(self.on_category_collapse_changed)
            self.category_widgets[key] = widget
            self.summary_layout.addWidget(widget)
            
        self.summary_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        QTimer.singleShot(100, self.load_summary_data)
        
    def setup_query_tab(self):
        """设置快递查询标签页"""
        layout = QVBoxLayout(self.query_tab)
        layout.setSpacing(10)
        
        query_group = QGroupBox("查询信息")
        query_layout = QGridLayout()
        query_layout.setSpacing(10)
        
        query_layout.addWidget(QLabel("快递单号："), 0, 0)
        self.tracking_num = QLineEdit()
        self.tracking_num.setPlaceholderText("请输入快递单号")
        self.tracking_num.setMinimumWidth(300)
        self.tracking_num.returnPressed.connect(self.query_express)
        query_layout.addWidget(self.tracking_num, 0, 1)
        
        query_layout.addWidget(QLabel("快递公司："), 0, 2)
        self.company_combo = QComboBox()
        self.company_combo.addItems(list(self.company_codes.keys()))
        self.company_combo.setCurrentText("自动识别")
        query_layout.addWidget(self.company_combo, 0, 3)
        
        self.query_btn = QPushButton("🔍 开始查询")
        self.query_btn.clicked.connect(self.query_express)
        self.query_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_SKY.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        query_layout.addWidget(self.query_btn, 0, 4)
        
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_query)
        query_layout.addWidget(clear_btn, 0, 5)
        
        self.query_progress = QProgressBar()
        self.query_progress.setVisible(False)
        query_layout.addWidget(self.query_progress, 1, 0, 1, 6)
        
        self.status_label = QLabel("就绪")
        query_layout.addWidget(self.status_label, 2, 0, 1, 6)
        
        query_group.setLayout(query_layout)
        layout.addWidget(query_group)
        
        result_group = QGroupBox("查询结果")
        result_layout = QVBoxLayout()
        
        self.result_tab_widget = QTabWidget()
        
        self.info_widget = QWidget()
        info_layout = QVBoxLayout()
        self.info_tree = QTreeWidget()
        self.info_tree.setHeaderLabels(["字段", "值"])
        self.info_tree.setColumnWidth(0, 200)
        info_layout.addWidget(self.info_tree)
        self.info_widget.setLayout(info_layout)
        self.result_tab_widget.addTab(self.info_widget, "基本信息")
        
        self.track_widget = QWidget()
        track_layout = QVBoxLayout()
        self.track_text = QTextEdit()
        self.track_text.setReadOnly(True)
        track_layout.addWidget(self.track_text)
        self.track_widget.setLayout(track_layout)
        self.result_tab_widget.addTab(self.track_widget, "物流轨迹")
        
        self.raw_widget = QWidget()
        raw_layout = QVBoxLayout()
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        raw_layout.addWidget(self.raw_text)
        self.raw_widget.setLayout(raw_layout)
        self.result_tab_widget.addTab(self.raw_widget, "原始数据")
        
        result_layout.addWidget(self.result_tab_widget)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
    def setup_history_tab(self):
        """设置历史记录标签页"""
        layout = QVBoxLayout(self.history_tab)
        layout.setSpacing(10)
        
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("🔎 搜索:"))
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("搜索单号、公司...")
        self.history_search.textChanged.connect(self.search_history)
        toolbar.addWidget(self.history_search)
        
        toolbar.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.load_history)
        toolbar.addWidget(refresh_btn)
        
        export_btn = QPushButton("📤 导出")
        export_btn.clicked.connect(self.export_history)
        toolbar.addWidget(export_btn)
        
        clear_history_btn = QPushButton("🗑️ 清空历史")
        clear_history_btn.clicked.connect(self.clear_history)
        clear_history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.RED_CORAL.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.RED_WATERMELON.name()};
            }}
        """)
        toolbar.addWidget(clear_history_btn)
        
        layout.addLayout(toolbar)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "查询时间", "快递单号", "快递公司", "状态", 
            "剩余配额", "结果", "操作"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSortingEnabled(True)
        
        layout.addWidget(self.history_table)
        
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        self.stats_label = QLabel("共 0 条记录")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_widget)
        
        self.load_history()
        
    def setup_quota_tab(self):
        """设置配额信息标签页"""
        layout = QVBoxLayout(self.quota_tab)
        layout.setSpacing(10)
        
        info_group = QGroupBox("实时配额信息")
        info_layout = QVBoxLayout()
        
        cards_widget = QWidget()
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setSpacing(15)
        
        self.daily_limit_card = self.create_info_card("每日总配额", "0", "次")
        cards_layout.addWidget(self.daily_limit_card)
        
        self.remaining_card = self.create_info_card("今日剩余次数", "0", "次")
        cards_layout.addWidget(self.remaining_card)
        
        self.used_card = self.create_info_card("今日已用", "0", "次")
        cards_layout.addWidget(self.used_card)
        
        self.usage_rate_card = self.create_info_card("今日使用率", "0", "%")
        cards_layout.addWidget(self.usage_rate_card)
        
        info_layout.addWidget(cards_widget)
        
        self.usage_bar = QProgressBar()
        self.usage_bar.setMinimum(0)
        self.usage_bar.setMaximum(100)
        self.usage_bar.setFormat("使用进度：%p%")
        self.usage_bar.setMinimumHeight(25)
        info_layout.addWidget(self.usage_bar)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        details_group = QGroupBox("配额详情")
        details_layout = QVBoxLayout()
        
        self.quota_tree = QTreeWidget()
        self.quota_tree.setHeaderLabels(["项目", "数值", "说明"])
        self.quota_tree.setColumnWidth(0, 200)
        self.quota_tree.setColumnWidth(1, 150)
        details_layout.addWidget(self.quota_tree)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新配额信息")
        refresh_btn.clicked.connect(self.refresh_quota_info)
        refresh_layout.addWidget(refresh_btn)
        
        layout.addLayout(refresh_layout)
        
    def setup_database_tab(self):
        """设置数据库管理标签页"""
        layout = QVBoxLayout(self.database_tab)
        layout.setSpacing(10)
        
        # 数据库信息
        info_group = QGroupBox("数据库信息")
        info_layout = QGridLayout()
        
        row = 0
        info_layout.addWidget(QLabel("当前数据库:"), row, 0)
        db_path = self.user_manager.current_user_db.db_path if self.user_manager.current_user_db else "未连接"
        self.db_path_label = QLabel(db_path)
        info_layout.addWidget(self.db_path_label, row, 1)
        
        row += 1
        info_layout.addWidget(QLabel("数据库大小:"), row, 0)
        self.db_size_label = QLabel("计算中...")
        info_layout.addWidget(self.db_size_label, row, 1)
        
        row += 1
        info_layout.addWidget(QLabel("WAL模式:"), row, 0)
        self.wal_mode_label = QLabel("已启用")
        info_layout.addWidget(self.wal_mode_label, row, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 数据表信息
        tables_group = QGroupBox("数据表信息")
        tables_layout = QVBoxLayout()
        
        self.tables_table = QTableWidget()
        self.tables_table.setColumnCount(3)
        self.tables_table.setHorizontalHeaderLabels(["表名", "记录数", "说明"])
        self.tables_table.horizontalHeader().setStretchLastSection(True)
        
        # 设置为只读模式
        self.tables_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.tables_table.setSelectionBehavior(QTableWidget.SelectRows)  # 按行选择
        self.tables_table.setSelectionMode(QTableWidget.SingleSelection)  # 单选模式
        self.tables_table.setAlternatingRowColors(True)  # 交替行颜色
        
        tables_layout.addWidget(self.tables_table)
        tables_group.setLayout(tables_layout)
        layout.addWidget(tables_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        backup_btn = QPushButton("💾 备份管理")
        backup_btn.clicked.connect(self.show_backup_dialog)
        btn_layout.addWidget(backup_btn)
        
        optimize_btn = QPushButton("🔧 优化数据库")
        optimize_btn.clicked.connect(self.optimize_database)
        btn_layout.addWidget(optimize_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 刷新数据库信息
        self.refresh_database_info()
        
    def create_info_card(self, title: str, value: str, unit: str) -> QGroupBox:
        """创建信息卡片"""
        card = QGroupBox(title)
        layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)
        
        unit_label = QLabel(unit)
        unit_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(unit_label)
        card.setLayout(layout)
        
        card.value_label = value_label
        
        return card
        
    def get_state_category(self, state: str, context: str = "") -> str:
        """
        根据状态码和物流内容获取分类
        """
        state = str(state)
        context_lower = context.lower() if context else ""
        
        # ====== 已签收相关 ======
        # 优先判断签收，因为有些物流在签收时也会有驿站信息
        # 状态码: 3-已签收, 40-妥投, 75-已完成, 85-已完结
        if state in ['3', '40', '75', '85']:
            return 'signed'
        
        # 通过内容判断是否已签收
        sign_keywords = ['签收', '已收', '妥投', '已签收', '本人签收', '他人签收', '快递员签收']
        for keyword in sign_keywords:
            if keyword in context_lower or keyword in context:
                return 'signed'
        
        # ====== 已到驿站/代收点 ======
        # 驿站相关关键词（优先级高于在途中和派件中）
        驿站_keywords = [
            '驿站', '菜鸟', '丰巢', '快递柜', '自提柜', '代收点', '妈妈驿站', 
            '兔喜', '超市', '代理点', '自提', '代收', '投柜', '出柜',
            '存局', '已送达', '便利店', '物业', '门卫', '快递点', '菜鸟驿站',
            '菜鸟裹裹', '取件码', '凭取件码', '请取件', '可取件', '待取件',
            '快递超市', '邻里驿站', '熊猫快收', '速递易', '云柜', '日日顺',
            '蜂巢', 'e栈', '收件宝', '近邻宝', '格格货栈', '乐收'
        ]
        
        for keyword in 驿站_keywords:
            if keyword in context_lower or keyword in context:
                return 'arrived'
        
        # ====== 派件中相关 ======
        # 状态码: 5-派件中, 15-派件, 39-投递, 41-未妥投, 43-退回未妥投, 45-预约投递
        if state in ['5', '15', '39', '41', '43', '45']:
            return 'delivering'
        
        # 通过内容判断派件中
        delivering_keywords = ['派件', '派送', '投递', '派送中', '派件中', '正在派送', '快递员派送']
        for keyword in delivering_keywords:
            if keyword in context_lower or keyword in context:
                return 'delivering'
        
        # ====== 待揽件/待处理 ======
        # 刚添加，还没有物流信息
        if not context or context == "等待揽件" or context == "暂无物流信息，等待揽件":
            return 'pending'
        
        # ====== 已揽收相关 ======
        # 状态码: 1-已揽收, 12-收件, 13-发件, 16-取件, 37-揽件, 38-收寄, 71-已接单, 72-已取件, 73-已收件
        if state in ['1', '12', '13', '16', '37', '38', '71', '72', '73']:
            return 'picked'
        
        # 通过内容判断已揽收
        picked_keywords = ['揽收', '已揽件', '收件', '取件', '已收寄', '已接单', '已取件']
        for keyword in picked_keywords:
            if keyword in context_lower or keyword in context:
                return 'picked'
        
        # ====== 疑难/问题件相关 ======
        # 状态码: 2-疑难, 11-清关异常, 19-问题件, 35-海关查验, 36-海关扣留
        if state in ['2', '11', '19', '35', '36']:
            return 'problem'
        
        # 更精确的疑难件关键词（排除"物流问题无需找商家"这类误判）
        problem_keywords = ['疑难件', '问题件', '物流异常', '快件异常', '滞留件', '超时件']
        for keyword in problem_keywords:
            if keyword in context_lower or keyword in context:
                return 'problem'
        
        # 未妥投（需要精确匹配）
        if '未妥投' in context or '未投妥' in context:
            return 'problem'
        
        # ====== 退件相关 ======
        # 状态码: 4-退签, 6-退回, 42-退回妥投, 90-已退回, 98-已退货
        if state in ['4', '6', '42', '90', '98']:
            return 'returned'
        
        # 通过内容判断退件
        returned_keywords = ['退回', '退件', '退签', '退货', '返程']
        for keyword in returned_keywords:
            if keyword in context_lower or keyword in context:
                return 'returned'
        
        # ====== 清关相关 ======
        # 状态码: 8-待清关, 9-清关中, 10-已清关, 34-海关放行
        if state in ['8', '9', '10', '34']:
            return 'customs'
        
        # 通过内容判断清关
        customs_keywords = ['清关', '海关', '报关', '通关']
        for keyword in customs_keywords:
            if keyword in context_lower or keyword in context:
                return 'customs'
        
        # ====== 在途中相关 ======
        # 状态码: 0-在途中, 7-转单, 14-到件, 17-投柜, 18-出柜, 20-入库, 21-出库, 22-安检, 23-装车, 24-卸车
        # 25-封发, 26-开拆, 27-离开, 28-到达, 29-中转, 30-交航, 31-起飞, 32-降落, 33-提货
        # 44-存局, 46-自提, 47-代收, 48-代理点
        transit_states = ['0', '7', '14', '17', '18', '20', '21', '22', '23', '24',
                        '25', '26', '27', '28', '29', '30', '31', '32', '33',
                        '44', '46', '47', '48']
        
        state_int = int(state) if state.isdigit() else 0
        if state in transit_states or (49 <= state_int <= 69) or (74 <= state_int <= 89) or (91 <= state_int <= 99):
            return 'transit'
        
        # 通过内容判断在途中
        transit_keywords = ['在途', '运输', '中转', '到达', '离开', '发出', '发往', '送往']
        for keyword in transit_keywords:
            if keyword in context_lower or keyword in context:
                return 'transit'
        
        # ====== 默认分类 ======
        # 如果都不匹配，默认归类为在途中
        return 'transit'

        
    def get_state_text(self, state: str) -> str:
        """状态码转文字"""
        states = {
            '0': '在途中',
            '1': '已揽收',
            '2': '疑难件',
            '3': '已签收',
            '4': '退签',
            '5': '派件中',
            '6': '退回',
            '7': '转单',
            '8': '待清关',
            '9': '清关中',
            '10': '已清关',
            '11': '清关异常',
            '12': '收件',
            '13': '发件',
            '14': '到件',
            '15': '派件',
            '16': '取件',
            '17': '投柜',
            '18': '出柜',
            '19': '问题件',
            '20': '入库',
            '21': '出库',
            '22': '安检',
            '23': '装车',
            '24': '卸车',
            '25': '封发',
            '26': '开拆',
            '27': '离开',
            '28': '到达',
            '29': '中转',
            '30': '交航',
            '31': '起飞',
            '32': '降落',
            '33': '提货',
            '34': '海关放行',
            '35': '海关查验',
            '36': '海关扣留',
            '37': '揽件',
            '38': '收寄',
            '39': '投递',
            '40': '妥投',
            '41': '未妥投',
            '42': '退回妥投',
            '43': '退回未妥投',
            '44': '存局',
            '45': '预约投递',
            '46': '自提',
            '47': '代收',
            '48': '代理点',
        }
        return states.get(str(state), f'状态{state}')
        
    def load_summary_data(self):
        """加载汇总数据"""
        if not self.user_manager.current_user_db:
            return
            
        for widget in self.category_widgets.values():
            widget.clear_items()
            
        query = """
        SELECT * FROM express_summary 
        WHERE is_deleted = 0 
        ORDER BY last_update DESC
        """
        
        results = self.user_manager.current_user_db.execute_query(query)
        
        for record in results:
            self.add_express_to_category(record)
            
    def add_express_to_category(self, record: Dict):
        """添加快递到对应分类"""
        category = record.get('status_category', 'other')
        
        if category not in self.category_widgets:
            category = 'other'
        
        widget = ExpressItemWidget(record, parent_gui=self)  # 传递 self
        widget.remark_changed.connect(self.on_remark_changed)
        widget.screenshot_changed.connect(self.on_screenshot_changed)
        widget.refresh_requested.connect(self.on_single_refresh)
        widget.view_details_requested.connect(self.on_view_details)
        widget.delete_requested.connect(self.on_delete_express)
        
        self.category_widgets[category].add_express_item(widget)
            
    def on_remark_changed(self, express_id: int, remark: str):
        """备注改变"""
        if self.user_manager.current_user_db:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE express_summary SET remark = ?, last_update = ? WHERE id = ?"
            self.user_manager.current_user_db.execute_update(sql, (remark, current_time, express_id))
            
    def on_screenshot_changed(self, express_id: int, screenshot: str):
        """截图改变"""
        if self.user_manager.current_user_db:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE express_summary SET screenshot = ?, last_update = ? WHERE id = ?"
            self.user_manager.current_user_db.execute_update(sql, (screenshot, current_time, express_id))
            
    def on_delete_express(self, express_id: int):
        """删除快递"""
        if self.user_manager.current_user_db:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE express_summary SET is_deleted = 1, last_update = ? WHERE id = ?"
            if self.user_manager.current_user_db.execute_update(sql, (current_time, express_id)):
                self.load_summary_data()
                self.status_bar.showMessage("快递已删除", 3000)
            
    def on_single_refresh(self, tracking_num: str, company_code: str):
        """单个快递刷新"""
        if not self.customer or not self.key:
            QMessageBox.warning(self, "提示", "未配置API账号，请先在设置中添加账号")
            return
        
        # 检查当前账号是否可用
        if self.api_account_manager:
            self.api_account_manager.check_and_reset_daily_usage()
            
            if not self.api_account_manager.is_current_account_available():
                # 尝试切换到下一个账号（正常切换，不强制）
                if self.api_account_manager.switch_to_next_account(force_switch=False):
                    self.load_current_api_account()
                    usage_info = self.api_account_manager.get_usage_info()
                    self.status_bar.showMessage(f"已自动切换到备用账号，剩余次数：{usage_info['remaining']}", 3000)
                else:
                    QMessageBox.warning(self, "提示", "所有账号今日额度都已用完，请明天再试")
                    return
                
        self.status_bar.showMessage(f"正在刷新 {tracking_num}...")
        
        thread = ExpressQueryThreadPro(tracking_num, company_code, self.customer, self.key)
        thread.finished.connect(lambda r: self.on_single_refresh_finished(r, tracking_num))
        thread.start()
        self.query_threads.append(thread)
        
    def on_single_refresh_finished(self, result: dict, tracking_num: str):
        """单个快递刷新完成"""
        if result.get('success'):
            self.update_express_summary(result['data'])
            self.status_bar.showMessage(f"{tracking_num} 刷新成功", 3000)
            self.load_summary_data()
            
            if self.api_account_manager:
                self.api_account_manager.increment_usage()
                self.update_api_account_display()
        else:
            # 刷新失败，尝试切换账号重试
            error_msg = result.get('error', '未知错误')
            
            if DEBUG_MODE:
                print(f"[刷新失败] {tracking_num}: {error_msg}")
            
            if self.api_account_manager:
                # 记录当前账号
                old_account = self.api_account_manager.current_account
                old_account_id = old_account.get('id') if old_account else None
                old_account_name = old_account.get('account_name', '未知') if old_account else '无'
                
                if DEBUG_MODE:
                    print(f"[刷新失败] 当前账号: {old_account_name}, 尝试切换...")
                
                # 尝试切换到下一个账号（强制切换）
                if self.api_account_manager.switch_to_next_account(force_switch=True):
                    new_account = self.api_account_manager.current_account
                    new_account_id = new_account.get('id') if new_account else None
                    new_account_name = new_account.get('account_name', '未知') if new_account else '无'
                    
                    if old_account_id != new_account_id:
                        if DEBUG_MODE:
                            print(f"[刷新失败] 切换到账号: {new_account_name}")
                        
                        if not self.load_current_api_account():
                            self.status_bar.showMessage(f"{tracking_num} 刷新失败（切换账号失败）", 3000)
                            return
                        
                        self.update_api_account_display()
                        self.status_bar.showMessage(f"{tracking_num} 刷新失败，正在切换账号重试...", 3000)
                        
                        # 获取该快递的公司代码
                        company_code = ""
                        if self.user_manager.current_user_db:
                            sql = "SELECT company_code FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
                            query_result = self.user_manager.current_user_db.execute_query(sql, (tracking_num,))
                            if query_result:
                                company_code = query_result[0].get('company_code', '')
                        
                        # 用新账号重试
                        thread = ExpressQueryThreadPro(tracking_num, company_code, self.customer, self.key)
                        thread.finished.connect(lambda r: self.on_single_refresh_retry_finished(r, tracking_num))
                        thread.start()
                        self.query_threads.append(thread)
                        return
                    else:
                        if DEBUG_MODE:
                            print(f"[刷新失败] 切换后账号未变化: {new_account_name}")
                        self.status_bar.showMessage(f"{tracking_num} 刷新失败（无可用备用账号）", 3000)
                else:
                    if DEBUG_MODE:
                        print("[刷新失败] switch_to_next_account 返回 False")
                    self.status_bar.showMessage(f"{tracking_num} 刷新失败，无备用账号可切换", 3000)
            else:
                if DEBUG_MODE:
                    print("[刷新失败] api_account_manager 为 None")
                self.status_bar.showMessage(f"{tracking_num} 刷新失败: {error_msg}", 5000)

    def on_single_refresh_retry_finished(self, result: dict, tracking_num: str):
        """单个快递刷新重试完成"""
        if result.get('success'):
            self.update_express_summary(result['data'])
            self.status_bar.showMessage(f"{tracking_num} 刷新成功（切换账号后）", 3000)
            self.load_summary_data()
            
            # 更新配额显示
            if self.api_account_manager:
                self.api_account_manager.increment_usage()
                self.update_api_account_display()
        else:
            error_msg = result.get('error', '未知错误')
            self.status_bar.showMessage(f"{tracking_num} 刷新失败: {error_msg}", 5000)
            
    def on_view_details(self, express_data: Dict):
        """查看快递详情"""
        express_id = express_data.get('id', 0)
        tracking_num = express_data.get('tracking_number', '')
        dialog = ExpressDetailDialog(express_id, tracking_num, self, self)
        dialog.exec()
        
    def add_manual_express(self):
        """手动添加快递"""
        tracking_num = self.manual_tracking_input.text().strip()
        if not tracking_num:
            QMessageBox.warning(self, "提示", "请输入快递单号！")
            return
            
        company_name = self.manual_company_combo.currentText()
        company_code = self.company_codes.get(company_name, "")
        
        if self.user_manager.current_user_db:
            check_sql = "SELECT id FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
            existing = self.user_manager.current_user_db.execute_query(check_sql, (tracking_num,))
            if existing:
                QMessageBox.information(self, "提示", "该快递单号已存在于汇总中")
                return
                
        self.status_bar.showMessage(f"正在查询并添加 {tracking_num}...")
        
        thread = ExpressQueryThreadPro(tracking_num, company_code, self.customer, self.key)
        thread.finished.connect(lambda r: self.on_manual_add_finished(r, tracking_num, company_code, company_name))
        thread.start()
        self.query_threads.append(thread)

    def batch_import_express(self):
        """批量导入快递单号"""
        if not self.customer or not self.key:
            reply = QMessageBox.question(
                self, "提示",
                "未配置API账号，无法查询快递。是否现在添加账号？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.show_settings()
            return
            
        dialog = BatchImportDialog(self.company_codes, self)
        if dialog.exec() != QDialog.Accepted:
            return
            
        numbers = dialog.get_imported_numbers()
        if not numbers:
            return
            
        # 过滤已存在的单号
        to_import = []
        existing_numbers = []
        
        if self.user_manager.current_user_db:
            for item in numbers:
                check_sql = "SELECT id FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
                existing = self.user_manager.current_user_db.execute_query(check_sql, (item['number'],))
                if existing:
                    existing_numbers.append(item['number'])
                else:
                    to_import.append(item)
                    
        if existing_numbers:
            reply = QMessageBox.question(
                self, "重复单号",
                f"有 {len(existing_numbers)} 个单号已存在于汇总中，是否跳过继续导入其余单号？\n\n"
                f"重复单号：{', '.join(existing_numbers[:5])}"
                f"{'...' if len(existing_numbers) > 5 else ''}",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
                
        if not to_import:
            QMessageBox.information(self, "提示", "所有单号都已存在于汇总中")
            return
            
        # 确认导入
        reply = QMessageBox.question(
            self, "确认导入",
            f"即将导入 {len(to_import)} 个快递单号，是否继续？\n\n"
            f"导入后系统将自动查询物流信息。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # 开始批量导入
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, len(to_import))
        self.global_progress.setValue(0)
        self.status_bar.showMessage(f"正在批量导入 {len(to_import)} 个单号...")
        
        self.batch_import_list = to_import
        self.batch_import_index = 0
        self.batch_import_results = []
        
        self.process_next_batch_import()
        
    def process_next_batch_import(self):
        """处理下一个批量导入"""
        if self.batch_import_index >= len(self.batch_import_list):
            self.finish_batch_import()
            return
            
        item = self.batch_import_list[self.batch_import_index]
        tracking_num = item['number']
        company_code = item['company_code']
        
        self.global_progress.setValue(self.batch_import_index)
        self.status_bar.showMessage(f"正在查询: {tracking_num} ({self.batch_import_index + 1}/{len(self.batch_import_list)})")
        
        thread = ExpressQueryThreadPro(tracking_num, company_code, self.customer, self.key)
        thread.finished.connect(lambda r, num=tracking_num: self.on_batch_import_finished(r, num))
        thread.start()
        self.query_threads.append(thread)
        
    def on_batch_import_finished(self, result: dict, tracking_num: str):
        """单个批量导入完成"""
        item = self.batch_import_list[self.batch_import_index]
        
        if result.get('success'):
            self.add_to_summary(result['data'], item['company_name'])
            self.batch_import_results.append({
                'number': tracking_num,
                'success': True,
                'message': '导入成功'
            })
            self.batch_import_index += 1
            QTimer.singleShot(300, self.process_next_batch_import)
        else:
            error_msg = result.get('error', '未知错误')
            
            retried = False
            if self.api_account_manager:
                # 尝试切换到下一个账号（强制切换）
                if self.api_account_manager.switch_to_next_account(force_switch=True):
                    self.load_current_api_account()
                    # 用新账号重试这个单号
                    thread = ExpressQueryThreadPro(tracking_num, item['company_code'], self.customer, self.key)
                    thread.finished.connect(lambda r, num=tracking_num: self.on_batch_import_retry_finished(r, num, item))
                    thread.start()
                    self.query_threads.append(thread)
                    retried = True
            
            if not retried:
                self.batch_import_results.append({
                    'number': tracking_num,
                    'success': False,
                    'message': error_msg
                })
                self.batch_import_index += 1
                QTimer.singleShot(300, self.process_next_batch_import)

    def on_batch_import_retry_finished(self, result: dict, tracking_num: str, item: dict):
        """批量导入重试完成"""
        if result.get('success'):
            self.add_to_summary(result['data'], item['company_name'])
            self.batch_import_results.append({
                'number': tracking_num,
                'success': True,
                'message': '导入成功（切换账号后）'
            })
        else:
            error_msg = result.get('error', '未知错误')
            self.batch_import_results.append({
                'number': tracking_num,
                'success': False,
                'message': f"{error_msg}（已切换账号重试）"
            })
        
        self.batch_import_index += 1
        QTimer.singleShot(300, self.process_next_batch_import)
        
    def finish_batch_import(self):
        """完成批量导入"""
        self.global_progress.setVisible(False)
        
        success_count = sum(1 for r in self.batch_import_results if r['success'])
        fail_count = len(self.batch_import_results) - success_count
        
        # 刷新汇总显示
        self.load_summary_data()
        
        # 显示结果摘要
        summary = f"批量导入完成！\n\n成功：{success_count} 个\n失败：{fail_count} 个"
        
        if fail_count > 0:
            failed_list = [f"{r['number']}: {r['message']}" for r in self.batch_import_results if not r['success']]
            detail = "\n\n失败详情（前10个）：\n" + "\n".join(failed_list[:10])
            if len(failed_list) > 10:
                detail += f"\n... 共 {len(failed_list)} 个失败"
            summary += detail

        print(summary)  # 在控制台输出结果摘要
        QMessageBox.information(self, "批量导入完成", summary)
        self.status_bar.showMessage(f"批量导入完成：成功 {success_count}，失败 {fail_count}", 5000)


    def on_manual_add_finished(self, result: dict, tracking_num: str, company_code: str, company_name: str):
        """手动添加完成"""
        if result.get('success'):
            self.add_to_summary(result['data'], company_name)
            self.manual_tracking_input.clear()
            self.status_bar.showMessage(f"{tracking_num} 已添加到汇总", 3000)
            self.load_summary_data()
        else:
            error_msg = result.get('error', '未知错误')
            print(f"查询失败：{error_msg}")
            QMessageBox.critical(self, "添加失败", f"查询失败：{error_msg}")
            self.status_bar.showMessage("添加失败", 3000)
            
    def add_to_summary(self, data: dict, company_name: str = None):
        """添加到汇总表"""
        if not self.user_manager.current_user_db:
            return
            
        tracking_num = data.get('nu', '')
        company_code = data.get('com', '')
        if not company_name:
            company_name = self.get_company_name(company_code)
        state = str(data.get('state', '0'))  # 默认状态为0（在途中/待揽件）
        state_text = self.get_state_text(state)
        
        track_list = data.get('data', [])
        latest_track = ''
        latest_context = ''
        if track_list:
            latest = track_list[0]
            latest_track = f"[{latest.get('time', '')}] {latest.get('context', '')}"
            latest_context = latest.get('context', '')
        else:
            # 没有物流轨迹时，设置默认值
            latest_track = "暂无物流信息，等待揽件"
            latest_context = "等待揽件"
        
        category = self.get_state_category(state, latest_context)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        check_sql = "SELECT id FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
        existing = self.user_manager.current_user_db.execute_query(check_sql, (tracking_num,))
        
        if existing:
            sql = """
            UPDATE express_summary 
            SET company_code = ?, company_name = ?, status = ?, status_category = ?, 
                latest_track = ?, result_data = ?, last_update = ?
            WHERE tracking_number = ? AND is_deleted = 0
            """
            self.user_manager.current_user_db.execute_update(
                sql,
                (company_code, company_name, state_text, category, latest_track, 
                json.dumps(data, ensure_ascii=False), current_time, tracking_num)
            )
        else:
            sql = """
            INSERT INTO express_summary 
            (tracking_number, company_code, company_name, status, status_category, 
            latest_track, result_data, last_update, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.user_manager.current_user_db.execute_update(
                sql,
                (tracking_num, company_code, company_name, state_text, category,
                latest_track, json.dumps(data, ensure_ascii=False), current_time, current_time)
            )
            
        # 记录时效数据（如果是已签收或已到驿站）
        if self.delivery_estimator:
            context = latest_context
            should_record = False
            
            # 检查是否已签收
            if state == '3':
                should_record = True
            elif self.delivery_estimator.is_signed(context):
                should_record = True
            # 检查是否已到驿站
            elif self.delivery_estimator.is_arrived_at_station(context):
                should_record = True
                
            # 也检查完整的物流轨迹（有时候最新一条不是签收/驿站信息）
            if not should_record and track_list:
                for track in track_list:
                    track_context = track.get('context', '')
                    if self.delivery_estimator.is_signed(track_context):
                        should_record = True
                        break
                    elif self.delivery_estimator.is_arrived_at_station(track_context):
                        should_record = True
                        break
                        
            if should_record:
                self.delivery_estimator.record_delivery(data)
        
    def update_express_summary(self, data: dict):
        """更新快递汇总信息"""
        if not self.user_manager.current_user_db:
            return
            
        tracking_num = data.get('nu', '')
        state = str(data.get('state', ''))
        state_text = self.get_state_text(state)
        
        track_list = data.get('data', [])
        latest_track = ''
        latest_context = ''
        if track_list:
            latest = track_list[0]
            latest_track = f"[{latest.get('time', '')}] {latest.get('context', '')}"
            latest_context = latest.get('context', '')
        
        category = self.get_state_category(state, latest_context)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sql = """
        UPDATE express_summary 
        SET status = ?, status_category = ?, latest_track = ?, 
            result_data = ?, last_update = ?
        WHERE tracking_number = ? AND is_deleted = 0
        """
        
        if self.user_manager.current_user_db.execute_update(
            sql,
            (state_text, category, latest_track, json.dumps(data, ensure_ascii=False), 
            current_time, tracking_num)
        ):
            self.load_summary_data()
            
        # 记录时效数据（如果是已签收或已到驿站）- 批量刷新时也会触发
        if self.delivery_estimator:
            context = latest_context
            should_record = False
            
            # 检查是否已签收
            if state == '3':
                should_record = True
            elif self.delivery_estimator.is_signed(context):
                should_record = True
            # 检查是否已到驿站
            elif self.delivery_estimator.is_arrived_at_station(context):
                should_record = True
                
            # 也检查完整的物流轨迹
            if not should_record and track_list:
                for track in track_list:
                    track_context = track.get('context', '')
                    if self.delivery_estimator.is_signed(track_context):
                        should_record = True
                        break
                    elif self.delivery_estimator.is_arrived_at_station(track_context):
                        should_record = True
                        break
                        
            if should_record:
                self.delivery_estimator.record_delivery(data)
            
    def refresh_category(self, category_key: str):
        """刷新分类下所有快递"""
        if not self.customer or not self.key:
            QMessageBox.warning(self, "提示", "未配置API账号，请先在设置中添加账号")
            return
            
        if category_key not in self.category_widgets:
            return
            
        category_widget = self.category_widgets[category_key]
        items = category_widget.express_items
        
        if not items:
            QMessageBox.information(self, "提示", "该分类下没有快递需要刷新")
            return
        
        # 检查当前账号是否可用
        if self.api_account_manager:
            self.api_account_manager.check_and_reset_daily_usage()
            
            if not self.api_account_manager.is_current_account_available():
                # 尝试切换到下一个账号（正常切换，不强制）
                if self.api_account_manager.switch_to_next_account(force_switch=False):
                    self.load_current_api_account()
                    usage_info = self.api_account_manager.get_usage_info()
                    self.status_bar.showMessage(f"已自动切换到备用账号，剩余次数：{usage_info['remaining']}", 3000)
                else:
                    QMessageBox.warning(self, "提示", "所有账号今日额度都已用完，请明天再试")
                    return
            
        tracking_list = []
        for item in items:
            tracking_list.append({
                'tracking_number': item.express_data.get('tracking_number', ''),
                'company_code': item.express_data.get('company_code', '')
            })
            
        self.global_progress.setVisible(True)
        self.status_bar.showMessage(f"正在刷新 {category_widget.category_name} 分类...")
        
        self.batch_thread = BatchRefreshThread(tracking_list, self.customer, self.key)
        self.batch_thread.finished.connect(self.on_batch_refresh_finished)  # 现在接收两个参数
        self.batch_thread.progress.connect(self.on_batch_progress)
        self.batch_thread.start()
        
    def refresh_all_express(self):
        """刷新所有快递"""
        if not self.customer or not self.key:
            QMessageBox.warning(self, "提示", "未配置API账号，请先在设置中添加账号")
            return
        
        # 检查当前账号是否可用
        if self.api_account_manager:
            self.api_account_manager.check_and_reset_daily_usage()
            
            if not self.api_account_manager.is_current_account_available():
                # 尝试切换到下一个账号（正常切换，不强制）
                if self.api_account_manager.switch_to_next_account(force_switch=False):
                    self.load_current_api_account()
                    usage_info = self.api_account_manager.get_usage_info()
                    self.status_bar.showMessage(f"已自动切换到备用账号，剩余次数：{usage_info['remaining']}", 3000)
                else:
                    QMessageBox.warning(self, "提示", "所有账号今日额度都已用完，请明天再试")
                    return
            
        tracking_list = []
        for widget in self.category_widgets.values():
            for item in widget.express_items:
                tracking_list.append({
                    'tracking_number': item.express_data.get('tracking_number', ''),
                    'company_code': item.express_data.get('company_code', '')
                })
                
        if not tracking_list:
            QMessageBox.information(self, "提示", "没有快递需要刷新")
            return
            
        self.global_progress.setVisible(True)
        self.status_bar.showMessage("正在刷新所有快递...")
        
        self.batch_thread = BatchRefreshThread(tracking_list, self.customer, self.key)
        self.batch_thread.finished.connect(self.on_batch_refresh_finished)  # 现在接收两个参数
        self.batch_thread.progress.connect(self.on_batch_progress)
        self.batch_thread.start()
        
    def on_batch_progress(self, value: int, message: str):
        """批量刷新进度"""
        self.global_progress.setValue(value)
        self.status_bar.showMessage(message)
        
    def on_batch_refresh_finished(self, success_results: list, failed_items: list):
        """批量刷新完成"""
        self.global_progress.setVisible(False)
        
        success_count = len(success_results)
        fail_count = len(failed_items)
        
        # 处理成功的结果
        for result in success_results:
            if result.get('success'):
                self.update_express_summary(result['data'])
        
        # 如果有失败的单号，尝试切换账号重试
        if failed_items and self.api_account_manager:
            if DEBUG_MODE:
                print(f"[批量刷新] 有 {fail_count} 个单号刷新失败，尝试切换账号...")
            
            # 记录当前账号
            old_account = self.api_account_manager.current_account
            old_account_id = old_account.get('id') if old_account else None
            
            # 尝试切换到下一个账号（强制切换）
            if self.api_account_manager.switch_to_next_account(force_switch=True):
                new_account = self.api_account_manager.current_account
                new_account_id = new_account.get('id') if new_account else None
                
                if old_account_id != new_account_id:
                    if DEBUG_MODE:
                        print(f"[批量刷新] 切换到账号: {new_account.get('account_name', '未知')}")
                    
                    if not self.load_current_api_account():
                        self.status_bar.showMessage(f"刷新完成：成功 {success_count}，失败 {fail_count}（切换账号失败）", 5000)
                        self.load_summary_data()
                        return
                    
                    self.update_api_account_display()
                    
                    # 询问是否重试失败的单号
                    reply = QMessageBox.question(
                        self, "刷新完成",
                        f"成功刷新 {success_count} 个快递，{fail_count} 个刷新失败。\n\n"
                        f"已自动切换到备用账号，是否使用新账号重试失败的单号？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        # 使用新账号重试失败的单号
                        self.retry_failed_refresh(failed_items)
                        return
                    else:
                        self.status_bar.showMessage(f"刷新完成：成功 {success_count}，失败 {fail_count}（已切换账号）", 5000)
                else:
                    if DEBUG_MODE:
                        print("[批量刷新] 切换后账号未变化")
                    self.status_bar.showMessage(f"刷新完成：成功 {success_count}，失败 {fail_count}（无可用备用账号）", 5000)
            else:
                if DEBUG_MODE:
                    print("[批量刷新] switch_to_next_account 返回 False")
                self.status_bar.showMessage(f"刷新完成：成功 {success_count}，失败 {fail_count}（无备用账号可切换）", 5000)
        else:
            self.status_bar.showMessage(f"刷新完成：成功 {success_count} 个，失败 {fail_count} 个", 5000)
        
        self.load_summary_data()

    def retry_failed_refresh(self, failed_items: list):
        """重试失败的刷新"""
        if not failed_items:
            return
        
        self.global_progress.setVisible(True)
        self.status_bar.showMessage(f"正在使用新账号重试 {len(failed_items)} 个失败的单号...")
        
        # 转换为批量刷新需要的格式
        tracking_list = [
            {'tracking_number': item['tracking_number'], 'company_code': item.get('company_code', '')}
            for item in failed_items
        ]
        
        self.batch_retry_thread = BatchRefreshThread(tracking_list, self.customer, self.key)
        self.batch_retry_thread.finished.connect(self.on_retry_batch_finished)
        self.batch_retry_thread.progress.connect(self.on_batch_progress)
        self.batch_retry_thread.start()

    def on_retry_batch_finished(self, success_results: list, failed_items: list):
        """重试批量刷新完成"""
        self.global_progress.setVisible(False)
        
        success_count = len(success_results)
        fail_count = len(failed_items)
        
        # 处理成功的结果
        for result in success_results:
            if result.get('success'):
                self.update_express_summary(result['data'])
                # 增加使用次数
                if self.api_account_manager:
                    self.api_account_manager.increment_usage()
        
        self.update_api_account_display()
        
        if fail_count == 0:
            self.status_bar.showMessage(f"重试成功！所有单号已刷新", 5000)
            QMessageBox.information(self, "重试完成", f"所有失败的单号都已成功刷新！")
        else:
            self.status_bar.showMessage(f"重试完成：成功 {success_count}，仍有 {fail_count} 个失败", 5000)
            QMessageBox.warning(self, "重试完成", 
                f"成功刷新 {success_count} 个单号\n"
                f"仍有 {fail_count} 个单号刷新失败，可能是单号无效或API问题。")
        
        self.load_summary_data()
        
    def on_category_collapse_changed(self, category_key: str, is_collapsed: bool):
        """分类折叠状态改变"""
        self.save_category_collapse_states()
        
    def save_category_collapse_states(self):
        """保存分类折叠状态"""
        states = {}
        for key, widget in self.category_widgets.items():
            states[key] = widget.is_collapsed
        
        self.user_manager.save_user_setting("category_collapse_states", json.dumps(states))
        
    def load_category_collapse_states(self):
        """加载分类折叠状态"""
        states_str = self.user_manager.get_user_setting("category_collapse_states", "")
        if states_str:
            try:
                states = json.loads(states_str)
                for key, is_collapsed in states.items():
                    if key in self.category_widgets:
                        self.category_widgets[key].set_collapsed(is_collapsed)
            except:
                pass
                
    def load_window_geometry(self):
        """加载窗口大小和位置"""
        geometry_str = self.user_manager.get_user_setting("window_geometry", "")
        if geometry_str:
            try:
                geometry = geometry_str.split(',')
                if len(geometry) == 4:
                    x, y, w, h = map(int, geometry)
                    self.setGeometry(x, y, w, h)
            except:
                pass
                
    def save_window_geometry(self):
        """保存窗口大小和位置"""
        geometry = self.geometry()
        geometry_str = f"{geometry.x()},{geometry.y()},{geometry.width()},{geometry.height()}"
        self.user_manager.save_user_setting("window_geometry", geometry_str)
        
    def export_summary(self):
        """导出汇总"""
        if not self.category_widgets:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出快递汇总", 
            f"express_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["分类", "快递单号", "快递公司", "状态", "备注", "最新轨迹", "最后更新"])
                
                for key, widget in self.category_widgets.items():
                    category_name = widget.category_name
                    for item in widget.express_items:
                        data = item.express_data
                        writer.writerow([
                            category_name,
                            data.get('tracking_number', ''),
                            data.get('company_name', ''),
                            data.get('status', ''),
                            data.get('remark', ''),
                            data.get('latest_track', ''),
                            data.get('last_update', '')
                        ])
                        
            QMessageBox.information(self, "成功", f"已导出到: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
            
    def get_company_name(self, code: str) -> str:
        """根据代码获取公司名称"""
        for name, c in self.company_codes.items():
            if c == code:
                return name
        return code or "未知"
        
    def query_express(self):
        """查询快递"""
        tracking_num = self.tracking_num.text().strip()
        if not tracking_num:
            QMessageBox.warning(self, "提示", "请输入快递单号！")
            return
            
        if not self.customer or not self.key:
            reply = QMessageBox.question(
                self, "提示",
                "未配置API账号，无法查询快递。是否现在添加账号？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.show_settings()
            return
    

        # 检查当前账号是否可用
        if self.api_account_manager:
            # 先检查是否需要重置
            self.api_account_manager.check_and_reset_daily_usage()
            
            if not self.api_account_manager.is_current_account_available():
                # 尝试切换到下一个账号（正常切换，不强制）
                if self.api_account_manager.switch_to_next_account(force_switch=False):
                    self.load_current_api_account()
                    usage_info = self.api_account_manager.get_usage_info()
                    QMessageBox.information(self, "提示", 
                        f"当前账号额度已用完，已自动切换到备用账号\n"
                        f"新账号今日剩余次数：{usage_info['remaining']}/{usage_info['limit']}")
                else:
                    # 获取所有账号的使用情况
                    accounts = self.api_account_manager.get_accounts()
                    info_text = "所有账号今日额度都已用完：\n"
                    for acc in accounts:
                        info_text += f"  {acc['account_name']}: {acc['used_today']}/{acc['daily_limit']}\n"
                    info_text += "\n请在明天0点后重试，或添加新的API账号。"
                    QMessageBox.warning(self, "提示", info_text)
                    return

        if self.api_account_manager and not self.api_account_manager.is_current_account_available():
            if self.api_account_manager.switch_to_next_account(force_switch=False):
                self.load_current_api_account()
                QMessageBox.information(self, "提示", "当前账号额度已用完，已自动切换到备用账号")
            else:
                QMessageBox.warning(self, "提示", "所有账号今日额度都已用完，请明天再试")
                return
            
        self.clear_results()
        
        company_name = self.company_combo.currentText()
        company_code = self.company_codes.get(company_name, "")
        
        self.status_label.setText("正在查询中，请稍候...")
        self.query_btn.setEnabled(False)
        self.query_progress.setVisible(True)
        self.query_progress.setRange(0, 100)
        self.status_bar.showMessage("正在查询...")
        
        self.query_thread = ExpressQueryThreadPro(
            tracking_num, company_code, 
            self.customer, self.key
        )
        self.query_thread.finished.connect(self.on_query_finished)
        self.query_thread.progress.connect(self.query_progress.setValue)
        self.query_thread.start()
        self.query_threads.append(self.query_thread)
        
    def on_query_finished(self, result: dict):
        """查询完成回调"""
        self.query_btn.setEnabled(True)
        self.query_progress.setVisible(False)
        
        if 'quota_info' in result:
            self.update_quota_info(result['quota_info'])
            
        if result.get('success'):
            if self.api_account_manager:
                self.api_account_manager.increment_usage()
                self.update_api_account_display()
            
            is_pending = result.get('is_pending', False)
            data = result['data']
            
            self.process_result(data)
            
            if is_pending:
                self.status_label.setText("查询成功！快递单号有效，等待揽件中...")
                self.status_bar.showMessage("单号有效，等待揽件", 3000)
            else:
                self.status_label.setText("查询成功！")
                self.status_bar.showMessage("查询成功", 3000)
            
            self.save_query_to_history(data, result.get('quota_info', {}))
            self.add_to_summary(data)
            self.load_summary_data()
            
            if is_pending:
                QMessageBox.information(self, "添加成功", 
                    "快递单号有效，已添加到汇总。\n\n"
                    "当前状态：等待揽件\n"
                    "温馨提示：有物流更新后，可在汇总页面点击\"刷新\"按钮更新状态。")
            else:
                reply = QMessageBox.question(
                    self, "添加成功",
                    "快递已添加到汇总，是否切换到汇总标签查看？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.main_tab_widget.setCurrentIndex(0)
        else:
            # ========== 查询失败，尝试切换账号重试 ==========
            error_msg = result.get('error', '未知错误')
            
            if DEBUG_MODE:
                print(f"[查询失败]: {error_msg}")
            
            if self.api_account_manager:
                # 增加当前账号的使用次数
                self.api_account_manager.increment_usage()
                
                # 记录当前账号
                old_account = self.api_account_manager.current_account
                old_account_id = old_account.get('id') if old_account else None
                old_account_name = old_account.get('account_name', '未知') if old_account else '无'
                
                if DEBUG_MODE:
                    print(f"[查询失败] 当前账号: {old_account_name}, 尝试切换...")
                    accounts = self.api_account_manager.get_accounts()
                    print(f"[查询失败] 共有 {len(accounts)} 个账号")
                    for i, acc in enumerate(accounts):
                        print(f"[查询失败]   账号{i+1}: {acc.get('account_name', '未知')} ({acc.get('used_today', 0)}/{acc.get('daily_limit', 100)})")
                
                # 尝试切换到下一个账号（强制切换）
                if self.api_account_manager.switch_to_next_account(force_switch=True):
                    new_account = self.api_account_manager.current_account
                    new_account_id = new_account.get('id') if new_account else None
                    new_account_name = new_account.get('account_name', '未知') if new_account else '无'
                    
                    if old_account_id != new_account_id:
                        if DEBUG_MODE:
                            print(f"[查询失败] 切换到账号: {new_account_name}")
                        
                        if not self.load_current_api_account():
                            self.status_label.setText(f"查询失败：{error_msg}（切换账号失败）")
                            self.status_bar.showMessage(f"查询失败：{error_msg}（切换账号失败）", 5000)
                            QMessageBox.critical(self, "查询失败", f"错误信息：{error_msg}\n\n切换账号失败，请检查账号配置。")
                            return
                        
                        if DEBUG_MODE:
                            print(f"[账号切换后] customer: {self.customer[:10] if self.customer else 'empty'}, key: {self.key[:10] if self.key else 'empty'}")
                        
                        self.update_api_account_display()
                        usage_info = self.api_account_manager.get_usage_info()
                        
                        reply = QMessageBox.question(
                            self, "自动切换账号",
                            f"查询失败：{error_msg}\n\n"
                            f"已自动切换到备用账号：{new_account_name}\n"
                            f"新账号今日剩余次数：{usage_info['remaining']}/{usage_info['limit']}\n\n"
                            f"是否使用新账号重新查询？",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if reply == QMessageBox.Yes:
                            QTimer.singleShot(100, self.query_express)
                            return
                        else:
                            self.status_label.setText(f"查询失败：{error_msg}（已切换账号）")
                            self.status_bar.showMessage(f"查询失败：{error_msg}（已切换账号）", 5000)
                    else:
                        if DEBUG_MODE:
                            print(f"[查询失败] 切换后账号未变化: {new_account_name}")
                        self.status_label.setText(f"查询失败：{error_msg}（无可用备用账号）")
                        self.status_bar.showMessage(f"查询失败：{error_msg}（无可用备用账号）", 5000)
                        QMessageBox.critical(self, "查询失败", f"错误信息：{error_msg}\n\n没有可用的备用账号。")
                else:
                    if DEBUG_MODE:
                        print("[查询失败] switch_to_next_account 返回 False")
                    self.status_label.setText(f"查询失败：{error_msg}（无备用账号）")
                    self.status_bar.showMessage(f"查询失败：{error_msg}（无备用账号）", 5000)
                    QMessageBox.critical(self, "查询失败", f"错误信息：{error_msg}\n\n请添加备用API账号。")
            else:
                if DEBUG_MODE:
                    print("[查询失败] api_account_manager 为 None")
                self.status_label.setText(f"查询失败：{error_msg}")
                self.status_bar.showMessage(f"查询失败：{error_msg}", 5000)
                QMessageBox.critical(self, "查询失败", f"错误信息：{error_msg}")
            
    def save_query_to_history(self, data: dict, quota_info: dict):
        """保存查询到历史"""
        if self.user_manager.current_user_db:
            tracking_num = data.get('nu', '')
            company_code = data.get('com', '')
            company_name = self.get_company_name(company_code)
            state = data.get('state', '')
            state_text = self.get_state_text(state)
            
            self.user_manager.save_query_history(
                tracking_num,
                company_code,
                company_name,
                state_text,
                json.dumps(data, ensure_ascii=False),
                quota_info.get('remaining', 0)
            )
            
            if self.main_tab_widget.currentIndex() == 2:
                self.load_history()
                
    def process_result(self, data: dict):
        """处理查询结果"""
        self.display_info(data)
        self.display_track(data)
        self.display_raw(data)
        
        state = data.get('state', '')
        state_text = self.get_state_text(state)
        
        # 检查是否有物流轨迹
        track_list = data.get('data', [])
        if not track_list:
            QMessageBox.information(self, "查询成功", 
                f"快递单号有效\n当前状态：{state_text}\n\n暂无物流信息，等待揽件。")
        else:
            QMessageBox.information(self, "查询成功", f"快递状态：{state_text}")
        
    def display_info(self, data: dict):
        """显示基本信息"""
        info_items = [
            ("快递单号", data.get('nu', '未知')),
            ("快递公司", data.get('com', '未知')),
            ("快递状态", self.get_state_text(data.get('state', ''))),
            ("当前状态码", data.get('state', '未知')),
            ("是否签收", "是" if data.get('state') == '3' else "否"),
            ("最后更新", data.get('updateTime', '未知')),
            ("数据来源", data.get('condition', '未知')),
        ]
        
        for field, value in info_items:
            item = QTreeWidgetItem([field, str(value)])
            self.info_tree.addTopLevelItem(item)
            
        self.info_tree.expandAll()
        
    def display_track(self, data: dict):
        """显示物流轨迹"""
        track_list = data.get('data', [])
        
        if not track_list:
            self.track_text.append("暂无物流信息")
            self.track_text.append("\n温馨提示：")
            self.track_text.append("1. 快递单号已录入系统，等待快递员揽件")
            self.track_text.append("2. 揽件后物流信息会自动更新")
            self.track_text.append("3. 您可以在\"快递汇总\"页面点击\"刷新\"按钮手动更新")
            return
            
        for track in track_list:
            time = track.get('time', '未知时间')
            context = track.get('context', '未知信息')
            
            self.track_text.append(f"【{time}】")
            self.track_text.append(f"{context}")
            
            if track.get('status') == '签收':
                self.track_text.append("--- 已签收 ---")
                
            self.track_text.append("-" * 50)
            
    def display_raw(self, data: dict):
        """显示原始JSON数据"""
        formatted_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.raw_text.setText(formatted_json)
        
    def clear_query(self):
        """清空查询"""
        self.tracking_num.clear()
        self.clear_results()
        
    def clear_results(self):
        """清空结果"""
        self.info_tree.clear()
        self.track_text.clear()
        self.raw_text.clear()
        
    def update_quota_info(self, quota_info: dict):
        """更新配额信息"""
        try:
            daily_limit = quota_info.get('daily_limit', 0)
            remaining = quota_info.get('remaining', 0)
            
            used = max(0, daily_limit - remaining)
            usage_rate = (used / daily_limit * 100) if daily_limit > 0 else 0
            
            self.daily_limit_card.value_label.setText(str(daily_limit))
            self.remaining_card.value_label.setText(str(remaining))
            self.used_card.value_label.setText(str(used))
            self.usage_rate_card.value_label.setText(f"{usage_rate:.1f}")
            
            self.usage_bar.setValue(int(usage_rate))
            
            # 根据使用率改变进度条颜色
            if usage_rate >= 90:
                self.usage_bar.setStyleSheet(f"""
                    QProgressBar::chunk {{
                        background-color: {MacaronColors.RED_CORAL.name()};
                    }}
                """)
            elif usage_rate >= 70:
                self.usage_bar.setStyleSheet(f"""
                    QProgressBar::chunk {{
                        background-color: {MacaronColors.ORANGE_PEACH.name()};
                    }}
                """)
            else:
                self.usage_bar.setStyleSheet(f"""
                    QProgressBar::chunk {{
                        background-color: {MacaronColors.GREEN_MINT.name()};
                    }}
                """)
                
            self.quota_tree.clear()
            
            quota_items = [
                ("Customer ID", self.customer, "API客户标识"),
                ("每日总配额", daily_limit, "每天可查询的最大次数"),
                ("今日剩余次数", remaining, "今天还可以查询的次数"),
                ("今日已用", used, "今天已经使用的次数"),
                ("使用率", f"{usage_rate:.1f}%", "今日配额使用百分比"),
                ("最后查询时间", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "最后一次查询的时间"),
            ]
            
            for item in quota_items:
                tree_item = QTreeWidgetItem([str(item[0]), str(item[1]), str(item[2])])
                self.quota_tree.addTopLevelItem(tree_item)
                
            self.quota_tree.expandAll()
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"更新配额信息出错：{e}")
                
    def refresh_quota_info(self):
        """刷新配额信息"""
        thread = ExpressQueryThreadPro("TEST123", "", self.customer, self.key)
        thread.finished.connect(self.on_quota_refresh)
        thread.start()
        self.query_threads.append(thread)
        self.status_bar.showMessage("正在刷新配额信息...")
        
    def on_quota_refresh(self, result: dict):
        """配额刷新回调"""
        if result.get('quota_info'):
            self.update_quota_info(result['quota_info'])
            self.status_bar.showMessage("配额信息已刷新", 3000)
        else:
            self.status_bar.showMessage("刷新失败，请稍后重试", 3000)
            
    def load_history(self):
        """加载历史记录"""
        if not self.user_manager.current_user_db:
            return
            
        self.history_table.setRowCount(0)
        
        query = """
        SELECT * FROM express_query_history 
        ORDER BY query_time DESC 
        LIMIT 1000
        """
        
        results = self.user_manager.current_user_db.execute_query(query)
        
        self.history_table.setRowCount(len(results))
        
        for row, record in enumerate(results):
            self.history_table.setItem(row, 0, QTableWidgetItem(record['query_time']))
            self.history_table.setItem(row, 1, QTableWidgetItem(record['tracking_number']))
            self.history_table.setItem(row, 2, QTableWidgetItem(record['company_name']))
            self.history_table.setItem(row, 3, QTableWidgetItem(record['status']))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(record['quota_remaining'])))
            
            result_text = "成功" if record['result_data'] else "失败"
            self.history_table.setItem(row, 5, QTableWidgetItem(result_text))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("查看")
            view_btn.setProperty("record_data", record)
            view_btn.clicked.connect(lambda checked, r=record: self.view_history_record(r))
            btn_layout.addWidget(view_btn)
            
            requery_btn = QPushButton("重新查询")
            requery_btn.setProperty("tracking_num", record['tracking_number'])
            requery_btn.setProperty("company_code", record['company_code'])
            requery_btn.clicked.connect(
                lambda checked, num=record['tracking_number'], code=record['company_code']: 
                self.requery_from_history(num, code)
            )
            btn_layout.addWidget(requery_btn)
            
            btn_widget.setLayout(btn_layout)
            self.history_table.setCellWidget(row, 6, btn_widget)
            
        self.stats_label.setText(f"共 {len(results)} 条记录")
        self.history_table.resizeColumnsToContents()
        
    def search_history(self):
        """搜索历史"""
        search_text = self.history_search.text().strip().lower()
        
        for row in range(self.history_table.rowCount()):
            show_row = False
            
            if not search_text:
                show_row = True
            else:
                for col in range(5):
                    item = self.history_table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break
                        
            self.history_table.setRowHidden(row, not show_row)
            
    def view_history_record(self, record: dict):
        """查看历史记录"""
        if record['result_data']:
            try:
                data = json.loads(record['result_data'])
                self.main_tab_widget.setCurrentIndex(1)
                self.clear_results()
                self.process_result(data)
                self.tracking_num.setText(record['tracking_number'])
            except:
                QMessageBox.warning(self, "错误", "无法解析历史数据")
                
    def requery_from_history(self, tracking_num: str, company_code: str):
        """从历史记录重新查询"""
        self.main_tab_widget.setCurrentIndex(1)
        self.tracking_num.setText(tracking_num)
        
        for name, code in self.company_codes.items():
            if code == company_code:
                self.company_combo.setCurrentText(name)
                break
                
        self.query_express()
        
    def export_history(self):
        """导出历史记录"""
        if self.history_table.rowCount() == 0:
            QMessageBox.information(self, "提示", "没有可导出的数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出历史记录", 
            f"express_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["查询时间", "快递单号", "快递公司", "状态", "剩余配额", "结果"])
                
                for row in range(self.history_table.rowCount()):
                    if not self.history_table.isRowHidden(row):
                        row_data = []
                        for col in range(6):
                            item = self.history_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                        
            QMessageBox.information(self, "成功", f"已导出到: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
            
    def clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有查询历史吗？此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.user_manager.current_user_db:
                sql = "DELETE FROM express_query_history"
                if self.user_manager.current_user_db.execute_update(sql):
                    self.load_history()
                    QMessageBox.information(self, "成功", "历史记录已清空")
                    
    def on_global_search(self):
        """全局搜索"""
        search_text = self.global_search.text().strip()
        if not search_text:
            return
            
        self.main_tab_widget.setCurrentIndex(2)
        self.history_search.setText(search_text)
        self.search_history()
        
    def refresh_database_info(self):
        """刷新数据库信息"""
        if not self.user_manager.current_user_db:
            return
            
        size = self.user_manager.current_user_db.get_database_size()
        self.db_size_label.setText(f"{size / (1024*1024):.2f} MB")
        
        tables = self.user_manager.current_user_db.get_table_info()
        self.tables_table.setRowCount(len(tables))
        
        row = 0
        table_descriptions = {
            'express_query_history': '快递查询历史记录',
            'express_summary': '快递汇总数据',
            'api_accounts': 'API账号',
            'delivery_history': '时效历史数据',
            'user_settings': '用户设置'
        }
        
        for table_name, info in tables.items():
            self.tables_table.setItem(row, 0, QTableWidgetItem(table_name))
            self.tables_table.setItem(row, 1, QTableWidgetItem(str(info['count'])))
            self.tables_table.setItem(row, 2, QTableWidgetItem(
                table_descriptions.get(table_name, '用户数据表')
            ))
            row += 1
            
        self.tables_table.resizeColumnsToContents()
        
    def optimize_database(self):
        """优化数据库"""
        if self.user_manager.current_user_db:
            self.global_progress.setVisible(True)
            self.global_progress.setRange(0, 0)
            
            def optimize():
                self.user_manager.current_user_db.vacuum()
                self.global_progress.setVisible(False)
                self.refresh_database_info()
                QMessageBox.information(self, "成功", "数据库优化完成")
                
            QTimer.singleShot(100, optimize)
            
    def show_backup_dialog(self):
        """显示备份对话框"""
        if not self.user_manager.current_user_db:
            return
            
        dialog = BackupRestoreDialogPro(
            self.backup_manager,
            self.user_manager.current_user_db.db_path,
            self
        )
        dialog.exec()
        self.refresh_database_info()
        
    def reinitialize_database(self):
        """重新初始化数据库连接"""
        if self.user_manager.current_user_db:
            self.user_manager.current_user_db.disconnect()
            
        db_path = self.user_manager.current_user_db.db_path
        self.user_manager.current_user_db.connect(db_path)
        self.refresh_database_info()
        self.load_history()
        self.load_summary_data()
        
        QMessageBox.information(self, "成功", "数据库已重新初始化")
        
    def auto_backup(self):
        """自动备份"""
        if self.user_manager.current_user_db:
            self.backup_manager.create_backup(
                self.user_manager.current_user_db.db_path,
                "auto",
                f"自动备份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
    def switch_user(self):
        """切换用户"""
        reply = QMessageBox.question(
            self, "确认切换",
            "切换用户将关闭当前会话，确定继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_user_settings()
            self.save_window_geometry()
            self.save_category_collapse_states()
            
            for thread in self.query_threads:
                if thread.isRunning():
                    thread.quit()
                    thread.wait()
            self.query_threads.clear()
            
            if self.user_manager.current_user_db:
                self.user_manager.current_user_db.disconnect()
                
            if self.show_login_dialog():
                # 使用 ProjectInfo 更新窗口标题
                self.setWindowTitle(ProjectInfo.get_window_title(self.user_manager.current_user['username']))
                self.refresh_database_info()
                self.load_history()
                self.load_summary_data()
                self.load_user_settings()
                self.load_window_geometry()
                self.load_category_collapse_states()
                
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialogPro(self)
        dialog.exec()
            
    def load_user_settings(self):
        """加载用户设置"""
        max_backups = self.user_manager.get_user_setting("max_backups", "30")
        try:
            self.backup_manager.set_max_backups(int(max_backups))
        except:
            pass
            
        auto_backup = self.user_manager.get_user_setting("auto_backup", "true")
        if auto_backup.lower() == "true":
            self.backup_timer.start()
        else:
            self.backup_timer.stop()
            
    def save_user_settings(self):
        """保存用户设置"""
        self.user_manager.save_user_setting("max_backups", str(self.backup_manager.max_backups))
        self.user_manager.save_user_setting("auto_backup", str(self.backup_timer.isActive()).lower())
        
    def closeEvent(self, event):
        """关闭事件"""
        self.save_user_settings()
        self.save_window_geometry()
        self.save_category_collapse_states()
        
        # 停止定时器
        if hasattr(self, 'quota_reset_timer'):
            self.quota_reset_timer.stop()
        if hasattr(self, 'backup_timer'):
            self.backup_timer.stop()
        
        for thread in self.query_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.query_threads.clear()
        
        if self.user_manager.current_user_db:
            self.user_manager.current_user_db.disconnect()
            
        event.accept()

    def get_company_code_by_number(self, tracking_num: str) -> Tuple[str, str]:
        """根据单号格式自动识别快递公司"""
        tracking_num = tracking_num.strip().upper()
        
        # 快递单号识别规则（完整版）
        rules = [
            # ========== 顺丰速运 ==========
            (lambda n: n.startswith('SF') and len(n) >= 12, 'shunfeng', '顺丰速运'),
            (lambda n: len(n) == 12 and n.isdigit(), 'shunfeng', '顺丰速运'),
            (lambda n: n.startswith('SF') and n[2:].isdigit() and len(n) == 15, 'shunfeng', '顺丰速运'),
            
            # ========== 圆通速递 ==========
            (lambda n: n.startswith('YT') and len(n) >= 10, 'yuantong', '圆通速递'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '23456', 'yuantong', '圆通速递'),
            
            # ========== 中通快递 ==========
            (lambda n: n.startswith('ZT') and len(n) >= 10, 'zhongtong', '中通快递'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '78', 'zhongtong', '中通快递'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('7'), 'zhongtong', '中通快递'),
            
            # ========== 韵达快递 ==========
            (lambda n: n.startswith('YD') and len(n) >= 10, 'yunda', '韵达快递'),
            (lambda n: len(n) == 13 and n.isdigit() and n[0] in '145', 'yunda', '韵达快递'),
            
            # ========== 申通快递 ==========
            (lambda n: n.startswith('ST') and len(n) >= 10, 'shentong', '申通快递'),
            (lambda n: len(n) == 12 and n.isdigit() and n[0] in '378', 'shentong', '申通快递'),
            (lambda n: n.startswith('STO') and len(n) >= 10, 'shentong', '申通快递'),
            
            # ========== 京东物流 ==========
            (lambda n: n.startswith('JD'), 'jd', '京东物流'),
            (lambda n: n.startswith('JDV'), 'jd', '京东物流'),
            (lambda n: n.startswith('JDE'), 'jd', '京东物流'),
            (lambda n: n.startswith('JDX'), 'jd', '京东物流'),
            (lambda n: 10 <= len(n) <= 15 and n.isdigit(), 'jd', '京东物流'),
            
            # ========== EMS ==========
            (lambda n: n.startswith('EMS'), 'ems', 'EMS'),
            (lambda n: len(n) == 13 and n.isdigit() and n[:2] in ['98', '99', '10', '11', '12', '13', '14'], 'ems', 'EMS'),
            (lambda n: n.startswith('EP') and len(n) >= 10, 'ems', 'EMS'),
            
            # ========== 中国邮政 ==========
            (lambda n: n.startswith('PA') and len(n) >= 10, 'youzhengguo', '中国邮政'),
            (lambda n: n.startswith('KA') and len(n) >= 10, 'youzhengguo', '中国邮政'),
            (lambda n: n.startswith('SA') and len(n) >= 10, 'youzhengguo', '中国邮政'),
            (lambda n: n.startswith('XA') and len(n) >= 10, 'youzhengguo', '中国邮政'),
            (lambda n: len(n) == 13 and n.isdigit() and n.startswith('9'), 'youzhengguo', '中国邮政'),
            
            # ========== 极兔速递 ==========
            (lambda n: n.startswith('JT') and len(n) >= 10, 'jtexpress', '极兔速递'),
            (lambda n: n.startswith('J&T') and len(n) >= 10, 'jtexpress', '极兔速递'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit(), 'jtexpress', '极兔速递'),
            
            # ========== 百世快递 ==========
            (lambda n: n.startswith('B') and len(n) >= 10, 'huitongkuaidi', '百世快递'),
            (lambda n: n.startswith('H') and len(n) >= 10, 'huitongkuaidi', '百世快递'),
            (lambda n: n.startswith('HT') and len(n) >= 10, 'huitongkuaidi', '百世快递'),
            (lambda n: n.startswith('BEST') and len(n) >= 10, 'huitongkuaidi', '百世快递'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('0'), 'huitongkuaidi', '百世快递'),
            
            # ========== 德邦快递 ==========
            (lambda n: n.startswith('DPK') and len(n) >= 10, 'debangwuliu', '德邦快递'),
            (lambda n: n.startswith('DP') and len(n) >= 10, 'debangwuliu', '德邦快递'),
            (lambda n: len(n) >= 8 and len(n) <= 12 and n.isdigit() and n[0] in '56789', 'debangwuliu', '德邦快递'),
            
            # ========== 天天快递 ==========
            (lambda n: n.startswith('TT') and len(n) >= 10, 'tiantian', '天天快递'),
            (lambda n: 12 <= len(n) <= 14 and n.isdigit(), 'tiantian', '天天快递'),
            
            # ========== 宅急送 ==========
            (lambda n: n.startswith('ZJS') and len(n) >= 10, 'zhaijisong', '宅急送'),
            (lambda n: 10 <= len(n) <= 12 and n.isdigit(), 'zhaijisong', '宅急送'),
            
            # ========== 优速快递 ==========
            (lambda n: n.startswith('UC') and len(n) >= 10, 'youshuwuliu', '优速快递'),
            (lambda n: n.startswith('YS') and len(n) >= 10, 'youshuwuliu', '优速快递'),
            
            # ========== 跨越速运 ==========
            (lambda n: n.startswith('KY') and len(n) >= 10, 'kuayue', '跨越速运'),
            (lambda n: n.startswith('KYE') and len(n) >= 10, 'kuayue', '跨越速运'),
            
            # ========== 速尔快递 ==========
            (lambda n: n.startswith('SR') and len(n) >= 10, 'suer', '速尔快递'),
            
            # ========== 联邦快递 ==========
            (lambda n: n.startswith('FX') and len(n) >= 10, 'fedex', '联邦快递'),
            (lambda n: len(n) == 12 and n.isdigit(), 'fedex', '联邦快递'),
            
            # ========== DHL ==========
            (lambda n: len(n) == 10 and n.isdigit(), 'dhl', 'DHL'),
            (lambda n: n.isdigit() and len(n) >= 10 and len(n) <= 14, 'dhl', 'DHL'),
            
            # ========== UPS ==========
            (lambda n: n.startswith('1Z') and len(n) >= 18, 'ups', 'UPS'),
            (lambda n: n.startswith('1Z') and len(n) == 18, 'ups', 'UPS'),
            (lambda n: n.startswith('K') and len(n) == 11, 'ups', 'UPS'),
            
            # ========== TNT ==========
            (lambda n: len(n) == 9 and n.isdigit(), 'tnt', 'TNT'),
            (lambda n: n.isdigit() and len(n) >= 9 and len(n) <= 15, 'tnt', 'TNT'),
            
            # ========== USPS ==========
            (lambda n: len(n) == 22 and n.isdigit(), 'usps', 'USPS'),
            (lambda n: len(n) == 20 and n.isdigit(), 'usps', 'USPS'),
            (lambda n: len(n) == 26 and n.isdigit(), 'usps', 'USPS'),
            (lambda n: n.startswith('EC') and len(n) >= 13, 'usps', 'USPS'),
            (lambda n: n.startswith('CP') and len(n) >= 13, 'usps', 'USPS'),
            (lambda n: n.startswith('92') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('93') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('94') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('95') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('96') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('97') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('98') and len(n) >= 22, 'usps', 'USPS'),
            (lambda n: n.startswith('99') and len(n) >= 22, 'usps', 'USPS'),
            
            # ========== 亚马逊物流 ==========
            (lambda n: n.startswith('TBA') and len(n) >= 10, 'amazon', '亚马逊物流'),
            (lambda n: n.startswith('AMZN') and len(n) >= 10, 'amazon', '亚马逊物流'),
            
            # ========== 菜鸟裹裹 ==========
            (lambda n: n.startswith('CN') and len(n) >= 10, 'cainiao', '菜鸟裹裹'),
            
            # ========== 丹鸟物流 ==========
            (lambda n: n.startswith('DN') and len(n) >= 10, 'danniao', '丹鸟物流'),
            
            # ========== 安能物流 ==========
            (lambda n: n.startswith('AN') and len(n) >= 10, 'annengwuliu', '安能物流'),
            (lambda n: n.startswith('ANE') and len(n) >= 10, 'annengwuliu', '安能物流'),
            
            # ========== 壹米滴答 ==========
            (lambda n: n.startswith('YM') and len(n) >= 10, 'yimidida', '壹米滴答'),
            (lambda n: n.startswith('YMD') and len(n) >= 10, 'yimidida', '壹米滴答'),
            
            # ========== 全峰快递 ==========
            (lambda n: n.startswith('QF') and len(n) >= 10, 'quanfengkuaidi', '全峰快递'),
            
            # ========== 国通快递 ==========
            (lambda n: n.startswith('GT') and len(n) >= 10, 'guotongkuaidi', '国通快递'),
            
            # ========== 快捷快递 ==========
            (lambda n: n.startswith('KJ') and len(n) >= 10, 'kuaijiesudi', '快捷快递'),
            
            # ========== 如风达 ==========
            (lambda n: n.startswith('RF') and len(n) >= 10, 'rufengda', '如风达'),
            
            # ========== 信丰物流 ==========
            (lambda n: n.startswith('XF') and len(n) >= 10, 'xinfengwuliu', '信丰物流'),
        ]
        
        for check, code, name in rules:
            try:
                if check(tracking_num):
                    return code, name
            except:
                continue
                
        return "", ""

    def update_api_account_display(self):
        """更新API账号显示"""
        if hasattr(self, 'api_account_label') and self.api_account_manager:
            account = self.api_account_manager.get_current_account()
            if account:
                account_name = account.get('account_name', '未知')
                used = account.get('used_today', 0)
                limit = account.get('daily_limit', 100)
                
                # 显示更详细的信息
                self.api_account_label.setText(
                    f" | 🔑 API账号: {account_name} ({used}/{limit})"
                )
                
                # 同时更新状态栏提示（使用 statusBar() 方法获取状态栏）
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage(f"当前使用API账号: {account_name}", 2000)
            else:
                self.api_account_label.setText(" | 🔑 API账号: 无")
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage("警告：未配置API账号，无法查询快递", 3000)

class SettingsDialogPro(QDialog):
    """设置对话框"""
    
    def __init__(self, parent: ExpressQueryProGUI):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("系统设置")
        self.setMinimumSize(500, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # API账号管理
        account_group = QGroupBox("API账号管理")
        account_layout = QVBoxLayout()
        
        account_info_label = QLabel("管理多个API账号，支持额度用完自动切换")
        account_layout.addWidget(account_info_label)
        
        manage_account_btn = QPushButton("管理API账号")
        manage_account_btn.clicked.connect(self.manage_accounts)
        account_layout.addWidget(manage_account_btn)
        
        account_group.setLayout(account_layout)
        layout.addWidget(account_group)
        
        # 时效数据管理
        delivery_group = QGroupBox("时效数据管理")
        delivery_layout = QVBoxLayout()
        
        delivery_info_label = QLabel("基于历史签收数据预估送达时间")
        delivery_layout.addWidget(delivery_info_label)
        
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("加载中...")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        delivery_layout.addLayout(stats_layout)
        
        clear_history_btn = QPushButton("清空时效历史数据")
        clear_history_btn.clicked.connect(self.clear_delivery_history)
        delivery_layout.addWidget(clear_history_btn)
        
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)
        
        # 备份设置
        backup_group = QGroupBox("备份设置")
        backup_layout = QVBoxLayout()
        
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大备份数量:"))
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        self.max_backups_spin.setValue(self.parent.backup_manager.max_backups)
        max_layout.addWidget(self.max_backups_spin)
        max_layout.addStretch()
        backup_layout.addLayout(max_layout)
        
        self.auto_backup_check = QCheckBox("启用自动备份（每小时）")
        self.auto_backup_check.setChecked(self.parent.backup_timer.isActive())
        backup_layout.addWidget(self.auto_backup_check)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("备份目录:"))
        self.dir_label = QLabel(str(self.parent.backup_manager.backup_dir))
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        backup_layout.addLayout(dir_layout)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # 调试模式
        debug_layout = QHBoxLayout()
        self.debug_check = QCheckBox("启用调试模式")
        self.debug_check.setChecked(DEBUG_MODE)
        debug_layout.addWidget(self.debug_check)
        debug_layout.addStretch()
        layout.addLayout(debug_layout)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.load_delivery_stats()
        
    def load_delivery_stats(self):
        """加载时效统计"""
        if self.parent.current_user_db:
            sql = "SELECT COUNT(*) as count FROM delivery_history"
            result = self.parent.current_user_db.execute_query(sql)
            if result:
                count = result[0]['count']
                self.stats_label.setText(f"已记录 {count} 条时效数据")
                
    def clear_delivery_history(self):
        """清空时效历史数据"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有时效历史数据吗？\n清空后预估功能将使用默认值。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.parent.current_user_db:
                sql = "DELETE FROM delivery_history"
                self.parent.current_user_db.execute_update(sql)
                self.load_delivery_stats()
                QMessageBox.information(self, "成功", "时效历史数据已清空")
        
    def manage_accounts(self):
        """管理API账号"""
        if self.parent.current_user_db:
            dialog = ApiAccountDialog(self.parent.current_user_db, self)
            if dialog.exec() == QDialog.Accepted:
                if self.parent.api_account_manager:
                    # ========== 确保刷新 ==========
                    self.parent.api_account_manager.load_accounts()
                    self.parent.load_current_api_account()
                    self.parent.update_api_account_display()
                    # ============================
        else:
            QMessageBox.warning(self, "提示", "数据库未连接")
            
    def save_settings(self):
        """保存设置"""
        self.parent.backup_manager.set_max_backups(self.max_backups_spin.value())
        self.parent.user_manager.save_user_setting("max_backups", str(self.max_backups_spin.value()))
        
        auto_backup = self.auto_backup_check.isChecked()
        if auto_backup:
            self.parent.backup_timer.start()
        else:
            self.parent.backup_timer.stop()
        self.parent.user_manager.save_user_setting("auto_backup", str(auto_backup).lower())
        
        global DEBUG_MODE
        DEBUG_MODE = self.debug_check.isChecked()
        
        QMessageBox.information(self, "成功", "设置已保存")

class BatchImportDialog(QDialog):
    """批量导入快递单号对话框"""
    
    def __init__(self, company_codes: dict, parent=None):
        super().__init__(parent)
        self.company_codes = company_codes
        self.imported_numbers = []
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle("批量导入快递单号")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 导入方式选择
        method_group = QGroupBox("导入方式")
        method_layout = QVBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["从文件导入", "粘贴多行文本", "手动输入（每行一个）"])
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # 文件导入区域
        self.file_widget = QWidget()
        file_layout = QVBoxLayout(self.file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        file_select_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择包含快递单号的文件...")
        self.file_path_edit.setReadOnly(True)
        file_select_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_file)
        file_select_layout.addWidget(browse_btn)
        
        file_layout.addLayout(file_select_layout)
        
        file_tip = QLabel("支持格式：TXT、CSV、文本文件，每行一个快递单号")
        file_tip.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px;")
        file_layout.addWidget(file_tip)
        
        layout.addWidget(self.file_widget)
        
        # 文本输入区域
        self.text_widget = QWidget()
        self.text_widget.setVisible(False)
        text_layout = QVBoxLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        text_label = QLabel("请输入快递单号（每行一个，或使用分隔符分隔）：")
        text_layout.addWidget(text_label)
        
        # 分隔符设置
        separator_layout = QHBoxLayout()
        separator_layout.addWidget(QLabel("分隔符："))
        
        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["换行（默认）", "逗号 ,", "空格", "分号 ;", "制表符", "自定义..."])
        self.separator_combo.currentIndexChanged.connect(self.on_separator_changed)
        separator_layout.addWidget(self.separator_combo)
        
        self.custom_separator_edit = QLineEdit()
        self.custom_separator_edit.setPlaceholderText("输入自定义分隔符")
        self.custom_separator_edit.setMaximumWidth(100)
        self.custom_separator_edit.setVisible(False)
        separator_layout.addWidget(self.custom_separator_edit)
        
        separator_layout.addStretch()
        text_layout.addLayout(separator_layout)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("例如：\nYT1234567890\nSF1234567890\nJD1234567890\n\n或使用逗号分隔：\nYT1234567890,SF1234567890,JD1234567890")
        self.text_edit.setMinimumHeight(200)
        text_layout.addWidget(self.text_edit)
        
        # 预览按钮
        preview_btn = QPushButton("预览解析结果")
        preview_btn.clicked.connect(self.preview_numbers)
        text_layout.addWidget(preview_btn)
        
        layout.addWidget(self.text_widget)
        
        # 快递公司选择
        company_group = QGroupBox("快递公司设置")
        company_layout = QHBoxLayout()
        
        company_layout.addWidget(QLabel("默认快递公司："))
        
        self.company_combo = QComboBox()
        self.company_combo.addItems(list(self.company_codes.keys()))
        self.company_combo.setCurrentText("自动识别")
        company_layout.addWidget(self.company_combo)
        
        company_layout.addStretch()
        
        self.auto_detect_check = QCheckBox("启用自动识别（单号格式识别）")
        self.auto_detect_check.setChecked(True)
        self.auto_detect_check.setToolTip("根据单号格式自动识别快递公司，仅对支持的单号格式有效")
        company_layout.addWidget(self.auto_detect_check)
        
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        # 预览区域
        preview_group = QGroupBox("待导入单号预览")
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["序号", "快递单号", "快递公司", "状态"])
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        preview_layout.addWidget(self.preview_table)
        
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("共 0 个单号")
        stats_layout.addWidget(self.stats_label)
        
        self.valid_count_label = QLabel("有效：0")
        stats_layout.addWidget(self.valid_count_label)
        
        self.duplicate_count_label = QLabel("重复：0")
        stats_layout.addWidget(self.duplicate_count_label)
        
        stats_layout.addStretch()
        preview_layout.addLayout(stats_layout)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.parse_btn = QPushButton("解析单号")
        self.parse_btn.clicked.connect(self.parse_numbers)
        btn_layout.addWidget(self.parse_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        self.import_btn = QPushButton("开始导入")
        self.import_btn.clicked.connect(self.accept)
        self.import_btn.setEnabled(False)
        self.import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
            }}
        """)
        btn_layout.addWidget(self.import_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def on_method_changed(self, index: int):
        """切换导入方式"""
        self.file_widget.setVisible(index == 0)
        self.text_widget.setVisible(index != 0)
        
        # 更新分隔符选项
        if index == 1:  # 粘贴多行文本
            self.separator_combo.setCurrentText("换行（默认）")
        elif index == 2:  # 手动输入
            self.separator_combo.setCurrentText("换行（默认）")
            
    def on_separator_changed(self, index: int):
        """分隔符改变"""
        self.custom_separator_edit.setVisible(index == 5)
        
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择快递单号文件", "",
            "文本文件 (*.txt *.csv *.log);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_file_content(file_path)
            
    def load_file_content(self, file_path: str):
        """加载文件内容"""
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'gb18030']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
                    
            if content is None:
                QMessageBox.warning(self, "错误", "无法识别文件编码，请确保文件为文本格式")
                return
                
            # 切换到文本输入模式显示内容
            self.method_combo.setCurrentIndex(1)
            self.text_edit.setText(content)
            
            # 自动解析 - 增加延迟确保UI更新
            QTimer.singleShot(200, self.parse_numbers)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取文件失败：{e}")
            
    def get_separator(self) -> Optional[str]:
        """获取当前分隔符"""
        index = self.separator_combo.currentIndex()
        separators = {
            0: '\n',      # 换行
            1: ',',       # 逗号
            2: ' ',       # 空格
            3: ';',       # 分号
            4: '\t',      # 制表符
            5: self.custom_separator_edit.text()  # 自定义
        }
        return separators.get(index)
        
    def detect_company_by_number(self, tracking_num: str) -> str:
        """根据单号格式自动识别快递公司"""
        tracking_num = tracking_num.strip().upper()
        
        # 快递单号识别规则（完整版）
        rules = [
            # ========== 顺丰速运 ==========
            # SF开头 + 12位数字，或纯12位数字
            (lambda n: n.startswith('SF') and len(n) >= 12, 'shunfeng'),
            (lambda n: len(n) == 12 and n.isdigit(), 'shunfeng'),
            (lambda n: n.startswith('SF') and n[2:].isdigit() and len(n) == 15, 'shunfeng'),
            
            # ========== 圆通速递 ==========
            # YT开头，或10-18位纯数字（常见以2、3、4、5、6开头）
            (lambda n: n.startswith('YT') and len(n) >= 10, 'yuantong'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '23456', 'yuantong'),
            (lambda n: n.startswith('YT') and n[2:].isdigit(), 'yuantong'),
            
            # ========== 中通快递 ==========
            # ZT开头，或10-18位数字（常见以7、8开头）
            (lambda n: n.startswith('ZT') and len(n) >= 10, 'zhongtong'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '78', 'zhongtong'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('7'), 'zhongtong'),
            (lambda n: len(n) == 14 and n.isdigit() and n.startswith('8'), 'zhongtong'),
            
            # ========== 韵达快递 ==========
            # YD开头，或13位数字（常见以1、4、5开头）
            (lambda n: n.startswith('YD') and len(n) >= 10, 'yunda'),
            (lambda n: len(n) == 13 and n.isdigit() and n[0] in '145', 'yunda'),
            (lambda n: n.startswith('YD') and n[2:].isdigit(), 'yunda'),
            (lambda n: len(n) == 15 and n.isdigit() and n.startswith('5'), 'yunda'),
            
            # ========== 申通快递 ==========
            # ST开头，或12位数字（常见以3、7、8开头）
            (lambda n: n.startswith('ST') and len(n) >= 10, 'shentong'),
            (lambda n: len(n) == 12 and n.isdigit() and n[0] in '378', 'shentong'),
            (lambda n: n.startswith('STO') and len(n) >= 10, 'shentong'),
            (lambda n: len(n) == 13 and n.isdigit() and n.startswith('77'), 'shentong'),
            
            # ========== 京东物流 ==========
            # JD开头，或JDV/JDE开头，或10-15位数字
            (lambda n: n.startswith('JD'), 'jd'),
            (lambda n: n.startswith('JDV'), 'jd'),
            (lambda n: n.startswith('JDE'), 'jd'),
            (lambda n: n.startswith('JDX'), 'jd'),
            (lambda n: n.startswith('JD') and len(n) >= 10, 'jd'),
            (lambda n: 10 <= len(n) <= 15 and n.isdigit() and n[0] in '0123456789', 'jd'),
            
            # ========== EMS/中国邮政 ==========
            # EMS开头，或13位数字（常见以9、10、11、12开头）
            (lambda n: n.startswith('EMS'), 'ems'),
            (lambda n: len(n) == 13 and n.isdigit() and n[:2] in ['98', '99', '10', '11', '12', '13', '14'], 'ems'),
            (lambda n: n.startswith('EP') and len(n) >= 10, 'ems'),
            (lambda n: n.startswith('EL') and len(n) >= 10, 'ems'),
            
            # ========== 中国邮政（国内） ==========
            (lambda n: n.startswith('PA') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('KA') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('SA') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XA') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XB') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XC') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XD') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XE') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XF') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XG') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('XH') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('PH') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('PK') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('AA') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('AB') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('AC') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('AD') and len(n) >= 10, 'youzhengguo'),
            (lambda n: n.startswith('AE') and len(n) >= 10, 'youzhengguo'),
            (lambda n: len(n) == 13 and n.isdigit() and n.startswith('9'), 'youzhengguo'),
            
            # ========== 极兔速递 ==========
            # JT开头，或10-15位数字
            (lambda n: n.startswith('JT') and len(n) >= 10, 'jtexpress'),
            (lambda n: n.startswith('J&T') and len(n) >= 10, 'jtexpress'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '0123456789', 'jtexpress'),
            
            # ========== 百世快递 ==========
            # 以B、H开头，或百世专用格式
            (lambda n: n.startswith('B') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: n.startswith('H') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: n.startswith('HT') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: n.startswith('BEST') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('0'), 'huitongkuaidi'),
            (lambda n: len(n) == 14 and n.isdigit() and n.startswith('3'), 'huitongkuaidi'),
            
            # ========== 德邦快递 ==========
            # DPK开头，或以DP开头
            (lambda n: n.startswith('DPK') and len(n) >= 10, 'debangwuliu'),
            (lambda n: n.startswith('DP') and len(n) >= 10, 'debangwuliu'),
            (lambda n: n.startswith('DEBANG') and len(n) >= 10, 'debangwuliu'),
            (lambda n: len(n) >= 8 and len(n) <= 12 and n.isdigit() and n[0] in '56789', 'debangwuliu'),
            
            # ========== 天天快递 ==========
            # TT开头，或12-14位数字
            (lambda n: n.startswith('TT') and len(n) >= 10, 'tiantian'),
            (lambda n: n.startswith('TTK') and len(n) >= 10, 'tiantian'),
            (lambda n: 12 <= len(n) <= 14 and n.isdigit() and n[0] in '0123456789', 'tiantian'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('6'), 'tiantian'),
            
            # ========== 宅急送 ==========
            (lambda n: n.startswith('ZJS') and len(n) >= 10, 'zhaijisong'),
            (lambda n: 10 <= len(n) <= 12 and n.isdigit() and n[0] in '0123456789', 'zhaijisong'),
            
            # ========== 优速快递 ==========
            (lambda n: n.startswith('UC') and len(n) >= 10, 'youshuwuliu'),
            (lambda n: n.startswith('YS') and len(n) >= 10, 'youshuwuliu'),
            (lambda n: 12 <= len(n) <= 15 and n.isdigit() and n.startswith('9'), 'youshuwuliu'),
            
            # ========== 跨越速运 ==========
            (lambda n: n.startswith('KY') and len(n) >= 10, 'kuayue'),
            (lambda n: n.startswith('KYE') and len(n) >= 10, 'kuayue'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('8'), 'kuayue'),
            
            # ========== 速尔快递 ==========
            (lambda n: n.startswith('SR') and len(n) >= 10, 'suer'),
            (lambda n: n.startswith('SURE') and len(n) >= 10, 'suer'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('4'), 'suer'),
            
            # ========== 全峰快递 ==========
            (lambda n: n.startswith('QF') and len(n) >= 10, 'quanfengkuaidi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('2'), 'quanfengkuaidi'),
            
            # ========== 国通快递 ==========
            (lambda n: n.startswith('GT') and len(n) >= 10, 'guotongkuaidi'),
            (lambda n: len(n) == 10 and n.isdigit() and n.startswith('3'), 'guotongkuaidi'),
            
            # ========== 快捷快递 ==========
            (lambda n: n.startswith('KJ') and len(n) >= 10, 'kuaijiesudi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('1'), 'kuaijiesudi'),
            
            # ========== 龙邦快递 ==========
            (lambda n: n.startswith('LB') and len(n) >= 10, 'longbanwuliu'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('8'), 'longbanwuliu'),
            
            # ========== 信丰物流 ==========
            (lambda n: n.startswith('XF') and len(n) >= 10, 'xinfengwuliu'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('5'), 'xinfengwuliu'),
            
            # ========== 增益快递 ==========
            (lambda n: n.startswith('ZY') and len(n) >= 10, 'zengyikuaidi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('7'), 'zengyikuaidi'),
            
            # ========== 联昊通 ==========
            (lambda n: n.startswith('LH') and len(n) >= 10, 'lianhaowuliu'),
            (lambda n: n.startswith('LHT') and len(n) >= 10, 'lianhaowuliu'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('9'), 'lianhaowuliu'),
            
            # ========== 全一快递 ==========
            (lambda n: n.startswith('QY') and len(n) >= 10, 'quanyikuaidi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('0'), 'quanyikuaidi'),
            
            # ========== 如风达 ==========
            (lambda n: n.startswith('RF') and len(n) >= 10, 'rufengda'),
            (lambda n: n.startswith('RFD') and len(n) >= 10, 'rufengda'),
            (lambda n: len(n) == 15 and n.isdigit(), 'rufengda'),
            
            # ========== 联邦快递 ==========
            (lambda n: n.startswith('FX') and len(n) >= 10, 'fedex'),
            (lambda n: len(n) == 12 and n.isdigit() and n[0] in '0123456789', 'fedex'),
            (lambda n: any(c.isalpha() for c in n) and len(n) == 12, 'fedex'),
            
            # ========== DHL ==========
            (lambda n: len(n) == 10 and n.isdigit(), 'dhl'),
            (lambda n: len(n) == 12 and n.isdigit(), 'dhl'),
            (lambda n: n.isdigit() and len(n) >= 10 and len(n) <= 14, 'dhl'),
            
            # ========== UPS ==========
            (lambda n: n.startswith('1Z') and len(n) >= 18, 'ups'),
            (lambda n: n.startswith('1Z') and len(n) == 18, 'ups'),
            (lambda n: n.startswith('K') and len(n) == 11, 'ups'),
            (lambda n: len(n) == 9 and n.isdigit(), 'ups'),
            (lambda n: len(n) == 12 and n.isalpha(), 'ups'),
            
            # ========== TNT ==========
            (lambda n: len(n) == 9 and n.isdigit(), 'tnt'),
            (lambda n: len(n) == 13 and n.isdigit(), 'tnt'),
            (lambda n: n.isdigit() and len(n) >= 9 and len(n) <= 15, 'tnt'),
            
            # ========== USPS ==========
            (lambda n: len(n) == 22 and n.isdigit(), 'usps'),
            (lambda n: len(n) == 20 and n.isdigit(), 'usps'),
            (lambda n: len(n) == 26 and n.isdigit(), 'usps'),
            (lambda n: len(n) == 30 and n.isdigit(), 'usps'),
            (lambda n: n.startswith('EC') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('CP') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('RA') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LC') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LJ') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LK') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LM') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LN') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LP') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LQ') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LR') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LS') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LT') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LU') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LV') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LW') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LX') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LY') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('LZ') and len(n) >= 13, 'usps'),
            (lambda n: n.startswith('UA') and len(n) >= 9, 'usps'),
            (lambda n: n.startswith('92') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('93') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('94') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('95') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('96') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('97') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('98') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('99') and len(n) >= 22, 'usps'),
            (lambda n: n.startswith('82') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('83') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('84') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('85') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('86') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('87') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('88') and len(n) >= 10, 'usps'),
            (lambda n: n.startswith('89') and len(n) >= 10, 'usps'),
            
            # ========== 亚马逊物流 ==========
            (lambda n: n.startswith('TBA') and len(n) >= 10, 'amazon'),
            (lambda n: n.startswith('TBC') and len(n) >= 10, 'amazon'),
            (lambda n: n.startswith('TBM') and len(n) >= 10, 'amazon'),
            (lambda n: n.startswith('AMZ') and len(n) >= 10, 'amazon'),
            (lambda n: n.startswith('AMZN') and len(n) >= 10, 'amazon'),
            (lambda n: len(n) == 14 and n.isdigit() and n.startswith('0'), 'amazon'),
            
            # ========== 菜鸟裹裹 ==========
            (lambda n: n.startswith('CN') and len(n) >= 10, 'cainiao'),
            (lambda n: n.startswith('CAINIAO') and len(n) >= 10, 'cainiao'),
            (lambda n: len(n) == 16 and n.isdigit() and n.startswith('9'), 'cainiao'),
            
            # ========== 丹鸟物流 ==========
            (lambda n: n.startswith('DN') and len(n) >= 10, 'danniao'),
            (lambda n: len(n) == 15 and n.isdigit() and n.startswith('6'), 'danniao'),
            
            # ========== 安能物流 ==========
            (lambda n: n.startswith('AN') and len(n) >= 10, 'annengwuliu'),
            (lambda n: n.startswith('ANE') and len(n) >= 10, 'annengwuliu'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('2'), 'annengwuliu'),
            (lambda n: len(n) == 13 and n.isdigit() and n.startswith('3'), 'annengwuliu'),
            
            # ========== 壹米滴答 ==========
            (lambda n: n.startswith('YM') and len(n) >= 10, 'yimidida'),
            (lambda n: n.startswith('YMD') and len(n) >= 10, 'yimidida'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('4'), 'yimidida'),
            
            # ========== 德坤物流 ==========
            (lambda n: n.startswith('DK') and len(n) >= 10, 'dekunwuliu'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('5'), 'dekunwuliu'),
            
            # ========== 中铁快运 ==========
            (lambda n: n.startswith('ZT') and len(n) >= 10, 'zhongtiewuliu'),
            (lambda n: n.startswith('CRE') and len(n) >= 10, 'zhongtiewuliu'),
            (lambda n: len(n) == 10 and n.isdigit() and n.startswith('K'), 'zhongtiewuliu'),
            
            # ========== 民航快递 ==========
            (lambda n: n.startswith('CA') and len(n) >= 10, 'minhangkuaidi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('6'), 'minhangkuaidi'),
            
            # ========== 运通中港 ==========
            (lambda n: n.startswith('YT') and 'HK' in n, 'yuntongkuaidi'),
            
            # ========== 泛捷国际 ==========
            (lambda n: n.startswith('FJ') and len(n) >= 10, 'fanjiekuaidi'),
            
            # ========== 新顺丰（国际） ==========
            (lambda n: n.startswith('XSF') and len(n) >= 10, 'xinshunfeng'),
        ]
        
        for check, code in rules:
            try:
                if check(tracking_num):
                    return code
            except:
                continue
                
        return ""
        
    def get_company_name_by_code(self, code: str) -> str:
        """根据代码获取公司名称"""
        for name, c in self.company_codes.items():
            if c == code:
                return name
        return "未知"
        
    def parse_numbers(self):
        """解析单号 - 支持快递公司名称+单号的混合格式"""
        method = self.method_combo.currentIndex()
        
        if method == 0:  # 文件导入
            file_path = self.file_path_edit.text().strip()
            if not file_path:
                QMessageBox.warning(self, "提示", "请先选择文件")
                return
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "提示", "文件不存在")
                return
            self.load_file_content(file_path)
            return
            
        # 文本导入
        content = self.text_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "提示", "请输入快递单号")
            return
            
        separator = self.get_separator()
        if not separator:
            QMessageBox.warning(self, "提示", "请输入自定义分隔符")
            return
            
        # 分割内容
        if separator == '\n':
            # 按行分割
            lines = content.split('\n')
            raw_items = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                raw_items.append(line)
        else:
            # 按指定分隔符分割
            raw_items = [n.strip() for n in content.split(separator) if n.strip()]
        
        # 解析每行内容，提取单号和预识别的公司
        numbers = []
        pre_recognized_companies = {}  # 单号 -> 预识别的公司代码
        
        # 常见快递公司名称关键词映射（只保留中文关键词，避免误判）
        company_keywords = {
            'shunfeng': ['顺丰', '顺丰速运'],
            'yuantong': ['圆通', '圆通速递'],
            'zhongtong': ['中通', '中通快递'],
            'yunda': ['韵达', '韵达快递'],
            'shentong': ['申通', '申通快递'],
            'jd': ['京东', '京东物流'],
            'youzhengguo': ['邮政', '中国邮政', '邮政快递'],
            'ems': ['EMS', '邮政速递'],
            'jtexpress': ['极兔', '极兔速递'],
            'huitongkuaidi': ['百世', '百世快递'],
            'debangwuliu': ['德邦', '德邦快递'],
            'tiantian': ['天天', '天天快递'],
            'zhaijisong': ['宅急送'],
            'youshuwuliu': ['优速', '优速快递'],
            'kuayue': ['跨越', '跨越速运'],
            'suer': ['速尔', '速尔快递'],
            'cainiao': ['菜鸟', '菜鸟裹裹', '菜鸟速递'],
            'danniao': ['丹鸟', '丹鸟物流'],
            'annengwuliu': ['安能', '安能物流'],
            'yimidida': ['壹米', '壹米滴答'],
            'fedex': ['联邦', '联邦快递'],
            'dhl': ['DHL'],
            'ups': ['UPS'],
            'tnt': ['TNT'],
            'usps': ['USPS'],
            'amazon': ['亚马逊'],
        }
        
        for item in raw_items:
            extracted_num = None
            pre_company = None
            
            # 先检查是否包含已知的快递公司关键词（只检查中文关键词）
            for company_code, keywords in company_keywords.items():
                for keyword in keywords:
                    # 检查关键词是否在字符串中
                    idx = item.find(keyword)
                    if idx >= 0:
                        pre_company = company_code
                        # 移除关键词部分，提取可能的单号
                        remaining = item[:idx] + item[idx + len(keyword):]
                        remaining = remaining.strip()
                        if remaining:
                            # 检查剩余部分是否看起来像单号
                            if len(remaining) >= 6:
                                extracted_num = remaining
                        break
                if extracted_num:
                    break
            
            # 如果没有通过关键词找到，尝试提取单号
            if not extracted_num:
                # 按空格分割，找出最像单号的部分
                parts = item.split()
                for part in parts:
                    part = part.strip()
                    # 检查是否像快递单号（长度>=6，包含字母或数字）
                    if len(part) >= 6 and any(c.isalnum() for c in part):
                        # 确保不是纯中文
                        if not all('\u4e00' <= c <= '\u9fff' for c in part):
                            extracted_num = part
                            break
                
                # 如果还是没找到，检查整个字符串
                if not extracted_num:
                    # 移除所有空格和中文字符
                    cleaned = re.sub(r'[\s\u4e00-\u9fff]+', '', item)
                    if len(cleaned) >= 6:
                        extracted_num = cleaned
                    else:
                        extracted_num = item
            
            # 清理单号
            if extracted_num:
                # 移除中文和特殊字符
                extracted_num = re.sub(r'[\u4e00-\u9fff\s]+', '', extracted_num)
                extracted_num = extracted_num.strip()
                
                # 提取字母数字部分
                alnum_part = ''.join(c for c in extracted_num if c.isalnum())
                if len(alnum_part) >= 6:
                    extracted_num = alnum_part
                
                if extracted_num and len(extracted_num) >= 6:
                    numbers.append(extracted_num)
                    if pre_company:
                        pre_recognized_companies[extracted_num] = pre_company
        
        # 去重并保持顺序
        seen = set()
        unique_numbers = []
        for num in numbers:
            if num not in seen:
                seen.add(num)
                unique_numbers.append(num)
                
        # 默认公司
        default_company_name = self.company_combo.currentText()
        default_company_code = self.company_codes.get(default_company_name, "")
        auto_detect = self.auto_detect_check.isChecked()
        
        # 更新预览表格
        self.preview_table.setRowCount(len(unique_numbers))
        
        self.imported_numbers = []
        valid_count = 0
        duplicate_warning = len(numbers) - len(unique_numbers)
        
        for row, num in enumerate(unique_numbers):
            self.preview_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.preview_table.setItem(row, 1, QTableWidgetItem(num))
            
            # 确定快递公司 - 关键修改：不确定时使用空字符串让API自动识别
            company_code = ""
            company_name = "自动识别"
            status = "API自动"
            status_color = QColor(100, 100, 100)
            
            # 优先使用从文本中识别的公司（这是最可靠的）
            if num in pre_recognized_companies:
                company_code = pre_recognized_companies[num]
                company_name = self.get_company_name_by_code(company_code)
                status = "从文本识别"
                status_color = QColor(0, 100, 200)
            elif auto_detect:
                # 只有当单号有明显特征时才自动识别
                # 对于纯数字单号，如果没有文本识别，就留空让API自动判断
                detected_code = self.detect_company_by_number(num)
                if detected_code:
                    company_code = detected_code
                    company_name = self.get_company_name_by_code(detected_code)
                    status = "格式识别"
                    status_color = QColor(0, 150, 0)
                else:
                    # 无法识别，使用空字符串让API自动判断
                    company_code = ""
                    company_name = "自动识别"
                    status = "API自动"
                    status_color = QColor(100, 100, 100)
            else:
                # 使用默认公司
                company_code = default_company_code
                company_name = default_company_name
                status = "使用默认"
                status_color = QColor(255, 165, 0)
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(status_color)
            
            self.preview_table.setItem(row, 2, QTableWidgetItem(company_name))
            self.preview_table.setItem(row, 3, status_item)
            
            self.imported_numbers.append({
                'number': num,
                'company_code': company_code,
                'company_name': company_name
            })
            
            valid_count += 1
            
        self.stats_label.setText(f"共 {len(unique_numbers)} 个单号")
        self.valid_count_label.setText(f"有效：{valid_count}")
        
        if duplicate_warning > 0:
            self.duplicate_count_label.setText(f"去重：{duplicate_warning}")
        else:
            self.duplicate_count_label.setText("无重复")
            
        self.import_btn.setEnabled(valid_count > 0)
        self.preview_table.resizeColumnsToContents()
        
    def preview_numbers(self):
        """预览解析结果"""
        self.parse_numbers()
        
    def clear_all(self):
        """清空所有"""
        self.file_path_edit.clear()
        self.text_edit.clear()
        self.preview_table.setRowCount(0)
        self.stats_label.setText("共 0 个单号")
        self.valid_count_label.setText("有效：0")
        self.duplicate_count_label.setText("去重：0")
        self.imported_numbers = []
        self.import_btn.setEnabled(False)
        
    def get_imported_numbers(self) -> List[Dict]:
        """获取导入的单号列表"""
        return self.imported_numbers

class CropImageDialog(QDialog):
    """图片裁剪对话框"""
    
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.original_pixmap = pixmap
        self.cropped_pixmap = None
        self.selection_rect = None
        self.is_selecting = False
        self.start_pos = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("裁剪图片")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 提示标签
        hint_label = QLabel("按住鼠标左键拖动选择裁剪区域，松开完成选择")
        hint_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(hint_label)
        
        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        
        # 缩放图片以适应窗口
        self.scaled_pixmap = self.original_pixmap.scaled(
            600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.scale_factor = self.scaled_pixmap.width() / self.original_pixmap.width()
        
        self.image_label.setPixmap(self.scaled_pixmap)
        
        # 启用鼠标跟踪
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event
        self.image_label.paintEvent = self.paint_event
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(False)
        scroll_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(scroll_area)
        
        # 信息标签
        self.info_label = QLabel("未选择区域")
        self.info_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.info_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("重置选择")
        self.reset_btn.clicked.connect(self.reset_selection)
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton("确认裁剪")
        self.ok_btn.clicked.connect(self.accept_crop)
        self.ok_btn.setEnabled(False)
        btn_layout.addWidget(self.ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def mouse_press_event(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.is_selecting = True
            self.selection_rect = None
            
    def mouse_move_event(self, event):
        """鼠标移动事件"""
        if self.is_selecting and self.start_pos:
            # 更新选择区域
            end_pos = event.pos()
            x = min(self.start_pos.x(), end_pos.x())
            y = min(self.start_pos.y(), end_pos.y())
            w = abs(self.start_pos.x() - end_pos.x())
            h = abs(self.start_pos.y() - end_pos.y())
            
            # 确保在选择区域内
            x = max(0, min(x, self.scaled_pixmap.width() - 1))
            y = max(0, min(y, self.scaled_pixmap.height() - 1))
            w = min(w, self.scaled_pixmap.width() - x)
            h = min(h, self.scaled_pixmap.height() - y)
            
            if w > 5 and h > 5:
                self.selection_rect = QRect(x, y, w, h)
                self.info_label.setText(f"选择区域: {w} x {h} 像素")
            
            self.image_label.update()
            
    def mouse_release_event(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            if self.selection_rect and self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                self.ok_btn.setEnabled(True)
            else:
                self.selection_rect = None
                self.info_label.setText("未选择区域（请拖动选择有效区域）")
            self.image_label.update()
            
    def paint_event(self, event):
        """绘制事件 - 绘制选择框"""
        # 先调用原始的绘制
        QLabel.paintEvent(self.image_label, event)
        
        # 绘制选择框
        if self.selection_rect:
            painter = QPainter(self.image_label)
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))
            painter.drawRect(self.selection_rect)
            
            # 绘制半透明遮罩
            painter.setBrush(QColor(0, 120, 215, 30))
            painter.drawRect(self.selection_rect)
            
    def reset_selection(self):
        """重置选择"""
        self.selection_rect = None
        self.ok_btn.setEnabled(False)
        self.info_label.setText("未选择区域")
        self.image_label.update()
        
    def accept_crop(self):
        """确认裁剪"""
        if not self.selection_rect:
            return
            
        # 计算原始图片上的裁剪区域
        scale = 1.0 / self.scale_factor
        orig_x = int(self.selection_rect.x() * scale)
        orig_y = int(self.selection_rect.y() * scale)
        orig_w = int(self.selection_rect.width() * scale)
        orig_h = int(self.selection_rect.height() * scale)
        
        # 裁剪图片
        self.cropped_pixmap = self.original_pixmap.copy(orig_x, orig_y, orig_w, orig_h)
        self.accept()
        
    def get_cropped_image(self) -> QPixmap:
        """获取裁剪后的图片"""
        return self.cropped_pixmap

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    window = ExpressQueryProGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()