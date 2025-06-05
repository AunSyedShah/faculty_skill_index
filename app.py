import streamlit as st
import json
import pandas as pd

# Set Streamlit to use full screen width
st.set_page_config(layout="wide")

# Load the JSON data
with open("faculty_module_status.json", "r", encoding="utf-8") as f:
    faculty_data = json.load(f)

# Convert nested dictionary to DataFrame
df = pd.DataFrame.from_dict(faculty_data, orient='index')
df.reset_index(inplace=True)
df = df.rename(columns={'index': 'Faculty'})

# Title
st.title("Faculty Module Approval Status")

# Search bar
faculty_search = st.text_input("Search Faculty Name")

# Status filter
status_filter = st.multiselect(
    "Filter by Status",
    options=["Approved", "Pending", "Not Approved", "Unknown"],
    default=["Approved", "Pending", "Not Approved", "Unknown"]
)

# Filter faculty name
filtered_df = df[df["Faculty"].str.contains(faculty_search, case=False, na=False)].copy()

# Apply status filter to all module columns (excluding Faculty name)
for col in filtered_df.columns[1:]:
    filtered_df[col] = filtered_df[col].apply(lambda x: x if x in status_filter else None)

# Define a color highlighting function
def highlight_status(val):
    color_map = {
        "Approved": "#b6fcb6",       # Light green
        "Pending": "#fff7aa",        # Light yellow
        "Not Approved": "#fcb6b6",   # Light red
        "Unknown": "#dddddd"         # Light gray
    }
    return f"background-color: {color_map.get(val, '#ffffff')}"

# Apply the styling
styled_df = filtered_df.style.applymap(highlight_status, subset=filtered_df.columns[1:])

# Display styled dataframe
st.dataframe(styled_df, use_container_width=True, height=600)
