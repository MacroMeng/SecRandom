# ==================================================
# UI 工具类
# ==================================================
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from qfluentwidgets import *
from loguru import logger

from app.tools.personalised import load_custom_font


class UIUtils:
    """UI 工具类，提供通用的 UI 相关功能"""

    @staticmethod
    def create_button_with_long_press(
        parent_widget, text, font_size, direction, update_count_callback
    ):
        """
        创建带长按功能的按钮

        Args:
            parent_widget: 父控件
            text: 按钮文本
            font_size: 字体大小
            direction: 长按方向（1为增加，-1为减少）
            update_count_callback: 更新计数的回调函数

        Returns:
            创建的按钮
        """
        button = PushButton(text)
        UIUtils.set_widget_font(button, font_size)
        button.setFixedSize(45, 45)
        button.clicked.connect(lambda: update_count_callback(direction))
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        button.mousePressEvent = lambda event: UIUtils.custom_mouse_press_event(
            button, event
        )
        button.mouseReleaseEvent = lambda event: UIUtils.custom_mouse_release_event(
            button, event
        )

        return button

    @staticmethod
    def custom_mouse_press_event(widget, event):
        """
        自定义鼠标按下事件，将右键转换为左键

        Args:
            widget: 控件
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.RightButton:
            new_event = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                event.position(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            QApplication.sendEvent(widget, new_event)
        else:
            PushButton.mousePressEvent(widget, event)

    @staticmethod
    def custom_mouse_release_event(widget, event):
        """
        自定义鼠标释放事件，将右键转换为左键

        Args:
            widget: 控件
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.RightButton:
            new_event = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                event.position(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            )
            QApplication.sendEvent(widget, new_event)
        else:
            PushButton.mouseReleaseEvent(widget, event)

    @staticmethod
    def set_widget_font(widget, font_size):
        """
        为控件设置字体

        Args:
            widget: 控件
            font_size: 字体大小
        """
        try:
            if not isinstance(font_size, (int, float)):
                font_size = int(font_size) if str(font_size).isdigit() else 12

            font_size = int(font_size)
            if font_size <= 0:
                font_size = 12

            custom_font = load_custom_font()
            if custom_font:
                widget.setFont(QFont(custom_font, font_size))
        except (ValueError, TypeError) as e:
            logger.warning(f"设置字体大小失败，使用默认值: {e}")
            custom_font = load_custom_font()
            if custom_font:
                widget.setFont(QFont(custom_font, 12))

    @staticmethod
    def event_filter(obj, event):
        """
        事件过滤器，处理触屏长按事件

        Args:
            obj: 对象
            event: 事件

        Returns:
            是否处理了事件
        """
        return False


class LongPressHandler:
    """长按处理器"""

    def __init__(
        self, update_count_callback, long_press_interval=100, long_press_delay=500
    ):
        """
        初始化长按处理器

        Args:
            update_count_callback: 更新计数的回调函数
            long_press_interval: 长按时连续触发的间隔时间(毫秒)
            long_press_delay: 开始长按前的延迟时间(毫秒)
        """
        self.press_timer = QTimer()
        self.press_timer.timeout.connect(self.handle_long_press)
        self.long_press_interval = long_press_interval
        self.long_press_delay = long_press_delay
        self.is_long_pressing = False
        self.long_press_direction = 0
        self.update_count_callback = update_count_callback

    def handle_long_press(self):
        """处理长按事件"""
        if self.is_long_pressing:
            self.press_timer.setInterval(self.long_press_interval)
            self.update_count_callback(self.long_press_direction)

    def start_long_press(self, direction):
        """
        开始长按

        Args:
            direction (int): 长按方向，1为增加，-1为减少
        """
        self.long_press_direction = direction
        self.is_long_pressing = True
        self.press_timer.setInterval(self.long_press_delay)
        self.press_timer.start()

    def stop_long_press(self):
        """停止长按"""
        self.is_long_pressing = False
        self.press_timer.stop()

    def stop(self):
        """停止定时器"""
        if hasattr(self, "press_timer"):
            self.press_timer.stop()
