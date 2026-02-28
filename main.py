import sys
from typing import Dict, List, Tuple

from PySide6.QtCore import Qt
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
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

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

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(860, 610)
        self.setMinimumSize(840, 580)

        root = QWidget()
        self.setCentralWidget(root)
        self.root_layout = QHBoxLayout(root)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
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
        self.grid.setContentsMargins(0, 8, 0, 0)
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
        for i, name in enumerate(THEMES.keys()):
            colors = THEMES[name]
            tile = QFrame()
            tile.setProperty("theme_tile", True)
            row = QHBoxLayout(tile)
            row.setContentsMargins(8, 6, 8, 6)
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

            self.grid.addWidget(tile, 0, i)

    def _make_card(self, data: Tuple[str, str, str, List[str]]) -> QFrame:
        abbr, title, desc, fields = data
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
                background: {c['window']};
                color: {c['text']};
                font-family: 'Inter';
                font-size: 12px;
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
