/*
 * File: Program.cs
 * Project: xy_field
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
using System.Linq;
using System.Threading;

namespace xy_field
{
    class Program
    {
        static int ScanNum((float, float) range, float resolution) => (int)Math.Floor((range.Item2 - range.Item1) / resolution) + 1;

        static float[] ScanPoints((float, float) range, float resolution)
        {
            var n = ScanNum(range, resolution);
            return Enumerable.Range(0, n).Select(i => range.Item1 + i * resolution).ToArray();
        }

        static void ShowScanPoints(float[] points)
        {
            if (points.Length == 0)
                Console.Write("N/A");
            else if (points.Length < 4)
                Console.Write(string.Join(',', points));
            else
                Console.Write($"{points[0]}, {points[1]}, ..., {points.Last()}");
            Console.WriteLine($" ({points.Length})");
        }

        static void Scan(PicoCnt pico, RobotController robo, Conditions cond, (float, float) xrange, (float, float) yrange, (float, float) zrange, float resolution, bool compress = false)
        {
            var scanX = ScanPoints(xrange, resolution);
            var scanY = ScanPoints(yrange, resolution);
            var scanZ = ScanPoints(zrange, resolution);
            var totalNum = scanX.Length * scanY.Length * scanZ.Length;

            var dataFolder = Utils.CreateFolderTimeStamped("xy");

            Console.WriteLine($"Scan range:");
            Console.Write($"\tx: ");
            ShowScanPoints(scanX);
            Console.Write($"\ty: ");
            ShowScanPoints(scanY);
            Console.Write($"\tz: ");
            ShowScanPoints(scanZ);
            Console.WriteLine($"Total Scan Points: {totalNum}");
            Console.WriteLine($"Saved to {dataFolder}");
            Console.WriteLine("Connect Ch. A to microphone. conditions are ...");
            cond.Check();
            cond.Save(dataFolder);

            int i = 0;
            Console.WriteLine("Start Scanning...");
            foreach (var (x, y, z) in Utils.Product(scanX, scanY, scanZ))
            {
                Console.Write("{0, 3:d0}/{1, 3:d0} ({2, 3:f0}%)", i, totalNum, 100.0 * i / totalNum);
                Console.SetCursorPosition(0, Console.CursorTop);

                robo.MoveTo(x, y, z);
                Thread.Sleep(500);

                pico.MeasureAndSave(false, Path.Join(dataFolder, $"x{x:F3}y{y:F3}z{z:F3}"), compress);
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

            float R = 100f;
            float r = 1f;

            var compress = true;
            var cond = new Conditions()
            {
                SampleRateHz = 10_000_000,
                SampleLen = 10_000,
                Temp = 22.7f,
                Humidity = 13f,
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
            pico.SetChannel(0, 2000, 1, null);
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
            autd.Focus(xc, yc, Z, 10);

            Scan(pico, robo, cond, (xc - R / 2, xc + R / 2), (yc - R / 2, yc + R / 2), (Z, Z), r, compress);

            Console.WriteLine("Finish.");
            autd.Stop();
            robo.Finish();
        }
    }
}
