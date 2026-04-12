from typing import List
from fastapi import WebSocket


class JobBroadcaster:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, jobs: list):
        print(f"[Broadcaster] Sending to {len(self.connections)} connections")
        disconnected = []
        for ws in self.connections:
            try:
                await ws.send_json(jobs)
                print("[Broadcaster] Sent successfully")
            except Exception as e:
                print(f"[Broadcaster] Failed to send: {e}")
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

        # Clean up any dead connections
        for ws in disconnected:
            self.disconnect(ws)


broadcaster = JobBroadcaster()