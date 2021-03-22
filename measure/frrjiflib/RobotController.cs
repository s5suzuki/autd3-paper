/*
 * File: RobotController.cs
 * Project: frrjiflib
 * Created Date: 17/02/2021
 * Author: Shun Suzuki
 * -----
 * Last Modified: 17/02/2021
 * Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
 * -----
 * Copyright (c) 2021 Hapis Lab. All rights reserved.
 * 
 */

using FRRJIf;
using System;
using System.Diagnostics;
using System.Linq;

#pragma warning disable CA1303
namespace frrjiflib
{
    public class RobotController : IDisposable
    {
        private const int ALARM_COUNT = 5;

        private Core _Core;
        private DataTable _DataTable;
        private DataCurPos _CurPosUF;
        private DataPosRegXyzwpr _PosRegXyzwpr;
        private DataNumReg _NumReg;
        private DataAlarm _Alarm;

        private int _timeOutValue = 10000;
        private bool _isFinished = true;

        public int TimeOutValue
        {
            get
            {
                if (_Core != null)
                    _timeOutValue = _Core.TimeOutValue;
                return _timeOutValue;
            }
            set
            {
                _timeOutValue = value;
                if (_Core != null)
                    _Core.TimeOutValue = _timeOutValue;
            }
        }

        public bool Connect(string hostName)
        {
            if (_Core != null)
                throw new InvalidOperationException("Already connected.");

            var timeOutvalue = _timeOutValue;
            _Core = new Core
            {
                TimeOutValue = timeOutvalue
            };
            InitDataTables();
            _isFinished = false;
            var res = _Core.Connect(hostName);

            var len = _NumReg.EndIndex - _NumReg.StartIndex + 1;
            var intValues = new int[len];
            intValues[0] = 0;
            intValues[1] = 0;
            if (!_NumReg.SetValues(_NumReg.StartIndex, intValues, len))
                throw new Exception("SetNumReg Int Error");
            RefreshDataTable();

            return res;
        }

        public bool Disconnect()
        {
            if (_Core == null || _Core.IsConnected)
                return true;

            Finish();

            var res = _Core.Disconnect();
            _Core = null;
            ClearDataTables();
            return res;
        }

        public Alarm[] CurrentAlarms(int count)
        {
            count = Math.Max(count, ALARM_COUNT);
            var alarms = new Alarm[count];
            for (int i = 0; i < alarms.Length; i++)
                alarms[i] = new Alarm(_Alarm, i);

            return alarms;
        }

        public bool ClearAlarms()
        {
            return _Core.ClearAlarm(0);
        }

        public float[] GetCurrentPos()
        {
            var config = GetConfig();
            return GetCurrentPos(config);
        }

        public float[] GetCurrentPos(Array config)
        {
            Array xyzwpr = new float[9];
            Array joint_ = new float[9];
            short UF_ = 0;
            short UT_ = 0;
            short ValidC_ = 0;
            short ValidJ_ = 0;

            RefreshDataTable();
            if (!_CurPosUF.GetValue(ref xyzwpr, ref config, ref joint_, ref UF_, ref UT_, ref ValidC_, ref ValidJ_))
                throw new Exception("Failed to_CurPos.GetValue");

            return (float[])xyzwpr;
        }

        public bool MoveTo(float x, float y, float z)
        {
            var config = GetConfig();
            return MoveTo(x, y, z, ref config);
        }

        public bool MoveTo(float x, float y, float z, ref Array config)
        {
            var curerntPos = GetCurrentPos(config);
            var diffX = x - curerntPos[0];
            var diffY = y - curerntPos[1];
            var diffZ = z - curerntPos[2];
            return Move(diffX, diffY, diffZ, ref config);
        }

        public bool Move(float x, float y, float z)
        {
            var config = GetConfig();
            return Move(x, y, z, ref config);
        }

        public bool Move(float x, float y, float z, ref Array config)
        {
            Array xyzwpr = new float[6];
            xyzwpr.SetValue(x, 0);
            xyzwpr.SetValue(y, 1);
            xyzwpr.SetValue(z, 2);
            for (var i = 3; i <= xyzwpr.GetUpperBound(0); i++)
                xyzwpr.SetValue(0f, i);

            if (!_PosRegXyzwpr.SetValueXyzwpr(1, ref xyzwpr, ref config))
                throw new Exception("Error_PosRegXyzwpr.SetValueXyzwpr");

            if (!_PosRegXyzwpr.Update())
                throw new Exception("Error_PosRegXyzwpr.Update");

            StartMoving();
            var res = WaitForMoved();
            RefreshDataTable();
            return res;
        }

        public bool RotateTo(float w, float p, float r)
        {
            var config = GetConfig();
            return RotateTo(w, p, r, ref config);
        }

        public bool RotateTo(float w, float p, float r, ref Array config)
        {
            var curerntPos = GetCurrentPos(config);
            var diffW = w - curerntPos[3];
            var diffP = p - curerntPos[4];
            var diffR = r - curerntPos[5];
            return Rotate(diffW, diffP, diffR, ref config);
        }

        public bool Rotate(float w, float p, float r)
        {
            var config = GetConfig();
            return Rotate(w, p, r, ref config);
        }

        public bool Rotate(float w, float p, float r, ref Array config)
        {
            Array xyzwpr = new float[6];
            xyzwpr.SetValue(w, 3);
            xyzwpr.SetValue(p, 4);
            xyzwpr.SetValue(r, 5);
            for (var i = 0; i < 3; i++)
                xyzwpr.SetValue(0f, i);

            if (!_PosRegXyzwpr.SetValueXyzwpr(1, ref xyzwpr, ref config))
                throw new Exception("Error_PosRegXyzwpr.SetValueXyzwpr");

            if (!_PosRegXyzwpr.Update())
                throw new Exception("Error_PosRegXyzwpr.Update");

            StartMoving();
            var res = WaitForMoved();
            RefreshDataTable();
            return res;
        }

        public void Finish()
        {
            if (_isFinished) return;
            _isFinished = true;

            var len = _NumReg.EndIndex - _NumReg.StartIndex + 1;
            var intValues = new int[len];
            intValues[0] = 0;
            intValues[1] = 1;

            if (!_NumReg.SetValues(_NumReg.StartIndex, intValues, len))
                throw new Exception("SetNumReg Int Error");

            WaitForMoved();
        }

        private Array GetConfig()
        {
            Array config = new short[7];
            Array _xyzwpr = new float[9];
            Array _joint = new float[9];
            short _UF = 0;
            short _UT = 0;
            short _validC = 0;
            short _validJ = 0;

            RefreshDataTable();
            if (!_CurPosUF.GetValue(ref _xyzwpr, ref config, ref _joint, ref _UF, ref _UT, ref _validC, ref _validJ))
                throw new Exception("Failed to_CurPos.GetValue");

            return config;
        }

        private void StartMoving()
        {
            var len = _NumReg.EndIndex - _NumReg.StartIndex + 1;
            var intValues = new int[len];
            intValues[0] = 1;

            if (!_NumReg.SetValues(_NumReg.StartIndex, intValues, len))
                throw new Exception("SetNumReg Int Error");
        }

        private bool WaitForMoved(int timeOut = 5000)
        {
            object vntValue = null;
            Alarm[] alarms;
            float[] previousPos = GetCurrentPos();
            Stopwatch sw = null;
            do
            {
                RefreshDataTable();
                _NumReg.GetValue(_NumReg.StartIndex, ref vntValue);
                alarms = CurrentAlarms(1);
                if (alarms[0].IsAlert) return false;
                var curentPos = GetCurrentPos();
                if (Enumerable.SequenceEqual(previousPos, curentPos))
                {
                    if (sw == null)
                    {
                        sw = new Stopwatch();
                        sw.Start();
                    }

                    if (sw.ElapsedMilliseconds > timeOut) return false;
                }
                else
                {
                    sw = null;
                }
            } while ((int)vntValue == 1);
            return true;
        }

        private void RefreshDataTable()
        {
            if (!_DataTable.Refresh())
                throw new Exception("Failed to refresh DataTable");
        }

        private void InitDataTables()
        {
            _DataTable = _Core.DataTable;
            {
                _CurPosUF = _DataTable.AddCurPosUF(FRIF_DATA_TYPE.CURPOS, 1, 15);
                _NumReg = _DataTable.AddNumReg(FRIF_DATA_TYPE.NUMREG_INT, 1, 2);
                _PosRegXyzwpr = _DataTable.AddPosRegXyzwpr(FRIF_DATA_TYPE.POSREG_XYZWPR, 1, 1, 1);
                _Alarm = _DataTable.AddAlarm(FRRJIf.FRIF_DATA_TYPE.ALARM_LIST, ALARM_COUNT, 0);
            }
        }

        private void ClearDataTables()
        {
            _DataTable = null;
            {
                _CurPosUF = null;
                _NumReg = null;
                _PosRegXyzwpr = null;
                _Alarm = null;
            }
        }

        #region IDisposable Support
        private bool disposedValue = false;

        protected virtual void Dispose(bool disposing)
        {
            if (!disposedValue)
            {
                if (disposing)
                {
                }

                Disconnect();

                disposedValue = true;
            }
        }

        ~RobotController()
        {
            Dispose(false);
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
        #endregion
    }
}
#pragma warning restore CA1303
