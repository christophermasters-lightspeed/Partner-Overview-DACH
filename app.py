import streamlit as st
import pandas as pd

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="DACH Integration Partner Dashboard", page_icon="🤝", layout="wide")

# ==========================================
# 2. DATA LOADING & ERROR HANDLING
# ==========================================
# REPLACE THIS URL with your published CSV link from Google Sheets
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQWmt5qh-UX63deRAlZZIlQe-elkrhUTkMgNNjxAlQ9HiWqUkanUEq9G7scOliRj3V7r-yD4xYp9yKb/pub?gid=1474258036&single=true&output=csv"

@st.cache_data(ttl=600) # Caches the data for 10 minutes to speed up the app
def load_data(url):
    """Fetches data from the Google Sheet CSV link and returns a Pandas DataFrame."""
    try:
        # Read the CSV directly from the generated URL
        df = pd.read_csv(url)
        
        # Clean up column names (strip trailing/leading spaces to avoid key errors)
        df.columns = df.columns.str.strip()
        
        # Fill empty values with an empty string for cleaner UI and filtering
        df = df.fillna("")
        
        return df
    except Exception as e:
        st.error(f"⚠️ Error loading data. Please check your Google Sheets link. Details: {e}")
        return pd.DataFrame() # Return empty dataframe on failure

# Load the dataset
raw_df = load_data(SHEET_CSV_URL)

# ==========================================
# 3. MAIN UI & DASHBOARD HEADER
# ==========================================
st.title("🤝 Partner Directory Dashboard")
st.markdown("Easily search, filter, and analyze your partner network data.")
st.divider()

if raw_df.empty:
    st.warning("No data found. Please ensure your Google Sheet is published and the URL is correct.")
    st.stop() # Stop execution if there's no data

# ==========================================
# 4. FILTERING & SEARCH UI (SIDEBAR)
# ==========================================
# Move all filters to the sidebar to keep the main view clean
st.sidebar.header("🔍 Filter Partners")

# Global Text Search Filter at the top of the sidebar
search_query = st.sidebar.text_input("Global Search (Account, Email, etc.)", "")
st.sidebar.divider()

# Define the exact columns you want to filter by
filter_columns = [
    "SF Account", "City", "Region", "Partner Growth Manager", "PDM", 
    "Status", "Tier", "Partner Industry", "Integration Products", 
    "Outbound Referral activated?", "Outbound Referral Contact Y / N", 
    "contact at Lightspeed", "Lightspeed Inbound AE", "2nd Lightspeed Inbound AE"
]

# Dictionary to store the user's selections
user_selections = {}

for col in filter_columns:
    # Only create a filter if the column actually exists in your Google Sheet
    if col in raw_df.columns:
        # Convert all to strings, handle blanks, and sort alphabetically
        unique_values = [str(x) for x in raw_df[col].unique() if str(x).strip() != ""]
        options = sorted(unique_values) # Removed "All" - empty multiselect handles this
        
        # Create the multiselect dropdown and save the choices (returns a list)
        user_selections[col] = st.sidebar.multiselect(f"{col}", options=options)

# ==========================================
# 5. APPLY FILTERS TO DATA
# ==========================================
filtered_df = raw_df.copy()

# Apply Categorical Multiselect Filters
for col, selected_val in user_selections.items():
    # If the user selected at least one option (the list is not empty)
    if len(selected_val) > 0:
        # Check if the dataframe column value is IN the list of selected options
        filtered_df = filtered_df[filtered_df[col].astype(str).isin(selected_val)]

# Apply Global Text Search Filter
if search_query:
    mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    filtered_df = filtered_df[mask]
    
# ==========================================
# 6. DISPLAY DATA
# ==========================================
st.markdown(f"**Showing {len(filtered_df)} partner(s)**")

# Streamlit's native dataframe is highly interactive. 
# It natively supports: clicking headers to sort (asc/desc), resizing columns, and scrolling.
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True, # Hides the arbitrary row numbers for a cleaner look
    height=600) # Sets a nice vertical height for the data table
