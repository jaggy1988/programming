from netmiko import ConnectHandler
import json
from typing import Dict, List
from router_config import RouterConfig

class RouterConnection:
    def __init__(self, router_id: str, config: Dict[str, str], device_type: str = "cisco_ios"):
        self.router_id = router_id
        self.device_info = {
            'device_type': device_type,
            'host': config['host'],
            'username': config['username'],
            'password': config['password'],
            'secret': config['password'],  # Enable secret
        }
        self.location = config['location']
        self.connection = None

    def connect(self) -> None:
        """Establish connection to the router"""
        try:
            self.connection = ConnectHandler(**self.device_info)
            self.connection.enable()  # Enter enable mode
        except Exception as e:
            raise Exception(f"Failed to connect to {self.device_info['host']} ({self.location}): {str(e)}")

    def get_bgp_table(self) -> List[Dict]:
        """Retrieve BGP routing table"""
        if not self.connection:
            raise Exception(f"Not connected to router {self.router_id} ({self.location})")
        
        try:
            # Get BGP table output
            bgp_output = self.connection.send_command("show ip bgp", use_textfsm=True)
            return bgp_output
        except Exception as e:
            raise Exception(f"Failed to retrieve BGP table from {self.router_id} ({self.location}): {str(e)}")

    def disconnect(self) -> None:
        """Close the connection to the router"""
        if self.connection:
            self.connection.disconnect()

def main():
    from dotenv import load_dotenv
    from bgp_visualizer import BGPVisualizer
    load_dotenv()

    # Initialize router configuration and visualizer
    router_config = RouterConfig()
    visualizer = BGPVisualizer()
    
    # Process BGP tables from all routers
    for router_id, config in router_config.get_all_routers().items():
        router = RouterConnection(router_id, config)
        try:
            print(f"\nConnecting to {router_id} ({router.location})...")
            router.connect()
            bgp_table = router.get_bgp_table()
            
            # Get local AS number from router
            local_as = router.connection.send_command("show run | include router bgp").split()[-1]
            
            # Create visualization
            visualizer.process_bgp_table(bgp_table, local_as)
            plt = visualizer.create_graph(f"BGP Network Topology - {router.location}")
            
            # Save the graph
            plt.savefig(f"bgp_topology_{router_id}.png")
            plt.close()
            
            print(f"BGP topology for {router_id} has been saved as bgp_topology_{router_id}.png")
            
        except Exception as e:
            print(f"Error with router {router_id}: {str(e)}")
        finally:
            router.disconnect()
    
    try:
        router.connect()
        bgp_table = router.get_bgp_table()
        print(json.dumps(bgp_table, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        router.disconnect()

if __name__ == "__main__":
    main()