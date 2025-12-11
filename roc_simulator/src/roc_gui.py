import datetime
import time
import tkinter as tk
import sys

from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkintermapview import TkinterMapView

# Don't update map widget more often than this to avoid flickering
MAP_WIDGET_UPDATE_CAP = 5

# -------------------------------------------------------
# GUI start
# -------------------------------------------------------
class RocGui:
    def __init__(self):
        root = tk.Tk()
        root.title("Vessel Readiness Panel – Interactive")
        root.geometry("1800x980")

        root.columnconfigure(0, weight=3, uniform="cols")
        root.columnconfigure(1, weight=3, uniform="cols")
        root.columnconfigure(2, weight=2, uniform="cols")
        root.rowconfigure(0, weight=3)
        root.rowconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        # Should exit main loop on closing window
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        ## First column

        # -------------------------------------------------------
        # VEHICLE MAP PANEL (live-map)
        # -------------------------------------------------------
        frame_map = tk.LabelFrame(root, text="Vessel position map")
        frame_map.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        map_widget = TkinterMapView(frame_map, width=600, height=500, corner_radius=0)
        map_widget.set_position(59.3293, 18.0686)  # Stockholm example
        map_widget.set_zoom(4)
        map_widget.pack(expand=True, fill="both")
        map_widget.set_marker(63.0888, 21.5617, text="ROC Vaasa", marker_color_circle="white", marker_color_outside="cyan")
        map_widget.set_marker(63.7045, 20.3530, text="ROC Umeå", marker_color_circle="yellow", marker_color_outside="cyan")

        self.marker = None
        self.root = root
        self.frame_map = frame_map
        self.map_widget = map_widget
        self.map_widget_last_updated_time = 0

        # -------------------------------------------------------
        # ROC info
        # -------------------------------------------------------
        frame_roc = tk.LabelFrame(root, text="ROC information", padx=10, pady=10)
        frame_roc.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Configure grid inside the frame
        frame_roc.columnconfigure(0, weight=1, pad=5)
        frame_roc.columnconfigure(1, weight=3, pad=5)

        # ROC identifier row
        tk.Label(frame_roc, text="ROC identifier:", font=("Arial", 12), anchor="w").grid(row=0, column=0, sticky="w")
        roc_id_label = tk.Label(frame_roc, text="ROC_1", font=("Arial", 12, "bold"), anchor="w")
        roc_id_label.grid(row=0, column=1, sticky="w")

        # ROC location row
        tk.Label(frame_roc, text="ROC location:", font=("Arial", 12), anchor="w").grid(row=1, column=0, sticky="w")
        roc_location_label = tk.Label(frame_roc, text="Vaasa", font=("Arial", 12, "bold"), anchor="w")
        roc_location_label.grid(row=1, column=1, sticky="w")

        ## Second column

        # -------------------------------------------------------
        # Visualisation area with Zenoh controls
        # -------------------------------------------------------
        frame_visual = tk.LabelFrame(root, text="Visualization / Data Modules")
        frame_visual.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Create control panel
        control_frame = tk.Frame(frame_visual)
        control_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # COG Control
        tk.Label(control_frame, text="Set course Over Ground (COG):", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        cog_entry = tk.Entry(control_frame, font=("Arial", 12), width=15)
        cog_entry.grid(row=0, column=1, padx=10, pady=5)
        cog_send_btn = tk.Button(control_frame, text="Send COG", font=("Arial", 10), 
                                 command=lambda: self.send_cog(cog_entry.get()))
        cog_send_btn.grid(row=0, column=2, padx=5, pady=5)

        # COG Output display
        tk.Label(control_frame, text="Current COG:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        cog_out_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="blue")
        cog_out_label.grid(row=1, column=1, sticky="w", pady=5)

        # SOG Control
        tk.Label(control_frame, text="Set speed Over Ground (SOG):", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        sog_entry = tk.Entry(control_frame, font=("Arial", 12), width=15)
        sog_entry.grid(row=2, column=1, padx=10, pady=5)
        sog_send_btn = tk.Button(control_frame, text="Send SOG", font=("Arial", 10),
                                 command=lambda: self.send_sog(sog_entry.get()))
        sog_send_btn.grid(row=2, column=2, padx=5, pady=5)

        # SOG Output display
        tk.Label(control_frame, text="Current SOG:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        sog_out_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="blue")
        sog_out_label.grid(row=3, column=1, sticky="w", pady=5)

        self.cog_out_label = cog_out_label
        self.sog_out_label = sog_out_label

        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky="ew", pady=15)

        # Position Display
        tk.Label(control_frame, text="Current Position:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", pady=5)

        tk.Label(control_frame, text="Latitude:", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=5)
        lat_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="green")
        lat_label.grid(row=6, column=1, sticky="w", pady=5)

        tk.Label(control_frame, text="Longitude:", font=("Arial", 10)).grid(row=7, column=0, sticky="w", pady=5)
        lon_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="green")
        lon_label.grid(row=7, column=1, sticky="w", pady=5)

        self.lat_label = lat_label
        self.lon_label = lon_label

        # State display
        tk.Label(control_frame, text="Vessel State:", font=("Arial", 10)).grid(row=9, column=0, sticky="w", pady=5)
        state_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="orange")
        state_label.grid(row=9, column=1, sticky="w", pady=5)

        self.state_label = state_label

        ## Third column

        # -------------------------------------------------------
        # INTERACTIVE CHECKLIST
        # -------------------------------------------------------
        frame_checklist = tk.LabelFrame(root, text="Bridge Checklist")
        frame_checklist.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        checklist_items = [
            "Position checked",
            "Course & speed verified",
            "Traffic conditions safe",
        ]

        scroll_canvas = tk.Canvas(frame_checklist)
        scroll_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_checklist, orient="vertical",
                                 command=scroll_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = tk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        check_vars = []

        for item in checklist_items:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(inner_frame, text=item, variable=var, anchor="w")
            chk.pack(fill="x", pady=2)
            check_vars.append((item, var))

        self.check_vars = check_vars

        inner_frame.update_idletasks()
        scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))

        # -------------------------------------------------------
        # NOTES EDITOR
        # -------------------------------------------------------
        frame_notes = tk.LabelFrame(root, text="Remarks about vessel status")
        frame_notes.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        notes_field = ScrolledText(frame_notes, height=5)
        notes_field.pack(expand=True, fill="both")

        # -------------------------------------------------------
        # VEHICLE NAME + TIMER
        # -------------------------------------------------------
        frame_info = tk.Frame(control_frame)
        frame_info.grid(row=10, column=0, sticky="nsew")

        vessel_label = tk.Label(frame_info, text="Vessel Name", font=("Arial", 20))
        vessel_label.pack(pady=10)

        timer_label = tk.Label(frame_info, text="--:--", font=("Arial", 36))
        timer_label.pack(pady=5)

        tk.Label(frame_info, text="Time left until safety gate", font=("Arial", 14)).pack()

        self.vessel_label = vessel_label
        self.timer_label = timer_label

        # -------------------------------------------------------
        # BOTTOM BUTTONS
        # -------------------------------------------------------
        #frame_buttons = tk.Frame(root)
        #frame_buttons.grid(row=2, column=0, columnspan=2, pady=20)

        #btn_ready = tk.Button(
        #    frame_buttons,
        #    text="ASSERT READY",
        #    font=("Arial", 22),
        #    width=15,
        #    bg="green",
        #    command=self.print_check_status
        #)
        #btn_ready.grid(row=0, column=0, padx=40)

        #btn_abort = tk.Button(
        #    frame_buttons,
        #    text="ABORT",
        #    font=("Arial", 22),
        #    width=15,
        #    bg="red",
        #    command=self.handle_abort
        #)
        #btn_abort.grid(row=0, column=1, padx=40)

        # Bit of an ugly hack - but if we get handed this we can properly close
        # the zenoh session and thus properly exit on closing the window.
        self.monitor = None

        print(f"{self.__class__.__name__} initialized.")

    def mainloop(self):
        self.root.mainloop()

    def on_close(self):
        # Close zenoh session properly at exit
        if self.monitor:
            self.monitor.session.close()

        self.root.quit()
        self.root.destroy()

    def send_cog(self, cog):
        print(f"(Placeholder) Send COG: {cog}")

    def send_sog(self, sog):
        print(f"(Placeholder) Send SOG: {sog}")

    def print_check_status(self):
        print("\n--- CHECKLIST STATUS ---")
        for item, var in self.check_vars:
            print(f"{item}: {'✓' if var.get() else '✗'}")
        print("-------------------------\n")

    def handle_abort(self):
        """Handle abort button - stop the vessel"""
        print("\n!!! ABORT BUTTON PRESSED !!!")
        self.send_sog(0)

    # Setup GUI callbacks for ship updates
    def update_cog_out(self, value):
        self.cog_out_label.config(text=value)

    def update_sog_out(self, value):
        self.sog_out_label.config(text=value)

    def update_remote_status(self, value):
        self.state_label.config(text=value)

    def update_remote_time(self, value):
        ## Format into hh:mm:ss at one second precision
        time_fmt = str(datetime.timedelta(seconds=int(value)))
        self.timer_label.config(text=time_fmt)

    def update_vessel_name(self, value):
        self.vessel_label.config(text=value)

    # Update map position to given lat/long
    def update_map_position(self, lat_val, lon_val):
        try:
            self.lat_label.config(text=lat_val)
            self.lon_label.config(text=lon_val)

            # To counter flickering, set a limit to map widget update frequency
            if time.time() > self.map_widget_last_updated_time + MAP_WIDGET_UPDATE_CAP:
                if self.marker:
                    self.marker.delete()
                self.marker = self.map_widget.set_marker(lat_val, lon_val, text="MASS_0")
                self.map_widget.set_position(lat_val, lon_val)
                self.map_widget_last_updated_time = time.time()
        except ValueError:
            pass

if __name__ == '__main__':
    print("Please run roc_main.py instead.")
    sys.exit(1)
