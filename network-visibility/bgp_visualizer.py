import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict
from collections import defaultdict

class BGPVisualizer:
    def __init__(self):
        self.G = nx.DiGraph()
        self.as_prefixes = defaultdict(list)

    def process_bgp_table(self, bgp_table: List[Dict], local_as: str):
        """Process BGP table and create graph data"""
        self.G.clear()
        self.as_prefixes.clear()
        
        # Add local AS
        self.G.add_node(f"AS{local_as}", node_type="local")
        
        for route in bgp_table:
            as_path = route.get('as_path', '').split()
            prefix = route.get('network', '')
            
            if as_path:
                # Add the prefix to the last AS in path (originating AS)
                self.as_prefixes[as_path[-1]].append(prefix)
                
                # Create edges between ASes in the path
                for i in range(len(as_path) - 1):
                    self.G.add_edge(f"AS{as_path[i]}", f"AS{as_path[i+1]}")
                
                # Connect local AS to first AS in path
                if as_path:
                    self.G.add_edge(f"AS{local_as}", f"AS{as_path[0]}")

    def create_graph(self, title: str = "BGP Network Topology"):
        """Create and display the BGP network graph"""
        plt.figure(figsize=(15, 10))
        
        # Create layout
        pos = nx.spring_layout(self.G, k=1, iterations=50)
        
        # Draw the graph
        nx.draw(self.G, pos, 
                node_color='lightblue',
                node_size=2000,
                arrows=True,
                with_labels=True,
                font_size=8,
                font_weight='bold')
        
        # Add prefixes as labels
        prefix_labels = {}
        for node in self.G.nodes():
            as_number = node.replace('AS', '')
            prefixes = self.as_prefixes.get(as_number, [])
            prefix_labels[node] = f"{node}\n" + "\n".join(prefixes[:3])
            if len(prefixes) > 3:
                prefix_labels[node] += f"\n...({len(prefixes)-3} more)"
                
        nx.draw_networkx_labels(self.G, pos, prefix_labels, font_size=6)
        
        plt.title(title)
        plt.axis('off')
        return plt