
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_db, disconnect_db
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.category.router import router as category_router
from app.modules.language.router import router as language_router
from app.modules.series.router import router as series_router
from app.modules.episode.router import router as episode_router
from app.modules.user_activity.router import router as user_activity_router
from app.modules.rating.router import router as rating_router
from app.modules.notification.router import router as notification_router
from app.modules.coins.router import router as coins_router
from app.modules.subscriptions.router import router as subscriptions_router
from app.modules.rewards.router import router as rewards_router
from app.modules.settings.router import router as settings_router
from app.modules.faq.router import router as faq_router
from app.modules.purchases.router import router as purchases_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Connecting to database...")
    await connect_db()
    logger.info("Database connected.")
    yield
    # Shutdown
    logger.info("Disconnecting from database...")
    await disconnect_db()
    logger.info("Database disconnected.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="POTG - FastAPI Authentication Service",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(category_router)
app.include_router(language_router)
app.include_router(series_router)
app.include_router(episode_router)
app.include_router(user_activity_router)
app.include_router(rating_router)
app.include_router(notification_router)
app.include_router(coins_router)
app.include_router(subscriptions_router)
app.include_router(rewards_router)
app.include_router(settings_router)
app.include_router(faq_router)
app.include_router(purchases_router)

@app.get("/")
async def root():
    return {"message": "Welcome to POTG App Authentication API"}
