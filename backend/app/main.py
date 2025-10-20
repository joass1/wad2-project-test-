from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
import os

from app.api.routes import auth, profile, pet, notifications, wellness, tasks
from app.core.firebase import db

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080/", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for sprites
static_path = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Socket.IO setup for real-time pet updates
sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=["http://localhost:8080", "*"]
)
socket_app = socketio.ASGIApp(sio, app)
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(wellness.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(pet.router)

# Pet update loop
pet_update_task = None


async def pet_update_loop():
    """Continuously update pet state and broadcast to clients"""
    from app.api.routes.pet import pet_state

    while True:
        try:
            if not pet_state.is_grabbed:
                pet_state.update_position(dt=0.1)

            # Broadcast to all connected clients
            await sio.emit("pet_update", pet_state.to_dict())

            # 10 updates per second
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Pet update error: {e}")
            await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    """Start pet update loop when server starts"""
    global pet_update_task
    pet_update_task = asyncio.create_task(pet_update_loop())


@app.on_event("shutdown")
async def shutdown_event():
    """Stop pet update loop when server stops"""
    if pet_update_task:
        pet_update_task.cancel()


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # Send initial pet state
    from app.api.routes.pet import pet_state

    await sio.emit("pet_state", pet_state.to_dict(), room=sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def move_pet(sid, data):
    from app.api.routes.pet import pet_state

    # CRITICAL: Actually update the backend state
    pet_state.set_position(data["x"], data["y"])

    # Log for debugging
    print(f'🎯 move_pet: x={data["x"]}, y={data["y"]}, grabbed={pet_state.is_grabbed}')


@sio.event
async def grab_pet(sid, data):
    from app.api.routes.pet import pet_state

    grabbed = data["grabbed"]

    print(f"grab_pet: {grabbed}, current_pos=({pet_state.x}, {pet_state.y})")

    # Update grab state
    pet_state.set_grabbed(grabbed)

    await sio.emit("pet_update", pet_state.to_dict(), broadcast=True)


@sio.event
async def grab_pet(sid, data):
    from app.api.routes.pet import pet_state

    grabbed = data["grabbed"]

    print(f"grab_pet: {grabbed}, current_pos=({pet_state.x}, {pet_state.y})")

    pet_state.set_grabbed(grabbed)

    await sio.emit("pet_update", pet_state.to_dict(), broadcast=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(socket_app, host="0.0.0.0", port=8000)


@app.get("/")
def root():
    return {"message": "Hello World"}
