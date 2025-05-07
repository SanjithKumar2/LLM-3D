from dataclasses import dataclass
import requests
from typing import Optional, Dict, Any, Union, List

@dataclass
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
