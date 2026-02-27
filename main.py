import customtkinter as ctk

ctk.set_appearance_mode("dark")

# Easy-to-change color palette
COLORS = {
    "window_bg": "#140812",
    "topbar_bg": "#1A0A18",
    "sidebar_bg": "#11070F",
    "panel_bg": "#1C0C1A",
    "panel_alt": "#1A0A16",
    "card_bg": "#2A1025",
    "card_border": "#4D1B3F",
    "card_glow": "#D84A8A",
    "text_main": "#F4E7F0",
    "text_muted": "#B89AB1",
    "accent": "#D84284",
    "accent_dark": "#99255B",
    "input_bg": "#2D1728",
    "input_border": "#4A2940",
}

MACRO_CARDS = [
    {
        "abbr": "HC",
        "title": "Hit Crystal",
        "desc": "Auto place obsidian and hit crystal",
        "fields": ["Keybind", "Delay", "Crystal Slot", "Obsidian Slot"],
    },
    {
        "abbr": "SA",
        "title": "Single Anchor",
        "desc": "Auto place and explode an anchor",
        "fields": ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"],
    },
    {
        "abbr": "DA",
        "title": "Double Anchor",
        "desc": "Auto place and explode two anchors",
        "fields": ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Totem/Explode Slot"],
    },
    {
        "abbr": "AP",
        "title": "Anchor Pearl",
        "desc": "Anchor and pearl right after to get low ground first",
        "fields": ["Keybind", "Delay", "Anchor Slot", "Glowstone Slot", "Pearl Slot"],
    },
]


class CrystalUI(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("198 Macros | Prestige Client")
        self.geometry("1200x760")
        self.configure(fg_color=COLORS["window_bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_topbar()
        self._build_sidebar()
        self._build_content()

    def _build_topbar(self) -> None:
        top = ctk.CTkFrame(self, fg_color=COLORS["topbar_bg"], corner_radius=0, height=44)
        top.grid(row=0, column=0, columnspan=2, sticky="nsew")
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top,
            text="198 Macros  |  By Prestige Client",
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

    def _build_sidebar(self) -> None:
        side = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"], corner_radius=0, width=220)
        side.grid(row=1, column=0, sticky="nsew")
        side.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(side, text="MACROS", text_color=COLORS["text_muted"], font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=18, pady=(16, 6), sticky="w"
        )

        for i, name in enumerate(["Crystal", "Mace", "Sword"], start=1):
            selected = name == "Crystal"
            ctk.CTkButton(
                side,
                text=name,
                command=lambda n=name: self._placeholder_action(n),
                fg_color=COLORS["accent_dark"] if selected else "transparent",
                hover_color=COLORS["card_border"],
                text_color=COLORS["text_main"],
                border_width=1 if selected else 0,
                border_color=COLORS["accent"],
                anchor="w",
                height=36,
            ).grid(row=i, column=0, padx=14, pady=5, sticky="ew")

        ctk.CTkLabel(side, text="OTHER", text_color=COLORS["text_muted"], font=ctk.CTkFont(size=12)).grid(
            row=5, column=0, padx=18, pady=(20, 6), sticky="w"
        )
        ctk.CTkButton(
            side,
            text="Themes",
            command=lambda: self._placeholder_action("Themes"),
            fg_color="transparent",
            hover_color=COLORS["card_border"],
            text_color=COLORS["text_main"],
            anchor="w",
            height=36,
        ).grid(row=6, column=0, padx=14, pady=5, sticky="ew")

        footer = ctk.CTkFrame(side, fg_color=COLORS["panel_alt"], corner_radius=12)
        footer.grid(row=9, column=0, padx=12, pady=12, sticky="ew")
        ctk.CTkLabel(footer, text="Efe_Bey0", text_color=COLORS["text_main"], font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        ctk.CTkLabel(footer, text="UID: 85", text_color=COLORS["text_muted"], font=ctk.CTkFont(size=11)).pack(
            anchor="w", padx=10, pady=(0, 8)
        )

    def _build_content(self) -> None:
        body = ctk.CTkFrame(self, fg_color=COLORS["panel_bg"], corner_radius=0)
        body.grid(row=1, column=1, sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(body, text="Crystal Macros", text_color=COLORS["text_main"], font=ctk.CTkFont(size=34, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=26, pady=(20, 2), sticky="w"
        )
        ctk.CTkLabel(
            body,
            text="Configure your end crystal PvP automation",
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, columnspan=2, padx=28, pady=(0, 12), sticky="w")

        for idx, card in enumerate(MACRO_CARDS):
            row = 2 + idx // 2
            col = idx % 2
            panel = self._macro_card(body, card)
            panel.grid(row=row, column=col, padx=14, pady=14, sticky="nsew")

    def _macro_card(self, parent: ctk.CTkFrame, data: dict) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=2,
            border_color=COLORS["card_border"],
        )
        card.grid_columnconfigure(1, weight=1)

        badge = ctk.CTkLabel(
            card,
            text=data["abbr"],
            width=42,
            height=42,
            corner_radius=10,
            fg_color=COLORS["accent_dark"],
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        badge.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="nw")

        heading = ctk.CTkFrame(card, fg_color="transparent")
        heading.grid(row=0, column=1, padx=(0, 12), pady=(12, 8), sticky="new")
        heading.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            heading,
            text=data["title"],
            text_color=COLORS["text_main"],
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(heading, text=data["desc"], text_color=COLORS["text_muted"], font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, sticky="w"
        )
        ctk.CTkButton(
            heading,
            text="⏻",
            width=28,
            height=28,
            corner_radius=14,
            fg_color=COLORS["input_bg"],
            hover_color=COLORS["card_border"],
            command=lambda: self._placeholder_action(f"Toggle {data['title']}"),
        ).grid(row=0, column=1, rowspan=2, padx=(6, 0), sticky="ne")

        for i, field in enumerate(data["fields"], start=1):
            ctk.CTkLabel(card, text=field, text_color=COLORS["text_muted"], font=ctk.CTkFont(size=14)).grid(
                row=i, column=0, padx=14, pady=6, sticky="w"
            )
            ctk.CTkButton(
                card,
                text="PLACEHOLDER",
                command=lambda f=field: self._placeholder_action(f),
                fg_color=COLORS["input_bg"],
                hover_color=COLORS["card_border"],
                border_width=1,
                border_color=COLORS["input_border"],
                text_color=COLORS["text_main"],
                width=130,
                height=30,
                corner_radius=7,
            ).grid(row=i, column=1, padx=12, pady=6, sticky="e")

        return card

    @staticmethod
    def _placeholder_action(name: str) -> None:
        print(f"Placeholder pressed: {name}")


if __name__ == "__main__":
    app = CrystalUI()
    app.mainloop()
