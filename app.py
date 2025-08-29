import streamlit as st
import pandas as pd
import networkx as nx
from collections import defaultdict
from io import StringIO
import time

st.set_page_config(layout="wide")
st.title("Smart Scheduler")

# --- Helper functions ---

def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return None
    required_cols = {"course_id", "course", "group", "teacher", "duration", "room_type"}
    if not required_cols.issubset(set(df.columns)):
        st.error(f"CSV missing columns: {required_cols - set(df.columns)}")
        return None
    return df

def preview(df):
    st.markdown("### Data Preview")
    st.dataframe(df.head(10))
    st.write("Columns:", ', '.join(df.columns))

def build_conflict_graph(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_node(row['course_id'], **row)
    # Conflicts: same teacher or same group
    for i, r1 in df.iterrows():
        for j, r2 in df.iterrows():
            if i >= j:
                continue
            if (r1['teacher'] == r2['teacher'] or r1['group'] == r2['group']):
                G.add_edge(r1['course_id'], r2['course_id'])
    return G

def get_time_slots():
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    hours = list(range(9, 18))  # 9AM - 5PM
    return [f"{d}_{h}" for d in days for h in hours]

def get_room_list():
    # Example: 2 rooms of each type
    return [
        {"room_id": "A", "room_type": "lecture"},
        {"room_id": "B", "room_type": "lecture"},
        {"room_id": "C", "room_type": "lab"},
        {"room_id": "D", "room_type": "lab"},
    ]

def greedy_schedule(df, G, time_slots, room_list):
    room_types = defaultdict(list)
    for room in room_list:
        room_types[room["room_type"]].append(room["room_id"])
    occupied = set()
    assignments = []
    course2slot = {}
    nodes = sorted(G.nodes, key=lambda n: G.degree[n], reverse=True)

    for cid in nodes:
        row = G.nodes[cid]
        duration = int(row["duration"])
        slots_to_try = time_slots
        found = False
        for slot in slots_to_try:
            start_idx = time_slots.index(slot)
            wanted_slots = time_slots[start_idx:start_idx+duration]
            if len(wanted_slots) < duration:
                continue
            neighbor_slots = [course2slot.get(nei) for nei in G.neighbors(cid)]
            if any(s in neighbor_slots for s in wanted_slots):
                continue
            for room_id in room_types[row["room_type"]]:
                if all((room_id, s) not in occupied for s in wanted_slots):
                    for s in wanted_slots:
                        occupied.add((room_id, s))
                    assignments.append({
                        "course_id": cid,
                        "course": row["course"],
                        "group": row["group"],
                        "teacher": row["teacher"],
                        "duration": duration,
                        "assigned_slots": wanted_slots,
                        "room": room_id,
                    })
                    for s in wanted_slots:
                        course2slot[cid] = s
                    found = True
                    break
            if found: break
        if not found:
            assignments.append({
                "course_id": cid,
                "course": row["course"],
                "group": row["group"],
                "teacher": row["teacher"],
                "duration": duration,
                "assigned_slots": [],
                "room": None,
            })
    return pd.DataFrame(assignments)

def calendar_grid(assignments_df, group=None, teacher=None):
    slots = get_time_slots()
    grid = pd.DataFrame('', index=slots, columns=["Course", "Room"])
    if group:
        df = assignments_df[assignments_df['group'] == group]
    elif teacher:
        df = assignments_df[assignments_df['teacher'] == teacher]
    else:
        df = assignments_df
    for _, row in df.iterrows():
        for slot in row['assigned_slots']:
            grid.loc[slot, "Course"] = row["course"]
            grid.loc[slot, "Room"] = row["room"]
    return grid

# --- Streamlit UI ---

uploaded = st.sidebar.file_uploader("Upload courses.csv", type="csv")

if uploaded:
    df = load_data(uploaded)

    if df is not None:
        preview(df)
        G = build_conflict_graph(df)
        st.markdown(f"**Conflict Graph:** {len(G.nodes)} courses, {len(G.edges)} edges")

        t0 = time.time()
        time_slots = get_time_slots()
        room_list = get_room_list()
        sched_df = greedy_schedule(df, G, time_slots, room_list)
        runtime = time.time() - t0

        st.success(f"Scheduling done in {runtime:.2f} seconds")
        st.dataframe(sched_df)
        st.download_button("Download Schedule CSV", sched_df.to_csv(index=False), file_name="schedule.csv")
else:
    st.info("Upload a valid courses.csv to begin.")
