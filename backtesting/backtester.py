import pandas as pd
import yfinance as yf

data = yf.download("ES=F", interval="1m", start="2023-01-13", end="2023-01-15")
data["day_of_month"] = data.index.day

print(data)

//@version=4
study("My script")
// Midnight Open Line
midnightOpen = time(0,0,0)
plot(midnightOpen == time ? midnightOpen : na, color=color.red, linewidth=2, style=plot.style_solid, title="Midnight Open")

// 8:30 AM Open Line
morningOpen = time(8,30,0)
plot(morningOpen == time ? morningOpen : na, color=color.green, linewidth=2, style=plot.style_solid, title="8:30 AM Open")

// 3:00 AM Vertical Line
verticalLine3 = time(3,0,0)
plot(verticalLine3 == time ? close : na, color=color.purple, linewidth=1, style=plot.style_dashed, title="3:00 AM")

// 9:30 AM Vertical Line
verticalLine9 = time(9,30,0)
plot(verticalLine9 == time ? close : na, color=color.purple, linewidth=1, style=plot.style_dashed, title="9:30 AM")

// 7:30 PM Vertical Line
verticalLine19 = time(19,30,0)
plot(verticalLine19 == time ? close : na, color=color.purple, linewidth=1, style=plot.style_dashed, title="7:30 PM")
