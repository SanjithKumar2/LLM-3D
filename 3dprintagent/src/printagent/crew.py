# from crewai import Agent, Task, Crew, Process, agent, task, crew
# from crewai.crew import BaseAgent
# from crewai.flow.flow import Flow, start, listen
# from crewai.project import CrewBase
# from typing import List
# import yaml

# @CrewBase
# class PrintAgent:
#     """3D Print Monitoring Crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     @agent
#     def observer(self) -> Agent:
#         return Agent(
#             config=self.agents_config['observer'],
#             verbose=True
#         )

#     @agent
#     def reasoner(self) -> Agent:
#         return Agent(
#             config=self.agents_config['reasoner'],
#             verbose=True
#         )

#     @agent
#     def planner(self) -> Agent:
#         return Agent(
#             config=self.agents_config['planner'],
#             verbose=True
#         )

#     @agent
#     def executor(self) -> Agent:
#         return Agent(
#             config=self.agents_config['executor'],
#             verbose=True
#         )

#     @task
#     def observation_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['observation_task'],
#         )

#     @task
#     def reasoning_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['reasoning_task'],
#         )

#     @task
#     def planning_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['planning_task'],
#         )

#     @task
#     def execution_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['execution_task'],
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the 3D Print Monitoring Crew"""
#         return Crew(
#             agents=self.agents,
#             tasks=self.tasks,
#             process=Process.sequential,

#             verbose=True
#         )

# class PrintAgent:

#     def __ini__(self,agent_config_path, task_config_path):
#         with open(agent_config_path) as f, open(task_config_path) as t:
#             self.agents_info = yaml.safe_load(f)
#             self.task_info = yaml.safe_load(t)
    
import dataclasses
import openai
import dotenv
import logging
import os
import base64
from typing import List
import yaml
from tools.custom_tool import tools
logger = logging.getLogger(__name__)
dotenv.load_dotenv("C://Users//ASUS//Desktop//AI Projects//LLM-Prt//3dprintagent//.env")
APIKEY = os.environ['OPENAI_API_KEY']

@dataclasses.dataclass
class Agent:
    config : dict
    SYS_PROMPT : str = ""
    name : str = ""
    def __post_init__(self):
        self.config_to_sys_prompt(self.config)
    
    def config_to_sys_prompt(self,config):
        assert "role" in config and "goal" in config and "backstory" in config
        try:
            self.SYS_PROMPT = f"""
            Agent Description:

            Role - Role of the Agent : {config["role"]},
            Goal - Goal of the Agent : {config["goal"]},
            Backstory - Backstory of the Agent: {config["backstory"]} 
            """
            if "tools" in config:
                self.SYS_PROMPT += f"""
                Tool Description:
                The Agent is allowed to use all tools available to it.
                """ + "\n".join([tools[t].description for t in config["tools"]])
            return True
        except Exception as e:
            raise e
@dataclasses.dataclass
class Task:
    config : str
    SYS_PROMPT : str = ""
    task_name : str = ""
    agent : Agent = None
    def __post_init__(self):
        self.config_to_sys_prompt(config=self.config, agent=self.agent)
    def config_to_sys_prompt(self,config, agent : Agent = None):
        assert "description" in config and "expected_output" in config
        try:
            agent_description = agent.SYS_PROMPT
            self.SYS_PROMPT = f"""
            Task Description:
            {config["description"]}
            Expected Output:
            you must strictly follow Expected output format
            {config["expected_output"]}
            {agent_description}
            """
        except Exception as e:
            raise e
@dataclasses.dataclass
class LLM:
    task : Task
    model : str = "chatgpt-4o-latest"
    openai_uri : str = ""
    system_prompt_payload : str = ""
    __apikey : str = APIKEY
    def __post_init__(self):
        self.setup(self.task)
    def setup(self, task : Task):
        self.system_prompt_payload = {
            "role" : "system",
            "content" : task.SYS_PROMPT
        }
    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    def process(self, input_text = None, input_image = None, is_image = False):
        image = None
        content = []
        if input_text:
            content.append({"type":"text","text":input_text})
        if is_image:
            assert input_image != None
            if isinstance(input_image, str):
                image = self.encode_image(input_image)
                content.append({"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{image}"}})
        if content:
            user_inp = {
                "role":"user", "content" : content
            }
            response = openai.chat.completions.create(
                model=self.model,
                messages=[self.system_prompt_payload,user_inp],
                max_tokens=10000
            )
            return response.choices[0].message.content
        return None
            
@dataclasses.dataclass
class Flow:

    # agents : List[Agent] = dataclasses.field(default_factory=list)
    process : List[LLM] = dataclasses.field(default_factory=list)

    def run(self,input = None, image_input = None):
        result = None
        for proc in self.process:
            if image_input:
                result = proc.process(input, image_input,True)
            else:
                result = proc.process(input)
            input = result
        return result
    
def main():

    with open("C://Users//ASUS//Desktop//AI Projects//LLM-Prt//3dprintagent//src//printagent//config//agents.yaml", "r") as f:
        agents_config = yaml.safe_load(f)
    with open("C://Users//ASUS//Desktop//AI Projects//LLM-Prt//3dprintagent//src//printagent//config//tasks.yaml", "r") as f:
        tasks_config = yaml.safe_load(f)
    agents = {}
    tasks = {}
    for agent, desc in agents_config.items():
        agents[agent] = Agent(desc,name=agent)
    for task, desc in tasks_config.items():
        tasks[task] = Task(desc,task_name=task,agent=agents[desc["agent"]])
    LLMs : List[LLM] = []
    for task,task_d in tasks.items():
        LLMs.append(LLM(task=task_d))

    observer, reasoner, planner, executor = LLMs[0], LLMs[1], LLMs[2], LLMs[3]
    image_path = "C://Users//ASUS//Desktop//AI Projects//LLM-Prt//3dprintagent//src//printagent//sample//test.jpg"
    observations = observer.process("Layer Level 9",image_path,is_image=True)
    extra_info = reasoner.process(f"Observations: {observations}")
    plans = planner.process(f"Observations: {observations}, reasoning modules: {extra_info}")
    executor = executor.process(f"Known Information : {plans}")
    print(executor)

if __name__ == "__main__":
    main()