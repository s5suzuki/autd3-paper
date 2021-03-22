'''
File: individual_diff.py
Project: analyze
Created Date: 19/02/2021
Author: Shun Suzuki
-----
Last Modified: 22/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.

'''


from shared import setup_pyplot, get_40kHz_amp, print_progress, get_40kHz_phase
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import re
from scipy.stats import norm
from scipy.optimize import curve_fit


def count_transducers(data_path):
    total = 0
    for dev_dir in glob.glob(os.path.join(data_path, '*')):
        for tr_dir in glob.glob(os.path.join(dev_dir, '*')):
            total += 1

    return total


def get_amp_data(data_path, total):
    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    sample_rate = cond.at[0, 1]
    mV_per_Pa = cond.at[2, 1]
    dt = 1.0 / sample_rate

    p = re.compile(r'x([+-]?\d+\.?\d+?)y([+-]?\d+\.?\d+?)z([+-]?\d+\.?\d+?).csv')

    results = pd.DataFrame(columns=['amp'])
    c = 0
    for dev_dir in glob.glob(os.path.join(data_path, '*')):
        for tr_dir in glob.glob(os.path.join(dev_dir, '*')):
            for filepath in glob.glob(os.path.join(tr_dir, '*')):
                m = p.match(filepath.split(os.path.sep)[-1])
                if m is None:
                    continue

                z = int(float(m.group(3)))
                if z != 200:
                    continue

                df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
                sound = df['  A Max [mV]']
                results.at[c, 'amp'] = get_40kHz_amp(sound, dt) / mV_per_Pa / np.sqrt(2)
                c += 1
                print_progress(c, total)
    print()
    results.to_csv('individual_amp.csv')


def plot_hist_amp():
    df = pd.read_csv(filepath_or_buffer='individual_amp.csv', sep=',', index_col=0)
    x = df.values
    print(x.min(), x.max())
    print('num data:', len(x))
    param = norm.fit(x)
    print(param)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)

    bins = 36
    plt_range_max = 3
    amps = np.linspace(0, 3, 1000)
    pdf_fitted = norm.pdf(amps, loc=param[0], scale=param[1])
    mu = f'{param[0]:.2f}'
    sigma = f'{param[1]:.2f}'
    label = 'Gaussian' + '\n' + r'$\ \mu=' + mu + '$\n ' + r'$\ \sigma=' + sigma + '$'
    ax.plot(amps, len(x) * plt_range_max / bins * pdf_fitted, label=label)

    ax.hist(x, bins=bins, range=(0, plt_range_max), label='measured')

    ax.set_xlim(0, 3)
    ax.set_ylim(0, 400)
    ax.set_xlabel('RMS of acoustic pressure [Pa]', fontname='Arial', fontsize=24)
    ax.set_ylabel('Freqency', fontname='Arial', fontsize=24)
    ax.legend()
    ax.set_xticks([0, 1, 2, 3])
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)

    plt.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=1, fontsize=18, frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join('plot', 'amp_individual_diff' + ext), bbox_inches='tight', pad_inches=0)


def surf2d(xy, a, b, d):
    x, y = xy[0:2]
    return a * x + b * y + d


def surf2d_fit(xy, a, b, d):
    return surf2d(xy, a, b, d).ravel()


def process_phase_data_dev(dev_dir, cond):
    sample_rate = cond.at[0, 1]
    dt = 1.0 / sample_rate

    p = re.compile(r'x([+-]?\d+\.?\d+?)y([+-]?\d+\.?\d+?)z([+-]?\d+\.?\d+?).csv')
    x_axis = []
    y_axis = []
    for tr_dir in glob.glob(os.path.join('./raw_data/individual/dev0', '*')):
        for filepath in glob.glob(os.path.join(tr_dir, '*')):
            m = p.match(filepath.split(os.path.sep)[-1])
            if m is None:
                continue

            if int(float(m.group(3))) != 200:
                continue

            x = float(m.group(1))
            y = float(m.group(2))

            x_axis.append(x)
            y_axis.append(y)

    x_axis = np.array(sorted(set(x_axis)))
    y_axis = np.array(sorted(set(y_axis)))

    results = pd.DataFrame(columns=x_axis, index=y_axis)
    for tr_dir in glob.glob(os.path.join('./raw_data/individual/dev0', '*')):
        for filepath in glob.glob(os.path.join(tr_dir, '*')):
            m = p.match(filepath.split(os.path.sep)[-1])
            if m is None:
                continue

            if int(float(m.group(3))) != 200:
                continue

            x = float(m.group(1))
            y = float(m.group(2))

            df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
            sound = df['  A Max [mV]']

            results.at[y, x] = get_40kHz_phase(sound, dt)

    x_fit = []
    y_fit = []
    phase_fit = []
    for col in results.columns:
        for row in results.index:
            if np.isnan(results.at[row, col]):
                continue
            x_fit.append(col)
            y_fit.append(row)
            phase_fit.append(results.at[row, col])

    x_fit = np.array(x_fit)
    y_fit = np.array(y_fit)
    phase_fit = np.array(phase_fit)
    popt, pcov = curve_fit(surf2d_fit, (x_fit, y_fit), phase_fit)

    for col in results.columns:
        for row in results.index:
            if np.isnan(results.at[row, col]):
                continue
            x = float(col)
            y = float(row)
            phase = results.at[row, col] - surf2d((x, y), *popt)
            results.at[row, col] = phase

    return np.array(list(map(lambda x: float(x), filter(lambda x: not np.isnan(x), results.values.flatten()))))


def get_phase_data(data_path, total):
    p = re.compile(r'dev(\d+)')
    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    phases = np.array([])
    print_progress(len(phases), total)
    for dev_dir in glob.glob(os.path.join(data_path, '*')):
        m = p.match(dev_dir.split(os.path.sep)[-1])
        if m is None:
            continue
        phases = np.concatenate([phases, process_phase_data_dev(dev_dir, cond)])
        print_progress(len(phases), total)
    print()

    results = pd.DataFrame(columns=['phase'])
    results['phase'] = phases

    results.to_csv('individual_phase.csv')


def plot_hist_phase():
    df = pd.read_csv(filepath_or_buffer='individual_phase.csv', sep=',', index_col=0)
    x = df.values
    print(x.min(), x.max())
    print('num data:', len(x))
    param = norm.fit(x)
    print(param)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)

    bins = 36
    amps = np.linspace(-np.pi, np.pi, 1000)
    pdf_fitted = norm.pdf(amps, loc=param[0], scale=param[1])
    mu = f'{param[0]:.2f}'
    sigma = f'{param[1]:.2f}'
    label = 'Gaussian' + '\n' + r'$\ \mu=' + mu + '$\n ' + r'$\ \sigma=' + sigma + '$'
    ax.plot(amps, len(x) * 2 * np.pi / bins * pdf_fitted, label=label)

    ax.hist(x, bins=bins, range=(-np.pi, np.pi), label='measured')

    ax.set_xlim(-np.pi, np.pi)
    ax.set_xlabel('Phase [rad]', fontname='Arial', fontsize=24)
    ax.set_ylabel('Freqency', fontname='Arial', fontsize=24)
    ax.legend()
    ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    ax.set_xticklabels([r'$-\pi$', r'$-\frac{\pi}{2}$', r'$0$', r'$\frac{\pi}{2}$', r'$\pi$'])

    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)

    plt.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=1, fontsize=18, frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join('plot', 'phase_individual_diff' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    data_path = './raw_data/individual'
    total = count_transducers(data_path)

    print('amp')
    get_amp_data(data_path, total)
    plot_hist_amp()

    print('phase')
    get_phase_data(data_path, total)
    plot_hist_phase()
