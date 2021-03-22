/*
 * File: Utils.cs
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

namespace shared
{
    public static class Utils
    {

        public static string CreateFolderTimeStamped(string prefix)
        {
            var date = DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss");
            var folder = prefix + date;
            Directory.CreateDirectory(folder);
            return folder;
        }

        public static IEnumerable<(T1, T2, T3)> Product<T1, T2, T3>(IEnumerable<T1> iter1, IEnumerable<T2> iter2, IEnumerable<T3> iter3)
        {
            foreach (var v3 in iter3)
                foreach (var v2 in iter2)
                    foreach (var v1 in iter1)
                        yield return (v1, v2, v3);
        }

        public static IEnumerable<(T1, T2)> Product<T1, T2>(IEnumerable<T1> iter1, IEnumerable<T2> iter2)
        {
                foreach (var v2 in iter2)
                    foreach (var v1 in iter1)
                        yield return (v1, v2);
        }
    }
}
