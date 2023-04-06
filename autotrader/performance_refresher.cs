using System;
using NinjaTrader.Cbi;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript;
using NinjaTrader.Gui;
using System.Windows.Threading;
using System.Windows;

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
                Window tradePerformanceWindow = null;

                foreach (var window in Core.Globals.AllWindows)
                {
                    if (window.Title == "Trade Performance")
                    {
                        tradePerformanceWindow = window;
                        break;
                    }
                }

                if (tradePerformanceWindow != null)
                {
                    tradePerformanceWindow.Dispatcher.Invoke(() =>
                    {
                        var generateButton = tradePerformanceWindow.FindName("generateButton") as System.Windows.Controls.Button;
                        if (generateButton != null)
                        {
                            generateButton.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                        }
                    });
                }
            }
        }
    }
}
