"""启动脚本"""

import uvicorn
from app.config import config


if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD
    )
