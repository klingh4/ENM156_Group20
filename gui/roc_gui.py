import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import time
from tkintermapview import TkinterMapView


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
root = tk.Tk()
root.title("Vehicle Readiness Panel – Interactive")
root.geometry("1800x980")

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=3)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)


# -------------------------------------------------------
# VEHICLE MAP PANEL (live-map)
# -------------------------------------------------------
frame_map = tk.LabelFrame(root, text="Vehicle position map")
frame_map.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

map_widget = TkinterMapView(frame_map, width=600, height=500, corner_radius=0)
map_widget.set_position(59.3293, 18.0686)  # Stockholm example
map_widget.set_zoom(8)
map_widget.pack(expand=True, fill="both")

marker = None

def set_marker_event(coords):
    global marker
    if marker:
        marker.delete()
    marker = map_widget.set_marker(coords[0], coords[1], text="Vehicle")

map_widget.add_left_click_map_command(set_marker_event)


# -------------------------------------------------------
# Visualisation area
# -------------------------------------------------------
frame_visual = tk.LabelFrame(root, text="Visualization / Data Modules")
frame_visual.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

vis_label = tk.Label(frame_visual, text="(Insert charts, graphs or realtime data here)",
                     font=("Arial", 14))
vis_label.pack(expand=True)


# -------------------------------------------------------
# INTERACTIVE CHECKLIST
# -------------------------------------------------------
frame_checklist = tk.LabelFrame(root, text="Bridge Checklist")
frame_checklist.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)

checklist_items = [
    "Night vision adaptation time allowed",
    "Master's daily orders reviewed",
    "GMDSS log updated",
    "Deck log updated",
    "Position checked",
    "Course & speed verified",
    "Traffic conditions safe",
    "Steering gear tested",
    "AIS operational",
    "Radar operational",
    "GNSS operational",
    "VHF working",
    "NAVTEX working",
    "EPIRB OK",
    "Fire doors status checked",
    "Propulsion & steering OK",
    "Special work in progress?",
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


def print_check_status():
    print("\n--- CHECKLIST STATUS ---")
    for item, var in check_vars:
        print(f"{item}: {'✔' if var.get() else '✘'}")
    print("-------------------------\n")


inner_frame.update_idletasks()
scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))


# -------------------------------------------------------
# NOTES EDITOR
# -------------------------------------------------------
frame_notes = tk.LabelFrame(root, text="Remarks about vehicle status")
frame_notes.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

notes_field = ScrolledText(frame_notes, height=5)
notes_field.pack(expand=True, fill="both")


# -------------------------------------------------------
# VEHICLE NAME + TIMER
# -------------------------------------------------------
frame_info = tk.Frame(root)
frame_info.grid(row=1, column=0, sticky="nsew")

vehicle_label = tk.Label(frame_info, text="Vehicle Name", font=("Arial", 20))
vehicle_label.pack(pady=10)

timer_label = tk.Label(frame_info, text="15:00", font=("Arial", 36))
timer_label.pack(pady=5)

tk.Label(frame_info, text="Time left until limit", font=("Arial", 14)).pack()

timer = 900


# -------------------------------------------------------
# BOTTOM BUTTONS
# -------------------------------------------------------
frame_buttons = tk.Frame(root)
frame_buttons.grid(row=2, column=0, columnspan=2, pady=20)

btn_ready = tk.Button(
    frame_buttons,
    text="ASSERT READY",
    font=("Arial", 22),
    width=15,
    bg="green",
    command=print_check_status
)
btn_ready.grid(row=0, column=0, padx=40)

btn_abort = tk.Button(
    frame_buttons,
    text="ABORT",
    font=("Arial", 22),
    width=15,
    bg="red",
    command=lambda: print("ABORT PRESSED")
)
btn_abort.grid(row=0, column=1, padx=40)

root.mainloop()
