from dataclasses import dataclass
import random

@dataclass
class Physics:
    acceleration:float=110.;friction:float=.91;kick_power:float=230.;dt:float=.05

class DuckKickEnv:
    actions=["等待","向左","向右","踢球"]
    def __init__(self,physics=None,seed=7):self.physics=physics or Physics();self.rng=random.Random(seed);self.reset()
    def reset(self):self.duck_x,self.duck_v,self.ball_x,self.ball_v,self.step_count=90.,0.,360.,0.,0;return self.observation()
    def observation(self):return [self.duck_x/800,self.duck_v/150,self.ball_x/800,self.ball_v/250]
    def step(self,action):
        old=abs(720-self.ball_x)
        if action==1:self.duck_v-=self.physics.acceleration*self.physics.dt
        elif action==2:self.duck_v+=self.physics.acceleration*self.physics.dt
        elif action==3 and abs(self.ball_x-self.duck_x)<58:self.ball_v+=self.physics.kick_power*self.physics.dt
        self.duck_v*=self.physics.friction;self.ball_v*=.975;self.duck_x=max(25,min(775,self.duck_x+self.duck_v));self.ball_x=max(15,min(785,self.ball_x+self.ball_v));self.step_count+=1
        reward=(old-abs(720-self.ball_x))*.08-.015+(25 if self.ball_x>=710 else 0)
        if action==3 and abs(self.ball_x-self.duck_x)>=70:reward-=.08
        done=self.ball_x>=710 or self.step_count>=400
        return self.observation(),reward,done,self.snapshot(action)
    def snapshot(self,action=0):return {"duck_x":self.duck_x,"duck_v":self.duck_v,"ball_x":self.ball_x,"ball_v":self.ball_v,"step":self.step_count,"action":action,"action_name":self.actions[action]}

class QAgent:
    def __init__(self,learning_rate=.18,gamma=.96,epsilon=.7,seed=7):self.lr,self.gamma,self.epsilon=learning_rate,gamma,epsilon;self.q={};self.rng=random.Random(seed)
    def state(self,obs):return max(0,min(11,int((obs[2]-obs[0]+1)*6))),max(0,min(7,int(obs[2]*8)))
    def values(self,s):return self.q.setdefault(s,[0.,0.,0.,0.])
    def choose(self,obs):
        if self.rng.random()<self.epsilon:return self.rng.randrange(4)
        values=self.values(self.state(obs));return max(range(4),key=values.__getitem__)
    def learn(self,obs,action,reward,next_obs,done):
        values=self.values(self.state(obs));target=reward if done else reward+self.gamma*max(self.values(self.state(next_obs)));error=target-values[action];values[action]+=self.lr*error;return error
    def end_episode(self):self.epsilon=max(.04,self.epsilon*.94)

def scripted_frames(commands,physics=None):
    env=DuckKickEnv(physics);frames=[]
    for command in commands:
        action=int(command.get("action",0));repeat=max(1,min(80,int(command.get("repeat",1))))
        for _ in range(repeat):
            _,reward,done,info=env.step(action);frames.append({**info,"reward":reward})
            if done:return frames
    return frames
