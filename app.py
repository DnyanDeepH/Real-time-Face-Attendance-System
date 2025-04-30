import streamlit as st
import pandas as pd
import time
import os
import random
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="Face Attendance System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with darker theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --background-color: #1E1E1E;
        --text-color: #E0E0E0;
        --accent-color: #4CAF50;
        --secondary-color: #2979FF;
        --card-bg-color: #2D2D2D;
        --hover-color: #3D3D3D;
    }
    
    /* Override Streamlit's default styling */
    .reportview-container {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .main .block-container {
        background-color: var(--background-color);
        padding: 2rem;
    }
    
    h1, h2, h3, h4, h5, h6, p, div {
        color: var(--text-color);
    }
    
    /* Custom classes */
    .main-header {
        font-size: 2.8rem;
        color: var(--accent-color);
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        padding: 1rem;
        border-bottom: 2px solid var(--accent-color);
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: var(--secondary-color);
        margin-bottom: 1rem;
        border-left: 4px solid var(--secondary-color);
        padding-left: 10px;
    }
    
    .card {
        background-color: var(--card-bg-color);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.4);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--accent-color);
    }
    
    .stat-label {
        font-size: 1rem;
        color: #BBBBBB;
    }
    
    .footer {
        text-align: center;
        color: #888888;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #444444;
    }
    
    /* Table styling */
    .dataframe {
        background-color: var(--card-bg-color) !important;
    }
    
    .dataframe th {
        background-color: var(--secondary-color) !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    .dataframe td {
        background-color: var(--card-bg-color) !important;
        color: var(--text-color) !important;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: var(--accent-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #3d8b40;
        transform: scale(1.05);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background-color: var(--card-bg-color);
        color: var(--text-color);
        border: 1px solid #555555;
    }
    
    /* Selectbox */
    .stSelectbox>div>div>select {
        background-color: var(--card-bg-color);
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh the app every 5 seconds (5000 ms)
st_autorefresh(interval=5000, limit=100, key="attendance_refresh")

# Header with animation effect
st.markdown('<div class="main-header">Face Recognition Attendance System</div>', unsafe_allow_html=True)

# Current date and time
ts = time.time()
current_date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
current_time = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

# Display current date and time in a nice format with cards
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'''
    <div class="card">
        <div class="stat-label">📅 CURRENT DATE</div>
        <div class="stat-value">{current_date}</div>
    </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
    <div class="card">
        <div class="stat-label">⏰ CURRENT TIME</div>
        <div class="stat-value">{current_time}</div>
    </div>
    ''', unsafe_allow_html=True)

# Add a progress bar for visual effect
st.markdown('<div class="sub-header">System Status</div>', unsafe_allow_html=True)
progress_val = random.randint(90, 99)  # Random value for demo purposes
st.progress(progress_val/100)
st.markdown(f"<div style='text-align: center; color: #BBBBBB;'>System running at {progress_val}% efficiency</div>", unsafe_allow_html=True)

# Date selection for viewing attendance
st.markdown('<div class="sub-header">Select Date to View Attendance</div>', unsafe_allow_html=True)

# Get list of available attendance files
attendance_files = []
if os.path.exists("Attendance"):
    for file in os.listdir("Attendance"):
        if file.startswith("Attendance_") and file.endswith(".csv"):
            date_str = file.replace("Attendance_", "").replace(".csv", "")
            attendance_files.append(date_str)

# Default to current date if available, otherwise use the first available date
default_date = current_date if current_date in attendance_files else (attendance_files[0] if attendance_files else current_date)

# Date selector with a more prominent style
selected_date = st.selectbox("📆 Select Date", options=attendance_files, index=attendance_files.index(default_date) if default_date in attendance_files else 0) if attendance_files else current_date

# Load and display attendance data
try:
    file_path = f"Attendance/Attendance_{selected_date}.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        
        # Add some statistics with interactive cards
        st.markdown('<div class="sub-header">Attendance Summary</div>', unsafe_allow_html=True)
        
        # Statistics row with 3 cards
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown(f'''
            <div class="card">
                <div class="stat-label">TOTAL ENTRIES</div>
                <div class="stat-value">{len(df)}</div>
            </div>
            ''', unsafe_allow_html=True)
        with stat_col2:
            unique_people = df['NAME'].nunique() if 'NAME' in df.columns else 0
            st.markdown(f'''
            <div class="card">
                <div class="stat-label">UNIQUE PEOPLE</div>
                <div class="stat-value">{unique_people}</div>
            </div>
            ''', unsafe_allow_html=True)
        with stat_col3:
            latest_time = df['TIME'].iloc[-1] if 'TIME' in df.columns and not df.empty else "N/A"
            st.markdown(f'''
            <div class="card">
                <div class="stat-label">LATEST ENTRY</div>
                <div class="stat-value" style="font-size: 1.5rem;">{latest_time}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Main attendance table
        st.markdown('<div class="sub-header">Attendance Details</div>', unsafe_allow_html=True)
        
        # Add a search box with better styling
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_term = st.text_input("🔍 Search by Name")
        with search_col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            refresh_button = st.button("🔄 Refresh Data")
        
        if search_term:
            filtered_df = df[df['NAME'].str.contains(search_term, case=False)] if 'NAME' in df.columns else df
            st.markdown(f"<div style='color: #BBBBBB;'>Showing {len(filtered_df)} results for '{search_term}'</div>", unsafe_allow_html=True)
        else:
            filtered_df = df
        
        # Display the dataframe with improved styling
        st.dataframe(
            filtered_df.style
            .highlight_max(axis=0, color='#4CAF50')
            .set_properties(**{
                'background-color': '#2D2D2D', 
                'color': '#E0E0E0', 
                'border': '1px solid #444444',
                'font-size': '16px'
            })
            .format({'TIME': lambda x: f"{x}"}),
            use_container_width=True,
            height=400  # Fixed height for better appearance
        )
        
        # Add interactive elements - tabs for different views
        tab1, tab2 = st.tabs(["📊 Statistics", "📥 Export Options"])
        
        with tab1:
            # Show some basic statistics about the attendance
            if 'NAME' in df.columns:
                # Count attendance by name
                attendance_counts = df['NAME'].value_counts().reset_index()
                attendance_counts.columns = ['Name', 'Attendance Count']
                
                st.markdown("<div class='card'><div class='stat-label'>ATTENDANCE FREQUENCY</div></div>", unsafe_allow_html=True)
                st.bar_chart(attendance_counts.set_index('Name'))
        
        with tab2:
            # Download options
            st.markdown("<div class='card'><div class='stat-label'>EXPORT OPTIONS</div></div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                # Download button for CSV
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"attendance_{selected_date}.csv",
                    mime="text/csv"
                )
            with col2:
                # Download button for Excel (simulated)
                st.download_button(
                    label="📊 Download Excel",
                    data=csv,  # Using CSV data as placeholder
                    file_name=f"attendance_{selected_date}.csv",  # Still CSV for now
                    mime="text/csv",
                    help="Excel format would require additional libraries"
                )
    else:
        st.warning(f"No attendance data found for {selected_date}")
        
        # Create a placeholder table with better styling
        st.markdown('<div class="sub-header">Attendance Details</div>', unsafe_allow_html=True)
        st.markdown('''
        <div class="card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <div style="font-size: 1.5rem; color: #BBBBBB;">No attendance data available</div>
            <div style="font-size: 1rem; color: #888888; margin-top: 1rem;">Run the face recognition system to record attendance</div>
        </div>
        ''', unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Error loading attendance data: {e}")
    
# Footer with additional information
st.markdown('''
<div class="footer">
    <div style="margin-bottom: 0.5rem;">© 2023 Face Recognition Attendance System</div>
    <div style="font-size: 0.7rem;">Powered by OpenCV and Streamlit</div>
</div>
''', unsafe_allow_html=True)