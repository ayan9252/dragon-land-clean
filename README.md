# Dragon Land Server

Replacement server for Dragon Land APK using GitHub Codespaces + Photon.

## Architecture

- **Backend API** (FastAPI): Player auth, profiles, game state
- **Photon Server**: Real-time multiplayer (Cloud or Self-hosted)
- **Modified APK**: Points to this server infrastructure

## Quick Start

### 1. Start Backend Server
```bash
cd backend-api
python app.py
```

### 2. Configure Photon
Option A: Use Photon Cloud
- Create account at https://dashboard.photonengine.com
- Get AppID
- Update APK configuration

Option B: Self-host
- Download Photon Server SDK
- Configure and run locally

### 3. Modify APK
```bash
cd apk-tools
python modify_apk.py
```

### 4. Test on Appetize.io
- Upload modified APK
- Test connection and gameplay

## API Endpoints

- `POST /auth/login` - Player authentication
- `GET /player/{id}` - Get player profile
- `POST /player/{id}/update` - Update player data
- `POST /game/save` - Save game progress
- `GET /leaderboard` - Get rankings

## Ports

- 8000: Backend API
- 5055: Photon UDP
- 9090: Photon WebSocket
- 3000: Admin Panel (optional)

## Server Configuration

### Photon AppID
Original: `1eb3a592-f2d1-41c1-ac3a-cd6308fca5cb`
Replacement: Configure in PhotonServerSettings

### Codespaces URL
The backend API will be accessible at:
`https://<codespace-name>-8000.app.github.dev`

## Testing Checklist

- [ ] Backend API responding
- [ ] Photon connection established
- [ ] APK connects to server
- [ ] Player authentication works
- [ ] Game state saves correctly
- [ ] Multiplayer functions properly

## Notes

- Photon free tier: 20 CCU
- Codespaces port forwarding: automatic HTTPS
- APK modification requires re-signing
