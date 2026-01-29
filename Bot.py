# bot.py
import os
import sys
import random
import asyncio
import logging
import json
from datetime import datetime

import discord
from discord.ext import commands, tasks
from openai import AsyncOpenAI
import aiosqlite
from aiohttp import web

# ===================== LOGGING =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sebastian_bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger("sebastian_bot")

# ===================== CONFIG =====================
class Config:
    OBEDIENCE_DECAY = 0.05
    SOUL_GAIN = 0.03
    JEALOUSY_DECAY = 0.03
    BOND_REWARD = 0.5
    OBEDIENCE_REWARD = 0.3
    QUEST_STEPS = 3
    STORY_EVENT_INTERVAL_MINUTES = 45
    MESSAGE_HISTORY_LIMIT = 6
    CHAT_TIMEOUT = 30
    IMAGE_TIMEOUT = 60
    COMMAND_COOLDOWN_SECONDS = 10
    LONG_MEMORY_LIMIT = 20

MOOD_COLORS = {
    "calm": 0x808080,
    "protective": 0x800080,
    "wrathful": 0xFF0000,
    "mischievous": 0x006400
}

# ===================== ENV VARIABLES =====================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

# ===================== PRE-CHECKS =====================
def precheck_env():
    missing = []
    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
    logger.info("Environment variables check passed")

# ===================== HTTP SERVER =====================
async def handle_health(request):
    if bot.is_ready():
        return web.Response(text="Sebastian Bot Running - Healthy", status=200)
    else:
        return web.Response(text="Sebastian Bot Starting...", status=503)

async def start_http_server():
    app = web.Application()
    app.add_routes([web.get("/", handle_health)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"HTTP server running on port {PORT}")

# ===================== BOT =====================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
DB_FILE = "sebastian.db"
SYSTEM_PROMPT = "You are Sebastian Michaelis from Black Butler. Elegant, aristocratic, subtly cruel. Remain in character."
user_cooldowns = {}
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ===================== DATABASE =====================
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            server_id TEXT,
            user_id TEXT,
            contract INTEGER DEFAULT 0,
            married INTEGER DEFAULT 0,
            obedience REAL DEFAULT 0,
            bond REAL DEFAULT 0,
            punishments INTEGER DEFAULT 0,
            rewards INTEGER DEFAULT 0,
            jealousy REAL DEFAULT 0,
            soul REAL DEFAULT 0,
            corruption REAL DEFAULT 0,
            mood TEXT DEFAULT 'calm',
            ending TEXT,
            true_demon INTEGER DEFAULT 0,
            story_progress INTEGER DEFAULT 0,
            current_quest TEXT,
            quest_stage INTEGER DEFAULT 0,
            current_step_text TEXT,
            current_step_image_url TEXT,
            last_seen TEXT,
            memory TEXT DEFAULT '[]',
            PRIMARY KEY(server_id, user_id)
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            user_id TEXT,
            content TEXT,
            timestamp TEXT
        )
        """)
        await db.commit()
    logger.info("Database initialized")

# ===================== MAIN =====================
async def main():
    precheck_env()
    await init_db()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
