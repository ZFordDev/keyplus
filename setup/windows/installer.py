"""
While normally i would use inno setup as a standard be done with it option
a custom installer engine gives more control over future deployment and allows for a more modernized UI experience.
This is a custom installer engine for Windows that provides a modernized UI experience for installing the Key
Linux does not need a installer by design, and MacOS is not supported at this time. This installer engine is designed to be used with the KeyPlus application.
The installer engine is built using Python and Tkinter, and it provides a simple and intuitive interface
i might move to making this UI pyside6 in future but for now tkinter is sufficient for the needs of this installer engine.
""" 
import tkinter as tk
from tkinter import messagebox, ttk
from engine import InstallerEngine

class ModernInstallerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyPlus Installation Wizard")
        self.root.geometry("540x520")  # Expanded height
        self.root.resizable(False, False)
        
        self.root.configure(bg="#ffffff")
        
        self.engine = InstallerEngine(vendor_name="ZFordDev", app_name="KeyPlus")
        
        self.add_to_path_var = tk.BooleanVar(value=True)
        self.create_shortcut_var = tk.BooleanVar(value=True)
        self.create_uninstaller_var = tk.BooleanVar(value=True)

        self.apply_theme_styles()
        self.assemble_ui()

    def apply_theme_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(".", background="#ffffff", foreground="#0f172a")

        self.style.configure("Header.TLabel", font=("Segoe UI", 15, "bold"), foreground="#0f172a", background="#f8fafc")
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10, "bold"), foreground="#334155")
        self.style.configure("Info.TLabel", font=("Segoe UI", 9), foreground="#64748b")
        
        self.style.configure("TEntry", fieldbackground="#f1f5f9", bordercolor="#cbd5e1", padding=6)
        
        self.style.configure("TCheckbutton", font=("Segoe UI", 10), background="#ffffff")
        self.style.map("TCheckbutton", foreground=[("active", "#0f172a")])

        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#2563eb", padding="12 6")
        self.style.map("Action.TButton", background=[("active", "#1d4ed8"), ("disabled", "#94a3b8")])
        
        self.style.configure("Secondary.TButton", font=("Segoe UI", 10), foreground="#475569", background="#f1f5f9", padding="12 6")
        self.style.map("Secondary.TButton", background=[("active", "#e2e8f0")])

        self.style.configure("Flat.Horizontal.TProgressbar", thickness=6, troughcolor="#e2e8f0", background="#2563eb")

    def assemble_ui(self):
        header_frame = tk.Frame(self.root, bg="#f8fafc", height=75)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ttk.Label(header_frame, text=f"Install {self.engine.app_name} Package", style="Header.TLabel").pack(padx=24, pady=24, anchor="w")

        tk.Frame(self.root, bg="#e2e8f0", height=1).pack(fill="x")

        self.content_frame = ttk.Frame(self.root, padding="28 24 28 24")  # Increased bottom padding
        self.content_frame.pack(fill="both", expand=True)

        ttk.Label(self.content_frame, text="Where should KeyPlus live?", style="Sub.TLabel").pack(anchor="w", pady=(0, 6))
        
        self.dir_entry = ttk.Entry(self.content_frame, font=("Segoe UI", 10))
        self.dir_entry.insert(0, str(self.engine.default_dir))
        self.dir_entry.pack(fill="x", pady=(0, 24))

        ttk.Label(self.content_frame, text="Extra Setup Options", style="Sub.TLabel").pack(anchor="w", pady=(0, 8))
        
        ttk.Checkbutton(self.content_frame, text="Add KeyPlus to the command line (so you can type 'keyplus' and it just works)", variable=self.add_to_path_var).pack(anchor="w", pady=5)
        ttk.Checkbutton(self.content_frame, text="Put a shiny KeyPlus icon on your desktop (for the click‑first people)", variable=self.create_shortcut_var).pack(anchor="w", pady=5)
        ttk.Checkbutton(self.content_frame, text="Add an uninstaller (for when you decide to break my heart and remove it)", variable=self.create_uninstaller_var).pack(anchor="w", pady=5)

        ttk.Label(self.content_frame, text="KeyPlus will be installed inside your LocalAppData folder. Nice and tidy.", style="Info.TLabel").pack(anchor="w", pady=(24, 0))

        self.status_frame = ttk.Frame(self.content_frame)
        self.status_label = ttk.Label(self.status_frame, text="Installing KeyPlus… please hold your excitement.", style="Info.TLabel")
        self.progress_bar = ttk.Progressbar(self.status_frame, style="Flat.Horizontal.TProgressbar", mode="indeterminate")

        footer_frame = ttk.Frame(self.root, padding="12 16 28 20")
        footer_frame.pack(fill="x", side="bottom")

        self.install_btn = ttk.Button(footer_frame, text="Install", style="Action.TButton", command=self.trigger_install)
        self.install_btn.pack(side="right", padx=(10, 0))
        
        self.cancel_btn = ttk.Button(footer_frame, text="Cancel", style="Secondary.TButton", command=self.root.quit)
        self.cancel_btn.pack(side="right")

    def trigger_install(self):
        """This button does not launch rockets, but it WILL install KeyPlus."""
        self.install_btn.state(["disabled"])
        self.cancel_btn.state(["disabled"])
        self.dir_entry.state(["disabled"])
        
        self.status_frame.pack(fill="x", pady=(20, 0))
        self.status_label.pack(anchor="w", pady=(0, 4))
        self.progress_bar.pack(fill="x")
        self.progress_bar.start(12)
        
        self.root.update_idletasks()
        self.root.after(800, self.run_engine_deployment)

    def run_engine_deployment(self):
        target_path = self.dir_entry.get().strip()
        try:
            final_destination = self.engine.execute_deployment(
                target_directory=target_path,
                add_to_path=self.add_to_path_var.get(),
                create_shortcut=self.create_shortcut_var.get(),
            )
            
            self.progress_bar.stop()
            messagebox.showinfo(
                "Success", 
                f"{self.engine.app_name} is now installed!\n\n"
                f"Location: {final_destination}\n\n"
                "You can now run 'keyplus' from the command line or use the desktop icon.\n\n"
                f"An uninstaller was added too (just in case):\n{final_destination / 'uninstall.bat'}"
            )
            self.root.quit()
            
        except Exception as e:
            self.progress_bar.stop()
            self.status_frame.pack_forget()
            messagebox.showerror("Oops!", f"Something went wrong during installation:\n\n{str(e)}\n\nNothing was damaged. You can try again!")
            
            self.install_btn.state(["!disabled"])
            self.cancel_btn.state(["!disabled"])
            self.dir_entry.state(["!disabled"])

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernInstallerUI(root)
    root.mainloop()
