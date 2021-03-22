/*
 * File: Program.cs
 * Project: trans_individual_diff
 * Created Date: 19/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 21/02/2021
 * Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
 * -----
 * Copyright (c) 2021 Hapis Lab. All rights reserved.
 * 
 */

using frrjiflib;
using shared;
using System;
using System.IO;
using System.Linq;
using System.Threading;

namespace trans_individual_diff
{
    class Program
    {
        static bool IsMissing(int tx, int ty)
        {
            return (ty == 1) && ((tx == 1) || (tx == 2) || (tx == 16));
        }

        static void Scan(AUTD3Cnt autd, byte duty, PicoCnt pico, RobotController robo, Conditions cond, int devNumX, int devNumY, float z, bool compress = false)
        {
            var totalNum = devNumX * devNumY * 249;

            var dataFolder = Utils.CreateFolderTimeStamped("individual");

            Console.WriteLine($"Total Scan Points: {totalNum}");
            Console.WriteLine($"Saved to {dataFolder}");
            Console.WriteLine("Connect Ch. A to microphone. conditions are ...");
            cond.Check();
            cond.Save(dataFolder);

            Console.WriteLine("Start Scanning...");
            var transX = Enumerable.Range(0, 18);
            var transY = Enumerable.Range(0, 14);

            var devX = Enumerable.Range(0, devNumX).Select(x => x * 192f);
            var devY = Enumerable.Range(0, devNumY).Select(y => y * 151.4f);

            int devIdx = 0;
            int idx = 0;
            foreach (var (dx, dy) in Utils.Product(devX, devY))
            {
                var df = Path.Join(dataFolder, $"dev{devIdx}");
                Directory.CreateDirectory(df);

                foreach (var (tx, ty) in Utils.Product(transX, transY))
                {
                    if (IsMissing(tx, ty)) continue;

                    autd.TransTest(idx, duty, 0);
                    Thread.Sleep(500);

                    var tf = Path.Join(df, $"tr{idx % 249}");
                    Directory.CreateDirectory(tf);

                    float x = dx + tx * 10.16f;
                    float y = dy + ty * 10.16f;

                    Console.Write("\r{0, 3:d0}/{1, 3:d0} ({2, 3:f0}%)", idx, totalNum, 100.0 * idx / totalNum);

                    robo.MoveTo(x, y, z);
                    Thread.Sleep(500);

                    pico.MeasureAndSave(true, Path.Join(tf, $"x{(tx * 10.16f):F3}y{(ty * 10.16f):F3}z{z:F3}"), compress);

                    autd.TransTest(idx, 0, 0);
                    idx++;
                }
                devIdx++;
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
            float Z = 200;

            var compress = true;
            var cond = new Conditions()
            {
                SampleRateHz = 10_000_000,
                SampleLen = 10_000,
                Temp = 22.8f,
                Humidity = 13f,
                Amplifer = 10,
                X = 0,
                Y = 0,
                Z = Z
            };

            using var robo = new RobotController();
            if (!robo.Connect("172.16.99.57"))
            {
                Console.WriteLine("Failed to connect to robot.");
                return;
            }
            robo.MoveTo(0, 0, Z);

            using var pico = new PicoCnt();
            pico.SetChannel(0, 50, 1, null);
            pico.SetChannel(1, 5000, 10, 1000);
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

            Scan(autd, 10, pico, robo, cond, NUM_AUTD_X, NUM_AUTD_Y, Z, compress);

            Console.WriteLine("Finish.");
            autd.Stop();
            robo.Finish();
        }
    }
}
