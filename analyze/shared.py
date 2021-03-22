'''
File: shared.py
Project: analyze
Created Date: 16/02/2021
Author: Shun Suzuki
-----
Last Modified: 20/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.

'''

import matplotlib.pyplot as plt
import numpy as np


def setup_pyplot():
    plt.rcParams['text.usetex'] = True
    plt.rcParams['axes.grid'] = False
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 1.0
    plt.rcParams['ytick.major.width'] = 1.0
    plt.rcParams['font.size'] = 16
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams["mathtext.fontset"] = 'stixsans'
    plt.rcParams['ps.useafm'] = True
    plt.rcParams['pdf.use14corefonts'] = True
    plt.rcParams['text.latex.preamble'] = r'\usepackage{sfmath}'


def find_nearest(array, value):
    array = np.asarray(array)
    return (np.abs(array - value)).argmin()


def get_40kHz_amp(array, dt):
    N = len(array)
    spectrum = np.fft.rfft(array) / (N / 2)
    magnitude = np.abs(spectrum)
    f = np.fft.rfftfreq(N, dt)
    idx = find_nearest(f, 40e3)
    return magnitude[idx]


def get_40kHz_phase(array, dt):
    N = len(array)
    spectrum = np.fft.rfft(array) / (N / 2)
    phases = np.angle(spectrum)
    f = np.fft.rfftfreq(N, dt)
    idx = find_nearest(f, 40e3)
    return phases[idx]


def print_progress(i, total, width=32):
    r = int((i * width) / total)
    progress = '#' * r + ' ' * (width - r)
    print('\r[{0}] {1}/{2} processing...'.format(progress, i, total), end="")


A = [0, 1.0, 1.0, 1.0, 0.891250938, 0.707945784, 0.501187234, 0.354813389, 0.251188643, 0.199526231]
B = [0, 0, 0, -0.00459648054721, -0.0155520765675, -0.0208114779827, -0.0182211227016, -0.0122437497109, -0.00780345575475, -0.00312857467007]
C = [0, 0, 0, -0.000787968093807, -0.000307591508224, -0.000218348633296, 0.00047738416141, 0.000120353137658, 0.000323676257958, 0.000143850511]
D = [0, 0, 0, 1.60125528528e-05, 2.9747624976e-06, 2.31910931569e-05, -1.1901034125e-05, 6.77743734332e-06, -5.99548024824e-06, -4.79372835035e-06]


def directivity(theta):
    """
    third degree spline interpolation
    """

    theta = theta * 180.0 / np.pi
    theta = abs(theta)
    while theta > 90.0:
        theta = abs(180.0 - theta)

    i = int(np.ceil(theta / 10.0))

    d = 1.0
    if i != 0:
        a = A[i]
        b = B[i]
        c = C[i]
        d = D[i]
        x = theta - (i - 1) * 10.0
        d = a + b * x + c * x**2 + d * x**3

    return d


def attenuation_coef(freq, hr, ps, ps0, t):
    '''
    Bass, Henry E., et al. "Atmospheric absorption of sound: Further developments."
    The Journal of the Acoustical Society of America 97.1 (1995): 680-683.
    '''
    T0 = 293.15
    T01 = 273.16
    psat = ps0 * np.power(10.0, -6.8346 * np.power(T01 / t, 1.261) + 4.6151)
    h = ps0 * (hr / ps) * (psat / ps0)
    f_ro = (24. + 4.04e4 * h * (0.02 + h) / (0.391 + h)) / ps0
    f_rn = (1. / ps0) * np.exp(9. + 280. * h * (-4.17 * (np.power(T0 / t, 1. / 3.) - 1.))) * np.power(T0 / t, 1. / 2.)
    f = freq / ps

    alpha = (f * f) / ps0 * ps * (1.84 * np.power(t / T0, 1. / 2.) * 1e-11 + np.power(t / T0, -5. / 2.) *
                                  (0.01278 * np.exp(-2239.1 / t) / (f_ro + f * f / f_ro) + 0.1068 * np.exp(-3352. / t) / (f_rn + f * f / f_rn)))
    return alpha * 1e-3
