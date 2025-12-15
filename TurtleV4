#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion
#region Using declarations
using System;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;
#endregion

// UncleLarry — Session Structure Breakout (FX-optimized sizing)
// • Sessions (ET): Asia 20:00–22:00, London 03:00–05:00, New York 09:30–11:30
// • Entry: close > prior high (long) / close < prior low (short)
// • SL: prior candle low/high   • TP: 1:1
// • Risk: $500 target per trade, $550 hard cap (skip if 1 contract > $550)
// • Daily guardrails: max 3 trades/day, halt if dailyPnL >= +1500 or <= -1000,
//   and halt for the rest of day if after a positive day the next trade is a loss.
// • Prop-safe cap: default 6 contracts (micros)

namespace NinjaTrader.NinjaScript.Strategies
{
    public class UncleLarry : Strategy
    {
        // --- Risk settings ---
        private const double RiskTarget  = 500.0;  // desired per-trade risk
        private const double RiskHardCap = 550.0;  // total trade risk must not exceed this

        // --- Daily controls ---
        private int      tradesToday        = 0;
        private DateTime lastTradeDate      = Core.Globals.MinDate;
        private double   dailyPnL           = 0.0;
        private double   dailyLossLimit     = -1000.0;
        private double   dailyProfitTarget  = 1500.0;
        private bool     dayHalted          = false;

        // --- Instrument meta ---
        private double tickValue = 1.25; // $/tick (mapped per instrument)
        private double tickSize  = 1.0;  // price per tick (from instrument)
        private int    maxContracts = 6; // prop-safe cap for micros

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name                = "UncleLarry";
                Calculate           = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling       = EntryHandling.AllEntries;
                IsOverlay           = true;
                IncludeCommission   = true;
            }
            else if (State == State.Configure)
            {
                tickSize  = Math.Max(TickSize, 0.0000001);
                tickValue = MapTickValue(Instrument?.MasterInstrument?.Name ?? "");
                maxContracts = 6; // adjust if you ever need to
            }
        }

        // Map common contracts to correct $/tick. Fallback uses PointValue*TickSize.
        private double MapTickValue(string name)
        {
            name = (name ?? "").ToUpper();

            // Currencies
            if (name.StartsWith("M6E")) return 0.625; // Micro EUR/USD
            if (name.StartsWith("6E"))  return 6.25;  // EUR/USD
            if (name.StartsWith("M6B")) return 0.625; // Micro GBP/USD
            if (name.StartsWith("6B"))  return 6.25;  // GBP/USD

            // Others you sometimes run
            if (name.StartsWith("MNQ")) return 0.50;
            if (name.StartsWith("MES")) return 1.25;
            if (name.StartsWith("MGC")) return 1.00;

            // Fallback
            double pv = Instrument?.MasterInstrument?.PointValue ?? 1.0;
            return pv * Math.Max(TickSize, 0.0000001);
        }

        // $ risk per contract for a given stop distance (price units)
        private double DollarRiskPerContract(double stopDistance)
        {
            double stopTicks = Math.Ceiling(Math.Abs(stopDistance) / tickSize);
            if (stopTicks < 1) stopTicks = 1;
            return stopTicks * tickValue;
        }

        // Determine contract qty under target and hard cap, then apply a prop-safe cap
        private int ContractsForRisk(double stopDistance)
        {
            double perContract = DollarRiskPerContract(stopDistance);
            if (perContract <= 0) return 0;
            if (perContract > RiskHardCap) return 0; // one contract already too risky

            int qty = (int)Math.Floor(RiskTarget / perContract);
            if (qty < 1) qty = 1;

            // keep total trade risk under hard cap
            while (qty > 1 && qty * perContract > RiskHardCap)
                qty--;

            // prop-safe limit
            if (qty > maxContracts) qty = maxContracts;

            return qty;
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 20) return;

            // New day reset
            if (Times[0][0].Date != lastTradeDate.Date)
            {
                tradesToday   = 0;
                dailyPnL      = 0;
                dayHalted     = false;
                lastTradeDate = Times[0][0].Date;
            }

            if (dayHalted) return;

            // Daily guardrails
            if (tradesToday >= 3 || dailyPnL <= dailyLossLimit || dailyPnL >= dailyProfitTarget)
                return;

            // Session filters (ET)
            DateTime et = Times[0][0].ToLocalTime();
            int h = et.Hour, m = et.Minute;

            bool inAsian  = (h == 20 || h == 21);
            bool inLondon = (h == 3  || h == 4);
            bool inNY     = ((h == 9 && m >= 30) || h == 10 || (h == 11 && m < 30));
            if (!(inAsian || inLondon || inNY))
                return;

            // Entry signals (structure/momentum breakout)
            bool longSignal  = Close[0] > Open[0] && Close[0] > High[1];
            bool shortSignal = Close[0] < Open[0] && Close[0] < Low[1];

            // Long
            if (longSignal && Position.MarketPosition == MarketPosition.Flat)
            {
                double stopPrice    = Low[1];
                double stopDistance = Close[0] - stopPrice;
                if (stopDistance <= 0) return;

                int qty = ContractsForRisk(stopDistance);
                if (qty < 1) return;

                double targetPrice = Close[0] + stopDistance; // 1:1

                SetStopLoss    ("LongEntry",  CalculationMode.Price, stopPrice,   false);
                SetProfitTarget("LongEntry",  CalculationMode.Price, targetPrice);
                EnterLong(qty, "LongEntry");
                tradesToday++;
            }

            // Short
            if (shortSignal && Position.MarketPosition == MarketPosition.Flat)
            {
                double stopPrice    = High[1];
                double stopDistance = stopPrice - Close[0];
                if (stopDistance <= 0) return;

                int qty = ContractsForRisk(stopDistance);
                if (qty < 1) return;

                double targetPrice = Close[0] - stopDistance; // 1:1

                SetStopLoss    ("ShortEntry", CalculationMode.Price, stopPrice,   false);
                SetProfitTarget("ShortEntry", CalculationMode.Price, targetPrice);
                EnterShort(qty, "ShortEntry");
                tradesToday++;
            }
        }

        protected override void OnExecutionUpdate(Execution exec, string id, double price, int qty,
                                                  MarketPosition pos, string orderId, DateTime time)
        {
            if (exec?.Order == null || exec.Order.OrderState != OrderState.Filled)
                return;

            // Recompute today's realized PnL
            dailyPnL = 0;
            foreach (var t in SystemPerformance.AllTrades)
                if (t.Exit != null && t.Exit.Time.Date == Time[0].Date)
                    dailyPnL += t.ProfitCurrency;

            // Halt rule: if we were positive on the day and the last trade lost → stop for day
            if (Position.MarketPosition == MarketPosition.Flat)
            {
                bool wasLoss = false;
                int c = SystemPerformance.AllTrades.Count;
                if (c > 0)
                {
                    var last = SystemPerformance.AllTrades[c - 1];
                    if (last?.Exit != null && last.Exit.Time.Date == Time[0].Date)
                        wasLoss = last.ProfitCurrency < 0;
                }
                if (wasLoss && dailyPnL > 0)
                    dayHalted = true;
            }

            // Hard daily stops
            if (dailyPnL >= dailyProfitTarget || dailyPnL <= dailyLossLimit)
                ExitAllPositions();
        }

        private void ExitAllPositions()
        {
            if (Position.MarketPosition == MarketPosition.Long)
                ExitLong("DailyCloseLong", "LongEntry");
            else if (Position.MarketPosition == MarketPosition.Short)
                ExitShort("DailyCloseShort", "ShortEntry");
        }
    }
}
