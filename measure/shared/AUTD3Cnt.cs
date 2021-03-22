/*
 * File: AUTD3Cnt.cs
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

using AUTD3Sharp;
using System;
using System.Collections.Generic;
using System.Linq;

namespace shared
{
    public class AUTD3Cnt : IDisposable
    {
        AUTD _autd;
        private bool disposedValue;

        public AUTD3Cnt()
        {
            _autd = new AUTD();
        }

        public static string GetIfname()
        {
            IEnumerable<EtherCATAdapter> adapters = AUTD.EnumerateAdapters();
            foreach ((EtherCATAdapter adapter, int index) in adapters.Select((adapter, index) => (adapter, index)))
            {
                Console.WriteLine($"[{index}]: {adapter}");
            }

            Console.Write("Choose number: ");
            int i;
            while (!int.TryParse(Console.ReadLine(), out i)) { }
            return adapters.ElementAt(i).Name;
        }
        public void AddDevice(float x, float y, float z)
        {
            _autd.AddDevice(new Vector3f(x, y, z), Vector3f.Zero);
        }

        public void Open(string ifname)
        {
            var link = AUTD.SOEMLink(ifname, _autd.NumDevices);
            _autd.OpenWith(link);
        }

        public void StaticMod(byte duty = 0xff)
        {
            _autd.AppendModulationSync(AUTD.Modulation(duty));
        }

        public void Focus(float x, float y, float z, byte duty = 0xff)
        {
            _autd.AppendGainSync(AUTD.FocalPointGain(new Vector3f(x, y, z), duty));
        }

        public void TransTest(int idx, byte duty, byte phase)
        {
            _autd.AppendGainSync(AUTD.TransducerTestGain(idx, duty, phase));
        }

        public void SetWavelength(float wavelen)
        {
            _autd.Wavelength = wavelen;
        }

        public void Clear()
        {
            _autd.Clear();
        }

        public void Calibrate()
        {
            _autd.Calibrate();
        }

        public void Stop()
        {
            _autd.Stop();
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!disposedValue)
            {
                if (disposing)
                {
                    _autd.Dispose();
                }

                disposedValue = true;
            }
        }

        public void Dispose()
        {
            Dispose(disposing: true);
            GC.SuppressFinalize(this);
        }
    }
}
