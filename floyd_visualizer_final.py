import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import time

# --- 1. PAGE CONFIGURATION & ANIMATED CSS ---
st.set_page_config(page_title="Neon Floyd-Warshall", layout="wide", initial_sidebar_state="collapsed")

# Injecting CSS for Cyber Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&display=swap');

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

    /* Highlighted Problem Statement Header */
    .problem-header {
        background: linear-gradient(135deg, #ff0844 0%, #ff4b2b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px rgba(255, 8, 68, 0.4);
    }

    /* Interactive Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #ff0844 0%, #ff4b2b 100%);
        border: none;
        color: white !important;
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

# --- 2. PROBLEM STATEMENT ---
st.markdown("<h1 class='problem-header'>🚨 Problem Statement: Disaster Relief Routing</h1>", unsafe_allow_html=True)
st.write("""
**Scenario:** A severe seismic event has fractured the region's primary transit grid. Emergency responders must navigate a chaotic, heavily damaged network of roads to deliver medical supplies, dispatch rescue units, and establish evacuation corridors. Some routes are completely destroyed, while others have severely delayed transit times.

**The Challenge:** Traditional point-to-point routing algorithms are insufficient during a crisis because command centers need to evaluate multiple origin and destination points simultaneously. We need a global, omnidirectional workflow that maps out the transit times between *every* hospital, shelter, and hazard zone concurrently. 

**The Objective:** Design and implement a robust algorithmic workflow utilizing the **Floyd-Warshall matrix**. This interface serves as the initial prototype for technical review, demonstrating how the algorithm acts as an optimal routing engine—calculating all-pairs shortest paths so emergency dispatchers can instantly route units from any secure node to any critical destination.
""")

st.markdown("---")

# --- 3. SECTION 1: HERO & CORE THEORY ---
st.title("⚡ Floyd-Warshall: Core Matrix Engine")
st.markdown(
    "<p style='font-size: 18px; color: #94a3b8;'>Dynamic Programming for All-Pairs Shortest Path Optimizations</p>",
    unsafe_allow_html=True)
st.write("")

col_hero1, col_hero2 = st.columns([1.2, 1])

with col_hero1:
    st.subheader("Algorithm Overview")
    st.write("""
    The **Floyd-Warshall algorithm** operates by testing whether routing through an intermediate node **`k`** yields a faster path between two nodes **`i`** and **`j`**.

    Unlike single-source approaches, this workflow systematically updates an $N \\times N$ distance matrix over $N$ dynamic iterations, processing every potential route concurrently to build a complete transit map.
    """)
    st.write("")

with col_hero2:
    st.subheader("Complexity Metrics")
    st.markdown("""
    - **Time Complexity:** $\\mathcal{O}(V^3)$ 
      *Triple-nested loop evaluating every pair across every intermediate node.*
    - **Space Complexity:** $\\mathcal{O}(V^2)$
      *In-place update of the $V \\times V$ adjacency matrix.*
    - **Negative Weights:** Supported ✅
      *(Crucial for mapping "gained resources" on routes, failing only if negative weight cycles exist).*
    """)

st.markdown("---")

# --- 4. SECTION 2: INTERACTIVE INPUT SECTION ---
st.title("🛠️ Configure Network Topology")
st.write(
    "Construct your own disaster transit grid. You can either use the **Input Form** below to configure specific routes, or directly click and edit the **Data Matrix**. Use `INF` for routes that are completely destroyed.")

# State management for the matrix size
num_nodes = st.slider("Select Number of Locations (Nodes)", min_value=3, max_value=8, value=4)

if 'matrix_size' not in st.session_state or st.session_state.matrix_size != num_nodes:
    # Generate default matrix populated with 'INF' and 0 on the diagonal
    default_matrix = [['INF' for _ in range(num_nodes)] for _ in range(num_nodes)]
    for i in range(num_nodes):
        default_matrix[i][i] = '0'

    # Prefill some interesting paths if size is 4 for demonstration purposes
    if num_nodes == 4:
        default_matrix[0][1] = '3'
        default_matrix[0][3] = '7'
        default_matrix[1][0] = '8'
        default_matrix[1][2] = '2'
        default_matrix[2][0] = '5'
        default_matrix[2][3] = '1'
        default_matrix[3][0] = '2'

    st.session_state.matrix_data = default_matrix
    st.session_state.matrix_size = num_nodes

st.write("")
col_form, col_matrix = st.columns([1, 1.5])

with col_form:
    st.markdown("<h3 style='font-size: 20px;'>📝 Quick Input Form</h3>", unsafe_allow_html=True)
    st.write("Target specific nodes to update their route cost.")

    c1, c2 = st.columns(2)
    with c1:
        u = st.number_input("Source Node (From)", min_value=0, max_value=num_nodes - 1, value=0, step=1)
    with c2:
        v = st.number_input("Target Node (To)", min_value=0, max_value=num_nodes - 1, value=1 if num_nodes > 1 else 0,
                            step=1)

    w = st.text_input("Transit Time / Cost", value="5", help="Enter a number, or type 'INF' if the route is broken.")

    # Button to apply form inputs
    if st.button("➕ Apply Route Update"):
        st.session_state.matrix_data[u][v] = str(w).strip().upper()
        # Safe rerun trigger compatible across Streamlit versions
        if hasattr(st, 'rerun'):
            st.rerun()
        else:
            st.experimental_rerun()

with col_matrix:
    st.markdown("<h3 style='font-size: 20px;'>📊 Direct Matrix Editor</h3>", unsafe_allow_html=True)
    st.write("Click inside any cell below to directly modify the grid.")
    # Create a DataFrame for the st.data_editor
    df_input = pd.DataFrame(st.session_state.matrix_data,
                            columns=[f"N-{i}" for i in range(num_nodes)],
                            index=[f"N-{i}" for i in range(num_nodes)])

    # The interactive data editor
    edited_df = st.data_editor(df_input, use_container_width=True)

    # Sync direct matrix edits back to session state so they aren't lost
    st.session_state.matrix_data = edited_df.values.tolist()

# Parse the dynamically updated matrix into float types for the algorithm
INF = float('inf')
custom_matrix = []
try:
    for i in range(num_nodes):
        row = []
        for j in range(num_nodes):
            val = str(st.session_state.matrix_data[i][j]).strip().upper()
            if val == 'INF' or val == 'NAN' or val == '':
                row.append(INF)
            else:
                row.append(float(val))
        custom_matrix.append(row)
except ValueError:
    st.error("⚠️ Invalid input detected! Please enter numbers or 'INF' only.")
    st.stop()

st.markdown("---")

# --- 5. ANIMATION & DASHBOARD SECTION ---
st.title("🎛️ Live Calculation Terminal")


def style_matrix(matrix, n):
    """Converts matrix to DataFrame with cyberpunk dark theme styling."""
    df = pd.DataFrame(matrix,
                      columns=[f"N-{i}" for i in range(n)],
                      index=[f"N-{i}" for i in range(n)])

    display_df = df.replace(INF, "∞")

    # Format floats to not show .0 if they are whole numbers
    # Safely handles Pandas API changes (applymap is removed in newer versions)
    format_func = lambda x: int(x) if isinstance(x, float) and x.is_integer() else x

    if hasattr(display_df, 'map'):
        display_df = display_df.map(format_func)
    else:
        display_df = display_df.applymap(format_func)

    styles = [
        dict(selector="th", props=[("font-size", "14px"), ("text-align", "center"), ("background-color", "#0f172a"),
                                   ("color", "#00f2fe"), ("border", "1px solid #1e293b")]),
        dict(selector="td", props=[("font-size", "16px"), ("text-align", "center"), ("border", "1px solid #1e293b"),
                                   ("color", "#f8fafc")]),
        dict(selector="table", props=[("width", "100%"), ("border-collapse", "collapse")])
    ]

    return display_df.style.set_table_styles(styles).set_properties(**{'background-color': '#090d16'})


def draw_graph(matrix, n, current_k=None, update_ij=None):
    """Generates a high-contrast dark mode network visualization."""
    plt.style.use('dark_background')

    G = nx.DiGraph()
    for i in range(n):
        G.add_node(i)

    for i in range(n):
        for j in range(n):
            if i != j and matrix[i][j] != INF:
                G.add_edge(i, j, weight=int(matrix[i][j]) if matrix[i][j].is_integer() else matrix[i][j])

    pos = nx.circular_layout(G)
    fig, ax = plt.subplots(figsize=(6, 4.5))

    # Transparent background matching the container
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#090d16')

    # Active node highlighted in glowing hot pink
    node_colors = ['#00f2fe'] * n
    node_edge_colors = ['#007a80'] * n
    if current_k is not None:
        node_colors[current_k] = '#ff0844'
        node_edge_colors[current_k] = '#ffb199'

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           edgecolors=node_edge_colors, linewidths=3, node_size=1100)

    labels = {i: f"N-{i}" for i in range(n)}
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


# Dashboard Columns Setup
col_graph, col_matrix = st.columns([1.2, 1])

with col_graph:
    st.markdown("<h3 style='text-align: center; font-size: 18px;'>Disaster Grid Topology</h3>", unsafe_allow_html=True)
    graph_placeholder = st.empty()
    graph_placeholder.pyplot(draw_graph(custom_matrix, num_nodes))

with col_matrix:
    st.markdown("<h3 style='text-align: center; font-size: 18px;'>Dynamic Distance Matrix</h3>", unsafe_allow_html=True)
    matrix_placeholder = st.empty()
    matrix_placeholder.markdown(style_matrix(custom_matrix, num_nodes).to_html(), unsafe_allow_html=True)
    st.write("")
    status_text = st.empty()

st.write("")

# --- 6. ANIMATION EXECUTION ---
if st.button("INITIATE ROUTING OVERRIDE (RUN ANIMATION)", use_container_width=True):
    dist = [row[:] for row in custom_matrix]

    # Track if any optimizations actually happened
    optimizations_found = False

    for k in range(num_nodes):
        for i in range(num_nodes):
            for j in range(num_nodes):

                if dist[i][k] != INF and dist[k][j] != INF and dist[i][k] + dist[k][j] < dist[i][j]:
                    optimizations_found = True
                    old_dist = dist[i][j]
                    dist[i][j] = dist[i][k] + dist[k][j]

                    old_val_str = "∞" if old_dist == INF else str(old_dist)

                    # Format for display (removes .0 if whole number)
                    new_val_display = int(dist[i][j]) if float(dist[i][j]).is_integer() else dist[i][j]

                    status_text.info(
                        f"**Optimization:** Routing via Node **N-{k}** bridges **N-{i}** ➔ **N-{j}**.\nTransit cost reduced from **{old_val_str}** to **{new_val_display}**.")

                    # Redraw Visuals
                    fig = draw_graph(dist, num_nodes, current_k=k, update_ij=(i, j))
                    graph_placeholder.pyplot(fig)
                    matrix_placeholder.markdown(style_matrix(dist, num_nodes).to_html(), unsafe_allow_html=True)

                    time.sleep(1.2)  # Animation speed

    # Final Redraw (removes colored highlights)
    fig = draw_graph(dist, num_nodes)
    graph_placeholder.pyplot(fig)
    matrix_placeholder.markdown(style_matrix(dist, num_nodes).to_html(), unsafe_allow_html=True)

    # Check for negative weight cycles
    negative_cycle = any(dist[i][i] < 0 for i in range(num_nodes))

    if negative_cycle:
        status_text.error(
            "🚨 CRITICAL ALERT: Negative weight cycle detected! The routing grid contains an infinite feedback loop.")
    elif not optimizations_found:
        status_text.warning(
            "SYSTEM ONLINE: Routing scan complete. The inputted grid was already fully optimized; no faster alternative routes were found.")
    else:
        status_text.success("✅ SYSTEM ONLINE: All emergency optimal routes successfully mapped.")
        st.balloons()

    # --- 7. FINAL OUTPUT SECTION ---
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #00ffcc;'>🏁 Final Output: Optimized Shortest Path Matrix</h2>",
                unsafe_allow_html=True)
    st.write(
        "Below is the completed **All-Pairs Shortest Path Matrix**. You can use this matrix to instantly look up the absolute fastest transit time from any source row to any destination column.")

    # Render final matrix in a centered layout
    col_empty1, col_final, col_empty3 = st.columns([1, 2, 1])
    with col_final:
        st.markdown(style_matrix(dist, num_nodes).to_html(), unsafe_allow_html=True)
