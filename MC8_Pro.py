# MC8_Pro - MIDI Remote Script
# Generated with midiremotescripts.structure-void.com/generator
# This generated script is yours: public domain (CC0 1.0), no restrictions.

from __future__ import absolute_import
from _Framework.ControlSurface import ControlSurface
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.TransportComponent import TransportComponent
from ableton.v2.base import Slot, SlotGroup
from ableton.v2.base import listens_group

import logging

from .SysExMessenger import SysExMessenger

logger = logging.getLogger(__name__)
class MC8_Pro(ControlSurface):

    def __init__(self, c_instance):
        super(MC8_Pro, self).__init__(c_instance)
        with self.component_guard():
            self._build()

    def _build(self):

        self._messenger = SysExMessenger(self._send_midi)

        self.BUTTON_CC_NUMBERS = [58, 59, 60, 61] # Select between the first 4 chains in the first rack of the current track
        self.MIDI_CHANNEL = 0 # Channel 1 in Ableton is index 0 in Python

        transport = TransportComponent()

        play_button = DynamicFeedbackButton(True, MIDI_CC_TYPE, 0, 55, 4)
        stop_button = DynamicFeedbackButton(True, MIDI_CC_TYPE, 0, 56, 5)
        record_button = DynamicFeedbackButton(True, MIDI_CC_TYPE, 0, 57, 6)

        transport.set_play_button(play_button)
        transport.set_stop_button(stop_button)
        transport.set_record_button(record_button)

        self._chain_select_buttons = self._create_chain_select_buttons()

        self._macro_listener_slot = Slot(listener=self._update_led_feedback, event_name="value")

        self._chain_name_slots = SlotGroup(listener=self._on_chain_name_changed, event_name="name")
        self._chain_color_slots = SlotGroup(listener=self._on_chain_color_changed, event_name="color")
        self._on_chain_selector_value.replace_subjects(self._chain_select_buttons)

        self._rack_chains_slot = Slot(
            listener=self._on_rack_structure_changed,
            event_name="chains"
        )

        self._selected_track_slot = Slot(
        subject=self.song().view,       # Must observe the view object!
        listener=self._on_track_changed, # Your track changer function
        event_name="selected_track"     # Looks for 'selected_track_has_listener'
        )

        self._on_track_changed()

    def _create_chain_select_buttons(self):
        buttons = []
        for feedback_val, cc in enumerate(self.BUTTON_CC_NUMBERS):
            btn = DynamicFeedbackButton(True, MIDI_CC_TYPE, self.MIDI_CHANNEL, cc, feedback_val)
            buttons.append(btn)

        return buttons

    def _get_first_rack_device(self,track):
        """Helper to find the first valid rack device on the track"""
        for device in track.devices:
            if device.can_have_chains:
                return device
        return None

    def _on_track_changed(self):

        # logger.info('Track Changed')
        """Triggered automatically when switching tracks"""
        
        track = self.song().view.selected_track
        device = self._get_first_rack_device(track)
        
        if device is not None:
            # 1. Listen to macro value changes for LEDs
            if len(device.parameters) > 1:
                self._macro_listener_slot.subject = device.parameters[1]
            else:
                self._macro_listener_slot.subject = None
            # 2. Listen to structural rack changes (Add, Delete, Move chains)
            self._rack_chains_slot.subject = device
            
            # 3. Setup individual text change listeners for current chains
            self._setup_chain_name_listeners(device.chains)
            self._setup_chain_color_listeners(device.chains)
        else:
            self._rack_chains_slot.subject = None

        self._on_rack_structure_changed()

    def _setup_chain_name_listeners(self, chains):
        """Attaches rename listeners to up to the first 4 chains safely using SlotGroup"""
        # Slice the first 4 chains
        target_chains = chains[:4]
        
        # replace_subjects automatically removes old listeners, ignores deleted/null objects, 
        # and safely binds the 'name' listener to the new 1-4 chains.
        self._chain_name_slots.replace_subjects(target_chains)

    def _setup_chain_color_listeners(self, chains):
        """Attaches rename listeners to up to the first 4 chains safely using SlotGroup"""
        # Slice the first 4 chains
        target_chains = chains[:4]
        
        # replace_subjects automatically removes old listeners, ignores deleted/null objects, 
        # and safely binds the 'name' listener to the new 1-4 chains.
        self._chain_color_slots.replace_subjects(target_chains)

    def _on_rack_structure_changed(self, *args):

        # logger.error('Rack Structure Changed')
        """Triggered when chains are added, deleted, or moved inside the rack"""
        device = self._rack_chains_slot.subject

        if device is not None:
            # Pass the new chain list. SlotGroup safely cleans up the old, dead chains.
            self._setup_chain_name_listeners(device.chains)
            self._setup_chain_color_listeners(device.chains)
        else:
            # If the rack itself was deleted, completely clear all tracked chain slots safely
            self._chain_name_slots.replace_subjects([])
            self._chain_color_slots.replace_subjects([])

        # Force structural recalculation updates down to the hardware
        self._update_all_button_names()
        self._update_all_button_leds()
        self._update_led_feedback()

    def _on_chain_name_changed(self, chain):
        """Triggered when a specific visible chain is explicitly renamed"""
        self._update_all_button_names()

    def _on_chain_color_changed(self, chain):
        # logger.info('Chain Color Changed')
        self._update_all_button_leds()

    def _update_all_button_names(self):
        """Updates text fields or blanks them if chains were deleted"""
        device = self._rack_chains_slot.subject
        chains = device.chains if device is not None else []

        for index in range(4):
            if index < len(chains):
                self._messenger.send_name_sysex(index, chains[index].name)
            else:
                self._messenger.send_name_sysex(index, "[EMPTY]")

    def _update_all_button_leds(self):
        """Updates colors blanks them if chains were deleted"""
        device = self._rack_chains_slot.subject
        chains = device.chains if device is not None else []
        # logger.info('Updating chain colors.')
        for index in range(4):
            if index < len(chains):
                self._messenger.send_color_sysex(index, chains[index].color_index)
                # logger.info(f"New Color index: {chains[index].color_index}")
            else:
                self._messenger.send_color_sysex(index, 0)

    @listens_group('value')
    def _on_chain_selector_value(self, value, button):

        if value == 0:
            return

        device = self._rack_chains_slot.subject
        if device is None or len(device.parameters) <= 1:
            return

        macro_1 = self._macro_listener_slot.subject
        total_chains = len(device.chains)
        if total_chains == 0:
            return

        btn_index = self._chain_select_buttons.index(button)
        if btn_index >= total_chains:
            return

        step_size = 128.0 / total_chains
        target_value = int((btn_index * step_size) + (step_size / 2))
        macro_1.value = target_value

    def _update_led_feedback(self,):
        device = self._rack_chains_slot.subject
        # logger.info(f"Device name is: {device.name if device else 'NO DEVICE'}")
        if device is None or len(device.parameters) <= 1 or len(device.chains) <=0:
            for btn in self._chain_select_buttons:
                btn.send_value(0)
            return

        macro_1 = device.parameters[1]
        total_chains = len(device.chains)

        step_size = 128.0 / total_chains
        active_index = int(macro_1.value / step_size)
        if active_index >= total_chains:
            active_index = total_chains - 1

        for index, btn in enumerate(self._chain_select_buttons):
            if index == active_index and index < total_chains:
                btn.send_value(127) 
            else:
                btn.send_value(0)   

    def handle_sysex(self, midi_bytes):
        self._messenger.parse_incoming_sysex(midi_bytes)

    def disconnect(self):
        self._macro_listener_slot.disconnect()
        self._chain_name_slots.disconnect()
        self._chain_color_slots.disconnect()
        self._rack_chains_slot.disconnect()
        for slot in self._chain_select_buttons:
            slot.disconnect()

        super(MC8_Pro, self).disconnect()

    def send_morningstar_midi(self, status, target_cc, feedback_val):
        """
        A completely independent method dedicated ONLY to Morningstar feedback.
        It bypasses standard Ableton pipeline logic, leaves standard _send_midi intact,
        and respects Ableton's optimization/accumulation queue.
        """
        midi_tuple = (status, target_cc, feedback_val)
        # logger.info("Morningstar Custom Routing: Status={}, CC={}, Val={}".format(status, target_cc, feedback_val))

        # Check if Ableton is accumulating MIDI optimization buffers
        if self._accumulate_midi_messages:
            entry = (self._midi_message_count, midi_tuple)
            
            # Use a unique tuple descriptor to avoid overwriting or clashing with 
            # standard CC values in the global cache dictionary
            self._midi_message_dict[('morningstar', target_cc, feedback_val)] = entry
            self._midi_message_count += 1
        else:
            # Safely pass it down to Ableton's raw output port pipeline
            self._do_send_midi(midi_tuple)
        return True

class DynamicFeedbackButton(ButtonElement):
    def __init__(self, is_momentary, msg_type, channel, identifier, feedback_val, *a, **k):
        super(DynamicFeedbackButton, self).__init__(is_momentary, msg_type, channel, identifier, *a, **k)
        self.feedback_val = feedback_val

    def _do_send_value(self, *a, **k):
        """
        Extracts the true realtime state being pushed by Ableton 
        directly out of the incoming argument wrapper tuple (*a).
        """
        # Look up the main root class instance via canonical_parent
        parent_script = getattr(self, 'canonical_parent', None)
        
        # If the parent is a component wrapper, climb up to reach the main script
        if parent_script and not hasattr(parent_script, 'send_morningstar_midi'):
            parent_script = getattr(parent_script, 'canonical_parent', None)
        
        # Grab the actual realtime value Ableton is pushing down the line right now.
        # If for any reason 'a' is empty, fallback safely to 0.
        realtime_value = a[0] if a else 0

        # Determine Morningstar parameters (CC 2 = ON, CC 3 = OFF)
        target_cc = 2 if bool(realtime_value) else 3
        channel = self.message_channel()
        status_byte = 0xB0 | channel
        
        # Send cleanly to your isolated custom script method
        parent_script.send_morningstar_midi(status_byte, target_cc, self.feedback_val)

