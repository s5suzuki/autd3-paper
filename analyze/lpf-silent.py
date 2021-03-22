'''
File: lpf.py
Project: low-pass filter
Created Date: 29/05/2020
Author: Shun Suzuki
-----
Last Modified: 22/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2020 Hapis Lab. All rights reserved.

'''

import math
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import os
from shared import setup_pyplot


def plot():
    lpf_coeff = [-0.000094, -0.000126, -0.000163, -0.000205, -0.000252, -0.000305, -0.000362, -0.000424, -0.000491, -0.000563, -0.000638, -0.000717, -0.000798, -0.000881, -0.000964, -0.001047, -0.001127, -0.001204, -0.001275, -0.001339, -0.001392, -0.001433, -0.001458, -0.001465, -0.001451, -0.001412, -0.001345, -0.001245, -0.001110, -0.000934, -0.000713, -0.000444, -0.000121, 0.000261, 0.000706, 0.001219, 0.001805, 0.002468, 0.003214, 0.004048, 0.004973, 0.005995, 0.007118, 0.008347, 0.009684, 0.011134, 0.012700, 0.014385, 0.016192, 0.018123, 0.020179, 0.022362, 0.024672, 0.027111, 0.029676, 0.032367, 0.035184, 0.038122, 0.041180, 0.044353, 0.047638, 0.051029, 0.054522, 0.058109, 0.061784, 0.065539, 0.069366, 0.073256, 0.077201, 0.081189, 0.085211, 0.089255, 0.093311, 0.097367, 0.101411, 0.105431, 0.109414, 0.113347, 0.117218, 0.121015, 0.124724, 0.128332, 0.131828, 0.135200, 0.138434, 0.141520, 0.144447, 0.147204, 0.149780, 0.152166, 0.154353, 0.156333, 0.158098, 0.159642, 0.160959, 0.162043, 0.162890, 0.163498, 0.163864, 0.163986, 0.163864, 0.163498, 0.162890, 0.162043, 0.160959, 0.159642, 0.158098, 0.156333, 0.154353, 0.152166, 0.149780, 0.147204, 0.144447, 0.141520, 0.138434, 0.135200, 0.131828, 0.128332, 0.124724, 0.121015, 0.117218, 0.113347, 0.109414, 0.105431, 0.101411, 0.097367, 0.093311, 0.089255, 0.085211, 0.081189, 0.077201, 0.073256, 0.069366, 0.065539, 0.061784, 0.058109, 0.054522, 0.051029, 0.047638, 0.044353, 0.041180, 0.038122, 0.035184, 0.032367, 0.029676, 0.027111, 0.024672, 0.022362, 0.020179, 0.018123, 0.016192, 0.014385, 0.012700, 0.011134, 0.009684, 0.008347, 0.007118, 0.005995, 0.004973, 0.004048, 0.003214, 0.002468, 0.001805, 0.001219, 0.000706, 0.000261, -0.000121, -0.000444, -0.000713, -0.000934, -0.001110, -0.001245, -0.001345, -0.001412, -0.001451, -0.001465, -0.001458, -0.001433, -0.001392, -0.001339, -0.001275, -0.001204, -0.001127, -0.001047, -0.000964, -0.000881, -0.000798, -0.000717, -0.000638, -0.000563, -0.000491, -0.000424, -0.000362, -0.000305, -0.000252, -0.000205, -0.000163, -0.000126, -0.000094]  # NOQA

    fs = 40e3
    fn = fs / 2

    fig = plt.figure(figsize=(6, 4), dpi=DPI)
    ax = fig.add_subplot(111)
    f1, h1 = signal.freqz(lpf_coeff, fs=fn)
    ax.semilogx(f1, 20 * np.log10(abs(h1) / 10))
    plt.ylabel('Gain [dB]', fontname='Arial', fontsize=18)
    plt.xlabel('Frequency [Hz]', fontname='Arial', fontsize=18)
    ax.set_ylim(-150, 5)
    plt.yticks(fontname='Arial', fontsize=16)
    plt.xticks(fontname='Arial', fontsize=16)

    # delete right up frame
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'lpf_filter' + ext), bbox_inches='tight', pad_inches=0)

    # filter effect
    n = 500
    dt = 1 / fs
    t = np.linspace(1, n, n) * dt - dt
    y = [math.pi if i > 200 else 0 for i in range(n)]
    y_filter = signal.lfilter(lpf_coeff, 1, y) / 10

    fig = plt.figure(figsize=(6, 4), dpi=DPI)
    ax = fig.add_subplot(111)
    plt.plot(t, y, label="Without LPF")
    plt.plot(t, y_filter, label="With LPF", linestyle='dashed')
    plt.yticks([0, math.pi / 2, math.pi], ['0', r'$\frac{\pi}{2}$', r'$\pi$'], fontname='Arial', fontsize=16)
    plt.xticks((np.linspace(1, n, 6) - 1) * dt, ['0', '2.5', '5', '7.5', '10', '12.5'], fontname='Arial', fontsize=16)
    plt.ylabel('Phase [rad]', fontname='Arial', fontsize=18)
    plt.xlabel('Time [ms]', fontname='Arial', fontsize=18)
    plt.legend(bbox_to_anchor=(1, 0), loc='lower right', borderaxespad=1, fontsize=14, frameon=False)

    # delete right up frame
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_xlim(0, n * dt)
    ax.set_ylim(0, math.pi + 0.05)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'phase_filtered' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    plot()
