import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import math

# --- Constants ---
MAX_ENERGY = 100  # Maximum energy per node
TRANSMISSION_COST = 2
RECEPTION_COST = 1

# --- Utility Functions ---
def euclidean_distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def generate_nodes(num_nodes, area_size):
    positions = {i: (random.uniform(0, area_size), random.uniform(0, area_size)) for i in range(num_nodes)}
    energy = {i: MAX_ENERGY for i in range(num_nodes)}
    return positions, energy

def connect_nodes(G, positions, tx_range):
    for i in positions:
        for j in positions:
            if i != j and euclidean_distance(positions[i], positions[j]) <= tx_range:
                G.add_edge(i, j)

def simulate_routing(G, source, sink, energy, mac_protocol):
    try:
        path = nx.shortest_path(G, source=source, target=sink)
        logs = []
        for i in range(len(path)-1):
            sender = path[i]
            receiver = path[i+1]
            # MAC Protocol Logic (simple simulation)
            if mac_protocol == "CSMA":
                energy[sender] -= TRANSMISSION_COST
                energy[receiver] -= RECEPTION_COST
            elif mac_protocol == "TDMA":
                energy[sender] -= TRANSMISSION_COST // 2
                energy[receiver] -= RECEPTION_COST // 2
            logs.append(f"{sender} → {receiver}")
        return path, logs
    except nx.NetworkXNoPath:
        return None, ["No path found!"]

def draw_network(G, pos, energy, path=None):
    plt.figure(figsize=(8, 6))
    colors = [energy[n] / MAX_ENERGY for n in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=colors, cmap=plt.cm.viridis, node_size=700)
    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3.0, edge_color="red")
    plt.title("WSN Topology & Routing Path")
    st.pyplot(plt)

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🛰️ Virtual WSN Designer & Simulator")

# Sidebar controls
st.sidebar.header("⚙️ Network Settings")
num_nodes = st.sidebar.slider("Number of Nodes", 5, 50, 10)
area_size = st.sidebar.slider("Deployment Area Size", 10, 100, 50)
tx_range = st.sidebar.slider("Transmission Range", 5, 50, 20)
mac_protocol = st.sidebar.selectbox("MAC Protocol", ["CSMA", "TDMA"])
case_study = st.sidebar.selectbox("Use Case", ["Forest Monitoring", "Habitat Monitoring", "Disaster Monitoring"])

# Generate topology
positions, energy = generate_nodes(num_nodes, area_size)
G = nx.Graph()
G.add_nodes_from(positions)
connect_nodes(G, positions, tx_range)

# Choose source and sink
source = st.sidebar.selectbox("Source Node", list(G.nodes))
sink = st.sidebar.selectbox("Sink Node", list(G.nodes))

# Simulate
if st.sidebar.button("🚀 Run Simulation"):
    path, logs = simulate_routing(G, source, sink, energy, mac_protocol)
    draw_network(G, positions, energy, path)
    st.success("✅ Simulation Completed")
    st.markdown("### 🔄 Routing Path:")
    for log in logs:
        st.write(log)
else:
    draw_network(G, positions, energy)

# Display energy levels
st.markdown("### 🔋 Node Energy Levels:")
energy_display = {f"Node {k}": f"{v:.1f}%" for k, v in energy.items()}
st.json(energy_display)

# Footer
st.caption("Developed for Wireless Sensor Networks - FI1915 | Anna University")
