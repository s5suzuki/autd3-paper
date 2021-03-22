/*
 * File: Program.cs
 * Project: single_trans_phase_duty
 * Created Date: 17/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 17/02/2021
 * Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
 * -----
 * Copyright (c) 2021 Hapis Lab. All rights reserved.
 * 
 */

using frrjiflib;
using shared;
using System;
using System.IO;
using System.Threading;

namespace single_trans_phase_duty
{
    class Program
    {
        static void Scan(AUTD3Cnt autd, PicoCnt pico, Conditions cond, string prefix, bool trig, Action<AUTD3Cnt, int> func, bool compress = false)
        {
            var dataFolder = Utils.CreateFolderTimeStamped(prefix);
            cond.Save(dataFolder);

            for (int i = 0; i <= byte.MaxValue; i++)
            {
                Console.Write("{0}: {1, 3:d0}/{2, 3:d0} ({3, 3:f0}%)", prefix, i, byte.MaxValue, 100.0 * i / byte.MaxValue);
                Console.SetCursorPosition(0, Console.CursorTop);

                func(autd, i);
                Thread.Sleep(500);

                pico.MeasureAndSave(trig, Path.Join(dataFolder, $"{prefix}{i}"), compress);

                autd.TransTest(0, 0, 0);
                Thread.Sleep(60 * 1000);
            }
            Console.WriteLine();
            autd.Stop();
        }

        static void Main(string[] args)
        {
            using var robo = new RobotController();
            if (!robo.Connect("172.16.99.57"))
            {
                Console.WriteLine("Failed to connect to robot.");
                return;
            }
            robo.MoveTo(0, 0, 200);

            using var pico = new PicoCnt();

            using var autd = new AUTD3Cnt();
            autd.AddDevice(0, 0, 0);

            var ifname = AUTD3Cnt.GetIfname();
            autd.Open(ifname);
            autd.Clear();
            autd.Calibrate();
            autd.StaticMod(0xFF);

            var compress = false;
            var cond = new Conditions()
            {
                SampleRateHz = 2_000_000,
                SampleLen = 2_000,
                Temp = 23.0f,
                Humidity = 19f,
                Amplifer = 10,
                X = 0,
                Y = 0,
                Z = 200
            };

            pico.SetChannel(0, 500, 1, null);
            pico.SetCondition(cond);
            Console.WriteLine("Connect Ch. A to microphone. conditions are ...");
            cond.Check();
            Scan(autd, pico, cond, "amp", false, (autd, i) => autd.TransTest(0, (byte)i, 0), compress);

            cond.SampleRateHz = 10_000_000;
            cond.SampleLen = 20000;

            pico.SetChannel(0, 50000, 10, null);
            pico.SetCondition(cond);
            Console.WriteLine("Connect Ch. A to microphone. conditions are ...");
            cond.Check();
            Scan(autd, pico, cond, "input", false, (autd, i) => autd.TransTest(0, (byte)i, 0), compress);

            pico.SetChannel(0, 500, 1, null);
            pico.SetChannel(1, 5000, 10, 1000);
            pico.SetCondition(cond);
            Console.WriteLine("Connect Ch. A to microphone and Ch. B to 40kHz reference signal. conditions are ...");
            cond.Check();
            Scan(autd, pico, cond, "phase", true, (autd, i) => autd.TransTest(0, 0xFF, (byte)i), compress);

            Console.WriteLine("Finish.");

            robo.Finish();
        }
    }
}
