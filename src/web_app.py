"""FastAPI web application for SSH AI Assistant."""

import uuid
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .ai_agent import AIAgent
from .database import init_database
from .models import MachineConfig

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(title="SSH AI Assistant", description="Web interface for SSH AI operations")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize AI agent
ai_agent = AIAgent()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))

manager = ConnectionManager()

# Pydantic models for API
class MachineCreate(BaseModel):
    name: str
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    description: Optional[str] = None

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    description: Optional[str] = None

class ChatMessage(BaseModel):
    message: str

class SessionCreate(BaseModel):
    pass

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with machine selection."""
    machines = ai_agent.list_machines()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "machines": machines
    })

@app.get("/chat/{session_id}", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str):
    """Chat page for a specific session."""
    # Verify session exists
    context = ai_agent.get_session(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get selected machine info if any
    selected_machine = None
    if context.selected_machine:
        machine = ai_agent.machine_manager.get_machine(context.selected_machine)
        if machine:
            selected_machine = {
                "id": machine.id,
                "name": machine.name,
                "host": machine.host,
                "description": machine.description
            }
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "session_id": session_id,
        "selected_machine": selected_machine,
        "conversation_history": context.conversation_history
    })

# API Routes
@app.post("/api/sessions")
async def create_session():
    """Create a new chat session."""
    session_id = ai_agent.create_session()
    return {"session_id": session_id}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    context = ai_agent.get_session(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": context.session_id,
        "selected_machine": context.selected_machine,
        "created_at": context.created_at.isoformat(),
        "last_activity": context.last_activity.isoformat(),
        "conversation_history": context.conversation_history
    }

@app.post("/api/sessions/{session_id}/select-machine/{machine_id}")
async def select_machine(session_id: str, machine_id: str):
    """Select a machine for the session."""
    result = ai_agent.select_machine(session_id, machine_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Notify WebSocket client
    await manager.send_message(session_id, {
        "type": "machine_selected",
        "machine": result["machine"]
    })
    
    return result

@app.get("/api/machines")
async def list_machines():
    """List all available machines."""
    return ai_agent.list_machines()

@app.post("/api/machines")
async def create_machine(machine: MachineCreate):
    """Create a new machine configuration."""
    machine_config = {
        "id": str(uuid.uuid4()),
        "name": machine.name,
        "host": machine.host,
        "port": machine.port,
        "username": machine.username,
        "password": machine.password,
        "private_key_path": machine.private_key_path,
        "description": machine.description
    }
    
    result = ai_agent.add_machine(machine_config)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/api/machines/{machine_id}")
async def get_machine(machine_id: str):
    """Get a specific machine configuration."""
    machine = ai_agent.machine_manager.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    return {
        "id": machine.id,
        "name": machine.name,
        "host": machine.host,
        "port": machine.port,
        "username": machine.username,
        "description": machine.description,
        "created_at": machine.created_at.isoformat(),
        "updated_at": machine.updated_at.isoformat()
    }

@app.put("/api/machines/{machine_id}")
async def update_machine(machine_id: str, updates: MachineUpdate):
    """Update a machine configuration."""
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    success = ai_agent.machine_manager.update_machine(machine_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Machine not found or update failed")
    
    return {"success": True}

@app.delete("/api/machines/{machine_id}")
async def delete_machine(machine_id: str):
    """Delete a machine configuration."""
    result = ai_agent.remove_machine(machine_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    return result

@app.get("/api/machines/search/{query}")
async def search_machines(query: str):
    """Search machines by name, host, or description."""
    machines = ai_agent.machine_manager.search_machines(query)
    return [
        {
            "id": machine.id,
            "name": machine.name,
            "host": machine.host,
            "port": machine.port,
            "description": machine.description,
            "created_at": machine.created_at.isoformat()
        }
        for machine in machines
    ]

# WebSocket endpoint for chat
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "chat_message":
                user_message = message_data["message"]
                
                # Send acknowledgment
                await manager.send_message(session_id, {
                    "type": "message_received",
                    "message": user_message,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Process command with AI agent
                try:
                    result = ai_agent.process_command(session_id, user_message)
                    
                    if result["success"]:
                        # Send successful response
                        await manager.send_message(session_id, {
                            "type": "ai_response",
                            "success": True,
                            "summary": result["summary"],
                            "results": result["results"],
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        # Send error response
                        await manager.send_message(session_id, {
                            "type": "ai_response",
                            "success": False,
                            "error": result["error"],
                            "suggestions": result.get("suggestions", []),
                            "available_commands": result.get("available_commands", {}),
                            "timestamp": datetime.now().isoformat()
                        })
                
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    await manager.send_message(session_id, {
                        "type": "ai_response",
                        "success": False,
                        "error": f"Internal error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_data["type"] == "ping":
                # Respond to ping with pong
                await manager.send_message(session_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)