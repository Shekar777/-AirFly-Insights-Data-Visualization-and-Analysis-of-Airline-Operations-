import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="NYC Aviation Hub Pro", layout="wide", page_icon="✈️")

@st.cache_data
def load_data():
    # Load the dataset
    df = pd.read_csv('flights_cleaned.csv')
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    # Map numbers to Day Names
    day_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    df['Day_Name'] = df['Day_of_Week'].map(day_map)
    # Prepare positive delay column for impact metrics
    df['delay_minutes_positive'] = df['arr_delay'].clip(lower=0)
    return df

df = load_data()

# --- SIDEBAR: DYNAMIC SEARCH CONTROLS ---
st.sidebar.title("🔍 Search & Filter")
st.sidebar.markdown("Configure your selection and click **Apply** to update all views.")

# 1. Select Airline
all_carriers = sorted(df['name'].unique())
selected_airline = st.sidebar.multiselect("1. Select Airlines:", all_carriers, default=all_carriers[0])

# 2. Dynamic Origin Hub (Only shows hubs relevant to selected airlines)
if selected_airline:
    relevant_origins = sorted(df[df['name'].isin(selected_airline)]['origin'].unique())
else:
    relevant_origins = sorted(df['origin'].unique())

selected_origin = st.sidebar.multiselect("2. Select Origin Hub:", relevant_origins, default=relevant_origins)

# 3. Apply Button (Inside a form to prevent accidental refreshes)
with st.sidebar.form(key='filter_form'):
    st.write("Click to confirm changes:")
    submit_button = st.form_submit_button(label='🚀 Apply Filters')

# --- DATA PROCESSING & SESSION STATE ---
# Initialize session state if it doesn't exist
if 'filtered_df' not in st.session_state:
    # Default initial view
    st.session_state['filtered_df'] = df[(df['name'].isin(selected_airline)) & (df['origin'].isin(selected_origin))]

# Update data only when button is clicked
if submit_button:
    st.session_state['filtered_df'] = df[(df['name'].isin(selected_airline)) & (df['origin'].isin(selected_origin))]

# Assign the active data for the session
work_df = st.session_state['filtered_df']

# Safety check for empty results
if work_df.empty:
    st.warning("⚠️ No data matches your current selection. Please adjust your filters in the sidebar.")
    st.stop()

# --- MAIN DASHBOARD NAVIGATION ---
app_mode = st.radio("Choose Perspective:", ["Passenger Assistant", "Infrastructure & Policy"], horizontal=True)
st.divider()

# --- VIEW 1: PASSENGER ASSISTANT ---
if app_mode == "Passenger Assistant":
    st.title("🧳 Smart Traveler Assistant")
    st.markdown("#### Maximize your travel efficiency and reliability.")
    
    # KPIs
    k1, k2, k3 = st.columns(3)
    # Find the best time safely
    time_stats = work_df.groupby('departure_period')['Arrival_Delay_Flag'].mean()
    best_time = time_stats.idxmin() if not time_stats.empty else "N/A"
    
    k1.metric("Recommended Time", best_time, help="The period with the lowest historical delay probability.")
    k2.metric("Flights Analyzed", f"{len(work_df):,}")
    k3.metric("On-Time Probability", f"{(1 - work_df['Arrival_Delay_Flag'].mean())*100:.1f}%")

    st.subheader("🗓️ Reliability Heatmap")
    heat_data = work_df.groupby(['Day_Name', 'departure_period'])['Arrival_Delay_Flag'].mean().reset_index()
    fig_heat = px.density_heatmap(heat_data, x="departure_period", y="Day_Name", z="Arrival_Delay_Flag",
                                 category_orders={"Day_Name": ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], 
                                                  "departure_period": ['Morning','Afternoon','Evening','Night','Late Night']},
                                 color_continuous_scale='YlOrRd', title="Delay Risk Intensity")
    st.plotly_chart(fig_heat, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🕒 Travel Outcomes")
        st.plotly_chart(px.pie(work_df, names='Delay_Severity', hole=0.4, 
                               color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    with c2:
        st.subheader("📊 Performance by Carrier")
        avg_del = work_df.groupby('name')['arr_delay'].mean().reset_index()
        st.plotly_chart(px.bar(avg_del, x='name', y='arr_delay', color='arr_delay', 
                               color_continuous_scale='RdYlGn_r'), use_container_width=True)

# --- VIEW 2: INFRASTRUCTURE & POLICY ---
else:
    st.title("🏛️ Infrastructure & Policy Oversight")
    st.markdown("#### Strategic metrics for regional transit planning.")
    
    # Financial Controls in sidebar specifically for this view
    st.sidebar.divider()
    st.sidebar.subheader("💰 Economic Parameters")
    val_time = st.sidebar.slider("Value of Time ($/hr)", 10, 100, 35)
    pax_avg = st.sidebar.number_input("Avg Passengers/Flight", 50, 300, 150)

    # Impact Metrics
    col1, col2, col3 = st.columns(3)
    total_delay_hrs = work_df['delay_minutes_positive'].sum() / 60
    economic_loss = total_delay_hrs * pax_avg * val_time
    fuel_waste = work_df['delay_minutes_positive'].sum() * 50 / 2000 # Tons proxy

    col1.metric("Systemic Delay Burden", f"{total_delay_hrs:,.0f} hrs")
    col2.metric("Est. Economic Loss", f"${economic_loss/1e6:,.1f}M")
    col3.metric("Est. Fuel Waste", f"{fuel_waste:,.0f} Tons")

    st.divider()

    # SIMPLIFIED SCATTER PLOT
    st.subheader("🚆 Strategic Focus: Top 15 High-Volume Routes")
    st.write("Analyzing these routes helps prioritize High-Speed Rail investment over air traffic.")
    
    route_stats = work_df.groupby('Route').agg({'arr_delay':'mean', 'id':'count'}).reset_index()
    top_routes = route_stats.sort_values('id', ascending=False).head(15)
    
    fig_scatter = px.scatter(top_routes, x='id', y='arr_delay', size='id', 
                             text='Route', color='arr_delay',
                             labels={'id':'Flight Volume', 'arr_delay':'Avg Delay (min)'},
                             color_continuous_scale='Portland', size_max=40)
    fig_scatter.update_traces(textposition='top center')
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Failure Points
    st.subheader("⚠️ Operational Failure Breakdown")
    cause_data = work_df[work_df['delay_cause'] != 'On-time']['delay_cause'].value_counts().reset_index()
    st.plotly_chart(px.bar(cause_data, x='count', y='delay_cause', orientation='h', 
                           color='delay_cause', color_discrete_sequence=px.colors.qualitative.Bold), use_container_width=True)