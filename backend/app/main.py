import asyncio,os
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from .simulation import DuckKickEnv,Physics,QAgent,scripted_frames
app=FastAPI(title="MicroduckTraining API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in os.getenv("ALLOWED_ORIGINS","http://localhost:5173").split(",")],allow_origin_regex=r"https://(microduck-training|frontend)(-[a-z0-9-]+)?\.vercel\.app",allow_methods=["*"],allow_headers=["*"])
class SimulationRequest(BaseModel):
    commands:list[dict]=Field(max_length=30);acceleration:float=Field(110,ge=20,le=300);friction:float=Field(.91,ge=.6,le=.999);kick_power:float=Field(230,ge=50,le=500)
@app.get("/health")
def health():return {"status":"ok","project":"MicroduckTraining"}
@app.post("/api/simulate")
def simulate(request:SimulationRequest):return {"frames":scripted_frames(request.commands,Physics(request.acceleration,request.friction,request.kick_power))}
@app.websocket("/ws/train")
async def train(ws:WebSocket):
    await ws.accept()
    try:
        while True:
            config=await ws.receive_json();episodes=max(1,min(300,int(config.get("episodes",40))));agent=QAgent(float(config.get("learning_rate",.18)),float(config.get("gamma",.96)),float(config.get("epsilon",.7)))
            for episode in range(1,episodes+1):
                env=DuckKickEnv(seed=episode);obs=env.reset();total=0.
                for step in range(300):
                    action=agent.choose(obs);next_obs,reward,done,info=env.step(action);td=agent.learn(obs,action,reward,next_obs,done);obs=next_obs;total+=reward
                    if step%8==0 or done:await ws.send_json({"type":"step","episode":episode,"reward":reward,"total_reward":total,"td_error":td,"epsilon":agent.epsilon,**info});await asyncio.sleep(.01)
                    if done:break
                agent.end_episode();await ws.send_json({"type":"episode","episode":episode,"total_reward":total,"epsilon":agent.epsilon,"q_states":len(agent.q)})
            await ws.send_json({"type":"complete","episodes":episodes})
    except WebSocketDisconnect:return
