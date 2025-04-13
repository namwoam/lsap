from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
import os
import uuid

app = FastAPI()

file_storage_root = os.getenv("IM_IN_LOVE_FILES") or os.path.join(
    os.path.dirname(__file__), "im_in_love_files"
)

if not os.path.exists(file_storage_root):
    os.makedirs(file_storage_root)

sqlite_url = os.getenv("IM_IN_LOVE_DB") or "sqlite:///im_in_love.db"
auth_secret = os.getenv("IM_IN_LOVE_AUTH_SECRET") or "default_secret"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    email: str = Field(max_length=100, unique=True)
    bio: str | None = Field(default=None, max_length=500)
    keywords: str | None = Field(default=None, max_length=500)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    text: str | None = Field(default=None, max_length=500)
    image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)


class Image(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(max_length=500)
    owner_id: int = Field(foreign_key="user.id")


class Video(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(max_length=500)
    owner_id: int = Field(foreign_key="user.id")


@app.get("/")
def read_information():
    return {
        "info": "This is the backend service for the 'IM in Love' application.",
        "version": "1.0",
    }


@app.post("/reset")
def reset(seceret: str):
    """Reset the database and file storage."""
    if seceret != auth_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    for root, _, files in os.walk(file_storage_root):
        for file in files:
            os.remove(os.path.join(root, file))
    return {"status": "success", "message": "Database and file storage reset."}


@app.post("/image/{user_id}")
async def upload_image(user_id: int, file: UploadFile = File(...)):
    """Upload an image and associate it with a user."""
    image_root = os.path.join(file_storage_root, str(user_id))
    if not os.path.exists(image_root):
        os.makedirs(image_root)

    # check if the file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")

    file_name = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
    file_path = os.path.join(image_root, file_name)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    image = Image(url=file_path, owner_id=user_id)
    with Session(engine) as session:
        session.add(image)
        session.commit()
        session.refresh(image)
    return {"status": "success", "image_id": image.id}


@app.get("/image/{image_id}")
def fetch_image(image_id: int):
    """Fetch an image by ID."""
    with Session(engine) as session:
        image = session.get(Image, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

    file_location = image.url

    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")

    file_format = os.path.splitext(file_location)[1]

    return FileResponse(
        file_location,
        media_type=f"image/{file_format[1:]}",  # Remove the dot from the file format
    )


@app.get("/video/{video_id}")
def fetch_video(video_id: int):
    """Fetch a video by ID."""
    with Session(engine) as session:
        video = session.get(Video, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

    file_location = video.url

    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")

    file_format = os.path.splitext(file_location)[1]

    return FileResponse(
        file_location,
        media_type=f"video/{file_format[1:]}",  # Remove the dot from the file format
    )


@app.post("/video/{user_id}")
async def upload_video(user_id: int, file: UploadFile = File(...)):
    """Upload a video and associate it with a user."""
    video_root = os.path.join(file_storage_root, str(user_id))
    if not os.path.exists(video_root):
        os.makedirs(video_root)
    file_name = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
    file_path = os.path.join(video_root, file_name)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    video = Video(url=file_path, owner_id=user_id)
    with Session(engine) as session:
        session.add(video)
        session.commit()
        session.refresh(video)
    return {"status": "success", "video_id": video.id}


@app.post("/message")
async def send_message(
    sender_id: int,
    receiver_id: int,
    text: str = None,
    image_url: str = None,
    video_url: str = None,
):
    """Send a message from one user to another."""
    if not text and not image_url and not video_url:
        raise HTTPException(
            status_code=400,
            detail="At least one of text, image_url or video_url must be provided.",
        )

    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        text=text,
        image_url=image_url,
        video_url=video_url,
    )
    with Session(engine) as session:
        session.add(message)
        session.commit()
        session.refresh(message)
    return {"status": "success", "message": "Message sent."}


@app.get("/messages/{user_id}")
def get_messages(user_id: int):
    """Retrieve messages for a user."""
    with Session(engine) as session:
        messages = session.exec(
            select(Message).where(
                (Message.sender_id == user_id) | (Message.receiver_id == user_id)
            )
        ).all()
    return {"status": "success", "messages": messages}


@app.get("/message/{message_id}")
def get_message(message_id: int):
    """Retrieve a specific message by ID."""
    with Session(engine) as session:
        message = session.get(Message, message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success", "message": message}


@app.post("/user")
def create_user(name: str, email: str, bio: str = None, keywords: str = None):
    """Create a new user."""
    user = User(name=name, email=email, bio=bio, keywords=keywords)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return {"status": "success", "user": user}


@app.get("/user/{user_id}")
def get_user(user_id: int):
    """Retrieve a user by ID."""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "user": user}


@app.put("/user/{user_id}")
def update_user(
    user_id: int,
    name: str = None,
    email: str = None,
    bio: str = None,
    keywords: str = None,
):
    """Update a user's information."""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if name:
            user.name = name
        if email:
            user.email = email
        if bio:
            user.bio = bio
        if keywords:
            user.keywords = keywords
        session.commit()
        session.refresh(user)
    return {"status": "success", "user": user}


@app.get("/users/search")
def search_users(name: str = None, email: str = None):
    """Search for users by name or email."""
    with Session(engine) as session:
        query = select(User)
        if name:
            query = query.where(User.name.contains(name))
        if email:
            query = query.where(User.email.contains(email))
        users = session.exec(query).all()
    return {"status": "success", "users": users}


@app.get("/users/recommendations")
def get_recommendations(user_id: int, limit: int = 10):
    """Get user recommendations based on keywords."""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        keywords = user.keywords.split(",") if user.keywords else []
        recommendations = session.exec(
            select(User)
            .where(User.id != user_id)
            .where(User.bio.contains(keywords))
            .limit(limit)
        ).all()
    return {"status": "success", "recommendations": recommendations}


@app.get("/users")
def get_users(limit: int = 100, offset: int = 0):
    """Retrieve a list of users."""
    with Session(engine) as session:
        users = session.exec(select(User).offset(offset).limit(limit)).all()
    return {"status": "success", "users": users}


@app.delete("/user/{user_id}")
def delete_user(user_id: int):
    """Delete a user by ID."""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
    return {"status": "success", "message": "User deleted."}
