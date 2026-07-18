# MC8_Pro - MIDI Remote Script
# Generated with midiremotescripts.structure-void.com/generator
# This generated script is yours: public domain (CC0 1.0), no restrictions.

from __future__ import absolute_import
from _Framework.ControlSurface import ControlSurface
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.TransportComponent import TransportComponent
import logging

logger = logging.getLogger(__name__)
class MC8_Pro(ControlSurface):

    def __init__(self, c_instance):
        super(MC8_Pro, self).__init__(c_instance)
        with self.component_guard():
            self._build()

    def _build(self):
        transport = TransportComponent()

        play_button = DynamicFeedbackButton(True, MIDI_CC_TYPE, 0, 55, 4)
        stop_button = DynamicFeedbackButton(True, MIDI_CC_TYPE, 0, 56, 5)
        record_button = DynamicFeedbackButton(True, MIDI_CC_TYPE, 0, 57, 6)

        transport.set_play_button(play_button)
        transport.set_stop_button(stop_button)
        transport.set_record_button(record_button)

    def send_morningstar_midi(self, status, target_cc, feedback_val):
        """
        A completely independent method dedicated ONLY to Morningstar feedback.
        It bypasses standard Ableton pipeline logic, leaves standard _send_midi intact,
        and respects Ableton's optimization/accumulation queue.
        """
        midi_tuple = (status, target_cc, feedback_val)
        logger.info("Morningstar Custom Routing: Status={}, CC={}, Val={}".format(status, target_cc, feedback_val))

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

    def disconnect(self):
        super(MC8_Pro, self).disconnect()

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

