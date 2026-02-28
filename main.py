import importlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

SETTINGS_PATH = Path("single_anchor_settings.json")

THEMES: Dict[str, Dict[str, str]] = {
    "Ice": {
        "window": "#0d131a",
        "sidebar": "#0f1720",
        "content": "#111a24",
        "card": "#273341",
        "card_soft": "#1f2935",
        "card_border": "#3e4f62",
        "text": "#edf4ff",
        "muted": "#a8b8c8",
        "accent": "#7dd6ff",
        "accent_soft": "#254053",
        "pill": "#2f3d4e",
        "pill_border": "#4a5f78",
    },
    "Graphite": {
        "window": "#101214",
        "sidebar": "#14181c",
        "content": "#161d24",
        "card": "#222a32",
        "card_soft": "#1b222a",
        "card_border": "#3a4652",
        "text": "#e8edf3",
        "muted": "#a5b2bf",
        "accent": "#79cff1",
        "accent_soft": "#2a3b47",
        "pill": "#2a333d",
        "pill_border": "#485665",
    },
}

CARDS_BY_TAB: Dict[str, List[Tuple[str, str, str, List[str]]]] = {
    "Crystal": [
        ("HC", "Hit Crystal", "Auto place obsidian and hit crystal", ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"]),
        ("SA", "Single Anchor", "Auto place and explode an anchor", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("DA", "Double Anchor", "Auto place and explode two anchors", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("SHC", "Slow Hit Crystal", "Hit crystal with optimal timing", ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"]),
    ],
    "Mace": [
        ("MB", "Mace Burst", "Burst combo chain", ["Keybind", "Delay", "Mace Slot", "Totem Slot"]),
        ("MS", "Mace Swap", "Quick weapon swap", ["Keybind", "Swap Delay", "Mace Slot", "Shield Slot"]),
    ],
    "Sword": [
        ("SC", "Sword Crit", "Timed crit setup", ["Keybind", "Delay", "Sword Slot", "Gap Slot"]),
        ("SP", "Sword Pressure", "Sustain pressure combo", ["Keybind", "Delay", "Sword Slot", "Pearl Slot"]),
    ],
}

ICONS = {"Crystal": "◇", "Mace": "✛", "Sword": "✦", "Themes": "◌"}


class MacroWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_theme = "Ice"
        self.current_tab = "Crystal"
        self.selected_card: QFrame | None = None
        self.nav_buttons: Dict[str, QPushButton] = {}

        self.single_anchor = {
            "bind": "F",
            "delay": 50,
            "place": "right",
            "anchor_key": "5",
            "glow_key": "6",
            "totem_key": "8",
        }
        self._load_settings()

        self.single_anchor_widgets: Dict[str, QWidget] = {}
        self.capture_target: str | None = None
        self.macro_steps: List[Tuple[str, str]] = []
        self.step_timer = QTimer(self)
        self.step_timer.timeout.connect(self._run_single_anchor_step)

        self.pyautogui = self._load_pyautogui()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.resize(860, 610)
        self.setMinimumSize(840, 580)

        root = QWidget()
        root.setObjectName("window_root")
        self.setCentralWidget(root)
        root_outer = QVBoxLayout(root)
        root_outer.setContentsMargins(0, 0, 0, 0)

        self.window_shell = QFrame()
        self.window_shell.setObjectName("window_shell")
        root_outer.addWidget(self.window_shell)

        self.root_layout = QHBoxLayout(self.window_shell)
        self.root_layout.setContentsMargins(12, 12, 12, 12)
        self.root_layout.setSpacing(10)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(12, 12, 12, 12)
        self.sidebar_layout.setSpacing(8)

        self.content_shell = QFrame()
        self.content_shell.setObjectName("content_shell")
        self.content_layout = QVBoxLayout(self.content_shell)
        self.content_layout.setContentsMargins(14, 14, 14, 14)
        self.content_layout.setSpacing(4)

        self.root_layout.addWidget(self.sidebar, 1)
        self.root_layout.addWidget(self.content_shell, 4)

        self._build_sidebar()
        self._build_content()
        self._render_current_tab()
        self._apply_styles()

    def _load_settings(self) -> None:
        if not SETTINGS_PATH.exists():
            return
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return

        if isinstance(data, dict):
            for key in self.single_anchor:
                if key in data:
                    self.single_anchor[key] = data[key]

    def _save_settings(self) -> None:
        SETTINGS_PATH.write_text(json.dumps(self.single_anchor, indent=2), encoding="utf-8")

    def _load_pyautogui(self):
        try:
            return importlib.import_module("pyautogui")
        except Exception:
            return None

    def colors(self) -> Dict[str, str]:
        return THEMES[self.current_theme]

    def _build_sidebar(self) -> None:
        title = QLabel("67 Macros")
        title.setObjectName("logo")
        self.sidebar_layout.addWidget(title)

        for key in ["Crystal", "Mace", "Sword", "Themes"]:
            btn = QPushButton(f"{ICONS[key]}  {key}")
            btn.setProperty("nav", True)
            btn.clicked.connect(lambda _=False, k=key: self._switch_tab(k))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        self.sidebar_layout.addStretch(1)

    def _build_content(self) -> None:
        self.header = QLabel()
        self.header.setObjectName("header")
        self.subheader = QLabel()
        self.subheader.setObjectName("subheader")
        self.content_layout.addWidget(self.header)
        self.content_layout.addWidget(self.subheader)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setContentsMargins(4, 10, 4, 10)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.scroll_content)
        self.content_layout.addWidget(self.scroll, 1)

    def _clear_grid(self) -> None:
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _switch_tab(self, key: str) -> None:
        self.current_tab = key
        self.selected_card = None
        self._render_current_tab()
        self._apply_styles()

    def _render_current_tab(self) -> None:
        self._clear_grid()

        if self.current_tab == "Themes":
            self.header.setText("Themes")
            self.subheader.setText("Small + simple presets")
            self._render_theme_tiles()
            return

        self.header.setText(f"{self.current_tab} Macros")
        self.subheader.setText("Configure your end crystal PvP automation")

        cards = CARDS_BY_TAB[self.current_tab]
        for i, data in enumerate(cards):
            self.grid.addWidget(self._make_card(data), i // 2, i % 2)

    def _render_theme_tiles(self) -> None:
        self.grid.setColumnStretch(0, 1)
        for i, name in enumerate(THEMES.keys()):
            colors = THEMES[name]
            tile = QFrame()
            tile.setProperty("theme_tile", True)
            row = QHBoxLayout(tile)
            row.setContentsMargins(10, 7, 10, 7)
            row.setSpacing(6)

            label = QLabel(name)
            label.setObjectName("theme_label")
            row.addWidget(label)

            swatch_holder = QWidget()
            swatch_row = QHBoxLayout(swatch_holder)
            swatch_row.setContentsMargins(0, 0, 0, 0)
            swatch_row.setSpacing(4)
            for key in ["window", "card", "accent", "pill"]:
                swatch = QFrame()
                swatch.setFixedSize(14, 8)
                swatch.setStyleSheet(f"background:{colors[key]}; border-radius:3px;")
                swatch_row.addWidget(swatch)
            row.addWidget(swatch_holder)

            apply_btn = QPushButton("Apply")
            apply_btn.setProperty("mini", True)
            apply_btn.clicked.connect(lambda _=False, n=name: self._apply_theme(n))
            row.addWidget(apply_btn)

            self.grid.addWidget(tile, i, 0)

    def _make_card(self, data: Tuple[str, str, str, List[str]]) -> QFrame:
        abbr, title, desc, fields = data
        if self.current_tab == "Crystal" and title == "Single Anchor":
            return self._make_single_anchor_card(abbr, title, desc)

        card = QFrame()
        card.setProperty("macro_card", True)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(6)

        top_row = QHBoxLayout()
        badge = QLabel(abbr)
        badge.setProperty("badge", True)
        top_row.addWidget(badge)

        text_col = QVBoxLayout()
        t = QLabel(title)
        t.setProperty("card_title", True)
        d = QLabel(desc)
        d.setProperty("card_desc", True)
        text_col.addWidget(t)
        text_col.addWidget(d)
        top_row.addLayout(text_col, 1)

        power = QPushButton("◉")
        power.setProperty("round", True)
        power.setFixedSize(24, 24)
        power.clicked.connect(lambda _=False, c=card, s=title: self._activate(c, s))
        top_row.addWidget(power)
        card_layout.addLayout(top_row)

        for field in fields:
            row = QHBoxLayout()
            row.setSpacing(8)
            field_label = QLabel(field)
            field_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row.addWidget(field_label)

            placeholder = QPushButton("None")
            placeholder.setProperty("pill", True)
            placeholder.setFixedSize(86, 22)
            placeholder.clicked.connect(lambda _=False, c=card, f=field: self._activate(c, f))
            row.addWidget(placeholder)
            card_layout.addLayout(row)

        self._set_glow(card, self.colors()["accent"], 16, 60)
        return card

    def _make_single_anchor_card(self, abbr: str, title: str, desc: str) -> QFrame:
        card = QFrame()
        card.setProperty("macro_card", True)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(7)

        top_row = QHBoxLayout()
        badge = QLabel(abbr)
        badge.setProperty("badge", True)
        top_row.addWidget(badge)

        text_col = QVBoxLayout()
        t = QLabel(title)
        t.setProperty("card_title", True)
        d = QLabel(desc)
        d.setProperty("card_desc", True)
        text_col.addWidget(t)
        text_col.addWidget(d)
        top_row.addLayout(text_col, 1)
        card_layout.addLayout(top_row)

        bind_row = QHBoxLayout()
        bind_row.addWidget(QLabel("Macro Bind"), 1)
        bind_btn = QPushButton(self.single_anchor["bind"])
        bind_btn.setProperty("pill", True)
        bind_btn.clicked.connect(self._start_single_anchor_macro)
        bind_row.addWidget(bind_btn)

        set_bind_btn = QPushButton("Set")
        set_bind_btn.setProperty("mini", True)
        set_bind_btn.clicked.connect(lambda: self._arm_capture("bind"))
        bind_row.addWidget(set_bind_btn)
        card_layout.addLayout(bind_row)

        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("Delay"), 1)
        delay_value = QLabel(f"{self.single_anchor['delay']} ms")
        delay_row.addWidget(delay_value)
        card_layout.addLayout(delay_row)

        delay_slider = QSlider(Qt.Horizontal)
        delay_slider.setMinimum(0)
        delay_slider.setMaximum(500)
        delay_slider.setValue(int(self.single_anchor["delay"]))
        delay_slider.setMaximumWidth(180)
        delay_slider.valueChanged.connect(self._update_single_anchor_delay)
        card_layout.addWidget(delay_slider)

        card_layout.addLayout(self._bind_row("Place Keybind", "place"))
        card_layout.addLayout(self._bind_row("Anchor Slot Key", "anchor_key"))
        card_layout.addLayout(self._bind_row("Glowstone Slot Key", "glow_key"))
        card_layout.addLayout(self._bind_row("Totem Slot Key", "totem_key"))

        run_btn = QPushButton("Run Single Anchor")
        run_btn.clicked.connect(self._start_single_anchor_macro)
        card_layout.addWidget(run_btn)

        hint = QLabel("Order: Anchor Key→Place, Glow Key→Place, Totem Key→Place")
        hint.setProperty("card_desc", True)
        card_layout.addWidget(hint)

        self.single_anchor_widgets = {
            "bind_btn": bind_btn,
            "delay_label": delay_value,
            "delay_slider": delay_slider,
            **self.single_anchor_widgets,
        }

        self._set_glow(card, self.colors()["accent"], 16, 60)
        return card

    def _bind_row(self, label: str, setting_key: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(QLabel(label), 1)

        btn = QPushButton(self._format_bind_display(str(self.single_anchor[setting_key])))
        btn.setProperty("pill", True)
        btn.clicked.connect(lambda: self._arm_capture(setting_key))
        row.addWidget(btn)
        self.single_anchor_widgets[f"{setting_key}_btn"] = btn
        return row

    def _update_single_anchor_delay(self, value: int) -> None:
        self.single_anchor["delay"] = value
        delay_label = self.single_anchor_widgets.get("delay_label")
        if isinstance(delay_label, QLabel):
            delay_label.setText(f"{value} ms")
        self._save_settings()

    def _arm_capture(self, target: str) -> None:
        self.capture_target = target
        self.activateWindow()
        self.setFocus()

        if target == "bind":
            bind_btn = self.single_anchor_widgets.get("bind_btn")
            if isinstance(bind_btn, QPushButton):
                bind_btn.setText("Press key...")
            return

        btn = self.single_anchor_widgets.get(f"{target}_btn")
        if isinstance(btn, QPushButton):
            btn.setText("Press key/mouse...")

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        key_name = self._event_key_name(event)
        if not key_name:
            super().keyPressEvent(event)
            return

        if self.capture_target:
            self._set_capture_value(self.capture_target, key_name.lower())
            return

        if key_name.upper() == str(self.single_anchor["bind"]).upper():
            self._start_single_anchor_macro()
            return

        super().keyPressEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if self.capture_target:
            mapping = {
                Qt.LeftButton: "left",
                Qt.RightButton: "right",
                Qt.MiddleButton: "middle",
            }
            if event.button() in mapping:
                self._set_capture_value(self.capture_target, mapping[event.button()])
                return
        super().mousePressEvent(event)

    def _set_capture_value(self, target: str, value: str) -> None:
        self.single_anchor[target] = value.upper() if target == "bind" else value
        if target == "bind":
            btn = self.single_anchor_widgets.get("bind_btn")
            if isinstance(btn, QPushButton):
                btn.setText(str(self.single_anchor[target]))
        else:
            btn = self.single_anchor_widgets.get(f"{target}_btn")
            if isinstance(btn, QPushButton):
                btn.setText(self._format_bind_display(str(self.single_anchor[target])))

        self.capture_target = None
        self._save_settings()

    def _event_key_name(self, event) -> str:
        text = event.text().strip()
        if text:
            return text.upper()
        special = {
            Qt.Key_Control: "CTRL",
            Qt.Key_Shift: "SHIFT",
            Qt.Key_Alt: "ALT",
            Qt.Key_Space: "SPACE",
            Qt.Key_Tab: "TAB",
        }
        return special.get(event.key(), "")

    def _start_single_anchor_macro(self) -> None:
        if self.step_timer.isActive():
            return

        self.macro_steps = [
            (str(self.single_anchor["anchor_key"]), str(self.single_anchor["place"])),
            (str(self.single_anchor["glow_key"]), str(self.single_anchor["place"])),
            (str(self.single_anchor["totem_key"]), str(self.single_anchor["place"])),
        ]
        self._run_single_anchor_step()

    def _run_single_anchor_step(self) -> None:
        if not self.macro_steps:
            self.step_timer.stop()
            return

        slot_key, place_key = self.macro_steps.pop(0)
        self._perform_macro_step(slot_key, place_key)

        if self.macro_steps:
            self.step_timer.start(int(self.single_anchor["delay"]))

    def _perform_macro_step(self, slot_key: str, place_key: str) -> None:
        if self.pyautogui is None:
            print(f"Single Anchor step -> slot key {slot_key}, place: {place_key}")
            return

        try:
            self.pyautogui.press(slot_key)
            if place_key in {"left", "right", "middle"}:
                self.pyautogui.click(button=place_key)
            else:
                self.pyautogui.press(place_key)
        except Exception as exc:  # pragma: no cover
            print(f"Macro execution failed: {exc}")

    @staticmethod
    def _format_bind_display(value: str) -> str:
        mapping = {"left": "LMB", "right": "RMB", "middle": "MMB"}
        return mapping.get(value.lower(), value.upper())

    def _activate(self, card: QFrame, source: str) -> None:
        if self.selected_card is not None:
            self.selected_card.setProperty("active", False)
            self.selected_card.style().unpolish(self.selected_card)
            self.selected_card.style().polish(self.selected_card)
            self._set_glow(self.selected_card, self.colors()["accent"], 16, 60)

        self.selected_card = card
        card.setProperty("active", True)
        card.style().unpolish(card)
        card.style().polish(card)
        self._set_glow(card, self.colors()["accent"], 28, 150)
        print(f"placeholder clicked: {source}")

    @staticmethod
    def _set_glow(widget: QWidget, hex_color: str, blur: int, alpha: int) -> None:
        effect = QGraphicsDropShadowEffect(widget)
        effect.setOffset(0, 0)
        effect.setBlurRadius(blur)
        color = QColor(hex_color)
        color.setAlpha(alpha)
        effect.setColor(color)
        widget.setGraphicsEffect(effect)

    def _apply_theme(self, name: str) -> None:
        self.current_theme = name
        self.selected_card = None
        self._render_current_tab()
        self._apply_styles()

    def _apply_styles(self) -> None:
        c = self.colors()

        for key, btn in self.nav_buttons.items():
            btn.setProperty("active", key == self.current_tab)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.setStyleSheet(
            f"""
            QWidget {{
                background: transparent;
                color: {c['text']};
                font-family: 'Inter';
                font-size: 12px;
            }}
            #window_root {{
                background: transparent;
            }}
            #window_shell {{
                background: {c['window']};
                border-radius: 16px;
                border: 1px solid #223143;
            }}
            #sidebar {{
                background: {c['sidebar']};
                border: 1px solid #223143;
                border-radius: 14px;
            }}
            #content_shell {{
                background: {c['content']};
                border: 1px solid #2a3b4f;
                border-radius: 14px;
            }}
            #logo {{
                font-size: 26px;
                font-weight: 700;
                color: {c['text']};
                background: transparent;
                margin-bottom: 6px;
            }}
            #header {{
                font-size: 40px;
                font-weight: 700;
                color: {c['text']};
                background: transparent;
            }}
            #subheader {{
                font-size: 13px;
                color: {c['muted']};
                background: transparent;
                margin-bottom: 4px;
            }}
            QPushButton[nav='true'] {{
                text-align: left;
                border-radius: 8px;
                border: 1px solid #2f4155;
                background: transparent;
                padding: 7px 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton[nav='true'][active='true'] {{
                background: {c['accent_soft']};
                border: 1px solid {c['accent']};
            }}
            QPushButton {{
                background: {c['pill']};
                border: 1px solid {c['pill_border']};
                border-radius: 7px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border: 1px solid {c['accent']};
            }}
            QSlider::groove:horizontal {{
                background: {c['pill']};
                height: 6px;
                border-radius: 3px;
                max-width: 180px;
            }}
            QSlider::handle:horizontal {{
                background: {c['accent']};
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QPushButton[pill='true'] {{
                background: {c['pill']};
                color: {c['text']};
            }}
            QPushButton[mini='true'] {{
                padding: 2px 8px;
                min-height: 20px;
            }}
            QPushButton[round='true'] {{
                border-radius: 12px;
                padding: 0px;
            }}
            QFrame[macro_card='true'] {{
                background: {c['card']};
                border: 1px solid {c['card_border']};
                border-radius: 12px;
            }}
            QFrame[macro_card='true'][active='true'] {{
                border: 1px solid {c['accent']};
                background: {c['card_soft']};
            }}
            QLabel[badge='true'] {{
                background: {c['accent_soft']};
                border: 1px solid {c['pill_border']};
                border-radius: 10px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
                color: {c['accent']};
                qproperty-alignment: AlignCenter;
                font-size: 12px;
                font-weight: 700;
            }}
            QLabel[card_title='true'] {{
                background: transparent;
                font-size: 17px;
                font-weight: 700;
            }}
            QLabel[card_desc='true'] {{
                background: transparent;
                color: {c['muted']};
                font-size: 12px;
            }}
            QFrame[theme_tile='true'] {{
                background: {c['card']};
                border: 1px solid {c['card_border']};
                border-radius: 9px;
                min-height: 34px;
            }}
            #theme_label {{
                background: transparent;
                font-size: 12px;
                font-weight: 600;
            }}
            QScrollArea, QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            """
        )

        self._set_glow(self.window_shell, c["accent"], 26, 44)
        self._set_glow(self.sidebar, c["accent"], 24, 50)
        self._set_glow(self.content_shell, c["accent"], 20, 36)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    window = MacroWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
