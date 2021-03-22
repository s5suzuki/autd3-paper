/*
 * File: Alarm.cs
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
using System.Text;

namespace frrjiflib
{
    public class Alarm
    {
        private readonly int _index;
        private readonly short _ID = 0;
        private readonly short _Number = 0;
        private readonly short _CauseID = 0;
        private readonly short _CauseNumber = 0;
        private readonly short _Severity = 0;
        private readonly short _Year = 0;
        private readonly short _Month = 0;
        private readonly short _Day = 0;
        private readonly short _Hour = 0;
        private readonly short _Minutes = 0;
        private readonly short _Seconds = 0;
        private readonly string _Message = "";
        private readonly string _CauseMessage = "";
        private readonly string _SeverityMessage = "";

        internal Alarm(DataAlarm dataAlarm, int index)
        {
            _index = index;
            IsAlert = dataAlarm.GetValue(index, ref _ID, ref _Number, ref _CauseID, ref _CauseNumber, ref _Severity, ref _Year, ref _Month, ref _Day, ref _Hour,
            ref _Minutes, ref _Seconds, ref _Message, ref _CauseMessage, ref _SeverityMessage);
        }

        public short ID { get => _ID; }
        public short Number { get => _Number; }
        public short CauseID { get => _CauseID; }
        public short CauseNumber { get => _CauseNumber; }
        public short Severity { get => _Severity; }
        public short Year { get => _Year; }
        public short Month { get => _Month; }
        public short Day { get => _Day; }
        public short Hour { get => _Hour; }
        public short Minutes { get => _Minutes; }
        public short Seconds { get => _Seconds; }
        public string Message { get => _Message; }
        public string CauseMessage { get => _CauseMessage; }
        public string SeverityMessage { get => _SeverityMessage; }
        public bool IsAlert { get; }

        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"-- Alarm {_index} --");
            if (!IsAlert)
            {
                sb.AppendLine($"Error");
                return sb.ToString();
            }

            sb.AppendLine($"{_ID}, {_Number}, {_CauseID}, {_CauseNumber}, {_Severity}");
            sb.AppendLine($"{_Year}/{_Month}/{_Day}, {_Hour}:{_Minutes}:{_Seconds}");

            if (!string.IsNullOrEmpty(_Message))
                sb.AppendLine(_Message);
            if (!string.IsNullOrEmpty(_CauseMessage))
                sb.AppendLine(_CauseMessage);
            if (!string.IsNullOrEmpty(_SeverityMessage))
                sb.AppendLine(_SeverityMessage);

            return sb.ToString();
        }
    }
}
