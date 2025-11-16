
import sys
sys.path.insert(0, '/workspace/dragon-land-server/backend-api')
from app import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
