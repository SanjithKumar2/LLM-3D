from typing import Type, List, Union, Dict, Any
from pydantic import BaseModel, Field
import requests
from typing import Optional, Dict, Any, Union, List
import dataclasses

@dataclasses.dataclass
class MakeRequests:
    moonraker_url: str = "http://192.168.1.100:7125"

    def send_post(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], None]:
        url = f"{self.moonraker_url}{endpoint}"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"POST request failed: {e}")
            return None

    def send_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], None]:
        url = f"{self.moonraker_url}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"GET request failed: {e}")
            return None

    def query_object(self, object_name: str, fields: Optional[List[str]] = None) -> Union[Dict[str, Any], None]:
        """
        Queries a specific G-code object and optionally its fields.

        :param object_name: Name of the G-code object (e.g., 'toolhead', 'extruder')
        :param fields: Optional list of specific fields to query
        :return: JSON response or None if error
        """
        payload = {
            "objects": {
                object_name: fields if fields is not None else None
            }
        }
        return self.send_post("/printer/objects/query", payload)


class Input(BaseModel):
    kind : str = Field(..., description="Must be set to SET/GET based on the action to perform, SET - sets GCode Objects, GET - gets GCode Objects")
    command : str = Field(None, description="GCode Command to run in case of SET (setting or overriding a GCode Object), Example : M220 S50")
    intention : str = Field(None, description="The intention of the Agent when Getting GCode Objects (Must be a clear cut thought of at most 2 lines, ONLY TO BE USED WHEN CALLED AS A TOOL)")
    object_name : str = Field(None, description="GCode Objects that needs to be queried, must be provided in case of using GET, Only allowed GCode Objects can be mentioned")
    fields : List[str] = Field([], description="A list of fields the needs to queried of a particular GCode object, NOTE : Only used when using GET, and the fields must be associated with the chosen object_name.")

class CommunicateTool:
    name: str = "PrinterCommunicateTool"
    description: str = (
        """Communicates with a 3D printer via Moonraker API.
        Use kind='SET' to send a GCode command (e.g., M220 S50). (Agent is not allowed to make SET requests, agents must only provide the commands to be sent or the fields that have to be updated after creful consideration and analysis, requests will be sent manually)
        Use kind='GET' to query GCode objects (e.g., extruder, temperature_sensor) and optionally their fields.
        
        Expected Input Format to the tool
        {toolcall : {
        kind : Must be set to SET/GET based on the action to perform, SET - sets GCode Objects, GET - gets GCode Objects, (AGENTS NOT ALLOWED TO USE SET DIRECTLY),
        command : List of GCode Command to run in case of SET (setting or overriding a GCode Object), Example : M220 S50, (NOT FOR AGENTS TO USE, MUST BE SET TO NONE WHEN USED AS A TOOL),
        intention: The intention of the Agent when Getting GCode Objects (Must be a clear cut thought of at most 2 lines, ONLY TO BE USED WHEN CALLED AS A TOOL),
        object_name : GCode Objects that needs to be queried, must be provided in case of using GET, Only allowed GCode Objects can be mentioned,
        fields : A list of fields the needs to queried of a particular GCode object, NOTE : Only used when using GET, and the fields must be associated with the chosen object_name.
        },}
        """
    )
    allowed_objects = {"extruder", "temperature_sensor"}

    def __init__(self):
        self.requester = MakeRequests()

    def run(self, input_data: Input) -> Union[Dict[str, Any], str]:
        if input_data.kind.upper() == "SET":
            if not input_data.command:
                return "Error: 'command' must be provided for SET operation."
            return self.requester.send_post("/printer/gcode/script", {"script": input_data.command}) or "SET operation failed."

        elif input_data.kind.upper() == "GET":
            if not input_data.object_name:
                return "Error: 'object_name' must be provided for GET operation."
            if input_data.object_name not in self.allowed_objects:
                return f"Error: object_name '{input_data.object_name}' is not allowed. Allowed objects: {self.allowed_objects}"
            return self.requester.query_object(input_data.object_name, input_data.fields) or "GET operation failed."

        else:
            return "Error: 'kind' must be either 'SET' or 'GET'."

tools = {"CommunicateTool":CommunicateTool()}