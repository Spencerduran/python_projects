using System;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript;

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

                foreach (Tab tab in MainWindow.Tabs)
                {
                    if (tab.Content.GetType().Name == "TradePerformance")
                    {
                        viewModel = (NinjaTrader.NinjaScript.AddOns.Performance.PerformanceViewModel)tab.DataContext;
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
