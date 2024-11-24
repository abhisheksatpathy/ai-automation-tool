# backend/main.py

from fastapi import FastAPI, WebSocket, HTTPException, Depends, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from websocket_manager import manager
from database import get_db, WorkflowModel
from sqlalchemy.orm import Session
from workflow_executor import execute_workflow, get_task_status
import asyncio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str

class Workflow(BaseModel):
    blocks: List[Dict[str, Any]]

class WorkflowSave(BaseModel):
    name: str
    description: Optional[str]
    workflow: Dict

@app.websocket("/ws/{workflow_id}")
async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
    print(f"WebSocket connection started for workflow: {workflow_id}")
    try:
        await manager.connect(websocket, workflow_id)
        while True:
            try:
                status = get_task_status(workflow_id)
                print(f"Task status for {workflow_id}: {status}")
                await manager.send_update(workflow_id, status)
                
                if status['state'] in ['SUCCESS', 'FAILURE']:
                    print(f"Workflow {workflow_id} completed with status: {status}")
                    break
                    
                await asyncio.sleep(1)
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for workflow: {workflow_id}")
                await manager.disconnect(websocket, workflow_id)
                break
            except Exception as e:
                print(f"Error in WebSocket loop: {str(e)}")
                break
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        if websocket in manager.active_connections.get(workflow_id, []):
            await manager.disconnect(websocket, workflow_id)

@app.post("/execute-workflow")
async def execute_workflow_endpoint(workflow: Workflow):
    try:
        workflow_dict = workflow.dict()
        result = execute_workflow(workflow_dict)
        if result:
            return {"task_id": result.id}
        raise HTTPException(status_code=400, detail="No valid tasks in workflow")
    except Exception as e:
        print(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/task-status/{task_id}")
async def get_task_status_endpoint(task_id: str):
    try:
        status = get_task_status(task_id)
        print(f"Task status for {task_id}: {status}")
        return status
    except Exception as e:
        print(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/save")
async def save_workflow(workflow_data: WorkflowSave, db: Session = Depends(get_db)):
    workflow = WorkflowModel(
        name=workflow_data.name,
        description=workflow_data.description,
        workflow_json=workflow_data.workflow,
        created_at=datetime.utcnow()
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return {"id": workflow.id, "message": "Workflow saved successfully"}

@app.get("/workflows")
async def get_workflows(db: Session = Depends(get_db)):
    workflows = db.query(WorkflowModel).all()
    return workflows

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
