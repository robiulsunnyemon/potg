import asyncio
import random
import sys
import os

# Add the parent directory to sys.path so we can import from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma import Prisma
from prisma.enums import Role, UserStatus
from app.core.security import hash_password

async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    print("🧑‍💻 Seeding 10 Users...")
    
    # We will generate a base password for all users for easy testing
    base_password = hash_password("User@12345")
    
    for i in range(1, 11):
        email = f"user{i}@potg.com"
        
        # Check if user already exists
        existing_user = await prisma.user.find_first(where={"email": email})
        
        if not existing_user:
            user = await prisma.user.create(
                data={
                    "fullName": f"Test User {i}",
                    "email": email,
                    "phoneNumber": f"01800000{i:03d}",
                    "password": base_password,
                    "role": Role.USER,
                    "isVerified": True,
                    "status": UserStatus.ACTIVE,
                    "balance": random.randint(100, 1000),
                    "profileImage": f"https://picsum.photos/seed/user{i}/200/200",
                    "isPremium": random.choice([True, False])
                }
            )
            print(f"✅ User created: {user.fullName} ({user.email})")
        else:
            print(f"⚡ User {email} already exists, skipping...")

    print("\n🎉 User seeding completed successfully!")
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
