from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path

# Import database and background tasks
from database.mongodb import db
from tasks.background_tasks import background_tasks

# Import routes
from routes.auth import router as auth_router
from routes.game import router as game_router
from routes.chat import router as chat_router
from routes.admin import router as admin_router
from routes.diplomacy import router as diplomacy_router

# Load environment variables
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Medieval Empires Server...")
    
    try:
        # Connect to MongoDB
        await db.connect_to_mongo()
        logger.info("Connected to MongoDB")
        
        # Start background tasks
        await background_tasks.start_all_tasks()
        logger.info("Background tasks started")
        
        # Create admin user if doesn't exist
        await create_admin_user()
        
        logger.info("Medieval Empires Server started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Medieval Empires Server...")
    
    try:
        # Stop background tasks
        await background_tasks.stop_all_tasks()
        logger.info("Background tasks stopped")
        
        # Close database connection
        await db.close_mongo_connection()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Medieval Empires Server shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Medieval Empires API",
    description="Medieval multiplayer strategy game API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "message": "Medieval Empires API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@api_router.get("/status")
async def server_status():
    """Server status endpoint"""
    try:
        # Check database connection
        await db.client.admin.command('ping')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    # Get basic stats
    try:
        stats = await db.get_game_stats()
    except:
        stats = {"error": "Unable to fetch stats"}
    
    return {
        "status": "running",
        "database": db_status,
        "background_tasks": background_tasks.running,
        "stats": stats
    }

# Include routers
api_router.include_router(auth_router)
api_router.include_router(game_router)
api_router.include_router(chat_router)
api_router.include_router(admin_router)
api_router.include_router(diplomacy_router)

# Include API router in main app
app.include_router(api_router)

async def create_admin_user():
    """Create default admin user if it doesn't exist"""
    try:
        # Check if admin user exists
        admin_user = await db.get_user_by_username("admin")
        if admin_user:
            logger.info("Admin user already exists")
            return
        
        # Create admin user
        from auth.password import hash_password
        from game.empire_bonuses import EmpireBonuses
        from game.buildings import BuildingSystem
        from datetime import datetime
        
        # Create admin user account
        admin_user_data = {
            "username": "admin",
            "email": "admin@medievalempires.com",
            "passwordHash": hash_password("admin"),
            "isAdmin": True,
            "joinDate": datetime.utcnow(),
            "lastActive": datetime.utcnow()
        }
        
        admin_user_id = await db.create_user(admin_user_data)
        
        # Create admin player profile
        starting_resources = EmpireBonuses.get_starting_resources("norman")
        # Give admin extra resources
        starting_resources = {
            "gold": 10000,
            "wood": 5000,
            "stone": 5000,
            "food": 5000
        }
        
        default_buildings = BuildingSystem.get_default_buildings()
        # Upgrade admin buildings
        for building in default_buildings:
            building["level"] = 5
        
        admin_player_data = {
            "userId": admin_user_id,
            "username": "admin",
            "kingdomName": "System Administration",
            "empire": "norman",
            "bio": "System Administrator - Maintaining order in the medieval world",
            "location": "Server Realm",
            "motto": "With great power comes great responsibility",
            "resources": starting_resources,
            "buildings": default_buildings,
            "army": {"soldiers": 1000, "archers": 500, "cavalry": 250},
            "power": 50000,
            "coordinates": {"x": 0, "y": 0},
            "createdAt": datetime.utcnow(),
            "lastActive": datetime.utcnow()
        }
        
        await db.create_player(admin_player_data)
        
        logger.info("Admin user created successfully (username: admin, password: admin)")
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "status_code": 404}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )