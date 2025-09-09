# Network Visibility Tool

This Python tool connects to network routers and retrieves BGP routing table information.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your router configurations:
   ```
   ROUTER_CONFIG={
       "router1_id": {
           "host": "192.168.1.1",
           "username": "admin",
           "password": "password",
           "location": "Data Center 1"
       },
       "router2_id": {
           "host": "192.168.2.1",
           "username": "admin",
           "password": "password",
           "location": "Data Center 2"
       }
   }
   ```

## Usage

Run the script:
```bash
python main.py
```

The script will connect to the specified router, retrieve the BGP table, and display it in JSON format.