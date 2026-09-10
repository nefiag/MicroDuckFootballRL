from math import atan2
import random
import mujoco

MODEL="""<mujoco model="microduck"><option timestep="0.012" integrator="RK4"/><default><joint damping="1.4"/><geom friction="1.2 .08 .02" density="650"/></default><worldbody><geom type="plane" size="30 2 .1" rgba=".7 .86 .74 1"/><body name="duck" pos="0 0 .65"><freejoint/><geom type="ellipsoid" size=".28 .14 .19" rgba="1 .76 .12 1"/><geom type="sphere" pos=".22 0 .13" size=".14" rgba="1 .84 .25 1"/><geom type="box" pos=".37 0 .11" size=".1 .09 .045" rgba="1 .38 .08 1"/><body pos="-.12 .1 -.16"><joint name="left" type="hinge" axis="0 1 0" range="-65 65"/><geom type="capsule" fromto="0 0 0 0 0 -.28" size=".045" rgba="1 .45 .08 1"/><geom type="box" pos=".07 0 -.29" size=".12 .06 .035" rgba="1 .45 .08 1"/></body><body pos=".12 -.1 -.16"><joint name="right" type="hinge" axis="0 1 0" range="-65 65"/><geom type="capsule" fromto="0 0 0 0 0 -.28" size=".045" rgba="1 .45 .08 1"/><geom type="box" pos=".07 0 -.29" size=".12 .06 .035" rgba="1 .45 .08 1"/></body></body></worldbody><actuator><motor joint="left" gear="18" ctrlrange="-1 1"/><motor joint="right" gear="18" ctrlrange="-1 1"/></actuator></mujoco>"""

class MujocoDuck:
    actions=["放松","左腿摆动","右腿摆动","迈步 A","迈步 B"]
    controls=[(0,0),(1,-.25),(-.25,1),(1,-1),(-1,1)]
    def __init__(self):self.model=mujoco.MjModel.from_xml_string(MODEL);self.data=mujoco.MjData(self.model);self.reset()
    def reset(self):mujoco.mj_resetData(self.model,self.data);self.data.qpos[2]=.65;mujoco.mj_forward(self.model,self.data);self.steps=0;return self.state()
    def state(self):
        body=self.data.body("duck");pitch=atan2(-body.xmat[6],body.xmat[8]);return (round(pitch/.35),round(float(self.data.qvel[0])/.2),round(float(self.data.qpos[7])/.4),round(float(self.data.qpos[8])/.4))
    def step(self,action):
        self.data.ctrl[:]=self.controls[action]
        for _ in range(4):mujoco.mj_step(self.model,self.data)
        self.steps+=1;body=self.data.body("duck");pitch=atan2(-body.xmat[6],body.xmat[8]);height=float(body.xpos[2]);vx=float(self.data.qvel[0]);fallen=height<.28 or abs(pitch)>1.15;success=float(self.data.qpos[0])>3.;reward=1.8*vx+.12-.003*sum(v*v for v in self.controls[action])-(8 if fallen else 0)+(25 if success else 0)
        frame={"duck_x":float(self.data.qpos[0]),"height":height,"angle":pitch,"velocity":vx,"left_hip":float(self.data.qpos[7]),"right_hip":float(self.data.qpos[8]),"action":action,"action_name":self.actions[action],"reward":reward,"physics_engine":"MuJoCo"}
        return self.state(),reward,fallen or success,frame

class MujocoQAgent:
    def __init__(self,seed=7):self.q={};self.epsilon=.85;self.rng=random.Random(seed)
    def values(self,state):return self.q.setdefault(state,[0.]*5)
    def choose(self,state):return self.rng.randrange(5) if self.rng.random()<self.epsilon else max(range(5),key=self.values(state).__getitem__)
    def learn(self,state,action,reward,next_state,done):
        values=self.values(state);target=reward if done else reward+.97*max(self.values(next_state));error=target-values[action];values[action]+=.16*error;return error
    def end(self):self.epsilon=max(.05,self.epsilon*.95)
