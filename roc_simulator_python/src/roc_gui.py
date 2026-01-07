import datetime
import time
import tkinter as tk
import sys

from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkintermapview import TkinterMapView

# Don't update map widget more often than this to avoid flickering
# (time in seconds)
MAP_WIDGET_UPDATE_CAP = 5

# Some enums
HANDOVER_STATE_PENDING = 0
HANDOVER_STATE_READY = 1
HANDOVER_STATE_COMPLETED = 2


class RocGui:
    def __init__(self, roc_controller):
        self.roc_controller = roc_controller
        self.roc_id = roc_controller.roc_id
        self.roc_id_num = int(self.roc_id[-1])
        # TODO: Hard coded for now.
        self.roc_location = {"ROC_1": "Vaasa", "ROC_2": "Umeå"}[self.roc_id]
        self.ship_id = roc_controller.ship_id
        # Hack!! TODO: have the ship tell us its controlling ROC instead.
        self.controlling_roc = "ROC_1"
        self.handover_state = HANDOVER_STATE_PENDING


        # -------------------------------------------------------
        # Root element setup
        # -------------------------------------------------------

        root = tk.Tk()
        root.title("Vessel Readiness Panel – Interactive")
        root.geometry("1800x980") # Static start value, but the window is resizable

        # Set up uniform (they don't adapt their width) columns with a slightly smaller third one
        root.columnconfigure(0, weight=3, uniform="cols")
        root.columnconfigure(1, weight=3, uniform="cols")
        root.columnconfigure(2, weight=2, uniform="cols")

        # Set up a tall first row and two smaller ones
        root.rowconfigure(0, weight=3)
        root.rowconfigure(1, weight=1)
        # TODO: Third row actually empty for now, but looks nice as padding.
        # Should probably add content or replace with actual padding.
        root.rowconfigure(2, weight=1)

        # Should exit main loop on closing window
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root = root

        self.label_font = ("Arial", 10)
        self.value_font = ("Arial", 10, "bold")


        # -------------------------------------------------------
        # First column setup
        # -------------------------------------------------------

        # Top left corner: Add pretty live map.
        self.marker = None
        self.map_widget = None
        self.map_widget_last_updated_time = 0
        self.setup_vehicle_map_panel()

        # Bottom left corner: Add ROC information (static for now, doesn't change after init).
        self.setup_roc_information_panel()


        # -------------------------------------------------------
        # Second column setup
        # -------------------------------------------------------

        # Top middle: Vessel controls
        self.roc_status_label = None
        self.ship_status_label = None
        self.sog_button = None
        self.sog_entry = None
        self.sog_label = None
        self.default_bgcol = None
        self.default_abgcol = None
        self.time_until_label = None
        self.handover_status_label = None
        self.verify_button = None
        self.relinquish_button = None
        self.takeover_button = None
        self.halt_button = None
        self.setup_vessel_control_panel()

        # Bottom middle: Further vessel information
        self.ship_id_label = None
        self.mmsi_label = None
        self.imo_label = None
        self.lat_label = None
        self.lon_label = None
        self.setup_vessel_info_panel()


        # -------------------------------------------------------
        # Third column setup
        # -------------------------------------------------------

        # Top right: Interactive checklist
        # TODO: This is not connected to any real functionality at the moment.
        # But at least you can click the boxes, that's always fun!
        self.checklist_variables = None
        self.setup_interactive_checklist_panel()

        # Bottom right: Arbitrary notes editor
        # TODO: Not connected to any real functionality yet either.
        self.notes_field = None
        self.setup_notes_panel()


        # -------------------------------------------------------
        # Finalize setup
        # -------------------------------------------------------
        self.conditionally_enable_elements()

        # Bit of an ugly hack - but if we get handed this we can properly close
        # the zenoh session and thus properly exit on closing the window.
        self.monitor = None

        print(f"{self.__class__.__name__} initialized.")


    # -------------------------------------------------------
    # Setup methods
    # -------------------------------------------------------
    def setup_vehicle_map_panel(self):
        '''
        Set up interactive live map showing vessel and ROC location.
        '''
        frame_map = tk.LabelFrame(self.root, text="Vessel position map")
        frame_map.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        map_widget = TkinterMapView(frame_map, width=600, height=500, corner_radius=0)
        map_widget.set_position(59.3293, 18.0686)  # Stockholm example
        map_widget.set_zoom(4)
        map_widget.pack(expand=True, fill="both")
        map_widget.set_marker(63.0888, 21.5617, text="ROC Vaasa", marker_color_circle="white", marker_color_outside="cyan")
        map_widget.set_marker(63.7045, 20.3530, text="ROC Umeå", marker_color_circle="yellow", marker_color_outside="cyan")

        self.map_widget = map_widget

    def setup_roc_information_panel(self):
        '''
        Set up panel with static ROC information.
        '''
        frame_roc = tk.LabelFrame(self.root, text="ROC information", padx=10, pady=10)
        frame_roc.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Configure grid inside the frame
        frame_roc.columnconfigure(0, weight=1, pad=5)
        frame_roc.columnconfigure(1, weight=3, pad=5)

        # ROC identifier row
        tk.Label(frame_roc, text="ROC identifier:", font=self.label_font, anchor="w").grid(row=0, column=0, sticky="w")
        roc_id_label = tk.Label(frame_roc, text=self.roc_id, font=self.value_font, anchor="w")
        roc_id_label.grid(row=0, column=1, sticky="w")

        # Separator
        ttk.Separator(frame_roc, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=10
        )

        # ROC location row
        tk.Label(frame_roc, text="ROC location:", font=self.label_font, anchor="w").grid(row=2, column=0, sticky="w")
        roc_location_label = tk.Label(frame_roc, text=self.roc_location, font=self.value_font, anchor="w")
        roc_location_label.grid(row=2, column=1, sticky="w")

    def setup_vessel_control_panel(self):
        '''
        Set up vessel COG/SOG and handover controls.
        '''
        frame_control = tk.LabelFrame(self.root, text="Vessel control", padx=10, pady=10)
        frame_control.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Internal grid configuration
        frame_control.columnconfigure(0, weight=1)
        frame_control.columnconfigure(1, weight=1)
        frame_control.columnconfigure(2, weight=1)

        # TODO: rework after we're able to get has_priority from the status as well
        tk.Label(frame_control, text="Controlling ROC:", anchor="w", font=self.label_font).grid(row=0, column=0, sticky="w")
        roc_status_label = tk.Label(frame_control, text=self.controlling_roc, anchor="w", font=self.value_font)
        roc_status_label.grid(row=0, column=1, sticky="w")

        self.roc_status_label = roc_status_label

        tk.Label(frame_control, text="Vessel status:", font=self.label_font, anchor="w").grid(
            row=1, column=0, sticky="w"
        )
        ship_status_label = tk.Label(frame_control, text="N/A", font=self.value_font, anchor="w")
        ship_status_label.grid(row=1, column=1, sticky="w")

        self.ship_status_label = ship_status_label

        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=10
        )

        # -------------------------
        # Section: Speed over ground
        # -------------------------
        tk.Label(frame_control, text="Speed over ground", font=self.value_font).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Current SOG:", anchor="w", font=self.label_font).grid(row=4, column=0, sticky="w")
        sog_label = tk.Label(frame_control, text="N/A", anchor="w", font=self.value_font)
        sog_label.grid(row=4, column=1, sticky="w")

        sog_entry = tk.Entry(frame_control)
        sog_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
        sog_button = tk.Button(frame_control, text="Set new SOG", command=self.send_sog)
        sog_button.grid(row=5, column=2, sticky="ew", padx=(5, 0))

        self.sog_button = sog_button
        self.sog_entry = sog_entry
        self.sog_label = sog_label

        # Stash these values for later use (so we can flash the button for the user)
        self.default_bgcol = sog_button.cget("background")
        self.default_abgcol = sog_button.cget("activebackground")

        halt_button = tk.Button(frame_control, text="Halt ship", fg="red", command=self.halt_ship)
        halt_button.grid(row=6, column=2, sticky="ew", pady=5)

        self.halt_button = halt_button

        # Separator
        ttk.Separator(frame_control, orient="horizontal").grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=10
        )

        # -------------------------
        # Section: Course over ground
        # -------------------------
        tk.Label(frame_control, text="Course over ground", font=self.value_font).grid(
            row=8, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Current COG:", anchor="w", font=self.label_font).grid(row=9, column=0, sticky="w")
        cog_label = tk.Label(frame_control, text="N/A", anchor="w", font=self.value_font)
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
        tk.Label(frame_control, text="ROC handover", font=self.value_font).grid(
            row=12, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        tk.Label(frame_control, text="Time until safety gate:", anchor="w", font=self.label_font).grid(row=13, column=0, sticky="w")
        time_until_label = tk.Label(frame_control, text="N/A", anchor="w", font=self.value_font)
        time_until_label.grid(row=13, column=1, sticky="w")

        self.time_until_label = time_until_label

        tk.Label(frame_control, text="Handover status:", anchor="w", font=self.label_font).grid(row=14, column=0, sticky="w")
        handover_status_label = tk.Label(frame_control, text="N/A", anchor="w", font=self.value_font)
        handover_status_label.grid(row=14, column=1, sticky="w")

        self.handover_status_label = handover_status_label

        verify_button = tk.Button(frame_control, text="Verify and send checklist (not implemented yet)", state="disabled")
        verify_button.grid(row=15, column=0, columnspan=3, sticky="ew", pady=2)

        self.verify_button = verify_button

        relinquish_button = tk.Button(frame_control, text="Relinquish control", command=self.on_relinquish, state="disabled")
        relinquish_button.grid(row=16, column=0, columnspan=3, sticky="ew", pady=5)

        self.relinquish_button = relinquish_button

        takeover_button = tk.Button(frame_control, text="Request control", command=self.on_request, state="disabled")
        takeover_button.grid(row=17, column=0, columnspan=3, sticky="ew", pady=5)

        self.takeover_button = takeover_button

    def setup_vessel_info_panel(self):
        '''
        Set up panel with additional vessel information.
        '''
        frame_ship_info = tk.LabelFrame(self.root, text="Vessel information", padx=10, pady=10)
        frame_ship_info.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Configure internal grid
        frame_ship_info.columnconfigure(0, weight=1)
        frame_ship_info.columnconfigure(1, weight=2)

        # --- Vessel identifier ---
        tk.Label(frame_ship_info, text="Vessel identifier:", font=self.label_font, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        ship_id_label = tk.Label(frame_ship_info, text="N/A", font=self.value_font, anchor="w")
        ship_id_label.grid(row=0, column=1, sticky="w")

        self.ship_id_label = ship_id_label

        # MMSI
        tk.Label(frame_ship_info, text="MMSI:", font=self.label_font, anchor="w").grid(
            row=1, column=0, sticky="w"
        )
        mmsi_label = tk.Label(frame_ship_info, text="N/A", font=self.value_font, anchor="w")
        mmsi_label.grid(row=1, column=1, sticky="w")

        self.mmsi_label = mmsi_label

        # IMO
        tk.Label(frame_ship_info, text="IMO:", font=self.label_font, anchor="w").grid(
            row=2, column=0, sticky="w"
        )
        imo_label = tk.Label(frame_ship_info, text="N/A", font=self.value_font, anchor="w")
        imo_label.grid(row=2, column=1, sticky="w")

        self.imo_label = imo_label

        # Separator
        ttk.Separator(frame_ship_info, orient="horizontal").grid(
            row=3, column=0, sticky="ew", pady=10
        )

        # Latitude
        tk.Label(frame_ship_info, text="Current latitude:", font=self.label_font, anchor="w").grid(
            row=4, column=0, sticky="w"
        )
        lat_label = tk.Label(frame_ship_info, text="N/A", font=self.value_font, anchor="w")
        lat_label.grid(row=4, column=1, sticky="w")

        self.lat_label = lat_label

        # Longitude
        tk.Label(frame_ship_info, text="Current longitude:", font=self.label_font, anchor="w").grid(
            row=5, column=0, sticky="w"
        )
        lon_label = tk.Label(frame_ship_info, text="N/A", font=self.value_font, anchor="w")
        lon_label.grid(row=5, column=1, sticky="w")

        self.lon_label = lon_label

    def setup_interactive_checklist_panel(self):
        '''
        Set up interactive checklist for various items that need to be manually checked
        before the handover can be completed.
        '''
        frame_checklist = tk.LabelFrame(self.root, text="Bridge Checklist")
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

        self.checklist_variables = check_vars

        inner_frame.update_idletasks()
        scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))

    def setup_notes_panel(self):
        '''
        Set up field where the ROC operator may add arbitrary remarks about the vessel.
        '''
        frame_notes = tk.LabelFrame(self.root, text="(Optional) remarks about ship status for next ROC")
        frame_notes.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        notes_field = ScrolledText(frame_notes, height=5)
        notes_field.pack(expand=True, fill="both")

        self.notes_field = notes_field


    # -------------------------------------------------------
    # Methods called from GUI actions
    # -------------------------------------------------------
    def on_close(self):
        '''
        Called upon window close, all cleanup needs to happen here.
        '''
        # Close zenoh session properly at exit
        if self.monitor:
            self.monitor.session.close()

        self.root.quit()
        self.root.destroy()

    def on_relinquish(self):
        '''
        Send relinquish control zenoh message and display a helpful GUI message.
        '''
        self.handover_status_label.configure(text="Awaiting confirmation...", fg="blue")
        self.roc_controller.send_relinquish()

    def on_request(self):
        '''
        Send request control zenoh message and display a helpful GUI message.
        '''
        self.handover_status_label.configure(text="Awaiting confirmation...", fg="blue")
        self.roc_controller.send_takeover()

    def send_cog(self):
        '''
        Send COG given in GUI to ship.
        '''
        # TODO: validate data, don't accept empty or nonnumeric!
        cog = self.cog_entry.get()
        self.cog_entry.delete(0, tk.END)
        self.roc_controller.send_cog(cog)

    def send_sog(self):
        '''
        Send SOG given in GUI to ship.
        '''
        # TODO: validate data, don't accept empty or nonnumeric!
        sog = self.sog_entry.get()
        self.sog_entry.delete(0, tk.END)
        self.roc_controller.send_sog(sog)

    def halt_ship(self):
        '''
        Immediately halt ship.
        '''
        print("\n!!! HALT BUTTON PRESSED !!!")
        self.roc_controller.send_sog(0)

    def print_checklist_status(self):
        '''
        Do something with the interactive checklist.
        Currently neither connected to the checklist, nor very useful as such.
        '''
        # TODO: Connect to checklist.
        print("\n--- CHECKLIST STATUS ---")
        for item, var in self.checklist_variables:
            print(f"{item}: {'✓' if var.get() else '✗'}")
        print("-------------------------\n")

    def update_map_position(self, lat_val, lon_val):
        '''
        Update map position to given lat/long value.
        '''
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

    def conditionally_enable_elements(self):
        '''
        Enable or disable certain elements, depending on handover status and whether we're the controling ROC.
        '''
        # Basic SOG/COG/halt
        for element in [
            self.sog_button, self.sog_entry, self.cog_button, self.cog_entry, self.halt_button
        ]:
            if self.roc_id == self.controlling_roc:
                element.config(state="normal")
            else:
                element.config(state="disabled")

        # Handover elements
        if self.handover_state in [HANDOVER_STATE_PENDING, HANDOVER_STATE_COMPLETED]:
            self.relinquish_button.config(state="disabled", bg=self.default_bgcol, activebackground=self.default_abgcol)
            self.takeover_button.config(state="disabled", bg=self.default_bgcol, activebackground=self.default_abgcol)
        elif self.handover_state == HANDOVER_STATE_READY:
            if self.roc_id == self.controlling_roc:
                self.relinquish_button.config(state="normal", bg="green", activebackground="lightgreen")
                self.takeover_button.config(state="disabled")
            else:
                self.relinquish_button.config(state="disabled")
                self.takeover_button.config(state="normal", bg="green", activebackground="lightgreen")


    # -------------------------------------------------------
    # Callbacks for ship updates
    # -------------------------------------------------------
    def on_handover_request(self, value):
        '''
        React to handover ready message from ship.
        '''
        self.handover_state = HANDOVER_STATE_READY
        self.handover_status_label.config(text="Ready for handover", fg="green")
        self.conditionally_enable_elements()

    def on_handover_state(self, value):
        '''
        React to handover completed message from ship.
        '''
        self.handover_state = HANDOVER_STATE_COMPLETED
        self.handover_status_label.config(text="Handover completed.", fg="green")
        self.time_until_label.config(text="N/A")

        # TODO: AWFUL HACK (but quick)
        priority_roc = "ROC_2" if "new_priority=ROC_2" in value else "ROC_1"
        self.controlling_roc = priority_roc
        self.roc_status_label.config(text=priority_roc)
        self.conditionally_enable_elements()

    def update_cog_out(self, value):
        '''
        React to cog message from ship.
        '''
        self.cog_label.config(text=f"{value:.2f}")

    def update_sog_out(self, value):
        '''
        React to sog message from ship.
        '''
        self.sog_label.config(text=f"{value:.2f}")

    def update_roc_status(self, value):
        '''
        React to roc status message from ship.
        '''
        # TODO: fix when we can get has_priority as well
        # self.roc_status_label.config(text=value)
        pass

    def update_mmsi(self, value):
        '''
        React to MMSI message from ship.
        '''
        self.mmsi_label.config(text=value)

    def update_imo(self, value):
        '''
        React to IMO message from ship.
        '''
        self.imo_label.config(text=value)

    def update_remote_status(self, value):
        '''
        React to remote status message from ship.
        '''
        self.ship_status_label.config(text=value)

    def update_remote_time(self, value):
        '''
        React to remote time message from ship.
        '''
        ## Format into hh:mm:ss at one second precision
        time_fmt = str(datetime.timedelta(seconds=int(value)))
        self.time_until_label.config(text=time_fmt)

    def update_ship_name(self, value):
        '''
        React to ship name message from ship.
        '''
        self.ship_id_label.config(text=value)


    # -------------------------------------------------------
    # Main loop entry point
    # -------------------------------------------------------
    def mainloop(self):
        self.root.mainloop()

if __name__ == '__main__':
    print("Please run roc_main.py instead.")
    sys.exit(1)
