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
    def __init__(self, roc_controller):
        self.roc_controller = roc_controller
        self.roc_id = roc_controller.roc_id
        self.roc_id_num = int(self.roc_id[-1])
        self.roc_location = {"ROC_1": "Vaasa", "ROC_2": "Umeå"}[self.roc_id]
        self.vessel = roc_controller.vessel
        # Hack !! TODO: listen to vessel when it supports this
        self.controlling_roc = "ROC_1"

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
        label_font = ("Arial", 10)
        value_font = ("Arial", 10, "bold")

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
        tk.Label(frame_roc, text="ROC identifier:", font=label_font, anchor="w").grid(row=0, column=0, sticky="w")
        roc_id_label = tk.Label(frame_roc, text=self.roc_id, font=value_font, anchor="w")
        roc_id_label.grid(row=0, column=1, sticky="w")

        # Separator
        ttk.Separator(frame_roc, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=10
        )

        # ROC location row
        tk.Label(frame_roc, text="ROC location:", font=label_font, anchor="w").grid(row=2, column=0, sticky="w")
        roc_location_label = tk.Label(frame_roc, text=self.roc_location, font=value_font, anchor="w")
        roc_location_label.grid(row=2, column=1, sticky="w")

        ## Second column
        # --- Vessel Control Frame ---
        frame_control = tk.LabelFrame(root, text="Vessel control", padx=10, pady=10)
        frame_control.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Internal grid configuration
        frame_control.columnconfigure(0, weight=1)
        frame_control.columnconfigure(1, weight=1)
        frame_control.columnconfigure(2, weight=1)

        # TODO: rework after we're able to get has_priority from the status as well
        tk.Label(frame_control, text="Controlling ROC:", anchor="w", font=label_font).grid(row=0, column=0, sticky="w")
        roc_status_label = tk.Label(frame_control, text=self.controlling_roc, anchor="w", font=value_font)
        roc_status_label.grid(row=0, column=1, sticky="w")

        self.roc_status_label = roc_status_label

        tk.Label(frame_control, text="Vessel status:", font=label_font, anchor="w").grid(
            row=1, column=0, sticky="w"
        )
        vessel_status_label = tk.Label(frame_control, text="N/A", font=value_font, anchor="w")
        vessel_status_label.grid(row=1, column=1, sticky="w")

        self.vessel_status_label = vessel_status_label

        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=10
        )

        # -------------------------
        # Section: Speed over ground
        # -------------------------
        tk.Label(frame_control, text="Speed over ground", font=value_font).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Current SOG:", anchor="w", font=label_font).grid(row=4, column=0, sticky="w")
        sog_label = tk.Label(frame_control, text="N/A", anchor="w", font=value_font)
        sog_label.grid(row=4, column=1, sticky="w")

        sog_entry = tk.Entry(frame_control)
        sog_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
        sog_button = tk.Button(frame_control, text="Set new SOG", command=self.send_sog)
        sog_button.grid(row=5, column=2, sticky="ew", padx=(5, 0))

        self.sog_button = sog_button
        self.sog_entry = sog_entry
        self.sog_label = sog_label

        halt_button = tk.Button(frame_control, text="Halt vessel", fg="red", command=self.halt_vessel)
        halt_button.grid(row=6, column=2, sticky="ew", pady=5)

        self.halt_button = halt_button

        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=10
        )


        # -------------------------
        # Section: Course over ground
        # -------------------------
        tk.Label(frame_control, text="Course over ground", font=value_font).grid(
            row=8, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Current COG:", anchor="w", font=label_font).grid(row=9, column=0, sticky="w")
        cog_label = tk.Label(frame_control, text="N/A", anchor="w", font=value_font)
        cog_label.grid(row=9, column=1, sticky="w")

        cog_entry = tk.Entry(frame_control)
        cog_entry.grid(row=10, column=0, columnspan=2, sticky="ew", pady=2)
        cog_button = tk.Button(frame_control, text="Set new COG", command=self.send_cog)
        cog_button.grid(row=10, column=2, sticky="ew", padx=(5, 0))

        self.cog_button = cog_button
        self.cog_entry = cog_entry
        self.cog_label = cog_label

        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=11, column=0, columnspan=3, sticky="ew", pady=10
        )


        # -------------------------
        # Section: ROC handover
        # -------------------------
        tk.Label(frame_control, text="ROC handover", font=value_font).grid(
            row=12, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Time until safety gate:", anchor="w", font=label_font).grid(row=13, column=0, sticky="w")
        time_until_label = tk.Label(frame_control, text="N/A", anchor="w", font=value_font)
        time_until_label.grid(row=13, column=1, sticky="w")

        self.time_until_label = time_until_label

        tk.Label(frame_control, text="Handover status:", anchor="w", font=label_font).grid(row=14, column=0, sticky="w")
        handover_status_label = tk.Label(frame_control, text="N/A", anchor="w", font=value_font)
        handover_status_label.grid(row=14, column=1, sticky="w")

        verify_button = tk.Button(frame_control, text="Verify and send checklist")
        verify_button.grid(row=15, column=0, columnspan=3, sticky="ew", pady=2)

        self.verify_button = verify_button

        relinquish_button = tk.Button(frame_control, text="Relinquish control", command=self.relinquish)
        relinquish_button.grid(row=16, column=0, columnspan=3, sticky="ew", pady=5)

        self.relinquish_button = relinquish_button


        # --- Vessel Information Frame ---
        frame_vessel_info = tk.LabelFrame(root, text="Vessel information", padx=10, pady=10)
        frame_vessel_info.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Configure internal grid
        frame_vessel_info.columnconfigure(0, weight=1)
        frame_vessel_info.columnconfigure(1, weight=2)

        # --- Vessel identifier ---
        tk.Label(frame_vessel_info, text="Vessel identifier:", font=label_font, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        vessel_id_label = tk.Label(frame_vessel_info, text="N/A", font=value_font, anchor="w")
        vessel_id_label.grid(row=0, column=1, sticky="w")

        self.vessel_id_label = vessel_id_label

        # Separator
        ttk.Separator(frame_vessel_info, orient="horizontal").grid(
            row=2, column=0, sticky="ew", pady=10
        )

        # Latitude
        tk.Label(frame_vessel_info, text="Current latitude:", font=label_font, anchor="w").grid(
            row=3, column=0, sticky="w"
        )
        lat_label = tk.Label(frame_vessel_info, text="N/A", font=value_font, anchor="w")
        lat_label.grid(row=3, column=1, sticky="w")

        self.lat_label = lat_label

        # Longitude
        tk.Label(frame_vessel_info, text="Current longitude:", font=label_font, anchor="w").grid(
            row=4, column=0, sticky="w"
        )
        lon_label = tk.Label(frame_vessel_info, text="N/A", font=value_font, anchor="w")
        lon_label.grid(row=4, column=1, sticky="w")

        self.lon_label = lon_label

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
        frame_notes = tk.LabelFrame(root, text="(Optional) remarks about vessel status for next ROC")
        frame_notes.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        notes_field = ScrolledText(frame_notes, height=5)
        notes_field.pack(expand=True, fill="both")

        self.conditionally_enable_elements()

        # Bit of an ugly hack - but if we get handed this we can properly close
        # the zenoh session and thus properly exit on closing the window.
        self.monitor = None

        print(f"{self.__class__.__name__} initialized.")

    def mainloop(self):
        self.root.mainloop()

    def conditionally_enable_elements(self):
        for element in [
            self.sog_button, self.sog_entry, self.cog_button, self.cog_entry,
            self.halt_button, self.verify_button, self.relinquish_button
        ]:
            if self.roc_id == self.controlling_roc:
                element.config(state="normal")
            else:
                element.config(state="disabled")

    def on_close(self):
        # Close zenoh session properly at exit
        if self.monitor:
            self.monitor.session.close()

        self.root.quit()
        self.root.destroy()

    def relinquish(self):
        self.roc_controller.send_relinquish()

    def send_cog(self):
        # TODO: validate data
        cog = self.cog_entry.get()
        self.cog_entry.delete(0, tk.END)
        self.roc_controller.send_cog(cog)

    def send_sog(self):
        # TODO: validate data
        sog = self.sog_entry.get()
        self.sog_entry.delete(0, tk.END)
        self.roc_controller.send_sog(sog)

    def halt_vessel(self):
        print("\n!!! HALT BUTTON PRESSED !!!")
        self.roc_controller.send_sog(0)

    def print_check_status(self):
        print("\n--- CHECKLIST STATUS ---")
        for item, var in self.check_vars:
            print(f"{item}: {'✓' if var.get() else '✗'}")
        print("-------------------------\n")

    # Setup GUI callbacks for ship updates
    def update_cog_out(self, value):
        self.cog_label.config(text=f"{value:.2f}")

    def update_sog_out(self, value):
        self.sog_label.config(text=f"{value:.2f}")

    def update_roc_status(self, value):
        # TODO: fix when we can get has_priority as well
        # self.roc_status_label.config(text=value)
        pass

    def update_remote_status(self, value):
        self.vessel_status_label.config(text=value)

    def update_remote_time(self, value):
        ## Format into hh:mm:ss at one second precision
        time_fmt = str(datetime.timedelta(seconds=int(value)))
        self.time_until_label.config(text=time_fmt)

    def update_vessel_name(self, value):
        self.vessel_id_label.config(text=value)

    # Update map position to given lat/long
    def update_map_position(self, lat_val, lon_val):
        try:
            self.lat_label.config(text=f"{lat_val:.6f}")
            self.lon_label.config(text=f"{lon_val:.6f}")

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
