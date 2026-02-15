import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from GitHub Pages frontend


def run_load_balancer(choice):


    # ----- STEP 2: Create servers based on choice -----

    servers = []  # Empty list to store our servers

    if choice == "horizontal":
        # ----- HORIZONTAL SCALING -----
        # Add MORE servers (6 servers instead of 4)
        # Each server still handles 2 requests
        capacity = 2  # Each server handles 2 requests
        
        # Create 6 servers
        for i in range(6):
            server = {"name": f"Server-{i}", "requests": [], "max_capacity": capacity}
            servers.append(server)

    else:
        capacity = 3  # Each server now handles 3 requests (upgraded!)
        
        # Create 4 servers
        for i in range(4):
            server = {"name": f"Server-{i}", "requests": [], "max_capacity": capacity}
            servers.append(server)


    # ----- STEP 3: Show our servers -----

    N = len(servers)  # Total number of servers

    # ----- STEP 4: Define our 10 requests -----

    requests_list = [
        "Request_A",
        "Request_B", 
        "Request_C",
        "Request_D",
        "Request_E",
        "Request_F",
        "Request_G",
        "Request_H",
        "Request_I",
        "Request_J"
    ]


    # ----- STEP 5: Function to assign request with RETRY -----
    # If a server is full, we try another server by adding a suffix and rehashing

    def assign_request(request_name):
        attempt = 0  # Count how many times we tried
        
        while True:
            # Create a key for hashing
            # First attempt: just use the request name
            # Later attempts: add attempt number to change the hash
            if attempt == 0:
                hash_key = request_name
            else:
                hash_key = f"{request_name}_retry{attempt}"
            
            # Calculate server index using hash
            hash_value = hash(hash_key)
            server_index = hash_value % N
            
            # Get the chosen server
            chosen_server = servers[server_index]
            
            # Check if server has space
            if len(chosen_server["requests"]) < chosen_server["max_capacity"]:
                # SUCCESS! Server has space
                chosen_server["requests"].append(request_name)
                return {
                    "request": request_name,
                    "server": chosen_server["name"],
                    "attempts": attempt + 1,
                    "status": "ACCEPTED"
                }
            else:
                # Server is full, try again with different has
                attempt += 1
                
                # Safety check: don't try forever (max 10 attempts)
                if attempt >= 10:
                    return {
                        "request": request_name,
                        "server": "NONE",
                        "attempts": attempt,
                        "status": "FAILED (all servers full)"
                    }


    results = []

    for req in requests_list:
        result = assign_request(req)
        results.append(result)


    for server in servers:
        current_load = len(server["requests"])
        max_load = server["max_capacity"]
        
        # Show a visual bar for load
        bar = "█" * current_load + "░" * (max_load - current_load)
        


    # ----- STEP 8: Summary -----

    total_accepted = sum(1 for r in results if "ACCEPTED" in r["status"])
    total_retries = sum(r["attempts"] - 1 for r in results)
    return {
    "choice": choice,
    "servers": servers,
    "results": results,
    "total_requests": len(requests_list),
    "accepted": total_accepted,
    "retries": total_retries
}


@app.route("/run", methods=["POST"])
def run():
    data = request.json
    choice = data["choice"]

    result = run_load_balancer(choice)

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
