import sys
from typing import Dict, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
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
    QVBoxLayout,
    QWidget,
)

THEMES: Dict[str, Dict[str, str]] = {
    "Arctic": {
        "window": "#0A121E",
        "panel": "#0F1C2E",
        "panel_soft": "#14263C",
        "card": "#162E4A",
        "card_border": "#2F5C86",
        "text": "#EAF7FF",
        "muted": "#9FC2DD",
        "accent": "#3FDBFF",
        "accent_alt": "#27B9DF",
        "input": "#1F3D5D",
        "input_border": "#3F6D94",
    },
    "Neon Violet": {
        "window": "#180D1E",
        "panel": "#24152F",
        "panel_soft": "#2B1C38",
        "card": "#322045",
        "card_border": "#72459C",
        "text": "#F9EEFF",
        "muted": "#D3B8E6",
        "accent": "#E27AFF",
        "accent_alt": "#B95BDB",
        "input": "#442E59",
        "input_border": "#8357A3",
    },
}

CARDS_BY_TAB = {
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


class MacroWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_theme = "Arctic"
        self.current_tab = "Crystal"
        self.nav_buttons: Dict[str, QPushButton] = {}
        self.selected_card: QFrame | None = None

        self.setWindowTitle("67 Macros | Fuck Prestige")
        self.resize(1366, 860)
        self.setMinimumSize(1080, 700)

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.root_layout = QHBoxLayout(self.central)
        self.root_layout.setContentsMargins(14, 14, 14, 14)
        self.root_layout.setSpacing(12)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(14, 14, 14, 14)
        self.sidebar_layout.setSpacing(8)

        self.content = QFrame()
        self.content.setObjectName("content")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(18, 18, 18, 18)
        self.content_layout.setSpacing(10)

        self.root_layout.addWidget(self.sidebar, 1)
        self.root_layout.addWidget(self.content, 5)

        self._build_sidebar()
        self._build_content()
        self._apply_styles()

    def theme(self) -> Dict[str, str]:
        return THEMES[self.current_theme]

    def _build_sidebar(self) -> None:
        self.logo = QLabel("67 Macros")
        self.logo.setObjectName("logo")
        self.sidebar_layout.addWidget(self.logo)

        nav_items = [
            ("◈ Crystal", "Crystal"),
            ("⚒ Mace", "Mace"),
            ("⚔ Sword", "Sword"),
            ("◎ Themes", "Themes"),
        ]
        for label, key in nav_items:
            btn = QPushButton(label)
            btn.setProperty("nav", True)
            btn.clicked.connect(lambda _=False, k=key: self.switch_tab(k))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        self.sidebar_layout.addStretch(1)

    def _build_content(self) -> None:
        self.title = QLabel()
        self.title.setObjectName("title")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(self.subtitle)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.page = QWidget()
        self.page_layout = QGridLayout(self.page)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.setSpacing(12)
        self.scroll.setWidget(self.page)
        self.content_layout.addWidget(self.scroll, 1)

        self.render_tab()

    def _clear_grid(self) -> None:
        while self.page_layout.count():
            item = self.page_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def switch_tab(self, key: str) -> None:
        self.current_tab = key
        self.selected_card = None
        self.render_tab()
        self._apply_styles()

    def render_tab(self) -> None:
        self._clear_grid()

        if self.current_tab == "Themes":
            self.title.setText("Themes")
            self.subtitle.setText("Compact presets with quick apply")
            self._render_themes()
            return

        self.title.setText(f"{self.current_tab} Macros")
        self.subtitle.setText("Configure your PvP automation")
        cards = CARDS_BY_TAB[self.current_tab]
        for i, card_data in enumerate(cards):
            card = self._build_card(card_data)
            self.page_layout.addWidget(card, i // 2, i % 2)

    def _render_themes(self) -> None:
        for i, name in enumerate(THEMES.keys()):
            tile = QFrame()
            tile.setProperty("theme_tile", True)
            row = QHBoxLayout(tile)
            row.setContentsMargins(10, 8, 10, 8)
            row.setSpacing(8)

            label = QLabel(name)
            row.addWidget(label)
            row.addStretch(1)

            swatches = QWidget()
            sw = QHBoxLayout(swatches)
            sw.setContentsMargins(0, 0, 0, 0)
            sw.setSpacing(4)
            for key in ["window", "card", "accent", "accent_alt"]:
                box = QFrame()
                box.setFixedSize(18, 10)
                box.setStyleSheet(f"background:{THEMES[name][key]}; border-radius:3px;")
                sw.addWidget(box)
            row.addWidget(swatches)

            btn = QPushButton("Apply")
            btn.clicked.connect(lambda _=False, n=name: self.apply_theme(n))
            row.addWidget(btn)
            self.page_layout.addWidget(tile, 0, i)

    def apply_theme(self, name: str) -> None:
        self.current_theme = name
        self._apply_styles()
        self.render_tab()

    def _build_card(self, data: tuple) -> QFrame:
        abbr, title, desc, fields = data
        card = QFrame()
        card.setProperty("macro_card", True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        badge = QLabel(abbr)
        badge.setProperty("badge", True)
        top.addWidget(badge)

        info = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setProperty("card_title", True)
        desc_lbl = QLabel(desc)
        desc_lbl.setProperty("card_desc", True)
        info.addWidget(title_lbl)
        info.addWidget(desc_lbl)
        top.addLayout(info, 1)

        power = QPushButton("⏻")
        power.setFixedSize(28, 28)
        power.clicked.connect(lambda _=False, c=card, s=title: self.activate_card(c, s))
        top.addWidget(power)
        layout.addLayout(top)

        for field in fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(field), 1)
            btn = QPushButton("PLACEHOLDER")
            btn.setFixedSize(130, 28)
            btn.clicked.connect(lambda _=False, c=card, f=field: self.activate_card(c, f))
            row.addWidget(btn)
            layout.addLayout(row)

        self._add_glow(card, self.theme()["accent"], 14, 0)
        return card

    def activate_card(self, card: QFrame, source: str) -> None:
        if self.selected_card:
            self.selected_card.setProperty("active", False)
            self.selected_card.style().unpolish(self.selected_card)
            self.selected_card.style().polish(self.selected_card)

        self.selected_card = card
        self.selected_card.setProperty("active", True)
        self.selected_card.style().unpolish(self.selected_card)
        self.selected_card.style().polish(self.selected_card)
        self._add_glow(self.selected_card, self.theme()["accent"], 28, 1)
        print(f"placeholder: {source}")

    @staticmethod
    def _add_glow(widget: QWidget, color: str, blur: int, alpha_boost: int) -> None:
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(blur)
        effect.setOffset(0, 0)
        from PySide6.QtGui import QColor

        c = QColor(color)
        c.setAlpha(130 + alpha_boost * 60)
        effect.setColor(c)
        widget.setGraphicsEffect(effect)

    def _apply_styles(self) -> None:
        t = self.theme()
        for key, btn in self.nav_buttons.items():
            btn.setProperty("active", key == self.current_tab)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.setStyleSheet(
            f"""
            QWidget {{
                background: {t['window']};
                color: {t['text']};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            #sidebar {{
                background: {t['panel']};
                border: 1px solid {t['card_border']};
                border-radius: 18px;
            }}
            #content {{
                background: {t['panel_soft']};
                border: 1px solid {t['card_border']};
                border-radius: 18px;
            }}
            #logo {{
                color: {t['accent']};
                font-size: 42px;
                font-weight: 800;
                background: transparent;
                margin-bottom: 6px;
            }}
            #title {{
                font-size: 40px;
                font-weight: 800;
                background: transparent;
            }}
            #subtitle {{
                color: {t['muted']};
                font-size: 15px;
                background: transparent;
                margin-bottom: 8px;
            }}
            QPushButton[nav='true'] {{
                text-align: left;
                padding: 8px 10px;
                border-radius: 10px;
                border: 1px solid {t['input_border']};
                background: transparent;
                font-size: 18px;
                font-weight: 700;
            }}
            QPushButton[nav='true'][active='true'] {{
                background: {t['accent_alt']};
                border: 1px solid {t['accent']};
            }}
            QPushButton {{
                border-radius: 8px;
                border: 1px solid {t['input_border']};
                background: {t['input']};
                padding: 4px 10px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {t['accent_alt']};
                border: 1px solid {t['accent']};
            }}
            QFrame[macro_card='true'] {{
                background: {t['card']};
                border: 1px solid {t['card_border']};
                border-radius: 16px;
            }}
            QFrame[macro_card='true'][active='true'] {{
                border: 2px solid {t['accent']};
            }}
            QLabel[badge='true'] {{
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                border-radius: 12px;
                background: {t['input']};
                color: {t['accent']};
                font-weight: 800;
                font-size: 15px;
                qproperty-alignment: 'AlignCenter';
            }}
            QLabel[card_title='true'] {{
                font-size: 30px;
                font-weight: 800;
                background: transparent;
            }}
            QLabel[card_desc='true'] {{
                color: {t['muted']};
                font-size: 13px;
                background: transparent;
            }}
            QFrame[theme_tile='true'] {{
                background: {t['card']};
                border: 1px solid {t['card_border']};
                border-radius: 10px;
            }}
            QScrollArea, QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            """
        )

        self._add_glow(self.sidebar, t["accent"], 30, 0)
        self._add_glow(self.content, t["accent_alt"], 20, 0)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    win = MacroWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
