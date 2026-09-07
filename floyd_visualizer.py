import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import time
import seaborn as sns

# --- 1. PAGE CONFIGURATION & ANIMATED CSS ---
st.set_page_config(page_title="Neon Floyd-Warshall", layout="wide", initial_sidebar_state="collapsed")

# Injecting CSS for Cyber Aesthetics (Removed the broken div wrappers)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600&display=swap');

    /* Global App Background */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a1c2e 0%, #080a12 80%);
        color: #c5c6c7;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Neon Typography */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 12px rgba(0, 242, 254, 0.3);
    }

    /* Interactive Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #ff0844 0%, #ff4b2b 100%);
        border: none;
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 18px;
        letter-spacing: 1px;
        padding: 12px 28px;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(255, 8, 68, 0.5);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        width: 100%;
    }

    .stButton>button:hover {
        box-shadow: 0 0 35px rgba(255, 8, 68, 0.9);
        transform: translateY(-3px) scale(1.01);
    }

    /* Custom Alert Styling */
    .stAlert {
        background-color: rgba(0, 242, 254, 0.08);
        border: 1px solid #00f2fe;
        color: #f1f5f9;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SECTION 1: HERO & CORE THEORY ---
st.title("⚡ Floyd-Warshall: Core Matrix Engine")
st.markdown(
    "<p style='font-size: 18px; color: #94a3b8;'>Dynamic Dynamic Programming for All-Pairs Shortest Path Optimizations</p>",
    unsafe_allow_html=True)
st.write("")

col_hero1, col_hero2 = st.columns([1.2, 1])

with col_hero1:
    st.subheader("Algorithm Overview")
    st.write("""
    The **Floyd-Warshall algorithm** operates by testing whether routing through an intermediate node **`k`** yields a faster path between two nodes **`i`** and **`j`**.

    Unlike Dijkstra's single-source approach, Floyd-Warshall systematically updates an $N \\times N$ distance matrix over $N$ dynamic iterations, processing every potential route concurrently.
    """)
    st.write("")
    st.subheader("The Matrix Recurrence Relation")
    st.latex(r"D^{(k)}[i][j] = \min \left( D^{(k-1)}[i][j], \; D^{(k-1)}[i][k] + D^{(k-1)}[k][j] \right)")

with col_hero2:
    st.subheader("Complexity Metrics")
    st.markdown("""
    - **Time Complexity:** $\\mathcal{O}(V^3)$ 
      *Triple-nested loop evaluating every pair across every intermediate node.*
    - **Space Complexity:** $\\mathcal{O}(V^2)$
      *In-place update of the $V \\times V$ adjacency matrix.*
    - **Negative Weights:** Supported ✅
      *(Fails only if negative weight cycles exist).*
    """)

st.markdown("---")

# --- 3. SECTION 2: SYSTEM APPLICATIONS ---
st.title("🛰️ Real-World System Implementations")
st.write("")

col_app1, col_app2, col_app3 = st.columns(3)

with col_app1:
    st.markdown("<h3 style='font-size: 20px;'>🌐 Network Routing</h3>", unsafe_allow_html=True)
    st.write("""
    Used in link-state routing protocols like **OSPF** and **IS-IS** to compute optimal transmission tables across interconnected server clusters and autonomous systems.
    """)

with col_app2:
    st.markdown("<h3 style='font-size: 20px;'>🗺️ Trans-GIS Systems</h3>", unsafe_allow_html=True)
    st.write("""
    Powers pre-calculated distance lookups in multi-stop logistics networks (e.g., airline matrix flight routes or fleet delivery optimization).
    """)

with col_app3:
    st.markdown("<h3 style='font-size: 20px;'>🧬 Graph Transitive Closure</h3>", unsafe_allow_html=True)
    st.write("""
    Adapted as Warshall's algorithm to determine reachability matrices in compiler dependency graphs and static security code analysis.
    """)

st.markdown("---")

# --- 4. SECTION 3: INTERACTIVE TERMINAL & GRAPH ANIMATION ---
st.title("🎛️ Live Calculation Terminal")

INF = float('inf')
NUM_NODES = 4

# Initialize default weighted directed matrix
initial_matrix = [
    [0, 3, INF, 7],
    [8, 0, 2, INF],
    [5, INF, 0, 1],
    [2, INF, INF, 0]
]


def style_matrix(matrix):
    """Converts matrix to DataFrame with cyberpunk dark theme styling."""
    df = pd.DataFrame(matrix,
                      columns=[f"N-{i}" for i in range(NUM_NODES)],
                      index=[f"N-{i}" for i in range(NUM_NODES)])

    display_df = df.replace(INF, "∞")

    styles = [
        dict(selector="th", props=[("font-size", "14px"), ("text-align", "center"), ("background-color", "#0f172a"),
                                   ("color", "#00f2fe"), ("border", "1px solid #1e293b")]),
        dict(selector="td", props=[("font-size", "16px"), ("text-align", "center"), ("border", "1px solid #1e293b"),
                                   ("color", "#f8fafc")]),
        dict(selector="table", props=[("width", "100%"), ("border-collapse", "collapse")])
    ]

    return display_df.style.set_table_styles(styles).set_properties(**{'background-color': '#090d16'})


def draw_graph(matrix, current_k=None, update_ij=None):
    """Generates a high-contrast dark mode network visualization."""
    plt.style.use('dark_background')

    G = nx.DiGraph()
    for i in range(NUM_NODES):
        G.add_node(i)

    for i in range(NUM_NODES):
        for j in range(NUM_NODES):
            if i != j and matrix[i][j] != INF:
                G.add_edge(i, j, weight=matrix[i][j])

    pos = nx.circular_layout(G)
    fig, ax = plt.subplots(figsize=(6, 4.5))

    # Transparent background matching the container
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#090d16')

    # Active node highlighted in glowing hot pink
    node_colors = ['#00f2fe'] * NUM_NODES
    node_edge_colors = ['#007a80'] * NUM_NODES
    if current_k is not None:
        node_colors[current_k] = '#ff0844'
        node_edge_colors[current_k] = '#ffb199'

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           edgecolors=node_edge_colors, linewidths=3, node_size=1100)

    labels = {i: f"N-{i}" for i in range(NUM_NODES)}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_color='#090d16', font_weight='bold', font_family='sans-serif')

    # Highlight newly discovered path in glowing bright green
    edge_colors = []
    edge_weights = []
    for u, v in G.edges():
        if update_ij and (u, v) == update_ij:
            edge_colors.append('#00ffcc')
            edge_weights.append(3.5)
        else:
            edge_colors.append('#334155')
            edge_weights.append(1.2)

    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color=edge_colors,
        width=edge_weights, arrowsize=20,
        connectionstyle='arc3, rad = 0.2'
    )

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                 label_pos=0.3, font_size=11, font_color='#e2e8f0',
                                 bbox=dict(facecolor='#090d16', edgecolor='none', alpha=0.7))

    plt.axis('off')
    return fig


# Dashboard Columns
col_graph, col_matrix = st.columns([1.2, 1])

with col_graph:
    st.markdown("<h3 style='text-align: center; font-size: 18px;'>Active Network Topology</h3>", unsafe_allow_html=True)
    graph_placeholder = st.empty()
    graph_placeholder.pyplot(draw_graph(initial_matrix))

with col_matrix:
    st.markdown("<h3 style='text-align: center; font-size: 18px;'>Dynamic Distance Matrix</h3>", unsafe_allow_html=True)
    matrix_placeholder = st.empty()
    matrix_placeholder.markdown(style_matrix(initial_matrix).to_html(), unsafe_allow_html=True)
    st.write("")
    status_text = st.empty()

st.write("")

# Animation Trigger Button
if st.button("RUN FLOYD-WARSHALL ANIMATION OVERRIDE"):
    dist = [row[:] for row in initial_matrix]

    for k in range(NUM_NODES):
        for i in range(NUM_NODES):
            for j in range(NUM_NODES):

                if dist[i][k] != INF and dist[k][j] != INF and dist[i][k] + dist[k][j] < dist[i][j]:
                    old_dist = dist[i][j]
                    dist[i][j] = dist[i][k] + dist[k][j]

                    old_val_str = "∞" if old_dist == INF else str(old_dist)
                    status_text.info(
                        f"**Optimization:** Node N-{k} bridges N-{i} ➔ N-{j}. Path reduced from {old_val_str} to **{dist[i][j]}**.")

                    fig = draw_graph(dist, current_k=k, update_ij=(i, j))
                    graph_placeholder.pyplot(fig)
                    matrix_placeholder.markdown(style_matrix(dist).to_html(), unsafe_allow_html=True)

                    time.sleep(1.4)

    status_text.success("OPTIMIZATION COMPLETE: All-pairs shortest paths rendered.")
    st.balloons()

    fig = draw_graph(dist)
    graph_placeholder.pyplot(fig)
    matrix_placeholder.markdown(style_matrix(dist).to_html(), unsafe_allow_html=True)
