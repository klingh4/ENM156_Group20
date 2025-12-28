#!/usr/bin/env python3

'''
Main entry point for the ROC simulator.
'''

import argparse

from ship_monitor import ShipTelemetryMonitor
from roc_controller import ROCController
from roc_gui import RocGui

def main():
    parser = argparse.ArgumentParser(description="ROC simulator")
    parser.add_argument("-r", "--roc",
                        required=True,
                        choices=["ROC_1", "ROC_2"],
                        help="ROC id")
    parser.add_argument("-s", "--ship",
                        type=str,
                        default="MASS_0")
    args = parser.parse_args()

    # Initialize ROC controller (thing sending commands to ship)
    roc_controller = ROCController(args.roc, args.ship)

    # Initialize GUI (clicky thing for human operator)
    gui = RocGui(roc_controller)

    # Add extra callbacks to update GUI components from telemetry monitor
    callbacks = {}
    callbacks['handle_location'] = gui.update_map_position
    callbacks['handle_cog'] = gui.update_cog_out
    callbacks['handle_sog'] = gui.update_sog_out
    callbacks['handle_name'] = gui.update_ship_name
    callbacks['handle_mmsi'] = gui.update_mmsi
    callbacks['handle_imo'] = gui.update_imo
    callbacks['handle_remote_status'] = gui.update_remote_status
    callbacks['handle_remote_time'] = gui.update_remote_time
    callbacks['handle_roc_status'] = gui.update_roc_status
    callbacks['handle_handover_request'] = gui.on_handover_request
    callbacks['handle_handover_state'] = gui.on_handover_state

    # Initialize telemetry monitor with added callbacks to GUI
    # (thing receiving Zenoh/keelson messages from ship)
    monitor = ShipTelemetryMonitor(args.ship, callbacks)
    gui.monitor = monitor

    # !! This blocks and must thus be done last !!
    gui.mainloop()

if __name__ == '__main__':
    main()

