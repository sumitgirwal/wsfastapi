import base64
from fastapi import FastAPI, WebSocket
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import HTMLResponse

# Database setup
DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String, index=True)
    lname = Column(String, index=True)
    email = Column(String, index=True)
    profile_photo = Column(String)
    user_voice = Column(String)

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()

    # Decode profile photo
    profile_photo_data = base64.b64decode(data['profile_photo'])
    profile_photo_path = f"profile_photos/{data['profile_photo_name']}"
    with open(profile_photo_path, "wb") as buffer:
        buffer.write(profile_photo_data)

    # Decode user voice
    user_voice_data = base64.b64decode(data['user_voice'])
    user_voice_path = f"voice_records/{data['user_voice_name']}"
    with open(user_voice_path, "wb") as buffer:
        buffer.write(user_voice_data)

    # Store in database
    db = SessionLocal()
    new_user = User(
        fname=data["fname"],
        lname=data["lname"],
        email=data["email"],
        profile_photo=profile_photo_path,
        user_voice=user_voice_path,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    await websocket.send_json({"message": "User data and voice recording stored successfully!"})
@app.get("/")
async def get_homepage():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)