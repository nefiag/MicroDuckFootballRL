from app.simulation import DuckKickEnv,QAgent,scripted_frames
def test_scripted_motion():assert scripted_frames([{"action":2,"repeat":34},{"action":3,"repeat":20}])[-1]["duck_x"]>90
def test_q_update():
    env=DuckKickEnv();agent=QAgent();obs=env.reset();action=agent.choose(obs);next_obs,reward,done,_=env.step(action);before=agent.values(agent.state(obs))[action];agent.learn(obs,action,reward,next_obs,done);assert agent.values(agent.state(obs))[action]!=before
