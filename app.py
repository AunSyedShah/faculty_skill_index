import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Set Streamlit to use full screen width
st.set_page_config(layout="wide")

# MongoDB connection
mongo_uri = "mongodb+srv://aunsyedshah:aunsyedshah@aunsyedshah.jv2le.mongodb.net/?retryWrites=true&w=majority&appName=aunsyedshah"
client = MongoClient(mongo_uri)
db = client["aptech"]
collection = db["faculty_status"]

# Load data from MongoDB
documents = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB internal _id
if not documents:
    st.error("No data found in MongoDB.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(documents)

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

# Filter by faculty name
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

# Display styled DataFrame
st.dataframe(styled_df, use_container_width=True, height=600)
