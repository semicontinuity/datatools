import tkinter as tk


class Popup:
    result: int|None

    def __init__(self, root, items: list[str], label: str, title="Entity"):
        self.result = None
        self.root = root
        self.root.title(title)

        # Create a frame to hold the menu items
        self.frame = tk.Frame(root, bg="lightgray", padx=10, pady=10)
        self.frame.pack(padx=10, pady=10)

        # Add a label on top of the menu
        i = 0

        self.entity_label = tk.Label(
            self.frame,
            text=label,
            font=("Courier", 20,),
            bg="lightgray",
            pady=10,
        )
        self.entity_label.grid(row=i, column=0, sticky="ew")  # Place at the top
        i += 1

        # self.label = tk.Label(
        #     self.frame,
        #     text="Send",
        #     font=("Arial", 20, "bold"),
        #     bg="lightgray",
        #     pady=10,
        # )
        # self.label.grid(row=i, column=0, sticky="ew")  # Place at the top
        # i += 1

        # List of menu items
        self.menu_items = items
        self.current_index = 0

        # Create labels for each menu item
        self.labels = []
        for item in self.menu_items:
            label = tk.Label(
                self.frame,
                text=item,
                font=("Arial", 20),
                padx=10,
                pady=5,
                anchor="w",
                bg="lightgray",
            )
            label.grid(row=i, column=0, sticky="ew")  # Start from row 1 (below the title)
            self.labels.append(label)
            i += 1

        # Configure the column to expand with the largest label
        self.frame.columnconfigure(0, weight=1)

        # Highlight the first item initially
        self.update_selection()

        # Bind keyboard events
        root.bind("<Up>", self.navigate_up)
        root.bind("<Down>", self.navigate_down)
        root.bind("<Return>", self.select_item)
        root.bind("<Escape>", self.close_app)  # Bind Escape key to close the app

        # Center the window on the screen after sizing
        self.root.update_idletasks()  # Ensure dimensions are calculated
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")

    def update_selection(self):
        """Highlight the currently selected menu item."""
        for i, label in enumerate(self.labels):
            if i == self.current_index:
                label.config(bg="blue", fg="white")
            else:
                label.config(bg="lightgray", fg="black")

    def navigate_up(self, event):
        """Move selection up."""
        self.current_index = (self.current_index - 1) % len(self.menu_items)
        self.update_selection()

    def navigate_down(self, event):
        """Move selection down."""
        self.current_index = (self.current_index + 1) % len(self.menu_items)
        self.update_selection()

    def select_item(self, event):
        """Handle item selection."""
        self.result = self.current_index
        self.close_app()  # Close the app after selection

    def close_app(self, event=None):
        """Close the application."""
        self.root.destroy()


def choose(items: list[str], label: str) -> int|None:
    root = tk.Tk()
    popup = Popup(root, items, label)
    root.mainloop()
    return popup.result
