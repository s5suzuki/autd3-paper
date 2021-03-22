/*
 * File: PicoCnt.cs
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

using PS4000Lib;
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;

namespace shared
{
    public class PicoCnt : IDisposable
    {
        PS4000 _pico;
        private bool disposedValue;

        public PicoCnt()
        {
            _pico = new PS4000();
            _pico.Open();

            _pico.ChannelA.Enabled = false;
            _pico.ChannelB.Enabled = false;

            BlockData.Delimiter = ",";
            BlockData.ShowADC = false;
        }

        public void SetCondition(Conditions cond)
        {

            _pico.SamplingRateHz = cond.SampleRateHz;
            _pico.BufferSize = cond.SampleLen;
        }

        static PS4000Lib.Range GetRange(int rangeMV)
        {
            return rangeMV switch
            {
                50 => PS4000Lib.Range.Range_50MV,
                200 => PS4000Lib.Range.Range_200MV,
                500 => PS4000Lib.Range.Range_500MV,
                1000 => PS4000Lib.Range.Range_1V,
                2000 => PS4000Lib.Range.Range_2V,
                5000 => PS4000Lib.Range.Range_5V,
                50000 => PS4000Lib.Range.Range_50V,
                _ => throw new Exception("Not suppoerted"),
            };
        }

        public void MeasureAndSave(bool triggered, string path, bool compress)
        {
            BlockData blockdata = triggered ? _pico.CollectBlockTriggered() : _pico.CollectBlockImmediate();
            if (compress)
            {
                using Stream stream = new FileStream(path + ".bin", FileMode.Create, FileAccess.Write);
                using var gzs = new GZipStream(stream, CompressionMode.Compress, true);
                var formatter = new BinaryFormatter();
                formatter.Serialize(gzs, blockdata.ToString());
            }
            else
            {
                File.WriteAllText(path + ".csv", blockdata.ToString());
            }
        }

        public void SetChannel(int ch, int rangeMV, int attenuation, short? triggerMV)
        {
            var channel = ch switch
            {
                0 => _pico.ChannelA,
                1 => _pico.ChannelB,
                _ => throw new Exception("Error"),
            };
            channel.Enabled = true;
            channel.Range = GetRange(rangeMV);
            channel.Attenuation = attenuation;

            if (triggerMV.HasValue)
            {
                channel.TriggerVoltageMV = triggerMV.Value;
                channel.TriggerMode = ThresholdMode.Level;
                channel.TriggerDirection = ThresholdDirection.Rising;
                var cnd = ch switch
                {
                    0 => new TriggerConditions
                    {
                        ChannelA = TriggerState.True,
                    },
                    1 => new TriggerConditions
                    {
                        ChannelB = TriggerState.True,
                    },
                    _ => throw new Exception("Error"),
                };
                _pico.AddTriggerConditions(cnd);
            }
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!disposedValue)
            {
                if (disposing)
                {
                    _pico.Dispose();
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
