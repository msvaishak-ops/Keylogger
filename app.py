# app.py
"""
Safe Keystroke Logger (Tkinter)
- Records only keys typed into this application's Text widget.
- Logs key events (name + timestamp) and the current text content to keystrokes.log.
- Purpose: learning, typing tests, accessibility research with informed consent.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

LOG_FILE = "keystrokes.log"


def log_event(entry):
    """Append a timestamped entry to the log file."""
    ts = datetime.utcnow().isoformat() + "Z"  # use UTC ISO timestamp
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} {entry}\n")


class KeyLoggerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Safe Keystroke Logger — type inside this window")
        self.minsize(600, 400)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=6)

        self.status_var = tk.StringVar(value="Ready — start typing below")
        ttk.Label(toolbar, textvariable=self.status_var).pack(side="left")

        ttk.Button(toolbar, text="Show Log", command=self.show_log).pack(side="right")
        ttk.Button(toolbar, text="Clear Log", command=self.clear_log_prompt).pack(side="right", padx=(0,6))

        # Text widget (where user types)
        self.text = tk.Text(self, wrap="word", undo=True)
        self.text.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # Bind key events to the Text widget (only active when widget has focus)
        # We'll capture KeyPress events and log a readable representation.
        self.text.bind("<KeyPress>", self.on_keypress)
        self.text.bind("<KeyRelease>", self.on_keyrelease)

        # Info footer
        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=8, pady=(0,8))
        ttk.Label(footer, text="This program logs ONLY keys typed into this window. Use ethically.").pack(side="left")

    def on_keypress(self, event):
        """Handle key press events inside the Text widget."""
        # event.keysym is a readable symbol like 'a', 'Return', 'BackSpace', 'Shift_L'
        keysym = event.keysym
        char = event.char if event.char else ""
        # Create a compact description
        desc = f"PRESS keysym={keysym!s} char={char!r}"
        # Also save snapshot of the last ~200 chars of the Text content (so you can see context)
        content = self.text.get("1.0", "end-1c")
        context = content[-200:].replace("\n", "\\n")
        log_event(f"{desc} | context='{context}'")
        # update status
        self.status_var.set(f"Last: {keysym} at {datetime.now().strftime('%H:%M:%S')}")

    def on_keyrelease(self, event):
        # optional: log releases if you want (commented out to reduce noise)
        pass

    def show_log(self):
        """Open a small window showing the log file contents."""
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("Log file", "No log file found yet.")
            return
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()[-20000:]  # show last chunk
        win = tk.Toplevel(self)
        win.title("Log file preview")
        win.minsize(600, 300)
        txt = tk.Text(win, wrap="word")
        txt.insert("1.0", content)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

    def clear_log_prompt(self):
        if messagebox.askyesno("Clear log", "Permanently delete the log file?"):
            try:
                if os.path.exists(LOG_FILE):
                    os.remove(LOG_FILE)
                messagebox.showinfo("Cleared", "Log file deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete log file: {e}")

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = KeyLoggerApp()
    app.mainloop()
