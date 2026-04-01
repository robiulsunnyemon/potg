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

    print("\n👥 Seeding 10 Normal Users...")
    user_password = hash_password("User@12345")
    
    for i in range(1, 11):
        email = f"user{i}@potg.com"
        phone = f"0180000{i:04d}"
        
        # Check if user already exists
        user_exists = await prisma.user.find_first(where={"email": email})
        if not user_exists:
            user = await prisma.user.create(
                data={
                    "fullName": f"Test User {i}",
                    "email": email,
                    "phoneNumber": phone,
                    "password": user_password,
                    "role": Role.USER,
                    "isVerified": True,
                    "status": random.choice([UserStatus.ACTIVE, UserStatus.INACTIVE]), # Mix of active and inactive
                    "profileImage": f"https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg",
                }
            )
            print(f"✅ User created: {user.email}")
        else:
            print(f"⚡ User {email} already exists, skipping...")

    print("\n🎉 Seeding completed successfully!")
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
