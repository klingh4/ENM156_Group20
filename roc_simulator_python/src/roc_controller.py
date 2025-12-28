#!/usr/bin/env python3

'''
This module contains the interface for sending control messages to a ship.
'''

import time
import zenoh as Zenoh
from zenoh import Config
from keelson import enclose
from keelson.payloads.Primitives_pb2 import TimestampedFloat


class ROCController:
    def __init__(self, roc_id, ship):
        self.roc_id = roc_id
        self.ship = ship

        cfg = Config()
        self.zenoh = Zenoh.open(cfg)

        self.pub_cog = self.zenoh.declare_publisher(f"{self.ship}/control/roc/{self.roc_id}/COG")
        self.pub_sog = self.zenoh.declare_publisher(f"{self.ship}/control/roc/{self.roc_id}/SOG")
        self.pub_relinquish = self.zenoh.declare_publisher(f"{self.ship}/handover/relinquish")
        self.pub_takeover = self.zenoh.declare_publisher(f"{self.ship}/handover/takeover")

    def send_cog(self, value):
        msg = TimestampedFloat()
        msg.timestamp.FromNanoseconds(time.time_ns())
        msg.value = float(value)
        self.pub_cog.put(enclose(msg.SerializeToString()))
        print(f"[{self.roc_id}] Sent COG={value}")

    def send_sog(self, value):
        msg = TimestampedFloat()
        msg.timestamp.FromNanoseconds(time.time_ns())
        msg.value = float(value)
        self.pub_sog.put(enclose(msg.SerializeToString()))
        print(f"[{self.roc_id}] Sent SOG={value}")

    def send_relinquish(self):
        self.pub_relinquish.put(self.roc_id)
        print(f"[{self.roc_id}] Sent relinquish")

    def send_takeover(self):
        self.pub_takeover.put(self.roc_id)
        print(f"[{self.roc_id}] Sent takeover")
