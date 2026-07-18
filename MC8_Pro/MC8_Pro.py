# MC8_Pro - MIDI Remote Script
# Generated with midiremotescripts.structure-void.com/generator
# This generated script is yours: public domain (CC0 1.0), no restrictions.

from __future__ import absolute_import
from _Framework.ControlSurface import ControlSurface
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.TransportComponent import TransportComponent

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

    def disconnect(self):
        super(MC8_Pro, self).disconnect()

class DynamicFeedbackButton(ButtonElement):
    def __init__(self, is_momentary, msg_type, channel, identifier, feedback_val, *a, **k):
        super(DynamicFeedbackButton, self).__init__(is_momentary, msg_type, channel, identifier, *a, **k)
        self.feedback_val = feedback_val
    
    def _send_midi(self, midi_event_bytes, optimized=True):
        new_cc = 2 if midi_event_bytes[0] > 0 else 3
        new_val = self.feedback_val
        if self._accumulate_midi_messages:
            sysex_status_byte = 240
            entry = (self._midi_message_count, midi_event_bytes)
            if optimized and midi_event_bytes[0] != sysex_status_byte:
                self._midi_message_dict[(new_cc, new_val)] = entry
            else:
                self._midi_message_list.append(entry)
            self._midi_message_count += 1
        else:
            self._do_send_midi((new_cc, new_val))
        return True
