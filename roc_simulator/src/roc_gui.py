import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import time
import threading
from tkintermapview import TkinterMapView
import zenoh


# -------------------------------------------------------
# Countdown timer
# -------------------------------------------------------
class CountdownTimer:
    def __init__(self, label, seconds=900):
        self.label = label
        self.remaining = seconds
        self.running = True
        self.update()

    def update(self):
        if self.running and self.remaining >= 0:
            mins, secs = divmod(self.remaining, 60)
            self.label.config(text=f"{mins:02}:{secs:02}")
            self.remaining -= 1
            self.label.after(1000, self.update)


# -------------------------------------------------------
# GUI start
# -------------------------------------------------------
class RocGui:
    def __init__(self):
        root = tk.Tk()
        root.title("Vehicle Readiness Panel – Interactive")
        root.geometry("1800x980")

        root.columnconfigure(0, weight=2)
        root.columnconfigure(1, weight=2)
        root.columnconfigure(2, weight=1)
        root.rowconfigure(0, weight=3)
        root.rowconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        # Should exit main loop on closing window
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        # -------------------------------------------------------
        # VEHICLE MAP PANEL (live-map)
        # -------------------------------------------------------
        frame_map = tk.LabelFrame(root, text="Vehicle position map")
        frame_map.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        map_widget = TkinterMapView(frame_map, width=600, height=500, corner_radius=0)
        map_widget.set_position(59.3293, 18.0686)  # Stockholm example
        map_widget.set_zoom(7)
        map_widget.pack(expand=True, fill="both")

        self.marker = None
        self.root = root
        self.frame_map = frame_map
        self.map_widget = map_widget

        ## -------------------------------------------------------
        ## Visualisation area with Zenoh controls
        ## -------------------------------------------------------
        frame_visual = tk.LabelFrame(root, text="Visualization / Data Modules")
        frame_visual.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Create control panel
        control_frame = tk.Frame(frame_visual)
        control_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # COG Control
        tk.Label(control_frame, text="Course Over Ground (COG):", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        cog_entry = tk.Entry(control_frame, font=("Arial", 12), width=15)
        cog_entry.grid(row=0, column=1, padx=10, pady=5)
        cog_send_btn = tk.Button(control_frame, text="Send COG", font=("Arial", 10), 
                                 command=lambda: self.send_cog(cog_entry.get()))
        cog_send_btn.grid(row=0, column=2, padx=5, pady=5)

        # COG Output display
        tk.Label(control_frame, text="COG Output:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        cog_out_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="blue")
        cog_out_label.grid(row=1, column=1, sticky="w", pady=5)

        # SOG Control
        tk.Label(control_frame, text="Speed Over Ground (SOG):", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        sog_entry = tk.Entry(control_frame, font=("Arial", 12), width=15)
        sog_entry.grid(row=2, column=1, padx=10, pady=5)
        sog_send_btn = tk.Button(control_frame, text="Send SOG", font=("Arial", 10),
                                 command=lambda: self.send_sog(sog_entry.get()))
        sog_send_btn.grid(row=2, column=2, padx=5, pady=5)

        # SOG Output display
        tk.Label(control_frame, text="SOG Output:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        sog_out_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="blue")
        sog_out_label.grid(row=3, column=1, sticky="w", pady=5)

        print(f"{self.__class__.__name__} initialized.")

    def mainloop(self):
        self.root.mainloop()

    def send_cog(self, cog):
        print(f"(Placeholder) Send COG: {cog}")

    def send_sog(self, sog):
        print(f"(Placeholder) Send SOG: {sog}")

    # Update map position to given lat/long
    def update_map_position(self, lat_val, lon_val):
        try:
            if self.marker:
                self.marker.delete()
            self.marker = self.map_widget.set_marker(lat_val, lon_val, text="MASS")
            self.map_widget.set_position(lat_val, lon_val)
        except ValueError:
            pass



    ## Separator
    #ttk.Separator(control_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky="ew", pady=15)

    ## Position Display
    #tk.Label(control_frame, text="Current Position:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", pady=5)

    #tk.Label(control_frame, text="Latitude:", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=5)
    #lat_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="green")
    #lat_label.grid(row=6, column=1, sticky="w", pady=5)

    #tk.Label(control_frame, text="Longitude:", font=("Arial", 10)).grid(row=7, column=0, sticky="w", pady=5)
    #lon_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="green")
    #lon_label.grid(row=7, column=1, sticky="w", pady=5)

    ## Update position button
    #update_map_btn = tk.Button(control_frame, text="Update Map Position", font=("Arial", 10),
    #                           command=update_map_position)
    #update_map_btn.grid(row=8, column=0, columnspan=2, pady=10)

    ## State display
    #tk.Label(control_frame, text="Vehicle State:", font=("Arial", 10)).grid(row=9, column=0, sticky="w", pady=5)
    #state_label = tk.Label(control_frame, text="---", font=("Arial", 10), fg="orange")
    #state_label.grid(row=9, column=1, sticky="w", pady=5)

    ## Setup GUI callbacks for Zenoh updates
    #def update_cog_out(value):
    #    cog_out_label.config(text=value)

    #def update_sog_out(value):
    #    sog_out_label.config(text=value)

    #def update_lat(value):
    #    lat_label.config(text=value)
    #    # Auto-update map when new position received
    #    root.after(100, update_map_position)

    #def update_lon(value):
    #    lon_label.config(text=value)
    #    # Auto-update map when new position received
    #    root.after(100, update_map_position)

    #def update_state(value):
    #    state_label.config(text=value)

    ## -------------------------------------------------------
    ## INTERACTIVE CHECKLIST
    ## -------------------------------------------------------
    #frame_checklist = tk.LabelFrame(root, text="Bridge Checklist")
    #frame_checklist.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)

    #checklist_items = [
    #    "Night vision adaptation time allowed",
    #    "Master's daily orders reviewed",
    #    "GMDSS log updated",
    #    "Deck log updated",
    #    "Position checked",
    #    "Course & speed verified",
    #    "Traffic conditions safe",
    #    "Steering gear tested",
    #    "AIS operational",
    #    "Radar operational",
    #    "GNSS operational",
    #    "VHF working",
    #    "NAVTEX working",
    #    "EPIRB OK",
    #    "Fire doors status checked",
    #    "Propulsion & steering OK",
    #    "Special work in progress?",
    #]

    #scroll_canvas = tk.Canvas(frame_checklist)
    #scroll_canvas.pack(side="left", fill="both", expand=True)

    #scrollbar = tk.Scrollbar(frame_checklist, orient="vertical",
    #                         command=scroll_canvas.yview)
    #scrollbar.pack(side="right", fill="y")
    #scroll_canvas.configure(yscrollcommand=scrollbar.set)

    #inner_frame = tk.Frame(scroll_canvas)
    #scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    #check_vars = []

    #for item in checklist_items:
    #    var = tk.BooleanVar()
    #    chk = tk.Checkbutton(inner_frame, text=item, variable=var, anchor="w")
    #    chk.pack(fill="x", pady=2)
    #    check_vars.append((item, var))


    #def print_check_status():
    #    print("\n--- CHECKLIST STATUS ---")
    #    for item, var in check_vars:
    #        print(f"{item}: {'✓' if var.get() else '✗'}")
    #    print("-------------------------\n")


    #inner_frame.update_idletasks()
    #scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))


    ## -------------------------------------------------------
    ## NOTES EDITOR
    ## -------------------------------------------------------
    #frame_notes = tk.LabelFrame(root, text="Remarks about vehicle status")
    #frame_notes.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    #notes_field = ScrolledText(frame_notes, height=5)
    #notes_field.pack(expand=True, fill="both")


    ## -------------------------------------------------------
    ## VEHICLE NAME + TIMER
    ## -------------------------------------------------------
    #frame_info = tk.Frame(root)
    #frame_info.grid(row=1, column=0, sticky="nsew")

    #vehicle_label = tk.Label(frame_info, text="Vehicle Name", font=("Arial", 20))
    #vehicle_label.pack(pady=10)

    #timer_label = tk.Label(frame_info, text="15:00", font=("Arial", 36))
    #timer_label.pack(pady=5)

    #tk.Label(frame_info, text="Time left until limit", font=("Arial", 14)).pack()

    #countdown = CountdownTimer(timer_label, 900)


    ## -------------------------------------------------------
    ## BOTTOM BUTTONS
    ## -------------------------------------------------------
    #frame_buttons = tk.Frame(root)
    #frame_buttons.grid(row=2, column=0, columnspan=2, pady=20)

    #def handle_abort():
    #    """Handle abort button - stop the vehicle"""
    #    print("\n!!! ABORT BUTTON PRESSED !!!")
    #    zenoh_conn.stop_vehicle()
    #    notes_field.insert(tk.END, f"\n[{time.strftime('%H:%M:%S')}] ABORT - Emergency stop commanded")

    #btn_ready = tk.Button(
    #    frame_buttons,
    #    text="ASSERT READY",
    #    font=("Arial", 22),
    #    width=15,
    #    bg="green",
    #    command=print_check_status
    #)
    #btn_ready.grid(row=0, column=0, padx=40)

    #btn_abort = tk.Button(
    #    frame_buttons,
    #    text="ABORT",
    #    font=("Arial", 22),
    #    width=15,
    #    bg="red",
    #    command=handle_abort
    #)
    #btn_abort.grid(row=0, column=1, padx=40)

