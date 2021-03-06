import zmq
import numpy as np
import pdb
from synth_commands import *

import os
import matplotlib.pyplot as plt

SWITCH_PATH1 = 1
SWITCH_PATH0 = 0

# table of output power setting vs. frequency for 7 dBm output with a hmc311 following the synth
# currently done manually..
HMC311_7DBM_TABLE_POW = [14, 8, 12, 8, 6, 1, 5, 10, 31, 31, 31]
HMC311_7DBM_TABLE_ATT = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
HMC311_3DBM_TABLE_POW = [10, 5, 5, 3, 2, 0, 0, 10, 10, 10, 10]
HMC311_3DBM_TABLE_ATT = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
HMC311_TABLE_FREQ = [250e6, 500e6, 1e9, 2e9, 2.5e9, 3e9, 3.5e9, 4e9, 5e9, 6e9, 7e9]

# table for 0 dBm out of rf synth with hmc311 amp board at output
RF_TABLE_FREQ = [2e9, 2.5e9, 3e9, 3.5e9, 4e9, 4.5e9, 5e9, 5.5e9, 6e9, 6.5e9, 7e9, 7.5e9, 8e9, 8.5e9, 9e9, 9.5e9, 10e9]
RF_TABLE_POW =  [0,   0,     0,   0,     0,   7,     7,   12,    12,  16,    14,  20,    20,  20,    20,  20,    20]
RF_TABLE_ATT =  [2.5, 2.5,   6,   3,     0,   0,     0,   0,     0,   0,      0,  0,     0,   0,     0,   0,     0]

class zmq_synth:
    def __init__(self, context, synth_ip, synth_port):
        self.sock = context.socket(zmq.REQ)
        self.sock.connect("tcp://{}:{}".format(synth_ip, synth_port))
        
        self.freq = np.float32(0)
        self.pow_cal = False   

    def _eth_cmd(self, cmd, payload):
        self.sock.send(cmd + str(payload))
        reply = self.sock.recv()
        assert reply[COMMAND_INDEX] == cmd
        return reply[COMMAND_INDEX:]
   
    def set_freq(self, f):
        self.freq = int(f)
        self._eth_cmd(FREQ_CMD, f)

    def wait_for_lock(self):
        self._eth_cmd(WAIT_CMD, '')

    def set_filt(self, f):
        self.freq = int(f)
        self._eth_cmd(FILT_CMD, f)

    def set_pow(self, power):
        self.channel_power = int(power)
        self._eth_cmd(POW_CMD, int(power))
    
    # hacked open-loop amplitude control until power detect board arrives
    # control LO for 7 dBm (optimum power into mixer)
    # leave RF synth uncontrolled, amplitude variation is controlled during calibration
    def level_pow(self, cal):
        freqs = HMC311_TABLE_FREQ
        pows = HMC311_3DBM_TABLE_POW
        atts = HMC311_3DBM_TABLE_ATT

        if cal == LO_CAL:
            freqs = HMC311_TABLE_FREQ
            pows = HMC311_3DBM_TABLE_POW
            atts = HMC311_3DBM_TABLE_ATT
            print('LO cal: ')
        
        if cal == RF_CAL:
            freqs = RF_TABLE_FREQ
            pows = RF_TABLE_POW 
            atts = RF_TABLE_ATT
            print('RF cal: ')


        pow_setting = int(np.interp(self.freq, freqs, pows))
        att_setting = int(np.interp(self.freq, freqs, atts))
        
        print('pow: {}, att: {}'.format(pow_setting, att_setting))

        self.set_att(att_setting) 
        self.set_pow(pow_setting) # TODO: this assumes freq < F_VCO_MAX, always picks path 0..
        
    def set_att(self, att):
        self._eth_cmd(ATT_CMD, att)

if __name__ == '__main__':
    context = zmq.Context()

    lo_port = SYNTH_PORTS['a']
    rf_port = SYNTH_PORTS['b']

    RF_IP = 'bbone'
    LO_IP = 'bbone'
    print('connecting to LO synth')
    lo_synth = zmq_synth(context, LO_IP, lo_port)

    print('connected, changing frequency')
    lo_synth.set_freq(2.2e9);
    lo_synth.set_filt(3.2e9);
    lo_synth.set_pow(0);
    lo_synth.set_att(5);


    pdb.set_trace()
