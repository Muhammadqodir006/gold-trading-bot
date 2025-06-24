# gold-trading-bot
# main.py
import asyncio
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta
import numpy as np
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import nest_asyncio

nest_asyncio.apply()

BOT_TOKEN = "BOT_TOKEN_YERGA_YOZING"
CHAT_ID = CHAT_ID_YERGA_YOZING  # raqam bo'lishi kerak, qo‘shtirnoqsiz

bot = Bot(token=BOT_TOKEN)

def get_signal():
    df = yf.download("GC=F", interval="15m", period="1d", progress=False)
    df.dropna(inplace=True)

    df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
    df["MACD"] = ta.trend.macd(df["Close"])
    df["MACD_signal"] = ta.trend.macd_signal(df["Close"])
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["Vol_Delta"] = df["Volume"].diff()

    bins = np.histogram(df["Close"], bins=10, weights=df["Volume"])[0]
    labels = np.histogram(df["Close"], bins=10)[1]

    price = float(df["Close"].iloc[-1])
    ema20 = float(df["EMA20"].iloc[-1])
    ema50 = float(df["EMA50"].iloc[-1])
    macd = float(df["MACD"].iloc[-1])
    signal = float(df["MACD_signal"].iloc[-1])
    rsi = float(df["RSI"].iloc[-1])
    vol = float(df["Volume"].iloc[-1])
    delta = float(df["Vol_Delta"].iloc[-1])

    msg = f"""📊 OLTIN TAHLILI:
Narx: {price:.2f} USD
RSI: {rsi:.2f}
MACD: {macd:.2f} | Signal: {signal:.2f}
Volume: {vol:.0f} | Delta: {delta:.0f}
"""

    take_profit = None
    if rsi < 30 and macd > signal and ema20 > ema50 and delta > 0:
        take_profit = price * 1.0065
        msg += f"🟢 Signal: SOTIB OLISH\n🎯 Take Profit: {take_profit:.2f} USD"
    elif rsi > 70 and macd < signal and ema20 < ema50 and delta < 0:
        take_profit = price * 0.9935
        msg += f"🔴 Signal: SOTISH\n🎯 Take Profit: {take_profit:.2f} USD"
    else:
        return None, None

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Close"], label="Narx", linewidth=2)
    ax.plot(df["EMA20"], label="EMA20", linestyle="--")
    ax.plot(df["EMA50"], label="EMA50", linestyle="--")
    ax.set_title("XAU/USD 15m")
    ax.grid()
    ax.legend()

    max_volume_index = np.argmax(bins)
    ax.axhline(labels[max_volume_index], color="gray", linestyle=":", label="VP max volume")
    plt.tight_layout()
    plt.savefig("gold_chart.png")
    plt.close()

    return msg, "gold_chart.png"

async def send_auto():
    msg, chart = get_signal()
    if msg:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        await bot.send_photo(chat_id=CHAT_ID, photo=open(chart, "rb"))

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_auto, "interval", minutes=15)
    scheduler.start()
    print("Bot ishga tushdi...")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
