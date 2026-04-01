import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from prisma import Prisma
from prisma.enums import UserStatus

async def main():
    prisma = Prisma()
    await prisma.connect()
    admin = await prisma.user.find_first(where={"email": "admin@potg.com"})
    if admin:
        if admin.status != UserStatus.ACTIVE:
            await prisma.user.update(
                where={"email": "admin@potg.com"},
                data={"status": UserStatus.ACTIVE}
            )
            print("✅ Admin account activated successfully!")
        else:
            print("✅ Admin is already ACTIVE!")
    else:
        print("❌ Admin account not found!")
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
