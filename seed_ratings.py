import asyncio
from app.core.database import prisma

async def seed_ratings():
    await prisma.connect()
    
    # Grab all available series to attach the mock reviews
    series_list = await prisma.series.find_many()
    if not series_list:
        print("No series found to attach reviews to. Please create a series first.")
        await prisma.disconnect()
        return

    print(f"Found {len(series_list)} series. Seeding ratings...")

    reviews_data = [
        {
            "userName": "Eleanor Summers",
            "stars": 5.0,
            "feedback": "What can I say it's amazing. No different to any of the other top-tier shows, nice pacing and adequate storyline.",
            "userImage": "https://img.freepik.com/premium-photo/3d-avatar-girl-character-with-long-brown-hair-wearing-black-baseball-cap-black-tshirt_908344-938.jpg"
        },
        {
            "userName": "Victoria Champain",
            "stars": 4.5,
            "feedback": "Story, as always, is good both at the beginning and the end. It's always clean (download the app for offline viewing etc.) sit upstairs every time, more relaxed feel.",
            "userImage": "https://img.freepik.com/premium-photo/profile-icon-girl-with-ponytail 3d-rendering_601748-4330.jpg"
        },
        {
            "userName": "Laura Smith",
            "stars": 5.0,
            "feedback": "Amazing series. Lots of choice. We took a while to choose as everything sounded amazing on the menu! All episodes to perfection. Portions were large. Definitely plan to watch again and often!",
            "userImage": "https://img.freepik.com/premium-photo/3d-avatar-girl-character-with-long-brown-hair-wearing-beanie_908344-935.jpg"
        },
        {
            "userName": "Dora Perry",
            "stars": 2.0,
            "feedback": "I popped in for a late preview on Friday after a long morning working. The protagonist was rude and unhelpful and the plot felt closed. I will not be returning and suggest others do not either.",
            "userImage": "https://img.freepik.com/free-photo/3d-illustration-person-with-sunglasses_23-2149436188.jpg"
        }
    ]

    for series in series_list:
        for idx, review in enumerate(reviews_data):
            # Fallback to realistic avatars if freepik links die
            avatar_url = f"https://api.dicebear.com/7.x/adventurer/png?seed={review['userName'].replace(' ', '')}"
            await prisma.rating.create(
                data={
                    "userName": review["userName"],
                    "stars": review["stars"],
                    "feedback": review["feedback"],
                    "userImage": avatar_url,
                    "seriesId": series.id,
                    "isActive": True
                }
            )
        print(f"Created {len(reviews_data)} ratings for series: {series.title}")

    await prisma.disconnect()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_ratings())
