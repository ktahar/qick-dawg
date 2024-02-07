"""
PLIntensity
===========
A NVAveragerProgram class that turns the laser source on and returns averaged
ADC values over an integration time.
"""

from .nvaverageprogram import NVAveragerProgram

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

class PLIntensity(NVAveragerProgram):
    """
    NVAveragerProgram which simply turns on an AOM and collects PL intensity from an 
    the adc for a time defined by cfg.readout_integrat_t#

    Parameters
    ----------
    cfg
        instance of `.NVConfiguration` class with attributes
        .adc_channel : int
            0 or 1 - adc channel for collecting data
        .laser_gate_pmod : int
            typicall 0 to 6 - pmod channel to trigger the laser gating
        .relax_delay_treg : int
            delay time between acquisitions so everything syncs, typicaly 1us or less
        .readout_integration_treg : int
            PL integration time for each data point
        .reps : int
            number of repititions for collecting PL intensity data
    """

    required_cfg = [
        "adc_channel",
        "laser_gate_pmod",
        "readout_integration_treg",
        "relax_delay_treg",
        "reps"]

    def initialize(self):
        """
        Method that generates the assembly code that initializes the pulse sequence. 

        For qickdawg.PLIntensity,  this simply sets up the adc to integrate for self.cfg.readout_intregration_t#
        """

        self.check_cfg()

        self.declare_readout(ch=self.cfg.adc_channel,
                             freq=0,
                             length=self.cfg.readout_integration_treg,
                             sel="input")

        self.synci(200)  # give processor some time to cfgure pulses

    def body(self):
        """
        Method that generates the assembly code that is looped over or repeated. 
        For qickdawg.PLIntensity this sets the PMODs to high for self.cfg.readout_integration_t#
        """
        self.trigger(
            adcs=[self.cfg.adc_channel],
            pins=[self.cfg.laser_gate_pmod],
            width=self.cfg.readout_integration_treg,
            t=0)

        self.wait_all()
        self.sync_all(self.cfg.relax_delay_treg)

    def acquire(self, *arg, **kwarg):
        '''
        Method that overloads the qickdawg.NVAvergerProgram.acquire() method to analyze the output
        to a single point which is the mean of the returned data points divided by
        self.cfg.readout_integration_treg
        '''
        data = super().acquire(*arg, **kwarg)

        data = np.mean(data) / self.cfg.readout_integration_treg

        return data

    def plot_sequence(cfg=None):
      
        '''
        Method that plots the pulse sequence generated by this program

        Parameters
        ----------
        cfg: `.NVConfiguration` or None(default None)
            If None, this plots the squence with configuration labels
            If a `.NVConfiguration` object is supplied, the configuraiton value are added to the plot
        '''

        graphics_folder = os.path.join(os.path.dirname(__file__), '../../graphics')
        image_path = os.path.join(graphics_folder, 'PL.png')

        if cfg is None:
            plt.figure(figsize=(8, 8))
            plt.axis('off')
            plt.imshow(mpimg.imread(image_path))
            plt.text(490, 680, "config.reps", fontsize=12)
            plt.text(290, 445, "config.readout_integration_t#", fontsize=12)
            plt.text(1000, 445, "config.relax_delay_t#", fontsize=12)
            plt.title("PL Pulse Sequence", fontsize=20)
        else:
            # Display PL Pulse Sequence Configuration 
            plt.figure(figsize=(8, 8))
            plt.axis('off')
            plt.imshow(mpimg.imread(image_path))
            plt.text(490, 680, "Repeat {} times".format(cfg.reps), fontsize=12)
            plt.text(290, 440, "readout_integration = {} us".format(int(cfg.readout_integration_tus)), fontsize=12)
            plt.text(1000, 445, "relax_delay = {} us".format(str(cfg.relax_delay_tus)[:4]), fontsize=12)
            plt.title("PL Pulse Sequence", fontsize=20)
