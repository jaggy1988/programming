import os
import json
from typing import Dict, Any

class RouterConfig:
    def __init__(self):
        self.routers = self._load_router_config()

    def _load_router_config(self) -> Dict[str, Any]:
        """Load router configurations from environment variable"""
        config = os.getenv('ROUTER_CONFIG')
        if not config:
            raise ValueError("ROUTER_CONFIG environment variable not found")
        try:
            return json.loads(config)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in ROUTER_CONFIG")

    def get_router_config(self, router_id: str) -> Dict[str, str]:
        """Get configuration for a specific router"""
        if router_id not in self.routers:
            raise ValueError(f"Router ID '{router_id}' not found in configuration")
        return self.routers[router_id]

    def get_all_routers(self) -> Dict[str, Any]:
        """Get all router configurations"""
        return self.routers

    def get_routers_by_location(self, location: str) -> Dict[str, Any]:
        """Get routers filtered by location"""
        return {
            router_id: config 
            for router_id, config in self.routers.items() 
            if config['location'].lower() == location.lower()
        }