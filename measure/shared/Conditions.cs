/*
 * File: Conditions.cs
 * Project: shared
 * Created Date: 17/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 17/02/2021
 * Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
 * -----
 * Copyright (c) 2021 Hapis Lab. All rights reserved.
 * 
 */

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace shared
{
    public class Conditions
    {
        public int SampleRateHz { get; set; }
        public int SampleLen { get; set; }
        public float Amplifer { get; set; }
        public float Temp { get; set; }
        public float Humidity { get; set; }
        public float Wavelength => CalcWavelen();
        public float X { get; set; }
        public float Y { get; set; }
        public float Z { get; set; }

        public float CalcWavelen()
        {
            var k = 1.403f;
            var M = 28.966e-3f; // kg/mol
            var R = 8.314462f;
            var T = 273.15f + Temp; // K
            var c = MathF.Sqrt(k * R * T / M); // m/s
            var f = 40; // kHz
            return c / f; // mm 
        }

        public void Check()
        {
            Console.WriteLine($"Sample Rate [Hz]: {SampleRateHz}");
            Console.WriteLine($"Sample Length [-]: {SampleLen}");
            Console.WriteLine($"Amplifer [mV/Pa]: {Amplifer}");
            Console.WriteLine($"Temp [℃]: {Temp}");
            Console.WriteLine($"Humidity [%]: {Humidity}");
            Console.WriteLine($"Wavelength [mm]: {Wavelength}");
            Console.WriteLine($"Center [mm]: {X}, {Y}, {Z}");
            Console.Write("OK?");
            Console.ReadLine();
        }

        public void Save(string dir)
        {
            using var sw = new StreamWriter(Path.Join(dir, "cond.txt"));
            sw.WriteLine($"Sample Rate [Hz], {SampleRateHz}");
            sw.WriteLine($"Sample Length, {SampleLen}");
            sw.WriteLine($"Amplifier [mV/Pa], {Amplifer}");
            sw.WriteLine($"Temp. [℃], {Temp}");
            sw.WriteLine($"Humidity [%], {Humidity}");
            sw.WriteLine($"Wavelength [mm], {Wavelength}");
            sw.WriteLine($"X [mm], {X}");
            sw.WriteLine($"Y [mm], {Y}");
            sw.WriteLine($"Z [mm], {Z}");
        }
    }
}
