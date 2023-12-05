from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
from gpt_researcher.utils.websocket_manager import WebSocketManager
from gpt_researcher.config.config import Config
from .utils import write_md_to_pdf
from mylogger import LoggerSingleton


class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str


app = FastAPI()

app.mount("/site", StaticFiles(directory="./frontend"), name="site")
app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

templates = Jinja2Templates(directory="./frontend")

manager = WebSocketManager()

logger = LoggerSingleton()


# Dynamic directory for outputs once first research is run
@app.on_event("startup")
def startup_event():
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "report": None}
    )


# @app.post("/start-research")
# async def start_research(request: ResearchRequest):
#     try:
#         # Process the research request
#         # This will depend on how your research process is implemented.
#         # For example, you might use a function from your WebSocketManager.
#         report = await manager.start_research(request.task, request.report_type)

#         # Convert the report to PDF and get the file path
#         pdf_path = await write_md_to_pdf(report)
#         return {"message": "Research completed", "pdf_path": pdf_path}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit_report")
async def submit_report(request: ResearchRequest):
    # Extracting the values
    task = request.task
    report_type = request.report_type
    agent = request.agent

    # Implement your logic here
    return {
        "message": "Report received",
        "task": task,
        "report_type": report_type,
        "agent": agent,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.log_debug(
                "server.py - websocket_endpoint: data recieved from websocket: %s", data
            )

            if data.startswith("start"):
                json_data = json.loads(data[6:])
                task = json_data.get("task")
                request_id = json_data.get("request_id")
                user_files = json_data.get("user_files")
                report_type = json_data.get("report_type")
                temperature = json_data.get("temperature", None)
                user_url_list = json_data.get("user_url_list", None)

                logger.log_debug(
                    "server.py - websocket_endpoint: task: %s, request_id: %s, user_files: %s, report_type: %s, temperature: %s, user_url_list: %s",
                    task,
                    request_id,
                    user_files,
                    report_type,
                    temperature,
                    user_url_list,
                )

                if task and report_type:
                    report = await manager.start_streaming(
                        task=task,
                        request_id=request_id,
                        user_files=user_files,
                        report_type=report_type,
                        user_url_list=user_url_list,
                        websocket=websocket,
                    )
                    path = await write_md_to_pdf(report)
                    await websocket.send_json({"type": "path", "output": path})

                elif task and report_type and temperature:
                    # normalize temprature
                    temperature = round(temperature / 100, 2)
                    logger.log_debug(
                        "server.py - websocket_endpoint: temperature: %s", temperature
                    )
                    Config.load_config_file(temperature)
                    report = await manager.start_streaming(
                        task=task,
                        report_type=report_type,
                        user_url_list=user_url_list,
                        websocket=websocket,
                    )
                    path = await write_md_to_pdf(report)
                    await websocket.send_json({"type": "path", "output": path})

                else:
                    print("Error: not enough parameters provided.")

    except WebSocketDisconnect:
        print("excp")
        await manager.disconnect(websocket)
