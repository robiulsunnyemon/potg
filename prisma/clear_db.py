import asyncio
from prisma import Prisma

async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    print("🗑️ Clearing existing data in a safe order...")

    # 1. Delete leaf nodes and junction tables
    print("   Deleting saved episodes...")
    await prisma.savedepisode.delete_many()

    print("   Deleting episode views...")
    await prisma.episodeview.delete_many()

    print("   Deleting transactions...")
    await prisma.transaction.delete_many()

    print("   Deleting ratings...")
    await prisma.rating.delete_many()

    # 2. Delete main content hierarchy
    print("   Deleting episodes...")
    await prisma.episode.delete_many()

    print("   Deleting series...")
    await prisma.series.delete_many()

    # 3. Delete root entities
    print("   Deleting categories...")
    await prisma.category.delete_many()

    print("   Deleting languages...")
    await prisma.language.delete_many()

    # 4. Delete user-related artifacts
    print("   Deleting OTP codes...")
    await prisma.otpcode.delete_many()

    print("   Deleting refresh tokens...")
    await prisma.refreshtoken.delete_many()

    print("   Deleting users...")
    await prisma.user.delete_many()

    print("\n✨ Database is now completely clean!")
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
