import os
from APP1.main import app
import uvicorn

if __name__ == "__main__":
    file = __file__
    file = os.path.basename(file)
    file = os.path.splitext(file)[0]
    uvicorn.run(app=f"{file}:app", host="127.0.0.1", port=8000, reload=True)