/*
 * File: Program.cs
 * Project: Uncompressor
 * Created Date: 17/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 18/02/2021
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

namespace Uncompressor
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

        static void UncompressFile(string path)
        {
            if (Path.GetExtension(path) != ".bin") return;

            var dir = Path.GetDirectoryName(path);
            var filename = Path.GetFileNameWithoutExtension(path);

            using (Stream stream = new FileStream(path, FileMode.Open, FileAccess.Read))
            using (var ds = new GZipStream(stream, CompressionMode.Decompress))
            {
                var formatter = new BinaryFormatter();
                var data = (string)(formatter.Deserialize(ds));

                File.WriteAllText(Path.Join(dir, filename + ".csv"), data);
            }

            File.Delete(path);
            Interlocked.Increment(ref i);
            ShowProgress(i, total, 50);
        }

        static void UncompressDirectory(string path)
        {
            foreach (var dir in Directory.EnumerateDirectories(path))
                UncompressDirectory(dir);

            Parallel.ForEach(Directory.EnumerateFiles(path), file => UncompressFile(file));
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
                    total += Directory.GetFiles(item, "*.bin", SearchOption.AllDirectories).Length;
                else
                    total++;
            }

            foreach (var item in args)
            {
                FileAttributes attr = File.GetAttributes(item);
                if ((attr & FileAttributes.Directory) == FileAttributes.Directory)
                    UncompressDirectory(item);
                else
                    UncompressFile(item);
            }
        }
    }
}
