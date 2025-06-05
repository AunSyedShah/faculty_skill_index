import streamlit as st
import pandas as pd
from pymongo import MongoClient

# ------------------ Streamlit Configuration ------------------
st.set_page_config(layout="wide")
st.title("Faculty Module Approval Status")

# ------------------ MongoDB Connection -----------------------
MONGO_URI = "mongodb+srv://aunsyedshah:aunsyedshah@aunsyedshah.jv2le.mongodb.net/?retryWrites=true&w=majority&appName=aunsyedshah"
client = MongoClient(MONGO_URI)
db = client["faculty_training"]
collection = db["faculty_module_status"]

# ------------------ Load Data from MongoDB -------------------
documents = list(collection.find({}, {'_id': 0}))  # Exclude _id
if not documents:
    st.warning("No data found in MongoDB.")
    st.stop()

df = pd.DataFrame(documents)

# ------------------ UI Filters ------------------------------
faculty_search = st.text_input("🔍 Search Faculty Name")

status_filter = st.multiselect(
    "🎯 Filter by Status",
    options=["Approved", "Pending", "Not Approved", "Unknown"],
    default=["Approved", "Pending", "Not Approved", "Unknown"]
)

filtered_df = df[df["Faculty"].str.contains(faculty_search, case=False, na=False)].copy()

# Apply status filter (exclude Faculty column)
for col in filtered_df.columns[1:]:
    filtered_df[col] = filtered_df[col].apply(lambda x: x if x in status_filter else None)

# ------------------ Highlight Function ----------------------
def highlight_status(val):
    color_map = {
        "Approved": "#b6fcb6",       # Light green
        "Pending": "#fff7aa",        # Light yellow
        "Not Approved": "#fcb6b6",   # Light red
        "Unknown": "#dddddd"         # Light gray
    }
    return f"background-color: {color_map.get(val, '#ffffff')}"

styled_df = filtered_df.style.map(highlight_status, subset=filtered_df.columns[1:])
st.dataframe(styled_df, use_container_width=True, height=600)

# ------------------ Sidebar: Add/Delete Faculty -------------------
st.sidebar.header("🛠 Manage Faculty")

# ----- Add Faculty -----
with st.sidebar.expander("➕ Add New Faculty", expanded=False):
    new_faculty_name = st.text_input("Faculty Name")

    if new_faculty_name:
        module_status_inputs = {}
        for module in df.columns[1:]:  # Exclude "Faculty"
            module_status_inputs[module] = st.selectbox(
                f"{module}",
                options=["Approved", "Pending", "Not Approved", "Unknown"],
                key=f"add_{module}"
            )

        if st.button("Add Faculty"):
            if collection.find_one({"Faculty": new_faculty_name}):
                st.warning("Faculty already exists.")
            else:
                new_record = {"Faculty": new_faculty_name}
                new_record.update(module_status_inputs)
                collection.insert_one(new_record)
                st.success(f"Faculty '{new_faculty_name}' added successfully.")
                st.rerun()

# ----- Delete Faculty -----
with st.sidebar.expander("❌ Delete Faculty", expanded=False):
    faculty_list = [doc["Faculty"] for doc in documents]
    delete_faculty = st.selectbox("Select Faculty to Delete", faculty_list)

    if st.button("Delete Faculty"):
        collection.delete_one({"Faculty": delete_faculty})
        st.success(f"Faculty '{delete_faculty}' deleted successfully.")
        st.rerun()

# ------------------ Module Coverage Statistics ------------------
st.markdown("## 📊 Module Coverage Statistics")

total_faculty = df.shape[0]
coverage_data = []

for module in df.columns[1:]:  # Skip 'Faculty'
    approved_count = df[module].eq("Approved").sum()
    percentage = (approved_count / total_faculty) * 100
    coverage_data.append({
        "Module": module,
        "Approved Faculty": approved_count,
        "Total Faculty": total_faculty,
        "Coverage %": round(percentage, 2)
    })

coverage_df = pd.DataFrame(coverage_data)
st.dataframe(coverage_df.sort_values(by="Coverage %", ascending=False), use_container_width=True)

# Optional bar chart
with st.expander("📈 View Module Coverage Chart"):
    st.bar_chart(coverage_df.set_index("Module")["Coverage %"])
