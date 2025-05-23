import os
import discord
from discord.ext import commands, tasks
import instaloader
import asyncio
import pickle 
from dotenv import load_dotenv  # ← 추가

# 🔐 .env 파일 로딩
load_dotenv()

# 🔧 설정값 환경 변수로부터 불러오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 아이브 멤버 계정들
members = {
    "장원영": "for_everyoung10",
    "안유진": "_yujin_an",
    "가을": "fallingin_fall",
    "리즈": "liz.yeyo",
    "이서": "eeseooes",
    "레이": "reinyourheart",
    "아이브(공식)": "ivestarship"
}

last_posts = {}

# 📥 세션 로딩
def load_session():
    loader = instaloader.Instaloader()
    with open(f"{INSTAGRAM_USERNAME}.session", "rb") as f:
        cookies = pickle.load(f)
    loader.context._session.cookies = cookies
    return loader

# 📸 최신 게시물 가져오기
async def get_latest_post(username):
    loader = load_session()
    await asyncio.sleep(10)  # 요청 간 간격

    profile = instaloader.Profile.from_username(loader.context, username)
    post = next(profile.get_posts())

    image_urls = []
    if post.typename == "GraphSidecar":
        for node in post.get_sidecar_nodes():
            image_urls.append(node.display_url)
    else:
        image_urls.append(post.url)

    return {
        "shortcode": post.shortcode,
        "url": f"https://www.instagram.com/p/{post.shortcode}/",
        "caption": post.caption or "(캡션 없음)",
        "images": image_urls
    }

# ⏱ 루프: 1시간마다 인스타 체크
@tasks.loop(hours=1)
async def check_instagram():
    channel = bot.get_channel(CHANNEL_ID)

    for name, username in members.items():
        try:
            data = await get_latest_post(username)
            code = data['shortcode']

            if last_posts.get(username) != code:
                last_posts[username] = code

                # ✨ Embed 메시지 구성
                embed = discord.Embed(
                    title=f"{name}의 새 인스타그램 게시물 📸",
                    description="🎀🖤✨💅",
                    url=data['url'],
                    color=0xff77aa
                )
                embed.set_image(url=data['images'][0])
                embed.set_footer(text=f"@{username} | Instagram")

                await channel.send(embed=embed)

        except Exception as e:
            print(f"[에러] {name}({username}) 처리 중 문제 발생: {e}")

# ✅ 봇 실행
@bot.event
async def on_ready():
    print(f"✅ 디스코드 봇 로그인 성공: {bot.user}")
    check_instagram.start()

bot.run(TOKEN)
