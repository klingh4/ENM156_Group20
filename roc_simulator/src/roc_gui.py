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

        # Separator
        ttk.Separator(frame_roc, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=10
        )

        # ROC location row
        tk.Label(frame_roc, text="ROC location:", font=("Arial", 12), anchor="w").grid(row=2, column=0, sticky="w")
        roc_location_label = tk.Label(frame_roc, text="Vaasa", font=("Arial", 12, "bold"), anchor="w")
        roc_location_label.grid(row=2, column=1, sticky="w")

        ## Second column
        # --- Vessel Control Frame ---
        frame_control = tk.LabelFrame(root, text="Vessel control", padx=10, pady=10)
        frame_control.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Internal grid configuration
        frame_control.columnconfigure(0, weight=1)
        frame_control.columnconfigure(1, weight=1)
        frame_control.columnconfigure(2, weight=1)


        # -------------------------
        # Section: Speed over ground
        # -------------------------
        tk.Label(frame_control, text="Speed over ground", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Current SOG:", anchor="w").grid(row=1, column=0, sticky="w")
        sog_label = tk.Label(frame_control, text="N/A", anchor="w")
        sog_label.grid(row=1, column=1, sticky="w")

        sog_entry = tk.Entry(frame_control)
        sog_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)
        sog_button = tk.Button(frame_control, text="Set new SOG")
        sog_button.grid(row=2, column=2, sticky="ew", padx=(5, 0))


        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=3, column=0, columnspan=3, sticky="ew", pady=10
        )


        # -------------------------
        # Section: Course over ground
        # -------------------------
        tk.Label(frame_control, text="Course over ground", font=("Arial", 10, "bold")).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Current COG:", anchor="w").grid(row=5, column=0, sticky="w")
        cog_label = tk.Label(frame_control, text="N/A", anchor="w")
        cog_label.grid(row=5, column=1, sticky="w")

        cog_entry = tk.Entry(frame_control)
        cog_entry.grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)
        cog_button = tk.Button(frame_control, text="Set new COG")
        cog_button.grid(row=6, column=2, sticky="ew", padx=(5, 0))

        halt_button = tk.Button(frame_control, text="Halt vessel immediately", bg="red")
        halt_button.grid(row=7, column=2, sticky="ew", pady=5)


        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=8, column=0, columnspan=3, sticky="ew", pady=10
        )


        # -------------------------
        # Section: ROC handover
        # -------------------------
        tk.Label(frame_control, text="ROC handover", font=("Arial", 10, "bold")).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Time until safety gate:", anchor="w").grid(row=10, column=0, sticky="w")
        time_until_label = tk.Label(frame_control, text="N/A", anchor="w")
        time_until_label.grid(row=10, column=1, sticky="w")

        tk.Label(frame_control, text="Handover status:", anchor="w").grid(row=11, column=0, sticky="w")
        handover_status_label = tk.Label(frame_control, text="N/A", anchor="w")
        handover_status_label.grid(row=11, column=1, sticky="w")

        verify_button = tk.Button(frame_control, text="Verify and send checklist")
        verify_button.grid(row=12, column=0, columnspan=3, sticky="ew", pady=2)

        relinquish_button = tk.Button(frame_control, text="Relinquish control")
        relinquish_button.grid(row=13, column=0, columnspan=3, sticky="ew", pady=5)

        # --- Vessel Information Frame ---
        frame_vessel_info = tk.LabelFrame(root, text="Vessel information", padx=10, pady=10)
        frame_vessel_info.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Configure internal grid
        frame_vessel_info.columnconfigure(0, weight=1)
        frame_vessel_info.columnconfigure(1, weight=2)

        label_font = ("Arial", 12)
        value_font = ("Arial", 12, "bold")

        # --- Vessel identifier ---
        tk.Label(frame_vessel_info, text="Vessel identifier:", font=label_font, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        vessel_id_label = tk.Label(frame_vessel_info, text="N/A", font=value_font, anchor="w")
        vessel_id_label.grid(row=0, column=1, sticky="w")

        # Separator
        ttk.Separator(frame_vessel_info, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=10
        )

        # Latitude
        tk.Label(frame_vessel_info, text="Current latitude:", font=label_font, anchor="w").grid(
            row=2, column=0, sticky="w"
        )
        lat_label = tk.Label(frame_vessel_info, text="N/A", font=value_font, anchor="w")
        lat_label.grid(row=2, column=1, sticky="w")

        # Longitude
        tk.Label(frame_vessel_info, text="Current longitude:", font=label_font, anchor="w").grid(
            row=3, column=0, sticky="w"
        )
        lon_label = tk.Label(frame_vessel_info, text="N/A", font=value_font, anchor="w")
        lon_label.grid(row=3, column=1, sticky="w")

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
        #frame_info = tk.Frame(control_frame)
        #frame_info.grid(row=10, column=0, sticky="nsew")

        #vessel_label = tk.Label(frame_info, text="Vessel Name", font=("Arial", 20))
        #vessel_label.pack(pady=10)

        #timer_label = tk.Label(frame_info, text="--:--", font=("Arial", 36))
        #timer_label.pack(pady=5)

        #tk.Label(frame_info, text="Time left until safety gate", font=("Arial", 14)).pack()

        #self.vessel_label = vessel_label
        #self.timer_label = timer_label

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
