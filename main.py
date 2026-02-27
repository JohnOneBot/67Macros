import customtkinter as ctk

ctk.set_appearance_mode("dark")

THEMES = {
    "Neon Wine": {
        "window_bg": "#12050F",
        "sidebar_bg": "#0F0410",
        "panel_bg": "#18081A",
        "card_bg": "#221028",
        "text_main": "#F8ECF4",
        "text_muted": "#BD9AB0",
        "accent": "#EC4EA3",
        "accent_soft": "#8D2E60",
        "glow": "#FF69BC",
        "input_bg": "#2D1733",
        "input_border": "#5A325D",
    },
    "Void Cyan": {
        "window_bg": "#060B12",
        "sidebar_bg": "#050912",
        "panel_bg": "#0A1624",
        "card_bg": "#102033",
        "text_main": "#E9F9FF",
        "text_muted": "#9BC1D8",
        "accent": "#22CCFF",
        "accent_soft": "#226B8A",
        "glow": "#3FE6FF",
        "input_bg": "#173046",
        "input_border": "#2B5B7F",
    },
    "Royal Ember": {
        "window_bg": "#130808",
        "sidebar_bg": "#100606",
        "panel_bg": "#1A0E0E",
        "card_bg": "#2A1516",
        "text_main": "#FFF1ED",
        "text_muted": "#D1A59A",
        "accent": "#FF6E4A",
        "accent_soft": "#8D3C2D",
        "glow": "#FF8E6C",
        "input_bg": "#3B1E20",
        "input_border": "#6C3236",
    },
}

CARDS_BY_TAB = {
    "Crystal": [
        ("HC", "Hit Crystal", "Auto place obsidian and hit crystal", ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"]),
        ("SA", "Single Anchor", "Auto place and explode an anchor", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("DA", "Double Anchor", "Auto place and explode two anchors", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("AP", "Anchor Pearl", "Anchor + pearl combo", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Pearl Slot"]),
    ],
    "Mace": [
        ("MB", "Mace Burst", "Burst combo chain", ["Keybind", "Delay", "Mace Slot", "Totem Slot"]),
        ("MS", "Mace Swap", "Quick weapon swap", ["Keybind", "Swap Delay", "Mace Slot", "Shield Slot"]),
    ],
    "Sword": [
        ("SC", "Sword Crit", "Timed crit setup", ["Keybind", "Delay", "Sword Slot", "Gap Slot"]),
        ("SP", "Sword Pressure", "Pressure combo", ["Keybind", "Delay", "Sword Slot", "Pearl Slot"]),
    ],
}


class MacroUI(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("67 Macros | Fuck Prestige")
        self.geometry("1220x780")
        self.minsize(1080, 680)

        self.current_theme_name = "Neon Wine"
        self.current_tab = "Crystal"
        self.selected_card = None
        self.nav_buttons = {}

        self._build_ui()

    @property
    def colors(self) -> dict:
        return THEMES[self.current_theme_name]

    def _build_ui(self) -> None:
        for child in self.winfo_children():
            child.destroy()

        self.configure(fg_color=self.colors["window_bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_glow = ctk.CTkFrame(self, fg_color=self.colors["glow"], corner_radius=26)
        self.sidebar_glow.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=10)

        self.sidebar = ctk.CTkFrame(self.sidebar_glow, fg_color=self.colors["sidebar_bg"], corner_radius=24)
        self.sidebar.pack(fill="both", expand=True, padx=2, pady=2)
        self.sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="67 Macros",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(family="Bahnschrift", size=34, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")

        nav = [("💎 Crystal", "Crystal"), ("🔨 Mace", "Mace"), ("⚔ Sword", "Sword"), ("🎨 Themes", "Themes")]
        self.nav_buttons = {}
        for i, (label, tab_name) in enumerate(nav, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda t=tab_name: self._switch_tab(t),
                corner_radius=12,
                height=40,
                anchor="w",
                font=ctk.CTkFont(family="Bahnschrift", size=16, weight="bold"),
            )
            btn.grid(row=i, column=0, padx=12, pady=6, sticky="ew")
            self.nav_buttons[tab_name] = btn

        self.sidebar.grid_rowconfigure(8, weight=1)

        self.content_glow = ctk.CTkFrame(self, fg_color=self.colors["accent_soft"], corner_radius=28)
        self.content_glow.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        self.content = ctk.CTkFrame(self.content_glow, fg_color=self.colors["panel_bg"], corner_radius=26)
        self.content.pack(fill="both", expand=True, padx=2, pady=2)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.page = ctk.CTkFrame(self.content, fg_color="transparent")
        self.page.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        self._refresh_nav_styles()
        self._render_tab()

    def _refresh_nav_styles(self) -> None:
        for name, btn in self.nav_buttons.items():
            active = name == self.current_tab
            btn.configure(
                fg_color=self.colors["accent_soft"] if active else "transparent",
                hover_color=self.colors["accent"],
                border_width=2 if active else 1,
                border_color=self.colors["glow"] if active else self.colors["input_border"],
                text_color=self.colors["text_main"],
            )

    def _switch_tab(self, tab: str) -> None:
        self.current_tab = tab
        self.selected_card = None
        self._refresh_nav_styles()
        self._render_tab()

    def _clear_page(self) -> None:
        for widget in self.page.winfo_children():
            widget.destroy()

    def _render_tab(self) -> None:
        self._clear_page()
        if self.current_tab == "Themes":
            self._render_theme_tab()
        else:
            self._render_macro_tab(self.current_tab)

    def _render_macro_tab(self, tab_name: str) -> None:
        self.page.grid_columnconfigure((0, 1), weight=1)
        cards = CARDS_BY_TAB[tab_name]
        for idx, data in enumerate(cards):
            r, c = idx // 2, idx % 2
            self._make_glow_card(self.page, data).grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

    def _make_glow_card(self, parent: ctk.CTkFrame, data: tuple) -> ctk.CTkFrame:
        abbr, title, desc, fields = data

        glow = ctk.CTkFrame(parent, fg_color=self.colors["accent_soft"], corner_radius=18)
        card = ctk.CTkFrame(glow, fg_color=self.colors["card_bg"], corner_radius=16, border_width=1, border_color=self.colors["input_border"])
        card.pack(fill="both", expand=True, padx=2, pady=2)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text=abbr,
            text_color=self.colors["accent"],
            fg_color=self.colors["input_bg"],
            width=44,
            height=44,
            corner_radius=12,
            font=ctk.CTkFont(family="Bahnschrift", size=16, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(12, 8), sticky="nw")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=1, sticky="new", padx=(2, 10), pady=(12, 8))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text=title, text_color=self.colors["text_main"], font=ctk.CTkFont(family="Bahnschrift", size=22, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text=desc, text_color=self.colors["text_muted"], font=ctk.CTkFont(family="Bahnschrift", size=13)).grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            top,
            text="⏻",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=self.colors["input_bg"],
            hover_color=self.colors["accent"],
            command=lambda g=glow, c=card, n=title: self._activate_card(g, c, n),
        ).grid(row=0, column=1, rowspan=2, padx=(8, 0), sticky="ne")

        for i, field in enumerate(fields, start=1):
            ctk.CTkLabel(card, text=field, text_color=self.colors["text_muted"], font=ctk.CTkFont(family="Bahnschrift", size=14)).grid(
                row=i, column=0, padx=12, pady=6, sticky="w"
            )
            ctk.CTkButton(
                card,
                text="PLACEHOLDER",
                height=30,
                width=130,
                corner_radius=8,
                fg_color=self.colors["input_bg"],
                hover_color=self.colors["accent"],
                border_width=1,
                border_color=self.colors["input_border"],
                text_color=self.colors["text_main"],
                font=ctk.CTkFont(family="Bahnschrift", size=12, weight="bold"),
                command=lambda g=glow, c=card, f=field: self._activate_card(g, c, f),
            ).grid(row=i, column=1, padx=10, pady=6, sticky="e")

        glow.inner = card
        return glow

    def _activate_card(self, glow: ctk.CTkFrame, card: ctk.CTkFrame, source: str) -> None:
        if self.selected_card is not None:
            old_glow, old_card = self.selected_card
            old_glow.configure(fg_color=self.colors["accent_soft"])
            old_card.configure(border_color=self.colors["input_border"], border_width=1)

        glow.configure(fg_color=self.colors["glow"])
        card.configure(border_color=self.colors["accent"], border_width=2)
        self.selected_card = (glow, card)
        print(f"clicked: {source}")

    def _render_theme_tab(self) -> None:
        self.page.grid_columnconfigure(0, weight=1)
        self.page.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.page,
            text="Themes",
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(family="Bahnschrift", size=24, weight="bold"),
        ).grid(row=0, column=0, padx=8, pady=(0, 8), sticky="w")

        strip = ctk.CTkFrame(self.page, fg_color="transparent")
        strip.grid(row=1, column=0, sticky="new")

        for i, (name, palette) in enumerate(THEMES.items()):
            tile_glow = ctk.CTkFrame(strip, fg_color=palette["accent_soft"], corner_radius=12)
            tile_glow.grid(row=0, column=i, padx=8, pady=8, sticky="ew")
            strip.grid_columnconfigure(i, weight=1)

            tile = ctk.CTkFrame(tile_glow, fg_color=palette["card_bg"], corner_radius=10)
            tile.pack(fill="both", expand=True, padx=2, pady=2)

            row = ctk.CTkFrame(tile, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=10)
            ctk.CTkLabel(
                row,
                text=name,
                text_color=palette["text_main"],
                font=ctk.CTkFont(family="Bahnschrift", size=13, weight="bold"),
            ).pack(side="left")

            sw = ctk.CTkFrame(row, fg_color="transparent")
            sw.pack(side="right")
            for key in ["window_bg", "card_bg", "accent", "glow"]:
                ctk.CTkFrame(sw, fg_color=palette[key], corner_radius=4, width=18, height=12).pack(side="left", padx=2)

            ctk.CTkButton(
                tile,
                text="Apply",
                height=26,
                corner_radius=8,
                fg_color=palette["accent_soft"],
                hover_color=palette["accent"],
                text_color=palette["text_main"],
                font=ctk.CTkFont(family="Bahnschrift", size=12, weight="bold"),
                command=lambda n=name: self._apply_theme(n),
            ).pack(fill="x", padx=10, pady=(0, 10))

    def _apply_theme(self, theme_name: str) -> None:
        self.current_theme_name = theme_name
        self.selected_card = None
        self._build_ui()


if __name__ == "__main__":
    app = MacroUI()
    app.mainloop()
