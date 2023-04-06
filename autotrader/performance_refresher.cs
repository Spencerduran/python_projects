using System;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript;
using NinjaTrader.Gui;

namespace NinjaTrader.NinjaScript.AddOns
{
    public class AutoRefreshTradePerformance : AddOnBase
    {
        private System.Windows.Forms.Timer timer;

        public AutoRefreshTradePerformance()
        {
            timer = new System.Windows.Forms.Timer();
            timer.Tick += Timer_Tick;
            timer.Interval = 10000; // Set the refresh interval in milliseconds (e.g., 10000 = 10 seconds)
            timer.Start();
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            if (Core.Globals.UserDataDir != null)
            {
                NinjaTrader.NinjaScript.AddOns.Performance.PerformanceViewModel viewModel = null;

                foreach (var window in Core.Globals.AllWindows)
                {
                    if (window.GetType().Name == "TradePerformanceWindow")
                    {
                        var tradePerformanceWindow = window as NinjaTrader.Gui.TradePerformance.TradePerformanceWindow;
                        viewModel = (NinjaTrader.NinjaScript.AddOns.Performance.PerformanceViewModel)tradePerformanceWindow.DataContext;
                        break;
                    }
                }

                if (viewModel != null)
                {
                    viewModel.Generate();
                }
            }
        }
    }
}
