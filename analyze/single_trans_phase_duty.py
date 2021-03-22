'''
File: single_trans_phase_duty.py
Project: analyze
Created Date: 16/02/2021
Author: Shun Suzuki
-----
Last Modified: 22/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.

'''


import glob
import math
import re
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from shared import setup_pyplot, get_40kHz_amp, print_progress


def sin_fit(v, a):
    res = (np.sin(v)) ** a
    return res


def normalized(array):
    max_v = array.max()
    min_v = array.min()
    return (array - min_v) / (max_v - min_v)


def get_amp_data(data_path):
    p = re.compile(r'amp(\d+).csv')

    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    sample_rate = cond.at[0, 1]
    mV_per_Pa = cond.at[2, 1]
    dt = 1.0 / sample_rate

    results_sound = np.zeros(256)
    c = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
        sound = df['  A Max [mV]']

        duty = int(m.group(1))
        results_sound[duty] = get_40kHz_amp(sound, dt) / mV_per_Pa / np.sqrt(2)
        c += 1
        print_progress(c, 256)

    print()
    print(f'max [Pa]: {results_sound.max()}')

    return normalized(results_sound)


def get_input_data(data_path):
    p = re.compile(r'input(\d+).csv')

    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    sample_rate = cond.at[0, 1]
    dt = 1.0 / sample_rate

    results_input = np.zeros(256)
    c = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
        input_sig = df['  A Max [mV]']

        duty = int(m.group(1))
        results_input[duty] = get_40kHz_amp(input_sig, dt)
        c += 1
        print_progress(c, 256)

    print()

    return normalized(results_input)


def duty(amp_path, input_path):
    sound_data = get_amp_data(amp_path)
    input_data = get_input_data(input_path)

    x = np.linspace(0, 255, 256)

    param, cov = curve_fit(sin_fit, (x / (2 * 255.0) * math.pi), sound_data, p0=[0.75], maxfev=2000)
    poten = param[0]
    print('alpha = ', poten)

    fig = plt.figure(figsize=(6, 6), dpi=DPI)
    ax = fig.add_subplot(111)
    x = np.linspace(0, 255, 256)
    theo = list(map(lambda x: math.sin(x), x / (2 * 255.0) * math.pi))
    ax.plot(x, sound_data, marker='.', markersize=4, linestyle='None', zorder=0, label='measured acoustic amp.')
    ax.plot(x, input_data, marker='+', markersize=4, linestyle='None', zorder=1, label='40 kHz component of input')
    ax.plot(x, theo, linewidth=1, zorder=3, label='theoretical')
    fit_model = list(map(lambda x: math.sin(x) ** poten, x / (2 * 255.0) * math.pi))
    ax.plot(x, fit_model, linewidth=1, label=r'$\sin^{0.803}$', zorder=2, linestyle='dashed')
    plt.ylabel('Normalized amplitude [-]', fontname='Arial', fontsize=18)
    plt.xlabel(r'Duty ratio $D$ [-]', fontname='Arial', fontsize=18)
    plt.yticks([0, 0.5, 1], [r'$0$', r'$0.5$', r'$1$'], fontname='Arial', fontsize=16)
    plt.xticks([0, 127, 255], ['0', '127', '255'], fontname='Arial', fontsize=16)
    plt.legend(bbox_to_anchor=(1, 0), loc='lower right', borderaxespad=1, fontsize=16, frameon=False, markerscale=2)

    # delete right up frame
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_xlim(0, 255)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'measured_amp_input' + ext), bbox_inches='tight', pad_inches=0)


def phase(data_path):
    p = re.compile(r'phase(\d+).csv')

    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    sample_rate = cond.at[0, 1]
    dt = 1.0 / sample_rate
    period = 25e-6

    df = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'phase0.csv'), sep=",")
    sig_base = df['  A Max [mV]']
    sig_base = sig_base - sig_base.mean()

    results = np.zeros(256)
    c = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
        sig = df['  A Max [mV]']
        sig = sig - sig.mean()

        corr = np.correlate(sig, sig_base, "full")
        delay = corr.argmax() - (len(sig) - 1)
        phases_delay = delay * dt / period * 2 * math.pi
        if phases_delay < 0:
            phases_delay += 2 * math.pi
        phases_delay %= 2 * math.pi

        phase_value = int(m.group(1))
        results[phase_value] = phases_delay
        c += 1
        print_progress(c, 256)
    print()

    x = np.linspace(0, 255, 256)
    fig = plt.figure(figsize=(6, 6), dpi=DPI)
    ax = fig.add_subplot(111)
    ax.plot(x, results, marker='.', zorder=2, markersize=4, linestyle='None', label='measured')
    ax.plot(x, x / 256.0 * 2 * math.pi, zorder=1, linewidth=1, label='theoretical')
    plt.ylabel('Phase [rad]', fontname='Arial', fontsize=18)
    plt.xlabel(r'$S$ [-]', fontname='Arial', fontsize=18)
    plt.yticks([0, math.pi, 2 * math.pi], [r'$0$', r'$\pi$', r'$2\pi$'], fontname='Arial', fontsize=16)
    plt.xticks([0, 127, 255], ['0', '127', '255'], fontname='Arial', fontsize=16)
    plt.legend(bbox_to_anchor=(1, 0), loc='lower right', borderaxespad=1, fontsize=16, frameon=False, markerscale=2)

    # delete right up frame
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_xlim(0, 255)
    ax.set_ylim(0, 2 * math.pi)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'measured_phase' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    duty('./raw_data/single_amp', './raw_data/single_input')
    phase('./raw_data/single_phase')
