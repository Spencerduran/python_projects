using System;
using NinjaTrader.Cbi;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript;
using NinjaTrader.Gui;
using System.Windows.Threading;

namespace NinjaTrader.NinjaScript.AddOns
{
    public class AutoRefreshTradePerformance : AddOnBase
    {
        private DispatcherTimer timer;

        public AutoRefreshTradePerformance()
        {
            timer = new DispatcherTimer();
            timer.Tick += Timer_Tick;
            timer.Interval = TimeSpan.FromSeconds(10); // Set the refresh interval (e.g., 10 seconds)
            timer.Start();
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            if (Core.Globals.UserDataDir != null)
            {
                NinjaTrader.Gui.TradePerformance.TradePerformanceWindow tradePerformanceWindow = null;

                foreach (var window in Core.Globals.AllWindows)
                {
                    if (window.GetType().Name == "TradePerformanceWindow")
                    {
                        tradePerformanceWindow = window as NinjaTrader.Gui.TradePerformance.TradePerformanceWindow;
                        break;
                    }
                }

                if (tradePerformanceWindow != null)
                {
                    tradePerformanceWindow.Dispatcher.Invoke(() =>
                    {
                        tradePerformanceWindow.Generate();
                    });
                }
            }
        }
    }
}
