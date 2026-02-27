import customtkinter as ctk

ctk.set_appearance_mode("dark")

# 1-to-1 editable visual theme
THEMES = {
    "Neon Wine": {
        "window_bg": "#130612",
        "sidebar_bg": "#0F0610",
        "content_bg": "#1A0B18",
        "card_bg": "#261022",
        "card_border": "#4C1C42",
        "card_active": "#E951A2",
        "text_main": "#F7EEF6",
        "text_muted": "#B892B0",
        "accent": "#D63F89",
        "accent_2": "#7A1D4F",
        "input_bg": "#321A2D",
        "input_border": "#553149",
        "chip_bg": "#3B1730",
    },
    "Void Cyan": {
        "window_bg": "#080D14",
        "sidebar_bg": "#070B11",
        "content_bg": "#111B28",
        "card_bg": "#142335",
        "card_border": "#1E3C58",
        "card_active": "#1ED6FF",
        "text_main": "#E9F7FF",
        "text_muted": "#93B5C9",
        "accent": "#00B8E6",
        "accent_2": "#155A78",
        "input_bg": "#172C41",
        "input_border": "#275073",
        "chip_bg": "#11364A",
    },
    "Royal Ember": {
        "window_bg": "#12090A",
        "sidebar_bg": "#100809",
        "content_bg": "#1E1012",
        "card_bg": "#2A1417",
        "card_border": "#5B252A",
        "card_active": "#FF7A4E",
        "text_main": "#FFF0EC",
        "text_muted": "#D2AAA0",
        "accent": "#FF5D40",
        "accent_2": "#903226",
        "input_bg": "#3A1D20",
        "input_border": "#6C3034",
        "chip_bg": "#4B2024",
    },
}

CARDS_BY_TAB = {
    "Crystal": [
        ("HC", "Hit Crystal", "Auto place obsidian and hit crystal", ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"]),
        ("SA", "Single Anchor", "Auto place and explode an anchor", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("DA", "Double Anchor", "Auto place and explode two anchors", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("AP", "Anchor Pearl", "Anchor + pearl combo for low-ground entry", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Pearl Slot"]),
    ],
    "Mace": [
        ("MB", "Mace Burst", "Quick swap and burst cycle", ["Keybind", "Delay", "Mace Slot", "Totem Slot"]),
        ("MS", "Mace Swap", "Auto swap for burst windows", ["Keybind", "Swap Delay", "Mace Slot", "Shield Slot"]),
    ],
    "Sword": [
        ("SC", "Sword Crit", "Timed crit sequence", ["Keybind", "Delay", "Sword Slot", "Gap Slot"]),
        ("SP", "Sword Pressure", "Sustain pressure combo", ["Keybind", "Delay", "Sword Slot", "Pearl Slot"]),
    ],
}


class MacroUI(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("67 Macros | Fuck Prestige")
        self.geometry("1220x780")
        self.minsize(1080, 700)

        self.current_theme_name = "Neon Wine"
        self.colors = THEMES[self.current_theme_name].copy()
        self.current_tab = "Crystal"
        self.selected_card = None
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self._setup_layout()
        self._build_sidebar()
        self._build_content_shell()
        self._render_current_tab()

    def _setup_layout(self) -> None:
        self.configure(fg_color=self.colors["window_bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=245, corner_radius=20, fg_color=self.colors["sidebar_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(14, 10), pady=14)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="67 Macros",
            text_color=self.colors["card_active"],
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(18, 4), sticky="w")

        ctk.CTkLabel(
            self.sidebar,
            text="MACRO PANELS",
            text_color=self.colors["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).grid(row=1, column=0, padx=18, pady=(6, 8), sticky="w")

        tabs = [("💎  Crystal", "Crystal"), ("🔨  Mace", "Mace"), ("⚔️  Sword", "Sword"), ("🎨  Themes", "Themes")]
        for i, (label, tab_name) in enumerate(tabs, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=40,
                corner_radius=12,
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                command=lambda t=tab_name: self._switch_tab(t),
            )
            btn.grid(row=i, column=0, padx=14, pady=6, sticky="ew")
            self.nav_buttons[tab_name] = btn

        self._refresh_nav_styles()

    def _build_content_shell(self) -> None:
        self.content_shell = ctk.CTkFrame(self, corner_radius=24, fg_color=self.colors["content_bg"])
        self.content_shell.grid(row=0, column=1, sticky="nsew", padx=(0, 14), pady=14)
        self.content_shell.grid_columnconfigure(0, weight=1)
        self.content_shell.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self.content_shell,
            text="",
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, padx=28, pady=(22, 2), sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.content_shell,
            text="",
            text_color=self.colors["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self.subtitle_label.grid(row=0, column=0, padx=30, pady=(66, 12), sticky="w")

        self.page_frame = ctk.CTkFrame(self.content_shell, fg_color="transparent")
        self.page_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))

    def _switch_tab(self, tab_name: str) -> None:
        self.current_tab = tab_name
        self.selected_card = None
        self._refresh_nav_styles()
        self._render_current_tab()

    def _refresh_nav_styles(self) -> None:
        for name, btn in self.nav_buttons.items():
            active = name == self.current_tab
            btn.configure(
                fg_color=self.colors["accent_2"] if active else "transparent",
                hover_color=self.colors["card_border"],
                text_color=self.colors["text_main"],
                border_width=2 if active else 1,
                border_color=self.colors["card_active"] if active else self.colors["card_border"],
            )

    def _clear_page(self) -> None:
        for w in self.page_frame.winfo_children():
            w.destroy()

    def _render_current_tab(self) -> None:
        self._clear_page()
        if self.current_tab == "Themes":
            self.title_label.configure(text="Theme Lab")
            self.subtitle_label.configure(text="One-click visual presets. Switch instantly and tune later.")
            self._render_themes_page()
        else:
            self.title_label.configure(text=f"{self.current_tab} Macros")
            self.subtitle_label.configure(text="Clickable placeholders with glow feedback.")
            self._render_macros_page(self.current_tab)

    def _render_macros_page(self, tab_name: str) -> None:
        self.page_frame.grid_columnconfigure((0, 1), weight=1)
        cards = CARDS_BY_TAB[tab_name]
        self.card_widgets = []
        for idx, data in enumerate(cards):
            row, col = idx // 2, idx % 2
            card = self._create_macro_card(self.page_frame, data)
            card.grid(row=row, column=col, sticky="nsew", padx=12, pady=12)
            self.card_widgets.append(card)

    def _create_macro_card(self, parent: ctk.CTkFrame, data: tuple) -> ctk.CTkFrame:
        abbr, title, desc, fields = data
        card = ctk.CTkFrame(parent, fg_color=self.colors["card_bg"], corner_radius=18, border_width=2, border_color=self.colors["card_border"])
        card.grid_columnconfigure(1, weight=1)

        chip = ctk.CTkLabel(
            card,
            text=abbr,
            width=44,
            height=44,
            corner_radius=12,
            fg_color=self.colors["chip_bg"],
            text_color=self.colors["card_active"],
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        )
        chip.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="nw")

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, padx=(2, 12), pady=(12, 8), sticky="new")
        info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(info, text=title, text_color=self.colors["text_main"], font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info, text=desc, text_color=self.colors["text_muted"], font=ctk.CTkFont(family="Segoe UI", size=13)).grid(row=1, column=0, sticky="w")

        power_btn = ctk.CTkButton(
            info,
            text="⏻",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=self.colors["input_bg"],
            hover_color=self.colors["card_active"],
            command=lambda c=card, t=title: self._activate_card(c, t),
        )
        power_btn.grid(row=0, column=1, rowspan=2, padx=(8, 0), sticky="ne")

        for i, field in enumerate(fields, start=1):
            ctk.CTkLabel(card, text=field, text_color=self.colors["text_muted"], font=ctk.CTkFont(family="Segoe UI", size=14)).grid(
                row=i, column=0, padx=14, pady=6, sticky="w"
            )
            ctk.CTkButton(
                card,
                text="PLACEHOLDER",
                height=30,
                width=132,
                corner_radius=8,
                fg_color=self.colors["input_bg"],
                hover_color=self.colors["card_active"],
                border_width=1,
                border_color=self.colors["input_border"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=lambda c=card, f=field: self._activate_card(c, f),
            ).grid(row=i, column=1, padx=12, pady=6, sticky="e")

        return card

    def _activate_card(self, card: ctk.CTkFrame, source: str) -> None:
        if self.selected_card is not None:
            self.selected_card.configure(border_color=self.colors["card_border"], border_width=2)
        self.selected_card = card
        self.selected_card.configure(border_color=self.colors["card_active"], border_width=3)
        print(f"Clicked: {source}")

    def _render_themes_page(self) -> None:
        self.page_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.page_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.page_frame,
            text="Choose a theme preset",
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=14, pady=(8, 10), sticky="w")

        for idx, (theme_name, theme_colors) in enumerate(THEMES.items()):
            card = ctk.CTkFrame(self.page_frame, fg_color=theme_colors["card_bg"], corner_radius=18, border_width=2, border_color=theme_colors["card_border"])
            card.grid(row=1, column=idx, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(
                card,
                text=theme_name,
                text_color=theme_colors["text_main"],
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            ).pack(anchor="w", padx=14, pady=(14, 8))

            swatches = ctk.CTkFrame(card, fg_color="transparent")
            swatches.pack(fill="x", padx=12, pady=(0, 10))
            for k in ["window_bg", "card_bg", "card_active", "accent"]:
                ctk.CTkFrame(swatches, width=24, height=24, corner_radius=8, fg_color=theme_colors[k]).pack(side="left", padx=4)

            ctk.CTkButton(
                card,
                text="Apply Theme",
                fg_color=theme_colors["accent_2"],
                hover_color=theme_colors["card_active"],
                text_color=theme_colors["text_main"],
                border_width=1,
                border_color=theme_colors["card_active"],
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                command=lambda n=theme_name: self._apply_theme(n),
            ).pack(fill="x", padx=12, pady=(6, 14))

    def _apply_theme(self, theme_name: str) -> None:
        self.current_theme_name = theme_name
        self.colors = THEMES[theme_name].copy()
        self.configure(fg_color=self.colors["window_bg"])
        self.sidebar.configure(fg_color=self.colors["sidebar_bg"])
        self.content_shell.configure(fg_color=self.colors["content_bg"])
        self._refresh_nav_styles()
        self._render_current_tab()


if __name__ == "__main__":
    app = MacroUI()
    app.mainloop()
