from prisma import Prisma

# Global Prisma client instance
prisma = Prisma()


async def connect_db() -> None:
    """Connect to the database."""
    await prisma.connect()


async def disconnect_db() -> None:
    """Disconnect from the database."""
    await prisma.disconnect()
