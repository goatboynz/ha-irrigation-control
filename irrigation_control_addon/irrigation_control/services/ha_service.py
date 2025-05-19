import requests
from typing import List, Dict, Any
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class HomeAssistantAPIError(Exception):
    """Custom exception for Home Assistant API errors"""
    pass

class HomeAssistantService:
    def __init__(self, supervisor_token: str):
        self.supervisor_token = supervisor_token
        self.headers = {
            "Authorization": f"Bearer {supervisor_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Home Assistant API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/api/states')
            json_data: Optional JSON data for POST requests
            
        Returns:
            Dict containing the API response
            
        Raises:
            HomeAssistantAPIError: If the API request fails
        """
        url = f"{settings.CORE_URL}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Home Assistant API error: {str(e)}")
            raise HomeAssistantAPIError(f"Failed to {method} {endpoint}: {str(e)}")
    
    def get_switches(self) -> List[Dict[str, str]]:
        """
        Get all switch entities from Home Assistant
        
        Returns:
            List of dicts containing entity_id and friendly_name for each switch
        """
        try:
            states = self._make_request("GET", "/api/states")
            switches = []
            
            for state in states:
                entity_id = state.get("entity_id", "")
                if entity_id.startswith("switch."):
                    attributes = state.get("attributes", {})
                    friendly_name = attributes.get("friendly_name", entity_id)
                    switches.append({
                        "entity_id": entity_id,
                        "name": friendly_name
                    })
            
            return switches
            
        except HomeAssistantAPIError as e:
            logger.error(f"Failed to get switches: {str(e)}")
            raise
    
    def control_switch(self, entity_id: str, action: str) -> bool:
        """
        Control a switch entity in Home Assistant
        
        Args:
            entity_id: The entity_id of the switch to control
            action: Either 'turn_on' or 'turn_off'
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If action is invalid
            HomeAssistantAPIError: If the API request fails
        """
        if action not in ["turn_on", "turn_off"]:
            raise ValueError("Action must be either 'turn_on' or 'turn_off'")
        
        try:
            self._make_request(
                method="POST",
                endpoint=f"/api/services/switch/{action}",
                json_data={"entity_id": entity_id}
            )
            return True
            
        except HomeAssistantAPIError as e:
            logger.error(f"Failed to {action} switch {entity_id}: {str(e)}")
            return False
    
    def get_switch_state(self, entity_id: str) -> bool:
        """
        Get the current state of a switch
        
        Args:
            entity_id: The entity_id of the switch
            
        Returns:
            bool: True if the switch is on, False if off
        """
        try:
            state = self._make_request("GET", f"/api/states/{entity_id}")
            return state.get("state") == "on"
            
        except HomeAssistantAPIError as e:
            logger.error(f"Failed to get state for {entity_id}: {str(e)}")
            return False
