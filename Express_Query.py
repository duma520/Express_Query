# Express_Query_Pro.py - 完整版（增强站点分析功能）

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

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QListWidget,
    QListWidgetItem, QTextEdit, QScrollArea, QProgressBar, QStatusBar,
    QTabWidget, QDialog, QFileDialog, QMessageBox, QInputDialog, QCheckBox,
    QSpinBox, QDateEdit, QCalendarWidget, QMenu, QSplitter, QHeaderView,
    QProgressDialog
)

from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSize, QByteArray, QBuffer, QIODevice,
    QDate, QUrl, QRect, QObject, QPropertyAnimation, QEasingCurve
)

from PySide6.QtGui import (
    QFont, QColor, QPixmap, QIcon, QImage, QPainter, QPalette, QBrush,
    QCursor, QKeySequence, QAction, QShortcut, QPen, QTransform
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
    VERSION = "2.0"  # 更新版本号
    BUILD_DATE = "2026-04-12"
    AUTHOR = "杜玛"
    LICENSE = "GNU Affero General Public License v3.0"
    COPYRIGHT = "© 永久 杜玛"
    URL = "https://github.com/duma520/Express_Query"
    MAINTAINER_EMAIL = "不提供"
    NAME = "快递查询系统"
    NAME_ENG = "Express_Query"
    DESCRIPTION = "Express_Query 快递查询系统 - 支持物流节点时间分析与站点预估"
    
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
DB_VERSION = "1.1"
BACKUP_DIR = "backups"
MAX_BACKUP_COUNT = 30
DEBUG_MODE = False


# ==================== 马卡龙色系定义 ====================
class MacaronColors:
    """马卡龙色系完整定义"""
    # 粉色系
    PINK_SAKURA = QColor('#FFB7CE')
    PINK_ROSE = QColor('#FF9AA2')
    PINK_COTTON = QColor('#FFD1DC')
    PINK_BALLET = QColor('#FCC9D3')
    
    # 蓝色系
    BLUE_SKY = QColor('#A2E1F6')
    BLUE_MIST = QColor('#C2E5F9')
    BLUE_PERIWINKLE = QColor('#C5D0E6')
    BLUE_LAVENDER = QColor('#D6EAF8')
    
    # 绿色系
    GREEN_MINT = QColor('#B5EAD7')
    GREEN_APPLE = QColor('#D4F1C7')
    GREEN_PISTACHIO = QColor('#D8E9D6')
    GREEN_SAGE = QColor('#C9DFC5')
    
    # 黄色/橙色系
    YELLOW_LEMON = QColor('#FFEAA5')
    YELLOW_CREAM = QColor('#FFF8B8')
    YELLOW_HONEY = QColor('#FCE5B4')
    ORANGE_PEACH = QColor('#FFDAC1')
    ORANGE_APRICOT = QColor('#FDD9B5')
    
    # 紫色系
    PURPLE_LAVENDER = QColor('#C7CEEA')
    PURPLE_TARO = QColor('#D8BFD8')
    PURPLE_WISTERIA = QColor('#C9B6D9')
    PURPLE_MAUVE = QColor('#E0C7D7')
    
    # 中性色
    NEUTRAL_CARAMEL = QColor('#F0E6DD')
    NEUTRAL_CREAM = QColor('#F7F1E5')
    NEUTRAL_MOCHA = QColor('#EAD7C7')
    NEUTRAL_ALMOND = QColor('#F2E4D4')
    
    # 其他颜色
    RED_CORAL = QColor('#FFB3A7')
    RED_WATERMELON = QColor('#FFC5C5')
    TEAL_MINT = QColor('#B8E2DE')
    
    # 文字颜色
    TEXT_DARK = QColor('#5A5A5A')
    TEXT_MEDIUM = QColor('#7A7A7A')
    TEXT_LIGHT = QColor('#9A9A9A')
    
    # 边框颜色
    BORDER_LIGHT = QColor('#E8E0D5')
    BORDER_MEDIUM = QColor('#D4C9BD')
    
    # 背景颜色
    BG_MAIN = QColor('#FDF8F5')
    BG_CARD = QColor('#FFFFFF')
    BG_HOVER = QColor('#F5F0EB')
    
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
            
            QLineEdit {{
                border: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                padding: 2px 4px;
                background-color: white;
                selection-background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
            
            QLineEdit:focus {{
                border: 1px solid {MacaronColors.BLUE_SKY.name()};
            }}
            
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
            
            /* ========== 增强的进度条样式 ========== */
            QProgressBar {{
                border: 1px solid {MacaronColors.BORDER_MEDIUM.name()};
                border-radius: 4px;
                background-color: #E8E8E8;
                text-align: center;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
                min-height: 18px;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MacaronColors.GREEN_MINT.name()},
                    stop:0.5 {MacaronColors.BLUE_SKY.name()},
                    stop:1 {MacaronColors.PURPLE_LAVENDER.name()});
                border-radius: 3px;
                margin: 1px;
            }}
            
            /* 不确定进度模式（旋转进度条） */
            QProgressBar:horizontal {{
                min-height: 20px;
            }}
            
            /* 状态栏进度条特殊样式 */
            QStatusBar QProgressBar {{
                border: 2px solid {MacaronColors.BORDER_MEDIUM.name()};
                border-radius: 5px;
                background-color: #E8E8E8;
                text-align: center;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
                min-height: 20px;
                max-height: 25px;
            }}
                
            QStatusBar QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MacaronColors.GREEN_APPLE.name()},
                    stop:0.5 {MacaronColors.BLUE_SKY.name()},
                    stop:1 {MacaronColors.ORANGE_PEACH.name()});
                border-radius: 3px;
                margin: 1px;
            }}

            QStatusBar {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_MEDIUM.name()};
                border-top: 1px solid {MacaronColors.BORDER_LIGHT.name()};
                min-height: 28px;
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

# ==================== 带状态栏的对话框基类 ====================
class DialogWithStatusBar(QDialog):
    """带状态栏的对话框基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status_bar = None
        self._progress_bar = None
    
    def setup_status_bar(self, main_layout: QVBoxLayout):
        """在布局底部添加状态栏"""
        # 创建状态栏
        self._status_bar = QStatusBar()
        self._status_bar.setMinimumHeight(28)
        self._status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_MEDIUM.name()};
                border-top: 1px solid {MacaronColors.BORDER_LIGHT.name()};
            }}
        """)
        
        # 添加进度条（默认隐藏）
        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.setMinimumHeight(18)
        self._progress_bar.setMaximumHeight(22)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {MacaronColors.BORDER_MEDIUM.name()};
                border-radius: 3px;
                background-color: #E8E8E8;
                text-align: center;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MacaronColors.GREEN_APPLE.name()},
                    stop:0.5 {MacaronColors.BLUE_SKY.name()},
                    stop:1 {MacaronColors.ORANGE_PEACH.name()});
                border-radius: 2px;
                margin: 1px;
            }}
        """)
        self._status_bar.addPermanentWidget(self._progress_bar)
        
        main_layout.addWidget(self._status_bar)
    
    def show_status(self, message: str, duration: int = 3000):
        """显示状态栏消息"""
        if self._status_bar:
            self._status_bar.showMessage(message, duration)
    
    def clear_status(self):
        """清除状态栏消息"""
        if self._status_bar:
            self._status_bar.clearMessage()
    
    def show_progress(self, visible: bool = True):
        """显示/隐藏进度条"""
        if self._progress_bar:
            self._progress_bar.setVisible(visible)
    
    def set_progress(self, value: int, maximum: int = 100):
        """设置进度条值"""
        if self._progress_bar:
            self._progress_bar.setMaximum(maximum)
            self._progress_bar.setValue(value)
            self._progress_bar.setVisible(True)
    
    def set_progress_indeterminate(self):
        """设置进度条为不确定模式（旋转）"""
        if self._progress_bar:
            self._progress_bar.setMaximum(0)
            self._progress_bar.setVisible(True)

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
                    print(f"  SQL: {query}")
                    print(f"  参数: {params}")
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


# ==================== 物流节点时间分析器（增强版） ====================
class LogisticsNodeAnalyzer:
    """物流节点时间分析器 - 分析快递在每个站点的停留和运输时间，支持站点预估"""
    
    def __init__(self, db_manager: DatabaseManagerPro):
        self.db_manager = db_manager
        self.init_node_history_table()
        
    def init_node_history_table(self):
        """初始化节点历史数据表（增强版 - 包含站点字段）"""
        sql = """
        CREATE TABLE IF NOT EXISTS node_transit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_code TEXT NOT NULL,
            from_city TEXT,
            to_city TEXT,
            from_site TEXT,
            to_site TEXT,
            node_type TEXT,
            action_type TEXT,
            avg_hours REAL,
            sample_count INTEGER DEFAULT 1,
            min_hours REAL,
            max_hours REAL,
            route_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute_update(sql)
        
        # 尝试添加新字段（如果表已存在但缺少字段）
        try:
            self.db_manager.execute_update("ALTER TABLE node_transit_history ADD COLUMN from_site TEXT")
        except:
            pass
        try:
            self.db_manager.execute_update("ALTER TABLE node_transit_history ADD COLUMN to_site TEXT")
        except:
            pass
        
        # 尝试删除旧的 UNIQUE 约束并创建新的
        try:
            # SQLite 不支持直接删除约束，需要重建表
            # 但我们可以先检查是否存在旧约束，如果有则重建
            self.db_manager.execute_update("""
                CREATE TABLE IF NOT EXISTS node_transit_history_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_code TEXT NOT NULL,
                    from_city TEXT,
                    to_city TEXT,
                    from_site TEXT,
                    to_site TEXT,
                    node_type TEXT,
                    action_type TEXT,
                    avg_hours REAL,
                    sample_count INTEGER DEFAULT 1,
                    min_hours REAL,
                    max_hours REAL,
                    route_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_code, from_city, to_city, from_site, to_site, node_type, action_type)
                )
            """)
            
            # 复制数据
            self.db_manager.execute_update("""
                INSERT INTO node_transit_history_new 
                SELECT * FROM node_transit_history
            """)
            
            # 删除旧表，重命名新表
            self.db_manager.execute_update("DROP TABLE node_transit_history")
            self.db_manager.execute_update("ALTER TABLE node_transit_history_new RENAME TO node_transit_history")
        except Exception as e:
            if DEBUG_MODE:
                print(f"重建表结构失败（可忽略）: {e}")
        
        # 创建索引
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_node_route ON node_transit_history(route_key)",
            "CREATE INDEX IF NOT EXISTS idx_node_company ON node_transit_history(company_code)",
            "CREATE INDEX IF NOT EXISTS idx_node_from_site ON node_transit_history(from_site)",
            "CREATE INDEX IF NOT EXISTS idx_node_to_site ON node_transit_history(to_site)"
        ]
        for sql in index_sqls:
            self.db_manager.execute_update(sql)
            
    def extract_nodes_from_track(self, track_list: List[Dict]) -> List[Dict]:
        """
        从物流轨迹中提取节点信息（增强版）
        返回节点列表，每个节点包含：时间、城市、站点名称、节点类型、动作类型、揽收员信息
        注意：返回的节点列表按时间从旧到新排序
        """
        nodes = []
        
        for track in track_list:
            context = track.get('context', '')
            time_str = track.get('time', '')
            
            if not time_str: continue
            try:
                time_dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            except:
                continue
            
            # 1. 提取快递员信息 (不影响站点判断)
            courier_info = self._extract_courier_info(context)
            
            # 2. 识别站点名称 (核心优化)
            site_name = self._extract_site_name_enhanced(context)
            
            # 3. 识别节点类型和动作类型
            node_type = self._identify_node_type(context)
            action_type = self._identify_action_type(context)
            
            # 4. 如果站点为空，根据动作类型兜底提取
            if not site_name:
                site_name = self._extract_site_by_action(context, action_type)

            city = self._extract_city(context)
            # site_name = self._extract_site_name(context)
            # courier_info = self._extract_courier_info(context)
            
            nodes.append({
                'time': time_dt,
                'time_str': time_str,
                'context': context,
                'city': city,
                'site_name': site_name,
                'node_type': node_type,
                'action_type': action_type,
                'courier_info': courier_info
            })
        
        # 按时间从旧到新排序
        nodes.sort(key=lambda x: x['time'])
        
        if DEBUG_MODE and nodes:
            print(f"  [节点排序] 共 {len(nodes)} 个节点，时间范围: {nodes[0]['time_str']} → {nodes[-1]['time_str']}")
        
        return nodes
    
    def _extract_site_name(self, context: str) -> str:
        """提取站点名称，如【广州市机场北包件车间】"""
        # 匹配中文方括号内的内容
        pattern = r'【([^】]+)】'
        matches = re.findall(pattern, context)
        if matches:
            for match in matches:
                # 排除时间格式和电话相关内容
                if not re.match(r'\d{4}-\d{2}-\d{2}', match) and '电话' not in match:
                    return match.strip()
        return ""

    def _extract_site_name_enhanced(self, context: str) -> str:
        """
        增强版站点名称提取
        支持：【站点名】、站点名[电话]、站点名-人名(电话) 等格式
        """
        # 1. 优先提取【】内的内容（通常是核心站点名）
        # 处理类似：【广州市】广东广州海珠区名粤公司[020-22049077]
        bracket_match = re.search(r'【[^】]*】\s*([^\[\s]+(?:公司|网点|分部|中心|仓|部|站))', context)
        if bracket_match:
            base_site = bracket_match.group(1).strip()
            # 尝试把后面的 -人名 或者 [电话] 也作为站点名的一部分保留
            # 匹配模式：站点名 - 人名 (电话) 或 站点名[电话]
            full_match = re.search(r'([^\[\s]+(?:公司|网点|分部|中心|仓|部|站)(?:-[^\[\s]+)?)', context)
            if full_match:
                return full_match.group(1).strip()
            return base_site

        # 2. 如果没有【】，提取带有明显站点后缀的词组，允许包含 [电话] 或 -人名
        # 例如：广东广州海珠区名粤公司[020-22049077] 或 浙江平阳县公司-王龙再（0577-28784350）
        pattern = r'([^\s，。；]*?(?:公司|网点|分部|中心|仓|部|站|投递部|揽投部)(?:-\S+)?(?:\[\S+\])?(?:（\S+）)?)'
        matches = re.findall(pattern, context)
        if matches:
            # 过滤掉太短或者纯数字的
            for m in matches:
                if len(m) > 3 and not m.isdigit():
                    # 特殊处理：如果提取的内容包含了电话号码，尽量保留完整结构
                    # 去除末尾可能的标点
                    return m.strip('。，； ')
        
        return ""

    def _extract_site_by_action(self, context: str, action_type: str) -> str:
        """
        当正则提取不到站点时，根据动作关键词提取前后文
        """
        # 到达类
        if action_type == 'arrive':
            # 已到达 XXX
            match = re.search(r'已到达\s*([^\s，。；]*?(?:公司|中心|网点|仓|部|站))', context)
            if match: return match.group(1)
        # 离开类
        elif action_type == 'depart':
            # 已离开 XXX 发往 YYY
            # 优先提取“离开”和“发往”之间的内容
            match = re.search(r'已离开\s*([^\s发]*?(?:公司|中心|网点|仓|部|站))', context)
            if match: return match.group(1)
        # 揽收类
        elif action_type == 'pickup':
            # XXX 已揽收
            match = re.search(r'([^\s，。；]*?(?:公司|网点|分部|仓|部|站)).*?已揽收', context)
            if match: return match.group(1)
            
        return ""


    def _extract_courier_info(self, context: str) -> Dict:
        """提取揽收员/快递员信息（优化版）"""
        info = {'name': '', 'phone': ''}
        
        # 1. 提取姓名
        # 匹配模式：快递员 张三、揽收员 李四、-王五、派件员 赵六
        name_patterns = [
            r'快递员[：:\s]*([^\s\d（(]+)',  # 快递员 刘健锋
            r'揽收员[：:\s]*([^\s\d（(]+)',
            r'派件员[：:\s]*([^\s\d（(]+)',
            r'[-－]\s*([^\s\d（(]+)',       # -王龙再
        ]
        for pattern in name_patterns:
            match = re.search(pattern, context)
            if match:
                name = match.group(1).strip()
                # 过滤掉一些误判（如“正在”）
                if name and len(name) >= 2 and not any(kw in name for kw in ['正在', '为你', '如有']):
                    info['name'] = name
                    break

        # 2. 提取电话
        # 支持格式：***已脱敏***-手机号、(***已脱敏***-手机号)、[***已脱敏***-手机号]、电话:***已脱敏***-手机号
        phone_match = re.search(r'[（(]?(\d{11})[）)]?', context)
        if not phone_match:
            phone_match = re.search(r'电话[:：]?\s*(\d{11})', context)
        if phone_match:
            info['phone'] = phone_match.group(1)
            
        return info
    
    def _identify_node_type(self, context: str) -> str:
        """识别节点类型"""
        context_lower = context.lower()
        
        # 转运中心/分拨中心/处理中心
        if any(kw in context_lower or kw in context for kw in 
            ['转运中心', '分拨中心', '处理中心', '中转中心', '分拣中心', '转运站',
                '包件车间', '直投中心', '投递部', '揽投部', '网格仓', '集散中心',
                '中转站', '分拨站', '集散点', '枢纽', '中转场', '航空部', '陆运部',
                '中转部', '分拣部', '操作中心', '运作中心', '集散中心', '分拨部']):
            return 'transit_center'
        
        # 营业点/网点/分部
        if any(kw in context_lower or kw in context for kw in 
            ['营业点', '网点', '服务点', '分公司', '分部', '营业部', '营业厅',
                '服务部', '服务站', '服务网点', '揽收点', '收件点', '派件点',
                '快递点', '快递站', '收派点', '营业处', '代办点', '服务处']):
            return 'service_point'
        
        # 驿站/代收点/快递柜
        if any(kw in context_lower or kw in context for kw in 
            ['驿站', '菜鸟', '丰巢', '快递柜', '自提柜', '代收点', '妈妈驿站',
                '店', '超市', '代理点', '兔喜', '快递超市', '邻里驿站', '熊猫快收',
                '速递易', '云柜', '日日顺', '蜂巢', 'e栈', '收件宝', '近邻宝',
                '格格货栈', '乐收', '菜鸟驿站', '菜鸟裹裹', '自提点', '代收站',
                '便利店', '物业', '门卫', '传达室', '收发室', '智能柜', '快递箱']):
            return 'pickup_point'
        
        # 机场/航空
        if any(kw in context_lower or kw in context for kw in 
            ['机场', '航空', '航站楼', '空港', '航班', '起飞', '降落',
                '航空部', '空运', '航运']):
            return 'airport'
        
        # 火车站/铁路
        if any(kw in context_lower or kw in context for kw in 
            ['火车站', '高铁', '铁路', '动车', '列车', '车次', '站台']):
            return 'railway'
        
        # 港口/码头
        if any(kw in context_lower or kw in context for kw in 
            ['港口', '码头', '港区', '海运', '船舶', '集装箱码头']):
            return 'port'
        
        # 海关
        if any(kw in context_lower or kw in context for kw in 
            ['海关', '报关', '清关', '通关', '检验检疫', '商检']):
            return 'customs'
        
        # 仓库
        if any(kw in context_lower or kw in context for kw in 
            ['仓库', '仓储', '库房', '备件库', '存货区', '存储区']):
            return 'warehouse'
        
        return 'unknown'


    def _identify_action_type(self, context: str) -> str:
        """识别动作类型"""
        context_lower = context.lower()
        
        # 揽收/收件
        if any(kw in context_lower or kw in context for kw in 
            ['揽收', '已揽件', '收件', '取件', '已取件', '已揽收', '揽件',
                '收寄', '已收寄', '上门取件', '已接单', '待取件', '预约取件',
                '取件成功', '揽收成功', '已收件']):
            return 'pickup'
        
        # 到达
        if any(kw in context_lower or kw in context for kw in 
            ['到达', '已到达', '抵达', '进站', '到件', '到站', '已到',
                '到达处理中心', '到达营业点', '到达网点', '抵达转运中心',
                '到达中转站', '已抵达', '到达分拨中心']):
            return 'arrive'
        
        # 离开/发出
        if any(kw in context_lower or kw in context for kw in 
            ['离开', '发出', '发往', '发件', '出站', '出库', '已发出', '转运到',
                '已离开', '离开处理中心', '发往下一站', '送往', '运往', '寄往',
                '已发往', '出发', '启程', '装车发出', '发车']):
            return 'depart'
        
        # 派送/派件
        if any(kw in context_lower or kw in context for kw in 
            ['派送', '派件', '投递', '快递员派送', '正在派送', '正在为您派件',
                '派送中', '派件中', '投递中', '正在投递', '派件员', '快递员',
                '开始派送', '安排派送', '预约派送', '派送员']):
            return 'delivering'
        
        # 签收
        if any(kw in context_lower or kw in context for kw in 
            ['签收', '已签收', '妥投', '本人签收', '他人签收', '快递员签收',
                '已妥投', '签收成功', '已收件人签收', '已签收完成', '代收',
                '家人代收', '同事代收', '前台代收', '物业代收']):
            return 'signed'
        
        # 已派送至驿站/代收点
        if any(kw in context_lower or kw in context for kw in 
            ['已派送至', '派送至', '投递至', '已放入', '存入', '入柜',
                '投柜', '已投柜', '放入快递柜', '放入丰巢', '放入驿站',
                '到达驿站', '已到驿站', '可取件', '待取件', '请取件',
                '凭取件码', '取件码', '已送达']):
            return 'arrived_pickup'
        
        # 疑难/异常
        if any(kw in context_lower or kw in context for kw in 
            ['疑难', '异常', '滞留', '超时', '未妥投', '问题件', '疑难件',
                '地址不详', '电话不通', '无法联系', '拒收', '改地址', '退回',
                '投递失败', '派送失败']):
            return 'problem'
        
        # 退回
        if any(kw in context_lower or kw in context for kw in 
            ['退回', '退件', '退签', '退货', '返程', '原路返回', '退件中',
                '已退回', '退回寄件人', '退回处理']):
            return 'returned'
        
        # 清关相关
        if any(kw in context_lower or kw in context for kw in 
            ['清关', '报关', '通关', '海关查验', '海关放行', '待清关',
                '清关中', '已清关', '海关扣留', '海关申报']):
            return 'customs'
        
        # 中转/转运
        if any(kw in context_lower or kw in context for kw in 
            ['中转', '转运', '经转', '转站', '换站']):
            return 'transit'
        
        # 装车/卸车
        if any(kw in context_lower or kw in context for kw in 
            ['装车', '已装车', '装车扫描', '装车发出']):
            return 'loading'
        
        if any(kw in context_lower or kw in context for kw in 
            ['卸车', '已卸车', '卸车扫描', '到车']):
            return 'unloading'
        
        # 分拣/扫描
        if any(kw in context_lower or kw in context for kw in 
            ['分拣', '扫描', '已扫描', '分拣完成', '建包', '拆包',
                '打包', '称重', '安检']):
            return 'processing'
        
        # 运输中
        if any(kw in context_lower or kw in context for kw in 
            ['运输中', '在途', '途中', '运送中', '正在运输']):
            return 'in_transit'
        
        # 起飞/降落（航空件）
        if any(kw in context_lower or kw in context for kw in 
            ['起飞', '已起飞', '航班起飞']):
            return 'takeoff'
        
        if any(kw in context_lower or kw in context for kw in 
            ['降落', '已降落', '航班降落', '到达机场']):
            return 'landing'
        
        # 状态更新/其他
        if any(kw in context_lower or kw in context for kw in 
            ['状态', '更新', '信息', '通知', '备注']):
            return 'status'
        
        return 'other'


    def _extract_city(self, context: str) -> str:
        """从上下文提取城市名（增强版 - 支持更多城市和提取方式）"""
        # 中国主要城市列表（按人口和经济重要性排序）
        cities = [
            # 直辖市
            '北京', '北京市', '上海', '上海市', '天津', '天津市', '重庆', '重庆市',
            
            # 省会城市
            '广州', '广州市', '深圳', '深圳市', '杭州', '杭州市', '南京', '南京市',
            '武汉', '武汉市', '成都', '成都市', '西安', '西安市', '郑州', '郑州市',
            '长沙', '长沙市', '青岛', '青岛市', '济南', '济南市', '合肥', '合肥市',
            '福州', '福州市', '厦门', '厦门市', '宁波', '宁波市', '大连', '大连市',
            '沈阳', '沈阳市', '哈尔滨', '哈尔滨市', '长春', '长春市', '昆明', '昆明市',
            '南宁', '南宁市', '贵阳', '贵阳市', '太原', '太原市', '石家庄', '石家庄市',
            '南昌', '南昌市', '乌鲁木齐', '乌鲁木齐市', '兰州', '兰州市', '呼和浩特',
            '呼和浩特市', '银川', '银川市', '西宁', '西宁市', '海口', '海口市',
            '三亚', '三亚市', '拉萨', '拉萨市',
            
            # 重要地级市/经济强市
            '珠海', '珠海市', '佛山', '佛山市', '东莞', '东莞市', '惠州', '惠州市',
            '中山', '中山市', '江门', '江门市', '湛江', '湛江市', '茂名', '茂名市',
            '肇庆', '肇庆市', '汕头', '汕头市', '潮州', '潮州市', '揭阳', '揭阳市',
            '汕尾', '汕尾市', '梅州', '梅州市', '河源', '河源市', '清远', '清远市',
            '韶关', '韶关市', '阳江', '阳江市', '云浮', '云浮市',
            
            # 江苏省
            '无锡', '无锡市', '常州', '常州市', '南通', '南通市', '扬州', '扬州市',
            '镇江', '镇江市', '徐州', '徐州市', '盐城', '盐城市', '淮安', '淮安市',
            '连云港', '连云港市', '泰州', '泰州市', '宿迁', '宿迁市', '苏州', '苏州市',
            '昆山', '昆山市', '江阴', '江阴市', '宜兴', '宜兴市', '常熟', '常熟市',
            '张家港', '张家港市', '太仓', '太仓市',
            
            # 浙江省
            '温州', '温州市', '绍兴', '绍兴市', '嘉兴', '嘉兴市', '金华', '金华市',
            '台州', '台州市', '湖州', '湖州市', '衢州', '衢州市', '丽水', '丽水市',
            '舟山', '舟山市', '义乌', '义乌市', '慈溪', '慈溪市', '余姚', '余姚市',
            
            # 福建省
            '泉州', '泉州市', '漳州', '漳州市', '莆田', '莆田市', '龙岩', '龙岩市',
            '三明', '三明市', '南平', '南平市', '宁德', '宁德市', '晋江', '晋江市',
            '福清', '福清市',
            
            # 山东省
            '烟台', '烟台市', '威海', '威海市', '潍坊', '潍坊市', '淄博', '淄博市',
            '临沂', '临沂市', '济宁', '济宁市', '泰安', '泰安市', '聊城', '聊城市',
            '德州', '德州市', '滨州', '滨州市', '东营', '东营市', '菏泽', '菏泽市',
            '日照', '日照市', '枣庄', '枣庄市',
            
            # 河南省
            '洛阳', '洛阳市', '南阳', '南阳市', '许昌', '许昌市', '周口', '周口市',
            '新乡', '新乡市', '商丘', '商丘市', '驻马店', '驻马店市', '信阳', '信阳市',
            '开封', '开封市', '平顶山', '平顶山市', '安阳', '安阳市', '焦作', '焦作市',
            '濮阳', '濮阳市', '漯河', '漯河市', '三门峡', '三门峡市', '鹤壁', '鹤壁市',
            
            # 河北省
            '唐山', '唐山市', '邯郸', '邯郸市', '保定', '保定市', '沧州', '沧州市',
            '邢台', '邢台市', '廊坊', '廊坊市', '张家口', '张家口市', '承德', '承德市',
            '秦皇岛', '秦皇岛市', '衡水', '衡水市',
            
            # 湖北省
            '襄阳', '襄阳市', '宜昌', '宜昌市', '荆州', '荆州市', '黄冈', '黄冈市',
            '孝感', '孝感市', '十堰', '十堰市', '荆门', '荆门市', '黄石', '黄石市',
            '咸宁', '咸宁市', '随州', '随州市', '鄂州', '鄂州市', '恩施', '恩施市',
            
            # 湖南省
            '株洲', '株洲市', '湘潭', '湘潭市', '衡阳', '衡阳市', '邵阳', '邵阳市',
            '岳阳', '岳阳市', '常德', '常德市', '张家界', '张家界市', '益阳', '益阳市',
            '郴州', '郴州市', '永州', '永州市', '怀化', '怀化市', '娄底', '娄底市',
            '湘西', '吉首市',
            
            # 广东省更多
            '河源', '河源市', '阳江', '阳江市', '清远', '清远市', '梅州', '梅州市',
            '揭阳', '揭阳市', '茂名', '茂名市', '湛江', '湛江市', '韶关', '韶关市',
            '汕尾', '汕尾市', '潮州', '潮州市', '云浮', '云浮市',
            
            # 四川省
            '绵阳', '绵阳市', '德阳', '德阳市', '宜宾', '宜宾市', '南充', '南充市',
            '泸州', '泸州市', '达州', '达州市', '乐山', '乐山市', '凉山', '西昌市',
            '内江', '内江市', '自贡', '自贡市', '攀枝花', '攀枝花市', '眉山', '眉山市',
            '遂宁', '遂宁市', '广安', '广安市', '巴中', '巴中市', '资阳', '资阳市',
            '雅安', '雅安市', '广元', '广元市', '甘孜', '康定市', '阿坝', '马尔康市',
            
            # 陕西省
            '宝鸡', '宝鸡市', '咸阳', '咸阳市', '渭南', '渭南市', '汉中', '汉中市',
            '榆林', '榆林市', '安康', '安康市', '商洛', '商洛市', '延安', '延安市',
            '铜川', '铜川市',
            
            # 辽宁省
            '鞍山', '鞍山市', '抚顺', '抚顺市', '本溪', '本溪市', '丹东', '丹东市',
            '锦州', '锦州市', '营口', '营口市', '阜新', '阜新市', '辽阳', '辽阳市',
            '盘锦', '盘锦市', '铁岭', '铁岭市', '朝阳', '朝阳市', '葫芦岛', '葫芦岛市',
            
            # 吉林省
            '吉林', '吉林市', '四平', '四平市', '辽源', '辽源市', '通化', '通化市',
            '白山', '白山市', '松原', '松原市', '白城', '白城市', '延边', '延吉市',
            
            # 黑龙江省
            '齐齐哈尔', '齐齐哈尔市', '鸡西', '鸡西市', '鹤岗', '鹤岗市', '双鸭山',
            '双鸭山市', '大庆', '大庆市', '伊春', '伊春市', '佳木斯', '佳木斯市',
            '七台河', '七台河市', '牡丹江', '牡丹江市', '黑河', '黑河市', '绥化',
            '绥化市', '大兴安岭',
            
            # 安徽省
            '芜湖', '芜湖市', '蚌埠', '蚌埠市', '淮南', '淮南市', '马鞍山', '马鞍山市',
            '淮北', '淮北市', '铜陵', '铜陵市', '安庆', '安庆市', '黄山', '黄山市',
            '滁州', '滁州市', '阜阳', '阜阳市', '宿州', '宿州市', '六安', '六安市',
            '亳州', '亳州市', '池州', '池州市', '宣城', '宣城市',
            
            # 江西省
            '景德镇', '景德镇市', '萍乡', '萍乡市', '九江', '九江市', '新余', '新余市',
            '鹰潭', '鹰潭市', '赣州', '赣州市', '吉安', '吉安市', '宜春', '宜春市',
            '抚州', '抚州市', '上饶', '上饶市',
            
            # 贵州省
            '遵义', '遵义市', '六盘水', '六盘水市', '安顺', '安顺市', '毕节', '毕节市',
            '铜仁', '铜仁市', '黔西南', '兴义市', '黔东南', '凯里市', '黔南', '都匀市',
            
            # 云南省
            '曲靖', '曲靖市', '玉溪', '玉溪市', '保山', '保山市', '昭通', '昭通市',
            '丽江', '丽江市', '普洱', '普洱市', '临沧', '临沧市', '楚雄', '楚雄市',
            '红河', '蒙自市', '文山', '文山市', '西双版纳', '景洪市', '大理', '大理市',
            '德宏', '芒市', '怒江', '泸水市', '迪庆', '香格里拉市',
            
            # 甘肃省
            '嘉峪关', '嘉峪关市', '金昌', '金昌市', '白银', '白银市', '天水', '天水市',
            '武威', '武威市', '张掖', '张掖市', '平凉', '平凉市', '酒泉', '酒泉市',
            '庆阳', '庆阳市', '定西', '定西市', '陇南', '陇南市', '临夏', '临夏市',
            '甘南', '合作市',
            
            # 内蒙古自治区
            '包头', '包头市', '乌海', '乌海市', '赤峰', '赤峰市', '通辽', '通辽市',
            '鄂尔多斯', '鄂尔多斯市', '呼伦贝尔', '呼伦贝尔市', '巴彦淖尔', '巴彦淖尔市',
            '乌兰察布', '乌兰察布市', '兴安', '乌兰浩特市', '锡林郭勒', '锡林浩特市',
            '阿拉善', '阿拉善左旗',
            
            # 广西壮族自治区
            '柳州', '柳州市', '桂林', '桂林市', '梧州', '梧州市', '北海', '北海市',
            '防城港', '防城港市', '钦州', '钦州市', '贵港', '贵港市', '玉林', '玉林市',
            '百色', '百色市', '贺州', '贺州市', '河池', '河池市', '来宾', '来宾市',
            '崇左', '崇左市',
            
            # 西藏自治区
            '日喀则', '日喀则市', '昌都', '昌都市', '林芝', '林芝市', '山南', '山南市',
            '那曲', '那曲市', '阿里',
            
            # 宁夏回族自治区
            '石嘴山', '石嘴山市', '吴忠', '吴忠市', '固原', '固原市', '中卫', '中卫市',
            
            # 新疆维吾尔自治区
            '克拉玛依', '克拉玛依市', '吐鲁番', '吐鲁番市', '哈密', '哈密市',
            '昌吉', '昌吉市', '博尔塔拉', '博乐市', '巴音郭楞', '库尔勒市',
            '阿克苏', '阿克苏市', '克孜勒苏', '阿图什市', '喀什', '喀什市',
            '和田', '和田市', '伊犁', '伊宁市', '塔城', '塔城市', '阿勒泰', '阿勒泰市',
            '石河子', '石河子市', '阿拉尔', '阿拉尔市', '图木舒克', '图木舒克市',
            '五家渠', '五家渠市', '北屯', '北屯市', '铁门关', '铁门关市', '双河', '双河市',
            '可克达拉', '可克达拉市', '昆玉', '昆玉市', '胡杨河', '胡杨河市',
            
            # 海南省更多
            '三沙', '三沙市', '儋州', '儋州市', '五指山', '五指山市', '琼海', '琼海市',
            '文昌', '文昌市', '万宁', '万宁市', '东方', '东方市', '定安', '定安县',
            '屯昌', '屯昌县', '澄迈', '澄迈县', '临高', '临高县', '白沙', '白沙黎族自治县',
            '昌江', '昌江黎族自治县', '乐东', '乐东黎族自治县', '陵水', '陵水黎族自治县',
            '保亭', '保亭黎族苗族自治县', '琼中', '琼中黎族苗族自治县',
            
            # 青海省
            '海东', '海东市', '海北', '海晏县', '黄南', '同仁市', '海南', '共和县',
            '果洛', '玛沁县', '玉树', '玉树市', '海西', '德令哈市',
            
            # 台湾省（中国不可分割的一部分）
            '台北', '台北市', '新北', '新北市', '桃园', '桃园市', '台中', '台中市',
            '台南', '台南市', '高雄', '高雄市', '基隆', '基隆市', '新竹', '新竹市',
            '嘉义', '嘉义市',
            
            # 香港特别行政区
            '香港',
            
            # 澳门特别行政区
            '澳门',
        ]
        
        # 1. 优先匹配【】内的城市信息
        bracket_match = re.search(r'【([^】]+)】', context)
        if bracket_match:
            bracket_content = bracket_match.group(1)
            for city in cities:
                if city in bracket_content:
                    # 去掉"市"后缀返回标准城市名
                    return city.replace('市', '')
        
        # 2. 匹配"发往XX"、"到达XX"等模式中的城市
        patterns = [
            r'发往\s*([^\s，。；]+(?:市|省|区|县))',
            r'送往\s*([^\s，。；]+(?:市|省|区|县))',
            r'运往\s*([^\s，。；]+(?:市|省|区|县))',
            r'到达\s*([^\s，。；]+(?:市|省|区|县|站|中心|部))',
            r'离开\s*([^\s，。；]+(?:市|省|区|县))',
            r'在\s*([^\s，。；]+(?:市|省|区|县))\s*处理',
            r'([^\s，。；]+(?:市|省))\s*公司',
            r'([^\s，。；]+(?:市|省))\s*转运中心',
            r'([^\s，。；]+(?:市|省))\s*分拨中心',
            r'([^\s，。；]+(?:市|省))\s*网点',
            r'([^\s，。；]+(?:市|省))\s*营业部',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                extracted = match.group(1)
                # 提取城市名
                for city in cities:
                    if city in extracted:
                        return city.replace('市', '').replace('省', '')
                # 如果没匹配到，返回提取的内容（去掉常见后缀）
                extracted = re.sub(r'[省市县区]', '', extracted)
                if len(extracted) >= 2:
                    return extracted
        
        # 3. 直接在城市列表中匹配
        for city in cities:
            if city in context:
                return city.replace('市', '')
        
        # 4. 匹配行政区划代码格式（如"北京市"、"广东省"等）
        province_match = re.search(r'([^\s，。；]+(?:省|自治区|特别行政区|市))', context)
        if province_match:
            province = province_match.group(1)
            # 如果是省级单位，返回省级名称
            return province.replace('省', '').replace('自治区', '').replace('特别行政区', '')
        
        # 5. 尝试从站点名称中提取城市（如"广东广州海珠区名粤公司"）
        site_match = re.search(r'([^\s，。；]*?(?:市|县|区))', context)
        if site_match:
            location = site_match.group(1)
            for city in cities:
                if city in location:
                    return city.replace('市', '')
        
        return ""
    
    def calculate_node_transit_times(self, nodes: List[Dict]) -> List[Dict]:
        """
        计算节点间的运输时间和停留时间（增强版）
        返回各阶段的时间分析，包含站点信息
        """
        if len(nodes) < 2:
            return []
            
        segments = []
        
        for i in range(1, len(nodes)):
            prev_node = nodes[i-1]
            curr_node = nodes[i]
            
            # 计算绝对时间差（小时）
            time_diff = abs((curr_node['time'] - prev_node['time']).total_seconds()) / 3600
            
            # 判断是否为停留（同一站点且不是出发动作）
            is_dwell = (prev_node['site_name'] == curr_node['site_name'] and 
                       prev_node['site_name'] and 
                       prev_node['action_type'] != 'depart')
            
            segment = {
                'from_city': prev_node['city'],
                'to_city': curr_node['city'],
                'from_site': prev_node['site_name'],
                'to_site': curr_node['site_name'],
                'from_time': prev_node['time_str'],
                'to_time': curr_node['time_str'],
                'hours': round(time_diff, 1),
                'is_dwell': is_dwell,
                'from_node_type': prev_node['node_type'],
                'to_node_type': curr_node['node_type'],
                'from_action': prev_node['action_type'],
                'to_action': curr_node['action_type'],
                'context': curr_node['context'],
                'courier_info': curr_node.get('courier_info', {})
            }
            segments.append(segment)
            
        return segments
    
    def record_node_transit(self, express_data: Dict):
        """记录节点运输时间到历史库"""
        track_list = express_data.get('data', [])
        if len(track_list) < 1:  # 改为至少1条
            if DEBUG_MODE:
                print(f"  [跳过] 无物流轨迹")
            return
            
        # 获取company_code，确保不为空
        company_code = express_data.get('com', '')
        if not company_code:
            company_code = express_data.get('company_code', '')
        if not company_code:
            # 尝试从单号推断
            nu = express_data.get('nu', '')
            if nu.startswith('YT'):
                company_code = 'yuantong'
            elif nu.startswith('JT'):
                company_code = 'jtexpress'
            elif nu.startswith('JD'):
                company_code = 'jd'
            elif nu.isdigit() and len(nu) >= 10:
                company_code = 'unknown'
            else:
                company_code = 'unknown'
        
        if DEBUG_MODE:
            print(f"  [记录节点] 单号: {express_data.get('nu', '')}, 公司: {company_code}, 轨迹数: {len(track_list)}")
            
        nodes = self.extract_nodes_from_track(track_list)
        
        # 如果只有1个节点，无法计算运输段
        if len(nodes) < 2:
            if DEBUG_MODE:
                print(f"  [跳过] 节点不足2个，无法计算运输段")
            return
        
        segments = self.calculate_node_transit_times(nodes)
        
        recorded_count = 0
        for seg in segments:
            hours = seg['hours']
            # 放宽时间范围：0.01-720小时
            if 0.01 <= hours <= 720:
                if seg['is_dwell']:
                    # 停留段：记录为停留
                    self._update_node_history(
                        company_code,
                        seg['from_city'],
                        seg['to_city'],
                        seg['from_site'],
                        seg['to_site'],
                        'dwell',
                        'stay',
                        hours
                    )
                    recorded_count += 1
                else:
                    # 运输段：记录为运输
                    self._update_node_history(
                        company_code,
                        seg['from_city'],
                        seg['to_city'],
                        seg['from_site'],
                        seg['to_site'],
                        seg['from_node_type'],
                        seg['to_action'],
                        hours
                    )
                    recorded_count += 1
            else:
                if DEBUG_MODE:
                    print(f"  [跳过段] 时间超出范围: {hours}h")
        
        if DEBUG_MODE:
            print(f"  本次共记录 {recorded_count} 条节点数据")

    def verify_table_structure(self):
        """验证表结构"""
        try:
            # 检查表是否存在
            check_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='node_transit_history'"
            result = self.db_manager.execute_query(check_sql)
            if not result:
                print("[错误] node_transit_history 表不存在")
                return False
            
            # 获取表结构
            pragma_sql = "PRAGMA table_info(node_transit_history)"
            columns = self.db_manager.execute_query(pragma_sql)
            print("[表结构] node_transit_history 列:")
            for col in columns:
                print(f"  {col['name']} ({col['type']})")
            return True
        except Exception as e:
            print(f"[错误] 验证表结构失败: {e}")
            return False

    def _update_node_history(self, company_code: str, from_city: str, to_city: str,
                            from_site: str, to_site: str,
                            node_type: str, action_type: str, hours: float):
        """更新节点历史数据（增强版 - 包含站点信息）"""
        from_city_display = from_city if from_city else "未知"
        to_city_display = to_city if to_city else "未知"
        from_site_display = from_site if from_site else ""
        to_site_display = to_site if to_site else ""
        
        route_key = f"{from_city_display}→{to_city_display}"
        if from_site_display and to_site_display:
            route_key = f"{from_site_display}→{to_site_display}"
        
        if hours < 0.01 or hours > 720:
            if DEBUG_MODE:
                print(f"  [跳过] 时间超出范围: {hours}小时")
            return
        
        if DEBUG_MODE:
            print(f"  [尝试记录] {company_code}: {from_site_display}→{to_site_display} ({hours:.1f}h)")
        
        # 先尝试精确匹配（包含站点）
        check_sql = """
        SELECT id, avg_hours, sample_count, min_hours, max_hours 
        FROM node_transit_history 
        WHERE company_code = ? AND from_city = ? AND to_city = ? 
        AND from_site = ? AND to_site = ?
        AND node_type = ? AND action_type = ?
        """
        existing = self.db_manager.execute_query(check_sql, (
            company_code, from_city_display, to_city_display,
            from_site_display, to_site_display,
            node_type, action_type
        ))
        
        # 如果没有精确匹配，尝试宽松匹配（站点可能为空）
        if not existing:
            check_sql = """
            SELECT id, avg_hours, sample_count, min_hours, max_hours 
            FROM node_transit_history 
            WHERE company_code = ? AND from_city = ? AND to_city = ? 
            AND (from_site = '' OR from_site IS NULL) AND (to_site = '' OR to_site IS NULL)
            AND node_type = ? AND action_type = ?
            """
            existing = self.db_manager.execute_query(check_sql, (
                company_code, from_city_display, to_city_display,
                node_type, action_type
            ))
        
        if existing:
            # 更新现有记录
            old_avg = existing[0]['avg_hours'] or 0
            old_count = existing[0]['sample_count'] or 0
            new_avg = (old_avg * old_count + hours) / (old_count + 1)
            new_count = old_count + 1
            
            old_min = existing[0].get('min_hours')
            old_max = existing[0].get('max_hours')
            new_min = min(old_min if old_min is not None else hours, hours)
            new_max = max(old_max if old_max is not None else hours, hours)
            
            update_sql = """
            UPDATE node_transit_history 
            SET avg_hours = ?, sample_count = ?, min_hours = ?, max_hours = ?, 
                from_site = CASE WHEN from_site = '' OR from_site IS NULL THEN ? ELSE from_site END,
                to_site = CASE WHEN to_site = '' OR to_site IS NULL THEN ? ELSE to_site END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            update_result = self.db_manager.execute_update(update_sql, (
                new_avg, new_count, new_min, new_max, 
                from_site_display, to_site_display, existing[0]['id']
            ))
            if DEBUG_MODE:
                if update_result:
                    print(f"    [更新成功] ID={existing[0]['id']}")
                else:
                    print(f"    [更新失败]")
        else:
            # 插入新记录 - 使用 INSERT OR REPLACE 处理冲突
            insert_sql = """
            INSERT OR REPLACE INTO node_transit_history 
            (company_code, from_city, to_city, from_site, to_site, node_type, action_type, 
            avg_hours, sample_count, min_hours, max_hours, route_key, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            insert_result = self.db_manager.execute_update(insert_sql, (
                company_code, from_city_display, to_city_display, 
                from_site_display, to_site_display,
                node_type, action_type,
                hours, hours, hours, route_key
            ))
            if DEBUG_MODE:
                if insert_result:
                    print(f"    [插入成功]")
                else:
                    print(f"    [插入失败] SQL执行返回False")
        
    def estimate_segment_time(self, company_code: str, from_city: str, to_city: str,
                              node_type: str = None, action_type: str = None) -> Tuple[Optional[float], str, int]:
        """
        预估某段运输的耗时
        返回 (预估小时数, 说明, 样本数量)
        """
        sql = """
        SELECT avg_hours, sample_count, min_hours, max_hours
        FROM node_transit_history
        WHERE company_code = ? AND from_city = ? AND to_city = ?
        """
        params = [company_code, from_city, to_city]
        
        if node_type:
            sql += " AND node_type = ?"
            params.append(node_type)
        if action_type:
            sql += " AND action_type = ?"
            params.append(action_type)
            
        result = self.db_manager.execute_query(sql, tuple(params))
        
        if result:
            avg = result[0]['avg_hours']
            count = result[0]['sample_count']
            min_h = result[0]['min_hours']
            max_h = result[0]['max_hours']
            
            if count >= 3:
                return avg, f"基于{count}次历史数据，预计{avg:.1f}小时", count
            else:
                return avg, f"基于{count}次数据（较少），预计{avg:.1f}小时", count
                
        return None, "暂无历史数据", 0
    def estimate_next_stations(self, express_data: Dict) -> List[Dict]:
        """
        根据当前物流状态，预估到达后续各个关键站点的时间
        支持跨公司数据参考
        """
        track_list = express_data.get('data', [])
        if not track_list:
            return []
            
        company_code = express_data.get('com', '')
        state = str(express_data.get('state', ''))
        
        # 已签收则无需预估
        if state == '3':
            return []
            
        nodes = self.extract_nodes_from_track(track_list)
        if not nodes:
            return []
            
        # 获取当前所在的最后一个站点
        last_node = nodes[-1]
        current_site = last_node['site_name']
        current_city = last_node['city']
        current_action = last_node['action_type']
        
        estimates = []
        
        # 如果当前正在派送中
        if current_action == 'delivering':
            # 预估签收时间（不限公司）
            sql = """
            SELECT AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples, company_code
            FROM node_transit_history
            WHERE from_site = ? AND action_type = 'signed'
            GROUP BY company_code
            ORDER BY total_samples DESC
            LIMIT 1
            """
            results = self.db_manager.execute_query(sql, (current_site,))
            if results and results[0]['avg_hours']:
                avg_hours = results[0]['avg_hours']
                total_samples = results[0]['total_samples'] or 1
                is_same = (results[0].get('company_code') == company_code)
                est_type = "同公司" if is_same else "跨公司参考"
                
                estimates.append({
                    'type': 'signed',
                    'description': f"[{est_type}] 预计 {avg_hours:.1f} 小时后签收",
                    'hours': round(avg_hours, 1),
                    'confidence': total_samples,
                    'confidence_level': '高' if total_samples >= 5 else ('中' if total_samples >= 2 else '低'),
                    'is_same_company': is_same
                })
        
        # 如果当前在转运中心
        if current_site and ('包件车间' in current_site or '处理中心' in current_site or '转运中心' in current_site):
            # 查询从该站点出发的常见下一站（不限公司）
            sql = """
            SELECT to_site, to_city, company_code, AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples
            FROM node_transit_history
            WHERE from_site = ? AND to_site != ''
            GROUP BY to_site, to_city, company_code
            ORDER BY total_samples DESC, avg_hours
            LIMIT 5
            """
            results = self.db_manager.execute_query(sql, (current_site,))
            for row in results:
                if row['to_site'] and row['avg_hours']:
                    confidence = row['total_samples'] or 1
                    is_same = (row['company_code'] == company_code)
                    est_type = "同公司" if is_same else "跨公司参考"
                    
                    estimates.append({
                        'type': 'next_station',
                        'next_site': row['to_site'],
                        'city': row['to_city'],
                        'description': f"[{est_type}] 预计 {row['avg_hours']:.1f} 小时后到达 {row['to_site']}",
                        'hours': round(row['avg_hours'], 1),
                        'confidence': confidence,
                        'confidence_level': '高' if confidence >= 5 else ('中' if confidence >= 2 else '低'),
                        'is_same_company': is_same,
                        'company': row['company_code']
                    })
        
        # 通用预估：查询从当前站点出发的所有记录
        if not estimates and current_site:
            sql = """
            SELECT to_site, to_city, action_type, company_code, AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples
            FROM node_transit_history
            WHERE from_site = ?
            GROUP BY to_site, to_city, action_type, company_code
            ORDER BY total_samples DESC, avg_hours
            LIMIT 5
            """
            results = self.db_manager.execute_query(sql, (current_site,))
            for row in results:
                if row['avg_hours']:
                    confidence = row['total_samples'] or 1
                    action_text = self._get_action_text(row['action_type'])
                    is_same = (row['company_code'] == company_code)
                    est_type = "同公司" if is_same else "跨公司参考"
                    
                    estimates.append({
                        'type': 'general',
                        'next_site': row['to_site'] or '下一站',
                        'description': f"[{est_type}] 预计 {row['avg_hours']:.1f} 小时后{action_text}",
                        'hours': round(row['avg_hours'], 1),
                        'confidence': confidence,
                        'confidence_level': '高' if confidence >= 5 else ('中' if confidence >= 2 else '低'),
                        'is_same_company': is_same,
                        'company': row['company_code']
                    })
        
        # 按置信度排序，同公司优先
        estimates.sort(key=lambda x: (x.get('is_same_company', False), x.get('confidence', 0)), reverse=True)
        
        return estimates
    
    def _get_action_text(self, action_type: str) -> str:
        """获取动作类型文本"""
        action_map = {
            'arrive': '到达',
            'depart': '离开',
            'delivering': '开始派送',
            'signed': '签收',
            'pickup': '揽收',
            'arrived_pickup': '到达取件点'
        }
        return action_map.get(action_type, '状态更新')
    
    def get_site_timeline_analysis(self, express_data: Dict) -> Dict:
        """
        获取站点时间轴分析（详细版）
        包含每个站点的到达/离开时间和停留时长
        """
        track_list = express_data.get('data', [])
        if not track_list:
            return {'error': '无物流数据'}
            
        nodes = self.extract_nodes_from_track(track_list)
        if len(nodes) < 2:
            return {'error': '节点不足，无法分析'}
        
        # 按站点聚合
        site_timeline = []
        current_site = None
        site_start_time = None
        site_events = []
        
        for node in nodes:
            site_name = node['site_name'] or node['city'] or '未知地点'
            
            if site_name != current_site:
                # 保存上一个站点的信息
                if current_site and site_start_time:
                    duration = (node['time'] - site_start_time).total_seconds() / 3600
                    site_timeline.append({
                        'site': current_site,
                        'city': node['city'],
                        'arrive_time': site_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'depart_time': node['time_str'] if node['action_type'] == 'depart' else None,
                        'duration_hours': round(duration, 1),
                        'events': site_events.copy()
                    })
                
                # 开始新站点
                current_site = site_name
                site_start_time = node['time']
                site_events = [node['context']]
            else:
                site_events.append(node['context'])
        
        # 添加最后一个站点
        if current_site and site_start_time:
            last_time = nodes[-1]['time']
            duration = (last_time - site_start_time).total_seconds() / 3600
            site_timeline.append({
                'site': current_site,
                'city': nodes[-1]['city'],
                'arrive_time': site_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'depart_time': None,
                'duration_hours': round(duration, 1),
                'events': site_events,
                'is_current': True
            })
        
        # 提取揽收员信息
        courier_info = {}
        for node in nodes:
            if node.get('courier_info', {}).get('name'):
                courier_info = node['courier_info']
                break
        
        return {
            'company_code': express_data.get('com', ''),
            'tracking_number': express_data.get('nu', ''),
            'total_sites': len(site_timeline),
            'site_timeline': site_timeline,
            'courier_info': courier_info,
            'total_transit_hours': sum(s['duration_hours'] for s in site_timeline),
            'current_site': site_timeline[-1]['site'] if site_timeline else None
        }


    def analyze_and_estimate(self, express_data: Dict) -> Dict:
        """
        综合分析并预估整个物流过程（增强版）
        即使节点不足，也尝试从历史数据中预估
        支持跨公司数据参考
        """
        track_list = express_data.get('data', [])
        if not track_list:
            return {'error': '无物流数据'}
            
        company_code = express_data.get('com', '')
        state = express_data.get('state', '')
        tracking_number = express_data.get('nu', '')
        
        # 提取节点
        nodes = self.extract_nodes_from_track(track_list)
        
        # 记录到历史
        self.record_node_transit(express_data)
        
        # 获取站点时间轴分析
        site_analysis = self.get_site_timeline_analysis(express_data)
        
        # 获取后续站点预估
        next_estimates = self.estimate_next_stations(express_data)
        
        # 分析结果
        result = {
            'company_code': company_code,
            'tracking_number': tracking_number,
            'state': state,
            'is_signed': state == '3',
            'total_nodes': len(nodes),
            'segments': [],
            'site_timeline': site_analysis.get('site_timeline', []),
            'courier_info': site_analysis.get('courier_info', {}),
            'summary': {
                'total_transit_hours': 0,
                'total_dwell_hours': 0,
                'cities_visited': [],
                'sites_visited': [],
                'key_milestones': []
            },
            'estimations': {
                'next_stations': next_estimates,
                'remaining_estimate': None,
                'final_estimate': None,
                'from_history': [],           # 同公司预估
                'cross_company_estimates': []  # 跨公司参考
            }
        }
        
        # ========== 即使节点不足，也从历史数据中查找预估 ==========
        if len(nodes) >= 1:
            last_node = nodes[-1]
            current_city = last_node['city']
            current_site = last_node['site_name']
            current_action = last_node['action_type']
            
            estimates_found = False
            
            # 1. 查询从当前站点出发的下一站（不限公司）
            if current_site:
                sql_next = """
                SELECT to_site, to_city, company_code, AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples
                FROM node_transit_history
                WHERE from_site = ? AND to_site != ''
                GROUP BY to_site, to_city, company_code
                ORDER BY total_samples DESC, avg_hours
                LIMIT 10
                """
                results = self.db_manager.execute_query(sql_next, (current_site,))
                
                same_company_estimates = []
                cross_company_estimates = []
                
                for row in results:
                    if row['to_site'] and row['avg_hours']:
                        confidence = row['total_samples'] or 1
                        is_same_company = (row['company_code'] == company_code)
                        est_type = '同公司' if is_same_company else '跨公司参考'
                        
                        estimate = {
                            'type': 'next_station',
                            'next_site': row['to_site'],
                            'city': row['to_city'],
                            'description': f"[{est_type}] 预计 {row['avg_hours']:.1f} 小时后到达 {row['to_site']}",
                            'hours': round(row['avg_hours'], 1),
                            'confidence': confidence,
                            'confidence_level': '高' if confidence >= 5 else ('中' if confidence >= 2 else '低'),
                            'company': row['company_code'],
                            'is_same_company': is_same_company
                        }
                        
                        if is_same_company:
                            same_company_estimates.append(estimate)
                        else:
                            cross_company_estimates.append(estimate)
                        
                        estimates_found = True
                
                # 同公司优先，按置信度排序
                same_company_estimates.sort(key=lambda x: x['confidence'], reverse=True)
                cross_company_estimates.sort(key=lambda x: x['confidence'], reverse=True)
                
                result['estimations']['from_history'] = same_company_estimates[:5]
                result['estimations']['cross_company_estimates'] = cross_company_estimates[:5]
            
            # 2. 如果没有找到任何站点数据，尝试只按城市查询（不限公司）
            if not estimates_found and current_city:
                sql_city = """
                SELECT to_city, company_code, AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples
                FROM node_transit_history
                WHERE from_city = ? AND to_city != '' AND to_city != from_city
                GROUP BY to_city, company_code
                ORDER BY total_samples DESC, avg_hours
                LIMIT 10
                """
                results = self.db_manager.execute_query(sql_city, (current_city,))
                
                same_company_estimates = []
                cross_company_estimates = []
                
                for row in results:
                    if row['to_city'] and row['avg_hours']:
                        confidence = row['total_samples'] or 1
                        is_same_company = (row['company_code'] == company_code)
                        est_type = '同公司' if is_same_company else '跨公司参考'
                        
                        estimate = {
                            'type': 'next_city',
                            'next_city': row['to_city'],
                            'description': f"[{est_type}] 从 {current_city} 到 {row['to_city']} 预计 {row['avg_hours']:.1f} 小时",
                            'hours': round(row['avg_hours'], 1),
                            'confidence': confidence,
                            'confidence_level': '高' if confidence >= 5 else ('中' if confidence >= 2 else '低'),
                            'company': row['company_code'],
                            'is_same_company': is_same_company
                        }
                        
                        if is_same_company:
                            same_company_estimates.append(estimate)
                        else:
                            cross_company_estimates.append(estimate)
                        
                        estimates_found = True
                
                same_company_estimates.sort(key=lambda x: x['confidence'], reverse=True)
                cross_company_estimates.sort(key=lambda x: x['confidence'], reverse=True)
                
                result['estimations']['from_history'] = same_company_estimates[:5]
                result['estimations']['cross_company_estimates'] = cross_company_estimates[:5]
            
            # 3. 预估签收时间（不限公司）
            if state != '3':  # 未签收
                sql_sign = """
                SELECT AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples, company_code
                FROM node_transit_history
                WHERE from_site = ? AND action_type = 'signed'
                GROUP BY company_code
                ORDER BY total_samples DESC
                LIMIT 1
                """
                search_term = current_site if current_site else current_city
                results = self.db_manager.execute_query(sql_sign, (search_term,))
                
                if not results and current_city:
                    # 如果按站点没找到，尝试按城市
                    sql_sign_city = """
                    SELECT AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples, company_code
                    FROM node_transit_history
                    WHERE from_city = ? AND action_type = 'signed'
                    GROUP BY company_code
                    ORDER BY total_samples DESC
                    LIMIT 1
                    """
                    results = self.db_manager.execute_query(sql_sign_city, (current_city,))
                
                if results and results[0]['avg_hours']:
                    avg_hours = results[0]['avg_hours']
                    total_samples = results[0]['total_samples'] or 1
                    est_company = results[0].get('company_code', '')
                    is_same = (est_company == company_code)
                    est_type = '同公司' if is_same else '跨公司参考'
                    
                    result['estimations']['final_estimate'] = {
                        'hours': round(avg_hours, 1),
                        'note': f"[{est_type}] 基于{total_samples}次历史数据，预计{avg_hours:.1f}小时后签收",
                        'confidence': total_samples,
                        'confidence_level': '高' if total_samples >= 5 else ('中' if total_samples >= 2 else '低'),
                        'is_same_company': is_same,
                        'company': est_company
                    }
                
                # 如果还是没有，尝试从 delivery_history 表查询
                if not result['estimations']['final_estimate'] and current_city:
                    sql_delivery = """
                    SELECT AVG((julianday(sign_time) - julianday(pickup_time)) * 24) as avg_hours, 
                        COUNT(*) as count, company_code
                    FROM delivery_history 
                    WHERE dest_city = ? AND sign_time IS NOT NULL AND pickup_time IS NOT NULL
                    GROUP BY company_code
                    ORDER BY count DESC
                    LIMIT 1
                    """
                    results = self.db_manager.execute_query(sql_delivery, (current_city,))
                    if results and results[0]['avg_hours'] and results[0]['avg_hours'] > 0:
                        avg_hours = round(results[0]['avg_hours'], 1)
                        count = results[0]['count']
                        est_company = results[0].get('company_code', '')
                        is_same = (est_company == company_code)
                        est_type = '同公司' if is_same else '跨公司参考'
                        
                        result['estimations']['final_estimate'] = {
                            'hours': avg_hours,
                            'note': f"[{est_type}] 基于{count}次该城市签收记录，预计{avg_hours}小时后签收",
                            'confidence': count,
                            'confidence_level': '高' if count >= 5 else ('中' if count >= 2 else '低'),
                            'is_same_company': is_same,
                            'company': est_company
                        }
        
        # ========== 如果节点足够，计算已发生的段 ==========
        if len(nodes) >= 2:
            segments = self.calculate_node_transit_times(nodes)
            
            visited_cities = set()
            visited_sites = set()
            total_transit = 0
            total_dwell = 0
            
            # 分析每个段
            for seg in segments:
                seg_info = {
                    'from_city': seg['from_city'] or '未知',
                    'to_city': seg['to_city'] or '未知',
                    'from_site': seg['from_site'] or '未知',
                    'to_site': seg['to_site'] or '未知',
                    'hours': seg['hours'],
                    'is_dwell': seg['is_dwell'],
                    'context': seg['context'],
                    'time_range': f"{seg['from_time']} → {seg['to_time']}"
                }
                
                if seg['from_city']:
                    visited_cities.add(seg['from_city'])
                if seg['to_city']:
                    visited_cities.add(seg['to_city'])
                if seg['from_site']:
                    visited_sites.add(seg['from_site'])
                if seg['to_site']:
                    visited_sites.add(seg['to_site'])
                    
                if seg['is_dwell']:
                    total_dwell += seg['hours']
                else:
                    total_transit += seg['hours']
                    # 尝试预估类似线路
                    if seg['from_city'] and seg['to_city']:
                        est_hours, est_note, sample = self.estimate_segment_time(
                            company_code, seg['from_city'], seg['to_city']
                        )
                        seg_info['estimate'] = {
                            'hours': est_hours,
                            'note': est_note,
                            'sample_count': sample
                        }
                        
                result['segments'].append(seg_info)
                
            # 汇总信息
            result['summary']['total_transit_hours'] = round(total_transit, 1)
            result['summary']['total_dwell_hours'] = round(total_dwell, 1)
            result['summary']['cities_visited'] = list(visited_cities)
            result['summary']['sites_visited'] = list(visited_sites)
            
            # 提取关键里程碑
            milestones = []
            for node in nodes:
                if node['action_type'] in ['pickup', 'signed', 'arrived_pickup']:
                    milestones.append({
                        'type': node['action_type'],
                        'time': node['time_str'],
                        'city': node['city'],
                        'site': node['site_name'],
                        'context': node['context']
                    })
                elif node['node_type'] == 'transit_center' and node['action_type'] == 'arrive':
                    milestones.append({
                        'type': 'arrive_transit',
                        'time': node['time_str'],
                        'city': node['city'],
                        'site': node['site_name'],
                        'context': node['context']
                    })
            result['summary']['key_milestones'] = milestones
        else:
            # 节点不足，但仍有基本信息
            if len(nodes) == 1:
                node = nodes[0]
                if node['city']:
                    result['summary']['cities_visited'] = [node['city']]
                if node['site_name']:
                    result['summary']['sites_visited'] = [node['site_name']]
                
                # 记录揽收里程碑
                if node['action_type'] == 'pickup':
                    result['summary']['key_milestones'].append({
                        'type': 'pickup',
                        'time': node['time_str'],
                        'city': node['city'],
                        'site': node['site_name'],
                        'context': node['context']
                    })
        
        return result



    def get_timeline_html(self, express_data: Dict) -> str:
        """
        生成物流时间轴HTML（用于显示）
        """
        analysis = self.analyze_and_estimate(express_data)
        
        if 'error' in analysis:
            return f"<div class='error'>{analysis['error']}</div>"
            
        html = f"""
        <div class="logistics-timeline">
            <style>
                .timeline-container {{
                    font-family: 'Microsoft YaHei', sans-serif;
                    padding: 10px;
                }}
                .timeline-title {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #4A90D9;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #4A90D9;
                }}
                .summary-cards {{
                    display: flex;
                    gap: 15px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }}
                .summary-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 12px;
                    flex: 1;
                    min-width: 120px;
                    text-align: center;
                }}
                .summary-card.blue {{
                    background: linear-gradient(135deg, #4A90D9, #357ABD);
                }}
                .summary-card.green {{
                    background: linear-gradient(135deg, #50C878, #3DA85E);
                }}
                .summary-card.orange {{
                    background: linear-gradient(135deg, #FF9800, #F57C00);
                }}
                .summary-card .value {{
                    font-size: 24px;
                    font-weight: bold;
                }}
                .summary-card .label {{
                    font-size: 12px;
                    opacity: 0.9;
                    margin-top: 5px;
                }}
                .timeline {{
                    position: relative;
                    padding-left: 30px;
                }}
                .timeline::before {{
                    content: '';
                    position: absolute;
                    left: 10px;
                    top: 0;
                    bottom: 0;
                    width: 2px;
                    background: #E0E0E0;
                }}
                .timeline-node {{
                    position: relative;
                    margin-bottom: 20px;
                    padding-left: 20px;
                }}
                .timeline-node::before {{
                    content: '';
                    position: absolute;
                    left: -24px;
                    top: 4px;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #4A90D9;
                    border: 2px solid white;
                    box-shadow: 0 0 0 2px #4A90D9;
                }}
                .timeline-node.pickup::before {{ background: #50C878; box-shadow: 0 0 0 2px #50C878; }}
                .timeline-node.signed::before {{ background: #FF9800; box-shadow: 0 0 0 2px #FF9800; }}
                .timeline-node.transit::before {{ background: #9C27B0; box-shadow: 0 0 0 2px #9C27B0; }}
                .timeline-time {{
                    font-size: 12px;
                    color: #999;
                    margin-bottom: 4px;
                }}
                .timeline-title-text {{
                    font-weight: bold;
                    font-size: 14px;
                    margin-bottom: 4px;
                }}
                .timeline-detail {{
                    font-size: 12px;
                    color: #666;
                }}
                .duration-badge {{
                    display: inline-block;
                    background: #F0F0F0;
                    border-radius: 12px;
                    padding: 2px 8px;
                    font-size: 11px;
                    margin-left: 8px;
                    color: #666;
                }}
                .estimate-badge {{
                    display: inline-block;
                    background: #E3F2FD;
                    border-radius: 12px;
                    padding: 2px 8px;
                    font-size: 11px;
                    margin-left: 8px;
                    color: #1976D2;
                }}
                .segment-card {{
                    background: #F8F9FA;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 10px 0;
                    border-left: 3px solid #4A90D9;
                }}
                .segment-title {{
                    font-weight: bold;
                    font-size: 13px;
                    margin-bottom: 5px;
                }}
                .segment-info {{
                    font-size: 12px;
                    color: #666;
                }}
                .estimate-info {{
                    font-size: 11px;
                    color: #1976D2;
                    margin-top: 5px;
                }}
            </style>
            <div class="timeline-container">
                <div class="timeline-title">📦 物流节点时间分析</div>
                
                <div class="summary-cards">
                    <div class="summary-card blue">
                        <div class="value">{analysis['total_nodes']}</div>
                        <div class="label">物流节点</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">{analysis['summary']['total_transit_hours']:.1f}h</div>
                        <div class="label">运输时间</div>
                    </div>
                    <div class="summary-card green">
                        <div class="value">{analysis['summary']['total_dwell_hours']:.1f}h</div>
                        <div class="label">停留时间</div>
                    </div>
                    <div class="summary-card orange">
                        <div class="value">{len(analysis['summary']['cities_visited'])}</div>
                        <div class="label">途经城市</div>
                    </div>
                </div>
        """
        
        # 添加预估信息
        if analysis['estimations']['final_estimate']:
            est = analysis['estimations']['final_estimate']
            html += f"""
                <div class="segment-card" style="border-left-color: #FF9800;">
                    <div class="segment-title">🎯 预计剩余时间</div>
                    <div class="segment-info">{est['note']}</div>
                </div>
            """
        
        # 添加时间轴
        nodes = self.extract_nodes_from_track(express_data.get('data', []))
        html += '<div class="timeline">'
        
        for i, node in enumerate(nodes):
            node_class = 'timeline-node'
            if node['action_type'] == 'pickup':
                node_class += ' pickup'
            elif node['action_type'] == 'signed':
                node_class += ' signed'
            elif node['node_type'] == 'transit_center':
                node_class += ' transit'
                
            # 计算到下一个节点的时间
            duration_text = ""
            if i < len(nodes) - 1:
                delta = (nodes[i+1]['time'] - node['time']).total_seconds() / 3600
                if delta >= 0.5:
                    duration_text = f'<span class="duration-badge">⏱️ {delta:.1f}小时</span>'
                    
            html += f"""
                <div class="{node_class}">
                    <div class="timeline-time">{node['time_str']} {duration_text}</div>
                    <div class="timeline-title-text">
                        {self._get_node_icon(node['action_type'])} {node['context'][:50]}
                    </div>
                    <div class="timeline-detail">
                        {'📍 ' + node['city'] if node['city'] else ''}
                        {' | ' + node['node_type'] if node['node_type'] != 'unknown' else ''}
                    </div>
                </div>
            """
            
        html += '</div></div></div>'
        
        return html
    
    def _get_node_icon(self, action_type: str) -> str:
        """获取节点图标"""
        icons = {
            'pickup': '📮',
            'depart': '🚚',
            'arrive': '📍',
            'delivering': '🚴',
            'signed': '✅',
            'status': '📋'
        }
        return icons.get(action_type, '📍')
    
    def get_detailed_analysis_text(self, express_data: Dict) -> str:
        """获取详细分析文本（用于显示）- 增强版"""
        analysis = self.analyze_and_estimate(express_data)
        
        if 'error' in analysis:
            return analysis['error']
            
        text = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                     物流节点时间分析报告（增强版）
    ╠══════════════════════════════════════════════════════════════╣
    ║ 快递单号: {analysis['tracking_number']}
    ║ 快递公司: {analysis['company_code']}
    ║ 物流状态: {'✅ 已签收' if analysis['is_signed'] else '🚚 运输中'}
    ╠══════════════════════════════════════════════════════════════╣
    ║ 统计摘要:
    ║   • 物流节点数: {analysis['total_nodes']}
    ║   • 途经站点数: {len(analysis['summary']['sites_visited'])}
    ║   • 累计运输时间: {analysis['summary']['total_transit_hours']:.1f} 小时
    ║   • 累计停留时间: {analysis['summary']['total_dwell_hours']:.1f} 小时
    """

        # 添加快递员/揽收员信息
        if analysis['courier_info'] and analysis['courier_info'].get('name'):
            text += f"║   • 揽收员: {analysis['courier_info']['name']}"
            if analysis['courier_info'].get('phone'):
                text += f" ({analysis['courier_info']['phone']})"
            text += "\n"
        
        text += "╠══════════════════════════════════════════════════════════════╣\n"
        text += "║ 站点时间轴:\n"
        
        # 添加站点时间轴
        if analysis['site_timeline']:
            for site in analysis['site_timeline']:
                marker = "📍" if site.get('is_current') else "  "
                text += f"║ {marker} {site['site']}\n"
                text += f"║     到达: {site['arrive_time']}\n"
                if site['depart_time']:
                    text += f"║     离开: {site['depart_time']}\n"
                text += f"║     停留: {site['duration_hours']:.1f} 小时\n"
                text += "║     ─────────────────────────────────\n"
        else:
            # 如果有当前站点信息，显示当前站点
            if analysis['total_nodes'] >= 1:
                text += f"║   📍 当前位置: {analysis['summary'].get('sites_visited', ['未知'])[0] if analysis['summary'].get('sites_visited') else '未知'}\n"
                text += "║     ─────────────────────────────────\n"
            else:
                text += "║   （暂无站点时间轴数据）\n"
                text += "║     ─────────────────────────────────\n"
        
        # 添加同公司历史数据预估
        if analysis['estimations']['from_history']:
            text += "\n╠══════════════════════════════════════════════════════════════╣\n"
            text += "║ 📊 同公司历史数据预估:\n"
            for est in analysis['estimations']['from_history']:
                text += f"║   • {est['description']}"
                if 'confidence' in est:
                    confidence = est['confidence']
                    confidence_icon = "🟢" if confidence >= 5 else ("🟡" if confidence >= 2 else "🔴")
                    text += f" {confidence_icon}(样本: {confidence})"
                text += "\n"
        
        # 添加跨公司参考数据
        if analysis['estimations'].get('cross_company_estimates'):
            text += "\n╠══════════════════════════════════════════════════════════════╣\n"
            text += "║ 🔄 跨公司参考数据 (仅供参考):\n"
            for est in analysis['estimations']['cross_company_estimates']:
                text += f"║   • {est['description']}"
                if 'confidence' in est:
                    confidence = est['confidence']
                    confidence_icon = "🟢" if confidence >= 5 else ("🟡" if confidence >= 2 else "🔴")
                    text += f" {confidence_icon}(样本: {confidence})"
                if 'company' in est:
                    text += f" [{est['company']}]"
                text += "\n"
        
        # 添加最终预估
        if analysis['estimations']['final_estimate']:
            est = analysis['estimations']['final_estimate']
            text += "\n╠══════════════════════════════════════════════════════════════╣\n"
            if est.get('is_same_company'):
                text += f"║ 🎯 最终预估: {est['note']}\n"
            else:
                text += f"║ 🎯 最终预估 (跨公司参考): {est['note']}\n"
        
        # 添加后续站点预估
        if analysis['estimations']['next_stations']:
            if not analysis['estimations']['from_history'] and not analysis['estimations'].get('cross_company_estimates'):
                text += "\n╠══════════════════════════════════════════════════════════════╣\n"
            text += "║ 🎯 后续站点到达预估:\n"
            for est in analysis['estimations']['next_stations']:
                text += f"║   • {est['description']} (置信度: {est['confidence_level']})\n"
        
        # 如果没有任何预估数据
        if (not analysis['estimations']['from_history'] and 
            not analysis['estimations'].get('cross_company_estimates') and
            not analysis['estimations']['next_stations'] and
            not analysis['estimations']['final_estimate']):
            text += "\n╠══════════════════════════════════════════════════════════════╣\n"
            text += "║ ℹ️ 暂无足够的历史数据用于预估\n"
            text += "║    建议：等待更多快递数据积累，或使用「数据库管理」中的\n"
            text += "║          「重建节点运输历史数据」功能来更新预估数据。\n"
        
        text += "╚══════════════════════════════════════════════════════════════╝"
        
        return text


    def estimate_arrival_to_destination(self, express_data: Dict, dest_address: str) -> Optional[Dict]:
        """
        预估到达指定收件地址的时间
        
        Args:
            express_data: 快递数据
            dest_address: 目标收件地址（城市或站点名）
        
        Returns:
            预估信息字典，包含 hours（预估小时数）、confidence（置信度）等
        """
        track_list = express_data.get('data', [])
        if not track_list:
            return None
        
        company_code = express_data.get('com', '')
        if not company_code:
            company_code = express_data.get('company_code', '')
        
        state = str(express_data.get('state', ''))
        
        # 已签收则无需预估
        if state == '3':
            return {'hours': 0, 'is_arrived': True, 'note': '已签收', 'confidence': 100}
        
        nodes = self.extract_nodes_from_track(track_list)
        if not nodes:
            return None
        
        last_node = nodes[-1]
        current_site = last_node['site_name']
        current_city = last_node['city']
        current_action = last_node['action_type']
        
        # 检查是否已经到达目标地址
        if dest_address:
            # 检查当前站点是否就是目标地址
            if current_site and dest_address in current_site:
                return {'hours': 0, 'is_arrived': True, 'note': '已到达目标站点', 'confidence': 100}
            if current_city and dest_address in current_city:
                # 检查是否在目标城市
                for node in nodes:
                    if node.get('action_type') == 'arrived_pickup' or node.get('action_type') == 'delivering':
                        return {'hours': 0, 'is_arrived': True, 'note': '已到达目标城市', 'confidence': 80}
        
        # 如果正在派送中，预估签收时间较短
        if current_action == 'delivering':
            return {'hours': 2, 'confidence': 50, 'note': '派送中，预计2小时内送达', 'is_same_company': True}
        
        estimates = []
        
        # 1. 查询从当前站点到目标地址的运输时间
        if current_site and dest_address:
            sql = """
            SELECT AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples, 
                MIN(min_hours) as min_hours, MAX(max_hours) as max_hours, company_code
            FROM node_transit_history
            WHERE from_site = ? AND (to_site LIKE ? OR to_city LIKE ?)
            GROUP BY company_code
            ORDER BY total_samples DESC
            """
            search_pattern = f"%{dest_address}%"
            results = self.db_manager.execute_query(sql, (current_site, search_pattern, search_pattern))
            
            for row in results:
                if row['avg_hours']:
                    estimates.append({
                        'hours': row['avg_hours'],
                        'confidence': row['total_samples'] or 1,
                        'is_same_company': row['company_code'] == company_code,
                        'source': '站点匹配',
                        'min_hours': row.get('min_hours'),
                        'max_hours': row.get('max_hours')
                    })
        
        # 2. 如果没找到，按城市查询
        if not estimates and current_city and dest_address:
            # 尝试从目标地址中提取城市
            dest_city = self._extract_city(dest_address)
            if not dest_city:
                dest_city = dest_address
            
            sql = """
            SELECT AVG(avg_hours) as avg_hours, SUM(sample_count) as total_samples,
                MIN(min_hours) as min_hours, MAX(max_hours) as max_hours, company_code
            FROM node_transit_history
            WHERE from_city = ? AND (to_city LIKE ? OR to_site LIKE ?)
            GROUP BY company_code
            ORDER BY total_samples DESC
            """
            results = self.db_manager.execute_query(sql, (current_city, f"%{dest_city}%", search_pattern))
            
            for row in results:
                if row['avg_hours']:
                    estimates.append({
                        'hours': row['avg_hours'],
                        'confidence': row['total_samples'] or 1,
                        'is_same_company': row['company_code'] == company_code,
                        'source': '城市匹配',
                        'min_hours': row.get('min_hours'),
                        'max_hours': row.get('max_hours')
                    })
        
        # 3. 如果还是没有，从 delivery_history 表查询同目的地的签收时间
        if not estimates and current_city:
            sql = """
            SELECT AVG((julianday(sign_time) - julianday(pickup_time)) * 24) as avg_hours, 
                COUNT(*) as count, company_code
            FROM delivery_history 
            WHERE dest_city LIKE ? AND sign_time IS NOT NULL AND pickup_time IS NOT NULL
            GROUP BY company_code
            ORDER BY count DESC
            """
            results = self.db_manager.execute_query(sql, (search_pattern,))
            
            for row in results:
                if row['avg_hours'] and row['avg_hours'] > 0:
                    # 计算已经过去的时间
                    if nodes and len(nodes) > 0:
                        first_time = nodes[0]['time']
                        elapsed_hours = (datetime.now() - first_time).total_seconds() / 3600
                        remaining_hours = max(0, row['avg_hours'] - elapsed_hours)
                    else:
                        remaining_hours = row['avg_hours']
                    
                    estimates.append({
                        'hours': remaining_hours,
                        'confidence': row['count'] or 1,
                        'is_same_company': row['company_code'] == company_code,
                        'source': '历史签收数据'
                    })
        
        # 4. 如果还是没有，按快递公司默认时效预估
        if not estimates:
            default_hours = {
                'shunfeng': 24,
                'jd': 24,
                'yuantong': 48,
                'zhongtong': 48,
                'yunda': 48,
                'shentong': 48,
                'ems': 72,
                'youzhengguo': 96,
                'jtexpress': 48,
            }
            hours = default_hours.get(company_code, 48)
            estimates.append({
                'hours': hours,
                'confidence': 1,
                'is_same_company': True,
                'source': '默认时效'
            })
        
        if estimates:
            # 优先选择同公司的预估
            same_company = [e for e in estimates if e['is_same_company']]
            if same_company:
                best = max(same_company, key=lambda x: x['confidence'])
            else:
                best = max(estimates, key=lambda x: x['confidence'])
            
            confidence = best.get('confidence', 1)
            confidence_level = '高' if confidence >= 5 else ('中' if confidence >= 2 else '低')
            
            note_parts = [f"预计 {best['hours']:.1f} 小时后到达"]
            if best.get('source'):
                note_parts.append(f"({best['source']})")
            if not best.get('is_same_company', True):
                note_parts.append("[跨公司参考]")
            
            return {
                'hours': round(best['hours'], 1),
                'confidence': confidence,
                'confidence_level': confidence_level,
                'is_same_company': best.get('is_same_company', True),
                'source': best.get('source', '未知'),
                'note': ' '.join(note_parts),
                'min_hours': best.get('min_hours'),
                'max_hours': best.get('max_hours')
            }
        
        return None


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
        
        # 检查字段是否存在再添加
        def column_exists(table_name, column_name):
            result = self.db_manager.execute_query(f"PRAGMA table_info({table_name})")
            for col in result:
                if col['name'] == column_name:
                    return True
            return False
        
        if not column_exists('delivery_history', 'arrival_time'):
            try:
                self.db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN arrival_time TEXT")
            except:
                pass
        
        if not column_exists('delivery_history', 'arrival_days'):
            try:
                self.db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN arrival_days INTEGER")
            except:
                pass
        
        if not column_exists('delivery_history', 'delivery_type'):
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
        station_keywords = [
            '驿站', '菜鸟', '丰巢', '快递柜', '自提柜', '代收点', '妈妈驿站', 
            '兔喜', '超市', '代理点', '自提', '代收', '投柜', '出柜',
            '存局', '已送达', '便利店', '物业', '门卫', '快递点', '菜鸟驿站',
            '菜鸟裹裹', '取件码', '凭取件码', '请取件', '可取件', '待取件',
            '快递超市', '邻里驿站', '熊猫快收', '速递易', '云柜', '日日顺',
            '蜂巢', 'e栈', '收件宝', '近邻宝', '格格货栈', '乐收'
        ]
        context_lower = context.lower()
        for keyword in station_keywords:
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
        if len(track_list) < 1:
            if DEBUG_MODE:
                print(f"  [记录时效] 跳过 {tracking_num}: 无物流轨迹")
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
            
            # 找揽收 - 优先找明确的揽收记录
            if not pickup_time and ('揽收' in context or '已揽件' in context or '收件' in context or '取件' in context):
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
        
        # 如果没找到明确的揽收时间，但有物流轨迹
        if not pickup_time and track_list:
            # 使用第一条轨迹的时间作为揽收时间
            first_track = track_list[0]
            pickup_time = first_track.get('time', '')
            origin_city = self.extract_city(first_track.get('context', ''))
            
            if DEBUG_MODE:
                print(f"  [记录时效] {tracking_num}: 未找到明确揽收记录，使用第一条轨迹时间 {pickup_time}")
        
        if not pickup_time:
            if DEBUG_MODE:
                print(f"  [记录时效] 跳过 {tracking_num}: 无法确定揽收时间")
            return
            
        # 确定终点时间
        end_time = sign_time if sign_time else arrival_time
        if not end_time:
            if DEBUG_MODE:
                print(f"  [记录时效] 跳过 {tracking_num}: 无法确定终点时间（未签收且未到驿站）")
            return
            
        # 计算天数差
        try:
            pickup_dt = datetime.strptime(pickup_time, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            delivery_days = (end_dt - pickup_dt).days
            if delivery_days < 0:
                delivery_days = 0
        except Exception as e:
            if DEBUG_MODE:
                print(f"  [记录时效] 跳过 {tracking_num}: 时间解析失败 {e}")
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
        
        if DEBUG_MODE:
            print(f"  [记录时效] 成功记录 {tracking_num}: {origin_city}->{dest_city}, {delivery_days}天")
        
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
        self.fixed_order = False  # 是否固定排序
        self.load_accounts()
        self.check_and_reset_daily_usage()  # 初始化时检查是否需要重置
        
    def load_fixed_order_setting(self) -> bool:
        """加载固定排序设置"""
        sql = "SELECT value FROM user_settings WHERE key = 'fixed_account_order'"
        result = self.db_manager.execute_query(sql)
        return (result and result[0]['value'] == '1')
        
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
        """加载所有账号"""
        # 刷新固定排序设置
        self.fixed_order = self.load_fixed_order_setting()
        
        # ========== 保存当前账号ID ==========
        current_id = self.current_account['id'] if self.current_account else None
        # ======================================
        
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
        
        # ========== 恢复当前账号 ==========
        if current_id:
            # 在 accounts 列表中查找之前保存的账号
            found = False
            for acc in self.accounts:
                if acc['id'] == current_id:
                    self.current_account = acc
                    found = True
                    break
            # 如果之前的账号不在列表中（可能被删除），才使用第一个
            if not found:
                if self.accounts:
                    self.current_account = self.accounts[0]
                else:
                    self.current_account = None
        else:
            if self.accounts:
                self.current_account = self.accounts[0]
            else:
                self.current_account = None

            
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
            
        # 刷新固定排序设置
        self.fixed_order = self.load_fixed_order_setting()
        
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
            print(f"[账号切换] 当前账号: {current_name}, 总数: {total}, 强制切换: {force_switch}, 固定排序: {self.fixed_order}")
        
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
                    old_account = self.current_account
                    self.current_account = account
                    self._refresh_single_account(account['id'])
                    
                    # ========== 关键修改：如果未启用固定排序，将新账号移到第一位 ==========
                    if not self.fixed_order:
                        self._move_account_to_first(account['id'])
                        # 重新加载账号列表以更新排序
                        self.load_accounts()
                    # ============================================================
                    
                    if DEBUG_MODE:
                        print(f"[账号切换] 强制切换到账号: {account_name}")
                    return True
            else:
                # 正常切换：检查账号是否可用（额度未用完）
                used_today = account.get('used_today', 0)
                daily_limit = account.get('daily_limit', 100)
                
                if used_today < daily_limit:
                    old_account = self.current_account
                    self.current_account = account
                    self._refresh_single_account(account['id'])
                    
                    # ========== 关键修改：如果未启用固定排序，将新账号移到第一位 ==========
                    if not self.fixed_order:
                        self._move_account_to_first(account['id'])
                        # 重新加载账号列表以更新排序
                        self.load_accounts()
                    # ============================================================
                    
                    if DEBUG_MODE:
                        print(f"[账号切换] 正常切换到账号: {account_name} ({used_today}/{daily_limit})")
                    return True
                else:
                    if DEBUG_MODE:
                        print(f"[账号切换] 账号 {account_name} 额度已满 ({used_today}/{daily_limit})，跳过")
        
        if DEBUG_MODE:
            print("[账号切换] 没有可切换的账号")
        return False

    def _move_account_to_first(self, account_id: int):
        """将指定账号移到排序的第一位"""
        try:
            # 先将所有账号的 sort_order 加 1
            sql1 = "UPDATE api_accounts SET sort_order = sort_order + 1"
            self.db_manager.execute_update(sql1)
            
            # 将目标账号的 sort_order 设为 0
            sql2 = "UPDATE api_accounts SET sort_order = 0 WHERE id = ?"
            self.db_manager.execute_update(sql2, (account_id,))
            
            if DEBUG_MODE:
                print(f"[排序调整] 已将账号 ID={account_id} 移到第一位")
        except Exception as e:
            if DEBUG_MODE:
                print(f"[排序调整失败] {e}")

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



# ==================== API接口配置管理 ====================
class ApiEndpointManager:
    """API接口配置管理器 - 支持多个API接口切换"""
    
    # 快递100收费接口
    KUAIDI100_PAID = {
        'name': '快递100收费接口',
        'type': 'paid',
        'url': 'https://poll.kuaidi100.com/poll/query.do',
        'description': '快递100官方收费接口，需要Customer和Auth Key，稳定性高，支持自动切换账号'
    }
    
    # 快递100免费接口
    KUAIDI100_FREE = {
        'name': '快递100免费接口',
        'type': 'free',
        'url': 'https://www.kuaidi100.com/query',
        'description': '快递100官方免费查询接口，无需认证，但有频率限制，适合少量查询'
    }
    
    def __init__(self, db_manager: DatabaseManagerPro):
        self.db_manager = db_manager
        self.current_endpoint = None
        self.init_endpoint_table()
        self.load_current_endpoint()
        
    def init_endpoint_table(self):
        """初始化API接口配置表"""
        sql = """
        CREATE TABLE IF NOT EXISTS api_endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            endpoint_type TEXT NOT NULL,
            url TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_current INTEGER DEFAULT 0,
            description TEXT,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute_update(sql)
        
        # 检查是否有默认配置（只检查表是否有记录，而不是检查 is_active 的数量）
        check_sql = "SELECT COUNT(*) as count FROM api_endpoints"
        result = self.db_manager.execute_query(check_sql)
        
        if result and result[0]['count'] == 0:
            # 插入默认接口配置
            default_endpoints = [
                (self.KUAIDI100_PAID['name'], 'paid', self.KUAIDI100_PAID['url'], 1, 
                self.KUAIDI100_PAID['description'], 100),
                (self.KUAIDI100_FREE['name'], 'free', self.KUAIDI100_FREE['url'], 0,
                self.KUAIDI100_FREE['description'], 50),
            ]
            
            for endpoint in default_endpoints:
                insert_sql = """
                INSERT INTO api_endpoints (name, endpoint_type, url, is_current, description, priority)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                self.db_manager.execute_update(insert_sql, endpoint)
            
            # 设置收费接口为当前使用
            self.db_manager.execute_update(
                "UPDATE api_endpoints SET is_current = 1 WHERE name = ?", 
                (self.KUAIDI100_PAID['name'],)
            )
            if DEBUG_MODE:
                print("[接口初始化] 数据库为空，插入默认接口配置")
        else:
            if DEBUG_MODE:
                print(f"[接口初始化] 数据库已有 {result[0]['count']} 条接口记录，保留现有配置")
    
    def load_current_endpoint(self):
        """加载当前使用的API接口"""
        sql = """
        SELECT * FROM api_endpoints 
        WHERE is_current = 1 AND is_active = 1
        LIMIT 1
        """
        result = self.db_manager.execute_query(sql)
        
        if result:
            self.current_endpoint = result[0]
            if DEBUG_MODE:
                print(f"[接口加载] 从数据库加载当前接口: {self.current_endpoint.get('name')}")
        else:
            # 如果没有当前接口，选择优先级最高的
            sql = """
            SELECT * FROM api_endpoints 
            WHERE is_active = 1
            ORDER BY priority DESC, id
            LIMIT 1
            """
            result = self.db_manager.execute_query(sql)
            if result:
                self.current_endpoint = result[0]
                if DEBUG_MODE:
                    print(f"[接口加载] 没有当前接口，使用优先级最高的: {self.current_endpoint.get('name')}")
                    
        return self.current_endpoint
    
    def get_current_endpoint(self) -> Dict:
        """获取当前API接口"""
        if not self.current_endpoint:
            self.load_current_endpoint()
        return self.current_endpoint
    
    def set_current_endpoint(self, endpoint_id: int) -> bool:
        """设置当前使用的API接口"""
        try:
            # 清除所有接口的 is_current 标记
            self.db_manager.execute_update("UPDATE api_endpoints SET is_current = 0")
            # 设置新的当前接口
            sql = "UPDATE api_endpoints SET is_current = 1 WHERE id = ?"
            result = self.db_manager.execute_update(sql, (endpoint_id,))
            
            if result:
                self.load_current_endpoint()
            return result
        except Exception as e:
            if DEBUG_MODE:
                print(f"设置API接口失败: {e}")
            return False
    
    def get_all_endpoints(self) -> List[Dict]:
        """获取所有API接口"""
        sql = """
        SELECT * FROM api_endpoints 
        WHERE is_active = 1
        ORDER BY priority DESC, id
        """
        return self.db_manager.execute_query(sql)
    
    def add_endpoint(self, name: str, endpoint_type: str, url: str, description: str = "") -> bool:
        """添加新的API接口"""
        try:
            # 获取最大优先级
            max_priority_sql = "SELECT MAX(priority) as max_priority FROM api_endpoints"
            result = self.db_manager.execute_query(max_priority_sql)
            max_priority = result[0]['max_priority'] if result and result[0]['max_priority'] else 0
            priority = max_priority - 10  # 新接口优先级较低
            
            sql = """
            INSERT INTO api_endpoints (name, endpoint_type, url, description, priority)
            VALUES (?, ?, ?, ?, ?)
            """
            return self.db_manager.execute_update(sql, (name, endpoint_type, url, description, priority))
        except Exception as e:
            if DEBUG_MODE:
                print(f"添加API接口失败: {e}")
            return False
    
    def update_endpoint(self, endpoint_id: int, name: str, url: str, description: str) -> bool:
        """更新API接口"""
        sql = """
        UPDATE api_endpoints 
        SET name = ?, url = ?, description = ?
        WHERE id = ?
        """
        return self.db_manager.execute_update(sql, (name, url, description, endpoint_id))
    
    def delete_endpoint(self, endpoint_id: int) -> bool:
        """删除API接口（软删除）"""
        sql = "UPDATE api_endpoints SET is_active = 0 WHERE id = ?"
        return self.db_manager.execute_update(sql, (endpoint_id,))
    
    def get_endpoint_type_name(self, endpoint_type: str) -> str:
        """获取接口类型名称"""
        type_map = {
            'paid': '💰 收费接口',
            'free': '🆓 免费接口',
            'custom': '🔧 自定义接口'
        }
        return type_map.get(endpoint_type, '📦 其他接口')

class ApiEndpointDialog(QDialog):
    """API接口管理对话框"""
    
    def __init__(self, endpoint_manager: ApiEndpointManager, parent=None):
        super().__init__(parent)
        self.endpoint_manager = endpoint_manager
        self.endpoints = []
        self.init_ui()
        self.load_endpoints()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle("API接口管理")
        self.setMinimumSize(800, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        info_label = QLabel(
            "管理快递查询API接口，支持收费接口和免费接口切换。\n"
            "收费接口需要配置Customer和Auth Key，稳定性高；免费接口无需认证，但有频率限制。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; padding: 5px;")
        layout.addWidget(info_label)
        
        # 接口列表
        list_group = QGroupBox("API接口列表")
        list_layout = QVBoxLayout()
        
        self.endpoint_table = QTableWidget()
        self.endpoint_table.setColumnCount(6)
        self.endpoint_table.setHorizontalHeaderLabels([
            "接口名称", "类型", "API地址", "状态", "当前使用", "操作"
        ])
        self.endpoint_table.horizontalHeader().setStretchLastSection(True)
        self.endpoint_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.endpoint_table.setAlternatingRowColors(True)
        
        list_layout.addWidget(self.endpoint_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加自定义接口")
        add_btn.clicked.connect(self.add_endpoint)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ 编辑接口")
        edit_btn.clicked.connect(self.edit_endpoint)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ 删除接口")
        delete_btn.clicked.connect(self.delete_endpoint)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_endpoints(self):
        """加载接口列表"""
        self.endpoints = self.endpoint_manager.get_all_endpoints()
        self.update_table()
    
    def update_table(self):
        """更新表格"""
        self.endpoint_table.setRowCount(len(self.endpoints))
        current_endpoint = self.endpoint_manager.get_current_endpoint()
        current_id = current_endpoint.get('id') if current_endpoint else None
        
        for row, endpoint in enumerate(self.endpoints):
            # 接口名称
            name_item = QTableWidgetItem(endpoint.get('name', ''))
            self.endpoint_table.setItem(row, 0, name_item)
            
            # 类型
            type_name = self.endpoint_manager.get_endpoint_type_name(endpoint.get('endpoint_type', 'custom'))
            type_item = QTableWidgetItem(type_name)
            if endpoint.get('endpoint_type') == 'free':
                type_item.setForeground(QColor(0, 150, 0))
            elif endpoint.get('endpoint_type') == 'paid':
                type_item.setForeground(QColor(255, 165, 0))
            self.endpoint_table.setItem(row, 1, type_item)
            
            # API地址
            url = endpoint.get('url', '')
            display_url = url[:50] + '...' if len(url) > 50 else url
            self.endpoint_table.setItem(row, 2, QTableWidgetItem(display_url))
            
            # 状态
            status = "启用" if endpoint.get('is_active', 1) else "禁用"
            status_item = QTableWidgetItem(status)
            if endpoint.get('is_active', 1):
                status_item.setForeground(QColor(0, 150, 0))
            else:
                status_item.setForeground(QColor(255, 0, 0))
            self.endpoint_table.setItem(row, 3, status_item)
            
            # 当前使用
            is_current = (endpoint.get('id') == current_id)
            current_item = QTableWidgetItem("✅ 当前使用" if is_current else "")
            if is_current:
                current_item.setForeground(QColor(0, 150, 0))
            self.endpoint_table.setItem(row, 4, current_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            if not is_current and endpoint.get('is_active', 1):
                switch_btn = QPushButton("切换到此接口")
                switch_btn.clicked.connect(lambda checked, e=endpoint: self.switch_to_endpoint(e))
                btn_layout.addWidget(switch_btn)
            
            btn_widget.setLayout(btn_layout)
            self.endpoint_table.setCellWidget(row, 5, btn_widget)
        
        self.endpoint_table.resizeColumnsToContents()
    
    def switch_to_endpoint(self, endpoint: Dict):
        """切换到指定接口"""
        reply = QMessageBox.question(
            self, "确认切换",
            f"确定要切换到接口「{endpoint.get('name')}」吗？\n\n"
            f"接口类型: {self.endpoint_manager.get_endpoint_type_name(endpoint.get('endpoint_type', 'custom'))}\n"
            f"API地址: {endpoint.get('url')}\n\n"
            f"{'⚠️ 免费接口可能有频率限制，适合少量查询。' if endpoint.get('endpoint_type') == 'free' else '收费接口需要配置有效的Customer和Auth Key。'}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.endpoint_manager.set_current_endpoint(endpoint['id']):
                QMessageBox.information(self, "成功", f"已切换到接口「{endpoint.get('name')}」")
                self.load_endpoints()
                
                # 通知主窗口刷新
                if hasattr(self.parent(), 'refresh_api_endpoint'):
                    self.parent().refresh_api_endpoint()
            else:
                QMessageBox.critical(self, "失败", "切换接口失败")
    
    def add_endpoint(self):
        """添加自定义接口"""
        dialog = ApiEndpointEditDialog(self.endpoint_manager, None, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_endpoints()
    
    def edit_endpoint(self):
        """编辑接口"""
        row = self.endpoint_table.currentRow()
        if row < 0 or row >= len(self.endpoints):
            QMessageBox.warning(self, "提示", "请先选择要编辑的接口")
            return
        
        endpoint = self.endpoints[row]
        # 只允许编辑自定义接口
        if endpoint.get('endpoint_type') == 'custom':
            dialog = ApiEndpointEditDialog(self.endpoint_manager, endpoint, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_endpoints()
        else:
            QMessageBox.information(self, "提示", "预设接口不可编辑，如需修改请添加自定义接口")
    
    def delete_endpoint(self):
        """删除接口"""
        row = self.endpoint_table.currentRow()
        if row < 0 or row >= len(self.endpoints):
            QMessageBox.warning(self, "提示", "请先选择要删除的接口")
            return
        
        endpoint = self.endpoints[row]
        
        # 检查是否是当前使用的接口
        current = self.endpoint_manager.get_current_endpoint()
        if current and current.get('id') == endpoint.get('id'):
            QMessageBox.warning(self, "提示", "不能删除当前正在使用的接口，请先切换到其他接口")
            return
        
        # 只允许删除自定义接口
        if endpoint.get('endpoint_type') != 'custom':
            QMessageBox.warning(self, "提示", "预设接口不可删除")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除接口「{endpoint.get('name')}」吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.endpoint_manager.delete_endpoint(endpoint['id']):
                self.load_endpoints()
                QMessageBox.information(self, "成功", "接口已删除")
            else:
                QMessageBox.critical(self, "失败", "删除接口失败")

class ApiEndpointEditDialog(QDialog):
    """API接口编辑对话框"""
    
    def __init__(self, endpoint_manager: ApiEndpointManager, endpoint: Dict = None, parent=None):
        super().__init__(parent)
        self.endpoint_manager = endpoint_manager
        self.endpoint = endpoint
        self.init_ui()
        
        if endpoint:
            self.load_data()
        
        self.setStyleSheet(MacaronStyle.get_main_style())
    
    def init_ui(self):
        title = "编辑自定义接口" if self.endpoint else "添加自定义接口"
        self.setWindowTitle(title)
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：我的自定义API")
        form_layout.addRow("接口名称:", self.name_edit)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://api.example.com/query")
        form_layout.addRow("API地址:", self.url_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("接口描述、注意事项等")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("描述:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        info_label = QLabel(
            "提示：自定义接口需要返回JSON格式数据，建议包含 nu、com、state、data 字段。\n"
            "如果不确定格式，建议使用预设的收费或免费接口。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px; padding: 5px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_endpoint)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """加载数据"""
        if self.endpoint:
            self.name_edit.setText(self.endpoint.get('name', ''))
            self.url_edit.setText(self.endpoint.get('url', ''))
            self.description_edit.setText(self.endpoint.get('description', ''))
    
    def save_endpoint(self):
        """保存接口"""
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "提示", "请输入接口名称")
            return
        
        if not url:
            QMessageBox.warning(self, "提示", "请输入API地址")
            return
        
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "提示", "API地址应以 http:// 或 https:// 开头")
            return
        
        if self.endpoint:
            # 编辑
            if self.endpoint_manager.update_endpoint(self.endpoint['id'], name, url, description):
                self.accept()
            else:
                QMessageBox.critical(self, "失败", "保存接口失败")
        else:
            # 新增
            if self.endpoint_manager.add_endpoint(name, 'custom', url, description):
                self.accept()
            else:
                QMessageBox.critical(self, "失败", "添加接口失败")



class ApiAccountDialog(DialogWithStatusBar):
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
        self.setMinimumSize(950, 650)
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
        
        # ========== 修改后的自动切换设置区域 ==========
        switch_group = QGroupBox("自动切换设置")
        switch_layout = QVBoxLayout()
        
        # 第一行：自动切换复选框
        switch_row1 = QHBoxLayout()
        self.auto_switch_check = QCheckBox("启用额度用完自动切换账号")
        self.auto_switch_check.setToolTip("当当前账号今日额度用完时，自动切换到下一个可用账号")
        switch_row1.addWidget(self.auto_switch_check)
        switch_row1.addStretch()
        switch_layout.addLayout(switch_row1)
        
        # 第二行：固定排序复选框
        switch_row2 = QHBoxLayout()
        self.fixed_order_check = QCheckBox("固定排序（切换账号时不自动调整顺序）")
        self.fixed_order_check.setToolTip("启用后，切换账号或设为当前使用时不会自动调整账号排序，保持手动设置的顺序")
        switch_row2.addWidget(self.fixed_order_check)
        switch_row2.addStretch()
        switch_layout.addLayout(switch_row2)
        
        switch_group.setLayout(switch_layout)
        layout.addWidget(switch_group)
        # ========== 修改结束 ==========
        
        bottom_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        bottom_layout.addWidget(save_btn)
        
        bottom_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setup_status_bar(layout)

        self.setLayout(layout)
        self.load_auto_switch_setting()
        
    def load_accounts(self):
        """加载账号列表（仅用于对话框显示，不影响主窗口当前账号）"""
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
            self.show_status("⚠️ 请先选择要编辑的账号", 3000)
            return
            
        account = self.accounts[row]
        dialog = ApiAccountEditDialog(self.db_manager, account, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_accounts()
            self.show_status("✅ 账号已更新", 2000)
            
    def delete_account(self):
        row = self.account_table.currentRow()
        if row < 0 or row >= len(self.accounts):
            self.show_status("⚠️ 请先选择要删除的账号", 3000)
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
            self.show_status("✅ 账号已删除", 2000)
            
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
        """设为当前使用账号"""
        row = self.account_table.currentRow()
        if row < 0 or row >= len(self.accounts):
            self.show_status("⚠️ 请先选择要设为当前的账号", 3000)
            return
            
        account = self.accounts[row]
        
        sql = "SELECT value FROM user_settings WHERE key = 'fixed_account_order'"
        result = self.db_manager.execute_query(sql)
        fixed_order = (result and result[0]['value'] == '1')
        
        if not fixed_order:
            sql1 = "UPDATE api_accounts SET sort_order = sort_order + 1"
            self.db_manager.execute_update(sql1)
            
            sql2 = "UPDATE api_accounts SET sort_order = 0 WHERE id = ?"
            self.db_manager.execute_update(sql2, (account['id'],))
        
        # ========== 从主窗口获取 api_account_manager ==========
        from PySide6.QtWidgets import QApplication
        
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ExpressQueryProGUI':
                main_window = widget
                break
        
        if main_window and hasattr(main_window, 'api_account_manager'):
            am = main_window.api_account_manager
            
            # 1. 直接设置 current_account 为目标账号
            am.current_account = account
            
            # 2. 只刷新列表数据，不改变 current_account
            am._refresh_accounts_list()
            
            # 3. 更新主窗口的 customer 和 key
            main_window.customer = account.get('customer', '')
            main_window.key = account.get('auth_key', '')
            main_window.update_api_account_display()
            
            if DEBUG_MODE:
                print(f"[设为当前] 已切换到账号: {account.get('account_name', '')} (ID={account['id']})")
        
        # 4. 只刷新对话框自己的账号列表显示，不触发 ApiAccountManager 的 load_accounts
        query = """
        SELECT * FROM api_accounts 
        WHERE is_active = 1 
        ORDER BY sort_order, id
        """
        self.accounts = self.db_manager.execute_query(query)
        self.update_table()
        
        self.show_status(f"✅ 已将 '{account['account_name']}' 设为当前使用账号", 3000)
        
    def reset_usage(self, row: int):
        if row < 0 or row >= len(self.accounts):
            return
            
        account = self.accounts[row]
        sql = "UPDATE api_accounts SET used_today = 0, last_used = NULL, last_used_date = NULL WHERE id = ?"
        self.db_manager.execute_update(sql, (account['id'],))
        self.load_accounts()
        self.show_status(f"✅ 账号 '{account['account_name']}' 额度已重置", 2000)
        
    def load_auto_switch_setting(self):
        """加载自动切换设置"""
        sql = "SELECT value FROM user_settings WHERE key = 'auto_switch_account'"
        result = self.db_manager.execute_query(sql)
        if result:
            self.auto_switch_check.setChecked(result[0]['value'] == '1')
        
        # 加载固定排序设置
        sql2 = "SELECT value FROM user_settings WHERE key = 'fixed_account_order'"
        result2 = self.db_manager.execute_query(sql2)
        if result2:
            self.fixed_order_check.setChecked(result2[0]['value'] == '1')
            
    def save_settings(self):
        """保存设置"""
        auto_switch = '1' if self.auto_switch_check.isChecked() else '0'
        sql1 = "INSERT OR REPLACE INTO user_settings (key, value) VALUES ('auto_switch_account', ?)"
        self.db_manager.execute_update(sql1, (auto_switch,))
        
        fixed_order = '1' if self.fixed_order_check.isChecked() else '0'
        sql2 = "INSERT OR REPLACE INTO user_settings (key, value) VALUES ('fixed_account_order', ?)"
        self.db_manager.execute_update(sql2, (fixed_order,))
        
        self.show_status("✅ 设置已保存", 2000)

    def export_accounts(self):
        """导出所有账号到JSON文件"""
        if not self.accounts:
            self.show_status("ℹ️ 没有可导出的账号", 3000)
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出API账号", 
            f"api_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
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
                    export_account['customer'] = account.get('customer', '')
                    export_account['auth_key'] = account.get('auth_key', '')
                    export_account['secret'] = account.get('secret', '')
                    export_account['userid'] = account.get('userid', '')
                else:
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
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.show_status(f"✅ 已导出 {len(self.accounts)} 个账号", 3000)
                
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
            
            if 'accounts' not in import_data:
                self.parent_gui.status_bar.showMessage("❌ 无效的账号文件格式", 5000)
                return
            
            accounts_to_import = import_data['accounts']
            include_secrets = import_data.get('include_secrets', False)
            
            if not accounts_to_import:
                self.parent_gui.status_bar.showMessage("✅ 文件中没有账号数据", 3000)
                return
            
            has_secrets = any('customer' in acc and 'auth_key' in acc and 
                            '****' not in str(acc.get('customer', '')) and 
                            '****' not in str(acc.get('auth_key', '')) 
                            for acc in accounts_to_import)
            
            if not has_secrets and include_secrets:
                QMessageBox.warning(self, "提示", 
                    "文件中的密钥信息已隐藏，无法导入完整账号。\n"
                    "请使用包含完整密钥的备份文件。")
                return
            
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
            
            existing_names = set()
            if not replace_existing:
                query = "SELECT account_name FROM api_accounts WHERE is_active = 1"
                existing = self.db_manager.execute_query(query)
                existing_names = {acc['account_name'] for acc in existing}
            
            import_count = 0
            skip_count = 0
            
            if replace_existing:
                sql = "UPDATE api_accounts SET is_active = 0"
                self.db_manager.execute_update(sql)
                
                sort_order = 0
                for account in accounts_to_import:
                    account_name = account.get('account_name', '').strip()
                    if not account_name:
                        skip_count += 1
                        continue
                    
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
                query = "SELECT MAX(sort_order) as max_order FROM api_accounts WHERE is_active = 1"
                result = self.db_manager.execute_query(query)
                max_order = result[0]['max_order'] if result and result[0]['max_order'] is not None else 0
                sort_order = max_order + 1
                
                for account in accounts_to_import:
                    account_name = account.get('account_name', '').strip()
                    if not account_name:
                        skip_count += 1
                        continue
                    
                    if account_name in existing_names:
                        reply = QMessageBox.question(self, "账号已存在", 
                            f"账号 '{account_name}' 已存在，是否覆盖？\n"
                            "点击「是」覆盖现有账号，点击「否」跳过该账号。",
                            QMessageBox.Yes | QMessageBox.No)
                        
                        if reply == QMessageBox.Yes:
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
            
            self.load_accounts()
            
            self.show_status(f"✅ 导入完成：成功 {import_count} 个，跳过 {skip_count} 个", 5000)
            
        except json.JSONDecodeError:
            self.show_status("❌ 无效的JSON文件格式", 5000)
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入账号时发生错误：\n{str(e)}")

    def closeEvent(self, event):
        """关闭事件 - 只刷新主窗口显示，不改变当前账号"""
        from PySide6.QtWidgets import QApplication
        
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ExpressQueryProGUI':
                main_window = widget
                break
        
        if main_window and hasattr(main_window, 'api_account_manager'):
            # 只刷新显示，不重新加载账号（避免重置 current_account）
            main_window.update_api_account_display()
        
        event.accept()


class ApiAccountEditDialog(DialogWithStatusBar): 
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
        self.setMinimumSize(500, 450)
        
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
        
        # 添加状态栏
        self.setup_status_bar(layout)

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
            self.show_status("⚠️ 请输入账号名称", 3000)
            return
            
        if not customer:
            self.show_status("⚠️ 请输入Customer ID", 3000)
            return
            
        if not auth_key:
            self.show_status("⚠️ 请输入Auth Key", 3000)
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
            
        self.show_status("✅ 账号已保存", 2000)
        QTimer.singleShot(500, self.accept)  # 延迟关闭，让用户看到提示


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
        
        # 修改 express_summary 表，添加 dest_address 和 dest_site 字段
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
            dest_address TEXT,
            dest_site TEXT,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
        """
        db_manager.execute_update(express_summary_sql)
    
        # 尝试添加新字段（如果表已存在但缺少字段）
        try:
            db_manager.execute_update("ALTER TABLE express_summary ADD COLUMN dest_address TEXT")
        except:
            pass
        try:
            db_manager.execute_update("ALTER TABLE express_summary ADD COLUMN dest_site TEXT")
        except:
            pass
    
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
            arrival_time TEXT,
            delivery_days INTEGER,
            arrival_days INTEGER,
            route_key TEXT,
            delivery_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tracking_number, company_code)
        )
        """
        db_manager.execute_update(delivery_history_sql)
        
        # 尝试添加 delivery_history 表的新字段
        try:
            db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN arrival_time TEXT")
        except:
            pass
        try:
            db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN arrival_days INTEGER")
        except:
            pass
        try:
            db_manager.execute_update("ALTER TABLE delivery_history ADD COLUMN delivery_type TEXT")
        except:
            pass
        
        # 节点历史表
        node_transit_history_sql = """
        CREATE TABLE IF NOT EXISTS node_transit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_code TEXT NOT NULL,
            from_city TEXT,
            to_city TEXT,
            from_site TEXT,
            to_site TEXT,
            node_type TEXT,
            action_type TEXT,
            avg_hours REAL,
            sample_count INTEGER DEFAULT 1,
            min_hours REAL,
            max_hours REAL,
            route_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_code, from_city, to_city, from_site, to_site, node_type, action_type)
        )
        """
        db_manager.execute_update(node_transit_history_sql)
        
        try:
            db_manager.execute_update("ALTER TABLE node_transit_history ADD COLUMN from_site TEXT")
        except:
            pass
        try:
            db_manager.execute_update("ALTER TABLE node_transit_history ADD COLUMN to_site TEXT")
        except:
            pass
        
        # ========== 新增：收件地址管理表 ==========
        dest_address_sql = """
        CREATE TABLE IF NOT EXISTS dest_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,              -- 地址名称（如：家、公司）
            address TEXT NOT NULL,           -- 地址内容
            address_type TEXT DEFAULT 'custom', -- 类型：custom(自定义) 或 site(站点)
            is_default INTEGER DEFAULT 0,    -- 是否默认使用
            sort_order INTEGER DEFAULT 0,    -- 排序
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        db_manager.execute_update(dest_address_sql)
        
        # 尝试添加新字段（如果表已存在但缺少字段）
        try:
            db_manager.execute_update("ALTER TABLE dest_addresses ADD COLUMN address_type TEXT DEFAULT 'custom'")
        except:
            pass
        try:
            db_manager.execute_update("ALTER TABLE dest_addresses ADD COLUMN is_default INTEGER DEFAULT 0")
        except:
            pass
        try:
            db_manager.execute_update("ALTER TABLE dest_addresses ADD COLUMN sort_order INTEGER DEFAULT 0")
        except:
            pass
        
        # 创建索引
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_tracking_number ON express_query_history(tracking_number)",
            "CREATE INDEX IF NOT EXISTS idx_query_time ON express_query_history(query_time)",
            "CREATE INDEX IF NOT EXISTS idx_company_name ON express_query_history(company_name)",
            "CREATE INDEX IF NOT EXISTS idx_summary_tracking ON express_summary(tracking_number)",
            "CREATE INDEX IF NOT EXISTS idx_summary_category ON express_summary(status_category)",
            "CREATE INDEX IF NOT EXISTS idx_summary_update ON express_summary(last_update)",
            "CREATE INDEX IF NOT EXISTS idx_route_key ON delivery_history(route_key)",
            "CREATE INDEX IF NOT EXISTS idx_dh_company_code ON delivery_history(company_code)",
            "CREATE INDEX IF NOT EXISTS idx_node_route ON node_transit_history(route_key)",
            "CREATE INDEX IF NOT EXISTS idx_node_company ON node_transit_history(company_code)",
            "CREATE INDEX IF NOT EXISTS idx_node_from_site ON node_transit_history(from_site)",
            "CREATE INDEX IF NOT EXISTS idx_node_to_site ON node_transit_history(to_site)"
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
    """快递查询线程 - 支持多种API接口和验证码"""
    finished = Signal(dict)
    progress = Signal(int)
    need_verification = Signal(str, str, str)  # 新增信号：需要验证码 (单号, 公司名, 公司代码)
    
    def __init__(self, tracking_num: str, company_code: str, customer: str, key: str, 
                 endpoint: Dict = None, auto_detect: bool = True, verification_code: str = ""):
        super().__init__()
        self.tracking_num = tracking_num
        self.company_code = company_code
        self.customer = customer
        self.key = key
        self.endpoint = endpoint
        self.auto_detect = auto_detect
        self.verification_code = verification_code  # 新增：验证码/手机尾号
        
    def run(self):
        try:
            self.progress.emit(20)
            
            # 如果没有指定接口，使用默认的收费接口逻辑
            if self.endpoint is None:
                self._query_with_paid_api()
            else:
                # 根据接口类型选择查询方法
                if self.endpoint.get('endpoint_type') == 'paid':
                    self._query_with_paid_api()
                elif self.endpoint.get('endpoint_type') == 'free':
                    self._query_with_free_api()
                else:
                    self._query_with_custom_api()
                    
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})
    
    def _check_need_verification(self, result: dict, response_text: str = "") -> bool:
        """检查是否需要验证码"""
        # 检查返回结果中的错误信息
        message = result.get('message', '').lower()
        return_code = str(result.get('returnCode', ''))
        status = str(result.get('status', ''))
        
        # 需要验证码的特征
        verification_keywords = [
            '验证码', '手机尾号', '验证', '手机号', '收件人手机',
            '需要验证', '请输入', '校验', 'verification', 'captcha'
        ]
        
        # 检查错误信息
        for keyword in verification_keywords:
            if keyword in message:
                return True
        
        # 检查特定的返回码（快递100验证码相关）
        if return_code in ['501', '502', '503', '504']:
            return True
        
        # 检查中通快递的特殊情况
        if '中通' in str(result) or 'zhongtong' in str(result).lower():
            if '验证' in message or '参数异常' in message:
                return True
        
        return False
    
    def _query_with_paid_api(self):
        """使用收费API查询"""
        self.progress.emit(30)
        
        param = {
            'com': self.company_code,
            'num': self.tracking_num
        }
        
        if self.verification_code:
            param['phone'] = self.verification_code
        
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
        
        # 获取代理设置（如果需要）
        proxies = None
        if hasattr(self, 'parent_gui') and self.parent_gui:
            proxy_settings = getattr(self.parent_gui, 'proxy_settings', {})
            if proxy_settings.get('enabled', False) and proxy_settings.get('for_api', False):
                proxies = self.parent_gui.get_proxy_dict()
        
        try:
            response = requests.post(url, data=data, headers=headers, timeout=15, proxies=proxies)
            self.progress.emit(80)
            
            quota_info = self._extract_quota_info(response.headers)
            result = response.json()
            
            self.progress.emit(100)
            
            # 检查是否需要验证码
            if self._check_need_verification(result):
                # 如果没有提供验证码，发出需要验证码的信号
                if not self.verification_code:
                    company_name = self._get_company_name(self.company_code)
                    self.need_verification.emit(self.tracking_num, company_name, self.company_code)
                    self.finished.emit({
                        'success': False, 
                        'error': '需要输入收件人手机尾号验证',
                        'need_verification': True,
                        'tracking_num': self.tracking_num,
                        'company_code': self.company_code
                    })
                    return
                else:
                    # 验证码错误
                    self.finished.emit({
                        'success': False,
                        'error': '验证码错误，请重新输入正确的手机尾号',
                        'need_verification': True,
                        'verification_failed': True,
                        'tracking_num': self.tracking_num,
                        'company_code': self.company_code
                    })
                    return
            
            status = result.get('status', '')
            return_code = result.get('returnCode', '')
            message = result.get('message', '')
            
            if status == '200' or return_code == '200':
                self.finished.emit({
                    'success': True, 
                    'data': result,
                    'quota_info': quota_info
                })
            elif message in ['暂无物流信息', '单号不存在', '暂无轨迹'] or '暂无' in message or '无物流' in message:
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
                error_msg = message or '查询失败'
                self.finished.emit({
                    'success': False, 
                    'error': error_msg,
                    'quota_info': quota_info
                })
                
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})

    def _query_with_free_api(self):
        """使用免费API查询"""
        self.progress.emit(30)
        
        # 如果需要自动识别公司代码
        if self.auto_detect and not self.company_code:
            detected_com = self._auto_detect_company(self.tracking_num)
            if detected_com:
                self.company_code = detected_com
                self.progress.emit(45)
        
        # 免费API的URL
        url = 'https://www.kuaidi100.com/query'
        params = {
            'type': self.company_code,
            'postid': self.tracking_num,
            'temp': int(time.time() * 1000)
        }
        
        # 如果有验证码，添加手机尾号参数
        if self.verification_code:
            params['phone'] = self.verification_code
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.kuaidi100.com/',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        
        self.progress.emit(60)
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            self.progress.emit(80)
            
            if DEBUG_MODE:
                print(f"免费接口HTTP状态码: {response.status_code}")
                print(f"免费接口返回结果: {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                except:
                    # 可能返回的是HTML（验证码页面）
                    self.finished.emit({
                        'success': False,
                        'error': 'API返回格式错误，可能需要验证码',
                        'need_verification': True,
                        'tracking_num': self.tracking_num,
                        'company_code': self.company_code
                    })
                    return
                
                # 检查是否需要验证码
                if self._check_need_verification(result):
                    if not self.verification_code:
                        company_name = self._get_company_name(self.company_code)
                        self.need_verification.emit(self.tracking_num, company_name, self.company_code)
                        self.finished.emit({
                            'success': False,
                            'error': '需要输入收件人手机尾号验证',
                            'need_verification': True,
                            'tracking_num': self.tracking_num,
                            'company_code': self.company_code
                        })
                        return
                    else:
                        self.finished.emit({
                            'success': False,
                            'error': '验证码错误，请重新输入正确的手机尾号',
                            'need_verification': True,
                            'verification_failed': True,
                            'tracking_num': self.tracking_num,
                            'company_code': self.company_code
                        })
                        return
                
                status_code = result.get('status', '')  # 注意：这里获取的是API返回的status字段
                message = result.get('message', '')
                
                # ========== 修复点：正确判断成功状态 ==========
                # 快递100免费接口的 status 字段：
                # '200' - 查询成功
                # '0' 或 '201' - 单号不存在或暂无轨迹
                # '400' - 参数错误
                # 其他 - 各种错误
                
                if status_code == '200':
                    # 查询成功
                    converted_data = self._convert_free_api_result(result)
                    self.finished.emit({
                        'success': True,
                        'data': converted_data,
                        'quota_info': {'daily_limit': 0, 'remaining': 0, 'reset_time': '免费接口无限制'},
                        'is_free_api': True
                    })
                elif status_code in ['0', '201']:
                    # 单号可能存在但暂无轨迹
                    converted_data = self._convert_free_api_result(result)
                    self.finished.emit({
                        'success': True,
                        'data': converted_data,
                        'quota_info': {'daily_limit': 0, 'remaining': 0, 'reset_time': '免费接口无限制'},
                        'is_pending': True,
                        'is_free_api': True
                    })
                elif status_code == '400':
                    # 参数错误 - 可能是 company_code 为空或不正确
                    error_detail = result.get('message', '参数错误')
                    self.finished.emit({
                        'success': False,
                        'error': f'免费接口参数错误: {error_detail}。请确认已选择正确的快递公司。',
                        'is_free_api': True
                    })
                else:
                    # 其他错误
                    error_msg = message or f'查询失败(status={status_code})'
                    self.finished.emit({
                        'success': False,
                        'error': f'免费接口查询失败: {error_msg}',
                        'is_free_api': True
                    })
            else:
                self.finished.emit({
                    'success': False,
                    'error': f'免费接口请求失败: HTTP {response.status_code}',
                    'is_free_api': True
                })
                
        except requests.exceptions.Timeout:
            self.finished.emit({'success': False, 'error': '免费接口请求超时', 'is_free_api': True})
        except requests.exceptions.ConnectionError:
            self.finished.emit({'success': False, 'error': '免费接口网络连接失败', 'is_free_api': True})
        except Exception as e:
            self.finished.emit({'success': False, 'error': f'免费接口异常: {str(e)}', 'is_free_api': True})
    
    def _get_company_name(self, company_code: str) -> str:
        """根据公司代码获取公司名称"""
        company_map = {
            'shunfeng': '顺丰速运',
            'yuantong': '圆通速递',
            'zhongtong': '中通快递',
            'yunda': '韵达快递',
            'shentong': '申通快递',
            'jd': '京东物流',
            'ems': 'EMS',
            'jtexpress': '极兔速递',
            'huitongkuaidi': '百世快递',
            'youzhengguo': '中国邮政',
        }
        return company_map.get(company_code, company_code or '未知')
        
    def _query_with_custom_api(self):
        """使用自定义API查询（备用）"""
        # 简单的GET请求，用于自定义接口
        url = self.endpoint.get('url', '')
        if not url:
            self.finished.emit({'success': False, 'error': '未配置API地址'})
            return
        
        params = {
            'com': self.company_code,
            'num': self.tracking_num
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                result = response.json()
                # 尝试转换为标准格式
                converted_data = self._try_convert_custom_result(result)
                self.finished.emit({'success': True, 'data': converted_data})
            else:
                self.finished.emit({'success': False, 'error': f'请求失败: HTTP {response.status_code}'})
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})
    
    def _auto_detect_company(self, tracking_num: str) -> str:
        """自动识别快递公司"""
        try:
            # 使用快递100的自动识别接口
            detect_url = 'https://www.kuaidi100.com/autonumber/auto'
            params = {'num': tracking_num}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(detect_url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0:
                    return result[0].get('comCode', '')
        except:
            pass
        
        # 如果自动识别失败，使用本地规则
        company_map = {
            'SF': 'shunfeng',
            'YT': 'yuantong',
            'ZT': 'zhongtong',
            'YD': 'yunda',
            'ST': 'shentong',
            'JD': 'jd',
            'JT': 'jtexpress',
        }
        
        tracking_upper = tracking_num.upper()
        for prefix, code in company_map.items():
            if tracking_upper.startswith(prefix):
                return code
        
        return ''
    
    def _convert_free_api_result(self, free_result: dict) -> dict:
        """将免费接口返回结果转换为标准格式"""
        # 免费接口返回格式示例：
        # {
        #   "status": "200",
        #   "message": "ok",
        #   "data": [{"time": "...", "context": "..."}],
        #   "state": 3,
        #   "ischeck": "1"
        # }
        
        converted = {
            'nu': self.tracking_num,
            'com': self.company_code,
            'state': str(free_result.get('state', '0')),
            'data': free_result.get('data', []),
            'message': free_result.get('message', ''),
            'ischeck': free_result.get('ischeck', '0'),
            'updateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 确保 data 中的每条记录都有 time 和 context
        for track in converted['data']:
            if 'time' not in track:
                track['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'context' not in track:
                track['context'] = '物流信息更新中'
        
        return converted
    
    def _try_convert_custom_result(self, custom_result: dict) -> dict:
        """尝试将自定义接口结果转换为标准格式"""
        # 如果已经是标准格式，直接返回
        if 'nu' in custom_result and 'data' in custom_result:
            return custom_result
        
        # 尝试自动适配
        converted = {
            'nu': self.tracking_num,
            'com': self.company_code,
            'state': '0',
            'data': [],
            'message': ''
        }
        
        # 尝试从不同字段名获取
        if 'number' in custom_result:
            converted['nu'] = custom_result['number']
        if 'company' in custom_result:
            converted['com'] = custom_result['company']
        if 'status' in custom_result:
            converted['state'] = str(custom_result.get('status', '0'))
        if 'track' in custom_result:
            converted['data'] = custom_result['track']
        if 'info' in custom_result:
            converted['message'] = custom_result['info']
        
        return converted

    def _extract_quota_info(self, headers: Dict) -> Dict:
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
        # state = self.express_data.get('status', '')
        
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
        
        move_btn = QPushButton("移动")
        move_btn.setToolTip("移动到其他分类")
        move_btn.setFixedSize(50, 30)
        move_btn.clicked.connect(self.on_move_click)
        btn_layout.addWidget(move_btn)
        
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
        current_dest = self.express_data.get('dest_address', '')
        
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
        
        # ========== 设置最终收件地址 ==========
        dest_menu = menu.addMenu("📮 设置收件地址")
        
        set_dest_action = dest_menu.addAction("✏️ 自定义收件地址...")
        set_dest_action.triggered.connect(self.set_destination_address)
        
        # 从物流轨迹中智能选择
        if self.express_data.get('result_data'):
            auto_dest_menu = dest_menu.addMenu("📍 从轨迹中选择")
            try:
                full_data = json.loads(self.express_data['result_data'])
                track_list = full_data.get('data', [])
                
                sites = set()
                if self.parent_gui and self.parent_gui.node_analyzer:
                    nodes = self.parent_gui.node_analyzer.extract_nodes_from_track(track_list)
                    for node in nodes:
                        if node.get('site_name'):
                            sites.add(node['site_name'])
                        if node.get('city'):
                            sites.add(node['city'])
                
                # 添加最终签收站点（如果有）
                for track in track_list:
                    context = track.get('context', '')
                    if '签收' in context or '已收' in context:
                        site_match = re.search(r'【([^】]+)】', context)
                        if site_match:
                            sites.add(site_match.group(1))
                        break
                
                for site in sorted(sites)[:10]:
                    if site:
                        action = auto_dest_menu.addAction(site)
                        action.triggered.connect(lambda checked, s=site: self.set_destination_address_from_site(s))
            except:
                pass
        
        if current_dest:
            dest_menu.addSeparator()
            dest_menu.addAction(f"当前地址: {current_dest}").setEnabled(False)
            clear_dest_action = dest_menu.addAction("🗑️ 清除收件地址")
            clear_dest_action.triggered.connect(self.clear_destination_address)
        
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
        # 改为状态栏提示，不再弹窗
        if hasattr(self, 'parent_gui') and self.parent_gui:
            if item_name:
                self.parent_gui.status_bar.showMessage(f"✅ {item_name}已复制到剪贴板", 2000)
            else:
                self.parent_gui.status_bar.showMessage("✅ 已复制到剪贴板", 2000)

    def copy_full_info(self):
        """复制完整信息"""
        tracking_num = self.express_data.get('tracking_number', '')
        company_name = self.express_data.get('company_name', '')
        status = self.express_data.get('status', '')
        remark = self.express_data.get('remark', '')
        latest_track = self.express_data.get('latest_track', '')
        last_update = self.express_data.get('last_update', '')
        dest_address = self.express_data.get('dest_address', '')
        
        full_info = f"""快递单号: {tracking_num}
    快递公司: {company_name}
    当前状态: {status}
    收件地址: {dest_address if dest_address else '未设置'}
    备注: {remark if remark else '无'}
    最新物流: {latest_track if latest_track else '暂无'}
    最后更新: {last_update}"""
        
        clipboard = QApplication.clipboard()
        clipboard.setText(full_info)
        if hasattr(self, 'parent_gui') and self.parent_gui:
            self.parent_gui.status_bar.showMessage("✅ 完整快递信息已复制到剪贴板", 2000)

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
        if hasattr(self, 'parent_gui') and self.parent_gui:
            self.parent_gui.status_bar.showMessage(f"✅ 已添加备注: {text}", 2000)

    def search_online(self):
        """在网上搜索快递单号"""
        import webbrowser
        tracking_num = self.express_data.get('tracking_number', '')
        if tracking_num:
            # 使用快递100搜索
            url = f"https://www.kuaidi100.com/all/{tracking_num}.shtml"
            webbrowser.open(url)
    
    # ========== 收件地址相关方法 ==========
    def set_destination_address(self):
        """设置自定义收件地址"""
        from PySide6.QtWidgets import QInputDialog
        
        current = self.express_data.get('dest_address', '')
        address, ok = QInputDialog.getText(
            self, "设置收件地址",
            "请输入最终收件地址（城市名或具体站点）：",
            QLineEdit.Normal,
            current
        )
        
        if ok and address.strip():
            self.save_destination_address(address.strip())

    def set_destination_address_from_site(self, site: str):
        """从轨迹中选择收件地址"""
        self.save_destination_address(site)

    def clear_destination_address(self):
        """清除收件地址"""
        self.save_destination_address("")

    def save_destination_address(self, address: str):
        """保存收件地址到数据库"""
        if self.parent_gui and self.parent_gui.user_manager.current_user_db:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE express_summary SET dest_address = ?, last_update = ? WHERE id = ?"
            self.parent_gui.user_manager.current_user_db.execute_update(
                sql, (address, current_time, self.express_id)
            )
            self.express_data['dest_address'] = address
            self.update_display()
            
            if self.parent_gui:
                if address:
                    self.parent_gui.status_bar.showMessage(f"✅ 已设置收件地址: {address}", 3000)
                else:
                    self.parent_gui.status_bar.showMessage("✅ 已清除收件地址", 2000)

    def update_display(self):
        """更新显示"""
        status_text = self.express_data.get('status', '未知')
        tracking_num = self.express_data.get('tracking_number', '')
        company = self.express_data.get('company_name', '')
        last_update = self.express_data.get('last_update', '')
        created_at = self.express_data.get('created_at', '')
        dest_address = self.express_data.get('dest_address', '')
        
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
    
        # ========== 计算并显示预计送达时间 ==========
        estimated_delivery_display = ""
        if hasattr(self, 'parent_gui') and self.parent_gui:
            result_data = self.express_data.get('result_data', '')
            if result_data:
                try:
                    full_data = json.loads(result_data)
                    state = str(full_data.get('state', ''))
                    
                    if state != '3':  # 非签收状态才显示预估
                        target_dest = dest_address or self.express_data.get('dest_site', '')
                        

                        # 如果快递没有单独设置，尝试使用全局默认地址
                        if not target_dest and self.parent_gui and hasattr(self.parent_gui, 'dest_address_manager'):
                            global_default = self.parent_gui.dest_address_manager.get_default_address_text()
                            if global_default:
                                target_dest = global_default

                        if target_dest and self.parent_gui.node_analyzer:
                            estimate_info = self.parent_gui.node_analyzer.estimate_arrival_to_destination(
                                full_data, target_dest
                            )
                            if estimate_info:
                                hours = estimate_info.get('hours', 0)
                                if hours > 0:
                                    est_time = datetime.now() + timedelta(hours=hours)
                                    estimated_delivery_display = f" | 🎯 预计 {est_time.strftime('%m-%d %H:%M')} 送达"
                                    if estimate_info.get('confidence_level') == '低':
                                        estimated_delivery_display += " (低置信度)"
                                elif estimate_info.get('is_arrived'):
                                    estimated_delivery_display = " | ✅ 已到达目标地址"
                        else:
                            if self.parent_gui.delivery_estimator:
                                estimated_text = self.parent_gui.delivery_estimator.get_estimate_text(full_data)
                                if estimated_text and estimated_text != "暂无预估信息":
                                    import re
                                    match = re.search(r'预计(\d+月\d+日)送达', estimated_text)
                                    if match:
                                        estimated_delivery_display = f" | {match.group(0)}"
                                    elif '派件中' in estimated_text:
                                        estimated_delivery_display = " | 派件中"
                                    elif '已到达' in estimated_text:
                                        estimated_delivery_display = " | 待取件"
                except:
                    pass

        # 构建状态标签文本
        label_parts = [
            f"快递单号: {tracking_num}",
            company,
            status_text
        ]
        if dest_address:
            label_parts.append(f"📮 {dest_address[:20]}{'...' if len(dest_address) > 20 else ''}")
        label_parts.append(f"{created_display}{update_display}{estimated_delivery_display}")
        
        self.status_label.setText(" | ".join(label_parts))
        
        # 备注显示
        remark = self.express_data.get('remark', '')
        if remark:
            self.remark_btn.setText(f"备注: {remark}")
        else:
            self.remark_btn.setText("点击添加备注...")
        
        # 如果有设置的收件地址，在备注按钮上显示提示
        if dest_address:
            self.remark_btn.setToolTip(f"📮 收件地址: {dest_address}")
        else:
            self.remark_btn.setToolTip("")
        
        # 物流轨迹显示
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
                scaled_pixmap = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        from PySide6.QtWidgets import QInputDialog, QProgressDialog
        
        url, ok = QInputDialog.getText(
            self, "从URL下载", 
            "请输入图片URL地址：",
            QLineEdit.Normal,
            "https://"
        )
        
        if not ok or not url.strip():
            return
        
        progress_dialog = QProgressDialog("正在下载图片...", "取消", 0, 0, self)
        progress_dialog.setWindowTitle("下载中")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        class DownloadThread(QThread):
            finished = Signal(bool, str, str)
            
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
                try:
                    image_bytes = base64.b64decode(image_data)
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_bytes):
                        self.screenshot_changed.emit(self.express_id, image_data)
                        self.express_data['screenshot'] = image_data
                        self.update_display()
                        if hasattr(self, 'parent_gui') and self.parent_gui:
                            self.parent_gui.status_bar.showMessage("✅ 图片已成功下载并添加", 3000)
                    else:
                        if hasattr(self, 'parent_gui') and self.parent_gui:
                            self.parent_gui.status_bar.showMessage("❌ 下载的文件不是有效的图片格式", 3000)
                except Exception as e:
                    if hasattr(self, 'parent_gui') and self.parent_gui:
                        self.parent_gui.status_bar.showMessage(f"❌ 图片处理失败：{str(e)}", 3000)
            else:
                if hasattr(self, 'parent_gui') and self.parent_gui:
                    self.parent_gui.status_bar.showMessage(f"❌ 下载失败：{error_msg}", 3000)
        
        self.download_thread.finished.connect(on_download_finished)
        self.download_thread.start()
        
        if progress_dialog.wasCanceled():
            if self.download_thread.isRunning():
                self.download_thread.terminate()
                self.download_thread.wait()
    
    def rotate_screenshot(self, angle: int):
        """旋转截图"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("⚠️ 没有可旋转的截图", 2000)
            return
        
        try:
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            transform = QTransform().rotate(angle)
            rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
            
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            rotated_pixmap.save(buffer, "PNG")
            
            new_image_data = base64.b64encode(byte_array.data()).decode('utf-8')
            
            self.screenshot_changed.emit(self.express_id, new_image_data)
            self.express_data['screenshot'] = new_image_data
            self.update_display()
            
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage(f"✅ 图片已旋转 {angle}°", 2000)
            
        except Exception as e:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage(f"❌ 旋转图片失败：{str(e)}", 3000)
    
    def crop_screenshot(self):
        """裁剪截图"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("⚠️ 没有可裁剪的截图", 2000)
            return
        
        try:
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            dialog = CropImageDialog(pixmap, self)
            if dialog.exec() == QDialog.Accepted:
                cropped_pixmap = dialog.get_cropped_image()
                if cropped_pixmap:
                    byte_array = QByteArray()
                    buffer = QBuffer(byte_array)
                    buffer.open(QIODevice.WriteOnly)
                    cropped_pixmap.save(buffer, "PNG")
                    
                    new_image_data = base64.b64encode(byte_array.data()).decode('utf-8')
                    
                    self.screenshot_changed.emit(self.express_id, new_image_data)
                    self.express_data['screenshot'] = new_image_data
                    self.update_display()
                    
                    if hasattr(self, 'parent_gui') and self.parent_gui:
                        self.parent_gui.status_bar.showMessage("✅ 图片已裁剪", 2000)
                    
        except Exception as e:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage(f"❌ 裁剪图片失败：{str(e)}", 3000)
    
    def export_screenshot(self, include_info: bool = False):
        """导出截图"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            return
        
        tracking_num = self.express_data.get('tracking_number', 'unknown')
        
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
                info_pixmap = self.create_screenshot_with_info(pixmap)
                info_pixmap.save(file_path)
            else:
                pixmap.save(file_path)
            
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage(f"✅ 截图已保存到：{file_path}", 3000)
            
        except Exception as e:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage(f"❌ 保存截图失败：{str(e)}", 3000)
    
    def create_screenshot_with_info(self, original_pixmap: QPixmap) -> QPixmap:
        """创建带信息的截图"""
        tracking_num = self.express_data.get('tracking_number', '')
        company_name = self.express_data.get('company_name', '')
        status = self.express_data.get('status', '')
        remark = self.express_data.get('remark', '')
        last_update = self.express_data.get('last_update', '')
        dest_address = self.express_data.get('dest_address', '')
        
        # 计算新图片尺寸
        info_height = 140
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
        if dest_address:
            painter.drawText(10, y, f"收件地址: {dest_address}")
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
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("⚠️ 没有可复制的截图", 2000)
            return
        
        try:
            image_bytes = base64.b64decode(screenshot)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("✅ 截图已复制到剪贴板", 2000)
            
        except Exception as e:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage(f"❌ 复制截图失败：{str(e)}", 3000)
    
    def delete_screenshot(self):
        """删除截图"""
        # 删除操作需要确认，保留弹窗
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除此截图吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.screenshot_changed.emit(self.express_id, "")
            self.express_data['screenshot'] = ""
            self.update_display()
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("✅ 截图已删除", 2000)
    
    def show_screenshot_info(self):
        """显示截图信息"""
        screenshot = self.express_data.get('screenshot', '')
        if not screenshot:
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("ℹ️ 暂无截图", 2000)
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
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("⚠️ 剪贴板中没有图片！", 3000)
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
            if hasattr(self, 'parent_gui') and self.parent_gui:
                self.parent_gui.status_bar.showMessage("✅ 截图已从剪贴板添加", 3000)
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
        # 删除操作需要确认，保留弹窗
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除快递 {self.express_data.get('tracking_number', '')} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_requested.emit(self.express_id)


    def apply_search_highlight(self, is_match: bool):
        """应用搜索高亮样式"""
        if is_match:
            self.setStyleSheet(f"""
                ExpressItemWidget {{
                    background-color: {MacaronColors.YELLOW_CREAM.name()} !important;
                    border: 3px solid {MacaronColors.ORANGE_PEACH.name()} !important;
                    border-radius: 10px;
                    padding: 5px;
                }}
                ExpressItemWidget:hover {{
                    background-color: {MacaronColors.YELLOW_HONEY.name()} !important;
                    border-width: 3px !important;
                }}
            """)
        else:
            self.apply_item_style()

    def update_from_data(self, data: dict):
        """根据新的物流数据更新自身状态"""
        tracking_num = self.express_data.get('tracking_number', '')
        
        # 更新 result_data
        self.express_data['result_data'] = json.dumps(data, ensure_ascii=False)
        
        # 更新状态
        state = str(data.get('state', ''))
        state_text = self.parent_gui.get_state_text(state) if self.parent_gui else ''
        
        track_list = data.get('data', [])
        latest_track = ''
        latest_context = ''
        if track_list:
            latest = track_list[0]
            latest_track = f"[{latest.get('time', '')}] {latest.get('context', '')}"
            latest_context = latest.get('context', '')
        
        category = self.parent_gui.get_state_category(state, latest_context) if self.parent_gui else 'other'
        
        # 更新 express_data
        self.express_data['status'] = state_text
        self.express_data['status_category'] = category
        self.express_data['latest_track'] = latest_track
        self.express_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新显示
        self.update_display()
        self.apply_item_style()
        
        # 如果分类变了，需要移动到对应的分类
        return category

    def on_move_click(self):
        """点击移动按钮 - 弹出分类选择菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(MacaronStyle.get_main_style())
        
        current_category = self.express_data.get('status_category', 'other')
        
        # 所有可用的分类
        categories = [
            ('signed', '✅ 已签收'),
            ('arrived', '📍 已到驿站'),
            ('delivering', '🚚 派件中'),
            ('transit', '✈️ 在途中'),
            ('picked', '📮 已揽收'),
            ('pending', '⏳ 待揽件'),
            ('problem', '⚠️ 疑难件'),
            ('returned', '↩️ 退件'),
            ('customs', '🛃 清关中'),
            ('other', '📦 其他')
        ]
        
        for key, name in categories:
            action = menu.addAction(name)
            if key == current_category:
                action.setEnabled(False)
                action.setText(f"{name} (当前)")
            else:
                action.triggered.connect(lambda checked, k=key: self.move_to_category(k))
        
        # 在按钮下方显示菜单
        move_btn = self.sender()
        if move_btn:
            menu.exec(move_btn.mapToGlobal(move_btn.rect().bottomLeft()))
        else:
            menu.exec(QCursor.pos())
    
    def move_to_category(self, target_category: str):
        """移动到指定分类"""
        if self.parent_gui:
            tracking_num = self.express_data.get('tracking_number', '')
            old_category = self.express_data.get('status_category', 'other')
            
            # 更新数据库
            if self.parent_gui.user_manager.current_user_db:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = """
                UPDATE express_summary 
                SET status_category = ?, last_update = ? 
                WHERE id = ? AND is_deleted = 0
                """
                self.parent_gui.user_manager.current_user_db.execute_update(
                    sql, (target_category, current_time, self.express_id)
                )
            
            # 更新本地数据
            self.express_data['status_category'] = target_category
            self.express_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 从旧分类移除
            if old_category in self.parent_gui.category_widgets:
                self.parent_gui.category_widgets[old_category].remove_express_item(self)
            
            # 添加到新分类
            # 需要重新创建 widget 或者直接移动
            # 这里采用从数据库重新加载该条记录的方式
            if self.parent_gui.user_manager.current_user_db:
                sql_new = "SELECT * FROM express_summary WHERE id = ? AND is_deleted = 0"
                new_record = self.parent_gui.user_manager.current_user_db.execute_query(sql_new, (self.express_id,))
                if new_record:
                    self.parent_gui.add_express_to_category(new_record[0])
            
            # 更新分类计数
            for w in self.parent_gui.category_widgets.values():
                w.update_count()
            
            self.parent_gui.status_bar.showMessage(
                f"✅ {tracking_num} 已移动到新分类", 3000
            )



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
    
    # 城市坐标缓存（静态坐标库）- 完整版
    CITY_COORDINATES = {
        # 直辖市
        '北京': (39.9042, 116.4074), '北京市': (39.9042, 116.4074),
        '上海': (31.2304, 121.4737), '上海市': (31.2304, 121.4737),
        '天津': (39.0842, 117.2009), '天津市': (39.0842, 117.2009),
        '重庆': (29.5630, 106.5516), '重庆市': (29.5630, 106.5516),
        
        # 广东省
        '广州': (23.1291, 113.2644), '广州市': (23.1291, 113.2644),
        '深圳': (22.5431, 114.0579), '深圳市': (22.5431, 114.0579),
        '珠海': (22.2707, 113.5767), '珠海市': (22.2707, 113.5767),
        '佛山': (23.0215, 113.1214), '佛山市': (23.0215, 113.1214),
        '东莞': (23.0207, 113.7518), '东莞市': (23.0207, 113.7518),
        '惠州': (23.1118, 114.4158), '惠州市': (23.1118, 114.4158),
        '中山': (22.5159, 113.3926), '中山市': (22.5159, 113.3926),
        '江门': (22.5787, 113.0819), '江门市': (22.5787, 113.0819),
        '湛江': (21.2707, 110.3594), '湛江市': (21.2707, 110.3594),
        '茂名': (21.6630, 110.9252), '茂名市': (21.6630, 110.9252),
        '肇庆': (23.0473, 112.4650), '肇庆市': (23.0473, 112.4650),
        '汕头': (23.3535, 116.6820), '汕头市': (23.3535, 116.6820),
        '潮州': (23.6567, 116.6226), '潮州市': (23.6567, 116.6226),
        '揭阳': (23.5497, 116.3727), '揭阳市': (23.5497, 116.3727),
        '汕尾': (22.7857, 115.3754), '汕尾市': (22.7857, 115.3754),
        '梅州': (24.2886, 116.1225), '梅州市': (24.2886, 116.1225),
        '河源': (23.7437, 114.7004), '河源市': (23.7437, 114.7004),
        '清远': (23.6820, 113.0560), '清远市': (23.6820, 113.0560),
        '韶关': (24.8104, 113.5976), '韶关市': (24.8104, 113.5976),
        '阳江': (21.8582, 111.9826), '阳江市': (21.8582, 111.9826),
        '云浮': (22.9152, 112.0445), '云浮市': (22.9152, 112.0445),
        
        # 江苏省
        '南京': (32.0603, 118.7969), '南京市': (32.0603, 118.7969),
        '苏州': (31.2990, 120.5853), '苏州市': (31.2990, 120.5853),
        '无锡': (31.4912, 120.3119), '无锡市': (31.4912, 120.3119),
        '常州': (31.8101, 119.9736), '常州市': (31.8101, 119.9736),
        '南通': (31.9796, 120.8937), '南通市': (31.9796, 120.8937),
        '扬州': (32.3936, 119.4129), '扬州市': (32.3936, 119.4129),
        '镇江': (32.1896, 119.4250), '镇江市': (32.1896, 119.4250),
        '徐州': (34.2048, 117.2848), '徐州市': (34.2048, 117.2848),
        '盐城': (33.3495, 120.1616), '盐城市': (33.3495, 120.1616),
        '淮安': (33.6101, 119.0153), '淮安市': (33.6101, 119.0153),
        '连云港': (34.5967, 119.2216), '连云港市': (34.5967, 119.2216),
        '泰州': (32.4555, 119.9255), '泰州市': (32.4555, 119.9255),
        '宿迁': (33.9619, 118.2755), '宿迁市': (33.9619, 118.2755),
        '昆山': (31.3846, 120.9817), '昆山市': (31.3846, 120.9817),
        '江阴': (31.9211, 120.2849), '江阴市': (31.9211, 120.2849),
        '宜兴': (31.3406, 119.8233), '宜兴市': (31.3406, 119.8233),
        '常熟': (31.6538, 120.7525), '常熟市': (31.6538, 120.7525),
        '张家港': (31.8754, 120.5556), '张家港市': (31.8754, 120.5556),
        '太仓': (31.4590, 121.1300), '太仓市': (31.4590, 121.1300),
        
        # 浙江省
        '杭州': (30.2741, 120.1551), '杭州市': (30.2741, 120.1551),
        '宁波': (29.8683, 121.5440), '宁波市': (29.8683, 121.5440),
        '温州': (27.9943, 120.6994), '温州市': (27.9943, 120.6994),
        '绍兴': (30.0303, 120.5802), '绍兴市': (30.0303, 120.5802),
        '嘉兴': (30.7460, 120.7555), '嘉兴市': (30.7460, 120.7555),
        '金华': (29.0781, 119.6474), '金华市': (29.0781, 119.6474),
        '台州': (28.6561, 121.4206), '台州市': (28.6561, 121.4206),
        '湖州': (30.8930, 120.0868), '湖州市': (30.8930, 120.0868),
        '衢州': (28.9359, 118.8595), '衢州市': (28.9359, 118.8595),
        '丽水': (28.4672, 119.9229), '丽水市': (28.4672, 119.9229),
        '舟山': (29.9853, 122.2078), '舟山市': (29.9853, 122.2078),
        '义乌': (29.3057, 120.0751), '义乌市': (29.3057, 120.0751),
        '慈溪': (30.1697, 121.2665), '慈溪市': (30.1697, 121.2665),
        '余姚': (30.0372, 121.1546), '余姚市': (30.0372, 121.1546),
        
        # 福建省
        '福州': (26.0745, 119.2965), '福州市': (26.0745, 119.2965),
        '厦门': (24.4798, 118.0894), '厦门市': (24.4798, 118.0894),
        '泉州': (24.8741, 118.6759), '泉州市': (24.8741, 118.6759),
        '漳州': (24.5130, 117.6475), '漳州市': (24.5130, 117.6475),
        '莆田': (25.4540, 119.0077), '莆田市': (25.4540, 119.0077),
        '龙岩': (25.0751, 117.0172), '龙岩市': (25.0751, 117.0172),
        '三明': (26.2638, 117.6392), '三明市': (26.2638, 117.6392),
        '南平': (26.6417, 118.1785), '南平市': (26.6417, 118.1785),
        '宁德': (26.6657, 119.5482), '宁德市': (26.6657, 119.5482),
        '晋江': (24.7817, 118.5524), '晋江市': (24.7817, 118.5524),
        '福清': (25.7202, 119.3842), '福清市': (25.7202, 119.3842),
        
        # 山东省
        '济南': (36.6512, 117.1201), '济南市': (36.6512, 117.1201),
        '青岛': (36.0671, 120.3826), '青岛市': (36.0671, 120.3826),
        '烟台': (37.4635, 121.4479), '烟台市': (37.4635, 121.4479),
        '威海': (37.5131, 122.1204), '威海市': (37.5131, 122.1204),
        '潍坊': (36.7068, 119.1618), '潍坊市': (36.7068, 119.1618),
        '淄博': (36.8131, 118.0548), '淄博市': (36.8131, 118.0548),
        '临沂': (35.1047, 118.3565), '临沂市': (35.1047, 118.3565),
        '济宁': (35.4146, 116.5872), '济宁市': (35.4146, 116.5872),
        '泰安': (36.2000, 117.0876), '泰安市': (36.2000, 117.0876),
        '聊城': (36.4570, 115.9854), '聊城市': (36.4570, 115.9854),
        '德州': (37.4355, 116.3593), '德州市': (37.4355, 116.3593),
        '滨州': (37.3821, 117.9728), '滨州市': (37.3821, 117.9728),
        '东营': (37.4337, 118.6747), '东营市': (37.4337, 118.6747),
        '菏泽': (35.2336, 115.4807), '菏泽市': (35.2336, 115.4807),
        '日照': (35.4164, 119.5271), '日照市': (35.4164, 119.5271),
        '枣庄': (34.8105, 117.3237), '枣庄市': (34.8105, 117.3237),
        
        # 河南省
        '郑州': (34.7472, 113.6253), '郑州市': (34.7472, 113.6253),
        '洛阳': (34.6197, 112.4539), '洛阳市': (34.6197, 112.4539),
        '南阳': (32.9908, 112.5283), '南阳市': (32.9908, 112.5283),
        '许昌': (34.0357, 113.8523), '许昌市': (34.0357, 113.8523),
        '周口': (33.6258, 114.6970), '周口市': (33.6258, 114.6970),
        '新乡': (35.3030, 113.9268), '新乡市': (35.3030, 113.9268),
        '商丘': (34.4143, 115.6564), '商丘市': (34.4143, 115.6564),
        '驻马店': (33.0114, 114.0223), '驻马店市': (33.0114, 114.0223),
        '信阳': (32.1473, 114.0910), '信阳市': (32.1473, 114.0910),
        '开封': (34.7975, 114.3076), '开封市': (34.7975, 114.3076),
        '平顶山': (33.7662, 113.1924), '平顶山市': (33.7662, 113.1924),
        '安阳': (36.0977, 114.3924), '安阳市': (36.0977, 114.3924),
        '焦作': (35.2159, 113.2420), '焦作市': (35.2159, 113.2420),
        '濮阳': (35.7618, 115.0292), '濮阳市': (35.7618, 115.0292),
        '漯河': (33.5815, 114.0165), '漯河市': (33.5815, 114.0165),
        '三门峡': (34.7726, 111.2003), '三门峡市': (34.7726, 111.2003),
        '鹤壁': (35.7472, 114.2973), '鹤壁市': (35.7472, 114.2973),
        
        # 河北省
        '石家庄': (38.0428, 114.5149), '石家庄市': (38.0428, 114.5149),
        '唐山': (39.6305, 118.1802), '唐山市': (39.6305, 118.1802),
        '邯郸': (36.6256, 114.5390), '邯郸市': (36.6256, 114.5390),
        '保定': (38.8739, 115.4648), '保定市': (38.8739, 115.4648),
        '沧州': (38.3045, 116.8387), '沧州市': (38.3045, 116.8387),
        '邢台': (37.0706, 114.5048), '邢台市': (37.0706, 114.5048),
        '廊坊': (39.5378, 116.6838), '廊坊市': (39.5378, 116.6838),
        '张家口': (40.7675, 114.8863), '张家口市': (40.7675, 114.8863),
        '承德': (40.9515, 117.9624), '承德市': (40.9515, 117.9624),
        '秦皇岛': (39.9355, 119.6005), '秦皇岛市': (39.9355, 119.6005),
        '衡水': (37.7389, 115.6702), '衡水市': (37.7389, 115.6702),
        
        # 湖北省
        '武汉': (30.5928, 114.3055), '武汉市': (30.5928, 114.3055),
        '襄阳': (32.0090, 112.1224), '襄阳市': (32.0090, 112.1224),
        '宜昌': (30.6908, 111.2865), '宜昌市': (30.6908, 111.2865),
        '荆州': (30.3348, 112.2397), '荆州市': (30.3348, 112.2397),
        '黄冈': (30.4537, 114.8724), '黄冈市': (30.4537, 114.8724),
        '孝感': (30.9248, 113.9169), '孝感市': (30.9248, 113.9169),
        '十堰': (32.6292, 110.7980), '十堰市': (32.6292, 110.7980),
        '荆门': (31.0355, 112.1994), '荆门市': (31.0355, 112.1994),
        '黄石': (30.1995, 115.0388), '黄石市': (30.1995, 115.0388),
        '咸宁': (29.8414, 114.3225), '咸宁市': (29.8414, 114.3225),
        '随州': (31.6901, 113.3826), '随州市': (31.6901, 113.3826),
        '鄂州': (30.3909, 114.8949), '鄂州市': (30.3909, 114.8949),
        '恩施': (30.2831, 109.4882), '恩施市': (30.2831, 109.4882),
        
        # 湖南省
        '长沙': (28.2282, 112.9388), '长沙市': (28.2282, 112.9388),
        '株洲': (27.8277, 113.1339), '株洲市': (27.8277, 113.1339),
        '湘潭': (27.8297, 112.9441), '湘潭市': (27.8297, 112.9441),
        '衡阳': (26.8932, 112.5720), '衡阳市': (26.8932, 112.5720),
        '邵阳': (27.2389, 111.4677), '邵阳市': (27.2389, 111.4677),
        '岳阳': (29.3573, 113.1290), '岳阳市': (29.3573, 113.1290),
        '常德': (29.0316, 111.6985), '常德市': (29.0316, 111.6985),
        '张家界': (29.1167, 110.4783), '张家界市': (29.1167, 110.4783),
        '益阳': (28.5539, 112.3550), '益阳市': (28.5539, 112.3550),
        '郴州': (25.7706, 113.0148), '郴州市': (25.7706, 113.0148),
        '永州': (26.4203, 111.6134), '永州市': (26.4203, 111.6134),
        '怀化': (27.5695, 110.0016), '怀化市': (27.5695, 110.0016),
        '娄底': (27.6973, 111.9945), '娄底市': (27.6973, 111.9945),
        
        # 四川省
        '成都': (30.5728, 104.0668), '成都市': (30.5728, 104.0668),
        '绵阳': (31.4675, 104.6791), '绵阳市': (31.4675, 104.6791),
        '德阳': (31.1269, 104.3979), '德阳市': (31.1269, 104.3979),
        '宜宾': (28.7513, 104.6433), '宜宾市': (28.7513, 104.6433),
        '南充': (30.8378, 106.1107), '南充市': (30.8378, 106.1107),
        '泸州': (28.8718, 105.4423), '泸州市': (28.8718, 105.4423),
        '达州': (31.2086, 107.4679), '达州市': (31.2086, 107.4679),
        '乐山': (29.5521, 103.7656), '乐山市': (29.5521, 103.7656),
        '内江': (29.5802, 105.0584), '内江市': (29.5802, 105.0584),
        '自贡': (29.3392, 104.7784), '自贡市': (29.3392, 104.7784),
        '攀枝花': (26.5823, 101.7186), '攀枝花市': (26.5823, 101.7186),
        '眉山': (30.0756, 103.8485), '眉山市': (30.0756, 103.8485),
        '遂宁': (30.5328, 105.5927), '遂宁市': (30.5328, 105.5927),
        '广安': (30.4559, 106.6332), '广安市': (30.4559, 106.6332),
        '巴中': (31.8672, 106.7475), '巴中市': (31.8672, 106.7475),
        '资阳': (30.1289, 104.6276), '资阳市': (30.1289, 104.6276),
        '雅安': (29.9805, 103.0133), '雅安市': (29.9805, 103.0133),
        '广元': (32.4355, 105.8436), '广元市': (32.4355, 105.8436),
        
        # 陕西省
        '西安': (34.3416, 108.9398), '西安市': (34.3416, 108.9398),
        '宝鸡': (34.3619, 107.2377), '宝鸡市': (34.3619, 107.2377),
        '咸阳': (34.3293, 108.7093), '咸阳市': (34.3293, 108.7093),
        '渭南': (34.4996, 109.5098), '渭南市': (34.4996, 109.5098),
        '汉中': (33.0676, 107.0238), '汉中市': (33.0676, 107.0238),
        '榆林': (38.2852, 109.7346), '榆林市': (38.2852, 109.7346),
        '安康': (32.6847, 109.0290), '安康市': (32.6847, 109.0290),
        '商洛': (33.8727, 109.9184), '商洛市': (33.8727, 109.9184),
        '延安': (36.5855, 109.4898), '延安市': (36.5855, 109.4898),
        '铜川': (34.8967, 108.9451), '铜川市': (34.8967, 108.9451),
        
        # 辽宁省
        '沈阳': (41.8057, 123.4315), '沈阳市': (41.8057, 123.4315),
        '大连': (38.9140, 121.6147), '大连市': (38.9140, 121.6147),
        '鞍山': (41.1078, 122.9946), '鞍山市': (41.1078, 122.9946),
        '抚顺': (41.8809, 123.9572), '抚顺市': (41.8809, 123.9572),
        '本溪': (41.2941, 123.7665), '本溪市': (41.2941, 123.7665),
        '丹东': (40.0008, 124.3547), '丹东市': (40.0008, 124.3547),
        '锦州': (41.0951, 121.1270), '锦州市': (41.0951, 121.1270),
        '营口': (40.6668, 122.2352), '营口市': (40.6668, 122.2352),
        '阜新': (42.0216, 121.6701), '阜新市': (42.0216, 121.6701),
        '辽阳': (41.2681, 123.2374), '辽阳市': (41.2681, 123.2374),
        '盘锦': (41.1199, 122.0708), '盘锦市': (41.1199, 122.0708),
        '铁岭': (42.2862, 123.8425), '铁岭市': (42.2862, 123.8425),
        '朝阳': (41.5734, 120.4508), '朝阳市': (41.5734, 120.4508),
        '葫芦岛': (40.7110, 120.8370), '葫芦岛市': (40.7110, 120.8370),
        
        # 吉林省
        '长春': (43.8171, 125.3235), '长春市': (43.8171, 125.3235),
        '吉林': (43.8378, 126.5495), '吉林市': (43.8378, 126.5495),
        '四平': (43.1665, 124.3504), '四平市': (43.1665, 124.3504),
        '辽源': (42.8880, 125.1436), '辽源市': (42.8880, 125.1436),
        '通化': (41.7283, 125.9399), '通化市': (41.7283, 125.9399),
        '白山': (41.9408, 126.4147), '白山市': (41.9408, 126.4147),
        '松原': (45.1411, 124.8251), '松原市': (45.1411, 124.8251),
        '白城': (45.6196, 122.8390), '白城市': (45.6196, 122.8390),
        '延吉': (42.8911, 129.5090), '延吉市': (42.8911, 129.5090),
        
        # 黑龙江省
        '哈尔滨': (45.8038, 126.5350), '哈尔滨市': (45.8038, 126.5350),
        '齐齐哈尔': (47.3543, 123.9182), '齐齐哈尔市': (47.3543, 123.9182),
        '鸡西': (45.2951, 130.9693), '鸡西市': (45.2951, 130.9693),
        '鹤岗': (47.3499, 130.2980), '鹤岗市': (47.3499, 130.2980),
        '双鸭山': (46.6466, 131.1591), '双鸭山市': (46.6466, 131.1591),
        '大庆': (46.5876, 125.1031), '大庆市': (46.5876, 125.1031),
        '伊春': (47.7275, 128.8412), '伊春市': (47.7275, 128.8412),
        '佳木斯': (46.7998, 130.3189), '佳木斯市': (46.7998, 130.3189),
        '七台河': (45.7713, 131.0031), '七台河市': (45.7713, 131.0031),
        '牡丹江': (44.5527, 129.6324), '牡丹江市': (44.5527, 129.6324),
        '黑河': (50.2452, 127.5285), '黑河市': (50.2452, 127.5285),
        '绥化': (46.6538, 126.9693), '绥化市': (46.6538, 126.9693),
        
        # 安徽省
        '合肥': (31.8206, 117.2272), '合肥市': (31.8206, 117.2272),
        '芜湖': (31.3526, 118.4329), '芜湖市': (31.3526, 118.4329),
        '蚌埠': (32.9155, 117.3893), '蚌埠市': (32.9155, 117.3893),
        '淮南': (32.6255, 116.9998), '淮南市': (32.6255, 116.9998),
        '马鞍山': (31.6707, 118.5061), '马鞍山市': (31.6707, 118.5061),
        '淮北': (33.9548, 116.7983), '淮北市': (33.9548, 116.7983),
        '铜陵': (30.9446, 117.8115), '铜陵市': (30.9446, 117.8115),
        '安庆': (30.5429, 117.0636), '安庆市': (30.5429, 117.0636),
        '黄山': (29.7152, 118.3375), '黄山市': (29.7152, 118.3375),
        '滁州': (32.3018, 118.3168), '滁州市': (32.3018, 118.3168),
        '阜阳': (32.8896, 115.8149), '阜阳市': (32.8896, 115.8149),
        '宿州': (33.6476, 116.9642), '宿州市': (33.6476, 116.9642),
        '六安': (31.7349, 116.5219), '六安市': (31.7349, 116.5219),
        '亳州': (33.8446, 115.7793), '亳州市': (33.8446, 115.7793),
        '池州': (30.6647, 117.4914), '池州市': (30.6647, 117.4914),
        '宣城': (30.9407, 118.7588), '宣城市': (30.9407, 118.7588),
        
        # 江西省
        '南昌': (28.6820, 115.8579), '南昌市': (28.6820, 115.8579),
        '景德镇': (29.2687, 117.1784), '景德镇市': (29.2687, 117.1784),
        '萍乡': (27.6228, 113.8546), '萍乡市': (27.6228, 113.8546),
        '九江': (29.7051, 116.0019), '九江市': (29.7051, 116.0019),
        '新余': (27.8178, 114.9173), '新余市': (27.8178, 114.9173),
        '鹰潭': (28.2602, 117.0692), '鹰潭市': (28.2602, 117.0692),
        '赣州': (25.8310, 114.9348), '赣州市': (25.8310, 114.9348),
        '吉安': (27.1138, 114.9929), '吉安市': (27.1138, 114.9929),
        '宜春': (27.8144, 114.4168), '宜春市': (27.8144, 114.4168),
        '抚州': (27.9492, 116.3581), '抚州市': (27.9492, 116.3581),
        '上饶': (28.4549, 117.9436), '上饶市': (28.4549, 117.9436),
        
        # 贵州省
        '贵阳': (26.6477, 106.6302), '贵阳市': (26.6477, 106.6302),
        '遵义': (27.7257, 106.9272), '遵义市': (27.7257, 106.9272),
        '六盘水': (26.5925, 104.8303), '六盘水市': (26.5925, 104.8303),
        '安顺': (26.2531, 105.9462), '安顺市': (26.2531, 105.9462),
        '毕节': (27.2985, 105.3050), '毕节市': (27.2985, 105.3050),
        '铜仁': (27.7315, 109.1896), '铜仁市': (27.7315, 109.1896),
        
        # 云南省
        '昆明': (24.8801, 102.8329), '昆明市': (24.8801, 102.8329),
        '曲靖': (25.4900, 103.7962), '曲靖市': (25.4900, 103.7962),
        '玉溪': (24.3518, 102.5466), '玉溪市': (24.3518, 102.5466),
        '保山': (25.1120, 99.1618), '保山市': (25.1120, 99.1618),
        '昭通': (27.3382, 103.7168), '昭通市': (27.3382, 103.7168),
        '丽江': (26.8567, 100.2271), '丽江市': (26.8567, 100.2271),
        '普洱': (22.8252, 100.9665), '普洱市': (22.8252, 100.9665),
        '临沧': (23.8842, 100.0888), '临沧市': (23.8842, 100.0888),
        '大理': (25.6065, 100.2676), '大理市': (25.6065, 100.2676),
        
        # 甘肃省
        '兰州': (36.0611, 103.8343), '兰州市': (36.0611, 103.8343),
        '嘉峪关': (39.7720, 98.2892), '嘉峪关市': (39.7720, 98.2892),
        '金昌': (38.5201, 102.1880), '金昌市': (38.5201, 102.1880),
        '白银': (36.5447, 104.1386), '白银市': (36.5447, 104.1386),
        '天水': (34.5809, 105.7249), '天水市': (34.5809, 105.7249),
        '武威': (37.9282, 102.6380), '武威市': (37.9282, 102.6380),
        '张掖': (38.9259, 100.4498), '张掖市': (38.9259, 100.4498),
        '平凉': (35.5430, 106.6653), '平凉市': (35.5430, 106.6653),
        '酒泉': (39.7329, 98.4940), '酒泉市': (39.7329, 98.4940),
        '庆阳': (35.7098, 107.6436), '庆阳市': (35.7098, 107.6436),
        '定西': (35.5806, 104.6250), '定西市': (35.5806, 104.6250),
        '陇南': (33.4010, 104.9218), '陇南市': (33.4010, 104.9218),
        
        # 内蒙古自治区
        '呼和浩特': (40.8426, 111.7490), '呼和浩特市': (40.8426, 111.7490),
        '包头': (40.6582, 109.8404), '包头市': (40.6582, 109.8404),
        '乌海': (39.6538, 106.7955), '乌海市': (39.6538, 106.7955),
        '赤峰': (42.2586, 118.8889), '赤峰市': (42.2586, 118.8889),
        '通辽': (43.6529, 122.2437), '通辽市': (43.6529, 122.2437),
        '鄂尔多斯': (39.6085, 109.7813), '鄂尔多斯市': (39.6085, 109.7813),
        '呼伦贝尔': (49.2116, 119.7658), '呼伦贝尔市': (49.2116, 119.7658),
        '巴彦淖尔': (40.7432, 107.3877), '巴彦淖尔市': (40.7432, 107.3877),
        '乌兰察布': (40.9948, 113.1338), '乌兰察布市': (40.9948, 113.1338),
        
        # 广西壮族自治区
        '南宁': (22.8170, 108.3665), '南宁市': (22.8170, 108.3665),
        '柳州': (24.3264, 109.4286), '柳州市': (24.3264, 109.4286),
        '桂林': (25.2736, 110.2900), '桂林市': (25.2736, 110.2900),
        '梧州': (23.4769, 111.2792), '梧州市': (23.4769, 111.2792),
        '北海': (21.4733, 109.1202), '北海市': (21.4733, 109.1202),
        '防城港': (21.6869, 108.3547), '防城港市': (21.6869, 108.3547),
        '钦州': (21.9809, 108.6543), '钦州市': (21.9809, 108.6543),
        '贵港': (23.1115, 109.5989), '贵港市': (23.1115, 109.5989),
        '玉林': (22.6545, 110.1810), '玉林市': (22.6545, 110.1810),
        '百色': (23.9022, 106.6184), '百色市': (23.9022, 106.6184),
        '贺州': (24.4035, 111.5667), '贺州市': (24.4035, 111.5667),
        '河池': (24.6929, 108.0854), '河池市': (24.6929, 108.0854),
        '来宾': (23.7502, 109.2215), '来宾市': (23.7502, 109.2215),
        '崇左': (22.3789, 107.3650), '崇左市': (22.3789, 107.3650),
        
        # 西藏自治区
        '拉萨': (29.6469, 91.1172), '拉萨市': (29.6469, 91.1172),
        '日喀则': (29.2670, 88.8812), '日喀则市': (29.2670, 88.8812),
        '昌都': (31.1409, 97.1720), '昌都市': (31.1409, 97.1720),
        '林芝': (29.6489, 94.3615), '林芝市': (29.6489, 94.3615),
        '山南': (29.2371, 91.7731), '山南市': (29.2371, 91.7731),
        '那曲': (31.4762, 92.0514), '那曲市': (31.4762, 92.0514),
        
        # 宁夏回族自治区
        '银川': (38.4872, 106.2309), '银川市': (38.4872, 106.2309),
        '石嘴山': (38.9841, 106.3842), '石嘴山市': (38.9841, 106.3842),
        '吴忠': (37.9975, 106.1984), '吴忠市': (37.9975, 106.1984),
        '固原': (36.0158, 106.2426), '固原市': (36.0158, 106.2426),
        '中卫': (37.5003, 105.1968), '中卫市': (37.5003, 105.1968),
        
        # 新疆维吾尔自治区
        '乌鲁木齐': (43.8256, 87.6168), '乌鲁木齐市': (43.8256, 87.6168),
        '克拉玛依': (45.5799, 84.8892), '克拉玛依市': (45.5799, 84.8892),
        '吐鲁番': (42.9513, 89.1895), '吐鲁番市': (42.9513, 89.1895),
        '哈密': (42.8185, 93.5149), '哈密市': (42.8185, 93.5149),
        '昌吉': (44.0112, 87.2675), '昌吉市': (44.0112, 87.2675),
        '伊宁': (43.9168, 81.3241), '伊宁市': (43.9168, 81.3241),
        '喀什': (39.4677, 75.9897), '喀什市': (39.4677, 75.9897),
        '和田': (37.1140, 79.9225), '和田市': (37.1140, 79.9225),
        
        # 海南省
        '海口': (20.0174, 110.3492), '海口市': (20.0174, 110.3492),
        '三亚': (18.2528, 109.5119), '三亚市': (18.2528, 109.5119),
        '三沙': (16.8310, 112.3333), '三沙市': (16.8310, 112.3333),
        '儋州': (19.5209, 109.5807), '儋州市': (19.5209, 109.5807),
        '琼海': (19.2591, 110.4746), '琼海市': (19.2591, 110.4746),
        '文昌': (19.5433, 110.7977), '文昌市': (19.5433, 110.7977),
        '万宁': (18.7953, 110.3910), '万宁市': (18.7953, 110.3910),
        '东方': (19.1020, 108.6537), '东方市': (19.1020, 108.6537),
        
        # 青海省
        '西宁': (36.6171, 101.7785), '西宁市': (36.6171, 101.7785),
        '海东': (36.5020, 102.4017), '海东市': (36.5020, 102.4017),
        '格尔木': (36.4029, 94.9030), '格尔木市': (36.4029, 94.9030),
        '德令哈': (37.3698, 97.3610), '德令哈市': (37.3698, 97.3610),
        
        # 台湾省
        '台北': (25.0330, 121.5654), '台北市': (25.0330, 121.5654),
        '新北': (25.0120, 121.4657), '新北市': (25.0120, 121.4657),
        '桃园': (24.9936, 121.3010), '桃园市': (24.9936, 121.3010),
        '台中': (24.1477, 120.6736), '台中市': (24.1477, 120.6736),
        '台南': (22.9999, 120.2269), '台南市': (22.9999, 120.2269),
        '高雄': (22.6273, 120.3014), '高雄市': (22.6273, 120.3014),
        '基隆': (25.1283, 121.7419), '基隆市': (25.1283, 121.7419),
        '新竹': (24.8067, 120.9688), '新竹市': (24.8067, 120.9688),
        '嘉义': (23.4800, 120.4491), '嘉义市': (23.4800, 120.4491),
        
        # 香港特别行政区
        '香港': (22.3193, 114.1694),
        
        # 澳门特别行政区
        '澳门': (22.1987, 113.5439),
    }

    # 站点关键词到城市的映射 - 完整版
    SITE_CITY_PATTERNS = {
        # 直辖市
        '北京': ['北京', '京', '北平', '燕京'],
        '上海': ['上海', '沪', '申城', '魔都'],
        '天津': ['天津', '津', '津门'],
        '重庆': ['重庆', '渝', '山城', '巴渝'],
        
        # 广东省
        '广州': ['广州', '穗', '广东广州', '羊城', '花城', '番禺', '天河', '白云'],
        '深圳': ['深圳', '深', '鹏城', '宝安', '龙岗', '福田', '南山', '罗湖'],
        '珠海': ['珠海', '香洲', '斗门', '金湾'],
        '佛山': ['佛山', '禅城', '南海', '顺德', '高明', '三水'],
        '东莞': ['东莞', '莞城', '虎门', '长安', '厚街'],
        '惠州': ['惠州', '惠城', '惠阳', '博罗', '惠东', '龙门'],
        '中山': ['中山', '石岐', '小榄', '古镇'],
        '江门': ['江门', '蓬江', '江海', '新会', '台山', '开平', '鹤山', '恩平'],
        '湛江': ['湛江', '赤坎', '霞山', '坡头', '麻章', '雷州', '廉江', '吴川', '遂溪', '徐闻'],
        '茂名': ['茂名', '茂南', '电白', '高州', '化州', '信宜'],
        '肇庆': ['肇庆', '端州', '鼎湖', '高要', '四会', '广宁', '怀集', '封开', '德庆'],
        '汕头': ['汕头', '龙湖', '金平', '濠江', '潮阳', '潮南', '澄海', '南澳'],
        '潮州': ['潮州', '湘桥', '潮安', '饶平'],
        '揭阳': ['揭阳', '榕城', '揭东', '揭西', '惠来', '普宁'],
        '汕尾': ['汕尾', '海丰', '陆河', '陆丰'],
        '梅州': ['梅州', '梅江', '梅县', '大埔', '丰顺', '五华', '平远', '蕉岭', '兴宁'],
        '河源': ['河源', '源城', '紫金', '龙川', '连平', '和平', '东源'],
        '清远': ['清远', '清城', '清新', '佛冈', '阳山', '连山', '连南', '英德', '连州'],
        '韶关': ['韶关', '武江', '浈江', '曲江', '始兴', '仁化', '翁源', '乳源', '新丰', '乐昌', '南雄'],
        '阳江': ['阳江', '江城', '阳东', '阳西', '阳春'],
        '云浮': ['云浮', '云城', '云安', '新兴', '郁南', '罗定'],
        
        # 江苏省
        '南京': ['南京', '宁', '江苏南京', '金陵', '江宁', '溧水', '高淳', '六合', '浦口', '栖霞', '鼓楼', '建邺', '秦淮'],
        '苏州': ['苏州', '苏', '姑苏', '吴中', '相城', '虎丘', '吴江', '常熟', '张家港', '昆山', '太仓'],
        '无锡': ['无锡', '锡', '梁溪', '锡山', '惠山', '滨湖', '新吴', '江阴', '宜兴'],
        '常州': ['常州', '常', '天宁', '钟楼', '新北', '武进', '金坛', '溧阳'],
        '南通': ['南通', '通', '崇川', '港闸', '通州', '海安', '如东', '启东', '如皋', '海门'],
        '扬州': ['扬州', '扬', '广陵', '邗江', '江都', '宝应', '仪征', '高邮'],
        '镇江': ['镇江', '镇', '京口', '润州', '丹徒', '丹阳', '扬中', '句容'],
        '徐州': ['徐州', '徐', '鼓楼', '云龙', '贾汪', '泉山', '铜山', '丰县', '沛县', '睢宁', '新沂', '邳州'],
        '盐城': ['盐城', '盐', '亭湖', '盐都', '大丰', '响水', '滨海', '阜宁', '射阳', '建湖', '东台'],
        '淮安': ['淮安', '淮', '清江浦', '淮安', '淮阴', '洪泽', '涟水', '盱眙', '金湖'],
        '连云港': ['连云港', '连', '连云', '海州', '赣榆', '东海', '灌云', '灌南'],
        '泰州': ['泰州', '泰', '海陵', '高港', '姜堰', '兴化', '靖江', '泰兴'],
        '宿迁': ['宿迁', '宿', '宿城', '宿豫', '沭阳', '泗阳', '泗洪'],
        
        # 浙江省
        '杭州': ['杭州', '杭', '浙江杭州', '上城', '下城', '江干', '拱墅', '西湖', '滨江', '萧山', '余杭', '富阳', '临安', '桐庐', '淳安', '建德'],
        '宁波': ['宁波', '甬', '海曙', '江北', '北仑', '镇海', '鄞州', '奉化', '象山', '宁海', '余姚', '慈溪'],
        '温州': ['温州', '温', '鹿城', '龙湾', '瓯海', '洞头', '永嘉', '平阳', '苍南', '文成', '泰顺', '瑞安', '乐清', '龙港'],
        '绍兴': ['绍兴', '绍', '越城', '柯桥', '上虞', '新昌', '诸暨', '嵊州'],
        '嘉兴': ['嘉兴', '嘉', '南湖', '秀洲', '嘉善', '海盐', '海宁', '平湖', '桐乡'],
        '金华': ['金华', '金', '婺城', '金东', '武义', '浦江', '磐安', '兰溪', '义乌', '东阳', '永康'],
        '台州': ['台州', '台', '椒江', '黄岩', '路桥', '三门', '天台', '仙居', '温岭', '临海', '玉环'],
        '湖州': ['湖州', '湖', '吴兴', '南浔', '德清', '长兴', '安吉'],
        '衢州': ['衢州', '衢', '柯城', '衢江', '常山', '开化', '龙游', '江山'],
        '丽水': ['丽水', '丽', '莲都', '青田', '缙云', '遂昌', '松阳', '云和', '庆元', '景宁', '龙泉'],
        '舟山': ['舟山', '舟', '定海', '普陀', '岱山', '嵊泗'],
        
        # 福建省
        '福州': ['福州', '榕', '福建福州', '鼓楼', '台江', '仓山', '马尾', '晋安', '长乐', '闽侯', '连江', '罗源', '闽清', '永泰', '平潭', '福清'],
        '厦门': ['厦门', '厦', '鹭岛', '思明', '湖里', '集美', '同安', '翔安'],
        '泉州': ['泉州', '泉', '鲤城', '丰泽', '洛江', '泉港', '惠安', '安溪', '永春', '德化', '金门', '石狮', '晋江', '南安'],
        '漳州': ['漳州', '漳', '芗城', '龙文', '云霄', '漳浦', '诏安', '长泰', '东山', '南靖', '平和', '华安', '龙海'],
        '莆田': ['莆田', '莆', '城厢', '涵江', '荔城', '秀屿', '仙游'],
        '龙岩': ['龙岩', '岩', '新罗', '永定', '长汀', '上杭', '武平', '连城', '漳平'],
        '三明': ['三明', '明', '梅列', '三元', '明溪', '清流', '宁化', '大田', '尤溪', '沙县', '将乐', '泰宁', '建宁', '永安'],
        '南平': ['南平', '南', '延平', '建阳', '顺昌', '浦城', '光泽', '松溪', '政和', '邵武', '武夷山', '建瓯'],
        '宁德': ['宁德', '宁', '蕉城', '霞浦', '古田', '屏南', '寿宁', '周宁', '柘荣', '福安', '福鼎'],
        
        # 山东省
        '济南': ['济南', '济', '山东济南', '历下', '市中', '槐荫', '天桥', '历城', '长清', '章丘', '济阳', '莱芜', '钢城', '平阴', '商河'],
        '青岛': ['青岛', '青', '市南', '市北', '黄岛', '崂山', '李沧', '城阳', '即墨', '胶州', '平度', '莱西'],
        '烟台': ['烟台', '烟', '芝罘', '福山', '牟平', '莱山', '长岛', '龙口', '莱阳', '莱州', '蓬莱', '招远', '栖霞', '海阳'],
        '威海': ['威海', '威', '环翠', '文登', '荣成', '乳山'],
        '潍坊': ['潍坊', '潍', '潍城', '寒亭', '坊子', '奎文', '临朐', '昌乐', '青州', '诸城', '寿光', '安丘', '高密', '昌邑'],
        '淄博': ['淄博', '淄', '淄川', '张店', '博山', '临淄', '周村', '桓台', '高青', '沂源'],
        '临沂': ['临沂', '临', '兰山', '罗庄', '河东', '沂南', '郯城', '沂水', '兰陵', '费县', '平邑', '莒南', '蒙阴', '临沭'],
        '济宁': ['济宁', '任城', '兖州', '微山', '鱼台', '金乡', '嘉祥', '汶上', '泗水', '梁山', '曲阜', '邹城'],
        '泰安': ['泰安', '泰', '泰山', '岱岳', '宁阳', '东平', '新泰', '肥城'],
        '聊城': ['聊城', '聊', '东昌府', '茌平', '阳谷', '莘县', '东阿', '冠县', '高唐', '临清'],
        '德州': ['德州', '德', '德城', '陵城', '宁津', '庆云', '临邑', '齐河', '平原', '夏津', '武城', '乐陵', '禹城'],
        '滨州': ['滨州', '滨', '滨城', '沾化', '惠民', '阳信', '无棣', '博兴', '邹平'],
        '东营': ['东营', '东', '东营区', '河口', '垦利', '利津', '广饶'],
        '菏泽': ['菏泽', '菏', '牡丹', '定陶', '曹县', '单县', '成武', '巨野', '郓城', '鄄城', '东明'],
        '日照': ['日照', '日', '东港', '岚山', '五莲', '莒县'],
        '枣庄': ['枣庄', '枣', '市中', '薛城', '峄城', '台儿庄', '山亭', '滕州'],
        
        # 河南省
        '郑州': ['郑州', '郑', '河南郑州', '中原', '二七', '管城', '金水', '上街', '惠济', '中牟', '巩义', '荥阳', '新密', '新郑', '登封'],
        '洛阳': ['洛阳', '洛', '老城', '西工', '瀍河', '涧西', '吉利', '洛龙', '孟津', '新安', '栾川', '嵩县', '汝阳', '宜阳', '洛宁', '伊川', '偃师'],
        '南阳': ['南阳', '宛', '卧龙', '宛城', '南召', '方城', '西峡', '镇平', '内乡', '淅川', '社旗', '唐河', '新野', '桐柏', '邓州'],
        '许昌': ['许昌', '许', '魏都', '建安', '鄢陵', '襄城', '禹州', '长葛'],
        '周口': ['周口', '周', '川汇', '淮阳', '扶沟', '西华', '商水', '沈丘', '郸城', '太康', '鹿邑', '项城'],
        '新乡': ['新乡', '新', '红旗', '卫滨', '凤泉', '牧野', '新乡县', '获嘉', '原阳', '延津', '封丘', '长垣', '卫辉', '辉县'],
        '商丘': ['商丘', '商', '梁园', '睢阳', '民权', '睢县', '宁陵', '柘城', '虞城', '夏邑', '永城'],
        '驻马店': ['驻马店', '驻', '驿城', '西平', '上蔡', '平舆', '正阳', '确山', '泌阳', '汝南', '遂平', '新蔡'],
        '信阳': ['信阳', '信', '浉河', '平桥', '罗山', '光山', '新县', '商城', '固始', '潢川', '淮滨', '息县'],
        '开封': ['开封', '汴', '龙亭', '顺河', '鼓楼', '禹王台', '祥符', '杞县', '通许', '尉氏', '兰考'],
        '平顶山': ['平顶山', '平', '新华', '卫东', '石龙', '湛河', '宝丰', '叶县', '鲁山', '郏县', '舞钢', '汝州'],
        '安阳': ['安阳', '安', '文峰', '北关', '殷都', '龙安', '安阳县', '汤阴', '滑县', '内黄', '林州'],
        '焦作': ['焦作', '焦', '解放', '中站', '马村', '山阳', '修武', '博爱', '武陟', '温县', '沁阳', '孟州'],
        '濮阳': ['濮阳', '濮', '华龙', '清丰', '南乐', '范县', '台前', '濮阳县'],
        '漯河': ['漯河', '漯', '源汇', '郾城', '召陵', '舞阳', '临颍'],
        '三门峡': ['三门峡', '峡', '湖滨', '陕州', '渑池', '卢氏', '义马', '灵宝'],
        '鹤壁': ['鹤壁', '鹤', '鹤山', '山城', '淇滨', '浚县', '淇县'],
        
        # 河北省
        '石家庄': ['石家庄', '石', '河北石家庄', '长安', '桥西', '新华', '井陉', '裕华', '藁城', '鹿泉', '栾城', '井陉县', '正定', '行唐', '灵寿', '高邑', '深泽', '赞皇', '无极', '平山', '元氏', '赵县', '辛集', '晋州', '新乐'],
        '唐山': ['唐山', '唐', '路南', '路北', '古冶', '开平', '丰南', '丰润', '曹妃甸', '滦南', '乐亭', '迁西', '玉田', '遵化', '迁安', '滦州'],
        '邯郸': ['邯郸', '邯', '邯山', '丛台', '复兴', '峰峰', '肥乡', '永年', '临漳', '成安', '大名', '涉县', '磁县', '邱县', '鸡泽', '广平', '馆陶', '魏县', '曲周', '武安'],
        '保定': ['保定', '保', '竞秀', '莲池', '满城', '清苑', '徐水', '涞水', '阜平', '定兴', '唐县', '高阳', '容城', '涞源', '望都', '安新', '易县', '曲阳', '蠡县', '顺平', '博野', '雄县', '涿州', '定州', '安国', '高碑店'],
        '沧州': ['沧州', '沧', '新华', '运河', '沧县', '青县', '东光', '海兴', '盐山', '肃宁', '南皮', '吴桥', '献县', '孟村', '泊头', '任丘', '黄骅', '河间'],
        '邢台': ['邢台', '邢', '桥东', '桥西', '邢台县', '临城', '内丘', '柏乡', '隆尧', '任县', '南和', '宁晋', '巨鹿', '新河', '广宗', '平乡', '威县', '清河', '临西', '南宫', '沙河'],
        '廊坊': ['廊坊', '廊', '安次', '广阳', '固安', '永清', '香河', '大城', '文安', '大厂', '霸州', '三河'],
        '张家口': ['张家口', '张', '桥东', '桥西', '宣化', '下花园', '万全', '崇礼', '张北', '康保', '沽源', '尚义', '蔚县', '阳原', '怀安', '怀来', '涿鹿', '赤城'],
        '承德': ['承德', '承', '双桥', '双滦', '鹰手营子', '承德县', '兴隆', '滦平', '隆化', '丰宁', '宽城', '围场', '平泉'],
        '秦皇岛': ['秦皇岛', '秦', '海港', '山海关', '北戴河', '抚宁', '青龙', '昌黎', '卢龙'],
        '衡水': ['衡水', '衡', '桃城', '冀州', '枣强', '武邑', '武强', '饶阳', '安平', '故城', '景县', '阜城', '深州'],
        
        # 湖北省
        '武汉': ['武汉', '汉', '湖北武汉', '江岸', '江汉', '硚口', '汉阳', '武昌', '青山', '洪山', '东西湖', '汉南', '蔡甸', '江夏', '黄陂', '新洲'],
        '襄阳': ['襄阳', '襄', '襄城', '樊城', '襄州', '南漳', '谷城', '保康', '老河口', '枣阳', '宜城'],
        '宜昌': ['宜昌', '宜', '西陵', '伍家岗', '点军', '猇亭', '夷陵', '远安', '兴山', '秭归', '长阳', '五峰', '宜都', '当阳', '枝江'],
        '荆州': ['荆州', '荆', '沙市', '荆州', '公安', '监利', '江陵', '石首', '洪湖', '松滋'],
        '黄冈': ['黄冈', '黄', '黄州', '团风', '红安', '罗田', '英山', '浠水', '蕲春', '黄梅', '麻城', '武穴'],
        '孝感': ['孝感', '孝', '孝南', '孝昌', '大悟', '云梦', '应城', '安陆', '汉川'],
        '十堰': ['十堰', '十', '茅箭', '张湾', '郧阳', '郧西', '竹山', '竹溪', '房县', '丹江口'],
        '荆门': ['荆门', '荆', '东宝', '掇刀', '沙洋', '钟祥', '京山'],
        '黄石': ['黄石', '黄', '黄石港', '西塞山', '下陆', '铁山', '阳新', '大冶'],
        '咸宁': ['咸宁', '咸', '咸安', '嘉鱼', '通城', '崇阳', '通山', '赤壁'],
        '随州': ['随州', '随', '曾都', '随县', '广水'],
        '鄂州': ['鄂州', '鄂', '梁子湖', '华容', '鄂城'],
        '恩施': ['恩施', '恩', '恩施市', '利川', '建始', '巴东', '宣恩', '咸丰', '来凤', '鹤峰'],
        
        # 湖南省
        '长沙': ['长沙', '长', '湖南长沙', '芙蓉', '天心', '岳麓', '开福', '雨花', '望城', '长沙县', '浏阳', '宁乡'],
        '株洲': ['株洲', '株', '荷塘', '芦淞', '石峰', '天元', '渌口', '攸县', '茶陵', '炎陵', '醴陵'],
        '湘潭': ['湘潭', '潭', '雨湖', '岳塘', '湘潭县', '湘乡', '韶山'],
        '衡阳': ['衡阳', '衡', '珠晖', '雁峰', '石鼓', '蒸湘', '南岳', '衡阳县', '衡南', '衡山', '衡东', '祁东', '耒阳', '常宁'],
        '邵阳': ['邵阳', '邵', '双清', '大祥', '北塔', '邵东', '新邵', '邵阳县', '隆回', '洞口', '绥宁', '新宁', '城步', '武冈'],
        '岳阳': ['岳阳', '岳', '岳阳楼', '云溪', '君山', '岳阳县', '华容', '湘阴', '平江', '汨罗', '临湘'],
        '常德': ['常德', '常', '武陵', '鼎城', '安乡', '汉寿', '澧县', '临澧', '桃源', '石门', '津市'],
        '张家界': ['张家界', '张', '永定', '武陵源', '慈利', '桑植'],
        '益阳': ['益阳', '益', '资阳', '赫山', '南县', '桃江', '安化', '沅江'],
        '郴州': ['郴州', '郴', '北湖', '苏仙', '桂阳', '宜章', '永兴', '嘉禾', '临武', '汝城', '桂东', '安仁', '资兴'],
        '永州': ['永州', '永', '零陵', '冷水滩', '祁阳', '东安', '双牌', '道县', '江永', '宁远', '蓝山', '新田', '江华'],
        '怀化': ['怀化', '怀', '鹤城', '中方', '沅陵', '辰溪', '溆浦', '会同', '麻阳', '新晃', '芷江', '靖州', '通道', '洪江'],
        '娄底': ['娄底', '娄', '娄星', '双峰', '新化', '冷水江', '涟源'],
        
        # 四川省
        '成都': ['成都', '蓉', '四川成都', '锦江', '青羊', '金牛', '武侯', '成华', '龙泉驿', '青白江', '新都', '温江', '双流', '郫都', '金堂', '大邑', '蒲江', '新津', '都江堰', '彭州', '邛崃', '崇州', '简阳'],
        '绵阳': ['绵阳', '绵', '涪城', '游仙', '安州', '三台', '盐亭', '梓潼', '北川', '平武', '江油'],
        '德阳': ['德阳', '德', '旌阳', '罗江', '中江', '广汉', '什邡', '绵竹'],
        '宜宾': ['宜宾', '宜', '翠屏', '南溪', '叙州', '江安', '长宁', '高县', '珙县', '筠连', '兴文', '屏山'],
        '南充': ['南充', '南', '顺庆', '高坪', '嘉陵', '南部', '营山', '蓬安', '仪陇', '西充', '阆中'],
        '泸州': ['泸州', '泸', '江阳', '纳溪', '龙马潭', '泸县', '合江', '叙永', '古蔺'],
        '达州': ['达州', '达', '通川', '达川', '宣汉', '开江', '大竹', '渠县', '万源'],
        '乐山': ['乐山', '乐', '市中', '沙湾', '五通桥', '金口河', '犍为', '井研', '夹江', '沐川', '峨边', '马边', '峨眉山'],
        '内江': ['内江', '内', '市中', '东兴', '威远', '资中', '隆昌'],
        '自贡': ['自贡', '自', '自流井', '贡井', '大安', '沿滩', '荣县', '富顺'],
        '攀枝花': ['攀枝花', '攀', '东区', '西区', '仁和', '米易', '盐边'],
        '眉山': ['眉山', '眉', '东坡', '彭山', '仁寿', '洪雅', '丹棱', '青神'],
        '遂宁': ['遂宁', '遂', '船山', '安居', '蓬溪', '射洪', '大英'],
        '广安': ['广安', '广', '广安区', '前锋', '岳池', '武胜', '邻水', '华蓥'],
        '巴中': ['巴中', '巴', '巴州', '恩阳', '通江', '南江', '平昌'],
        '资阳': ['资阳', '资', '雁江', '安岳', '乐至'],
        '雅安': ['雅安', '雅', '雨城', '名山', '荥经', '汉源', '石棉', '天全', '芦山', '宝兴'],
        '广元': ['广元', '元', '利州', '昭化', '朝天', '旺苍', '青川', '剑阁', '苍溪'],
        
        # 陕西省
        '西安': ['西安', '镐', '陕西西安', '新城', '碑林', '莲湖', '灞桥', '未央', '雁塔', '阎良', '临潼', '长安', '高陵', '鄠邑', '蓝田', '周至'],
        '宝鸡': ['宝鸡', '宝', '渭滨', '金台', '陈仓', '凤翔', '岐山', '扶风', '眉县', '陇县', '千阳', '麟游', '凤县', '太白'],
        '咸阳': ['咸阳', '咸', '秦都', '杨陵', '渭城', '三原', '泾阳', '乾县', '礼泉', '永寿', '长武', '旬邑', '淳化', '武功', '兴平', '彬州'],
        '渭南': ['渭南', '渭', '临渭', '华州', '潼关', '大荔', '合阳', '澄城', '蒲城', '白水', '富平', '韩城', '华阴'],
        '汉中': ['汉中', '汉', '汉台', '南郑', '城固', '洋县', '西乡', '勉县', '宁强', '略阳', '镇巴', '留坝', '佛坪'],
        '榆林': ['榆林', '榆', '榆阳', '横山', '府谷', '靖边', '定边', '绥德', '米脂', '佳县', '吴堡', '清涧', '子洲', '神木'],
        '安康': ['安康', '安', '汉滨', '汉阴', '石泉', '宁陕', '紫阳', '岚皋', '平利', '镇坪', '旬阳', '白河'],
        '商洛': ['商洛', '商', '商州', '洛南', '丹凤', '商南', '山阳', '镇安', '柞水'],
        '延安': ['延安', '延', '宝塔', '安塞', '延长', '延川', '志丹', '吴起', '甘泉', '富县', '洛川', '宜川', '黄龙', '黄陵', '子长'],
        '铜川': ['铜川', '铜', '王益', '印台', '耀州', '宜君'],
        
        # 辽宁省
        '沈阳': ['沈阳', '沈', '辽宁沈阳', '和平', '沈河', '大东', '皇姑', '铁西', '苏家屯', '浑南', '沈北', '于洪', '辽中', '康平', '法库', '新民'],
        '大连': ['大连', '大', '中山', '西岗', '沙河口', '甘井子', '旅顺口', '金州', '普兰店', '长海', '瓦房店', '庄河'],
        '鞍山': ['鞍山', '鞍', '铁东', '铁西', '立山', '千山', '台安', '岫岩', '海城'],
        '抚顺': ['抚顺', '抚', '新抚', '东洲', '望花', '顺城', '抚顺县', '新宾', '清原'],
        '本溪': ['本溪', '本', '平山', '溪湖', '明山', '南芬', '本溪县', '桓仁'],
        '丹东': ['丹东', '丹', '元宝', '振兴', '振安', '宽甸', '东港', '凤城'],
        '锦州': ['锦州', '锦', '古塔', '凌河', '太和', '黑山', '义县', '凌海', '北镇'],
        '营口': ['营口', '营', '站前', '西市', '鲅鱼圈', '老边', '盖州', '大石桥'],
        '阜新': ['阜新', '阜', '海州', '新邱', '太平', '清河门', '细河', '阜新县', '彰武'],
        '辽阳': ['辽阳', '辽', '白塔', '文圣', '宏伟', '弓长岭', '太子河', '辽阳县', '灯塔'],
        '盘锦': ['盘锦', '盘', '双台子', '兴隆台', '大洼', '盘山'],
        '铁岭': ['铁岭', '铁', '银州', '清河', '铁岭县', '西丰', '昌图', '调兵山', '开原'],
        '朝阳': ['朝阳', '朝', '双塔', '龙城', '朝阳县', '建平', '喀左', '北票', '凌源'],
        '葫芦岛': ['葫芦岛', '葫', '连山', '龙港', '南票', '绥中', '建昌', '兴城'],
        
        # 吉林省
        '长春': ['长春', '春', '吉林长春', '南关', '宽城', '朝阳', '二道', '绿园', '双阳', '九台', '农安', '榆树', '德惠'],
        '吉林': ['吉林', '吉', '昌邑', '龙潭', '船营', '丰满', '永吉', '蛟河', '桦甸', '舒兰', '磐石'],
        '四平': ['四平', '四', '铁西', '铁东', '梨树', '伊通', '公主岭', '双辽'],
        '辽源': ['辽源', '辽', '龙山', '西安', '东丰', '东辽'],
        '通化': ['通化', '通', '东昌', '二道江', '通化县', '辉南', '柳河', '梅河口', '集安'],
        '白山': ['白山', '白', '浑江', '江源', '抚松', '靖宇', '长白', '临江'],
        '松原': ['松原', '松', '宁江', '前郭', '长岭', '乾安', '扶余'],
        '白城': ['白城', '白', '洮北', '镇赉', '通榆', '洮南', '大安'],
        '延边': ['延边', '延吉', '图们', '敦化', '珲春', '龙井', '和龙', '汪清', '安图'],
        
        # 黑龙江省
        '哈尔滨': ['哈尔滨', '哈', '黑龙江哈尔滨', '道里', '南岗', '道外', '平房', '松北', '香坊', '呼兰', '阿城', '双城', '依兰', '方正', '宾县', '巴彦', '木兰', '通河', '延寿', '尚志', '五常'],
        '齐齐哈尔': ['齐齐哈尔', '齐', '龙沙', '建华', '铁锋', '昂昂溪', '富拉尔基', '碾子山', '梅里斯', '龙江', '依安', '泰来', '甘南', '富裕', '克山', '克东', '拜泉', '讷河'],
        '鸡西': ['鸡西', '鸡', '鸡冠', '恒山', '滴道', '梨树', '城子河', '麻山', '鸡东', '虎林', '密山'],
        '鹤岗': ['鹤岗', '鹤', '向阳', '工农', '南山', '兴安', '东山', '兴山', '萝北', '绥滨'],
        '双鸭山': ['双鸭山', '双', '尖山', '岭东', '四方台', '宝山', '集贤', '友谊', '宝清', '饶河'],
        '大庆': ['大庆', '庆', '萨尔图', '龙凤', '让胡路', '红岗', '大同', '肇州', '肇源', '林甸', '杜尔伯特'],
        '伊春': ['伊春', '伊', '伊美', '乌翠', '友好', '金林', '嘉荫', '汤旺', '丰林', '大箐山', '南岔', '铁力'],
        '佳木斯': ['佳木斯', '佳', '向阳', '前进', '东风', '郊区', '桦南', '桦川', '汤原', '同江', '富锦', '抚远'],
        '七台河': ['七台河', '七', '新兴', '桃山', '茄子河', '勃利'],
        '牡丹江': ['牡丹江', '牡', '东安', '阳明', '爱民', '西安', '林口', '绥芬河', '海林', '宁安', '穆棱', '东宁'],
        '黑河': ['黑河', '黑', '爱辉', '逊克', '孙吴', '北安', '五大连池', '嫩江'],
        '绥化': ['绥化', '绥', '北林', '望奎', '兰西', '青冈', '庆安', '明水', '绥棱', '安达', '肇东', '海伦'],
        
        # 安徽省
        '合肥': ['合肥', '合', '安徽合肥', '瑶海', '庐阳', '蜀山', '包河', '长丰', '肥东', '肥西', '庐江', '巢湖'],
        '芜湖': ['芜湖', '芜', '镜湖', '弋江', '鸠江', '三山', '芜湖县', '繁昌', '南陵', '无为'],
        '蚌埠': ['蚌埠', '蚌', '龙子湖', '蚌山', '禹会', '淮上', '怀远', '五河', '固镇'],
        '淮南': ['淮南', '淮', '大通', '田家庵', '谢家集', '八公山', '潘集', '凤台', '寿县'],
        '马鞍山': ['马鞍山', '马', '花山', '雨山', '博望', '当涂', '含山', '和县'],
        '淮北': ['淮北', '淮', '杜集', '相山', '烈山', '濉溪'],
        '铜陵': ['铜陵', '铜', '铜官', '义安', '郊区', '枞阳'],
        '安庆': ['安庆', '安', '迎江', '大观', '宜秀', '怀宁', '太湖', '宿松', '望江', '岳西', '桐城', '潜山'],
        '黄山': ['黄山', '黄', '屯溪', '黄山', '徽州', '歙县', '休宁', '黟县', '祁门'],
        '滁州': ['滁州', '滁', '琅琊', '南谯', '来安', '全椒', '定远', '凤阳', '天长', '明光'],
        '阜阳': ['阜阳', '阜', '颍州', '颍东', '颍泉', '临泉', '太和', '阜南', '颍上', '界首'],
        '宿州': ['宿州', '宿', '埇桥', '砀山', '萧县', '灵璧', '泗县'],
        '六安': ['六安', '六', '金安', '裕安', '叶集', '霍邱', '舒城', '金寨', '霍山'],
        '亳州': ['亳州', '亳', '谯城', '涡阳', '蒙城', '利辛'],
        '池州': ['池州', '池', '贵池', '东至', '石台', '青阳'],
        '宣城': ['宣城', '宣', '宣州', '郎溪', '泾县', '绩溪', '旌德', '宁国', '广德'],
        
        # 江西省
        '南昌': ['南昌', '洪', '江西南昌', '东湖', '西湖', '青云谱', '青山湖', '新建', '红谷滩', '南昌县', '安义', '进贤'],
        '景德镇': ['景德镇', '景', '昌江', '珠山', '浮梁', '乐平'],
        '萍乡': ['萍乡', '萍', '安源', '湘东', '莲花', '上栗', '芦溪'],
        '九江': ['九江', '九', '濂溪', '浔阳', '柴桑', '武宁', '修水', '永修', '德安', '都昌', '湖口', '彭泽', '瑞昌', '共青城', '庐山'],
        '新余': ['新余', '余', '渝水', '分宜'],
        '鹰潭': ['鹰潭', '鹰', '月湖', '余江', '贵溪'],
        '赣州': ['赣州', '赣', '章贡', '南康', '赣县', '信丰', '大余', '上犹', '崇义', '安远', '定南', '全南', '宁都', '于都', '兴国', '会昌', '寻乌', '石城', '瑞金', '龙南'],
        '吉安': ['吉安', '吉', '吉州', '青原', '吉安县', '吉水', '峡江', '新干', '永丰', '泰和', '遂川', '万安', '安福', '永新', '井冈山'],
        '宜春': ['宜春', '宜', '袁州', '奉新', '万载', '上高', '宜丰', '靖安', '铜鼓', '丰城', '樟树', '高安'],
        '抚州': ['抚州', '抚', '临川', '东乡', '南城', '黎川', '南丰', '崇仁', '乐安', '宜黄', '金溪', '资溪', '广昌'],
        '上饶': ['上饶', '饶', '信州', '广丰', '广信', '玉山', '铅山', '横峰', '弋阳', '余干', '鄱阳', '万年', '婺源', '德兴'],
        
        # 贵州省
        '贵阳': ['贵阳', '筑', '贵州贵阳', '南明', '云岩', '花溪', '乌当', '白云', '观山湖', '开阳', '息烽', '修文', '清镇'],
        '遵义': ['遵义', '遵', '红花岗', '汇川', '播州', '桐梓', '绥阳', '正安', '道真', '务川', '凤冈', '湄潭', '余庆', '习水', '赤水', '仁怀'],
        '六盘水': ['六盘水', '六', '钟山', '六枝特', '水城', '盘州'],
        '安顺': ['安顺', '安', '西秀', '平坝', '普定', '镇宁', '关岭', '紫云'],
        '毕节': ['毕节', '毕', '七星关', '大方', '黔西', '金沙', '织金', '纳雍', '威宁', '赫章'],
        '铜仁': ['铜仁', '铜', '碧江', '万山', '江口', '玉屏', '石阡', '思南', '印江', '德江', '沿河', '松桃'],
        '黔东南': ['黔东南', '凯里', '黄平', '施秉', '三穗', '镇远', '岑巩', '天柱', '锦屏', '剑河', '台江', '黎平', '榕江', '从江', '雷山', '麻江', '丹寨'],
        '黔南': ['黔南', '都匀', '福泉', '荔波', '贵定', '瓮安', '独山', '平塘', '罗甸', '长顺', '龙里', '惠水', '三都'],
        '黔西南': ['黔西南', '兴义', '兴仁', '普安', '晴隆', '贞丰', '望谟', '册亨', '安龙'],
        
        # 云南省
        '昆明': ['昆明', '昆', '云南昆明', '五华', '盘龙', '官渡', '西山', '东川', '呈贡', '晋宁', '富民', '宜良', '石林', '嵩明', '禄劝', '寻甸', '安宁'],
        '曲靖': ['曲靖', '曲', '麒麟', '沾益', '马龙', '陆良', '师宗', '罗平', '富源', '会泽', '宣威'],
        '玉溪': ['玉溪', '玉', '红塔', '江川', '通海', '华宁', '易门', '峨山', '新平', '元江', '澄江'],
        '保山': ['保山', '保', '隆阳', '施甸', '龙陵', '昌宁', '腾冲'],
        '昭通': ['昭通', '昭', '昭阳', '鲁甸', '巧家', '盐津', '大关', '永善', '绥江', '镇雄', '彝良', '威信', '水富'],
        '丽江': ['丽江', '丽', '古城', '玉龙', '永胜', '华坪', '宁蒗'],
        '普洱': ['普洱', '普', '思茅', '宁洱', '墨江', '景东', '景谷', '镇沅', '江城', '孟连', '澜沧', '西盟'],
        '临沧': ['临沧', '临', '临翔', '凤庆', '云县', '永德', '镇康', '双江', '耿马', '沧源'],
        '楚雄': ['楚雄', '楚', '楚雄市', '双柏', '牟定', '南华', '姚安', '大姚', '永仁', '元谋', '武定', '禄丰'],
        '红河': ['红河', '蒙自', '个旧', '开远', '弥勒', '建水', '石屏', '泸西', '元阳', '红河县', '金平', '绿春', '河口', '屏边'],
        '文山': ['文山', '文', '文山市', '砚山', '西畴', '麻栗坡', '马关', '丘北', '广南', '富宁'],
        '西双版纳': ['西双版纳', '景洪', '勐海', '勐腊'],
        '大理': ['大理', '大理市', '漾濞', '祥云', '宾川', '弥渡', '南涧', '巍山', '永平', '云龙', '洱源', '剑川', '鹤庆'],
        '德宏': ['德宏', '芒市', '瑞丽', '梁河', '盈江', '陇川'],
        '怒江': ['怒江', '泸水', '福贡', '贡山', '兰坪'],
        '迪庆': ['迪庆', '香格里拉', '德钦', '维西'],
        
        # 甘肃省
        '兰州': ['兰州', '兰', '甘肃兰州', '城关', '七里河', '西固', '安宁', '红古', '永登', '皋兰', '榆中'],
        '嘉峪关': ['嘉峪关', '嘉'],
        '金昌': ['金昌', '金', '金川', '永昌'],
        '白银': ['白银', '白', '白银区', '平川', '靖远', '会宁', '景泰'],
        '天水': ['天水', '天', '秦州', '麦积', '清水', '秦安', '甘谷', '武山', '张家川'],
        '武威': ['武威', '武', '凉州', '民勤', '古浪', '天祝'],
        '张掖': ['张掖', '张', '甘州', '肃南', '民乐', '临泽', '高台', '山丹'],
        '平凉': ['平凉', '平', '崆峒', '泾川', '灵台', '崇信', '华亭', '庄浪', '静宁'],
        '酒泉': ['酒泉', '酒', '肃州', '金塔', '瓜州', '肃北', '阿克塞', '玉门', '敦煌'],
        '庆阳': ['庆阳', '庆', '西峰', '庆城', '环县', '华池', '合水', '正宁', '宁县', '镇原'],
        '定西': ['定西', '定', '安定', '通渭', '陇西', '渭源', '临洮', '漳县', '岷县'],
        '陇南': ['陇南', '陇', '武都', '成县', '文县', '宕昌', '康县', '西和', '礼县', '徽县', '两当'],
        '临夏': ['临夏', '临夏市', '临夏县', '康乐', '永靖', '广河', '和政', '东乡', '积石山'],
        '甘南': ['甘南', '合作', '临潭', '卓尼', '舟曲', '迭部', '玛曲', '碌曲', '夏河'],
        
        # 内蒙古自治区
        '呼和浩特': ['呼和浩特', '呼', '新城', '回民', '玉泉', '赛罕', '土左旗', '托克托', '和林格尔', '清水河', '武川'],
        '包头': ['包头', '包', '东河', '昆都仑', '青山', '石拐', '白云鄂博', '九原', '土右旗', '固阳', '达茂旗'],
        '乌海': ['乌海', '乌', '海勃湾', '海南', '乌达'],
        '赤峰': ['赤峰', '赤', '红山', '元宝山', '松山', '阿旗', '巴林左旗', '巴林右旗', '林西', '克旗', '翁旗', '喀旗', '宁城', '敖汉'],
        '通辽': ['通辽', '通', '科尔沁', '科左中旗', '科左后旗', '开鲁', '库伦', '奈曼', '扎鲁特', '霍林郭勒'],
        '鄂尔多斯': ['鄂尔多斯', '鄂', '东胜', '康巴什', '达拉特', '准格尔', '鄂前旗', '鄂旗', '杭锦旗', '乌审旗', '伊旗'],
        '呼伦贝尔': ['呼伦贝尔', '呼伦', '海拉尔', '扎赉诺尔', '阿荣旗', '莫旗', '鄂伦春', '鄂温克', '陈旗', '新左旗', '新右旗', '满洲里', '牙克石', '扎兰屯', '额尔古纳', '根河'],
        '巴彦淖尔': ['巴彦淖尔', '巴', '临河', '五原', '磴口', '乌拉特前旗', '乌拉特中旗', '乌拉特后旗', '杭锦后旗'],
        '乌兰察布': ['乌兰察布', '乌', '集宁', '卓资', '化德', '商都', '兴和', '凉城', '察右前旗', '察右中旗', '察右后旗', '四子王旗', '丰镇'],
        '兴安': ['兴安', '乌兰浩特', '阿尔山', '科右前旗', '科右中旗', '扎赉特', '突泉'],
        '锡林郭勒': ['锡林郭勒', '锡林浩特', '二连浩特', '阿巴嘎', '苏尼特左旗', '苏尼特右旗', '东乌旗', '西乌旗', '太仆寺', '镶黄旗', '正镶白旗', '正蓝旗', '多伦'],
        '阿拉善': ['阿拉善', '阿拉善左旗', '阿拉善右旗', '额济纳'],
        
        # 广西壮族自治区
        '南宁': ['南宁', '邕', '广西南宁', '兴宁', '青秀', '江南', '西乡塘', '良庆', '邕宁', '武鸣', '隆安', '马山', '上林', '宾阳', '横县'],
        '柳州': ['柳州', '柳', '城中', '鱼峰', '柳南', '柳北', '柳江', '柳城', '鹿寨', '融安', '融水', '三江'],
        '桂林': ['桂林', '桂', '秀峰', '叠彩', '象山', '七星', '雁山', '临桂', '阳朔', '灵川', '全州', '兴安', '永福', '灌阳', '龙胜', '资源', '平乐', '恭城', '荔浦'],
        '梧州': ['梧州', '梧', '万秀', '长洲', '龙圩', '苍梧', '藤县', '蒙山', '岑溪'],
        '北海': ['北海', '北', '海城', '银海', '铁山港', '合浦'],
        '防城港': ['防城港', '防', '港口', '防城', '上思', '东兴'],
        '钦州': ['钦州', '钦', '钦南', '钦北', '灵山', '浦北'],
        '贵港': ['贵港', '贵', '港北', '港南', '覃塘', '平南', '桂平'],
        '玉林': ['玉林', '玉', '玉州', '福绵', '容县', '陆川', '博白', '兴业', '北流'],
        '百色': ['百色', '百', '右江', '田阳', '田东', '平果', '德保', '那坡', '凌云', '乐业', '田林', '西林', '隆林', '靖西'],
        '贺州': ['贺州', '贺', '八步', '平桂', '昭平', '钟山', '富川'],
        '河池': ['河池', '河', '金城江', '宜州', '南丹', '天峨', '凤山', '东兰', '罗城', '环江', '巴马', '都安', '大化'],
        '来宾': ['来宾', '来', '兴宾', '忻城', '象州', '武宣', '金秀', '合山'],
        '崇左': ['崇左', '崇', '江州', '扶绥', '宁明', '龙州', '大新', '天等', '凭祥'],
        
        # 西藏自治区
        '拉萨': ['拉萨', '拉', '城关', '堆龙德庆', '达孜', '林周', '当雄', '尼木', '曲水', '墨竹工卡'],
        '日喀则': ['日喀则', '日', '桑珠孜', '南木林', '江孜', '定日', '萨迦', '拉孜', '昂仁', '谢通门', '白朗', '仁布', '康马', '定结', '仲巴', '亚东', '吉隆', '聂拉木', '萨嘎', '岗巴'],
        '昌都': ['昌都', '昌', '卡若', '江达', '贡觉', '类乌齐', '丁青', '察雅', '八宿', '左贡', '芒康', '洛隆', '边坝'],
        '林芝': ['林芝', '林', '巴宜', '工布江达', '米林', '墨脱', '波密', '察隅', '朗县'],
        '山南': ['山南', '山', '乃东', '扎囊', '贡嘎', '桑日', '琼结', '曲松', '措美', '洛扎', '加查', '隆子', '错那', '浪卡子'],
        '那曲': ['那曲', '那', '色尼', '嘉黎', '比如', '聂荣', '安多', '申扎', '索县', '班戈', '巴青', '尼玛', '双湖'],
        '阿里': ['阿里', '普兰', '札达', '噶尔', '日土', '革吉', '改则', '措勤'],
        
        # 宁夏回族自治区
        '银川': ['银川', '银', '宁夏银川', '兴庆', '西夏', '金凤', '永宁', '贺兰', '灵武'],
        '石嘴山': ['石嘴山', '石', '大武口', '惠农', '平罗'],
        '吴忠': ['吴忠', '吴', '利通', '红寺堡', '盐池', '同心', '青铜峡'],
        '固原': ['固原', '固', '原州', '西吉', '隆德', '泾源', '彭阳'],
        '中卫': ['中卫', '中', '沙坡头', '中宁', '海原'],
        
        # 新疆维吾尔自治区
        '乌鲁木齐': ['乌鲁木齐', '乌', '新疆乌鲁木齐', '天山', '沙依巴克', '新市', '水磨沟', '头屯河', '达坂城', '米东', '乌鲁木齐县'],
        '克拉玛依': ['克拉玛依', '克', '独山子', '克拉玛依区', '白碱滩', '乌尔禾'],
        '吐鲁番': ['吐鲁番', '吐', '高昌', '鄯善', '托克逊'],
        '哈密': ['哈密', '哈', '伊州', '巴里坤', '伊吾'],
        '昌吉': ['昌吉', '昌', '昌吉市', '阜康', '呼图壁', '玛纳斯', '奇台', '吉木萨尔', '木垒'],
        '博尔塔拉': ['博尔塔拉', '博乐', '阿拉山口', '精河', '温泉'],
        '巴音郭楞': ['巴音郭楞', '库尔勒', '轮台', '尉犁', '若羌', '且末', '焉耆', '和静', '和硕', '博湖'],
        '阿克苏': ['阿克苏', '阿', '阿克苏市', '温宿', '库车', '沙雅', '新和', '拜城', '乌什', '阿瓦提', '柯坪'],
        '克孜勒苏': ['克孜勒苏', '阿图什', '阿克陶', '阿合奇', '乌恰'],
        '喀什': ['喀什', '喀', '喀什市', '疏附', '疏勒', '英吉沙', '泽普', '莎车', '叶城', '麦盖提', '岳普湖', '伽师', '巴楚', '塔什库尔干'],
        '和田': ['和田', '和', '和田市', '和田县', '墨玉', '皮山', '洛浦', '策勒', '于田', '民丰'],
        '伊犁': ['伊犁', '伊宁', '奎屯', '霍尔果斯', '伊宁县', '察布查尔', '霍城', '巩留', '新源', '昭苏', '特克斯', '尼勒克'],
        '塔城': ['塔城', '塔', '塔城市', '乌苏', '额敏', '沙湾', '托里', '裕民', '和布克赛尔'],
        '阿勒泰': ['阿勒泰', '阿勒', '阿勒泰市', '布尔津', '富蕴', '福海', '哈巴河', '青河', '吉木乃'],
        '石河子': ['石河子'],
        '阿拉尔': ['阿拉尔'],
        '图木舒克': ['图木舒克'],
        '五家渠': ['五家渠'],
        '北屯': ['北屯'],
        '铁门关': ['铁门关'],
        '双河': ['双河'],
        '可克达拉': ['可克达拉'],
        '昆玉': ['昆玉'],
        '胡杨河': ['胡杨河'],
        
        # 海南省
        '海口': ['海口', '海', '海南海口', '秀英', '龙华', '琼山', '美兰'],
        '三亚': ['三亚', '三', '海棠', '吉阳', '天涯', '崖州'],
        '三沙': ['三沙', '西沙', '南沙'],
        '儋州': ['儋州', '儋'],
        '琼海': ['琼海'],
        '文昌': ['文昌'],
        '万宁': ['万宁'],
        '东方': ['东方'],
        '五指山': ['五指山'],
        
        # 青海省
        '西宁': ['西宁', '西', '青海西宁', '城东', '城中', '城西', '城北', '湟中', '湟源', '大通'],
        '海东': ['海东', '乐都', '平安', '民和', '互助', '化隆', '循化'],
        '海北': ['海北', '海晏', '祁连', '刚察', '门源'],
        '黄南': ['黄南', '同仁', '尖扎', '泽库', '河南'],
        '海南州': ['海南', '共和', '同德', '贵德', '兴海', '贵南'],
        '果洛': ['果洛', '玛沁', '班玛', '甘德', '达日', '久治', '玛多'],
        '玉树': ['玉树', '玉树市', '杂多', '称多', '治多', '囊谦', '曲麻莱'],
        '海西': ['海西', '格尔木', '德令哈', '茫崖', '乌兰', '都兰', '天峻'],
        
        # 台湾省
        '台北': ['台北', '北市'],
        '新北': ['新北', '新北市'],
        '桃园': ['桃园', '桃园市'],
        '台中': ['台中', '台中市'],
        '台南': ['台南', '台南市'],
        '高雄': ['高雄', '高雄市'],
        '基隆': ['基隆', '基隆市'],
        '新竹': ['新竹', '新竹市'],
        '嘉义': ['嘉义', '嘉义市'],
        
        # 香港特别行政区
        '香港': ['香港', '港', 'HK', 'Hong Kong'],
        
        # 澳门特别行政区
        '澳门': ['澳门', '澳', 'Macau', 'Macao'],
    }

    

    def __init__(self, express_id: int, tracking_num: str, parent_gui, parent=None):
        super().__init__(parent)
        self.express_id = express_id
        self.tracking_num = tracking_num
        self.parent_gui = parent_gui
        self.express_data = None
        self.query_thread = None
        self.estimator = DeliveryTimeEstimator(parent_gui.current_user_db) if parent_gui and parent_gui.current_user_db else None
        self.node_analyzer = None
        if parent_gui and hasattr(parent_gui, 'node_analyzer'):
            self.node_analyzer = parent_gui.node_analyzer
        self.init_ui()
        self.load_data()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{ProjectInfo.NAME} - 快递详情 - {self.tracking_num}")
        self.setMinimumSize(900, 750)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 使用QTabWidget来组织内容
        self.detail_tab_widget = QTabWidget()
        
        # ========== 标签页1：基本信息 ==========
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        self.info_group = QGroupBox("基本信息")
        self.info_layout = QGridLayout()
        self.info_group.setLayout(self.info_layout)
        info_layout.addWidget(self.info_group)
        
        self.remark_group = QGroupBox("备注")
        self.remark_layout = QVBoxLayout()
        self.remark_label = QLabel()
        self.remark_label.setWordWrap(True)
        self.remark_layout.addWidget(self.remark_label)
        self.remark_group.setLayout(self.remark_layout)
        info_layout.addWidget(self.remark_group)
        
        self.detail_tab_widget.addTab(info_widget, "📋 基本信息")
        
        # ========== 标签页2：物流轨迹 ==========
        track_widget = QWidget()
        track_layout = QVBoxLayout(track_widget)
        self.track_text = QTextEdit()
        self.track_text.setReadOnly(True)
        track_layout.addWidget(self.track_text)
        self.detail_tab_widget.addTab(track_widget, "📜 物流轨迹")
    
        # ========== 标签页3：地图轨迹 ==========
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        map_layout.setContentsMargins(0, 0, 0, 0)
        map_layout.setSpacing(0)

        # 合并后的紧凑工具栏（一行显示）
        compact_toolbar = QWidget()
        compact_toolbar.setFixedHeight(32)  # 固定高度32px
        compact_toolbar_layout = QHBoxLayout(compact_toolbar)
        compact_toolbar_layout.setContentsMargins(5, 2, 5, 2)
        compact_toolbar_layout.setSpacing(8)

        # 瓦片源选择（带图标）
        compact_toolbar_layout.addWidget(QLabel("🗺️"))
        self.tile_source_combo = QComboBox()
        self.tile_source_combo.addItem("高德地图", "amap")
        self.tile_source_combo.addItem("高德卫星", "amap_satellite")
        self.tile_source_combo.addItem("OpenStreetMap", "osm")
        self.tile_source_combo.addItem("CartoDB", "cartodb")
        self.tile_source_combo.addItem("Stamen Terrain", "stamen")
        self.tile_source_combo.addItem("Stamen Toner", "stamen_toner")
        self.tile_source_combo.setToolTip("选择地图瓦片源")
        self.tile_source_combo.setFixedWidth(130)
        self.tile_source_combo.currentIndexChanged.connect(self.on_tile_source_changed)
        compact_toolbar_layout.addWidget(self.tile_source_combo)

        # 分隔线
        sep = QLabel("|")
        sep.setStyleSheet("color: #ccc;")
        compact_toolbar_layout.addWidget(sep)

        # 代理状态（紧凑显示）
        self.proxy_status_label = QLabel()
        self.proxy_status_label.setFixedHeight(20)
        self.update_proxy_status_display()
        compact_toolbar_layout.addWidget(self.proxy_status_label)

        compact_toolbar_layout.addStretch()

        # 当前瓦片源信息（右侧显示）
        self.tile_info_label = QLabel()
        self.tile_info_label.setStyleSheet("color: #888; font-size: 10px; padding: 0 4px;")
        self.update_tile_info_display()
        compact_toolbar_layout.addWidget(self.tile_info_label)

        map_layout.addWidget(compact_toolbar)


        # 创建 WebEngine 视图
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
            
            # ========== 关键修复：设置 WebEngine 代理 ==========
            self.setup_webengine_proxy()
        
            self.map_view = QWebEngineView()
            self.has_webengine = True
        except ImportError:
            self.map_view = QTextEdit()
            self.map_view.setReadOnly(True)
            self.has_webengine = False
            if DEBUG_MODE:
                print("[地图] PySide6-WebEngine 未安装，将使用文本模式显示地图信息")

        # 直接添加地图视图，不添加任何工具栏（工具栏已在HTML内部）
        map_layout.addWidget(self.map_view)

        self.detail_tab_widget.addTab(map_widget, "🗺️ 地图轨迹")
    
        # ========== 标签页4：站点时间轴 ==========
        site_timeline_widget = QWidget()
        site_timeline_layout = QVBoxLayout(site_timeline_widget)
        
        # 分割为上下两部分：站点时间轴 + 预估信息
        splitter = QSplitter(Qt.Vertical)
        
        # 站点时间轴表格
        self.site_table = QTableWidget()
        self.site_table.setColumnCount(5)
        self.site_table.setHorizontalHeaderLabels(["站点名称", "到达时间", "离开时间", "停留时长", "状态"])
        self.site_table.horizontalHeader().setStretchLastSection(True)
        self.site_table.setAlternatingRowColors(True)
        self.site_table.setEditTriggers(QTableWidget.NoEditTriggers)
        splitter.addWidget(self.site_table)
        
        # 预估信息区域
        estimate_widget = QWidget()
        estimate_layout = QVBoxLayout(estimate_widget)
        
        estimate_title = QLabel("🎯 后续站点预估（基于历史数据）")
        estimate_title.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        estimate_layout.addWidget(estimate_title)
        
        self.estimate_text = QTextEdit()
        self.estimate_text.setReadOnly(True)
        self.estimate_text.setMaximumHeight(150)
        estimate_layout.addWidget(self.estimate_text)
        
        splitter.addWidget(estimate_widget)
        splitter.setSizes([400, 150])
        
        site_timeline_layout.addWidget(splitter)
        self.detail_tab_widget.addTab(site_timeline_widget, "📍 站点时间轴")
        
        # ========== 标签页5：详细分析 ==========
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setFont(QFont("Consolas", 10))
        analysis_layout.addWidget(self.analysis_text)
        self.detail_tab_widget.addTab(analysis_widget, "📊 详细分析")
        
        layout.addWidget(self.detail_tab_widget)
        
        # 底部按钮
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

    def update_tile_info_display(self):
        """更新瓦片源信息显示"""
        tile_source = self.tile_source_combo.currentData()
        tile_names = {
            'osm': '🌍 OSM',
            'cartodb': '🗺️ CartoDB',
            'stamen': '🎨 Stamen',
            'stamen_toner': '⚫ Stamen Toner',
            'amap': '🇨🇳 高德',
            'amap_satellite': '🛰️ 高德卫星'
        }
        self.tile_info_label.setText(tile_names.get(tile_source, ''))


    def update_proxy_status_display(self):
        """更新代理状态显示（紧凑版）- 根据当前瓦片源动态显示"""
        if self.parent_gui and hasattr(self.parent_gui, 'proxy_settings'):
            proxy_settings = self.parent_gui.proxy_settings
            proxy_enabled = proxy_settings.get('enabled', False)
            
            # 获取当前瓦片源
            tile_source = self.tile_source_combo.currentData() if hasattr(self, 'tile_source_combo') else 'cartodb'
            
            # 高德地图源
            amap_sources = ['amap', 'amap_satellite']
            
            if tile_source in amap_sources:
                self.proxy_status_label.setText("🇨🇳 高德直连")
                self.proxy_status_label.setStyleSheet("font-size: 10px; padding: 2px 6px; border-radius: 10px; background-color: #E8F5E9; color: #2E7D32;")
            elif tile_source == 'osm':
                if proxy_enabled:
                    self.proxy_status_label.setText("🔌 OSM(代理)")
                    self.proxy_status_label.setStyleSheet("font-size: 10px; padding: 2px 6px; border-radius: 10px; background-color: #E8F5E9; color: #2E7D32;")
                else:
                    self.proxy_status_label.setText("⚠️ OSM需代理")
                    self.proxy_status_label.setStyleSheet("font-size: 10px; padding: 2px 6px; border-radius: 10px; background-color: #FFEBEE; color: #C62828;")
            else:
                if proxy_enabled:
                    self.proxy_status_label.setText("🔌 代理已启用")
                    self.proxy_status_label.setStyleSheet("font-size: 10px; padding: 2px 6px; border-radius: 10px; background-color: #E8F5E9; color: #2E7D32;")
                else:
                    self.proxy_status_label.setText("🌐 直连")
                    self.proxy_status_label.setStyleSheet("font-size: 10px; padding: 2px 6px; border-radius: 10px; background-color: #FFF3E0; color: #E65100;")

    def on_tile_source_changed(self, index: int):
        """瓦片源改变时重新加载地图"""
        self.update_tile_info_display()
        self.load_map()


    def get_tile_config(self, tile_source: str) -> Tuple[str, str, str, str]:
        """
        获取瓦片源配置
        返回: (url, attribution, subdomains, badge_text)
        """
        configs = {
            # OpenStreetMap 官方瓦片（需要 Referer）
            'osm': (
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                'abc',
                '🌍 OpenStreetMap'
            ),
            # CartoDB 瓦片（OpenStreetMap 数据，无需 Referer）
            'cartodb': (
                "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
                'abcd',
                '🗺️ CartoDB'
            ),
            # Stamen Terrain 地形图
            'stamen': (
                "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
                'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> | Data by &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
                'abcd',
                '🎨 Stamen Terrain'
            ),
            # Stamen Toner 黑白图
            'stamen_toner': (
                "https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
                'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> | Data by &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
                'abcd',
                '🎨 Stamen Toner'
            ),
            # 高德地图（国内）
            'amap': (
                "https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}",
                '&copy; <a href="https://www.amap.com/">高德地图</a>',
                '1234',
                '🇨🇳 高德地图'
            ),
            # 高德卫星图
            'amap_satellite': (
                "https://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
                '&copy; <a href="https://www.amap.com/">高德地图</a>',
                '1234',
                '🛰️ 高德卫星图'
            ),
        }
        
        return configs.get(tile_source, configs['cartodb'])

    def setup_webengine_proxy(self):
        """设置 WebEngine 的代理配置"""
        try:
            from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
            
            # 获取代理设置
            use_proxy = False
            proxy_host = None
            proxy_port = None
            proxy_username = None
            proxy_password = None
            
            if self.parent_gui and hasattr(self.parent_gui, 'proxy_settings'):
                proxy_settings = self.parent_gui.proxy_settings
                use_proxy = proxy_settings.get('enabled', False) and proxy_settings.get('for_map', True)
                
                if use_proxy:
                    proxy_host = proxy_settings.get('host', '')
                    proxy_port = proxy_settings.get('port', 0)
                    proxy_username = proxy_settings.get('username', '')
                    proxy_password = proxy_settings.get('password', '')
            
            if use_proxy and proxy_host and proxy_port:
                # 方法1：通过环境变量设置代理（简单有效）
                import os
                proxy_url = f"http://{proxy_host}:{proxy_port}"
                os.environ['QT_WEBENGINE_DISABLE_SANDBOX'] = '1'
                
                # 设置 HTTP/HTTPS 代理环境变量
                os.environ['http_proxy'] = proxy_url
                os.environ['https_proxy'] = proxy_url
                
                # 如果有用户名密码，需要特殊处理
                if proxy_username and proxy_password:
                    proxy_auth_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                    os.environ['http_proxy'] = proxy_auth_url
                    os.environ['https_proxy'] = proxy_auth_url
                
                # 方法2：通过 QWebEngineProfile 设置代理（更精确）
                profile = QWebEngineProfile.defaultProfile()
                
                # 设置代理
                from PySide6.QtNetwork import QNetworkProxy
                proxy = QNetworkProxy()
                proxy.setType(QNetworkProxy.HttpProxy)
                proxy.setHostName(proxy_host)
                proxy.setPort(proxy_port)
                if proxy_username and proxy_password:
                    proxy.setUser(proxy_username)
                    proxy.setPassword(proxy_password)
                QNetworkProxy.setApplicationProxy(proxy)
                
                # 设置 WebEngine 设置
                settings = profile.settings()
                settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
                settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
                settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
                
                if DEBUG_MODE:
                    print(f"[WebEngine代理] 已设置代理: {proxy_host}:{proxy_port}")
            else:
                if DEBUG_MODE:
                    print("[WebEngine代理] 未启用代理，使用直连")
        
        except Exception as e:
            if DEBUG_MODE:
                print(f"[WebEngine代理设置失败] {e}")

    def refresh_data(self):
        """刷新数据 - 主动查询API"""
        if not self.parent_gui:
            return
            
        tracking_num = self.express_data.get('tracking_number', '') if self.express_data else self.tracking_num
        company_code = self.express_data.get('company_code', '') if self.express_data else ''
        
        if not tracking_num:
            self.parent_gui.status_bar.showMessage("⚠️ 无法获取快递单号", 3000)
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
                    self.parent_gui.status_bar.showMessage("⚠️ 所有账号今日额度都已用完，请明天再试", 3000)
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
            self.parent_gui.status_bar.showMessage("✅ 快递信息已更新", 3000)
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
        
        # 清空并更新基本信息布局
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
        
        # 备注显示
        remark = self.express_data.get('remark', '')
        if remark:
            self.remark_label.setText(remark)
            self.remark_label.setStyleSheet("")
        else:
            self.remark_label.setText("无备注")
            self.remark_label.setStyleSheet("color: #999; font-style: italic;")
        
        # 物流轨迹显示
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
    
        # ========== 加载地图 ==========
        self.load_map()
        
        # 更新站点时间轴
        self.update_site_timeline(full_data)
        
        # 更新节点时间分析
        if self.node_analyzer and full_data:
            try:
                analysis_text = self.node_analyzer.get_detailed_analysis_text(full_data)
                self.analysis_text.setText(analysis_text)
            except Exception as e:
                self.analysis_text.setText(f"分析失败: {e}")
        elif self.node_analyzer and result_data:
            try:
                full_data = json.loads(result_data)
                analysis_text = self.node_analyzer.get_detailed_analysis_text(full_data)
                self.analysis_text.setText(analysis_text)
            except Exception as e:
                self.analysis_text.setText(f"分析失败: {e}")
        else:
            self.analysis_text.setText("暂无足够数据进行分析")
    
    def update_site_timeline(self, full_data: dict):
        """更新站点时间轴"""
        self.site_table.setRowCount(0)
        self.estimate_text.clear()
        
        if not full_data or not self.node_analyzer:
            return
        
        try:
            # 获取站点时间轴分析
            site_analysis = self.node_analyzer.get_site_timeline_analysis(full_data)
            
            if 'error' in site_analysis:
                return
            
            site_timeline = site_analysis.get('site_timeline', [])
            courier_info = site_analysis.get('courier_info', {})
            
            self.site_table.setRowCount(len(site_timeline))
            
            for row, site in enumerate(site_timeline):
                site_name = site.get('site', '未知站点')
                arr_time = site.get('arrive_time', '')
                dep_time = site.get('depart_time', '')
                duration = f"{site.get('duration_hours', 0):.1f} 小时"
                status = "📍 当前位置" if site.get('is_current') else ""
                
                self.site_table.setItem(row, 0, QTableWidgetItem(site_name))
                self.site_table.setItem(row, 1, QTableWidgetItem(arr_time))
                self.site_table.setItem(row, 2, QTableWidgetItem(dep_time or '--'))
                self.site_table.setItem(row, 3, QTableWidgetItem(duration))
                
                status_item = QTableWidgetItem(status)
                if site.get('is_current'):
                    status_item.setForeground(QColor(0, 150, 0))
                    status_item.setFont(QFont("", -1, QFont.Bold))
                self.site_table.setItem(row, 4, status_item)
            
            self.site_table.resizeColumnsToContents()
            
            # 显示揽收员信息
            if courier_info and courier_info.get('name'):
                info_text = f"📮 揽收员: {courier_info['name']}"
                if courier_info.get('phone'):
                    info_text += f" (电话: {courier_info['phone']})"
                self.estimate_text.append(info_text)
                self.estimate_text.append("")
            
            # 获取并显示后续站点预估
            next_estimates = self.node_analyzer.estimate_next_stations(full_data)
            
            if next_estimates:
                self.estimate_text.append("🎯 基于历史数据的后续站点预估:")
                for est in next_estimates:
                    confidence_icon = "🟢" if est['confidence_level'] == '高' else ("🟡" if est['confidence_level'] == '中' else "🔴")
                    self.estimate_text.append(f"  {confidence_icon} {est['description']} (置信度: {est['confidence_level']}, 样本: {est['confidence']})")
            else:
                self.estimate_text.append("暂无后续站点预估数据")
                
        except Exception as e:
            if DEBUG_MODE:
                print(f"更新站点时间轴失败: {e}")

    # ==================== 地图相关方法 ====================
    
    def extract_city_from_site(self, site_name: str) -> str:
        """从站点名称提取城市"""
        if not site_name:
            return ""
        
        for city, patterns in self.SITE_CITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in site_name:
                    return city
        return ""

    def get_city_coordinates(self, city_name: str) -> tuple:
        """获取城市坐标"""
        if not city_name:
            return None, None
        
        # 清理城市名
        city_name = city_name.replace('市', '').replace('省', '').strip()
        
        # 查找精确匹配
        if city_name in self.CITY_COORDINATES:
            lat, lng = self.CITY_COORDINATES[city_name]
            return lat, lng
        
        # 模糊匹配
        for key, coords in self.CITY_COORDINATES.items():
            if city_name in key or key in city_name:
                return coords[0], coords[1]
        
        return None, None

    def extract_city_from_context(self, context: str) -> str:
        """从上下文提取城市"""
        if not context:
            return ""
        
        for city in self.CITY_COORDINATES.keys():
            if city in context:
                return city
        
        # 尝试匹配省+市格式
        pattern = r'([^\s]+?[省市])?([^\s]+?[市])'
        match = re.search(pattern, context)
        if match:
            city_part = match.group(2) or match.group(1)
            if city_part:
                city = city_part.replace('市', '').replace('省', '')
                return city
        
        return ""

    def extract_site_from_context(self, context: str) -> str:
        """从上下文提取站点名"""
        if not context:
            return ""
        
        # 提取【】内的内容
        bracket_match = re.search(r'【([^】]+)】', context)
        if bracket_match:
            return bracket_match.group(1)
        
        # 提取常见站点后缀
        pattern = r'([^\s，。；]*?(?:公司|网点|分部|中心|仓|部|站|转运中心|分拨中心|处理中心))'
        match = re.search(pattern, context)
        if match:
            return match.group(1)
        
        return ""

    def extract_track_points(self, full_data: dict) -> List[Dict]:
        """从物流数据中提取轨迹点（包含坐标信息）"""
        track_points = []
        
        if not full_data:
            return track_points
        
        track_list = full_data.get('data', [])
        if not track_list:
            return track_points
        
        # 使用节点分析器提取节点
        if self.node_analyzer:
            nodes = self.node_analyzer.extract_nodes_from_track(track_list)
        else:
            # 如果没有节点分析器，手动解析
            nodes = []
            for track in track_list:
                context = track.get('context', '')
                time_str = track.get('time', '')
                if time_str:
                    nodes.append({
                        'context': context,
                        'time_str': time_str,
                        'city': self.extract_city_from_context(context),
                        'site_name': self.extract_site_from_context(context),
                        'action_type': 'other',
                        'node_type': 'unknown',
                    })
        
        # 为每个节点添加坐标
        for i, node in enumerate(nodes):
            city = node.get('city', '')
            site_name = node.get('site_name', '')
            
            # 尝试从站点名提取城市
            if not city and site_name:
                city = self.extract_city_from_site(site_name)
            
            lat, lng = None, None
            if city:
                lat, lng = self.get_city_coordinates(city)
            
            # 确定节点类型
            node_type = 'normal'
            action_type = node.get('action_type', '')
            if action_type == 'pickup':
                node_type = 'pickup'
            elif node.get('node_type') == 'transit_center':
                node_type = 'transit_center'
            
            # 最后一个节点标记为当前位置
            if i == len(nodes) - 1:
                node_type = 'current'
            
            track_points.append({
                'lat': lat,
                'lng': lng,
                'city': city,
                'site_name': site_name,
                'time_str': node.get('time_str', ''),
                'context': node.get('context', '')[:100],
                'type': node_type,
                'action_type': action_type,
            })
        
        return track_points

    def load_map(self):
        """加载地图"""
        if not self.express_data:
            return
        
        result_data = self.express_data.get('result_data', '')
        if not result_data:
            error_msg = "<html><body style='font-family: Microsoft YaHei; padding: 20px; text-align: center;'><h3>暂无物流数据</h3><p>无法显示地图轨迹</p></body></html>"
            if self.has_webengine:
                self.map_view.setHtml(error_msg)
            else:
                self.map_view.setText("暂无物流数据，无法显示地图轨迹")
            return
        
        try:
            full_data = json.loads(result_data)
            track_points = self.extract_track_points(full_data)
            
            # 统计有效点
            valid_count = sum(1 for p in track_points if p['lat'] and p['lng'])
            # 在状态栏显示统计信息
            if self.parent_gui:
                self.parent_gui.status_bar.showMessage(
                    f"🗺️ 地图轨迹: 共 {len(track_points)} 个节点，{valid_count} 个有效位置点", 
                    3000
                )
            
            if self.has_webengine:
                # 生成并显示地图
                html_content = self.get_map_html(track_points)
                self.map_view.setHtml(html_content)
            else:
                # 文本模式显示轨迹信息
                text_display = self.get_map_text_display(track_points)
                self.map_view.setText(text_display)
            
        except Exception as e:
            error_msg = f"""
            <html>
            <body style="font-family: Microsoft YaHei; padding: 20px; text-align: center;">
                <h3>地图加载失败</h3>
                <p style="color: #F44336;">{str(e)}</p>
            </body>
            </html>
            """
            if self.has_webengine:
                self.map_view.setHtml(error_msg)
            else:
                self.map_view.setText(f"地图加载失败：{str(e)}")

    def get_map_html(self, track_points: List[Dict]) -> str:
        """生成地图HTML - 高德直连，OSM等走代理"""
        import json
        
        # 处理轨迹点
        points_json = json.dumps(track_points, ensure_ascii=False)
        
        # 获取当前选择的瓦片源
        tile_source = self.tile_source_combo.currentData()
        if not tile_source:
            tile_source = 'cartodb'  # 默认使用 CartoDB
        
        # 获取瓦片配置
        tile_url, tile_attribution, tile_subdomains, map_badge = self.get_tile_config(tile_source)
        
        # ========== 核心逻辑：根据瓦片源类型决定是否使用代理 ==========
        # 高德地图相关瓦片源（直通，不需要代理）
        amap_sources = ['amap', 'amap_satellite']
        # OSM 相关瓦片源（需要代理）
        need_proxy_sources = ['osm']
        
        use_proxy = False
        proxy_host = None
        proxy_port = None
        proxy_username = None
        proxy_password = None
        
        # 检查代理设置
        if self.parent_gui and hasattr(self.parent_gui, 'proxy_settings'):
            proxy_settings = self.parent_gui.proxy_settings
            proxy_enabled = proxy_settings.get('enabled', False)
            
            if proxy_enabled:
                # 对于高德地图，强制不使用代理（直连更快更稳定）
                if tile_source in amap_sources:
                    use_proxy = False
                # 对于 OSM，必须使用代理
                elif tile_source in need_proxy_sources:
                    use_proxy = True
                    proxy_host = proxy_settings.get('host', '')
                    proxy_port = proxy_settings.get('port', 0)
                    proxy_username = proxy_settings.get('username', '')
                    proxy_password = proxy_settings.get('password', '')
                else:
                    # CartoDB、Stamen 等：优先尝试直连，失败时可通过用户设置决定
                    use_proxy = proxy_settings.get('for_map', True)
                    proxy_host = proxy_settings.get('host', '')
                    proxy_port = proxy_settings.get('port', 0)
                    proxy_username = proxy_settings.get('username', '')
                    proxy_password = proxy_settings.get('password', '')
        
        # 根据是否需要代理，选择最终的瓦片 URL
        final_tile_url = tile_url
        final_tile_attribution = tile_attribution
        final_tile_subdomains = tile_subdomains
        final_map_badge = map_badge
        
        if use_proxy and tile_source in need_proxy_sources:
            # OSM 需要代理，使用 HTTPS 协议
            final_tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            final_tile_attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            final_tile_subdomains = 'abc'
            final_map_badge = '🌍 OpenStreetMap (代理)'
        elif tile_source in amap_sources:
            # 高德地图：直连
            final_map_badge = f'🇨🇳 {map_badge} (直连)'
        elif use_proxy:
            # 其他瓦片源使用代理
            final_map_badge = f'{map_badge} (代理)'
        else:
            final_map_badge = f'{map_badge} (直连)'
        
        # 代理提示（仅用于显示）
        proxy_hint = ""
        if tile_source in need_proxy_sources and not use_proxy:
            proxy_hint = '<span style="color: #F44336; font-size: 10px; margin-left: 8px;">⚠️ OSM需要代理才能使用</span>'
        elif tile_source in amap_sources:
            proxy_hint = '<span style="color: #4CAF50; font-size: 10px; margin-left: 8px;">✅ 国内直连</span>'
        elif use_proxy:
            proxy_hint = '<span style="color: #4CAF50; font-size: 10px; margin-left: 8px;">✅ 代理已启用</span>'
        
        return f'''<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <title>物流轨迹地图</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body, html {{
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            
            #map {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
            }}
            
            /* 右上角紧凑工具栏 */
            .map-toolbar {{
                position: absolute;
                top: 12px;
                right: 12px;
                z-index: 1000;
                display: flex;
                gap: 8px;
                pointer-events: none;
            }}
            
            .toolbar-btn {{
                pointer-events: auto;
                background: rgba(255, 255, 255, 0.92);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 20px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 500;
                color: #333;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 4px;
                border: none;
                outline: none;
                line-height: 1;
            }}
            
            .toolbar-btn:hover {{
                background: rgba(255, 255, 255, 0.98);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
            }}
            
            .toolbar-btn:active {{
                transform: translateY(0);
            }}
            
            .toolbar-btn.zoom-fit {{
                background: rgba(33, 150, 243, 0.9);
                color: white;
            }}
            
            .toolbar-btn.zoom-fit:hover {{
                background: #1976D2;
            }}
            
            .toolbar-btn.zoom-in {{
                background: rgba(76, 175, 80, 0.9);
                color: white;
            }}
            
            .toolbar-btn.zoom-out {{
                background: rgba(76, 175, 80, 0.9);
                color: white;
            }}
            
            /* 瓦片源信息面板 */
            .tile-info {{
                position: absolute;
                bottom: 12px;
                left: 12px;
                z-index: 1000;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(8px);
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 10px;
                color: #ccc;
                pointer-events: none;
                font-family: monospace;
            }}
            
            /* 左上角信息面板 */
            .info-panel {{
                position: absolute;
                top: 12px;
                left: 12px;
                z-index: 1000;
                background: rgba(255, 255, 255, 0.92);
                backdrop-filter: blur(8px);
                padding: 8px 16px;
                border-radius: 24px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.5);
                font-size: 12px;
                color: #333;
                pointer-events: none;
            }}
            
            .route-stats {{
                display: flex;
                align-items: center;
                gap: 16px;
                flex-wrap: wrap;
            }}
            
            .stat-item {{
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            
            .stat-icon {{
                font-size: 14px;
            }}
            
            .stat-value {{
                font-weight: 600;
                color: #2196F3;
            }}
            
            .map-badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 16px;
                font-size: 10px;
                font-weight: 500;
                margin-left: 8px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
        
            .map-badge.osm {{
                background: linear-gradient(135deg, #4CAF50, #2E7D32);
            }}
            
            /* 右下角图例 */
            .legend {{
                position: absolute;
                bottom: 24px;
                right: 12px;
                z-index: 1000;
                background: rgba(255, 255, 255, 0.92);
                backdrop-filter: blur(8px);
                padding: 12px 16px;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.5);
                font-size: 11px;
                min-width: 150px;
                pointer-events: none;
            }}
            
            .legend-title {{
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 6px 0;
                gap: 8px;
            }}
            
            .legend-dot {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 1px 4px rgba(0,0,0,0.15);
                flex-shrink: 0;
            }}
            
            .legend-line {{
                width: 20px;
                height: 2px;
                border-radius: 2px;
                flex-shrink: 0;
            }}
            
            .legend-line.dashed {{
                background: repeating-linear-gradient(90deg, #9E9E9E 0px, #9E9E9E 3px, transparent 3px, transparent 6px);
            }}
            
            .legend-text {{
                color: #555;
            }}
            
            /* 缩放控件样式优化 */
            .leaflet-control-zoom {{
                border: none !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
                border-radius: 8px !important;
                overflow: hidden;
                margin: 12px !important;
            }}
            
            .leaflet-control-zoom a {{
                background: rgba(255, 255, 255, 0.92) !important;
                backdrop-filter: blur(8px);
                color: #333 !important;
                border: none !important;
                width: 32px !important;
                height: 32px !important;
                line-height: 32px !important;
                font-size: 16px !important;
            }}
            
            .leaflet-control-zoom a:hover {{
                background: rgba(255, 255, 255, 0.98) !important;
            }}
            
            /* 弹出框样式 */
            .leaflet-popup-content-wrapper {{
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
                padding: 4px;
            }}
            
            .leaflet-popup-content {{
                font-size: 12px;
                max-width: 300px;
                margin: 10px 14px;
            }}
            
            .popup-title {{
                font-weight: 600;
                color: #333;
                margin-bottom: 4px;
                font-size: 13px;
            }}
            
            .popup-time {{
                color: #999;
                font-size: 10px;
                margin-bottom: 6px;
            }}
            
            .popup-context {{
                color: #555;
                line-height: 1.5;
                font-size: 11px;
            }}
            
            /* 无数据提示 */
            .no-data-message {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 1000;
                background: rgba(255, 255, 255, 0.95);
                padding: 20px 28px;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            
            .no-data-message .icon {{
                font-size: 40px;
                margin-bottom: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        
        <!-- 左上角信息 -->
        <div class="info-panel">
            <div class="route-stats">
                <span class="stat-item">
                    <span class="stat-icon">📍</span>
                    <span>节点: <span class="stat-value" id="node-count">0</span></span>
                </span>
                <span class="stat-item">
                    <span class="stat-icon">📏</span>
                    <span>有效点: <span class="stat-value" id="valid-count">0</span></span>
                </span>
                <span class="stat-item">
                    <span class="stat-icon">🛣️</span>
                    <span>总长 <span class="stat-value" id="total-distance">0</span> km</span>
                </span>
                {final_map_badge}{proxy_hint}
            </div>
        </div>
        
        <!-- 右上角工具栏 -->
        <div class="map-toolbar">
            <button class="toolbar-btn zoom-fit" onclick="fitMapToBounds()">📍 自适应缩放</button>
            <button class="toolbar-btn zoom-in" onclick="zoomIn()">🔍 +</button>
            <button class="toolbar-btn zoom-out" onclick="zoomOut()">🔍 -</button>
        </div>
        
        <div class="tile-info" id="tile-info">📡 当前瓦片源: {final_map_badge}</div>

        <script>
            const trackPoints = {points_json};
            
            let map;
            let markers = [];
            let lines = [];
            let bounds = null;
            let validPoints = 0;
            
            // 瓦片配置
            const tileUrl = '{final_tile_url}';
            const tileAttribution = '{final_tile_attribution}';
            const tileSubdomains = '{final_tile_subdomains}';
            
            function initMap() {{
                map = L.map('map', {{
                    zoomControl: false,
                    fadeAnimation: true,
                    attributionControl: true
                }});
                
                // 添加自定义缩放控件
                L.control.zoom({{
                    position: 'bottomright'
                }}).addTo(map);
                
                // 添加瓦片图层
                L.tileLayer(tileUrl, {{
                    attribution: tileAttribution,
                    maxZoom: 19,
                    subdomains: tileSubdomains
                }}).addTo(map);
                
                const icons = {{
                    start: L.divIcon({{
                        html: '<div style="background: linear-gradient(135deg, #4CAF50, #2E7D32); width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(76, 175, 80, 0.4);"></div>',
                        iconSize: [14, 14],
                        iconAnchor: [7, 7]
                    }}),
                    end: L.divIcon({{
                        html: '<div style="background: linear-gradient(135deg, #F44336, #C62828); width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(244, 67, 54, 0.4);"></div>',
                        iconSize: [14, 14],
                        iconAnchor: [7, 7]
                    }}),
                    normal: L.divIcon({{
                        html: '<div style="background: linear-gradient(135deg, #2196F3, #1565C0); width: 10px; height: 10px; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 4px rgba(33, 150, 243, 0.4);"></div>',
                        iconSize: [10, 10],
                        iconAnchor: [5, 5]
                    }}),
                    transit: L.divIcon({{
                        html: '<div style="background: linear-gradient(135deg, #FF9800, #E65100); width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 4px rgba(255, 152, 0, 0.4);"></div>',
                        iconSize: [12, 12],
                        iconAnchor: [6, 6]
                    }}),
                    pickup: L.divIcon({{
                        html: '<div style="background: linear-gradient(135deg, #9C27B0, #6A1B9A); width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 4px rgba(156, 39, 176, 0.4);"></div>',
                        iconSize: [12, 12],
                        iconAnchor: [6, 6]
                    }})
                }};
                
                let boundsTemp = L.latLngBounds([]);
                let totalDistance = 0;
                const totalNodes = trackPoints.length;
                validPoints = 0;
                
                // 先收集所有有效坐标
                const validLatLngs = [];
                
                for (let i = 0; i < trackPoints.length; i++) {{
                    const point = trackPoints[i];
                    if (point.lat && point.lng) {{
                        validPoints++;
                        const latLng = L.latLng(point.lat, point.lng);
                        validLatLngs.push(latLng);
                        boundsTemp.extend(latLng);
                    }}
                }}
                
                // 更新显示统计信息
                document.getElementById('node-count').textContent = totalNodes;
                document.getElementById('valid-count').textContent = validPoints;
                
                if (validPoints > 0) {{
                    // 计算总距离
                    for (let i = 1; i < validLatLngs.length; i++) {{
                        totalDistance += validLatLngs[i-1].distanceTo(validLatLngs[i]);
                    }}
                    document.getElementById('total-distance').textContent = (totalDistance / 1000).toFixed(1);
                    
                    // 添加标记点
                    for (let i = 0; i < trackPoints.length; i++) {{
                        const point = trackPoints[i];
                        if (!point.lat || !point.lng) continue;
                        
                        const latLng = L.latLng(point.lat, point.lng);
                        
                        let icon = icons.normal;
                        if (i === 0) icon = icons.start;
                        else if (i === trackPoints.length - 1) icon = icons.end;
                        else if (point.type === 'transit_center') icon = icons.transit;
                        else if (point.type === 'pickup') icon = icons.pickup;
                        
                        const marker = L.marker(latLng, {{ icon: icon }})
                            .bindPopup(`
                                <div class="popup-title">${{point.site_name || point.city || '未知地点'}}</div>
                                <div class="popup-time">🕐 ${{point.time_str || ''}}</div>
                                <div class="popup-context">${{point.context || ''}}</div>
                            `)
                            .addTo(map);
                        
                        markers.push(marker);
                    }}
                    
                    // 绘制主路线（连接所有有效点）
                    if (validLatLngs.length >= 2) {{
                        // 主路线 - 粗线
                        const mainPolyline = L.polyline(validLatLngs, {{
                            color: '#2196F3',
                            weight: 3,
                            opacity: 0.7,
                            smoothFactor: 1
                        }}).addTo(map);
                        lines.push(mainPolyline);
                        
                        // 分段绘制（区分不同颜色）
                        for (let i = 1; i < trackPoints.length; i++) {{
                            const p1 = trackPoints[i-1];
                            const p2 = trackPoints[i];
                            
                            if (p1.lat && p1.lng && p2.lat && p2.lng) {{
                                let color = '#2196F3';
                                let dashArray = null;
                                let weight = 2;
                                
                                if (p1.type === 'transit_center' || p2.type === 'transit_center') {{
                                    color = '#FF9800';
                                }}
                                
                                // 同一站点内移动，用虚线表示
                                if (p1.site_name && p2.site_name && p1.site_name === p2.site_name) {{
                                    color = '#9E9E9E';
                                    dashArray = '5, 5';
                                    weight = 2;
                                }}
                                
                                const segmentLine = L.polyline([[p1.lat, p1.lng], [p2.lat, p2.lng]], {{
                                    color: color,
                                    weight: weight,
                                    opacity: 0.5,
                                    dashArray: dashArray
                                }}).addTo(map);
                                
                                lines.push(segmentLine);
                            }}
                        }}
                    }}
                    
                    // 自动缩放以适应所有轨迹点
                    if (validPoints === 1) {{
                        map.setView(boundsTemp.getCenter(), 12);
                    }} else if (validPoints >= 2) {{
                        setTimeout(function() {{
                            map.fitBounds(boundsTemp, {{ 
                                padding: [50, 50],
                                maxZoom: 15,
                                animate: true
                            }});
                        }}, 100);
                        
                        bounds = boundsTemp;
                    }}
                }} else {{
                    showNoDataMessage();
                    map.setView([35.0, 105.0], 4);
                    document.getElementById('node-count').textContent = '0';
                    document.getElementById('valid-count').textContent = '0';
                    document.getElementById('total-distance').textContent = '0';
                }}
                
                addLegend();
                L.control.scale({{ imperial: false, metric: true, position: 'bottomleft' }}).addTo(map);
            }}
            
            function showNoDataMessage() {{
                const div = document.createElement('div');
                div.className = 'no-data-message';
                div.innerHTML = '<div class="icon">🗺️</div><div>暂无有效的地理位置信息</div><div style="font-size: 11px; margin-top: 6px; opacity: 0.7;">无法显示地图轨迹</div>';
                document.body.appendChild(div);
            }}
            
            function addLegend() {{
                const div = document.createElement('div');
                div.className = 'legend';
                div.innerHTML = `
                    <div class="legend-title"><span>📌</span> 图例</div>
                    <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #4CAF50, #2E7D32);"></div><span class="legend-text">起点/揽收</span></div>
                    <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #F44336, #C62828);"></div><span class="legend-text">当前位置/终点</span></div>
                    <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #FF9800, #E65100);"></div><span class="legend-text">转运中心</span></div>
                    <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #2196F3, #1565C0);"></div><span class="legend-text">普通节点</span></div>
                    <div class="legend-item"><div class="legend-line" style="background: #2196F3;"></div><span class="legend-text">运输路线</span></div>
                    <div class="legend-item"><div class="legend-line dashed"></div><span class="legend-text">站点停留</span></div>
                `;
                document.body.appendChild(div);
            }}
            
            function fitMapToBounds() {{
                // 手动触发自适应缩放
                if (bounds && validPoints > 1) {{
                    map.fitBounds(bounds, {{ 
                        padding: [50, 50],
                        maxZoom: 15,
                        animate: true
                    }});
                }} else if (validPoints === 1 && bounds) {{
                    map.setView(bounds.getCenter(), 12);
                }} else {{
                    // 重新计算边界
                    const newBounds = L.latLngBounds([]);
                    let hasPoint = false;
                    for (let i = 0; i < trackPoints.length; i++) {{
                        const point = trackPoints[i];
                        if (point.lat && point.lng) {{
                            newBounds.extend([point.lat, point.lng]);
                            hasPoint = true;
                        }}
                    }}
                    if (hasPoint) {{
                        bounds = newBounds;
                        if (validPoints === 1) {{
                            map.setView(bounds.getCenter(), 12);
                        }} else {{
                            map.fitBounds(bounds, {{ padding: [50, 50], maxZoom: 15, animate: true }});
                        }}
                    }}
                }}
            }}
            
            function zoomIn() {{
                map.zoomIn();
            }}
            
            function zoomOut() {{
                map.zoomOut();
            }}
            
            // 监听窗口大小变化，重新调整地图视图
            window.addEventListener('resize', function() {{
                if (map && bounds && validPoints > 1) {{
                    setTimeout(function() {{
                        map.fitBounds(bounds, {{ padding: [50, 50], maxZoom: 15 }});
                    }}, 100);
                }}
            }});
            
            // 页面加载完成后初始化地图
            document.addEventListener('DOMContentLoaded', initMap);
        </script>
    </body>
    </html>'''



    def refresh_map(self):
        """刷新地图"""
        self.load_map()
        if self.parent_gui:
            self.parent_gui.status_bar.showMessage("🔄 地图已刷新", 2000)

    def export_map(self):
        """导出地图为HTML文件"""
        if not self.express_data:
            return
        
        tracking_num = self.express_data.get('tracking_number', 'unknown')
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出地图轨迹", 
            f"express_map_{tracking_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML文件 (*.html)"
        )
        
        if not file_path:
            return
        
        try:
            result_data = self.express_data.get('result_data', '')
            if result_data:
                full_data = json.loads(result_data)
                track_points = self.extract_track_points(full_data)
                
                if self.has_webengine:
                    html_content = self.get_map_html(track_points)
                else:
                    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>物流轨迹</title></head>
<body style="font-family: monospace; padding: 20px;">
<pre>{self.get_map_text_display(track_points)}</pre>
</body></html>"""
                
                # 添加导出信息
                export_header = f"""<!-- 
    快递轨迹地图
    单号: {tracking_num}
    导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    程序: {ProjectInfo.NAME} v{ProjectInfo.VERSION}
-->
"""
                html_content = export_header + html_content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                if self.parent_gui:
                    self.parent_gui.status_bar.showMessage(f"✅ 地图已导出到: {file_path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出地图失败：{str(e)}")

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
        # 强制处理事件，确保 widget 已经完全添加到布局
        QApplication.processEvents()
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
        """更新计数（统计所有条目）"""
        # 改为统计所有条目，而不是只统计可见的
        total_count = len(self.express_items)
        self.count_label.setText(f"({total_count})")


class UserLoginDialogPro(DialogWithStatusBar):
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
        self.setFixedSize(500, 450)
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
        
        # 添加状态栏
        self.setup_status_bar(layout)

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
                    self.show_status(f"✅ {message}", 3000)
                    self.load_users()
                else:
                    self.show_status(f"❌ {message}", 3000)
                    
            QTimer.singleShot(100, add_user_thread)
            
    def edit_user(self):
        """修改用户名"""
        current_item = self.user_list.currentItem()
        if not current_item:
            self.show_status("⚠️ 请先选择要修改的用户", 3000)
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
                    self.show_status(f"✅ {message}", 3000)
                    self.load_users()
                else:
                    self.show_status(f"❌ {message}", 3000)
                    
            QTimer.singleShot(100, edit_user_thread)
            
    def delete_user(self):
        """删除用户"""
        current_item = self.user_list.currentItem()
        if not current_item:
            self.show_status("⚠️ 请先选择要删除的用户", 3000)
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
                    self.show_status(f"✅ {message}", 3000)
                    self.load_users()
                else:
                    self.show_status(f"❌ {message}", 3000)
                    
            QTimer.singleShot(100, delete_user_thread)
            
    def login_selected_user(self):
        """登录选中的用户"""
        current_item = self.user_list.currentItem()
        if not current_item:
            self.show_status("⚠️ 请先选择用户", 3000)
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
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
        
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
                self.parent_gui.status_bar.showMessage("✅ 备份已删除", 3000)
                self.load_backups()
            else:
                self.parent_gui.status_bar.showMessage("❌ 删除备份失败", 5000)
                
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
        
        hint_label = QLabel("按住鼠标左键拖动选择裁剪区域，松开完成选择")
        hint_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(hint_label)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        
        self.scaled_pixmap = self.original_pixmap.scaled(
            600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.scale_factor = self.scaled_pixmap.width() / self.original_pixmap.width()
        
        self.image_label.setPixmap(self.scaled_pixmap)
        
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
        
        self.info_label = QLabel("未选择区域")
        self.info_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.info_label)
        
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
            end_pos = event.pos()
            x = min(self.start_pos.x(), end_pos.x())
            y = min(self.start_pos.y(), end_pos.y())
            w = abs(self.start_pos.x() - end_pos.x())
            h = abs(self.start_pos.y() - end_pos.y())
            
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
        QLabel.paintEvent(self.image_label, event)
        
        if self.selection_rect:
            painter = QPainter(self.image_label)
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))
            painter.drawRect(self.selection_rect)
            
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
            
        scale = 1.0 / self.scale_factor
        orig_x = int(self.selection_rect.x() * scale)
        orig_y = int(self.selection_rect.y() * scale)
        orig_w = int(self.selection_rect.width() * scale)
        orig_h = int(self.selection_rect.height() * scale)
        
        self.cropped_pixmap = self.original_pixmap.copy(orig_x, orig_y, orig_w, orig_h)
        self.accept()
        
    def get_cropped_image(self) -> QPixmap:
        """获取裁剪后的图片"""
        return self.cropped_pixmap


class RebuildDeliveryWorker(QObject):
    """重建时效历史数据的工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, db_manager: DatabaseManagerPro):
        super().__init__()
        self.db_manager = db_manager
        
    def run(self):
        try:
            sql = """
            SELECT id, tracking_number, company_code, company_name, result_data, created_at
            FROM express_summary 
            WHERE is_deleted = 0 
            AND result_data IS NOT NULL 
            AND result_data != ''
            """
            records = self.db_manager.execute_query(sql)
            
            if not records:
                self.finished.emit(True, "没有找到可用的快递数据")
                return
            
            total = len(records)
            self.status.emit(f"正在扫描 {total} 条快递记录...")
            
            self.db_manager.execute_update("DELETE FROM delivery_history")
            
            estimator = DeliveryTimeEstimator(self.db_manager)
            
            success_count = 0
            
            for i, record in enumerate(records):
                try:
                    result_data = record.get('result_data', '')
                    if not result_data:
                        continue
                    
                    data = json.loads(result_data)
                    
                    track_list = data.get('data', [])
                    if len(track_list) < 2:
                        continue
                    
                    state = str(data.get('state', ''))
                    last_context = track_list[-1].get('context', '') if track_list else ''
                    is_signed = (state == '3') or estimator.is_signed(last_context)
                    is_arrived = estimator.is_arrived_at_station(last_context)
                    
                    if not is_signed and not is_arrived:
                        continue
                    
                    estimator.record_delivery(data)
                    success_count += 1
                    
                except:
                    continue
                
                progress_val = int((i + 1) / total * 100)
                self.progress.emit(progress_val)
                self.status.emit(f"已处理 {i+1}/{total} 条记录，成功 {success_count} 条")
            
            verify_sql = "SELECT COUNT(*) as count FROM delivery_history"
            verify_result = self.db_manager.execute_query(verify_sql)
            final_count = verify_result[0]['count'] if verify_result else 0
            
            self.finished.emit(True, f"重建完成！\n扫描 {total} 条记录，成功提取 {success_count} 条时效数据\n最终 delivery_history 表共有 {final_count} 条记录")
            
        except Exception as e:
            self.finished.emit(False, f"重建失败：{str(e)}")


class RebuildNodeWorker(QObject):
    """重建节点运输历史数据的工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, db_manager: DatabaseManagerPro):
        super().__init__()
        self.db_manager = db_manager
        
    def run(self):
        try:
            self.status.emit("正在验证表结构...")
            check_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='node_transit_history'"
            result = self.db_manager.execute_query(check_sql)
            if not result:
                self.status.emit("表不存在，正在创建...")
                analyzer = LogisticsNodeAnalyzer(self.db_manager)
                analyzer.init_node_history_table()
            
            sql = """
            SELECT id, tracking_number, company_code, company_name, result_data, created_at
            FROM express_summary 
            WHERE is_deleted = 0 
            AND result_data IS NOT NULL 
            AND result_data != ''
            """
            records = self.db_manager.execute_query(sql)
            
            if not records:
                self.finished.emit(True, "没有找到可用的快递数据")
                return
            
            total = len(records)
            self.status.emit(f"正在扫描 {total} 条快递记录...")
            
            self.db_manager.execute_update("DELETE FROM node_transit_history")
            
            analyzer = LogisticsNodeAnalyzer(self.db_manager)
            
            success_count = 0
            node_segments_count = 0
            
            for i, record in enumerate(records):
                try:
                    result_data = record.get('result_data', '')
                    if not result_data:
                        continue
                    
                    data = json.loads(result_data)
                    
                    track_list = data.get('data', [])
                    if len(track_list) < 2:
                        continue
                    
                    analyzer.record_node_transit(data)
                    success_count += 1
                    
                    nodes = analyzer.extract_nodes_from_track(track_list)
                    segments = analyzer.calculate_node_transit_times(nodes)
                    node_segments_count += len(segments)
                    
                except:
                    continue
                
                progress_val = int((i + 1) / total * 100)
                self.progress.emit(progress_val)
                self.status.emit(f"已处理 {i+1}/{total} 条记录，成功 {success_count} 条，提取 {node_segments_count} 个节点段")
            
            verify_sql = "SELECT COUNT(*) as count FROM node_transit_history"
            verify_result = self.db_manager.execute_query(verify_sql)
            final_count = verify_result[0]['count'] if verify_result else 0
            
            self.finished.emit(True, f"重建完成！\n扫描 {total} 条记录\n成功处理 {success_count} 条快递\n提取 {node_segments_count} 个节点段\n最终 node_transit_history 表共有 {final_count} 条记录")
            
        except Exception as e:
            self.finished.emit(False, f"重建失败：{str(e)}")


class RebuildAllWorker(QObject):
    """全部重建（时效+节点）的工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, db_manager: DatabaseManagerPro):
        super().__init__()
        self.db_manager = db_manager
        
    def run(self):
        try:
            sql = """
            SELECT id, tracking_number, company_code, company_name, result_data, created_at
            FROM express_summary 
            WHERE is_deleted = 0 
            AND result_data IS NOT NULL 
            AND result_data != ''
            """
            records = self.db_manager.execute_query(sql)
            
            if not records:
                self.finished.emit(True, "没有找到可用的快递数据")
                return
            
            total = len(records)
            self.status.emit(f"正在扫描 {total} 条快递记录...")
            
            self.db_manager.execute_update("DELETE FROM delivery_history")
            self.db_manager.execute_update("DELETE FROM node_transit_history")
            
            estimator = DeliveryTimeEstimator(self.db_manager)
            analyzer = LogisticsNodeAnalyzer(self.db_manager)
            
            delivery_count = 0
            node_count = 0
            
            for i, record in enumerate(records):
                try:
                    result_data = record.get('result_data', '')
                    if not result_data:
                        continue
                    
                    data = json.loads(result_data)
                    track_list = data.get('data', [])
                    
                    if len(track_list) >= 2:
                        estimator.record_delivery(data)
                        delivery_count += 1
                        
                        analyzer.record_node_transit(data)
                        node_count += 1
                        
                except:
                    continue
                
                progress_val = int((i + 1) / total * 100)
                self.progress.emit(progress_val)
                self.status.emit(f"已处理 {i+1}/{total} 条记录 | 时效: {delivery_count} | 节点: {node_count}")
            
            self.finished.emit(True, f"重建完成！\n扫描 {total} 条记录\n时效数据: {delivery_count} 条\n节点数据: {node_count} 条")
            
        except Exception as e:
            self.finished.emit(False, f"重建失败：{str(e)}")


class BatchImportDialog(DialogWithStatusBar): 
    """批量导入快递单号对话框"""
    
    def __init__(self, company_codes: dict, parent=None):
        super().__init__(parent)
        self.company_codes = company_codes
        self.imported_numbers = []
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle("批量导入快递单号")
        self.setMinimumSize(700, 650)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        method_group = QGroupBox("导入方式")
        method_layout = QVBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["从文件导入", "粘贴多行文本", "手动输入（每行一个）"])
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
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
        
        self.text_widget = QWidget()
        self.text_widget.setVisible(False)
        text_layout = QVBoxLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        text_label = QLabel("请输入快递单号（每行一个，或使用分隔符分隔）：")
        text_layout.addWidget(text_label)
        
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
        
        preview_btn = QPushButton("预览解析结果")
        preview_btn.clicked.connect(self.preview_numbers)
        text_layout.addWidget(preview_btn)
        
        layout.addWidget(self.text_widget)
        
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
        
        # 添加状态栏
        self.setup_status_bar(layout)

        self.setLayout(layout)
        
    def on_method_changed(self, index: int):
        """切换导入方式"""
        self.file_widget.setVisible(index == 0)
        self.text_widget.setVisible(index != 0)
        
        if index == 1:
            self.separator_combo.setCurrentText("换行（默认）")
        elif index == 2:
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
                self.show_status("⚠️ 无法识别文件编码，请确保文件为文本格式", 3000)
                return
                
            self.method_combo.setCurrentIndex(1)
            self.text_edit.setText(content)
            
            QTimer.singleShot(200, self.parse_numbers)
            
        except Exception as e:
            self.show_status(f"❌ 读取文件失败：{e}", 5000)
            
    def get_separator(self) -> Optional[str]:
        """获取当前分隔符"""
        index = self.separator_combo.currentIndex()
        separators = {
            0: '\n',
            1: ',',
            2: ' ',
            3: ';',
            4: '\t',
            5: self.custom_separator_edit.text()
        }
        return separators.get(index)
        
    def detect_company_by_number(self, tracking_num: str) -> str:
        """根据单号格式自动识别快递公司"""
        tracking_num = tracking_num.strip().upper()
        
        rules = [
            (lambda n: n.startswith('SF') and len(n) >= 12, 'shunfeng'),
            (lambda n: len(n) == 12 and n.isdigit(), 'shunfeng'),
            (lambda n: n.startswith('YT') and len(n) >= 10, 'yuantong'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '23456', 'yuantong'),
            (lambda n: n.startswith('ZT') and len(n) >= 10, 'zhongtong'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '78', 'zhongtong'),
            (lambda n: n.startswith('YD') and len(n) >= 10, 'yunda'),
            (lambda n: len(n) == 13 and n.isdigit() and n[0] in '145', 'yunda'),
            (lambda n: n.startswith('ST') and len(n) >= 10, 'shentong'),
            (lambda n: len(n) == 12 and n.isdigit() and n[0] in '378', 'shentong'),
            (lambda n: n.startswith('JD'), 'jd'),
            (lambda n: n.startswith('EMS'), 'ems'),
            (lambda n: len(n) == 13 and n.isdigit() and n[:2] in ['98', '99', '10', '11', '12', '13', '14'], 'ems'),
            (lambda n: n.startswith('JT') and len(n) >= 10, 'jtexpress'),
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
        """解析单号"""
        method = self.method_combo.currentIndex()
        
        if method == 0:
            file_path = self.file_path_edit.text().strip()
            if not file_path:
                self.show_status("⚠️ 请先选择文件", 3000)
                return
            if not os.path.exists(file_path):
                self.show_status("⚠️ 请先选择文件", 3000)
                return
            self.load_file_content(file_path)
            return
            
        content = self.text_edit.toPlainText().strip()
        if not content:
            self.show_status("⚠️ 请输入快递单号", 3000)
            return
            
        separator = self.get_separator()
        if not separator:
            self.show_status("⚠️ 请输入自定义分隔符", 3000)
            return
            
        if separator == '\n':
            lines = content.split('\n')
            raw_items = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                raw_items.append(line)
        else:
            raw_items = [n.strip() for n in content.split(separator) if n.strip()]
        
        numbers = []
        for item in raw_items:
            cleaned = re.sub(r'[\s\u4e00-\u9fff]+', '', item)
            if len(cleaned) >= 6:
                numbers.append(cleaned)
            else:
                numbers.append(item.strip())
        
        seen = set()
        unique_numbers = []
        for num in numbers:
            if num not in seen:
                seen.add(num)
                unique_numbers.append(num)
                
        default_company_name = self.company_combo.currentText()
        default_company_code = self.company_codes.get(default_company_name, "")
        auto_detect = self.auto_detect_check.isChecked()
        
        self.preview_table.setRowCount(len(unique_numbers))
        
        self.imported_numbers = []
        valid_count = 0
        duplicate_warning = len(numbers) - len(unique_numbers)
        
        for row, num in enumerate(unique_numbers):
            self.preview_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.preview_table.setItem(row, 1, QTableWidgetItem(num))
            
            company_code = ""
            company_name = "自动识别"
            status = "API自动"
            status_color = QColor(100, 100, 100)
            
            if auto_detect:
                detected_code = self.detect_company_by_number(num)
                if detected_code:
                    company_code = detected_code
                    company_name = self.get_company_name_by_code(detected_code)
                    status = "格式识别"
                    status_color = QColor(0, 150, 0)
                else:
                    company_code = ""
                    company_name = "自动识别"
                    status = "API自动"
                    status_color = QColor(100, 100, 100)
            else:
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

        self.show_status(f"✅ 解析完成：{valid_count} 个有效单号", 2000)
        
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
        self.node_analyzer = None
        self.api_endpoint_manager = None  # 先初始化为 None

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

        self.is_filtered = False  # 是否处于过滤状态
        self.filtered_items = {}  # 保存过滤前的原始条目 {category_key: [items]}

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
        
        # 初始化API接口管理器（在登录成功后）
        self.api_endpoint_manager = ApiEndpointManager(self.current_user_db)
        
        # 应用全局样式
        self.setStyleSheet(MacaronStyle.get_main_style())
    
        # ========== 关键修改：延迟更新接口显示，确保UI完全加载 ==========
        # 等待 100ms 后再次更新，确保 api_endpoint_manager 已完全初始化
        QTimer.singleShot(100, self.update_api_endpoint_display)

        
        # 添加验证码相关属性
        self.pending_verification = None  # 待验证的查询信息
        self.verification_dialog = None    # 验证码对话框
        self.verification_retry_count = 0  # 验证重试次数
    
        self.refreshing_category_key = None  # 正在刷新的分类key
        self.pending_retry_failed_items = []  # 待重试的失败列表

        # 添加代理设置属性
        self.proxy_settings = {
            'enabled': False,
            'type': 'http',
            'host': '127.0.0.1',
            'port': 20808,
            'username': '',
            'password': '',
            'for_map': True,
            'for_api': False
        }
        
        # 加载代理设置
        QTimer.singleShot(200, self.load_proxy_settings)

    def load_proxy_settings(self):
        """加载代理设置"""
        if not self.user_manager.current_user_db:
            return
        
        self.proxy_settings['enabled'] = self.user_manager.get_user_setting("proxy_enabled", "1") == "1"
        self.proxy_settings['type'] = self.user_manager.get_user_setting("proxy_type", "HTTP").lower()
        self.proxy_settings['host'] = self.user_manager.get_user_setting("proxy_host", "127.0.0.1")
        self.proxy_settings['port'] = int(self.user_manager.get_user_setting("proxy_port", "20808"))
        self.proxy_settings['username'] = self.user_manager.get_user_setting("proxy_username", "")
        self.proxy_settings['password'] = self.user_manager.get_user_setting("proxy_password", "")
        self.proxy_settings['for_map'] = self.user_manager.get_user_setting("proxy_for_map", "1") == "1"
        self.proxy_settings['for_api'] = self.user_manager.get_user_setting("proxy_for_api", "0") == "1"

    def update_proxy_settings(self):
        """更新代理设置（供设置对话框调用）"""
        self.load_proxy_settings()
        self.status_bar.showMessage("✅ 代理设置已更新", 2000)

    def get_proxy_dict(self) -> Optional[Dict]:
        """获取代理配置字典"""
        if not self.proxy_settings['enabled']:
            return None
        
        proxy_type = self.proxy_settings['type']
        host = self.proxy_settings['host']
        port = self.proxy_settings['port']
        username = self.proxy_settings['username']
        password = self.proxy_settings['password']
        
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }

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
                    self.node_analyzer = LogisticsNodeAnalyzer(self.current_user_db)
                    self.load_current_api_account()
                    
                    # 初始化API接口管理器
                    self.api_endpoint_manager = ApiEndpointManager(self.current_user_db)
                    
                    # 更新接口显示（如果界面已创建）
                    if hasattr(self, 'api_endpoint_status'):
                        self.update_api_endpoint_display()
                    
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
            
            # ========== 不要调用 load_accounts()，因为它会重置当前账号 ==========
            # 直接获取当前账号（保持之前设置的 current_account）
            account = self.api_account_manager.get_current_account()
            
            if account:
                self.customer = account.get('customer', '')
                self.key = account.get('auth_key', '')
                self.update_api_account_display()
                
                if DEBUG_MODE:
                    print(f"[账号加载] 当前账号: {account.get('account_name', '')} (ID={account.get('id', '')})")
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

        self.dest_address_tab = QWidget()
        self.setup_dest_address_tab()
        self.main_tab_widget.addTab(self.dest_address_tab, "📮 收件地址")

        main_layout.addWidget(self.main_tab_widget)
        
        # ========== 状态栏设置 ==========
        self.status_bar = QStatusBar()
        self.status_bar.setMinimumHeight(30)  # 增加状态栏高度
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # ========== 全局进度条 - 加粗版 ==========
        self.global_progress = QProgressBar()
        self.global_progress.setMinimumHeight(22)  # 最小高度22px
        self.global_progress.setMaximumHeight(26)  # 最大高度26px
        self.global_progress.setMinimumWidth(250)  # 最小宽度
        self.global_progress.setTextVisible(True)  # 显示文字
        self.global_progress.setFormat("%p%")      # 显示百分比
        self.global_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {MacaronColors.BORDER_MEDIUM.name()};
                border-radius: 6px;
                background-color: #E8E8E8;
                text-align: center;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
                font-size: 11px;
                padding: 0px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MacaronColors.GREEN_APPLE.name()},
                    stop:0.4 {MacaronColors.BLUE_SKY.name()},
                    stop:1 {MacaronColors.ORANGE_PEACH.name()});
                border-radius: 4px;
                margin: 2px;
            }}
        """)
        self.status_bar.addPermanentWidget(self.global_progress)
        self.global_progress.setVisible(False)
        
        # 设置全局快捷键
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_global_search)

        # 添加清空搜索的快捷键
        clear_search_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        clear_search_shortcut.activated.connect(self.clear_global_search)

        # 添加 ESC 键清除搜索的快捷键
        esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        esc_shortcut.activated.connect(self.on_escape_clear_search)

        for i in range(1, 6):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda idx=i-1: self.main_tab_widget.setCurrentIndex(idx))

        if not self.load_current_api_account():
            QTimer.singleShot(500, self.check_api_accounts)

        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_selected_content)


    def on_escape_clear_search(self):
        """ESC键清除搜索（仅当搜索框有焦点或处于过滤状态时）"""
        if self.global_search.hasFocus() or self.is_filtered:
            self.clear_global_search()

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
        """创建工具栏 - 添加醒目的进度条"""
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
        self.update_api_account_display()
    
        # ========== 新增：接口类型状态标签 ==========
        self.api_endpoint_status = QLabel()
        self.api_endpoint_status.setStyleSheet("""
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 12px;
            margin: 0 5px;
        """)
        toolbar_layout.addWidget(self.api_endpoint_status)

        # 尝试立即更新接口显示（此时 api_endpoint_manager 可能还未完全初始化）
        # 但这个方法会被调用，不会报错，只是可能显示不准确
        self.update_api_endpoint_display()  # 更新接口状态显示
        
        toolbar_layout.addStretch()

        # ========== 增强的工具栏进度条 ==========
        self.toolbar_progress = QProgressBar()
        self.toolbar_progress.setMaximumWidth(250)
        self.toolbar_progress.setMinimumHeight(20)
        self.toolbar_progress.setVisible(False)
        self.toolbar_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {MacaronColors.BORDER_MEDIUM.name()};
                border-radius: 5px;
                background-color: #F0F0F0;
                text-align: center;
                font-weight: bold;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MacaronColors.GREEN_APPLE.name()},
                    stop:0.5 {MacaronColors.BLUE_SKY.name()},
                    stop:1 {MacaronColors.ORANGE_PEACH.name()});
                border-radius: 3px;
                margin: 1px;
            }}
        """)
        toolbar_layout.addWidget(self.toolbar_progress)
        
        search_label = QLabel("🔎 全局搜索:")
        toolbar_layout.addWidget(search_label)
        
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("输入单号、公司、状态、备注... (实时过滤，ESC清除)")
        self.global_search.setMinimumWidth(280)
        # 实时输入时只做高亮过滤（不弹窗）
        self.global_search.textChanged.connect(self.on_global_search_filter)
        # 按回车时弹出搜索范围选择对话框
        self.global_search.returnPressed.connect(self.on_global_search)
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

    def on_global_search_filter(self):
        """实时过滤 - 只显示符合条件的快递条目"""
        search_text = self.global_search.text().strip()
        
        if not search_text:
            # 清空搜索时，恢复显示所有条目
            self.clear_summary_filter()
            self.status_bar.showMessage("就绪", 2000)
            return
        
        search_lower = search_text.lower()
        match_count = 0
        first_match_item = None
        
        # 如果是第一次过滤，先保存原始状态
        if not self.is_filtered:
            self.save_original_items()
            self.is_filtered = True
        
        # 遍历所有分类
        for category_key, widget in self.category_widgets.items():
            # 获取该分类下的所有条目
            items_to_keep = []
            items_to_hide = []
            
            for item in widget.express_items:
                data = item.express_data
                tracking_num = (data.get('tracking_number') or '').lower()
                company_name = (data.get('company_name') or '').lower()
                status = (data.get('status') or '').lower()
                remark = (data.get('remark') or '').lower()
                latest_track = (data.get('latest_track') or '').lower()
                
                # 检查是否匹配
                is_match = (search_lower in tracking_num or 
                        search_lower in company_name or 
                        search_lower in status or 
                        search_lower in remark or 
                        search_lower in latest_track)
                
                if is_match:
                    match_count += 1
                    items_to_keep.append(item)
                    # 记录第一个匹配的条目
                    if first_match_item is None:
                        first_match_item = (widget, item)
                else:
                    items_to_hide.append(item)
            
            # 隐藏不匹配的条目
            for item in items_to_hide:
                item.setVisible(False)
            
            # 确保匹配的条目可见
            for item in items_to_keep:
                item.setVisible(True)
            
            # 如果分类中有匹配项，自动展开该分类
            if items_to_keep and widget.is_collapsed:
                widget.set_collapsed(False)
            
            # 更新分类计数（只显示可见条目数）
            widget.update_count()
        
        # 更新状态栏提示
        if match_count > 0:
            self.status_bar.showMessage(f"🔍 找到 {match_count} 条匹配结果 (按ESC或清空搜索框恢复)", 0)
            
            # 滚动到第一个匹配的条目
            if first_match_item:
                widget, item = first_match_item
                QTimer.singleShot(100, lambda: self.scroll_to_item(widget, item))
        else:
            self.status_bar.showMessage(f"🔍 未找到匹配结果 (ESC或清空搜索框恢复)", 0)

    def clear_summary_filter(self):
        """清除过滤，恢复显示所有条目"""
        if not self.is_filtered:
            return
        
        for category_key, widget in self.category_widgets.items():
            # 恢复所有条目的可见性
            for item in widget.express_items:
                item.setVisible(True)
            
            # 更新分类计数
            widget.update_count()
        
        self.is_filtered = False
        self.status_bar.showMessage("已恢复显示所有快递", 2000)
        

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
    
        # ========== 直接添加按钮 ==========
        direct_add_btn = QPushButton("⚡ 直接添加")
        direct_add_btn.setToolTip("跳过API查询，直接将单号添加到汇总（状态为待查询）")
        direct_add_btn.clicked.connect(self.direct_add_manual_express)
        direct_add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.ORANGE_PEACH.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.ORANGE_APRICOT.name()};
            }}
        """)
        toolbar.addWidget(direct_add_btn)

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
        
        # 添加批量导出按钮
        batch_export_btn = QPushButton("📋 批量导出单号")
        batch_export_btn.setToolTip("批量导出选中的快递单号")
        batch_export_btn.clicked.connect(self.batch_export_numbers)
        batch_export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.ORANGE_PEACH.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.ORANGE_APRICOT.name()};
            }}
        """)
        toolbar.addWidget(batch_export_btn)
        
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
            ('picked', '📮 已揽收'),
            ('pending', '⏳ 待揽件'),
            ('signed', '✅ 已签收'),
            ('problem', '⚠️ 疑难件'),
            ('returned', '↩️ 退件'),
            ('customs', '🛃 清关中'),
            ('other', '📦 其他')
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


    def direct_add_manual_express(self):
        """直接添加快递到汇总（跳过API查询）"""
        tracking_num = self.manual_tracking_input.text().strip()
        if not tracking_num:
            self.status_bar.showMessage("⚠️ 请输入快递单号！", 3000)
            return
            
        company_name = self.manual_company_combo.currentText()
        company_code = self.company_codes.get(company_name, "")
        
        # 如果启用了自动识别，尝试根据单号格式识别
        if company_name == "自动识别" or not company_code:
            detected_code, detected_name = self.get_company_code_by_number(tracking_num)
            if detected_code:
                company_code = detected_code
                company_name = detected_name
            else:
                company_name = "未知"
                company_code = ""
        
        if self.user_manager.current_user_db:
            # 检查是否已存在
            check_sql = "SELECT id FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
            existing = self.user_manager.current_user_db.execute_query(check_sql, (tracking_num,))
            if existing:
                self.status_bar.showMessage("✅ 该快递单号已存在于汇总中", 3000)
                return
            
            # 创建待查询状态的数据
            pending_data = {
                'nu': tracking_num,
                'com': company_code,
                'state': '0',
                'data': [],
                'message': '手动添加，待查询'
            }
            
            # 添加到汇总
            self.add_to_summary(pending_data, company_name)
            
            # 清空输入框
            self.manual_tracking_input.clear()
            
            # 刷新汇总显示
            self.load_summary_data()
            
            self.status_bar.showMessage(f"✅ {tracking_num} 已直接添加到汇总（待查询）", 3000)
        else:
            self.status_bar.showMessage("⚠️ 数据库未连接", 3000)

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
        
        self.tables_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tables_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tables_table.setSelectionMode(QTableWidget.SingleSelection)
        self.tables_table.setAlternatingRowColors(True)
        
        tables_layout.addWidget(self.tables_table)
        tables_group.setLayout(tables_layout)
        layout.addWidget(tables_group)
        
        # 操作按钮 - 第一行
        btn_layout1 = QHBoxLayout()
        
        backup_btn = QPushButton("💾 备份管理")
        backup_btn.clicked.connect(self.show_backup_dialog)
        btn_layout1.addWidget(backup_btn)
        
        optimize_btn = QPushButton("🔧 优化数据库")
        optimize_btn.clicked.connect(self.optimize_database)
        btn_layout1.addWidget(optimize_btn)
        
        btn_layout1.addStretch()
        layout.addLayout(btn_layout1)
        
        # ========== 新增：历史数据重建按钮 ==========
        rebuild_group = QGroupBox("历史数据重建（从现有物流轨迹解析）")
        rebuild_layout = QVBoxLayout()
        
        rebuild_info = QLabel(
            "💡 说明：从快递汇总表中已有的物流轨迹数据，重新解析并生成时效历史和节点运输历史。\n"
            "   适用于：已有签收/到站记录但未自动记录到历史表的情况。无需调用API，基于本地数据重建。"
        )
        rebuild_info.setWordWrap(True)
        rebuild_info.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        rebuild_layout.addWidget(rebuild_info)
        
        rebuild_btn_layout = QHBoxLayout()
        
        # 重建时效历史按钮
        self.rebuild_delivery_btn = QPushButton("📊 重建时效历史数据")
        self.rebuild_delivery_btn.setToolTip("从现有快递数据中解析揽收和签收时间，更新 delivery_history 表")
        self.rebuild_delivery_btn.clicked.connect(self.rebuild_delivery_history)
        self.rebuild_delivery_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
            }}
        """)
        rebuild_btn_layout.addWidget(self.rebuild_delivery_btn)
        
        # 重建节点历史按钮
        self.rebuild_node_btn = QPushButton("📍 重建节点运输历史数据")
        self.rebuild_node_btn.setToolTip("从现有快递数据中解析物流节点，更新 node_transit_history 表")
        self.rebuild_node_btn.clicked.connect(self.rebuild_node_history)
        self.rebuild_node_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PURPLE_WISTERIA.name()};
            }}
        """)
        rebuild_btn_layout.addWidget(self.rebuild_node_btn)
        
        # 全部重建按钮
        self.rebuild_all_btn = QPushButton("🔄 全部重建（时效+节点）")
        self.rebuild_all_btn.setToolTip("同时重建时效历史和节点运输历史")
        self.rebuild_all_btn.clicked.connect(self.rebuild_all_history)
        self.rebuild_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_SKY.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        rebuild_btn_layout.addWidget(self.rebuild_all_btn)
        
        rebuild_layout.addLayout(rebuild_btn_layout)
        
        # 进度条
        self.rebuild_progress = QProgressBar()
        self.rebuild_progress.setVisible(False)
        rebuild_layout.addWidget(self.rebuild_progress)
        
        # 状态标签
        self.rebuild_status = QLabel("")
        self.rebuild_status.setStyleSheet("color: #666; font-size: 11px;")
        rebuild_layout.addWidget(self.rebuild_status)
        
        rebuild_group.setLayout(rebuild_layout)
        layout.addWidget(rebuild_group)
        # ========== 新增结束 ==========
        
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
        判断优先级：已签收 > 驿站/代收点 > 派件中 > 待揽件 > 已揽收 > 疑难件 > 退件 > 清关中 > 在途中
        """
        state = str(state)
        context_lower = context.lower() if context else ""
        
        # ========== 1. 优先判断：已签收 ==========
        # 状态码: 3-已签收, 40-妥投, 75-已完成, 85-已完结
        if state in ['3', '40', '75', '85']:
            return 'signed'
        
        # 精确匹配已签收关键词（排除"请签收"、"领取签收"等未完成状态）
        # 注意：不使用单独的"签收"二字，避免误判
        sign_keywords = [
            '已签收', '本人签收', '他人签收', '快递员签收', 
            '签收人凭取货码签收', '凭取货码签收', '已取件',
            '已妥投', '签收成功', '已收件人签收', '已签收完成',
            '代收已签收', '家人代收', '同事代收', '前台代收', '物业代收'
        ]
        
        for keyword in sign_keywords:
            if keyword in context_lower or keyword in context:
                return 'signed'
    
        # ========== 2. 已到驿站/代收点 ==========
        station_keywords = [
            '驿站', '菜鸟', '丰巢', '快递柜', '自提柜', '代收点', '妈妈驿站', 
            '兔喜', '超市', '代理点', '自提', '代收', '投柜', '出柜',
            '存局', '已送达', '便利店', '物业', '门卫', '快递点', '菜鸟驿站',
            '菜鸟裹裹', '取件码', '凭取件码', '请取件', '可取件', '待取件',
            '快递超市', '邻里驿站', '熊猫快收', '速递易', '云柜', '日日顺',
            '蜂巢', 'e栈', '收件宝', '近邻宝', '格格货栈', '乐收',
            '已暂存至', '暂存至'
        ]
        
        for keyword in station_keywords:
            if keyword in context_lower or keyword in context:
                return 'arrived'
    
        # ========== 3. 派件中相关 ==========
        # 状态码: 5-派件中, 15-派件, 39-投递, 41-未妥投, 43-退回未妥投, 45-预约投递
        if state in ['5', '15', '39', '41', '43', '45']:
            return 'delivering'
        
        # 通过内容判断派件中
        delivering_keywords = ['派件', '派送', '投递', '派送中', '派件中', '正在派送', '快递员派送', '开始派送']
        for keyword in delivering_keywords:
            if keyword in context_lower or keyword in context:
                return 'delivering'
        
        # ========== 4. 待揽件/待处理 ==========
        # 注意：这个判断要放在已揽收之前
        # 状态码为0且没有物流内容，或者明确是待揽件状态
        if (state == '0' and (not context or context == "等待揽件" or "暂无物流信息" in context)):
            return 'pending'
        
        # 明确是待揽件的内容
        pending_keywords = ['等待揽件', '暂无物流信息', '待揽件', '未揽件', '等待收件']
        for keyword in pending_keywords:
            if keyword in context_lower or keyword in context:
                return 'pending'
        
        
        # ========== 5. 已揽收相关 ==========
        # 状态码: 1-已揽收, 12-收件, 13-发件, 16-取件, 37-揽件, 38-收寄, 71-已接单, 72-已取件, 73-已收件
        if state in ['1', '12', '13', '16', '37', '38', '71', '72', '73']:
            return 'picked'
        
        # 通过内容判断已揽收
        picked_keywords = ['揽收', '已揽件', '收件', '取件', '已收寄', '已接单', '已取件', '揽收成功']
        for keyword in picked_keywords:
            if keyword in context_lower or keyword in context:
                return 'picked'
        
        # ========== 6. 疑难/问题件相关 ==========
        # 状态码: 2-疑难, 11-清关异常, 19-问题件, 35-海关查验, 36-海关扣留
        if state in ['2', '11', '19', '35', '36']:
            return 'problem'
        
        # 精确的疑难件关键词
        problem_keywords = ['疑难件', '问题件', '物流异常', '快件异常', '滞留件', '超时件', '未妥投', '未投妥']
        for keyword in problem_keywords:
            if keyword in context_lower or keyword in context:
                return 'problem'
        
        # ========== 7. 退件相关 ==========
        # 状态码: 4-退签, 6-退回, 42-退回妥投, 90-已退回, 98-已退货
        if state in ['4', '6', '42', '90', '98']:
            return 'returned'
        
        # 通过内容判断退件
        returned_keywords = ['退回', '退件', '退签', '退货', '返程', '原路返回']
        for keyword in returned_keywords:
            if keyword in context_lower or keyword in context:
                return 'returned'
        
        # ========== 8. 清关相关 ==========
        # 状态码: 8-待清关, 9-清关中, 10-已清关, 34-海关放行
        if state in ['8', '9', '10', '34']:
            return 'customs'
        
        # 通过内容判断清关
        customs_keywords = ['清关', '海关', '报关', '通关', '海关放行']
        for keyword in customs_keywords:
            if keyword in context_lower or keyword in context:
                return 'customs'
        
        # ========== 9. 在途中相关（默认分类） ==========
        # 状态码: 0-在途中, 7-转单, 14-到件, 17-投柜, 18-出柜, 20-入库, 21-出库, 22-安检, 23-装车, 24-卸车
        # 25-封发, 26-开拆, 27-离开, 28-到达, 29-中转, 30-交航, 31-起飞, 32-降落, 33-提货
        # 44-存局, 46-自提, 47-代收, 48-代理点
        transit_states = ['0', '7', '14', '17', '18', '20', '21', '22', '23', '24',
                        '25', '26', '27', '28', '29', '30', '31', '32', '33',
                        '44', '46', '47', '48']
        
        if state in transit_states:
            return 'transit'
        
        # 通过内容判断在途中
        transit_keywords = ['在途', '运输', '中转', '到达', '离开', '发出', '发往', '送往']
        for keyword in transit_keywords:
            if keyword in context_lower or keyword in context:
                return 'transit'
        
        # ========== 默认分类 ==========
        # 如果都不匹配，默认归类为在途中
        return 'pending' if state == '0' else 'transit'

        
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
    
        # 添加调试输出
        # if DEBUG_MODE:
        #     print(f"[加载汇总] 共查询到 {len(results)} 条记录")

        for record in results:
            category = record.get('status_category', 'other')
            # if DEBUG_MODE:
            #     print(f"[加载汇总] 单号: {record.get('tracking_number', '')}, 分类: {category}")
            self.add_express_to_category(record)
    
        # 添加调试输出
        # if DEBUG_MODE:
        #     for key, widget in self.category_widgets.items():
        #         print(f"[加载汇总] 分类 {key}: {len(widget.express_items)} 个条目")
        
        # 强制刷新计数
        # for widget in self.category_widgets.values():
        #     widget.update_count()

        # QTimer.singleShot(50, self._force_refresh_all_counts)

        # 强制刷新所有分类的计数
        for widget in self.category_widgets.values():
            widget.update_count()

    def _force_refresh_all_counts(self):
        """强制刷新所有分类的计数"""
        for widget in self.category_widgets.values():
            widget.update_count()
            # 强制处理待处理的事件
            QApplication.processEvents()

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
                self.status_bar.showMessage("🗑️ 快递已删除", 3000)
            
    def on_single_refresh(self, tracking_num: str, company_code: str):
        """单个快递刷新"""
        if not self.customer or not self.key:
            self.status_bar.showMessage("⚠️ 未配置API账号，请先在设置中添加账号", 3000)
            return
    
        # 显示当前使用的接口类型
        if hasattr(self, 'api_endpoint_manager') and self.api_endpoint_manager:
            endpoint = self.api_endpoint_manager.get_current_endpoint()
            if endpoint:
                endpoint_type = endpoint.get('endpoint_type', 'unknown')
                endpoint_name = endpoint.get('name', '未知')
                if endpoint_type == 'free':
                    self.status_bar.showMessage(f"🔄 使用免费接口 [{endpoint_name}] 刷新 {tracking_num}...", 2000)
                elif endpoint_type == 'paid':
                    self.status_bar.showMessage(f"🔄 使用收费接口 [{endpoint_name}] 刷新 {tracking_num}...", 2000)
                else:
                    self.status_bar.showMessage(f"🔄 使用自定义接口 [{endpoint_name}] 刷新 {tracking_num}...", 2000)
        
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
                    self.status_bar.showMessage("⚠️ 所有账号今日额度都已用完，请明天再试", 3000)
                    return
            
        # 显示进度条
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, 0)  # 不确定进度模式
        self.global_progress.setValue(0)
        self.status_bar.showMessage(f"正在刷新 {tracking_num}...")
        
        thread = ExpressQueryThreadPro(tracking_num, company_code, self.customer, self.key)
        thread.finished.connect(lambda r: self.on_single_refresh_finished(r, tracking_num))
        thread.start()
        self.query_threads.append(thread)
        


    def on_single_refresh_retry_finished(self, result, tracking_num):
        """单个快递刷新重试完成"""
        self.global_progress.setVisible(False)
        if result.get('success'):
            # ========== 修改：只更新单个条目 ==========
            self.update_single_express_item(tracking_num, result['data'])
            self.status_bar.showMessage(f"{tracking_num} 刷新成功（切换账号后）", 3000)
            
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
            self.status_bar.showMessage("✅ 所有单号都已存在于汇总中", 3000)
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
        
    def on_batch_import_finished(self, result, tracking_num):
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
            
            # ========== 修复：只在额度/权限错误时才切换账号重试 ==========
            if self._should_switch_account_on_error(error_msg) and self._try_switch_and_retry(tracking_num, item['company_code'], error_msg):
                thread = ExpressQueryThreadPro(
                    tracking_num, item['company_code'],
                    self.customer, self.key
                )
                thread.finished.connect(lambda r, num=tracking_num, itm=item: self.on_batch_import_retry_finished(r, num, itm))
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
        
        self.load_summary_data()
        
        # 批量导入完成只需要状态栏提示，不需要弹窗
        self.status_bar.showMessage(f"📦 批量导入完成：成功 {success_count} 个，失败 {fail_count} 个", 5000)
        
        # 如果有失败的，可以在控制台输出详情（调试模式）
        if fail_count > 0 and DEBUG_MODE:
            failed_list = [f"{r['number']}: {r['message']}" for r in self.batch_import_results if not r['success']]
            print("失败详情：")
            for item in failed_list[:10]:
                print(f"  {item}")
            if len(failed_list) > 10:
                print(f"  ... 共 {len(failed_list)} 个失败")


            
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
    
        # ========== 获取默认收件地址 ==========
        # 优先使用地址管理器中的默认地址，其次使用用户设置中的默认地址
        default_dest = ""
        if hasattr(self, 'dest_address_manager'):
            default_dest = self.dest_address_manager.get_default_address_text()
        if not default_dest:
            default_dest = self.user_manager.get_user_setting("default_dest_address", "")
        
        check_sql = "SELECT id FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
        existing = self.user_manager.current_user_db.execute_query(check_sql, (tracking_num,))
        
        if existing:
            # 更新现有记录，只设置 dest_address 如果原本为空
            sql = """
            UPDATE express_summary 
            SET company_code = ?, company_name = ?, status = ?, status_category = ?, 
                latest_track = ?, result_data = ?, last_update = ?,
                dest_address = CASE 
                    WHEN dest_address IS NULL OR dest_address = '' THEN ? 
                    ELSE dest_address 
                END
            WHERE tracking_number = ? AND is_deleted = 0
            """
            self.user_manager.current_user_db.execute_update(
                sql,
                (company_code, company_name, state_text, category, latest_track, 
                json.dumps(data, ensure_ascii=False), current_time, 
                default_dest, tracking_num)
            )
        else:
            # 插入新记录，使用默认地址
            sql = """
            INSERT INTO express_summary 
            (tracking_number, company_code, company_name, status, status_category, 
            latest_track, result_data, dest_address, last_update, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.user_manager.current_user_db.execute_update(
                sql,
                (tracking_num, company_code, company_name, state_text, category,
                latest_track, json.dumps(data, ensure_ascii=False), default_dest,
                current_time, current_time)
            )
            
        # 记录时效数据（如果是已签收或已到驿站）
        if self.delivery_estimator and track_list:
            context = latest_context
            should_record = False
            
            if state == '3':
                should_record = True
            elif self.delivery_estimator.is_signed(context):
                should_record = True
            elif self.delivery_estimator.is_arrived_at_station(context):
                should_record = True
                
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
                
        # 记录节点运输时间（只要有轨迹就记录）
        if self.node_analyzer and track_list:
            self.node_analyzer.record_node_transit(data)
        
    def update_express_summary(self, data: dict, auto_refresh_ui: bool = True):
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
        
        self.user_manager.current_user_db.execute_update(
            sql,
            (state_text, category, latest_track, json.dumps(data, ensure_ascii=False), 
            current_time, tracking_num)
        )
        
        # 记录时效数据
        if self.delivery_estimator:
            context = latest_context
            should_record = False
            
            if state == '3':
                should_record = True
            elif self.delivery_estimator.is_signed(context):
                should_record = True
            elif self.delivery_estimator.is_arrived_at_station(context):
                should_record = True
                
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
                
        # 记录节点运输时间
        if self.node_analyzer and track_list:
            self.node_analyzer.record_node_transit(data)
        
        # 只在需要时刷新界面
        if auto_refresh_ui:
            self.load_summary_data()
            
    def refresh_category(self, category_key: str):
        """刷新分类下所有快递 - 添加进度条"""
        if not self.customer or not self.key:
            self.status_bar.showMessage("⚠️ 未配置API账号，请先在设置中添加账号", 3000)
            return
            
        if category_key not in self.category_widgets:
            return
            
        category_widget = self.category_widgets[category_key]
        items = category_widget.express_items
        
        if not items:
            self.status_bar.showMessage("✅ 该分类下没有快递需要刷新", 3000)
            return
        
        # 检查当前账号是否可用
        if self.api_account_manager:
            self.api_account_manager.check_and_reset_daily_usage()
            
            if not self.api_account_manager.is_current_account_available():
                if self.api_account_manager.switch_to_next_account(force_switch=False):
                    self.load_current_api_account()
                    usage_info = self.api_account_manager.get_usage_info()
                    self.status_bar.showMessage(f"已自动切换到备用账号，剩余次数：{usage_info['remaining']}", 3000)
                else:
                    self.status_bar.showMessage("⚠️ 所有账号今日额度都已用完，请明天再试", 3000)
                    return
            
        tracking_list = []
        for item in items:
            tracking_list.append({
                'tracking_number': item.express_data.get('tracking_number', ''),
                'company_code': item.express_data.get('company_code', '')
            })
            
        # 显示进度条（确定进度模式）
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        self.status_bar.showMessage(f"正在刷新 {category_widget.category_name} 分类...")
        
        # 保存正在刷新的分类key
        self.refreshing_category_key = category_key
        
        self.batch_thread = BatchRefreshThread(tracking_list, self.customer, self.key)
        self.batch_thread.finished.connect(self.on_category_refresh_finished)
        self.batch_thread.progress.connect(self.on_batch_progress)
        self.batch_thread.start()


    def on_category_refresh_finished(self, success_results, failed_items):
        """分类刷新完成"""
        self.global_progress.setVisible(False)
        if hasattr(self, 'toolbar_progress'):
            self.toolbar_progress.setVisible(False)
        
        success_count = len(success_results)
        fail_count = len(failed_items)
        
        # 批量更新数据库，不刷新界面
        for result in success_results:
            if result.get('success'):
                self.update_express_summary(result['data'], auto_refresh_ui=False)
        
        # ========== 修复：只在额度/权限错误时才切换账号重试 ==========
        category_name = self.category_widgets.get(self.refreshing_category_key, None)
        cat_name = category_name.category_name if category_name else "分类"
        
        if failed_items:
            # 检查第一个失败的错误是否值得切换账号
            first_error = failed_items[0].get('error', '') if failed_items else ''
            
            if self._should_switch_account_on_error(first_error) and self._try_switch_and_retry("", "", first_error):
                new_account = self.api_account_manager.get_current_account()
                new_account_name = new_account.get('account_name', '未知') if new_account else '未知'
                
                reply = QMessageBox.question(
                    self, "刷新完成",
                    f"成功刷新 {success_count} 个快递，{fail_count} 个刷新失败。\n\n"
                    f"已自动切换到备用账号：{new_account_name}\n\n"
                    f"是否使用新账号重试失败的单号？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.pending_retry_failed_items = failed_items
                    self.retry_category_failed_refresh(failed_items)
                    return
                else:
                    self.load_summary_data()
                    self.status_bar.showMessage(f"{cat_name} 刷新完成：成功 {success_count}，失败 {fail_count}（已切换账号）", 5000)
            else:
                self.load_summary_data()
                self.status_bar.showMessage(f"✅ {cat_name} 刷新完成：成功 {success_count}，失败 {fail_count}", 5000)
        else:
            self.load_summary_data()
            self.status_bar.showMessage(f"✅ {cat_name} 刷新完成：成功 {success_count} 个", 5000)

    def retry_category_failed_refresh(self, failed_items: list):
        """重试分类中失败的刷新"""
        if not failed_items:
            return
        
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        self.status_bar.showMessage(f"正在使用新账号重试 {len(failed_items)} 个失败的单号...")
        
        tracking_list = [
            {'tracking_number': item['tracking_number'], 'company_code': item.get('company_code', '')}
            for item in failed_items
        ]
        
        self.batch_retry_thread = BatchRefreshThread(tracking_list, self.customer, self.key)
        self.batch_retry_thread.finished.connect(self.on_category_retry_finished)
        self.batch_retry_thread.progress.connect(self.on_batch_progress)
        self.batch_retry_thread.start()

    def on_category_retry_finished(self, success_results: list, failed_items: list):
        """分类重试刷新完成"""
        self.global_progress.setVisible(False)
        
        success_count = len(success_results)
        fail_count = len(failed_items)
        
        # 批量更新数据库，不刷新界面
        for result in success_results:
            if result.get('success'):
                self.update_express_summary(result['data'], auto_refresh_ui=False)
                if self.api_account_manager:
                    self.api_account_manager.increment_usage()
        
        self.update_api_account_display()
        
        # 最后一次性刷新界面
        self.load_summary_data()
        
        category_name = self.category_widgets.get(self.refreshing_category_key, None)
        cat_name = category_name.category_name if category_name else "分类"
        
        if fail_count == 0:
            self.status_bar.showMessage(f"✅ {cat_name} 重试成功！所有单号已刷新", 5000)
        else:
            self.status_bar.showMessage(f"⚠️ {cat_name} 重试完成：成功 {success_count}，仍有 {fail_count} 个失败", 5000)

    def refresh_all_express(self):
        """刷新所有快递 - 添加进度条"""
        if not self.customer or not self.key:
            self.status_bar.showMessage("⚠️ 未配置API账号，请先在设置中添加账号", 3000)
            return
    
        # 显示当前使用的接口类型
        if hasattr(self, 'api_endpoint_manager') and self.api_endpoint_manager:
            endpoint = self.api_endpoint_manager.get_current_endpoint()
            if endpoint:
                endpoint_type = endpoint.get('endpoint_type', 'unknown')
                if endpoint_type == 'free':
                    self.status_bar.showMessage("🔄 使用免费接口刷新所有快递...", 2000)
                elif endpoint_type == 'paid':
                    self.status_bar.showMessage("🔄 使用收费接口刷新所有快递...", 2000)
        
        # 检查当前账号是否可用
        if self.api_account_manager:
            self.api_account_manager.check_and_reset_daily_usage()
            
            if not self.api_account_manager.is_current_account_available():
                if self.api_account_manager.switch_to_next_account(force_switch=False):
                    self.load_current_api_account()
                    usage_info = self.api_account_manager.get_usage_info()
                    self.status_bar.showMessage(f"已自动切换到备用账号，剩余次数：{usage_info['remaining']}", 3000)
                else:
                    self.status_bar.showMessage("⚠️ 所有账号今日额度都已用完，请明天再试", 3000)
                    return
            
        tracking_list = []
        for widget in self.category_widgets.values():
            for item in widget.express_items:
                tracking_list.append({
                    'tracking_number': item.express_data.get('tracking_number', ''),
                    'company_code': item.express_data.get('company_code', '')
                })
                
        if not tracking_list:
            self.status_bar.showMessage("✅ 没有快递需要刷新", 3000)
            return
            
        # 显示进度条（确定进度模式）
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        self.status_bar.showMessage("正在刷新所有快递...")
        
        self.batch_thread = BatchRefreshThread(tracking_list, self.customer, self.key)
        self.batch_thread.finished.connect(self.on_batch_refresh_finished)
        self.batch_thread.progress.connect(self.on_batch_progress)
        self.batch_thread.start()
        
    def on_batch_progress(self, value: int, message: str):
        """批量刷新进度"""
        self.global_progress.setValue(value)
        if hasattr(self, 'toolbar_progress'):
            self.toolbar_progress.setVisible(True)
            self.toolbar_progress.setRange(0, 100)
            self.toolbar_progress.setValue(value)
            # 简化显示，只显示进度百分比
            self.toolbar_progress.setFormat(f"%p%")
        self.status_bar.showMessage(message)
        
    def on_batch_refresh_finished(self, success_results, failed_items):
        """批量刷新完成"""
        self.global_progress.setVisible(False)
        if hasattr(self, 'toolbar_progress'):
            self.toolbar_progress.setVisible(False)
        
        success_count = len(success_results)
        fail_count = len(failed_items)
        
        for result in success_results:
            if result.get('success'):
                self.update_express_summary(result['data'], auto_refresh_ui=False)
        
        # ========== 修复：只在额度/权限错误时才切换账号重试 ==========
        if failed_items:
            first_error = failed_items[0].get('error', '') if failed_items else ''
            
            if self._should_switch_account_on_error(first_error) and self._try_switch_and_retry("", "", first_error):
                new_account = self.api_account_manager.get_current_account()
                new_account_name = new_account.get('account_name', '未知') if new_account else '未知'
                
                reply = QMessageBox.question(
                    self, "刷新完成",
                    f"成功刷新 {success_count} 个快递，{fail_count} 个刷新失败。\n\n"
                    f"已自动切换到备用账号：{new_account_name}\n\n"
                    f"是否使用新账号重试失败的单号？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.retry_failed_refresh(failed_items)
                    return
                else:
                    self.load_summary_data()
                    self.status_bar.showMessage(f"刷新完成：成功 {success_count}，失败 {fail_count}（已切换账号）", 5000)
            else:
                self.load_summary_data()
                self.status_bar.showMessage(f"✅ 刷新完成：成功 {success_count} 个，失败 {fail_count} 个", 5000)
        else:
            self.load_summary_data()
            self.status_bar.showMessage(f"✅ 刷新完成：成功 {success_count} 个", 5000)

    def retry_failed_refresh(self, failed_items: list):
        """重试失败的刷新"""
        if not failed_items:
            return
        
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        self.status_bar.showMessage(f"正在使用新账号重试 {len(failed_items)} 个失败的单号...")
        
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
        
        # 批量更新数据库，不刷新界面
        for result in success_results:
            if result.get('success'):
                self.update_express_summary(result['data'], auto_refresh_ui=False)
                if self.api_account_manager:
                    self.api_account_manager.increment_usage()
        
        self.update_api_account_display()
        
        # ========== 最后一次性刷新界面 ==========
        self.load_summary_data()
        
        if fail_count == 0:
            self.status_bar.showMessage(f"✅ 重试成功！所有单号已刷新", 5000)
        else:
            self.status_bar.showMessage(f"⚠️ 重试完成：成功 {success_count}，仍有 {fail_count} 个失败", 5000)
        
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
                        
            self.status_bar.showMessage(f"✅ 已导出到: {file_path}", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"❌ 导出失败: {e}", 5000)

    def get_company_name(self, code: str) -> str:
        """根据代码获取公司名称"""
        for name, c in self.company_codes.items():
            if c == code:
                return name
        return code or "未知"
        
    def query_express(self, verification_code: str = ""):
        """查询快递 - 支持验证码"""
        tracking_num = self.tracking_num.text().strip()
        if not tracking_num:
            self.status_bar.showMessage("⚠️ 请输入快递单号！", 3000)
            return
        
        # 获取公司代码
        company_name = self.company_combo.currentText()
        company_code = self.company_codes.get(company_name, "")
        
        # 获取当前API接口
        current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
        
        # ========== 新增：免费接口需要具体的公司代码 ==========
        if current_endpoint and current_endpoint.get('endpoint_type') == 'free':
            if company_name == "自动识别" or not company_code:
                # 免费接口也需要公司代码，先尝试自动识别
                detected_code, detected_name = self.get_company_code_by_number(tracking_num)
                if detected_code:
                    company_code = detected_code
                    company_name = detected_name
                    # 更新下拉框显示
                    if company_name in self.company_codes:
                        self.company_combo.setCurrentText(company_name)
                else:
                    QMessageBox.warning(self, "提示", 
                        "免费接口需要指定快递公司。\n\n"
                        "自动识别未能匹配到快递公司，请手动选择快递公司后再查询。\n\n"
                        "提示：\n"
                        "• 顺丰单号通常以SF开头\n"
                        "• 圆通单号通常以YT开头\n"
                        "• 中通单号通常以ZT或7开头\n"
                        "• 韵达单号通常以YD或1/4/5开头\n"
                        "• 申通单号通常以ST或3/7/8开头\n"
                        "• 极兔单号通常以JT开头")
                    return
        
        # 检查接口类型并验证必要配置
        if current_endpoint and current_endpoint.get('endpoint_type') == 'free':
            # 免费接口不需要验证customer/key
            pass
        else:
            if not self.customer or not self.key:
                self.load_current_api_account()
                if not self.customer or not self.key:
                    reply = QMessageBox.question(
                        self, "提示",
                        "收费接口需要配置API账号。是否现在添加账号？\n\n"
                        "或者您可以切换到免费接口使用（设置 → API接口）。",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.show_settings()
                    return
        
        # 检查当前账号是否可用（仅收费接口需要）
        if current_endpoint and current_endpoint.get('endpoint_type') != 'free':
            if self.api_account_manager:
                self.api_account_manager.check_and_reset_daily_usage()
                
                if not self.api_account_manager.is_current_account_available():
                    if self.api_account_manager.switch_to_next_account(force_switch=False):
                        self.load_current_api_account()
                        usage_info = self.api_account_manager.get_usage_info()
                        QMessageBox.information(self, "提示", 
                            f"当前账号额度已用完，已自动切换到备用账号\n"
                            f"新账号今日剩余次数：{usage_info['remaining']}/{usage_info['limit']}")
                    else:
                        accounts = self.api_account_manager.get_accounts()
                        info_text = "所有账号今日额度都已用完：\n"
                        for acc in accounts:
                            info_text += f"  {acc['account_name']}: {acc['used_today']}/{acc['daily_limit']}\n"
                        info_text += "\n请在明天0点后重试，或添加新的API账号。"
                        QMessageBox.warning(self, "提示", info_text)
                        return
        
        # 清空之前的结果
        self.clear_results()
        
        # 显示进度条
        self.query_btn.setEnabled(False)
        self.query_progress.setVisible(True)
        self.query_progress.setRange(0, 100)
        
        # 显示更详细的查询信息
        if current_endpoint and current_endpoint.get('endpoint_type') == 'free':
            self.status_label.setText(f"正在使用免费接口查询 {tracking_num}（{company_name}）...")
            self.status_bar.showMessage(f"🆓 免费接口查询中: {tracking_num} ({company_name})")
        else:
            self.status_label.setText("正在查询中，请稍候...")
            self.status_bar.showMessage("正在查询...")
        
        # 创建查询线程
        if current_endpoint and current_endpoint.get('endpoint_type') == 'free':
            self.query_thread = ExpressQueryThreadPro(
                tracking_num, company_code, 
                "", "", current_endpoint, auto_detect=True,
                verification_code=verification_code
            )
        else:
            self.query_thread = ExpressQueryThreadPro(
                tracking_num, company_code, 
                self.customer, self.key, current_endpoint,
                verification_code=verification_code
            )
        
        # 连接信号
        self.query_thread.finished.connect(self.on_query_finished)
        self.query_thread.progress.connect(self.query_progress.setValue)
        self.query_thread.need_verification.connect(self.on_need_verification)
        self.query_thread.start()
        self.query_threads.append(self.query_thread)

    
    def on_need_verification(self, tracking_num: str, company_name: str, company_code: str):
        """需要验证码时调用"""
        # 保存待验证的信息
        self.pending_verification = {
            'tracking_num': tracking_num,
            'company_name': company_name,
            'company_code': company_code
        }
        
        # 显示验证码对话框
        dialog = VerificationCodeDialog(tracking_num, company_name, self)
        if dialog.exec() == QDialog.Accepted:
            verification_code = dialog.get_verification_code()
            
            # 用验证码重新查询
            self.status_bar.showMessage(f"正在使用验证码重新查询 {tracking_num}...")
            
            # 更新查询输入框
            self.tracking_num.setText(tracking_num)
            for name, code in self.company_codes.items():
                if code == company_code:
                    self.company_combo.setCurrentText(name)
                    break
            
            # 重新查询（带验证码）
            self.query_express(verification_code)
        else:
            self.status_bar.showMessage(f"已取消查询 {tracking_num}（需要验证）", 3000)
            self.pending_verification = None
        
    def on_query_finished(self, result):
        """查询完成回调"""
        self.query_btn.setEnabled(True)
        self.query_progress.setVisible(False)
        
        if 'quota_info' in result:
            self.update_quota_info(result['quota_info'])
        
        # 检查是否需要验证码
        if result.get('need_verification'):
            if result.get('verification_failed'):
                self.verification_retry_count += 1
                
                tracking_num = result.get('tracking_num', '')
                company_code = result.get('company_code', '')
                company_name = self.get_company_name(company_code)
                
                reply = QMessageBox.question(
                    self, "验证失败",
                    f"手机尾号验证失败，是否重新输入？\n\n"
                    f"快递单号：{tracking_num}\n"
                    f"快递公司：{company_name}\n"
                    f"已尝试次数：{self.verification_retry_count}\n\n"
                    f"💡 提示：请确认收件人手机尾号是否正确。",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    dialog = VerificationCodeDialog(tracking_num, company_name, self)
                    if dialog.exec() == QDialog.Accepted:
                        verification_code = dialog.get_verification_code()
                        self.tracking_num.setText(tracking_num)
                        for name, code in self.company_codes.items():
                            if code == company_code:
                                self.company_combo.setCurrentText(name)
                                break
                        self.query_express(verification_code)
                    else:
                        self.status_label.setText("查询取消（需要验证）")
                        self.status_bar.showMessage(f"已取消查询 {tracking_num}", 3000)
                        self.verification_retry_count = 0
                else:
                    self.status_label.setText("查询取消（需要验证）")
                    self.status_bar.showMessage(f"已取消查询 {tracking_num}", 3000)
                    self.verification_retry_count = 0
                return
            
            self.verification_retry_count = 0
            return
        
        # 重置验证重试计数
        self.verification_retry_count = 0
        
        if result.get('success'):
            if self.api_account_manager:
                self.api_account_manager.increment_usage()
                self.update_api_account_display()
            
            is_pending = result.get('is_pending', False)
            data = result['data']
            
            self.process_result(data)
            
            if is_pending:
                self.status_label.setText("查询成功！快递单号有效，等待揽件中...")
                self.status_bar.showMessage("✅ 单号有效，等待揽件", 5000)
            else:
                self.status_label.setText("查询成功！")
                self.status_bar.showMessage("✅ 查询成功", 3000)
            
            self.save_query_to_history(data, result.get('quota_info', {}))
            self.add_to_summary(data)
            self.load_summary_data()
            
            # 询问是否查看汇总
            if is_pending:
                reply = QMessageBox.question(
                    self, "添加成功",
                    f"快递单号有效，已添加到汇总。\n\n"
                    f"当前状态：等待揽件\n"
                    f"温馨提示：有物流更新后，可在汇总页面点击\"刷新\"按钮更新状态。\n\n"
                    f"是否切换到汇总标签查看？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.main_tab_widget.setCurrentIndex(0)
            else:
                reply = QMessageBox.question(
                    self, "添加成功",
                    "快递已添加到汇总，是否切换到汇总标签查看？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.main_tab_widget.setCurrentIndex(0)
        else:
            error_msg = result.get('error', '未知错误')
            tracking_num = self.tracking_num.text().strip()
            company_name = self.company_combo.currentText()
            company_code = self.company_codes.get(company_name, "")
            
            self.status_label.setText(f"查询失败：{error_msg}")
            
            # 判断是否应该提供"仍然添加"选项
            allow_add_keywords = ['没该功能权限', '权限', '单号不存在', '暂无轨迹', '暂无物流信息', '未揽件', '无物流']
            should_offer_add = any(keyword in error_msg for keyword in allow_add_keywords)
            
            if should_offer_add:
                reply = QMessageBox.question(
                    self, "查询失败",
                    f"API查询失败：{error_msg}\n\n"
                    f"快递单号：{tracking_num}\n"
                    f"快递公司：{company_name}\n\n"
                    f"可能是单号有效但API暂时无法查询（如权限不足或未揽件）。\n\n"
                    f"是否仍然将此单号添加到快递汇总？\n"
                    f"（添加后可以稍后刷新获取物流信息）",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    pending_data = {
                        'nu': tracking_num,
                        'com': company_code,
                        'state': '0',
                        'data': [],
                        'message': f'添加时查询失败：{error_msg}'
                    }
                    
                    self.add_to_summary(pending_data, company_name)
                    self.load_summary_data()
                    
                    if self.user_manager.current_user_db:
                        self.user_manager.save_query_history(
                            tracking_num, company_code, company_name, '待查询',
                            json.dumps(pending_data, ensure_ascii=False),
                            result.get('quota_info', {}).get('remaining', 0)
                        )
                    
                    self.status_label.setText(f"已添加到汇总（等待刷新）")
                    self.status_bar.showMessage(f"✅ {tracking_num} 已添加到汇总", 5000)
                    
                    self.clear_results()
                    
                    view_reply = QMessageBox.question(
                        self, "添加成功",
                        f"快递单号 {tracking_num} 已添加到汇总。\n\n"
                        f"当前状态：待查询/待揽件\n"
                        f"温馨提示：稍后可在汇总页面点击\"刷新\"按钮更新状态。\n\n"
                        f"是否切换到汇总标签查看？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if view_reply == QMessageBox.Yes:
                        self.main_tab_widget.setCurrentIndex(0)
                    return
                else:
                    self.status_bar.showMessage(f"🚫 已取消添加 {tracking_num}", 3000)
                    return
            
            # ========== 修复：只在额度/权限错误时才切换账号 ==========
            if self.api_account_manager:
                self.api_account_manager.increment_usage()  # 即使失败也算使用次数
                
                if self._try_switch_and_retry(tracking_num, company_code, error_msg):
                    new_account = self.api_account_manager.get_current_account()
                    new_account_name = new_account.get('account_name', '未知') if new_account else '未知'
                    
                    reply = QMessageBox.question(
                        self, "查询失败",
                        f"查询失败：{error_msg}\n\n"
                        f"已自动切换到备用账号：{new_account_name}\n\n"
                        f"是否使用新账号重新查询？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        QTimer.singleShot(100, self.query_express)
                        return
                    else:
                        self.status_label.setText(f"查询失败：{error_msg}（已切换账号）")
                        self.status_bar.showMessage(f"❌ 查询失败：{error_msg}（已切换账号）", 5000)
                else:
                    self.status_bar.showMessage(f"❌ 查询失败：{error_msg}", 5000)
            else:
                self.status_bar.showMessage(f"❌ 查询失败：{error_msg}", 5000)



    def add_manual_express(self):
        """手动添加快递"""
        tracking_num = self.manual_tracking_input.text().strip()
        if not tracking_num:
            self.status_bar.showMessage("⚠️ 请输入快递单号！", 3000)
            return
            
        company_name = self.manual_company_combo.currentText()
        company_code = self.company_codes.get(company_name, "")
        
        if self.user_manager.current_user_db:
            check_sql = "SELECT id FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
            existing = self.user_manager.current_user_db.execute_query(check_sql, (tracking_num,))
            if existing:
                self.status_bar.showMessage("✅ 该快递单号已存在于汇总中", 3000)
                return
        
        # 保存待添加的信息
        self.pending_manual_add = {
            'tracking_num': tracking_num,
            'company_name': company_name,
            'company_code': company_code
        }
        
        # 显示进度条
        self.global_progress.setVisible(True)
        self.global_progress.setRange(0, 0)
        self.status_bar.showMessage(f"正在查询并添加 {tracking_num}...")
        
        # 创建查询线程
        current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
        
        thread = ExpressQueryThreadPro(
            tracking_num, company_code, 
            self.customer, self.key, current_endpoint
        )
        thread.finished.connect(self.on_manual_add_finished)
        thread.need_verification.connect(self.on_manual_add_need_verification)
        thread.start()
        self.query_threads.append(thread)

    def on_manual_add_need_verification(self, tracking_num: str, company_name: str, company_code: str):
        """手动添加时需要验证码"""
        self.global_progress.setVisible(False)
        
        # 保存待验证信息
        self.pending_manual_add = {
            'tracking_num': tracking_num,
            'company_name': company_name,
            'company_code': company_code
        }
        
        dialog = VerificationCodeDialog(tracking_num, company_name, self)
        if dialog.exec() == QDialog.Accepted:
            verification_code = dialog.get_verification_code()
            
            # 重新查询
            self.global_progress.setVisible(True)
            self.global_progress.setRange(0, 0)
            self.status_bar.showMessage(f"正在使用验证码查询 {tracking_num}...")
            
            current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
            
            thread = ExpressQueryThreadPro(
                tracking_num, company_code,
                self.customer, self.key, current_endpoint,
                verification_code=verification_code
            )
            thread.finished.connect(self.on_manual_add_finished)
            thread.need_verification.connect(self.on_manual_add_need_verification)
            thread.start()
            self.query_threads.append(thread)
        else:
            self.status_bar.showMessage(f"已取消添加 {tracking_num}（需要验证）", 3000)
            self.pending_manual_add = None

    def on_manual_add_finished(self, result):
        """手动添加完成"""
        self.global_progress.setVisible(False)
        
        if result.get('need_verification'):
            if result.get('verification_failed'):
                tracking_num = self.pending_manual_add.get('tracking_num', '') if self.pending_manual_add else ''
                company_name = self.pending_manual_add.get('company_name', '') if self.pending_manual_add else ''
                
                reply = QMessageBox.question(
                    self, "验证失败",
                    f"手机尾号验证失败，是否重新输入？\n\n"
                    f"快递单号：{tracking_num}\n"
                    f"快递公司：{company_name}",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    if self.pending_manual_add:
                        dialog = VerificationCodeDialog(tracking_num, company_name, self)
                        if dialog.exec() == QDialog.Accepted:
                            verification_code = dialog.get_verification_code()
                            
                            self.global_progress.setVisible(True)
                            self.global_progress.setRange(0, 0)
                            
                            current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
                            
                            thread = ExpressQueryThreadPro(
                                tracking_num, self.pending_manual_add['company_code'],
                                self.customer, self.key, current_endpoint,
                                verification_code=verification_code
                            )
                            thread.finished.connect(self.on_manual_add_finished)
                            thread.start()
                            self.query_threads.append(thread)
                            return
                else:
                    self.status_bar.showMessage(f"已取消添加 {tracking_num}", 3000)
            return
        
        tracking_num = self.pending_manual_add.get('tracking_num', '') if self.pending_manual_add else ''
        company_name = self.pending_manual_add.get('company_name', '') if self.pending_manual_add else ''
        company_code = self.pending_manual_add.get('company_code', '') if self.pending_manual_add else ''
        
        if result.get('success'):
            is_pending = result.get('is_pending', False)
            self.add_to_summary(result['data'], company_name)
            self.manual_tracking_input.clear()
            
            if is_pending:
                self.status_bar.showMessage(f"✅ {tracking_num} 已添加到汇总（等待揽件）", 5000)
            else:
                self.status_bar.showMessage(f"✅ {tracking_num} 已添加到汇总", 3000)
            
            self.load_summary_data()
        else:
            error_msg = result.get('error', '未知错误')
            
            allow_add_keywords = ['没该功能权限', '权限', '单号不存在', '暂无轨迹', '暂无物流信息', '未揽件', '无物流']
            should_offer_add = any(keyword in error_msg for keyword in allow_add_keywords)
            
            if should_offer_add:
                reply = QMessageBox.question(
                    self, "查询失败",
                    f"API查询失败：{error_msg}\n\n"
                    f"快递单号：{tracking_num}\n"
                    f"快递公司：{company_name}\n\n"
                    f"可能是单号有效但API暂时无法查询。\n\n"
                    f"是否仍然将此单号添加到快递汇总？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    pending_data = {
                        'nu': tracking_num,
                        'com': company_code,
                        'state': '0',
                        'data': [],
                        'message': f'添加时查询失败：{error_msg}'
                    }
                    
                    self.add_to_summary(pending_data, company_name)
                    self.manual_tracking_input.clear()
                    self.load_summary_data()
                    
                    self.status_bar.showMessage(f"✅ {tracking_num} 已强制添加到汇总（待查询）", 5000)
                    return
                else:
                    self.status_bar.showMessage(f"🚫 已取消添加 {tracking_num}", 3000)
            else:
                # ========== 修复：只在额度/权限错误时才切换账号 ==========
                self.status_bar.showMessage(f"❌ 查询失败：{error_msg}", 5000)
        
        self.pending_manual_add = None

    def on_single_refresh_finished(self, result, tracking_num):
        """单个快递刷新完成"""
        self.global_progress.setVisible(False)
        
        # 检查是否需要验证码
        if result.get('need_verification'):
            if result.get('verification_failed'):
                company_code = result.get('company_code', '')
                company_name = self.get_company_name(company_code)
                
                reply = QMessageBox.question(
                    self, "验证失败",
                    f"刷新 {tracking_num} 需要验证手机尾号，验证失败。\n\n"
                    f"快递公司：{company_name}\n\n"
                    f"是否重新输入验证？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    dialog = VerificationCodeDialog(tracking_num, company_name, self)
                    if dialog.exec() == QDialog.Accepted:
                        verification_code = dialog.get_verification_code()
                        
                        company_code = ""
                        if self.user_manager.current_user_db:
                            sql = "SELECT company_code FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
                            query_result = self.user_manager.current_user_db.execute_query(sql, (tracking_num,))
                            if query_result:
                                company_code = query_result[0].get('company_code', '')
                        
                        self.global_progress.setVisible(True)
                        self.global_progress.setRange(0, 0)
                        self.status_bar.showMessage(f"正在使用验证码刷新 {tracking_num}...")
                        
                        current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
                        
                        thread = ExpressQueryThreadPro(
                            tracking_num, company_code,
                            self.customer, self.key, current_endpoint,
                            verification_code=verification_code
                        )
                        thread.finished.connect(lambda r: self.on_single_refresh_finished(r, tracking_num))
                        thread.start()
                        self.query_threads.append(thread)
                        return
            return
        
        if result.get('success'):
            # ========== 修改：只更新单个条目 ==========
            self.update_single_express_item(tracking_num, result['data'])
            self.status_bar.showMessage(f"{tracking_num} 刷新成功", 3000)
            
            if self.api_account_manager:
                self.api_account_manager.increment_usage()
                self.update_api_account_display()
        else:
            error_msg = result.get('error', '未知错误')
            
            # ========== 修复：只在需要时切换账号 ==========
            if self._try_switch_and_retry(tracking_num, "", error_msg):
                new_account = self.api_account_manager.get_current_account()
                new_account_name = new_account.get('account_name', '未知') if new_account else '未知'
                
                reply = QMessageBox.question(
                    self, "刷新失败",
                    f"{tracking_num} 刷新失败：{error_msg}\n\n"
                    f"已自动切换到备用账号：{new_account_name}\n\n"
                    f"是否使用新账号重试？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # 获取公司代码
                    company_code = ""
                    if self.user_manager.current_user_db:
                        sql = "SELECT company_code FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
                        query_result = self.user_manager.current_user_db.execute_query(sql, (tracking_num,))
                        if query_result:
                            company_code = query_result[0].get('company_code', '')
                    
                    self.global_progress.setVisible(True)
                    self.global_progress.setRange(0, 0)
                    self.status_bar.showMessage(f"{tracking_num} 刷新失败，正在切换账号重试...")
                    
                    current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
                    
                    thread = ExpressQueryThreadPro(
                        tracking_num, company_code,
                        self.customer, self.key, current_endpoint
                    )
                    thread.finished.connect(lambda r: self.on_single_refresh_retry_finished(r, tracking_num))
                    thread.start()
                    self.query_threads.append(thread)
                    return
                else:
                    self.status_bar.showMessage(f"{tracking_num} 刷新失败（已切换账号）", 3000)
            else:
                # 普通错误或无法切换，不强制切换
                self.status_bar.showMessage(f"{tracking_num} 刷新失败: {error_msg}", 5000)



    def on_single_refresh_need_verification(self, tracking_num: str, company_name: str, company_code: str):
        """单个刷新需要验证码"""
        dialog = VerificationCodeDialog(tracking_num, company_name, self)
        if dialog.exec() == QDialog.Accepted:
            verification_code = dialog.get_verification_code()
            
            self.global_progress.setVisible(True)
            self.global_progress.setRange(0, 0)
            self.status_bar.showMessage(f"正在使用验证码刷新 {tracking_num}...")
            
            current_endpoint = self.api_endpoint_manager.get_current_endpoint() if self.api_endpoint_manager else None
            
            thread = ExpressQueryThreadPro(
                tracking_num, company_code,
                self.customer, self.key, current_endpoint,
                verification_code=verification_code
            )
            thread.finished.connect(lambda r: self.on_single_refresh_finished(r, tracking_num))
            thread.start()
            self.query_threads.append(thread)

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
                self.status_bar.showMessage("⚠️ 无法解析历史数据", 3000)
                
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
            self.status_bar.showMessage("⚠️ 没有可导出的数据", 3000)
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
                        
            self.status_bar.showMessage(f"✅ 已导出到: {file_path}", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"❌ 导出失败: {e}", 5000)
            
    def clear_history(self):
        """清空历史记录"""
        # 清空操作需要确认，保留弹窗
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
                    self.status_bar.showMessage("✅ 历史记录已清空", 3000)
                    
    def on_global_search(self):
        """全局搜索 - 按回车时弹出选择对话框"""
        search_text = self.global_search.text().strip()
        if not search_text:
            self.clear_summary_filter()
            return
        
        # 弹出选择对话框前，可以先不清除过滤
        # 让用户决定搜索范围
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("全局搜索")
        msg_box.setText(f"搜索关键词: \"{search_text}\"\n\n请选择操作：")
        
        summary_btn = msg_box.addButton("📦 查看汇总过滤结果", QMessageBox.YesRole)
        history_btn = msg_box.addButton("📋 搜索查询历史", QMessageBox.NoRole)
        both_btn = msg_box.addButton("🔍 两者都搜索", QMessageBox.AcceptRole)
        clear_btn = msg_box.addButton("🔄 清除过滤", QMessageBox.ResetRole)
        cancel_btn = msg_box.addButton("取消", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        clicked_btn = msg_box.clickedButton()
        
        if clicked_btn == cancel_btn:
            return
        elif clicked_btn == clear_btn:
            self.clear_global_search()
            return
        elif clicked_btn == summary_btn:
            # 已经在过滤状态，不需要额外操作
            self.main_tab_widget.setCurrentIndex(0)
            self.status_bar.showMessage(f"当前显示 \"{search_text}\" 的过滤结果", 3000)
        elif clicked_btn == history_btn:
            # 清除汇总过滤，搜索历史
            self.clear_summary_filter()
            self.main_tab_widget.setCurrentIndex(2)
            self.history_search.setText(search_text)
            self.search_history()
            self.status_bar.showMessage(f"已切换到查询历史搜索 \"{search_text}\"", 3000)
        elif clicked_btn == both_btn:
            # 保持汇总过滤，同时搜索历史
            self.main_tab_widget.setCurrentIndex(2)
            self.history_search.setText(search_text)
            self.search_history()
            self.status_bar.showMessage(f"汇总已过滤，历史已搜索 \"{search_text}\"", 5000)



    def search_in_summary(self, search_text: str):
        """在快递汇总中搜索并高亮匹配的条目"""
        search_lower = search_text.lower()
        match_count = 0
        first_match_item = None  # 记录第一个匹配的条目
        
        # 先清除之前的高亮
        self.clear_summary_search_highlight()
        
        # 遍历所有分类和条目
        for category_key, widget in self.category_widgets.items():
            category_has_match = False
            
            for item in widget.express_items:
                data = item.express_data
                tracking_num = (data.get('tracking_number') or '').lower()
                company_name = (data.get('company_name') or '').lower()
                status = (data.get('status') or '').lower()
                remark = (data.get('remark') or '').lower()
                latest_track = (data.get('latest_track') or '').lower()
                
                # 检查是否匹配
                is_match = (search_lower in tracking_num or 
                        search_lower in company_name or 
                        search_lower in status or 
                        search_lower in remark or 
                        search_lower in latest_track)
                
                if is_match:
                    match_count += 1
                    print(f"[搜索高亮] 匹配到单号: {tracking_num}")  # 调试信息
                    category_has_match = True
                    # 高亮显示匹配的条目
                    item.setProperty("search_match", True)
                    item.apply_search_highlight(True)
                    
                    # 记录第一个匹配的条目
                    if first_match_item is None:
                        first_match_item = (widget, item)
            
            # 如果分类中有匹配项，自动展开该分类
            if category_has_match and widget.is_collapsed:
                widget.set_collapsed(False)
        
        # 切换到快递汇总标签页
        self.main_tab_widget.setCurrentIndex(0)
        
        if match_count > 0:
            self.status_bar.showMessage(f"在快递汇总中找到 {match_count} 条匹配结果", 5000)
            
            # 滚动到第一个匹配的条目
            if first_match_item:
                widget, item = first_match_item
                # 使用 QTimer 延迟执行，确保 UI 已更新
                QTimer.singleShot(100, lambda: self.scroll_to_item(widget, item))
        else:
            self.status_bar.showMessage(f"在快递汇总中未找到 \"{search_text}\" 的匹配结果", 3000)
            QMessageBox.information(self, "搜索完成", 
                f"在快递汇总中未找到 \"{search_text}\" 的匹配结果。\n\n"
                f"您可以尝试：\n"
                f"• 检查关键词拼写\n"
                f"• 使用更简短的词搜索\n"
                f"• 在\"查询历史\"中搜索")


    def clear_summary_search_highlight(self):
        """清除快递汇总中的搜索高亮"""
        for category_key, widget in self.category_widgets.items():
            for item in widget.express_items:
                item.setProperty("search_match", False)
                item.apply_search_highlight(False)

    def save_original_items(self):
        """保存过滤前的原始条目状态"""
        self.original_items_visibility = {}
        for category_key, widget in self.category_widgets.items():
            visibility_list = []
            for item in widget.express_items:
                visibility_list.append(item.isVisible())
            self.original_items_visibility[category_key] = visibility_list



    def restore_original_visibility(self):
        """恢复原始的可见性状态（如果有保存的话）"""
        if hasattr(self, 'original_items_visibility'):
            for category_key, widget in self.category_widgets.items():
                if category_key in self.original_items_visibility:
                    visibility_list = self.original_items_visibility[category_key]
                    for i, item in enumerate(widget.express_items):
                        if i < len(visibility_list):
                            item.setVisible(visibility_list[i])
            self.is_filtered = False

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
            'node_transit_history': '节点运输历史数据',
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
                self.status_bar.showMessage("✅ 数据库优化完成", 3000)
                
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
        
        self.status_bar.showMessage("✅ 数据库已重新初始化", 3000)
        
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
    
        # 添加：加载调试模式设置
        debug_mode_str = self.user_manager.get_user_setting("debug_mode", "0")
        global DEBUG_MODE
        DEBUG_MODE = debug_mode_str == "1"

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
                
                # 同时更新状态栏提示
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage(f"当前使用API账号: {account_name}", 2000)
            else:
                self.api_account_label.setText(" | 🔑 API账号: 无")
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage("警告：未配置API账号，无法查询快递", 3000)



    def rebuild_delivery_history(self):
        """重建时效历史数据 - 从现有快递数据中解析揽收和签收时间"""
        if not self.user_manager.current_user_db:
            self.status_bar.showMessage("⚠️ 数据库未连接", 3000)
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认重建",
            "此操作将扫描所有快递汇总数据，\n"
            "从已有物流轨迹中提取揽收和签收时间，\n"
            "重建 delivery_history 表。\n\n"
            "现有数据将被覆盖，确定继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 使用线程执行，避免界面卡顿
        self.rebuild_thread = QThread()
        self.rebuild_worker = RebuildDeliveryWorker(self.user_manager.current_user_db)
        self.rebuild_worker.moveToThread(self.rebuild_thread)
        
        self.rebuild_thread.started.connect(self.rebuild_worker.run)
        self.rebuild_worker.progress.connect(self.on_rebuild_progress)
        self.rebuild_worker.status.connect(self.on_rebuild_status)
        self.rebuild_worker.finished.connect(self.on_rebuild_finished)
        self.rebuild_worker.finished.connect(self.rebuild_thread.quit)
        self.rebuild_worker.finished.connect(self.rebuild_worker.deleteLater)
        self.rebuild_thread.finished.connect(self.rebuild_thread.deleteLater)
        
        self.rebuild_progress.setVisible(True)
        self.rebuild_progress.setValue(0)
        self.rebuild_delivery_btn.setEnabled(False)
        self.rebuild_node_btn.setEnabled(False)
        self.rebuild_all_btn.setEnabled(False)
        self.rebuild_status.setText("正在重建时效历史数据...")
        
        self.rebuild_thread.start()


    def rebuild_node_history(self):
        """重建节点运输历史数据 - 从现有快递数据中解析物流节点"""
        if not self.user_manager.current_user_db:
            self.status_bar.showMessage("⚠️ 数据库未连接", 3000)
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认重建",
            "此操作将扫描所有快递汇总数据，\n"
            "从已有物流轨迹中提取节点信息，\n"
            "重建 node_transit_history 表。\n\n"
            "现有数据将被覆盖，确定继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 使用线程执行
        self.rebuild_thread = QThread()
        self.rebuild_worker = RebuildNodeWorker(self.user_manager.current_user_db)
        self.rebuild_worker.moveToThread(self.rebuild_thread)
        
        self.rebuild_thread.started.connect(self.rebuild_worker.run)
        self.rebuild_worker.progress.connect(self.on_rebuild_progress)
        self.rebuild_worker.status.connect(self.on_rebuild_status)
        self.rebuild_worker.finished.connect(self.on_rebuild_finished)
        self.rebuild_worker.finished.connect(self.rebuild_thread.quit)
        self.rebuild_worker.finished.connect(self.rebuild_worker.deleteLater)
        self.rebuild_thread.finished.connect(self.rebuild_thread.deleteLater)
        
        self.rebuild_progress.setVisible(True)
        self.rebuild_progress.setValue(0)
        self.rebuild_delivery_btn.setEnabled(False)
        self.rebuild_node_btn.setEnabled(False)
        self.rebuild_all_btn.setEnabled(False)
        self.rebuild_status.setText("正在重建节点运输历史数据...")
        
        self.rebuild_thread.start()


    def rebuild_all_history(self):
        """全部重建（时效+节点）"""
        if not self.user_manager.current_user_db:
            self.status_bar.showMessage("⚠️ 数据库未连接", 3000)
            return
        
        reply = QMessageBox.question(
            self, "确认重建",
            "此操作将扫描所有快递汇总数据，\n"
            "同时重建 delivery_history 和 node_transit_history 表。\n\n"
            "现有数据将被覆盖，确定继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.rebuild_thread = QThread()
        self.rebuild_worker = RebuildAllWorker(self.user_manager.current_user_db)
        self.rebuild_worker.moveToThread(self.rebuild_thread)
        
        self.rebuild_thread.started.connect(self.rebuild_worker.run)
        self.rebuild_worker.progress.connect(self.on_rebuild_progress)
        self.rebuild_worker.status.connect(self.on_rebuild_status)
        self.rebuild_worker.finished.connect(self.on_rebuild_finished)
        self.rebuild_worker.finished.connect(self.rebuild_thread.quit)
        self.rebuild_worker.finished.connect(self.rebuild_worker.deleteLater)
        self.rebuild_thread.finished.connect(self.rebuild_thread.deleteLater)
        
        self.rebuild_progress.setVisible(True)
        self.rebuild_progress.setValue(0)
        self.rebuild_delivery_btn.setEnabled(False)
        self.rebuild_node_btn.setEnabled(False)
        self.rebuild_all_btn.setEnabled(False)
        self.rebuild_status.setText("正在全部重建（时效+节点）...")
        
        self.rebuild_thread.start()


    def on_rebuild_progress(self, value: int):
        """重建进度更新"""
        self.rebuild_progress.setValue(value)


    def on_rebuild_status(self, message: str):
        """重建状态更新"""
        self.rebuild_status.setText(message)


    def on_rebuild_finished(self, success: bool, message: str):
        """重建完成"""
        self.rebuild_progress.setVisible(False)
        self.rebuild_delivery_btn.setEnabled(True)
        self.rebuild_node_btn.setEnabled(True)
        self.rebuild_all_btn.setEnabled(True)
        
        if success:
            # 刷新数据库信息显示
            self.refresh_database_info()
            
            # 调试模式下输出详细信息到控制台
            if DEBUG_MODE:
                print("=" * 60)
                print("[重建完成]")
                print(f"  结果: 成功")
                print(f"  详情: {message}")
                print("=" * 60)
            
            QMessageBox.information(self, "重建完成", message)
        else:
            # 调试模式下输出错误信息到控制台
            if DEBUG_MODE:
                print("=" * 60)
                print("[重建失败]")
                print(f"  结果: 失败")
                print(f"  错误信息: {message}")
                print("=" * 60)
            
            QMessageBox.critical(self, "重建失败", message)
        
        self.rebuild_status.setText("")

    def batch_export_numbers(self):
        """批量导出快递单号"""
        # 收集所有快递单号
        all_numbers = []
        selected_numbers = []
        
        for category_key, widget in self.category_widgets.items():
            for item in widget.express_items:
                data = item.express_data
                tracking_num = data.get('tracking_number', '')
                company_name = data.get('company_name', '')
                status = data.get('status', '')
                remark = data.get('remark', '')
                
                if tracking_num:
                    all_numbers.append({
                        'number': tracking_num,
                        'company': company_name,
                        'status': status,
                        'remark': remark,
                        'category': widget.category_name
                    })
        
        if not all_numbers:
            self.status_bar.showMessage("✅ 没有可导出的快递单号", 3000)
            return
        
        # 弹出选择对话框
        dialog = BatchExportDialog(all_numbers, self)
        if dialog.exec() != QDialog.Accepted:
            return
        
        selected_numbers = dialog.get_selected_numbers()
        export_format = dialog.get_export_format()
        
        if not selected_numbers:
            self.status_bar.showMessage("✅ 未选择任何快递单号", 3000)
            return
        
        # 根据格式导出
        if export_format == 'txt':
            self.export_numbers_as_txt(selected_numbers)
        elif export_format == 'csv':
            self.export_numbers_as_csv(selected_numbers)
        elif export_format == 'json':
            self.export_numbers_as_json(selected_numbers)


    def export_numbers_as_txt(self, numbers: List[Dict]):
        """导出为纯文本格式"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出快递单号", 
            f"express_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in numbers:
                    f.write(f"{item['number']}\n")
            
            self.status_bar.showMessage(f"✅ 已导出 {len(numbers)} 个快递单号", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"❌ 导出失败：{str(e)}", 3000)
    
    def export_numbers_as_csv(self, numbers: List[Dict]):
        """导出为CSV格式"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出快递单号", 
            f"express_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["快递单号", "快递公司", "当前状态", "备注", "分类"])
                
                for item in numbers:
                    writer.writerow([
                        item['number'],
                        item['company'],
                        item['status'],
                        item['remark'],
                        item['category']
                    ])
            
            self.status_bar.showMessage(f"✅ 已导出 {len(numbers)} 个快递单号", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"❌ 导出失败：{str(e)}", 3000)
    
    def export_numbers_as_json(self, numbers: List[Dict]):
        """导出为JSON格式"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出快递单号", 
            f"express_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            export_data = {
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_count': len(numbers),
                'numbers': numbers
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.status_bar.showMessage(f"✅ 已导出 {len(numbers)} 个快递单号", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"❌ 导出失败：{str(e)}", 3000)

    def clear_global_search(self):
        """清空全局搜索框并恢复显示"""
        self.global_search.clear()
        self.clear_summary_filter()
        self.status_bar.showMessage("已清除搜索", 2000)

    def scroll_to_item(self, category_widget, item_widget):
        """滚动到指定的快递条目"""
        # 获取快递汇总标签页中的滚动区域
        scroll_area = self.summary_tab.findChild(QScrollArea)
        if not scroll_area:
            print("[调试] 未找到 QScrollArea")
            return
        
        # 获取滚动区域内部的 widget
        scroll_content = scroll_area.widget()
        if not scroll_content:
            print("[调试] 未找到 scroll_content")
            return
        
        # 确保 item_widget 是可见的
        if not item_widget.isVisible():
            print("[调试] item_widget 不可见")
        
        # 计算 item_widget 相对于 scroll_content 的位置
        item_pos = item_widget.mapTo(scroll_content, item_widget.rect().topLeft())
        
        print(f"[调试] item_pos.y() = {item_pos.y()}")
        print(f"[调试] scroll_area.height() = {scroll_area.height()}")
        print(f"[调试] current_value = {scroll_area.verticalScrollBar().value()}")
        print(f"[调试] maximum = {scroll_area.verticalScrollBar().maximum()}")
        
        # 获取当前滚动条位置
        current_value = scroll_area.verticalScrollBar().value()
        
        # 计算目标滚动位置
        target_value = item_pos.y() - scroll_area.height() // 3
        target_value = max(0, min(target_value, scroll_area.verticalScrollBar().maximum()))
        
        print(f"[调试] target_value = {target_value}")
        
        if target_value == current_value:
            print("[调试] 目标位置与当前位置相同，无需滚动")
            return
        
        # 动画滚动效果
        self.animate_scroll(scroll_area.verticalScrollBar(), current_value, target_value)

    def animate_scroll(self, scroll_bar, start_value, end_value, duration=300):
        """动画滚动效果"""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        animation = QPropertyAnimation(scroll_bar, b"value")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        
        # 保存动画引用，防止被垃圾回收
        if not hasattr(self, '_scroll_animations'):
            self._scroll_animations = []
        
        # 清理已完成的动画
        self._scroll_animations = [a for a in self._scroll_animations if a.state() == QPropertyAnimation.Running]
        self._scroll_animations.append(animation)

    def refresh_api_endpoint(self):
        """刷新API接口显示（供设置对话框调用）"""
        if hasattr(self, 'api_endpoint_manager'):
            endpoint = self.api_endpoint_manager.get_current_endpoint()
            if endpoint:
                endpoint_type = endpoint.get('endpoint_type', 'unknown')
                if endpoint_type == 'free':
                    self.status_bar.showMessage("✅ 当前使用免费接口，无需API账号", 3000)
                elif endpoint_type == 'paid':
                    self.status_bar.showMessage("✅ 当前使用收费接口", 3000)
                else:
                    self.status_bar.showMessage(f"✅ 当前使用{endpoint.get('name', '自定义接口')}", 3000)
            self.update_api_account_display()
            self.update_api_endpoint_display()  

    def update_api_endpoint_display(self):
        """更新API接口状态显示"""
        if hasattr(self, 'api_endpoint_manager') and self.api_endpoint_manager:
            endpoint = self.api_endpoint_manager.get_current_endpoint()
            if endpoint:
                endpoint_type = endpoint.get('endpoint_type', 'unknown')
                endpoint_name = endpoint.get('name', '未知接口')
                
                # 根据接口类型设置不同的显示样式
                if endpoint_type == 'free':
                    self.api_endpoint_status.setText(f"🆓 免费接口")
                    self.api_endpoint_status.setStyleSheet("""
                        font-weight: bold;
                        padding: 2px 8px;
                        border-radius: 12px;
                        margin: 0 5px;
                        background-color: #E8F5E9;
                        color: #2E7D32;
                    """)
                    self.api_endpoint_status.setToolTip(f"当前使用：{endpoint_name}\n免费接口无需API账号，但有频率限制")
                elif endpoint_type == 'paid':
                    self.api_endpoint_status.setText(f"💰 收费接口")
                    self.api_endpoint_status.setStyleSheet("""
                        font-weight: bold;
                        padding: 2px 8px;
                        border-radius: 12px;
                        margin: 0 5px;
                        background-color: #FFF3E0;
                        color: #E65100;
                    """)
                    self.api_endpoint_status.setToolTip(f"当前使用：{endpoint_name}\n收费接口需要配置API账号，稳定性高")
                else:
                    self.api_endpoint_status.setText(f"🔧 自定义接口")
                    self.api_endpoint_status.setStyleSheet("""
                        font-weight: bold;
                        padding: 2px 8px;
                        border-radius: 12px;
                        margin: 0 5px;
                        background-color: #E3F2FD;
                        color: #1565C0;
                    """)
                    self.api_endpoint_status.setToolTip(f"当前使用：{endpoint_name}\n自定义API接口")
            else:
                self.api_endpoint_status.setText("❓ 无接口")
                self.api_endpoint_status.setStyleSheet("""
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 12px;
                    margin: 0 5px;
                    background-color: #FFEBEE;
                    color: #C62828;
                """)
                self.api_endpoint_status.setToolTip("未配置API接口，请检查设置")

    def update_proxy_settings(self):
        """更新代理设置（供设置对话框调用）"""
        self.load_proxy_settings()
        
        # 通知所有已打开的详情对话框重新加载地图（应用新代理）
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, ExpressDetailDialog):
                widget.refresh_map()
        
        self.status_bar.showMessage("✅ 代理设置已更新", 2000)

    def setup_dest_address_tab(self):
        """设置收件地址管理标签页"""
        layout = QVBoxLayout(self.dest_address_tab)
        layout.setSpacing(10)
        
        # 初始化地址管理器
        self.dest_address_manager = DestAddressManager(self.current_user_db, self)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 当前默认地址显示
        self.current_default_label = QLabel()
        self.update_default_address_display()
        toolbar.addWidget(self.current_default_label)
        
        toolbar.addStretch()
        
        # 从历史站点导入按钮
        import_sites_btn = QPushButton("📍 从历史站点导入")
        import_sites_btn.setToolTip("从已签收快递的物流轨迹中提取站点，添加到地址列表")
        import_sites_btn.clicked.connect(self.import_sites_from_history)
        import_sites_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PURPLE_WISTERIA.name()};
            }}
        """)
        toolbar.addWidget(import_sites_btn)
        
        # 添加自定义地址按钮
        add_custom_btn = QPushButton("✏️ 添加自定义地址")
        add_custom_btn.clicked.connect(self.add_custom_dest_address)
        add_custom_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_SKY.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        toolbar.addWidget(add_custom_btn)
        
        layout.addLayout(toolbar)
        
        # 说明信息
        info_label = QLabel(
            "💡 说明：设置收件地址后，未单独设置收件地址的快递将自动使用默认地址进行送达时间预估。\n"
            "   可以添加多个地址，设置其中一个为默认。站点列表从历史快递的物流轨迹中自动收集。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; padding: 5px; background-color: {MacaronColors.NEUTRAL_CREAM.name()}; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # 地址列表
        list_group = QGroupBox("收件地址列表")
        list_layout = QVBoxLayout()
        
        self.dest_table = QTableWidget()
        self.dest_table.setColumnCount(6)
        self.dest_table.setHorizontalHeaderLabels(["默认", "名称", "地址", "类型", "添加时间", "操作"])
        self.dest_table.horizontalHeader().setStretchLastSection(True)
        self.dest_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dest_table.setAlternatingRowColors(True)
        self.dest_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置列宽
        self.dest_table.setColumnWidth(0, 60)
        self.dest_table.setColumnWidth(1, 120)
        self.dest_table.setColumnWidth(2, 250)
        self.dest_table.setColumnWidth(3, 80)
        self.dest_table.setColumnWidth(4, 150)
        
        list_layout.addWidget(self.dest_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 快捷操作按钮
        quick_layout = QHBoxLayout()
        
        apply_to_all_btn = QPushButton("📌 应用到所有未设置的快递")
        apply_to_all_btn.setToolTip("将默认地址应用到所有未设置收件地址的快递")
        apply_to_all_btn.clicked.connect(self.apply_default_to_all)
        apply_to_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.ORANGE_PEACH.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.ORANGE_APRICOT.name()};
            }}
        """)
        quick_layout.addWidget(apply_to_all_btn)
        
        quick_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新列表")
        refresh_btn.clicked.connect(self.refresh_dest_table)
        quick_layout.addWidget(refresh_btn)
        
        layout.addLayout(quick_layout)
        
        # 加载数据
        self.refresh_dest_table()

    def update_default_address_display(self):
        """更新默认地址显示"""
        if hasattr(self, 'dest_address_manager'):
            default = self.dest_address_manager.get_default_address()
            if default:
                self.current_default_label.setText(
                    f"📮 当前默认地址: {default.get('name', '')} - {default.get('address', '')[:30]}..."
                )
                self.current_default_label.setStyleSheet(f"color: {MacaronColors.TEXT_DARK.name()}; font-weight: bold;")
            else:
                self.current_default_label.setText("⚠️ 未设置默认收件地址")
                self.current_default_label.setStyleSheet(f"color: {MacaronColors.RED_CORAL.name()};")

    def refresh_dest_table(self):
        """刷新地址表格"""
        if not hasattr(self, 'dest_address_manager'):
            return
        
        addresses = self.dest_address_manager.get_all_addresses()
        self.dest_table.setRowCount(len(addresses))
        
        type_names = {
            'custom': '自定义',
            'site': '历史站点',
        }
        
        for row, addr in enumerate(addresses):
            # 默认标记
            is_default = addr.get('is_default', 0) == 1
            default_item = QTableWidgetItem("✅ 默认" if is_default else "")
            if is_default:
                default_item.setForeground(QColor(0, 150, 0))
            self.dest_table.setItem(row, 0, default_item)
            
            # 名称
            self.dest_table.setItem(row, 1, QTableWidgetItem(addr.get('name', '')))
            
            # 地址
            address = addr.get('address', '')
            display_address = address[:40] + '...' if len(address) > 40 else address
            self.dest_table.setItem(row, 2, QTableWidgetItem(display_address))
            
            # 类型
            addr_type = addr.get('address_type', 'custom')
            type_item = QTableWidgetItem(type_names.get(addr_type, addr_type))
            if addr_type == 'site':
                type_item.setForeground(QColor(100, 100, 200))
            self.dest_table.setItem(row, 3, type_item)
            
            # 添加时间
            created_at = addr.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    created_at = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            self.dest_table.setItem(row, 4, QTableWidgetItem(created_at))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)
            
            addr_id = addr['id']
            
            if not is_default:
                set_default_btn = QPushButton("设为默认")
                set_default_btn.setToolTip("将此地址设为默认收件地址")
                set_default_btn.clicked.connect(lambda checked, aid=addr_id: self.set_default_dest_address(aid))
                btn_layout.addWidget(set_default_btn)
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, a=addr: self.edit_dest_address(a))
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, aid=addr_id: self.delete_dest_address(aid))
            btn_layout.addWidget(delete_btn)
            
            if row > 0:
                up_btn = QPushButton("↑")
                up_btn.setToolTip("上移")
                up_btn.setFixedWidth(25)
                up_btn.clicked.connect(lambda checked, aid=addr_id: self.move_dest_address_up(aid))
                btn_layout.addWidget(up_btn)
            
            if row < len(addresses) - 1:
                down_btn = QPushButton("↓")
                down_btn.setToolTip("下移")
                down_btn.setFixedWidth(25)
                down_btn.clicked.connect(lambda checked, aid=addr_id: self.move_dest_address_down(aid))
                btn_layout.addWidget(down_btn)
            
            btn_widget.setLayout(btn_layout)
            self.dest_table.setCellWidget(row, 5, btn_widget)
        
        self.update_default_address_display()

    def import_sites_from_history(self):
        """从历史站点导入"""
        # 显示进度
        self.status_bar.showMessage("正在收集历史站点...")
        QApplication.processEvents()
        
        sites = self.dest_address_manager.collect_sites_from_history()
        
        if not sites:
            QMessageBox.information(self, "提示", "未找到任何历史站点数据")
            self.status_bar.showMessage("就绪", 2000)
            return
        
        # 获取已有地址
        existing_addresses = set()
        for addr in self.dest_address_manager.get_all_addresses():
            existing_addresses.add(addr.get('address', ''))
        
        # 过滤出新站点
        new_sites = [s for s in sites if s not in existing_addresses]
        
        if not new_sites:
            QMessageBox.information(self, "提示", f"共找到 {len(sites)} 个站点，但都已存在于地址列表中")
            self.status_bar.showMessage("就绪", 2000)
            return
        
        # 显示选择对话框
        dialog = SiteImportDialog(new_sites, self)
        if dialog.exec() != QDialog.Accepted:
            self.status_bar.showMessage("就绪", 2000)
            return
        
        selected_sites = dialog.get_selected_sites()
        
        if not selected_sites:
            self.status_bar.showMessage("就绪", 2000)
            return
        
        # 导入选中的站点
        imported = 0
        for site in selected_sites:
            # 生成名称（取站点前20个字符）
            name = site[:20] + ('...' if len(site) > 20 else '')
            if self.dest_address_manager.add_address(name, site, 'site'):
                imported += 1
        
        self.refresh_dest_table()
        self.status_bar.showMessage(f"✅ 已导入 {imported} 个站点", 3000)

    def add_custom_dest_address(self):
        """添加自定义地址"""
        dialog = DestAddressEditDialog(self, None)
        if dialog.exec() == QDialog.Accepted:
            name, address = dialog.get_data()
            if self.dest_address_manager.add_address(name, address, 'custom'):
                self.refresh_dest_table()
                self.status_bar.showMessage(f"✅ 已添加地址: {name}", 2000)

    def edit_dest_address(self, addr: Dict):
        """编辑地址"""
        dialog = DestAddressEditDialog(self, addr)
        if dialog.exec() == QDialog.Accepted:
            name, address = dialog.get_data()
            if self.dest_address_manager.update_address(addr['id'], name, address):
                self.refresh_dest_table()
                self.status_bar.showMessage(f"✅ 已更新地址: {name}", 2000)

    def delete_dest_address(self, addr_id: int):
        """删除地址"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除此收件地址吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.dest_address_manager.delete_address(addr_id):
                self.refresh_dest_table()
                self.status_bar.showMessage("✅ 地址已删除", 2000)

    def set_default_dest_address(self, addr_id: int):
        """设为默认地址"""
        if self.dest_address_manager.set_default(addr_id):
            self.refresh_dest_table()
            self.status_bar.showMessage("✅ 已设为默认收件地址", 2000)

    def move_dest_address_up(self, addr_id: int):
        """上移地址"""
        if self.dest_address_manager.move_up(addr_id):
            self.refresh_dest_table()

    def move_dest_address_down(self, addr_id: int):
        """下移地址"""
        if self.dest_address_manager.move_down(addr_id):
            self.refresh_dest_table()

    def apply_default_to_all(self):
        """将默认地址应用到所有未设置的快递"""
        default = self.dest_address_manager.get_default_address()
        if not default:
            QMessageBox.warning(self, "提示", "请先设置默认收件地址")
            return
        
        reply = QMessageBox.question(
            self, "确认应用",
            f"确定要将默认地址应用到所有未设置收件地址的快递吗？\n\n"
            f"默认地址: {default.get('name')} - {default.get('address')}\n\n"
            f"此操作将更新所有 dest_address 为空的快递记录。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        sql = """
        UPDATE express_summary 
        SET dest_address = ?, last_update = ?
        WHERE (dest_address IS NULL OR dest_address = '') AND is_deleted = 0
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if self.current_user_db:
            self.current_user_db.execute_update(sql, (default['address'], current_time))
            self.load_summary_data()
            self.status_bar.showMessage("✅ 已将默认地址应用到所有未设置的快递", 3000)

    def _should_switch_account_on_error(self, error_msg: str) -> bool:
        """判断错误信息是否需要切换账号"""
        if not error_msg:
            return False
        
        error_lower = error_msg.lower()
        
        # 需要切换账号的错误特征
        switch_keywords = [
            # 额度相关
            '额度已用完', 'quota exceeded', 'rate limit', '频率限制',
            '今日次数已用完', '超过限制', '请求过于频繁', 'daily limit',
            'too many requests', '请求次数超限',
            # 权限/认证相关
            '没该功能权限', '无权限', '认证失败', 'auth failed',
            'key invalid', 'customer invalid', '签名错误', 'sign error',
            '账号过期', 'account expired', '未开通', 'no permission',
            '权限不足', 'insufficient permissions',
        ]
        
        for keyword in switch_keywords:
            if keyword in error_lower:
                return True
        
        # 检查当前账号是否确实额度用完
        if self.api_account_manager:
            if not self.api_account_manager.is_current_account_available():
                return True
        
        return False


    def _try_switch_and_retry(self, tracking_num: str, company_code: str = "", 
                            error_msg: str = "") -> bool:
        """
        尝试切换账号并询问是否重试
        返回 True 表示已发起重试，False 表示不重试
        """
        if not self._should_switch_account_on_error(error_msg):
            return False
        
        if not self.api_account_manager:
            return False
        
        old_account = self.api_account_manager.current_account
        old_account_id = old_account.get('id') if old_account else None
        
        if not self.api_account_manager.switch_to_next_account(force_switch=True):
            return False
        
        new_account = self.api_account_manager.current_account
        new_account_id = new_account.get('id') if new_account else None
        
        if old_account_id == new_account_id:
            return False
        
        if not self.load_current_api_account():
            self.status_bar.showMessage(f"切换账号失败", 3000)
            return False
        
        self.update_api_account_display()
        
        return True

    def update_single_express_item(self, tracking_num: str, data: dict):
        """更新单个快递条目（不重建整个列表）"""
        if not self.user_manager.current_user_db:
            return
        
        # 更新数据库
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
        
        # 获取旧的分类
        old_category = None
        sql_old = "SELECT status_category FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
        old_result = self.user_manager.current_user_db.execute_query(sql_old, (tracking_num,))
        if old_result:
            old_category = old_result[0].get('status_category', '')
        
        # 更新数据库
        sql = """
        UPDATE express_summary 
        SET status = ?, status_category = ?, latest_track = ?, 
            result_data = ?, last_update = ?
        WHERE tracking_number = ? AND is_deleted = 0
        """
        self.user_manager.current_user_db.execute_update(
            sql,
            (state_text, category, latest_track, 
            json.dumps(data, ensure_ascii=False), current_time, tracking_num)
        )
        
        # 记录时效数据
        if self.delivery_estimator:
            context = latest_context
            should_record = (state == '3' or 
                            self.delivery_estimator.is_signed(context) or 
                            self.delivery_estimator.is_arrived_at_station(context))
            if should_record:
                self.delivery_estimator.record_delivery(data)
        
        # 记录节点运输时间
        if self.node_analyzer and track_list:
            self.node_analyzer.record_node_transit(data)
        
        # ========== 更新界面：只更新对应的条目 ==========
        if old_category and old_category != category:
            # 分类变了，需要从旧分类移除，添加到新分类
            if old_category in self.category_widgets:
                for item in self.category_widgets[old_category].express_items[:]:
                    if item.express_data.get('tracking_number', '') == tracking_num:
                        self.category_widgets[old_category].remove_express_item(item)
                        break
            
            # 需要新的 express_data 来创建或移动条目
            # 从数据库获取最新数据
            sql_new = "SELECT * FROM express_summary WHERE tracking_number = ? AND is_deleted = 0"
            new_record = self.user_manager.current_user_db.execute_query(sql_new, (tracking_num,))
            if new_record:
                self.add_express_to_category(new_record[0])
        else:
            # 分类没变，只更新条目内容
            target_category = category if category in self.category_widgets else 'other'
            widget = self.category_widgets[target_category]
            
            found = False
            for item in widget.express_items:
                if item.express_data.get('tracking_number', '') == tracking_num:
                    item.update_from_data(data)
                    found = True
                    break
            
            # 如果没找到（可能在过滤中被隐藏了），则重新加载汇总
            if not found:
                self.load_summary_data()
        
        # 更新分类计数
        for w in self.category_widgets.values():
            w.update_count()



class SettingsDialogPro(QDialog):
    """设置对话框 - 多标签页版本"""
    
    def __init__(self, parent: ExpressQueryProGUI):
        super().__init__(parent)
        self.parent = parent
        # ===== 设置实时自动保存（防抖 400ms） =====
        self._loading = True  # 加载标志：加载/恢复设置期间不触发自动保存
        self._settings_save_timer = QTimer(self)
        self._settings_save_timer.setSingleShot(True)
        self._settings_save_timer.setInterval(400)
        self._settings_save_timer.timeout.connect(self._save_settings_now)
        self.init_ui()
        self._loading = False
        self._connect_autosave()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        """初始化UI - 多标签页版本"""
        self.setWindowTitle("系统设置")
        self.setMinimumSize(600, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        
        # ========== 标签页1：API账号管理 ==========
        self.account_tab = QWidget()
        self.setup_account_tab()
        self.tab_widget.addTab(self.account_tab, "🔑 API账号")
        
        # ========== 标签页2：数据管理 ==========
        self.data_tab = QWidget()
        self.setup_data_tab()
        self.tab_widget.addTab(self.data_tab, "📊 数据管理")
        
        # ========== 标签页3：备份设置 ==========
        self.backup_tab = QWidget()
        self.setup_backup_tab()
        self.tab_widget.addTab(self.backup_tab, "💾 备份设置")
        
        # ========== 标签页4：高级设置 ==========
        self.advanced_tab = QWidget()
        self.setup_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "⚙️ 高级")
        
        # ========== 标签页5：API接口 ==========
        self.api_endpoint_tab = QWidget()
        self.setup_api_endpoint_tab()
        self.tab_widget.addTab(self.api_endpoint_tab, "🌐 API接口")
    
        # ========== 标签页6：代理设置 ==========
        self.proxy_tab = QWidget()
        self.setup_proxy_tab()
        self.tab_widget.addTab(self.proxy_tab, "🔀 代理")

        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
            }}
        """)
        btn_layout.addWidget(save_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 加载各标签页的数据
        self.load_all_stats()
        
    def setup_account_tab(self):
        """设置API账号管理标签页"""
        layout = QVBoxLayout(self.account_tab)
        layout.setSpacing(15)
        
        # 说明信息
        info_label = QLabel("管理多个API账号，支持额度用完自动切换")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; padding: 5px;")
        layout.addWidget(info_label)
        
        # 当前账号信息
        current_group = QGroupBox("当前使用账号")
        current_layout = QVBoxLayout()
        
        self.current_account_label = QLabel("加载中...")
        self.current_account_label.setStyleSheet("font-weight: bold; padding: 5px;")
        current_layout.addWidget(self.current_account_label)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # 管理按钮
        manage_layout = QHBoxLayout()
        
        manage_account_btn = QPushButton("管理API账号")
        manage_account_btn.setToolTip("添加、编辑、删除API账号，设置自动切换")
        manage_account_btn.clicked.connect(self.manage_accounts)
        manage_account_btn.setMinimumHeight(40)
        manage_account_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_SKY.name()};
            }}
        """)
        manage_layout.addWidget(manage_account_btn)
        
        layout.addLayout(manage_layout)
        
        # 快速操作
        quick_group = QGroupBox("快速操作")
        quick_layout = QVBoxLayout()
        
        refresh_account_btn = QPushButton("🔄 刷新账号信息")
        refresh_account_btn.setToolTip("刷新API账号的使用情况和配额信息")
        refresh_account_btn.clicked.connect(self.refresh_account_info)
        quick_layout.addWidget(refresh_account_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        
    def setup_data_tab(self):
        """设置数据管理标签页"""
        layout = QVBoxLayout(self.data_tab)
        layout.setSpacing(15)
        
        # 时效数据管理
        delivery_group = QGroupBox("时效数据管理")
        delivery_layout = QVBoxLayout()
        
        delivery_info_label = QLabel("基于历史签收数据预估送达时间")
        delivery_info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()};")
        delivery_layout.addWidget(delivery_info_label)
        
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("加载中...")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        delivery_layout.addLayout(stats_layout)
        
        btn_layout1 = QHBoxLayout()
        
        clear_history_btn = QPushButton("清空时效历史数据")
        clear_history_btn.setToolTip("清空所有已记录的时效数据，清空后预估功能将使用默认值")
        clear_history_btn.clicked.connect(self.clear_delivery_history)
        clear_history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.ORANGE_PEACH.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.ORANGE_APRICOT.name()};
            }}
        """)
        btn_layout1.addWidget(clear_history_btn)
        btn_layout1.addStretch()
        delivery_layout.addLayout(btn_layout1)
        
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)
        
        # 节点历史数据管理
        node_group = QGroupBox("节点运输历史数据")
        node_layout = QVBoxLayout()
        
        node_info_label = QLabel("基于历史节点运输数据预估各路段耗时")
        node_info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()};")
        node_layout.addWidget(node_info_label)
        
        node_stats_layout = QHBoxLayout()
        self.node_stats_label = QLabel("加载中...")
        node_stats_layout.addWidget(self.node_stats_label)
        node_stats_layout.addStretch()
        node_layout.addLayout(node_stats_layout)
        
        btn_layout2 = QHBoxLayout()
        
        clear_node_btn = QPushButton("清空节点历史数据")
        clear_node_btn.setToolTip("清空所有已记录的节点运输数据，清空后节点时间预估将使用默认值")
        clear_node_btn.clicked.connect(self.clear_node_history)
        clear_node_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.ORANGE_PEACH.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.ORANGE_APRICOT.name()};
            }}
        """)
        btn_layout2.addWidget(clear_node_btn)
        btn_layout2.addStretch()
        node_layout.addLayout(btn_layout2)
        
        node_group.setLayout(node_layout)
        layout.addWidget(node_group)
        
        # 数据统计摘要
        summary_group = QGroupBox("数据统计摘要")
        summary_layout = QGridLayout()
        
        summary_layout.addWidget(QLabel("时效数据记录数:"), 0, 0)
        self.delivery_count_label = QLabel("0")
        self.delivery_count_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.delivery_count_label, 0, 1)
        
        summary_layout.addWidget(QLabel("节点数据记录数:"), 1, 0)
        self.node_count_label = QLabel("0")
        self.node_count_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.node_count_label, 1, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        layout.addStretch()
        
    def setup_backup_tab(self):
        """设置备份设置标签页"""
        layout = QVBoxLayout(self.backup_tab)
        layout.setSpacing(15)
        
        # 备份保留设置
        retention_group = QGroupBox("备份保留设置")
        retention_layout = QVBoxLayout()
        
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大备份数量:"))
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        self.max_backups_spin.setValue(self.parent.backup_manager.max_backups)
        self.max_backups_spin.setSuffix(" 个")
        self.max_backups_spin.setToolTip("超过此数量的旧备份将自动删除")
        max_layout.addWidget(self.max_backups_spin)
        max_layout.addStretch()
        retention_layout.addLayout(max_layout)
        
        info_label = QLabel("说明: 超过最大数量的旧备份将自动删除")
        info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px;")
        retention_layout.addWidget(info_label)
        
        retention_group.setLayout(retention_layout)
        layout.addWidget(retention_group)
        
        # 自动备份设置
        auto_group = QGroupBox("自动备份")
        auto_layout = QVBoxLayout()
        
        self.auto_backup_check = QCheckBox("启用自动备份（每小时）")
        self.auto_backup_check.setChecked(self.parent.backup_timer.isActive())
        self.auto_backup_check.setToolTip("每小时自动创建一次数据库备份")
        auto_layout.addWidget(self.auto_backup_check)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # 备份存储位置
        location_group = QGroupBox("备份存储位置")
        location_layout = QVBoxLayout()
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("备份目录:"))
        self.dir_label = QLabel(str(self.parent.backup_manager.backup_dir))
        self.dir_label.setStyleSheet(f"color: {MacaronColors.TEXT_DARK.name()};")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        location_layout.addLayout(dir_layout)
        
        open_dir_btn = QPushButton("📁 打开备份目录")
        open_dir_btn.clicked.connect(self.open_backup_dir)
        location_layout.addWidget(open_dir_btn)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # 快速操作
        quick_group = QGroupBox("快速操作")
        quick_layout = QHBoxLayout()
        
        backup_now_btn = QPushButton("💾 立即备份")
        backup_now_btn.setToolTip("立即创建一个手动备份")
        backup_now_btn.clicked.connect(self.create_manual_backup)
        quick_layout.addWidget(backup_now_btn)
        
        manage_backup_btn = QPushButton("📋 备份管理")
        manage_backup_btn.setToolTip("打开备份管理对话框，查看和恢复备份")
        manage_backup_btn.clicked.connect(self.show_backup_dialog)
        quick_layout.addWidget(manage_backup_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        
    def setup_advanced_tab(self):
        """设置高级设置标签页"""
        layout = QVBoxLayout(self.advanced_tab)
        layout.setSpacing(15)
        
        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QVBoxLayout()
        
        self.debug_check = QCheckBox("启用调试模式")
        self.debug_check.setChecked(DEBUG_MODE)
        self.debug_check.setToolTip("启用后将在控制台输出详细的调试信息")
        debug_layout.addWidget(self.debug_check)
        
        debug_info = QLabel("调试模式会输出详细日志，建议仅在排查问题时启用。")
        debug_info.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px;")
        debug_layout.addWidget(debug_info)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
    
        # ========== 新增：默认收件地址设置 ==========
        dest_group = QGroupBox("默认收件地址")
        dest_layout = QVBoxLayout()
        
        dest_info = QLabel("设置默认收件地址后，新添加的快递会自动使用此地址进行送达时间预估")
        dest_info.setWordWrap(True)
        dest_info.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px; padding: 5px;")
        dest_layout.addWidget(dest_info)
        
        dest_input_layout = QHBoxLayout()
        dest_input_layout.addWidget(QLabel("默认地址:"))
        
        self.default_dest_edit = QLineEdit()
        self.default_dest_edit.setPlaceholderText("例如：北京市朝阳区 或 北京转运中心")
        self.default_dest_edit.setToolTip("输入您的常用收件地址，新添加快递时会自动关联")
        dest_input_layout.addWidget(self.default_dest_edit)
        
        # 添加清除按钮
        clear_dest_btn = QPushButton("清除")
        clear_dest_btn.setToolTip("清除默认收件地址")
        clear_dest_btn.clicked.connect(lambda: self.default_dest_edit.clear())
        dest_input_layout.addWidget(clear_dest_btn)
        
        dest_layout.addLayout(dest_input_layout)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
    
        # 界面设置
        ui_group = QGroupBox("界面设置")
        ui_layout = QVBoxLayout()
        
        # 窗口重置按钮
        reset_window_btn = QPushButton("📐 重置窗口大小")
        reset_window_btn.setToolTip("将主窗口大小恢复为默认值")
        reset_window_btn.clicked.connect(self.reset_main_window_size)
        ui_layout.addWidget(reset_window_btn)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # 系统信息
        info_group = QGroupBox("系统信息")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("程序版本:"), 0, 0)
        version_label = QLabel(ProjectInfo.VERSION)
        version_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(version_label, 0, 1)
        
        info_layout.addWidget(QLabel("构建日期:"), 1, 0)
        build_label = QLabel(ProjectInfo.BUILD_DATE)
        build_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(build_label, 1, 1)
        
        info_layout.addWidget(QLabel("数据目录:"), 2, 0)
        data_dir_label = QLabel(str(self.parent.app_data_dir))
        data_dir_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 10px;")
        data_dir_label.setWordWrap(True)
        info_layout.addWidget(data_dir_label, 2, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
    
        # 加载已保存的设置
        default_dest = self.parent.user_manager.get_user_setting("default_dest_address", "")
        self.default_dest_edit.setText(default_dest)

    def setup_api_endpoint_tab(self):
        """设置API接口标签页"""
        layout = QVBoxLayout(self.api_endpoint_tab)
        layout.setSpacing(15)
        
        # 当前接口信息
        current_group = QGroupBox("当前使用的API接口")
        current_layout = QVBoxLayout()
        
        self.current_endpoint_label = QLabel("加载中...")
        self.current_endpoint_label.setWordWrap(True)
        self.current_endpoint_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f0f8ff; border-radius: 5px;")
        current_layout.addWidget(self.current_endpoint_label)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # 接口选择
        select_group = QGroupBox("切换API接口")
        select_layout = QVBoxLayout()
        
        select_info = QLabel("选择要使用的API接口类型：")
        select_layout.addWidget(select_info)
        
        # 接口选择按钮组
        self.endpoint_buttons = QWidget()
        endpoint_btn_layout = QHBoxLayout(self.endpoint_buttons)
        
        self.use_paid_btn = QPushButton("💰 收费接口")
        self.use_paid_btn.setToolTip("使用快递100收费接口，需要配置Customer和Auth Key")
        self.use_paid_btn.clicked.connect(lambda: self.switch_to_paid_endpoint())
        endpoint_btn_layout.addWidget(self.use_paid_btn)
        
        self.use_free_btn = QPushButton("🆓 免费接口")
        self.use_free_btn.setToolTip("使用快递100免费接口，无需认证，但有频率限制")
        self.use_free_btn.clicked.connect(lambda: self.switch_to_free_endpoint())
        endpoint_btn_layout.addWidget(self.use_free_btn)
        
        endpoint_btn_layout.addStretch()
        
        select_layout.addWidget(self.endpoint_buttons)
        
        # 说明信息
        info_text = QLabel(
            "💡 接口说明：\n"
            "• 收费接口：需要配置API账号（Customer和Auth Key），稳定性高，支持自动切换账号\n"
            "• 免费接口：无需配置，直接使用快递100官方免费查询接口，适合少量查询（每天约50-100次）\n"
            "• 自定义接口：可添加其他快递查询API"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px; padding: 5px;")
        select_layout.addWidget(info_text)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # 管理按钮
        manage_group = QGroupBox("高级管理")
        manage_layout = QHBoxLayout()
        
        manage_endpoints_btn = QPushButton("📋 管理所有接口")
        manage_endpoints_btn.setToolTip("添加、编辑、删除自定义API接口")
        manage_endpoints_btn.clicked.connect(self.manage_endpoints)
        manage_layout.addWidget(manage_endpoints_btn)
        
        test_endpoint_btn = QPushButton("🔍 测试当前接口")
        test_endpoint_btn.setToolTip("测试当前API接口是否可用")
        test_endpoint_btn.clicked.connect(self.test_current_endpoint)
        manage_layout.addWidget(test_endpoint_btn)
        
        manage_layout.addStretch()
        
        manage_group.setLayout(manage_layout)
        layout.addWidget(manage_group)
        
        layout.addStretch()
        
        # 加载当前接口信息
        self.refresh_endpoint_display()

    def setup_proxy_tab(self):
        """设置代理标签页 - 简化版，高德直连，OSM走代理"""
        layout = QVBoxLayout(self.proxy_tab)
        layout.setSpacing(15)
        
        # 说明信息
        info_label = QLabel(
            "配置网络代理，用于访问需要代理的地图服务（如 OpenStreetMap）。\n"
            "💡 提示：高德地图无需代理，可直接使用。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; padding: 5px;")
        layout.addWidget(info_label)
        
        # 代理开关
        enable_group = QGroupBox("代理状态")
        enable_layout = QVBoxLayout()
        
        self.proxy_enable_check = QCheckBox("启用代理")
        self.proxy_enable_check.setToolTip("开启后，OpenStreetMap 等需要代理的地图服务将使用代理连接")
        enable_layout.addWidget(self.proxy_enable_check)
        
        enable_group.setLayout(enable_layout)
        layout.addWidget(enable_group)
        
        # 代理服务器设置
        server_group = QGroupBox("代理服务器设置")
        server_layout = QFormLayout()
        
        # 代理类型
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "SOCKS5"])
        self.proxy_type_combo.setToolTip("选择代理服务器类型")
        server_layout.addRow("代理类型:", self.proxy_type_combo)
        
        # 代理地址
        address_layout = QHBoxLayout()
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("127.0.0.1")
        self.proxy_host_edit.setText("127.0.0.1")
        address_layout.addWidget(self.proxy_host_edit)
        
        address_layout.addWidget(QLabel(":"))
        
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(20808)
        self.proxy_port_spin.setToolTip("代理端口")
        address_layout.addWidget(self.proxy_port_spin)
        
        address_layout.addStretch()
        server_layout.addRow("代理地址:", address_layout)
        
        # 用户名（可选）
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setPlaceholderText("可选，如需认证请填写")
        server_layout.addRow("用户名:", self.proxy_username_edit)
        
        # 密码（可选）
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setPlaceholderText("可选，如需认证请填写")
        self.proxy_password_edit.setEchoMode(QLineEdit.Password)
        server_layout.addRow("密码:", self.proxy_password_edit)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # 测试按钮
        test_layout = QHBoxLayout()
        
        self.test_proxy_btn = QPushButton("🔍 测试代理连接")
        self.test_proxy_btn.setToolTip("测试代理服务器是否可用")
        self.test_proxy_btn.clicked.connect(self.test_proxy_connection)
        test_layout.addWidget(self.test_proxy_btn)
        
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        
        # 状态提示
        self.proxy_status_label = QLabel("")
        self.proxy_status_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(self.proxy_status_label)
        
        layout.addStretch()
        
        # 加载当前代理设置
        self.load_proxy_settings()
        
        # 连接信号
        self.proxy_enable_check.stateChanged.connect(self.on_proxy_enable_changed)
        self.on_proxy_enable_changed()

    def on_proxy_enable_changed(self):
        """代理启用状态改变"""
        enabled = self.proxy_enable_check.isChecked()
        self.proxy_type_combo.setEnabled(enabled)
        self.proxy_host_edit.setEnabled(enabled)
        self.proxy_port_spin.setEnabled(enabled)
        self.proxy_username_edit.setEnabled(enabled)
        self.proxy_password_edit.setEnabled(enabled)
        self.test_proxy_btn.setEnabled(enabled)
        # 检查控件是否存在（兼容性）
        if hasattr(self, 'proxy_map_check'):
            self.proxy_map_check.setEnabled(enabled)
        if hasattr(self, 'proxy_api_check'):
            self.proxy_api_check.setEnabled(enabled)

    def load_proxy_settings(self):
        """加载代理设置"""
        if not self.parent.user_manager.current_user_db:
            return
        
        # 加载启用状态
        enabled = self.parent.user_manager.get_user_setting("proxy_enabled", "0")
        self.proxy_enable_check.setChecked(enabled == "1")
        
        # 加载代理类型
        proxy_type = self.parent.user_manager.get_user_setting("proxy_type", "HTTP")
        index = self.proxy_type_combo.findText(proxy_type)
        if index >= 0:
            self.proxy_type_combo.setCurrentIndex(index)
        
        # 加载代理地址
        host = self.parent.user_manager.get_user_setting("proxy_host", "127.0.0.1")
        self.proxy_host_edit.setText(host)
        
        port = self.parent.user_manager.get_user_setting("proxy_port", "20808")
        try:
            self.proxy_port_spin.setValue(int(port))
        except:
            self.proxy_port_spin.setValue(20808)
        
        # 加载用户名密码
        username = self.parent.user_manager.get_user_setting("proxy_username", "")
        self.proxy_username_edit.setText(username)
        
        password = self.parent.user_manager.get_user_setting("proxy_password", "")
        self.proxy_password_edit.setText(password)

    def save_proxy_settings(self):
        """保存代理设置"""
        if not self.parent.user_manager.current_user_db:
            return
        
        self.parent.user_manager.save_user_setting(
            "proxy_enabled", 
            "1" if self.proxy_enable_check.isChecked() else "0"
        )
        self.parent.user_manager.save_user_setting(
            "proxy_type", 
            self.proxy_type_combo.currentText()
        )
        self.parent.user_manager.save_user_setting(
            "proxy_host", 
            self.proxy_host_edit.text().strip()
        )
        self.parent.user_manager.save_user_setting(
            "proxy_port", 
            str(self.proxy_port_spin.value())
        )
        self.parent.user_manager.save_user_setting(
            "proxy_username", 
            self.proxy_username_edit.text().strip()
        )
        self.parent.user_manager.save_user_setting(
            "proxy_password", 
            self.proxy_password_edit.text().strip()
        )
        # 简化：地图始终使用代理设置，API不使用代理
        self.parent.user_manager.save_user_setting("proxy_for_map", "1")
        self.parent.user_manager.save_user_setting("proxy_for_api", "0")
        # 注：应用代理到主窗口（update_proxy_settings）由保存/关闭时统一调用，
        # 自动保存仅写库，避免频繁刷新地图造成卡顿

    def test_proxy_connection(self):
        """测试代理连接"""
        import requests
        
        proxy_type = self.proxy_type_combo.currentText().lower()
        host = self.proxy_host_edit.text().strip()
        port = self.proxy_port_spin.value()
        username = self.proxy_username_edit.text().strip()
        password = self.proxy_password_edit.text().strip()
        
        if not host:
            QMessageBox.warning(self, "提示", "请输入代理服务器地址")
            return
        
        # 构建代理URL
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        self.proxy_status_label.setText("正在测试代理连接...")
        self.proxy_status_label.setStyleSheet("color: #FF9800; font-size: 11px; padding: 5px;")
        
        # 在新线程中测试
        class ProxyTestThread(QThread):
            finished = Signal(bool, str)
            
            def __init__(self, proxies):
                super().__init__()
                self.proxies = proxies
            
            def run(self):
                try:
                    # 测试连接到 OpenStreetMap
                    response = requests.get(
                        "https://tile.openstreetmap.org/",
                        proxies=self.proxies,
                        timeout=10
                    )
                    if response.status_code == 200:
                        self.finished.emit(True, "代理连接成功！")
                    else:
                        self.finished.emit(False, f"代理连接失败：HTTP {response.status_code}")
                except requests.exceptions.ProxyError as e:
                    self.finished.emit(False, f"代理错误：无法连接到代理服务器")
                except requests.exceptions.ConnectTimeout:
                    self.finished.emit(False, "连接超时：代理服务器无响应")
                except Exception as e:
                    self.finished.emit(False, f"测试失败：{str(e)}")
        
        self.test_thread = ProxyTestThread(proxies)
        
        def on_test_finished(success, message):
            if success:
                self.proxy_status_label.setText(f"✅ {message}")
                self.proxy_status_label.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px;")
                QMessageBox.information(self, "测试成功", message)
            else:
                self.proxy_status_label.setText(f"❌ {message}")
                self.proxy_status_label.setStyleSheet("color: #F44336; font-size: 11px; padding: 5px;")
                QMessageBox.warning(self, "测试失败", message)
        
        self.test_thread.finished.connect(on_test_finished)
        self.test_thread.start()

    def refresh_endpoint_display(self):
        """刷新接口显示"""
        if hasattr(self.parent, 'api_endpoint_manager') and self.parent.api_endpoint_manager:
            endpoint = self.parent.api_endpoint_manager.get_current_endpoint()
            if endpoint:
                endpoint_type_name = self.parent.api_endpoint_manager.get_endpoint_type_name(
                    endpoint.get('endpoint_type', 'custom')
                )
                self.current_endpoint_label.setText(
                    f"📡 {endpoint.get('name')}\n"
                    f"   类型: {endpoint_type_name}\n"
                    f"   API地址: {endpoint.get('url')}\n"
                    f"   描述: {endpoint.get('description', '无')}"
                )
                
                # 更新按钮样式
                is_paid = endpoint.get('endpoint_type') == 'paid'
                is_free = endpoint.get('endpoint_type') == 'free'
                
                self.use_paid_btn.setStyleSheet(
                    f"background-color: {MacaronColors.GREEN_MINT.name()}; font-weight: bold;" if is_paid else ""
                )
                self.use_free_btn.setStyleSheet(
                    f"background-color: {MacaronColors.GREEN_MINT.name()}; font-weight: bold;" if is_free else ""
                )
    
    def switch_to_paid_endpoint(self):
        """切换到收费接口"""
        current = self.parent.api_endpoint_manager.get_current_endpoint()
        if current and current.get('endpoint_type') == 'paid':
            QMessageBox.information(self, "提示", "当前已经是收费接口")
            return
        
        # 查找收费接口
        endpoints = self.parent.api_endpoint_manager.get_all_endpoints()
        paid_endpoint = None
        for ep in endpoints:
            if ep.get('endpoint_type') == 'paid':
                paid_endpoint = ep
                break
        
        if paid_endpoint:
            reply = QMessageBox.question(
                self, "确认切换",
                f"确定要切换到收费接口吗？\n\n"
                f"收费接口需要配置有效的API账号（Customer和Auth Key）。\n"
                f"如果尚未配置，请在「API账号」标签页中添加账号。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.parent.api_endpoint_manager.set_current_endpoint(paid_endpoint['id']):
                    QMessageBox.information(self, "成功", "已切换到收费接口")
                    self.refresh_endpoint_display()
                    # 刷新主窗口的接口显示
                    if hasattr(self.parent, 'update_api_endpoint_display'):
                        self.parent.update_api_endpoint_display()
                    self.parent.status_bar.showMessage("✅ 已切换到收费接口，请确保已配置API账号", 5000)
                else:
                    QMessageBox.critical(self, "失败", "切换接口失败")
        else:
            QMessageBox.warning(self, "提示", "未找到收费接口配置，请检查数据库")
    
    def switch_to_free_endpoint(self):
        """切换到免费接口"""
        current = self.parent.api_endpoint_manager.get_current_endpoint()
        if current and current.get('endpoint_type') == 'free':
            QMessageBox.information(self, "提示", "当前已经是免费接口")
            return
        
        # 查找免费接口
        endpoints = self.parent.api_endpoint_manager.get_all_endpoints()
        free_endpoint = None
        for ep in endpoints:
            if ep.get('endpoint_type') == 'free':
                free_endpoint = ep
                break
        
        if free_endpoint:
            reply = QMessageBox.question(
                self, "确认切换",
                f"确定要切换到免费接口吗？\n\n"
                f"⚠️ 注意事项：\n"
                f"• 免费接口无需配置API账号\n"
                f"• 有频率限制，建议每天查询不超过50次\n"
                f"• 稳定性不如收费接口，可能出现查询失败\n"
                f"• 部分快递公司可能不支持\n\n"
                f"是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.parent.api_endpoint_manager.set_current_endpoint(free_endpoint['id']):
                    QMessageBox.information(self, "成功", "已切换到免费接口")
                    self.refresh_endpoint_display()
                    # 刷新主窗口的接口显示
                    if hasattr(self.parent, 'update_api_endpoint_display'):
                        self.parent.update_api_endpoint_display()
                    self.parent.status_bar.showMessage("✅ 已切换到免费接口，无需API账号即可查询", 5000)
                else:
                    QMessageBox.critical(self, "失败", "切换接口失败")
        else:
            QMessageBox.warning(self, "提示", "未找到免费接口配置，请检查数据库")
    
    def manage_endpoints(self):
        """管理所有接口"""
        dialog = ApiEndpointDialog(self.parent.api_endpoint_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_endpoint_display()
    
    def test_current_endpoint(self):
        """测试当前接口"""
        if not hasattr(self.parent, 'api_endpoint_manager'):
            QMessageBox.warning(self, "提示", "API接口管理器未初始化")
            return
        
        endpoint = self.parent.api_endpoint_manager.get_current_endpoint()
        if not endpoint:
            QMessageBox.warning(self, "提示", "未找到当前接口配置")
            return
        
        # 显示测试进度
        progress_dialog = QProgressDialog("正在测试API接口...", "取消", 0, 0, self)
        progress_dialog.setWindowTitle("测试中")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.show()
        
        # 使用一个测试单号
        test_number = "SF1234567890"
        test_company = "shunfeng"
        
        class TestThread(QThread):
            finished = Signal(bool, str, dict)
            
            def __init__(self, tracking_num, company_code, endpoint, customer="", key=""):
                super().__init__()
                self.tracking_num = tracking_num
                self.company_code = company_code
                self.endpoint = endpoint
                self.customer = customer
                self.key = key
                self._is_cancelled = False
            
            def cancel(self):
                self._is_cancelled = True
            
            def run(self):
                try:
                    if self._is_cancelled:
                        self.finished.emit(False, "测试已取消", {})
                        return
                        
                    if self.endpoint.get('endpoint_type') == 'free':
                        url = self.endpoint.get('url', 'https://www.kuaidi100.com/query')
                        params = {
                            'type': self.company_code,
                            'postid': self.tracking_num,
                            'temp': int(time.time() * 1000)
                        }
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        response = requests.get(url, params=params, headers=headers, timeout=10)
                        
                        if self._is_cancelled:
                            self.finished.emit(False, "测试已取消", {})
                            return
                            
                        if response.status_code == 200:
                            self.finished.emit(True, "接口可用", response.json())
                        else:
                            self.finished.emit(False, f"请求失败: HTTP {response.status_code}", {})
                    else:
                        self.finished.emit(False, "请使用实际查询测试收费接口", {})
                        
                except Exception as e:
                    self.finished.emit(False, f"测试失败: {str(e)}", {})
        
        # 创建并保存线程引用
        self.test_thread = TestThread(test_number, test_company, endpoint, self.parent.customer, self.parent.key)
        
        def on_test_finished(success, message, data):
            # 检查进度对话框是否还存在
            if progress_dialog and not progress_dialog.isHidden():
                progress_dialog.close()
            
            if success:
                QMessageBox.information(self, "测试结果", 
                    f"✅ {message}\n\n"
                    f"接口返回数据示例:\n{json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
            else:
                QMessageBox.warning(self, "测试结果", f"❌ {message}")
            
            # 清理线程引用
            if hasattr(self, 'test_thread'):
                self.test_thread = None
        
        def on_cancel():
            if hasattr(self, 'test_thread') and self.test_thread and self.test_thread.isRunning():
                self.test_thread.cancel()
                self.test_thread.quit()
                self.test_thread.wait(1000)
            progress_dialog.close()
        
        # 连接信号
        self.test_thread.finished.connect(on_test_finished)
        progress_dialog.canceled.connect(on_cancel)
        
        # 启动线程
        self.test_thread.start()



    def load_all_stats(self):
        """加载所有统计数据"""
        self.load_delivery_stats()
        self.load_node_stats()
        self.update_current_account_display()
        
    def update_current_account_display(self):
        """更新当前账号显示"""
        if hasattr(self, 'current_account_label'):
            if self.parent.api_account_manager:
                account = self.parent.api_account_manager.get_current_account()
                if account:
                    account_name = account.get('account_name', '未知')
                    used = account.get('used_today', 0)
                    limit = account.get('daily_limit', 100)
                    remaining = limit - used
                    
                    display_text = f"📋 {account_name} | 今日已用: {used}/{limit} | 剩余: {remaining}"
                    self.current_account_label.setText(display_text)
                    
                    if remaining <= 0:
                        self.current_account_label.setStyleSheet("font-weight: bold; padding: 5px; color: red;")
                    elif remaining <= limit * 0.2:
                        self.current_account_label.setStyleSheet("font-weight: bold; padding: 5px; color: orange;")
                    else:
                        self.current_account_label.setStyleSheet("font-weight: bold; padding: 5px; color: green;")
                else:
                    self.current_account_label.setText("⚠️ 未配置API账号")
                    self.current_account_label.setStyleSheet("font-weight: bold; padding: 5px; color: red;")
            else:
                self.current_account_label.setText("⚠️ 未配置API账号")
                self.current_account_label.setStyleSheet("font-weight: bold; padding: 5px; color: red;")
        
    def load_delivery_stats(self):
        """加载时效统计"""
        if self.parent.current_user_db:
            sql = "SELECT COUNT(*) as count FROM delivery_history"
            result = self.parent.current_user_db.execute_query(sql)
            if result:
                count = result[0]['count']
                self.stats_label.setText(f"📊 已记录 {count} 条时效数据")
                if hasattr(self, 'delivery_count_label'):
                    self.delivery_count_label.setText(str(count))
                
    def load_node_stats(self):
        """加载节点统计"""
        if self.parent.current_user_db:
            sql = "SELECT COUNT(*) as count FROM node_transit_history"
            result = self.parent.current_user_db.execute_query(sql)
            if result:
                count = result[0]['count']
                self.node_stats_label.setText(f"📍 已记录 {count} 条节点运输数据")
                if hasattr(self, 'node_count_label'):
                    self.node_count_label.setText(str(count))
                
    def clear_delivery_history(self):
        """清空时效历史数据"""
        # 清空操作需要确认，保留弹窗
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
                self.parent.status_bar.showMessage("✅ 时效历史数据已清空", 3000)
    
    def clear_node_history(self):
        """清空节点历史数据"""
        # 清空操作需要确认，保留弹窗
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有节点运输历史数据吗？\n清空后节点时间预估将使用默认值。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.parent.current_user_db:
                sql = "DELETE FROM node_transit_history"
                self.parent.current_user_db.execute_update(sql)
                self.load_node_stats()
                self.parent.status_bar.showMessage("✅ 节点历史数据已清空", 3000)
        
    def manage_accounts(self):
        """管理API账号"""
        if self.parent.current_user_db:
            dialog = ApiAccountDialog(self.parent.current_user_db, self)
            if dialog.exec() == QDialog.Accepted:
                if self.parent.api_account_manager:
                    self.parent.api_account_manager.load_accounts()
                    self.parent.load_current_api_account()
                    self.parent.update_api_account_display()
                self.update_current_account_display()
        else:
            self.status_bar.showMessage("⚠️ 数据库未连接", 3000)
            
    def refresh_account_info(self):
        """刷新账号信息"""
        if self.parent.api_account_manager:
            self.parent.api_account_manager.check_and_reset_daily_usage()
            self.parent.load_current_api_account()
            self.parent.update_api_account_display()
            self.update_current_account_display()
            self.parent.status_bar.showMessage("✅ 账号信息已刷新", 2000)
            
    def open_backup_dir(self):
        """打开备份目录"""
        import subprocess
        backup_dir = str(self.parent.backup_manager.backup_dir)
        
        if sys.platform == 'win32':
            os.startfile(backup_dir)
        elif sys.platform == 'darwin':
            subprocess.run(['open', backup_dir])
        else:
            subprocess.run(['xdg-open', backup_dir])
            
    def create_manual_backup(self):
        """创建手动备份"""
        if self.parent.user_manager.current_user_db:
            success, message, path = self.parent.backup_manager.create_backup(
                self.parent.user_manager.current_user_db.db_path,
                "manual",
                f"手动备份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            if success:
                self.parent.status_bar.showMessage(f"✅ 备份创建成功", 3000)
            else:
                self.parent.status_bar.showMessage(f"❌ 备份失败: {message}", 3000)
        else:
            self.parent.status_bar.showMessage("⚠️ 数据库未连接", 2000)
            
    def show_backup_dialog(self):
        """显示备份管理对话框"""
        if self.parent.user_manager.current_user_db:
            dialog = BackupRestoreDialogPro(
                self.parent.backup_manager,
                self.parent.user_manager.current_user_db.db_path,
                self
            )
            dialog.exec()
        else:
            self.status_bar.showMessage("⚠️ 数据库未连接", 3000)
            
    def reset_main_window_size(self):
        """重置主窗口大小"""
        self.parent.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.parent.status_bar.showMessage("✅ 窗口大小已重置", 2000)
    
    def _save_settings_now(self):
        """立即保存设置到数据库（自动保存核心，轻量不弹提示）"""
        self.parent.backup_manager.set_max_backups(self.max_backups_spin.value())
        self.parent.user_manager.save_user_setting("max_backups", str(self.max_backups_spin.value()))
        
        auto_backup = self.auto_backup_check.isChecked()
        if auto_backup:
            self.parent.backup_timer.start()
        else:
            self.parent.backup_timer.stop()
        self.parent.user_manager.save_user_setting("auto_backup", str(auto_backup).lower())
        
        debug_mode = self.debug_check.isChecked()
        self.parent.user_manager.save_user_setting("debug_mode", "1" if debug_mode else "0")
        
        global DEBUG_MODE
        DEBUG_MODE = debug_mode
    
        # 保存默认收件地址
        default_dest = self.default_dest_edit.text().strip()
        self.parent.user_manager.save_user_setting("default_dest_address", default_dest)

        # 保存代理设置
        self.save_proxy_settings()

    def _apply_settings(self):
        """应用设置到主窗口（代理刷新、接口显示）"""
        # 刷新主窗口的接口显示
        if hasattr(self.parent, 'update_api_endpoint_display'):
            self.parent.update_api_endpoint_display()
        # 应用代理设置到主窗口（刷新地图等）
        if hasattr(self.parent, 'update_proxy_settings'):
            self.parent.update_proxy_settings()

    def save_settings(self):
        """手动保存设置（带提示并应用）"""
        self._save_settings_now()
        self._apply_settings()
        self.parent.status_bar.showMessage("✅ 设置已保存", 2000)

    def _autosave_settings(self):
        """设置变更信号回调：防抖触发自动保存"""
        if self._loading:
            return
        self._settings_save_timer.start()

    def _connect_autosave(self):
        """连接所有设置控件的变更信号到实时自动保存"""
        # 备份设置
        self.max_backups_spin.valueChanged.connect(self._autosave_settings)
        self.auto_backup_check.stateChanged.connect(self._autosave_settings)
        # 高级设置
        self.debug_check.stateChanged.connect(self._autosave_settings)
        self.default_dest_edit.textChanged.connect(self._autosave_settings)
        # 代理设置
        self.proxy_enable_check.stateChanged.connect(self._autosave_settings)
        self.proxy_type_combo.currentIndexChanged.connect(self._autosave_settings)
        self.proxy_host_edit.textChanged.connect(self._autosave_settings)
        self.proxy_port_spin.valueChanged.connect(self._autosave_settings)
        self.proxy_username_edit.textChanged.connect(self._autosave_settings)
        self.proxy_password_edit.textChanged.connect(self._autosave_settings)

    def _on_close(self):
        """关闭设置对话框：强制保存后关闭"""
        if hasattr(self, '_settings_save_timer'):
            self._settings_save_timer.stop()
        self._save_settings_now()
        self._apply_settings()
        self.accept()

    def closeEvent(self, event):
        """关闭事件：强制保存设置（Esc/窗口X等）"""
        if hasattr(self, '_settings_save_timer'):
            self._settings_save_timer.stop()
            self._save_settings_now()
        super().closeEvent(event)



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
                self.parent_gui.status_bar.showMessage("⚠️ 无法识别文件编码，请确保文件为文本格式", 3000)
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
            (lambda n: n.startswith('SF') and len(n) >= 12, 'shunfeng'),
            (lambda n: len(n) == 12 and n.isdigit(), 'shunfeng'),
            (lambda n: n.startswith('SF') and n[2:].isdigit() and len(n) == 15, 'shunfeng'),
            
            # ========== 圆通速递 ==========
            (lambda n: n.startswith('YT') and len(n) >= 10, 'yuantong'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '23456', 'yuantong'),
            (lambda n: n.startswith('YT') and n[2:].isdigit(), 'yuantong'),
            
            # ========== 中通快递 ==========
            (lambda n: n.startswith('ZT') and len(n) >= 10, 'zhongtong'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '78', 'zhongtong'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('7'), 'zhongtong'),
            (lambda n: len(n) == 14 and n.isdigit() and n.startswith('8'), 'zhongtong'),
            
            # ========== 韵达快递 ==========
            (lambda n: n.startswith('YD') and len(n) >= 10, 'yunda'),
            (lambda n: len(n) == 13 and n.isdigit() and n[0] in '145', 'yunda'),
            (lambda n: n.startswith('YD') and n[2:].isdigit(), 'yunda'),
            (lambda n: len(n) == 15 and n.isdigit() and n.startswith('5'), 'yunda'),
            
            # ========== 申通快递 ==========
            (lambda n: n.startswith('ST') and len(n) >= 10, 'shentong'),
            (lambda n: len(n) == 12 and n.isdigit() and n[0] in '378', 'shentong'),
            (lambda n: n.startswith('STO') and len(n) >= 10, 'shentong'),
            (lambda n: len(n) == 13 and n.isdigit() and n.startswith('77'), 'shentong'),
            
            # ========== 京东物流 ==========
            (lambda n: n.startswith('JD'), 'jd'),
            (lambda n: n.startswith('JDV'), 'jd'),
            (lambda n: n.startswith('JDE'), 'jd'),
            (lambda n: n.startswith('JDX'), 'jd'),
            (lambda n: n.startswith('JD') and len(n) >= 10, 'jd'),
            (lambda n: 10 <= len(n) <= 15 and n.isdigit() and n[0] in '0123456789', 'jd'),
            
            # ========== EMS/中国邮政 ==========
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
            (lambda n: n.startswith('JT') and len(n) >= 10, 'jtexpress'),
            (lambda n: n.startswith('J&T') and len(n) >= 10, 'jtexpress'),
            (lambda n: 10 <= len(n) <= 18 and n.isdigit() and n[0] in '0123456789', 'jtexpress'),
            
            # ========== 百世快递 ==========
            (lambda n: n.startswith('B') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: n.startswith('H') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: n.startswith('HT') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: n.startswith('BEST') and len(n) >= 10, 'huitongkuaidi'),
            (lambda n: len(n) == 12 and n.isdigit() and n.startswith('0'), 'huitongkuaidi'),
            (lambda n: len(n) == 14 and n.isdigit() and n.startswith('3'), 'huitongkuaidi'),
            
            # ========== 德邦快递 ==========
            (lambda n: n.startswith('DPK') and len(n) >= 10, 'debangwuliu'),
            (lambda n: n.startswith('DP') and len(n) >= 10, 'debangwuliu'),
            (lambda n: n.startswith('DEBANG') and len(n) >= 10, 'debangwuliu'),
            (lambda n: len(n) >= 8 and len(n) <= 12 and n.isdigit() and n[0] in '56789', 'debangwuliu'),
            
            # ========== 天天快递 ==========
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
                self.parent_gui.status_bar.showMessage("⚠️ 请先选择文件", 3000)
                return
            if not os.path.exists(file_path):
                self.parent_gui.status_bar.showMessage("⚠️ 文件不存在", 3000)
                return
            self.load_file_content(file_path)
            return
            
        # 文本导入
        content = self.text_edit.toPlainText().strip()
        if not content:
            self.parent_gui.status_bar.showMessage("⚠️ 请输入快递单号", 3000)
            return
            
        separator = self.get_separator()
        if not separator:
            self.parent_gui.status_bar.showMessage("⚠️ 请输入自定义分隔符", 3000)
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
        
        # 常见快递公司名称关键词映射
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
            
            # 先检查是否包含已知的快递公司关键词
            for company_code, keywords in company_keywords.items():
                for keyword in keywords:
                    idx = item.find(keyword)
                    if idx >= 0:
                        pre_company = company_code
                        remaining = item[:idx] + item[idx + len(keyword):]
                        remaining = remaining.strip()
                        if remaining:
                            if len(remaining) >= 6:
                                extracted_num = remaining
                        break
                if extracted_num:
                    break
            
            # 如果没有通过关键词找到，尝试提取单号
            if not extracted_num:
                parts = item.split()
                for part in parts:
                    part = part.strip()
                    if len(part) >= 6 and any(c.isalnum() for c in part):
                        if not all('\u4e00' <= c <= '\u9fff' for c in part):
                            extracted_num = part
                            break
                
                if not extracted_num:
                    cleaned = re.sub(r'[\s\u4e00-\u9fff]+', '', item)
                    if len(cleaned) >= 6:
                        extracted_num = cleaned
                    else:
                        extracted_num = item
            
            # 清理单号
            if extracted_num:
                extracted_num = re.sub(r'[\u4e00-\u9fff\s]+', '', extracted_num)
                extracted_num = extracted_num.strip()
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
            
            # 确定快递公司
            company_code = ""
            company_name = "自动识别"
            status = "API自动"
            status_color = QColor(100, 100, 100)
            
            if num in pre_recognized_companies:
                company_code = pre_recognized_companies[num]
                company_name = self.get_company_name_by_code(company_code)
                status = "从文本识别"
                status_color = QColor(0, 100, 200)
            elif auto_detect:
                detected_code = self.detect_company_by_number(num)
                if detected_code:
                    company_code = detected_code
                    company_name = self.get_company_name_by_code(detected_code)
                    status = "格式识别"
                    status_color = QColor(0, 150, 0)
                else:
                    company_code = ""
                    company_name = "自动识别"
                    status = "API自动"
                    status_color = QColor(100, 100, 100)
            else:
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

class RebuildDeliveryWorker(QObject):
    """重建时效历史数据的工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, db_manager: DatabaseManagerPro):
        super().__init__()
        self.db_manager = db_manager
        
    def run(self):
        try:
            # 获取所有有完整物流数据的快递
            sql = """
            SELECT id, tracking_number, company_code, company_name, result_data, created_at
            FROM express_summary 
            WHERE is_deleted = 0 
            AND result_data IS NOT NULL 
            AND result_data != ''
            """
            records = self.db_manager.execute_query(sql)
            
            if not records:
                if DEBUG_MODE:
                    print("[重建时效] 没有找到可用的快递数据")
                self.finished.emit(True, "没有找到可用的快递数据")
                return
            
            total = len(records)
            
            if DEBUG_MODE:
                print(f"[重建时效] 开始扫描，共 {total} 条快递记录")
            
            self.status.emit(f"正在扫描 {total} 条快递记录...")
            
            # 先清空现有数据
            self.db_manager.execute_update("DELETE FROM delivery_history")
            
            if DEBUG_MODE:
                print("[重建时效] 已清空 delivery_history 表")
            
            # 创建临时时效估算器用于解析
            estimator = DeliveryTimeEstimator(self.db_manager)
            
            success_count = 0
            skip_count = 0  # 跳过的记录数
            error_count = 0  # 错误记录数
            
            for i, record in enumerate(records):
                try:
                    result_data = record.get('result_data', '')
                    if not result_data:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建时效] 跳过 {record.get('tracking_number', '')}: result_data 为空")
                        continue
                    
                    data = json.loads(result_data)
                    
                    # 检查是否有完整的物流轨迹
                    track_list = data.get('data', [])
                    if len(track_list) < 2:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建时效] 跳过 {record.get('tracking_number', '')}: 轨迹不足2条 (共{len(track_list)}条)")
                        continue
                    
                    # 检查是否已签收（state=3）
                    state = str(data.get('state', ''))
                    
                    # 检查最后一条轨迹是否是签收
                    last_context = track_list[-1].get('context', '') if track_list else ''
                    is_signed = (state == '3') or estimator.is_signed(last_context)
                    
                    # 检查是否已到驿站
                    is_arrived = estimator.is_arrived_at_station(last_context)
                    
                    if not is_signed and not is_arrived:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建时效] 跳过 {record.get('tracking_number', '')}: 未签收且未到驿站 (state={state})")
                        continue
                    
                    # 使用现有的 estimator 记录数据
                    estimator.record_delivery(data)
                    success_count += 1
                    
                    if DEBUG_MODE:
                        print(f"[重建时效] 成功记录 {record.get('tracking_number', '')} (签收={is_signed}, 到站={is_arrived})")
                    
                except json.JSONDecodeError as e:
                    error_count += 1
                    if DEBUG_MODE:
                        print(f"[重建时效] JSON解析失败 {record.get('tracking_number', '')}: {e}")
                except Exception as e:
                    error_count += 1
                    if DEBUG_MODE:
                        print(f"[重建时效] 处理记录 {record.get('tracking_number', '')} 失败: {e}")
                    continue
                
                # 更新进度
                progress_val = int((i + 1) / total * 100)
                self.progress.emit(progress_val)
                self.status.emit(f"已处理 {i+1}/{total} 条记录，成功 {success_count} 条")
            
            # 验证结果
            verify_sql = "SELECT COUNT(*) as count FROM delivery_history"
            verify_result = self.db_manager.execute_query(verify_sql)
            final_count = verify_result[0]['count'] if verify_result else 0
            
            if DEBUG_MODE:
                print(f"[重建时效] 完成统计:")
                print(f"  总记录数: {total}")
                print(f"  成功记录: {success_count}")
                print(f"  跳过记录: {skip_count}")
                print(f"  错误记录: {error_count}")
                print(f"  最终 delivery_history 表记录数: {final_count}")
            
            self.finished.emit(True, f"重建完成！\n扫描 {total} 条记录，成功提取 {success_count} 条时效数据\n最终 delivery_history 表共有 {final_count} 条记录")
            
        except Exception as e:
            if DEBUG_MODE:
                import traceback
                print(f"[重建时效] 异常: {e}")
                traceback.print_exc()
            self.finished.emit(False, f"重建失败：{str(e)}")

class RebuildNodeWorker(QObject):
    """重建节点运输历史数据的工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, db_manager: DatabaseManagerPro):
        super().__init__()
        self.db_manager = db_manager
        
    def run(self):
        try:
            # 验证表结构
            self.status.emit("正在验证表结构...")
            check_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='node_transit_history'"
            result = self.db_manager.execute_query(check_sql)
            if not result:
                # 表不存在，尝试创建
                self.status.emit("表不存在，正在创建...")
                analyzer = LogisticsNodeAnalyzer(self.db_manager)
                analyzer.init_node_history_table()
            
            # 获取表结构信息用于调试
            pragma_sql = "PRAGMA table_info(node_transit_history)"
            columns = self.db_manager.execute_query(pragma_sql)
            if DEBUG_MODE:
                print("[表结构] node_transit_history 列:")
                for col in columns:
                    print(f"  {col['name']} ({col['type']})")
            

            # 获取所有有完整物流数据的快递
            sql = """
            SELECT id, tracking_number, company_code, company_name, result_data, created_at
            FROM express_summary 
            WHERE is_deleted = 0 
            AND result_data IS NOT NULL 
            AND result_data != ''
            """
            records = self.db_manager.execute_query(sql)
            
            if not records:
                if DEBUG_MODE:
                    print("[重建节点] 没有找到可用的快递数据")
                self.finished.emit(True, "没有找到可用的快递数据")
                return
            
            total = len(records)
            
            if DEBUG_MODE:
                print(f"[重建节点] 开始扫描，共 {total} 条快递记录")
            
            self.status.emit(f"正在扫描 {total} 条快递记录...")
            
            # 先清空现有数据
            self.db_manager.execute_update("DELETE FROM node_transit_history")
            
            if DEBUG_MODE:
                print("[重建节点] 已清空 node_transit_history 表")
            
            # 创建节点分析器
            analyzer = LogisticsNodeAnalyzer(self.db_manager)
            
            success_count = 0
            skip_count = 0  # 跳过的记录数
            error_count = 0  # 错误记录数
            node_segments_count = 0  # 记录提取的节点段数
            
            for i, record in enumerate(records):
                try:
                    result_data = record.get('result_data', '')
                    if not result_data:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建节点] 跳过 {record.get('tracking_number', '')}: result_data 为空")
                        continue
                    
                    data = json.loads(result_data)
                    
                    # 检查是否有完整的物流轨迹（至少2条）
                    track_list = data.get('data', [])
                    if len(track_list) < 2:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建节点] 跳过 {record.get('tracking_number', '')}: 轨迹不足2条 (共{len(track_list)}条)")
                        continue
                    
                    # 记录节点数据
                    analyzer.record_node_transit(data)
                    success_count += 1
                    
                    # 统计节点段数（用于调试）
                    nodes = analyzer.extract_nodes_from_track(track_list)
                    segments = analyzer.calculate_node_transit_times(nodes)
                    node_segments_count += len(segments)
                    
                    if DEBUG_MODE:
                        print(f"[重建节点] 成功处理 {record.get('tracking_number', '')}: 提取 {len(segments)} 个节点段")
                    
                except json.JSONDecodeError as e:
                    error_count += 1
                    if DEBUG_MODE:
                        print(f"[重建节点] JSON解析失败 {record.get('tracking_number', '')}: {e}")
                except Exception as e:
                    error_count += 1
                    if DEBUG_MODE:
                        print(f"[重建节点] 处理记录 {record.get('tracking_number', '')} 失败: {e}")
                    continue
                
                # 更新进度
                progress_val = int((i + 1) / total * 100)
                self.progress.emit(progress_val)
                self.status.emit(f"已处理 {i+1}/{total} 条记录，成功 {success_count} 条，提取 {node_segments_count} 个节点段")
            
            # 验证结果
            verify_sql = "SELECT COUNT(*) as count FROM node_transit_history"
            verify_result = self.db_manager.execute_query(verify_sql)
            final_count = verify_result[0]['count'] if verify_result else 0
            
            if DEBUG_MODE:
                print(f"[重建节点] 完成统计:")
                print(f"  总记录数: {total}")
                print(f"  成功记录: {success_count}")
                print(f"  跳过记录: {skip_count}")
                print(f"  错误记录: {error_count}")
                print(f"  提取节点段数: {node_segments_count}")
                print(f"  最终 node_transit_history 表记录数: {final_count}")
            
            self.finished.emit(True, f"重建完成！\n扫描 {total} 条记录\n成功处理 {success_count} 条快递\n提取 {node_segments_count} 个节点段\n最终 node_transit_history 表共有 {final_count} 条记录")
            
        except Exception as e:
            if DEBUG_MODE:
                import traceback
                print(f"[重建节点] 异常: {e}")
                traceback.print_exc()
            self.finished.emit(False, f"重建失败：{str(e)}")

class RebuildAllWorker(QObject):
    """全部重建（时效+节点）的工作线程"""
    finished = Signal(bool, str)
    progress = Signal(int)
    status = Signal(str)
    
    def __init__(self, db_manager: DatabaseManagerPro):
        super().__init__()
        self.db_manager = db_manager
        
    def run(self):
        try:
            # 获取所有有完整物流数据的快递
            sql = """
            SELECT id, tracking_number, company_code, company_name, result_data, created_at
            FROM express_summary 
            WHERE is_deleted = 0 
            AND result_data IS NOT NULL 
            AND result_data != ''
            """
            records = self.db_manager.execute_query(sql)
            
            if not records:
                if DEBUG_MODE:
                    print("[重建全部] 没有找到可用的快递数据")
                self.finished.emit(True, "没有找到可用的快递数据")
                return
            
            total = len(records)
            
            if DEBUG_MODE:
                print(f"[重建全部] 开始扫描，共 {total} 条快递记录")
            
            self.status.emit(f"正在扫描 {total} 条快递记录...")
            
            # 清空现有数据
            self.db_manager.execute_update("DELETE FROM delivery_history")
            self.db_manager.execute_update("DELETE FROM node_transit_history")
            
            if DEBUG_MODE:
                print("[重建全部] 已清空 delivery_history 和 node_transit_history 表")
            
            # 创建分析器
            estimator = DeliveryTimeEstimator(self.db_manager)
            analyzer = LogisticsNodeAnalyzer(self.db_manager)
            
            delivery_count = 0
            node_count = 0
            skip_count = 0
            error_count = 0
            
            for i, record in enumerate(records):
                try:
                    result_data = record.get('result_data', '')
                    if not result_data:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建全部] 跳过 {record.get('tracking_number', '')}: result_data 为空")
                        continue
                    
                    data = json.loads(result_data)
                    track_list = data.get('data', [])
                    
                    if len(track_list) >= 2:
                        # 记录时效数据
                        estimator.record_delivery(data)
                        delivery_count += 1
                        
                        # 记录节点数据
                        analyzer.record_node_transit(data)
                        node_count += 1
                        
                        if DEBUG_MODE:
                            print(f"[重建全部] 成功处理 {record.get('tracking_number', '')}")
                    else:
                        skip_count += 1
                        if DEBUG_MODE:
                            print(f"[重建全部] 跳过 {record.get('tracking_number', '')}: 轨迹不足2条")
                        
                except json.JSONDecodeError as e:
                    error_count += 1
                    if DEBUG_MODE:
                        print(f"[重建全部] JSON解析失败 {record.get('tracking_number', '')}: {e}")
                except Exception as e:
                    error_count += 1
                    if DEBUG_MODE:
                        print(f"[重建全部] 处理记录 {record.get('tracking_number', '')} 失败: {e}")
                    continue
                
                # 更新进度
                progress_val = int((i + 1) / total * 100)
                self.progress.emit(progress_val)
                self.status.emit(f"已处理 {i+1}/{total} 条记录 | 时效: {delivery_count} | 节点: {node_count}")
            
            if DEBUG_MODE:
                print(f"[重建全部] 完成统计:")
                print(f"  总记录数: {total}")
                print(f"  时效数据: {delivery_count}")
                print(f"  节点数据: {node_count}")
                print(f"  跳过记录: {skip_count}")
                print(f"  错误记录: {error_count}")
            
            self.finished.emit(True, f"重建完成！\n扫描 {total} 条记录\n时效数据: {delivery_count} 条\n节点数据: {node_count} 条")
            
        except Exception as e:
            if DEBUG_MODE:
                import traceback
                print(f"[重建全部] 异常: {e}")
                traceback.print_exc()
            self.finished.emit(False, f"重建失败：{str(e)}")

class BatchExportDialog(QDialog):
    """批量导出快递单号选择对话框"""
    
    def __init__(self, numbers: List[Dict], parent=None):
        super().__init__(parent)
        self.all_numbers = numbers
        self.selected_numbers = []
        self.init_ui()
        self.load_numbers()
        self.setStyleSheet(MacaronStyle.get_main_style())
    
    def init_ui(self):
        self.setWindowTitle("批量导出快递单号")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 导出格式选择
        format_group = QGroupBox("导出格式")
        format_layout = QHBoxLayout()
        
        format_layout.addWidget(QLabel("选择导出格式："))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "纯文本 (.txt) - 每行一个单号",
            "CSV文件 (.csv) - 包含详细信息",
            "JSON文件 (.json) - 结构化数据"
        ])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # 筛选工具栏
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        filter_layout.addWidget(QLabel("🔍 筛选："))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("输入单号或公司名称筛选...")
        self.filter_edit.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_edit)
        
        # 分类筛选
        filter_layout.addWidget(QLabel("分类："))
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        self.category_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.category_combo)
        
        layout.addWidget(filter_widget)
        
        # 单号列表
        list_group = QGroupBox("选择要导出的快递单号")
        list_layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.select_all_check = QCheckBox("全选")
        self.select_all_check.stateChanged.connect(self.on_select_all)
        toolbar.addWidget(self.select_all_check)
        
        self.invert_select_btn = QPushButton("反选")
        self.invert_select_btn.clicked.connect(self.on_invert_selection)
        toolbar.addWidget(self.invert_select_btn)
        
        toolbar.addStretch()
        
        self.stats_label = QLabel()
        toolbar.addWidget(self.stats_label)
        
        list_layout.addLayout(toolbar)
        
        # 表格
        self.numbers_table = QTableWidget()
        self.numbers_table.setColumnCount(5)
        self.numbers_table.setHorizontalHeaderLabels(["选择", "快递单号", "快递公司", "状态", "分类"])
        self.numbers_table.horizontalHeader().setStretchLastSection(True)
        self.numbers_table.setAlternatingRowColors(True)
        self.numbers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.numbers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置列宽
        self.numbers_table.setColumnWidth(0, 50)
        self.numbers_table.setColumnWidth(1, 180)
        self.numbers_table.setColumnWidth(2, 120)
        self.numbers_table.setColumnWidth(3, 100)
        
        list_layout.addWidget(self.numbers_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 导出选中")
        export_btn.clicked.connect(self.accept)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
            }}
        """)
        btn_layout.addWidget(export_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_numbers(self):
        """加载单号列表"""
        # 收集所有分类
        categories = set()
        for num in self.all_numbers:
            categories.add(num['category'])
        
        # 清空并添加分类选项（保留"全部"）
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("全部")
        self.category_combo.addItems(sorted(categories))
        self.category_combo.blockSignals(False)
        
        self.update_table(self.all_numbers)
    
    def update_table(self, numbers: List[Dict]):
        """更新表格"""
        self.numbers_table.setRowCount(len(numbers))
        
        for row, item in enumerate(numbers):
            # 创建复选框
            check_box = QCheckBox()
            check_box.setProperty("number_data", item)
            # 使用 lambda 捕获当前的复选框
            check_box.stateChanged.connect(lambda state, cb=check_box: self.on_single_check_changed(cb))
            
            # 将复选框放入容器以实现居中
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)
            check_layout.setContentsMargins(0, 0, 0, 0)
            check_layout.setAlignment(Qt.AlignCenter)
            check_layout.addWidget(check_box)
            
            self.numbers_table.setCellWidget(row, 0, check_widget)
            self.numbers_table.setItem(row, 1, QTableWidgetItem(item['number']))
            self.numbers_table.setItem(row, 2, QTableWidgetItem(item['company']))
            self.numbers_table.setItem(row, 3, QTableWidgetItem(item['status']))
            self.numbers_table.setItem(row, 4, QTableWidgetItem(item['category']))
        
        self.update_stats()
        self.update_select_all_state()
    
    def get_all_checkboxes(self) -> List[QCheckBox]:
        """获取表格中所有的复选框"""
        checkboxes = []
        for row in range(self.numbers_table.rowCount()):
            check_widget = self.numbers_table.cellWidget(row, 0)
            if check_widget:
                # 从布局中获取复选框
                for i in range(check_widget.layout().count()):
                    widget = check_widget.layout().itemAt(i).widget()
                    if isinstance(widget, QCheckBox):
                        checkboxes.append(widget)
                        break
        return checkboxes
    
    def apply_filter(self):
        """应用筛选"""
        filter_text = self.filter_edit.text().strip().lower()
        filter_category = self.category_combo.currentText()
        
        filtered = []
        for num in self.all_numbers:
            # 分类筛选
            if filter_category != "全部" and num['category'] != filter_category:
                continue
            
            # 文本筛选
            if filter_text:
                if filter_text not in num['number'].lower() and filter_text not in num['company'].lower():
                    continue
            
            filtered.append(num)
        
        self.update_table(filtered)
    
    def on_select_all(self, state):
        """全选/取消全选"""
        # 获取实际的选中状态
        checked = (state == Qt.Checked.value or state == Qt.Checked)
        
        # 阻止信号循环
        self.select_all_check.blockSignals(True)
        
        checkboxes = self.get_all_checkboxes()
        for check_box in checkboxes:
            check_box.blockSignals(True)
            check_box.setChecked(checked)
            check_box.blockSignals(False)
        
        self.select_all_check.blockSignals(False)
        self.update_stats()
    
    def on_invert_selection(self):
        """反选"""
        checkboxes = self.get_all_checkboxes()
        for check_box in checkboxes:
            check_box.blockSignals(True)
            check_box.setChecked(not check_box.isChecked())
            check_box.blockSignals(False)
        
        self.update_stats()
        self.update_select_all_state()
    
    def on_single_check_changed(self, check_box: QCheckBox):
        """单个复选框状态改变"""
        # 防止递归
        check_box.blockSignals(True)
        check_box.blockSignals(False)
        self.update_stats()
        self.update_select_all_state()
    
    def update_select_all_state(self):
        """更新全选复选框状态"""
        checkboxes = self.get_all_checkboxes()
        if not checkboxes:
            self.select_all_check.setChecked(False)
            return
        
        checked_count = sum(1 for cb in checkboxes if cb.isChecked())
        total = len(checkboxes)
        
        # 阻止信号避免循环
        self.select_all_check.blockSignals(True)
        if checked_count == total:
            self.select_all_check.setCheckState(Qt.Checked)
        elif checked_count == 0:
            self.select_all_check.setCheckState(Qt.Unchecked)
        else:
            self.select_all_check.setCheckState(Qt.PartiallyChecked)
        self.select_all_check.blockSignals(False)
    
    def update_stats(self):
        """更新统计信息"""
        checkboxes = self.get_all_checkboxes()
        total = len(checkboxes)
        checked_count = sum(1 for cb in checkboxes if cb.isChecked())
        self.stats_label.setText(f"共 {total} 个，选中 {checked_count} 个")
    
    def get_selected_numbers(self) -> List[Dict]:
        """获取选中的单号"""
        selected = []
        checkboxes = self.get_all_checkboxes()
        for check_box in checkboxes:
            if check_box.isChecked():
                data = check_box.property("number_data")
                if data:
                    selected.append(data)
        return selected
    
    def get_export_format(self) -> str:
        """获取导出格式"""
        index = self.format_combo.currentIndex()
        formats = ['txt', 'csv', 'json']
        return formats[index]

class VerificationCodeDialog(DialogWithStatusBar):
    """验证码/手机尾号输入对话框"""
    
    def __init__(self, tracking_num: str, company_name: str, parent=None):
        super().__init__(parent)
        self.tracking_num = tracking_num
        self.company_name = company_name
        self.verification_code = ""
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
        
    def init_ui(self):
        self.setWindowTitle("需要验证")
        self.setMinimumSize(400, 200)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 提示信息
        info_label = QLabel(
            f"<b>查询快递需要验证</b><br><br>"
            f"快递单号：{self.tracking_num}<br>"
            f"快递公司：{self.company_name}<br><br>"
            f"<span style='color: #E65100;'>请输入收件人手机尾号（后4位）进行验证：</span>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("手机尾号："))
        
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("请输入4位数字")
        self.code_edit.setMaxLength(4)
        self.code_edit.setMinimumWidth(100)
        self.code_edit.returnPressed.connect(self.verify_and_accept)
        # 只允许输入数字
        self.code_edit.textChanged.connect(self.on_text_changed)
        input_layout.addWidget(self.code_edit)
        input_layout.addStretch()
        
        layout.addLayout(input_layout)
        
        # 提示文字
        hint_label = QLabel(
            "<span style='color: #666; font-size: 11px;'>"
            "💡 提示：<br>"
            "• 如果是隐私号码，可能需要尝试几个尾号<br>"
            "• 中通快递常见需要验证收件人手机尾号<br>"
            "• 验证码错误可以重新输入"
            "</span>"
        )
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        verify_btn = QPushButton("验证查询")
        verify_btn.clicked.connect(self.verify_and_accept)
        verify_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_SKY.name()};
                font-weight: bold;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_LAVENDER.name()};
            }}
        """)
        btn_layout.addWidget(verify_btn)
        
        skip_btn = QPushButton("跳过")
        skip_btn.setToolTip("不查询此单号")
        skip_btn.clicked.connect(self.reject)
        btn_layout.addWidget(skip_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 添加状态栏
        self.setup_status_bar(layout)
        
        self.setLayout(layout)
        
    def on_text_changed(self, text: str):
        """只允许输入数字"""
        filtered = ''.join(c for c in text if c.isdigit())
        if filtered != text:
            self.code_edit.setText(filtered)
    
    def verify_and_accept(self):
        """验证并接受"""
        code = self.code_edit.text().strip()
        if len(code) != 4:
            self.show_status("⚠️ 请输入4位手机尾号", 2000)
            return
        
        self.verification_code = code
        self.accept()
    
    def get_verification_code(self) -> str:
        """获取验证码"""
        return self.verification_code

# ==================== 地图轨迹 HTML 模板 ====================
class MapTemplate:
    """Leaflet 地图 HTML 模板"""
    
    @classmethod
    def get_map_html(cls, track_points: List[Dict]) -> str:
        """生成地图HTML"""
        import json
        
        # 处理轨迹点
        points_json = json.dumps(track_points, ensure_ascii=False)
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>物流轨迹地图</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Microsoft YaHei', sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        #map {{
            flex: 1;
            width: 100%;
        }}
        .info-panel {{
            background: white;
            padding: 8px 12px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
        }}
        .legend {{
            background: white;
            padding: 8px 12px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 4px 0;
        }}
        .legend-color {{
            width: 20px;
            height: 4px;
            margin-right: 8px;
            border-radius: 2px;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .leaflet-popup-content {{
            font-size: 12px;
            max-width: 300px;
        }}
        .popup-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .popup-time {{
            color: #999;
            font-size: 11px;
            margin-bottom: 5px;
        }}
        .popup-context {{
            color: #666;
            line-height: 1.5;
        }}
        .route-stats {{
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="info-panel" id="info-panel">
        <span id="route-info">正在加载地图...</span>
    </div>
    <div id="map"></div>
    
    <script>
        // 轨迹点数据
        const trackPoints = {points_json};
        
        // 初始化地图
        const map = L.map('map', {{
            zoomControl: true,
            fadeAnimation: true
        }});
        
        // 添加 OpenStreetMap 图层
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }}).addTo(map);
        
        // 定义图标
        const startIcon = L.divIcon({{
            html: '<div style="background-color: #4CAF50; width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(76, 175, 80, 0.5);"></div>',
            className: 'custom-marker',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        }});
        
        const endIcon = L.divIcon({{
            html: '<div style="background-color: #F44336; width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(244, 67, 54, 0.5);"></div>',
            className: 'custom-marker',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        }});
        
        const normalIcon = L.divIcon({{
            html: '<div style="background-color: #2196F3; width: 10px; height: 10px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(33, 150, 243, 0.4);"></div>',
            className: 'custom-marker',
            iconSize: [10, 10],
            iconAnchor: [5, 5]
        }});
        
        const transitIcon = L.divIcon({{
            html: '<div style="background-color: #FF9800; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(255, 152, 0, 0.4);"></div>',
            className: 'custom-marker',
            iconSize: [12, 12],
            iconAnchor: [6, 6]
        }});
        
        const pickupIcon = L.divIcon({{
            html: '<div style="background-color: #9C27B0; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(156, 39, 176, 0.4);"></div>',
            className: 'custom-marker',
            iconSize: [12, 12],
            iconAnchor: [6, 6]
        }});
        
        // 存储所有标记和线条
        const markers = [];
        const lines = [];
        let bounds = L.latLngBounds([]);
        
        // 颜色定义
        const colors = {{
            transit: '#FF9800',
            pickup: '#9C27B0',
            normal: '#2196F3',
            start: '#4CAF50',
            end: '#F44336'
        }};
        
        // 处理轨迹点
        if (trackPoints && trackPoints.length > 0) {{
            let validPoints = 0;
            let totalDistance = 0;
            
            // 创建标记
            trackPoints.forEach((point, index) => {{
                if (point.lat && point.lng) {{
                    validPoints++;
                    const latLng = L.latLng(point.lat, point.lng);
                    bounds.extend(latLng);
                    
                    // 选择图标
                    let icon = normalIcon;
                    if (index === 0) {{
                        icon = startIcon;
                    }} else if (index === trackPoints.length - 1) {{
                        icon = endIcon;
                    }} else if (point.type === 'transit_center') {{
                        icon = transitIcon;
                    }} else if (point.type === 'pickup') {{
                        icon = pickupIcon;
                    }}
                    
                    // 创建弹出内容
                    const popupContent = `
                        <div class="popup-title">${{point.site_name || point.city || '未知地点'}}</div>
                        <div class="popup-time">${{point.time_str || ''}}</div>
                        <div class="popup-context">${{point.context || ''}}</div>
                    `;
                    
                    // 添加标记
                    const marker = L.marker(latLng, {{ icon: icon }})
                        .bindPopup(popupContent)
                        .addTo(map);
                    
                    markers.push(marker);
                }}
            }});
            
            // 绘制连线
            const validLatLngs = trackPoints
                .filter(p => p.lat && p.lng)
                .map(p => [p.lat, p.lng]);
            
            if (validLatLngs.length >= 2) {{
                // 绘制主线路
                const polyline = L.polyline(validLatLngs, {{
                    color: '#2196F3',
                    weight: 3,
                    opacity: 0.7,
                    smoothFactor: 1,
                    dashArray: null
                }}).addTo(map);
                
                lines.push(polyline);
                
                // 计算总距离（粗略估算）
                for (let i = 1; i < validLatLngs.length; i++) {{
                    const p1 = L.latLng(validLatLngs[i-1][0], validLatLngs[i-1][1]);
                    const p2 = L.latLng(validLatLngs[i][0], validLatLngs[i][1]);
                    totalDistance += p1.distanceTo(p2);
                }}
                
                // 绘制各段（用不同颜色区分运输段和停留段）
                for (let i = 1; i < trackPoints.length; i++) {{
                    const p1 = trackPoints[i-1];
                    const p2 = trackPoints[i];
                    
                    if (p1.lat && p1.lng && p2.lat && p2.lng) {{
                        let color = colors.normal;
                        let dashArray = null;
                        let weight = 2;
                        
                        // 根据类型设置颜色
                        if (p1.type === 'transit_center' || p2.type === 'transit_center') {{
                            color = colors.transit;
                        }}
                        
                        // 如果是同一站点，用虚线表示停留
                        if (p1.site_name && p2.site_name && p1.site_name === p2.site_name) {{
                            color = '#9E9E9E';
                            dashArray = '5, 5';
                            weight = 2;
                        }}
                        
                        const segmentLine = L.polyline([[p1.lat, p1.lng], [p2.lat, p2.lng]], {{
                            color: color,
                            weight: weight,
                            opacity: 0.5,
                            dashArray: dashArray
                        }}).addTo(map);
                        
                        lines.push(segmentLine);
                    }}
                }}
            }}
            
            // 更新信息面板
            const infoPanel = document.getElementById('route-info');
            const totalPoints = trackPoints.length;
            const distanceKm = (totalDistance / 1000).toFixed(1);
            
            infoPanel.innerHTML = `
                📍 共 ${{totalPoints}} 个物流节点 | 
                📏 有效位置点: ${{validPoints}} 个 | 
                🛣️ 轨迹总长约 ${{distanceKm}} 公里
            `;
            
            // 调整地图视图
            if (validPoints > 0) {{
                if (validPoints === 1) {{
                    map.setView(bounds.getCenter(), 10);
                }} else {{
                    map.fitBounds(bounds, {{ padding: [30, 30] }});
                }}
            }}
        }} else {{
            document.getElementById('route-info').innerHTML = '⚠️ 暂无有效的地理位置信息，无法显示地图轨迹';
            map.setView([35.0, 105.0], 4);  // 默认显示中国中心
        }}
        
        // 添加图例
        const legend = L.control({{ position: 'bottomright' }});
        legend.onAdd = function(map) {{
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML = `
                <div style="font-weight: bold; margin-bottom: 8px;">📌 图例</div>
                <div class="legend-item">
                    <div class="legend-dot" style="background-color: #4CAF50;"></div>
                    <span>起点/揽收</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background-color: #F44336;"></div>
                    <span>当前位置/终点</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background-color: #FF9800;"></div>
                    <span>转运中心</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background-color: #2196F3;"></div>
                    <span>普通节点</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #2196F3;"></div>
                    <span>运输路线</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: repeating-linear-gradient(90deg, #9E9E9E 0px, #9E9E9E 5px, transparent 5px, transparent 10px);"></div>
                    <span>站点停留</span>
                </div>
            `;
            return div;
        }};
        
        if (trackPoints && trackPoints.length > 0) {{
            legend.addTo(map);
        }}
        
        // 添加比例尺
        L.control.scale({{
            imperial: false,
            metric: true,
            position: 'bottomleft'
        }}).addTo(map);
    </script>
</body>
</html>'''

class DestAddressManager:
    """收件地址管理器"""
    
    def __init__(self, db_manager: DatabaseManagerPro, parent_gui):
        self.db_manager = db_manager
        self.parent_gui = parent_gui
        self.addresses = []
        self.init_table()
        self.load_addresses()
    
    def init_table(self):
        """初始化表"""
        sql = """
        CREATE TABLE IF NOT EXISTS dest_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            address_type TEXT DEFAULT 'custom',
            is_default INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute_update(sql)
        
        # 尝试添加新字段
        try:
            self.db_manager.execute_update("ALTER TABLE dest_addresses ADD COLUMN address_type TEXT DEFAULT 'custom'")
        except:
            pass
        try:
            self.db_manager.execute_update("ALTER TABLE dest_addresses ADD COLUMN is_default INTEGER DEFAULT 0")
        except:
            pass
        try:
            self.db_manager.execute_update("ALTER TABLE dest_addresses ADD COLUMN sort_order INTEGER DEFAULT 0")
        except:
            pass
    
    def load_addresses(self):
        """加载所有地址"""
        sql = """
        SELECT * FROM dest_addresses 
        ORDER BY is_default DESC, sort_order, id
        """
        self.addresses = self.db_manager.execute_query(sql)
        return self.addresses
    
    def get_all_addresses(self) -> List[Dict]:
        """获取所有地址"""
        return self.addresses
    
    def get_default_address(self) -> Optional[Dict]:
        """获取默认地址"""
        for addr in self.addresses:
            if addr.get('is_default', 0) == 1:
                return addr
        return None
    
    def get_default_address_text(self) -> str:
        """获取默认地址文本"""
        default = self.get_default_address()
        if default:
            return default.get('address', '')
        return ""
    
    def add_address(self, name: str, address: str, address_type: str = 'custom') -> bool:
        """添加地址"""
        # 获取最大排序
        sql = "SELECT MAX(sort_order) as max_order FROM dest_addresses"
        result = self.db_manager.execute_query(sql)
        max_order = result[0]['max_order'] if result and result[0]['max_order'] is not None else 0
        
        sql = """
        INSERT INTO dest_addresses (name, address, address_type, sort_order)
        VALUES (?, ?, ?, ?)
        """
        result = self.db_manager.execute_update(sql, (name, address, address_type, max_order + 1))
        if result:
            self.load_addresses()
        return result
    
    def update_address(self, addr_id: int, name: str, address: str) -> bool:
        """更新地址"""
        sql = """
        UPDATE dest_addresses 
        SET name = ?, address = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        result = self.db_manager.execute_update(sql, (name, address, addr_id))
        if result:
            self.load_addresses()
        return result
    
    def delete_address(self, addr_id: int) -> bool:
        """删除地址"""
        sql = "DELETE FROM dest_addresses WHERE id = ?"
        result = self.db_manager.execute_update(sql, (addr_id,))
        if result:
            self.load_addresses()
        return result
    
    def set_default(self, addr_id: int) -> bool:
        """设为默认地址"""
        # 清除其他默认
        sql1 = "UPDATE dest_addresses SET is_default = 0"
        self.db_manager.execute_update(sql1)
        
        # 设置新的默认
        sql2 = "UPDATE dest_addresses SET is_default = 1 WHERE id = ?"
        result = self.db_manager.execute_update(sql2, (addr_id,))
        if result:
            self.load_addresses()
        return result
    
    def move_up(self, addr_id: int) -> bool:
        """上移"""
        for i, addr in enumerate(self.addresses):
            if addr['id'] == addr_id and i > 0:
                # 交换排序
                addr1 = self.addresses[i-1]
                addr2 = addr
                sql1 = "UPDATE dest_addresses SET sort_order = ? WHERE id = ?"
                sql2 = "UPDATE dest_addresses SET sort_order = ? WHERE id = ?"
                self.db_manager.execute_update(sql1, (addr2['sort_order'], addr1['id']))
                self.db_manager.execute_update(sql2, (addr1['sort_order'], addr2['id']))
                self.load_addresses()
                return True
        return False
    
    def move_down(self, addr_id: int) -> bool:
        """下移"""
        for i, addr in enumerate(self.addresses):
            if addr['id'] == addr_id and i < len(self.addresses) - 1:
                addr1 = addr
                addr2 = self.addresses[i+1]
                sql1 = "UPDATE dest_addresses SET sort_order = ? WHERE id = ?"
                sql2 = "UPDATE dest_addresses SET sort_order = ? WHERE id = ?"
                self.db_manager.execute_update(sql1, (addr2['sort_order'], addr1['id']))
                self.db_manager.execute_update(sql2, (addr1['sort_order'], addr2['id']))
                self.load_addresses()
                return True
        return False
    
    def collect_sites_from_history(self) -> List[str]:
        """从历史快递中收集所有站点"""
        sites = set()
        
        # 从 express_summary 的 result_data 中提取站点
        sql = """
        SELECT result_data FROM express_summary 
        WHERE is_deleted = 0 AND result_data IS NOT NULL AND result_data != ''
        """
        records = self.db_manager.execute_query(sql)
        
        for record in records:
            try:
                data = json.loads(record['result_data'])
                track_list = data.get('data', [])
                
                # 使用节点分析器提取站点
                if self.parent_gui and self.parent_gui.node_analyzer:
                    nodes = self.parent_gui.node_analyzer.extract_nodes_from_track(track_list)
                    for node in nodes:
                        if node.get('site_name'):
                            sites.add(node['site_name'])
                        if node.get('city'):
                            sites.add(node['city'])
                else:
                    # 简单正则提取
                    for track in track_list:
                        context = track.get('context', '')
                        # 提取【】内的内容
                        matches = re.findall(r'【([^】]+)】', context)
                        for m in matches:
                            if len(m) > 2 and not re.match(r'\d{4}-\d{2}-\d{2}', m):
                                sites.add(m.strip())
                        # 提取城市
                        city_match = re.search(r'([^\s，。；]+(?:市|省|区|县))', context)
                        if city_match:
                            sites.add(city_match.group(1))
            except:
                continue
        
        # 从 delivery_history 中提取目的城市
        sql2 = "SELECT DISTINCT dest_city FROM delivery_history WHERE dest_city != ''"
        records2 = self.db_manager.execute_query(sql2)
        for record in records2:
            if record['dest_city']:
                sites.add(record['dest_city'])
        
        # 从 node_transit_history 中提取站点
        sql3 = "SELECT DISTINCT from_site FROM node_transit_history WHERE from_site != ''"
        records3 = self.db_manager.execute_query(sql3)
        for record in records3:
            if record['from_site']:
                sites.add(record['from_site'])
        
        sql4 = "SELECT DISTINCT to_site FROM node_transit_history WHERE to_site != ''"
        records4 = self.db_manager.execute_query(sql4)
        for record in records4:
            if record['to_site']:
                sites.add(record['to_site'])
        
        return sorted(sites)

class SiteImportDialog(QDialog):
    """站点导入选择对话框"""
    
    def __init__(self, sites: List[str], parent=None):
        super().__init__(parent)
        self.sites = sites
        self.selected_sites = []
        self.init_ui()
        self.setStyleSheet(MacaronStyle.get_main_style())
    
    def init_ui(self):
        self.setWindowTitle("从历史站点导入")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 说明
        info_label = QLabel(
            f"共找到 {len(self.sites)} 个历史站点（从已签收快递的物流轨迹中收集）。\n"
            "请选择要导入的站点："
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词筛选站点...")
        self.search_edit.textChanged.connect(self.apply_filter)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # 站点列表
        list_group = QGroupBox("站点列表")
        list_layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        self.select_all_check = QCheckBox("全选")
        self.select_all_check.stateChanged.connect(self.on_select_all)
        toolbar.addWidget(self.select_all_check)
        
        self.invert_btn = QPushButton("反选")
        self.invert_btn.clicked.connect(self.on_invert_selection)
        toolbar.addWidget(self.invert_btn)
        
        toolbar.addStretch()
        
        self.stats_label = QLabel()
        toolbar.addWidget(self.stats_label)
        
        list_layout.addLayout(toolbar)
        
        # 列表
        self.site_list = QListWidget()
        self.site_list.setSelectionMode(QListWidget.ExtendedSelection)
        list_layout.addWidget(self.site_list)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 导入选中")
        import_btn.clicked.connect(self.accept)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
            }}
        """)
        btn_layout.addWidget(import_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 加载数据
        self.load_sites()
    
    def load_sites(self):
        """加载站点"""
        self.all_sites = self.sites
        self.apply_filter()
    
    def apply_filter(self):
        """应用筛选"""
        filter_text = self.search_edit.text().strip().lower()
        
        self.site_list.clear()
        
        for site in self.all_sites:
            if not filter_text or filter_text in site.lower():
                item = QListWidgetItem(site)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.site_list.addItem(item)
        
        self.update_stats()
        self.update_select_all_state()
    
    def on_select_all(self, state):
        """全选/取消全选"""
        checked = (state == Qt.Checked.value or state == Qt.Checked)
        for i in range(self.site_list.count()):
            item = self.site_list.item(i)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.update_stats()
    
    def on_invert_selection(self):
        """反选"""
        for i in range(self.site_list.count()):
            item = self.site_list.item(i)
            item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)
        self.update_stats()
        self.update_select_all_state()
    
    def update_select_all_state(self):
        """更新全选状态"""
        if self.site_list.count() == 0:
            self.select_all_check.setCheckState(Qt.Unchecked)
            return
        
        checked_count = 0
        for i in range(self.site_list.count()):
            if self.site_list.item(i).checkState() == Qt.Checked:
                checked_count += 1
        
        if checked_count == self.site_list.count():
            self.select_all_check.setCheckState(Qt.Checked)
        elif checked_count == 0:
            self.select_all_check.setCheckState(Qt.Unchecked)
        else:
            self.select_all_check.setCheckState(Qt.PartiallyChecked)
    
    def update_stats(self):
        """更新统计"""
        total = self.site_list.count()
        checked = 0
        for i in range(total):
            if self.site_list.item(i).checkState() == Qt.Checked:
                checked += 1
        self.stats_label.setText(f"共 {total} 个，选中 {checked} 个")
    
    def get_selected_sites(self) -> List[str]:
        """获取选中的站点"""
        selected = []
        for i in range(self.site_list.count()):
            item = self.site_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected

class DestAddressEditDialog(QDialog):
    """收件地址编辑对话框"""
    
    def __init__(self, parent=None, addr: Dict = None):
        super().__init__(parent)
        self.addr = addr
        self.init_ui()
        if addr:
            self.load_data()
        self.setStyleSheet(MacaronStyle.get_main_style())
    
    def init_ui(self):
        title = "编辑地址" if self.addr else "添加自定义地址"
        self.setWindowTitle(title)
        self.setMinimumSize(450, 200)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：家、公司、学校")
        form_layout.addRow("地址名称:", self.name_edit)
        
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("例如：北京市朝阳区xxx小区")
        form_layout.addRow("详细地址:", self.address_edit)
        
        layout.addLayout(form_layout)
        
        # 提示
        hint_label = QLabel("💡 提示：地址名称用于标识，详细地址用于送达时间预估")
        hint_label.setStyleSheet(f"color: {MacaronColors.TEXT_MEDIUM.name()}; font-size: 11px;")
        layout.addWidget(hint_label)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.GREEN_MINT.name()};
            }}
        """)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """加载数据"""
        if self.addr:
            self.name_edit.setText(self.addr.get('name', ''))
            self.address_edit.setText(self.addr.get('address', ''))
    
    def get_data(self) -> Tuple[str, str]:
        """获取数据"""
        return self.name_edit.text().strip(), self.address_edit.text().strip()
    
    def accept(self):
        name = self.name_edit.text().strip()
        address = self.address_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "提示", "请输入地址名称")
            return
        
        if not address:
            QMessageBox.warning(self, "提示", "请输入详细地址")
            return
        
        super().accept()



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