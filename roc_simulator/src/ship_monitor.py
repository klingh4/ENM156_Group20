#!/usr/bin/env python3
import time
import zenoh
from datetime import datetime

from keelson import uncover, construct_pubsub_key
from keelson.payloads.foxglove.LocationFix_pb2 import LocationFix
from keelson.payloads.Primitives_pb2 import TimestampedFloat, TimestampedInt, TimestampedString
from keelson.payloads.VesselNavStatus_pb2 import VesselNavStatus
from keelson.payloads.ROCStatus_pb2 import ROCStatus


class ShipTelemetryMonitor:
    def __init__(self, ship_name, extra_callbacks):
        self.ship = ship_name
        self.extra_callbacks = extra_callbacks

        # Latest telemetry
        self.location = None
        self.cog = None
        self.sog = None
        self.remote_status = None
        self.remote_time = None
        self.nav_status = None
        self.mmsi = None
        self.imo = None

        cfg = zenoh.Config()
        self.session = zenoh.open(cfg)

        self.base = "rise/@v0"

        # ----------- ALL SUBSCRIPTIONS NOW USING construct_pubsub_key() -------------

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "location_fix", "gnss/0"),
            self._handle_location)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "course_over_ground_deg", "gnss/0"),
            self._handle_cog)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "speed_over_ground_knots", "gnss/0"),
            self._handle_sog)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "name", "registrar/0"),
            self._handle_name)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "mmsi_number", "registrar/0"),
            self._handle_mmsi)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "imo_number", "registrar/0"),
            self._handle_imo)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "nav_status", "bridge/0"),
            self._handle_nav_status)

        self.session.declare_subscriber(
            construct_pubsub_key(self.base, self.ship, "roc_status", "bridge/0"),
            self._handle_roc_status)

        # RAW zenoh strings (not keelson)
        self.session.declare_subscriber(
            f"{self.base}/{self.ship}/pubsub/remote_status/bridge/0",
            self._handle_remote_status)

        self.session.declare_subscriber(
            f"{self.base}/{self.ship}/pubsub/remote_time/bridge/1",
            self._handle_remote_time)

        print(f"{self.__class__.__name__} initialized.")


    # -------------------------------------------------------------------
    # DECODING HELPERS
    # -------------------------------------------------------------------

    def _decode(self, sample, cls):
        try:
            _, _, payload = uncover(sample.payload.to_bytes())
            return cls.FromString(payload)
        except Exception as e:
            print(f"[WARN] Decode failed for {cls.__name__}: {e}")
            return None


    # -------------------------------------------------------------------
    # MESSAGE CALLBACKS
    # -------------------------------------------------------------------

    def _handle_location(self, sample):
        msg = self._decode(sample, LocationFix)
        if msg:
            self.location = (msg.latitude, msg.longitude)
            if 'handle_location' in self.extra_callbacks:
                self.extra_callbacks['handle_location'](self.location[0], self.location[1])

    def _handle_cog(self, sample):
        msg = self._decode(sample, TimestampedFloat)
        if msg:
            self.cog = msg.value
            if 'handle_cog' in self.extra_callbacks:
                self.extra_callbacks['handle_cog'](self.cog)

    def _handle_sog(self, sample):
        msg = self._decode(sample, TimestampedFloat)
        if msg:
            self.sog = msg.value
            if 'handle_sog' in self.extra_callbacks:
                self.extra_callbacks['handle_sog'](self.sog)

    def _handle_name(self, sample):
        self._decode(sample, TimestampedString)

    def _handle_mmsi(self, sample):
        msg = self._decode(sample, TimestampedInt)
        if msg:
            self.mmsi = msg.value
            if 'handle_mmsi' in self.extra_callbacks:
                self.extra_callbacks['handle_mmsi'](self.mmsi)

    def _handle_imo(self, sample):
        msg = self._decode(sample, TimestampedInt)
        if msg:
            self.imo = msg.value
            if 'handle_imo' in self.extra_callbacks:
                self.extra_callbacks['handle_imo'](self.imo)

    def _handle_nav_status(self, sample):
        msg = self._decode(sample, VesselNavStatus)
        if msg:
            self.nav_status = VesselNavStatus.NavigationStatus.Name(msg.navigation_status)
            if 'handle_nav_status' in self.extra_callbacks:
                self.extra_callbacks['handle_nav_status'](self.nav_status)

    def _handle_roc_status(self, sample):
        roc_status = self._decode(sample, ROCStatus)
        if 'handle_roc_status' in self.extra_callbacks:
            self.extra_callbacks['handle_roc_status'](self.roc_status)

    def _handle_remote_status(self, sample):
        try:
            self.remote_status = sample.payload.to_string()
            if 'handle_remote_status' in self.extra_callbacks:
                self.extra_callbacks['handle_remote_status'](self.remote_status)
        except:
            self.remote_status = None

    def _handle_remote_time(self, sample):
        try:
            self.remote_time = float(sample.payload.to_string())
            if 'handle_remote_time' in self.extra_callbacks:
                self.extra_callbacks['handle_remote_time'](self.remote_time)
        except:
            self.remote_time = None

