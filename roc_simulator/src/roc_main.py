#!/usr/bin/env python3

from ship_monitor import ShipTelemetryMonitor
from roc_gui import RocGui

def main():
    # Initialize GUI
    gui = RocGui()

    # Add extra callbacks to update GUI components from telemetry monitor
    callbacks = {}
    callbacks['handle_location'] = gui.update_map_position
    callbacks['handle_cog'] = gui.update_cog_out
    callbacks['handle_sog'] = gui.update_sog_out
    callbacks['handle_name'] = gui.update_vehicle_name
    callbacks['handle_remote_status'] = gui.update_remote_status
    callbacks['handle_remote_time'] = gui.update_remote_time

    # Initialize telemetry monitor with added callbacks to GUI
    monitor = ShipTelemetryMonitor("MASS_0", callbacks)

    # This blocks and must thus be done last
    gui.mainloop()

if __name__ == '__main__':
    main()

