"""
Dragon Land Backend API
Handles player authentication, profiles, and game state
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="Dragon Land Server", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
players = {}
sessions = {}

class Player(BaseModel):
    user_id: str
    username: str
    level: int = 1
    coins: int = 0
    gems: int = 0
    dragons: List[str] = []
    current_episode: int = 1
    current_level: int = 1

class AuthRequest(BaseModel):
    device_id: str
    username: Optional[str] = None

class GameState(BaseModel):
    player_id: str
    episode: int
    level: int
    score: int
    coins_collected: int
    dragons_used: List[str]

@app.get("/")
async def root():
    return {
        "service": "Dragon Land Server",
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "photon_status": "connected"}

@app.post("/auth/login")
async def login(auth: AuthRequest):
    """Authenticate player and return session token"""
    device_id = auth.device_id
    
    if device_id in players:
        player = players[device_id]
    else:
        # Create new player
        player = Player(
            user_id=device_id,
            username=auth.username or f"Dragon{len(players)}",
            dragons=["fire"]  # Starting dragon
        )
        players[device_id] = player
    
    # Create session
    session_token = f"session_{device_id}_{datetime.utcnow().timestamp()}"
    sessions[session_token] = device_id
    
    return {
        "success": True,
        "session_token": session_token,
        "player": player.dict()
    }

@app.get("/player/{player_id}")
async def get_player(player_id: str):
    """Get player profile"""
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    return players[player_id].dict()

@app.post("/player/{player_id}/update")
async def update_player(player_id: str, updates: Dict):
    """Update player data"""
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player = players[player_id]
    for key, value in updates.items():
        if hasattr(player, key):
            setattr(player, key, value)
    
    return {"success": True, "player": player.dict()}

@app.post("/game/save")
async def save_game_state(state: GameState):
    """Save game progress"""
    player_id = state.player_id
    if player_id in players:
        player = players[player_id]
        player.current_episode = state.episode
        player.current_level = state.level
        player.coins += state.coins_collected
        return {"success": True, "message": "Progress saved"}
    return {"success": False, "message": "Player not found"}

@app.get("/leaderboard")
async def get_leaderboard():
    """Get top players"""
    sorted_players = sorted(
        players.values(),
        key=lambda p: p.level * 1000 + p.coins,
        reverse=True
    )[:100]
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "username": p.username,
                "level": p.level,
                "coins": p.coins
            }
            for i, p in enumerate(sorted_players)
        ]
    }

@app.get("/server/stats")
async def server_stats():
    """Get server statistics"""
    return {
        "total_players": len(players),
        "active_sessions": len(sessions),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print("=" * 60)
    print("Dragon Land Backend Server")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
