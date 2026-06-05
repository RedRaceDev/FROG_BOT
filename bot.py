import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ.get("BOT_TOKEN")

# ==================== ПИЛОТЫ ====================
DRIVERS = {
    "verstappen": {"name": "Макс Ферстаппен", "emoji": "🔴", "team": "redbull",
                   "SPD":94,"RAC":95,"REA":96,"CNT":90,"OVT":94,"DEF":86,"WET":92,"CST":89},
    "hamilton": {"name": "Льюис Хэмилтон", "emoji": "⭐", "team": "mercedes",
                 "SPD":88,"RAC":92,"REA":94,"CNT":91,"OVT":93,"DEF":88,"WET":87,"CST":92},
    "norris": {"name": "Ландо Норрис", "emoji": "🧡", "team": "mclaren",
               "SPD":86,"RAC":88,"REA":89,"CNT":87,"OVT":86,"DEF":84,"WET":85,"CST":88},
    "leclerc": {"name": "Шарль Леклер", "emoji": "🐴", "team": "ferrari",
                "SPD":89,"RAC":90,"REA":88,"CNT":86,"OVT":87,"DEF":83,"WET":84,"CST":85},
    "sainz": {"name": "Карлос Сайнс", "emoji": "🐴", "team": "ferrari",
              "SPD":87,"RAC":88,"REA":87,"CNT":88,"OVT":85,"DEF":86,"WET":86,"CST":90},
    "russell": {"name": "Джордж Расселл", "emoji": "⭐", "team": "mercedes",
                "SPD":87,"RAC":89,"REA":88,"CNT":86,"OVT":88,"DEF":85,"WET":84,"CST":86},
    "perez": {"name": "Серхио Перес", "emoji": "🔴", "team": "redbull",
              "SPD":86,"RAC":87,"REA":85,"CNT":86,"OVT":85,"DEF":87,"WET":83,"CST":84},
    "alonso": {"name": "Фернандо Алонсо", "emoji": "🟢", "team": "aston",
               "SPD":85,"RAC":90,"REA":89,"CNT":92,"OVT":88,"DEF":91,"WET":89,"CST":91}
}

# ==================== КОМАНДЫ ====================
TEAMS = {
    "redbull": {"STR":92,"PIT":91,"OPS":93},
    "mercedes": {"STR":91,"PIT":93,"OPS":90},
    "mclaren": {"STR":88,"PIT":89,"OPS":87},
    "ferrari": {"STR":86,"PIT":85,"OPS":84},
    "aston": {"STR":85,"PIT":86,"OPS":85}
}

# ==================== БОЛИДЫ ====================
CARS = {
    "redbull": {"VMAX":94,"HND":92,"REL":91,"AERO":94},
    "mercedes": {"VMAX":92,"HND":90,"REL":93,"AERO":90},
    "mclaren": {"VMAX":88,"HND":89,"REL":90,"AERO":89},
    "ferrari": {"VMAX":90,"HND":87,"REL":86,"AERO":88},
    "aston": {"VMAX":86,"HND":88,"REL":89,"AERO":86}
}

# ==================== ТРАССЫ ====================
TRACKS = {
    "monaco": {"name": "Монако", "laps": 78, "mult_driver": {"REA":1.5,"CNT":1.4,"DEF":1.3}},
    "monza": {"name": "Монца", "laps": 53, "mult_driver": {"SPD":1.4,"OVT":1.3},"mult_car":{"VMAX":1.5}},
    "suzuka": {"name": "Сузука", "laps": 53, "mult_driver": {"CNT":1.4,"CST":1.3}}
}

# ==================== СИМУЛЯЦИЯ ====================
def simulate_race(track_id):
    track = TRACKS[track_id]
    weather = random.choice(["☀️ Сухо", "🌧️ Дождь"])
    
    results = []
    for driver_id, driver in DRIVERS.items():
        car = CARS[driver["team"]]
        team = TEAMS[driver["team"]]
        
        pace = (driver["SPD"]*0.15 + driver["RAC"]*0.15 + driver["REA"]*0.1 + 
                driver["CNT"]*0.1 + driver["OVT"]*0.08 + driver["DEF"]*0.08)
        
        for p, m in track.get("mult_driver", {}).items():
            pace += driver.get(p, 0) * (m - 1) * 0.1
        for p, m in track.get("mult_car", {}).items():
            pace += car.get(p, 0) * (m - 1) * 0.08
        
        pace += team["STR"]*0.05 + team["OPS"]*0.05
        
        if "Дождь" in weather:
            pace += driver["WET"] * 0.12
        
        pace *= random.uniform(0.95, 1.05)
        
        dnf = random.randint(0, 100) < max(0, 20 - car["REL"] * 0.2)
        
        results.append({"name": driver["name"], "emoji": driver["emoji"], "pace": pace, "dnf": dnf})
    
    results.sort(key=lambda x: (x["dnf"], -x["pace"]))
    
    msg = f"🏁 **ГРАН-ПРИ {track['name'].upper()}**\n{weather} | {track['laps']} кругов\n\n**РЕЗУЛЬТАТ:**\n"
    pos = 1
    for r in results:
        if not r["dnf"]:
            msg += f"{pos}. {r['emoji']} {r['name']}\n"
            pos += 1
    
    dnf_list = [r for r in results if r["dnf"]]
    if dnf_list:
        msg += "\n**⚠️ СХОДЫ:**\n" + "\n".join([f"• {r['emoji']} {r['name']}" for r in dnf_list])
    
    return msg

# ==================== КОМАНДЫ ====================
async def start(update, context):
    keyboard = [[InlineKeyboardButton("🏁 Монако", callback_data="monaco"),
                 InlineKeyboardButton("⚡ Монца", callback_data="monza")],
                [InlineKeyboardButton("🇯🇵 Сузука", callback_data="suzuka"),
                 InlineKeyboardButton("🎲 Случайная", callback_data="random")]]
    await update.message.reply_text("🏎️ **F1 СИМУЛЯТОР**\nВыбери трассу:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_callback(update, context):
    query = update.callback_query
    await query.answer()
    track = query.data
    if track == "random":
        track = random.choice(list(TRACKS.keys()))
    await query.edit_message_text(f"🏎️ Симуляция...")
    result = simulate_race(track)
    await query.edit_message_text(result, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏁 Новая гонка", callback_data="new")]]))

async def new_race(update, context):
    keyboard = [[InlineKeyboardButton("🏁 Монако", callback_data="monaco"),
                 InlineKeyboardButton("⚡ Монца", callback_data="monza")],
                [InlineKeyboardButton("🇯🇵 Сузука", callback_data="suzuka"),
                 InlineKeyboardButton("🎲 Случайная", callback_data="random")]]
    await update.callback_query.edit_message_text("🏎️ **Выбери трассу:**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== ЗАПУСК ====================
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_callback, pattern="^(monaco|monza|suzuka|random)$"))
app.add_handler(CallbackQueryHandler(new_race, pattern="^new$"))

print("🤖 Бот запущен!")
app.run_polling()
