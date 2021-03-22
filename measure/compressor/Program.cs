/*
 * File: Program.cs
 * Project: compressor
 * Created Date: 19/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 21/02/2021
 * Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
 * -----
 * Copyright (c) 2021 Hapis Lab. All rights reserved.
 * 
 */

using System;
using System.IO;
using System.IO.Compression;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace compressor
{
    class Program
    {
        static int total = 0;
        static int i = 0;

        static void ShowProgress(int i, int total, int width)
        {
            var r = (int)(((double)i * width) / total);
            var sb = new StringBuilder();
            var bar = sb.Insert(0, "#", r).Insert(r, " ", width - r).ToString();
            Console.Write($"\r[{bar}] {i}/{total} processing...");
        }

        static void CompressFile(string path)
        {
            if (Path.GetExtension(path) != ".csv") return;

            var dir = Path.GetDirectoryName(path);
            var filename = Path.GetFileNameWithoutExtension(path);

            using (Stream stream = new FileStream(Path.Join(dir, filename + ".bin"), FileMode.Create, FileAccess.Write))
            using (var gzs = new GZipStream(stream, CompressionMode.Compress, true))
            {
                var f = File.ReadAllText(path);
                var formatter = new BinaryFormatter();
                formatter.Serialize(gzs, f);
            }

            File.Delete(path);
            Interlocked.Increment(ref i);
            ShowProgress(i, total, 50);
        }

        static void CompressDirectory(string path)
        {
            foreach (var dir in Directory.EnumerateDirectories(path))
                CompressDirectory(dir);

            Parallel.ForEach(Directory.EnumerateFiles(path), file => CompressFile(file));
        }

        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.Write("Input path of data file or directory including data files: ");
                var dir = Console.ReadLine();
                args = new[] { dir };
            }

            foreach (var item in args)
            {
                FileAttributes attr = File.GetAttributes(item);
                if ((attr & FileAttributes.Directory) == FileAttributes.Directory)
                    total += Directory.GetFiles(item, "*.csv", SearchOption.AllDirectories).Length;
                else
                    total++;
            }

            foreach (var item in args)
            {
                FileAttributes attr = File.GetAttributes(item);
                if ((attr & FileAttributes.Directory) == FileAttributes.Directory)
                    CompressDirectory(item);
                else
                    CompressFile(item);
            }
        }
    }
}
