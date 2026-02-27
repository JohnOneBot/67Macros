import customtkinter as ctk

ctk.set_appearance_mode("dark")

THEMES = {
    "Arctic": {
        "window": "#070e18",
        "chrome": "#141b24",
        "sidebar": "#050d1a",
        "panel": "#07182b",
        "card": "#0d2742",
        "card_edge": "#2f4f71",
        "text": "#e9f6ff",
        "muted": "#9cc0da",
        "accent": "#3fd8ff",
        "accent_2": "#24a6cf",
        "input": "#1a3a5f",
        "input_edge": "#3c668d",
        "glow_soft": "#123654",
        "glow_strong": "#69e2ff",
    },
    "Neon Violet": {
        "window": "#130917",
        "chrome": "#1a1221",
        "sidebar": "#120716",
        "panel": "#1b0f24",
        "card": "#271436",
        "card_edge": "#5e2f79",
        "text": "#faedff",
        "muted": "#d0aee2",
        "accent": "#e062ff",
        "accent_2": "#b144d6",
        "input": "#39204e",
        "input_edge": "#744796",
        "glow_soft": "#432352",
        "glow_strong": "#f090ff",
    },
    "Carbon": {
        "window": "#101214",
        "chrome": "#191d20",
        "sidebar": "#111518",
        "panel": "#171d24",
        "card": "#1f2831",
        "card_edge": "#374755",
        "text": "#f2f6fa",
        "muted": "#a2b0be",
        "accent": "#6be8ff",
        "accent_2": "#3f9db1",
        "input": "#283440",
        "input_edge": "#4a5e72",
        "glow_soft": "#2a3e4c",
        "glow_strong": "#9befff",
    },
}

CARDS_BY_TAB = {
    "Crystal": [
        ("HC", "Hit Crystal", "Auto place obsidian and hit crystal", ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"]),
        ("SA", "Single Anchor", "Auto place and explode an anchor", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("DA", "Double Anchor", "Auto place and explode two anchors", ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"]),
        ("SHC", "Slow Hit Crystal", "Optimized crystal hit timing", ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"]),
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


class MacroUI(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("67 Macros | Fuck Prestige")
        self.geometry("1320x860")
        self.minsize(1080, 700)

        self.current_theme = "Arctic"
        self.current_tab = "Crystal"
        self.selected = None
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self._rebuild()

    @property
    def c(self) -> dict:
        return THEMES[self.current_theme]

    def _rebuild(self) -> None:
        for w in self.winfo_children():
            w.destroy()

        self.configure(fg_color=self.c["window"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color=self.c["chrome"], corner_radius=0, height=44)
        top.grid(row=0, column=0, columnspan=2, sticky="nsew")
        ctk.CTkLabel(
            top,
            text="67 Macros  |  Fuck Prestige",
            text_color=self.c["text"],
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
        ).pack(side="left", padx=12, pady=8)

        self._build_sidebar()
        self._build_content()
        self._refresh_nav()
        self._render_page()

    def _build_sidebar(self) -> None:
        shell = ctk.CTkFrame(self, fg_color=self.c["glow_soft"], corner_radius=20)
        shell.grid(row=1, column=0, sticky="nsew", padx=(10, 6), pady=10)

        self.sidebar = ctk.CTkFrame(shell, fg_color=self.c["sidebar"], corner_radius=18)
        self.sidebar.pack(fill="both", expand=True, padx=1, pady=1)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(9, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="67 Macros",
            text_color=self.c["accent"],
            font=ctk.CTkFont(family="Segoe UI", size=44, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 8))

        nav = [("◈ Crystal", "Crystal"), ("⚒ Mace", "Mace"), ("⚔ Sword", "Sword"), ("◉ Themes", "Themes")]
        self.nav_buttons.clear()
        for i, (label, tab) in enumerate(nav, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                height=40,
                corner_radius=12,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                command=lambda t=tab: self._switch_tab(t),
            )
            btn.grid(row=i, column=0, sticky="ew", padx=12, pady=6)
            self.nav_buttons[tab] = btn

    def _build_content(self) -> None:
        shell = ctk.CTkFrame(self, fg_color=self.c["glow_soft"], corner_radius=20)
        shell.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        self.content = ctk.CTkFrame(shell, fg_color=self.c["panel"], corner_radius=18)
        self.content.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(
            self.content,
            text="",
            text_color=self.c["text"],
            font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
        )
        self.header.grid(row=0, column=0, sticky="w", padx=22, pady=(16, 2))

        self.sub = ctk.CTkLabel(
            self.content,
            text="",
            text_color=self.c["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=20),
        )
        self.sub.grid(row=0, column=0, sticky="w", padx=24, pady=(64, 8))

        self.page = ctk.CTkFrame(self.content, fg_color="transparent")
        self.page.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def _refresh_nav(self) -> None:
        for name, btn in self.nav_buttons.items():
            active = name == self.current_tab
            btn.configure(
                fg_color=self.c["accent_2"] if active else "transparent",
                hover_color=self.c["accent"],
                border_width=2 if active else 1,
                border_color=self.c["glow_strong"] if active else self.c["input_edge"],
                text_color=self.c["text"],
            )

    def _switch_tab(self, tab: str) -> None:
        self.current_tab = tab
        self.selected = None
        self._refresh_nav()
        self._render_page()

    def _render_page(self) -> None:
        for w in self.page.winfo_children():
            w.destroy()

        if self.current_tab == "Themes":
            self.header.configure(text="Theme Presets")
            self.sub.configure(text="Compact palette strip with instant apply")
            self._render_themes()
            return

        self.header.configure(text=f"{self.current_tab} Macros")
        self.sub.configure(text="Configure your macros with cleaner glow interactions")

        self.page.grid_columnconfigure((0, 1), weight=1)
        cards = CARDS_BY_TAB[self.current_tab]
        for i, card in enumerate(cards):
            r, cidx = i // 2, i % 2
            self._build_card(self.page, card).grid(row=r, column=cidx, sticky="nsew", padx=8, pady=8)

    def _build_card(self, parent: ctk.CTkFrame, data: tuple) -> ctk.CTkFrame:
        abbr, title, desc, fields = data

        glow = ctk.CTkFrame(parent, fg_color=self.c["glow_soft"], corner_radius=16)
        edge = ctk.CTkFrame(glow, fg_color=self.c["card_edge"], corner_radius=15)
        edge.pack(fill="both", expand=True, padx=1, pady=1)
        card = ctk.CTkFrame(edge, fg_color=self.c["card"], corner_radius=14)
        card.pack(fill="both", expand=True, padx=1, pady=1)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text=abbr,
            text_color=self.c["accent"],
            fg_color=self.c["input"],
            width=40,
            height=40,
            corner_radius=11,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(12, 8), sticky="nw")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=1, sticky="new", padx=(2, 10), pady=(10, 8))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text=title, text_color=self.c["text"], font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text=desc, text_color=self.c["muted"], font=ctk.CTkFont(family="Segoe UI", size=13)).grid(row=1, column=0, sticky="w")
        ctk.CTkButton(
            top,
            text="⏻",
            width=26,
            height=26,
            corner_radius=13,
            fg_color=self.c["input"],
            hover_color=self.c["accent"],
            command=lambda g=glow, e=edge, t=title: self._activate(g, e, t),
        ).grid(row=0, column=1, rowspan=2, sticky="ne")

        for i, field in enumerate(fields, start=1):
            ctk.CTkLabel(card, text=field, text_color=self.c["muted"], font=ctk.CTkFont(family="Segoe UI", size=13)).grid(row=i, column=0, padx=12, pady=5, sticky="w")
            ctk.CTkButton(
                card,
                text="PLACEHOLDER",
                width=118,
                height=28,
                corner_radius=8,
                fg_color=self.c["input"],
                hover_color=self.c["accent_2"],
                border_width=1,
                border_color=self.c["input_edge"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=lambda g=glow, e=edge, f=field: self._activate(g, e, f),
            ).grid(row=i, column=1, padx=10, pady=5, sticky="e")

        return glow

    def _activate(self, glow: ctk.CTkFrame, edge: ctk.CTkFrame, source: str) -> None:
        if self.selected:
            old_glow, old_edge = self.selected
            old_glow.configure(fg_color=self.c["glow_soft"])
            old_edge.configure(fg_color=self.c["card_edge"])
        glow.configure(fg_color=self.c["glow_strong"])
        edge.configure(fg_color=self.c["accent"])
        self.selected = (glow, edge)
        print(f"placeholder click: {source}")

    def _render_themes(self) -> None:
        self.page.grid_columnconfigure(0, weight=1)
        strip = ctk.CTkFrame(self.page, fg_color="transparent")
        strip.grid(row=0, column=0, sticky="ew")

        for i, (name, palette) in enumerate(THEMES.items()):
            tile = ctk.CTkFrame(strip, fg_color=palette["card"], corner_radius=10, border_width=1, border_color=palette["card_edge"])
            tile.grid(row=0, column=i, sticky="ew", padx=6, pady=6)
            strip.grid_columnconfigure(i, weight=1)

            row = ctk.CTkFrame(tile, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=8)
            ctk.CTkLabel(row, text=name, text_color=palette["text"], font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(side="left")

            sw = ctk.CTkFrame(row, fg_color="transparent")
            sw.pack(side="right")
            for key in ["window", "card", "accent", "glow_strong"]:
                ctk.CTkFrame(sw, fg_color=palette[key], width=16, height=10, corner_radius=3).pack(side="left", padx=2)

            ctk.CTkButton(
                tile,
                text="Apply",
                height=24,
                corner_radius=7,
                fg_color=palette["accent_2"],
                hover_color=palette["accent"],
                text_color=palette["text"],
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                command=lambda n=name: self._apply_theme(n),
            ).pack(fill="x", padx=8, pady=(0, 8))

    def _apply_theme(self, name: str) -> None:
        self.current_theme = name
        self.selected = None
        self._rebuild()


if __name__ == "__main__":
    app = MacroUI()
    app.mainloop()
