from crewai import Agent, Task, Crew, Process, agent, task, crew
from crewai.crew import BaseAgent
from crewai.flow.flow import Flow, start, listen
from crewai.project import CrewBase
from typing import List
import yaml

@CrewBase
class PrintAgent:
    """3D Print Monitoring Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def observer(self) -> Agent:
        return Agent(
            config=self.agents_config['observer'],
            verbose=True
        )

    @agent
    def reasoner(self) -> Agent:
        return Agent(
            config=self.agents_config['reasoner'],
            verbose=True
        )

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            verbose=True
        )

    @agent
    def executor(self) -> Agent:
        return Agent(
            config=self.agents_config['executor'],
            verbose=True
        )

    @task
    def observation_task(self) -> Task:
        return Task(
            config=self.tasks_config['observation_task'],
        )

    @task
    def reasoning_task(self) -> Task:
        return Task(
            config=self.tasks_config['reasoning_task'],
        )

    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['planning_task'],
        )

    @task
    def execution_task(self) -> Task:
        return Task(
            config=self.tasks_config['execution_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the 3D Print Monitoring Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,

            verbose=True
        )

class PrintAgent:

    def __ini__(self,agent_config_path, task_config_path):
        with open(agent_config_path) as f, open(task_config_path) as t:
            self.agents_info = yaml.safe_load(f)
            self.task_info = yaml.safe_load(t)
    
import dataclasses
import openai
import dotenv
import logging
import os

logger = logging.getLogger(__name__)
dotenv.load_dotenv("C://Users//ASUS//Desktop//AI Projects//LLM-Prt//3dprintagent//.env")
APIKEY = os.environ['OPENAI_API_KEY']

@dataclasses.dataclass
class Agent:

    SYS_PROMPT : str = ""
    name : str = ""
    
    def config_to_sys_prompt(self, agent_name,config):
        assert "role" in config and "goal" in config and "backstory" in config
        try:
            self.name = agent_name
            self.SYS_PROMPT = f"""
            Agent Description:

            Role - Role of the Agent : {config["role"]},
            Goal - Goal of the Agent : {config["goal"]},
            Backstory - Backstory of the Agent: {config["backstory"]}
            """
            return True
        except Exception as e:
            raise e
@dataclasses.dataclass
class Task:
    SYS_PROMPT : str = ""
    task_name : str = ""
    agent : Agent = None
    def config_to_sys_prompt(self, task_name,config, agent : Agent = None):
        assert "description" in config and "expected_output" in config
        try:
            agent_description = agent.SYS_PROMPT
            self.task_name = task_name
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

    openai_uri : str = ""
    is_image : bool = False
    system_prompt : str = ""
    __apikey : str = APIKEY

    def setup(self, task : Task):
        pass
