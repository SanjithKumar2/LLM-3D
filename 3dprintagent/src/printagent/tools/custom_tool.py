from crewai.tools import BaseTool
from typing import Type, List, Union, Dict, Any
from pydantic import BaseModel, Field
from communicate.makerequests import MakeRequests


class Input(BaseModel):
    kind : str = Field(..., description="Must be set to SET/GET based on the action to perform, SET - sets GCode Objects, GET - gets GCode Objects")
    command : str = Field(None, description="GCode Command to run in case of SET (setting or overriding a GCode Object), Example : M220 S50")
    object_name : str = Field(None, description="GCode Objects that needs to be queried, must be provided in case of using GET, Only allowed GCode Objects can be mentioned")
    fields : List[str] = Field([], description="A list of fields the needs to queried of a particular GCode object, NOTE : Only used when using GET, and the fields must be associated with the chosen object_name.")

class CommunicateTool:
    name: str = "PrinterCommunicateTool"
    description: str = (
        "Communicates with a 3D printer via Moonraker API. "
        "Use kind='SET' to send a GCode command (e.g., M220 S50). "
        "Use kind='GET' to query GCode objects (e.g., extruder, temperature_sensor) and optionally their fields."
    )
    allowed_objects = {"extruder", "temperature_sensor"}

    def __init__(self, requester: MakeRequests):
        self.requester = requester

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