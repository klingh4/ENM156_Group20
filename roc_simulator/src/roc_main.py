#!/usr/bin/env python3

import argparse

from ship_monitor import ShipTelemetryMonitor
from roc_controller import ROCController
from roc_gui import RocGui

def main():
    parser = argparse.ArgumentParser(description="ROC simulator")
    parser.add_argument("roc",
                        choices=["ROC_1", "ROC_2"],
                        help="ROC id")
    args = parser.parse_args()

    # Hard code vessel for now...
    roc_controller = ROCController(args.roc, "MASS_0")

    # Initialize GUI
    gui = RocGui(roc_controller)

    # Add extra callbacks to update GUI components from telemetry monitor
    callbacks = {}
    callbacks['handle_location'] = gui.update_map_position
    callbacks['handle_cog'] = gui.update_cog_out
    callbacks['handle_sog'] = gui.update_sog_out
    callbacks['handle_name'] = gui.update_vessel_name
    callbacks['handle_remote_status'] = gui.update_remote_status
    callbacks['handle_remote_time'] = gui.update_remote_time

    # Initialize telemetry monitor with added callbacks to GUI
    monitor = ShipTelemetryMonitor("MASS_0", callbacks)
    gui.monitor = monitor

    # This blocks and must thus be done last
    gui.mainloop()

if __name__ == '__main__':
    main()

