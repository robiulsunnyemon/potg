import asyncio
import random
from prisma import Prisma
from prisma.enums import Role, UserStatus
import sys
import os

# Add the parent directory to sys.path so we can import from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password

async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    print("🌱 Clearing existing data...")
    # Optional: Clear existing users before seeding
    # await prisma.user.delete_many()

    print("🧑‍💻 Seeding 1 Admin User...")
    admin_password = hash_password("Admin@12345")
    
    # Check if admin already exists
    admin_exists = await prisma.user.find_first(where={"email": "admin@potg.com"})
    if not admin_exists:
        admin_user = await prisma.user.create(
            data={
                "fullName": "Super Admin",
                "email": "admin@potg.com",
                "phoneNumber": "01700000000",
                "password": admin_password,
                "role": Role.ADMIN,
                "isVerified": True,
                "status": UserStatus.ACTIVE,
                "profileImage": "https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg",
            }
        )
        print(f"✅ Admin created: {admin_user.email}")
    else:
        print("⚡ Admin already exists, skipping...")

    print("\n📦 Seeding Categories...")
    categories = ["Action", "Drama", "Comedy", "Thriller", "Kids"]
    category_ids = []
    for cat_name in categories:
        cat = await prisma.category.upsert(
            where={"name": cat_name},
            data={"create": {"name": cat_name}, "update": {}}
        )
        category_ids.append(cat.id)
        print(f"✅ Category: {cat_name}")

    print("\n🌐 Seeding Languages...")
    languages = ["English", "Bangla"]
    language_ids = []
    for lang_name in languages:
        lang = await prisma.language.upsert(
            where={"name": lang_name},
            data={"create": {"name": lang_name}, "update": {}}
        )
        language_ids.append(lang.id)
        print(f"✅ Language: {lang_name}")

    print("\n📺 Seeding 5 Series...")
    from prisma.enums import EpisodeUnlockMethod, AccessControlStatus
    series_ids = []
    for i in range(1, 6):
        title = f"Amazing Series {i}"
        series = await prisma.series.create(
            data={
                "title": title,
                "description": f"This is the description for {title}. It's a very interesting series with lots of twists.",
                "categoryId": random.choice(category_ids),
                "languageId": random.choice(language_ids),
                "keywords": "thriller, mystery, fun",
                "thumbnail": f"https://picsum.photos/seed/series{i}/400/600",
                "freeEpisodeLimit": 1,
                "episodeUnlockMethod": random.choice([EpisodeUnlockMethod.FREE, EpisodeUnlockMethod.COIN]),
                "coinPerEpisode": 10 if i % 2 == 0 else 0,
                "accessControlStatus": AccessControlStatus.PUBLIC,
                "isSensitiveContent": False,
                "tags": "popular, trending"
            }
        )
        series_ids.append(series.id)
        print(f"✅ Series created: {series.title}")

    print("\n🎬 Seeding 3 Episodes per Series...")
    for s_id in series_ids:
        for j in range(1, 4):
            episode = await prisma.episode.create(
                data={
                    "title": f"Episode {j}",
                    "series": {
                        "connect": {
                            "id": s_id
                        }
                    },
                    "description": f"In this episode {j}, things get even more exciting.",
                    "episodeSerialNumber": j,
                    "thumbnail": f"https://picsum.photos/seed/episode{s_id[:4]}{j}/800/450",
                    "resolution": "1080p",
                    "muxAssetId": "QR8OVYbXpHksEfOYeXd3FT02h6kJ6BA0101DA9jgTp61LA",
                    "muxPlaybackId": "o5Lfd3eHEhVF24cKFJPU002bUSM013UTBmOXYKJ29A01SA",
                    "duration": 4.795867,
                    "isProcessing": False
                }
            )
            print(f"   ✅ Episode {j} for Series {s_id[:8]}...")

    print("\n🎉 Seeding completed successfully!")
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
