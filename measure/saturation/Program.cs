/*
 * File: Program.cs
 * Project: saturation
 * Created Date: 19/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 19/02/2021
 * Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
 * -----
 * Copyright (c) 2021 Hapis Lab. All rights reserved.
 * 
 */

using frrjiflib;
using shared;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;

namespace saturation
{
    class Program
    {
        static void Scan(AUTD3Cnt autd, PicoCnt pico, (float, float, float) focus, IEnumerable<int> dutyies, string dataFolder, bool compress = false)
        {
            var totalNum = dutyies.Count();

            Console.WriteLine($"Total Scan Points: {totalNum}");

            int i = 0;
            Console.WriteLine("Start Scanning...");
            foreach (int duty in dutyies)
            {
                Console.Write("{0, 3:d0}/{1, 3:d0} ({2, 3:f0}%)", i, totalNum, 100.0 * i / totalNum);
                Console.SetCursorPosition(0, Console.CursorTop);

                autd.Focus(focus.Item1, focus.Item2, focus.Item3, (byte)duty);
                Thread.Sleep(500);

                pico.MeasureAndSave(false, Path.Join(dataFolder, $"duty{duty}"), compress);

                autd.Stop();
                Thread.Sleep(60 * 1000);

                i++;
            }

            Console.WriteLine();
        }

        static void Main(string[] args)
        {
            int NUM_AUTD_X = 3;
            int NUM_AUTD_Y = 3;

            float W = 192f;
            float H = 151.4f;

            float xc = W * NUM_AUTD_X / 2f;
            float yc = H * NUM_AUTD_Y / 2f;
            float Z = 500;

            var compress = false;
            var cond = new Conditions()
            {
                SampleRateHz = 10_000_000,
                SampleLen = 10_000,
                Temp = 23.0f,
                Humidity = 21f,
                Amplifer = 1,
                X = xc,
                Y = yc,
                Z = Z
            };

            using var robo = new RobotController();
            if (!robo.Connect("172.16.99.57"))
            {
                Console.WriteLine("Failed to connect to robot.");
                return;
            }
            robo.MoveTo(xc, yc, Z);

            using var pico = new PicoCnt();
            pico.SetChannel(0, 5000, 1, null);
            pico.SetCondition(cond);

            using var autd = new AUTD3Cnt();

            for (int y = 0; y < NUM_AUTD_Y; y++)
                for (int x = 0; x < NUM_AUTD_X; x++)
                    autd.AddDevice(x * W, y * H, 0);
            var ifname = AUTD3Cnt.GetIfname();
            autd.Open(ifname);
            autd.Clear();
            autd.Calibrate();
            autd.StaticMod(0xFF);
            autd.SetWavelength(cond.Wavelength);

            var dataFolder = Utils.CreateFolderTimeStamped("saturation");
            Console.WriteLine("Connect Ch. A to microphone without cover. conditions are ...");
            cond.Check();
            cond.Save(dataFolder);
            Scan(autd, pico, (xc, yc, Z), Enumerable.Range(0, 50), dataFolder, compress);

            pico.SetChannel(0, 5000, 1, null);
            cond.Amplifer = 100;
            dataFolder = Utils.CreateFolderTimeStamped("saturation_cover");
            Console.WriteLine("Connect Ch. A to microphone with cover. conditions are ...");
            cond.Check();
            cond.Save(dataFolder);
            Scan(autd, pico, (xc, yc, Z), Enumerable.Range(0, 256), dataFolder, compress);

            Console.WriteLine("Finish.");
            autd.Stop();

            robo.Finish();
        }
    }
}
