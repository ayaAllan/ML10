import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px

# --- Load Data ---
risk_df = pd.read_csv('risk_df.csv', parse_dates=['end_date'])

# Ensure correct types
risk_df['risk_label'] = risk_df['risk_label'].astype(str)
risk_df['risk_cluster'] = risk_df['risk_cluster'].astype(str)

# --- Sidebar filters ---
st.sidebar.title("Filters")

coins = risk_df['coin'].unique()
selected_coins = st.sidebar.multiselect("Select Coins", options=sorted(coins), default=sorted(coins)[:5])

min_date = risk_df['end_date'].min()
max_date = risk_df['end_date'].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

risk_categories = sorted(risk_df['risk_label'].unique())
selected_risk_cats = st.sidebar.multiselect("Select Risk Categories", options=risk_categories, default=risk_categories)

# --- Filter Data ---
filtered_df = risk_df[
    (risk_df['coin'].isin(selected_coins)) &
    (risk_df['end_date'] >= pd.to_datetime(selected_dates[0])) &
    (risk_df['end_date'] <= pd.to_datetime(selected_dates[1])) &
    (risk_df['risk_label'].isin(selected_risk_cats))
]

# --- Dashboard Title ---
st.title("Crypto Risk Cluster Dashboard")

# --- Summary KPIs ---
st.subheader("Summary Statistics")

total_coins = filtered_df['coin'].nunique()
total_obs = filtered_df.shape[0]
avg_volatility = filtered_df['volatility'].mean()
avg_return = filtered_df['avg_return'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Coins Selected", total_coins)
col2.metric("Observations", total_obs)
col3.metric("Avg Volatility", f"{avg_volatility:.4f}")
col4.metric("Avg Return", f"{avg_return:.4f}")

# --- Risk Cluster Timeline + Price Chart ---
def plot_multi_coin_risk_timelines_with_price(df, coins):
    y_to_risk_label = df[['risk_label_y', 'risk_label', 'color']].drop_duplicates().sort_values('risk_label_y')
    y_positions = y_to_risk_label['risk_label_y'].astype(int).tolist()
    y_labels = y_to_risk_label['risk_label'].tolist()
    label_to_y = dict(zip(y_labels, y_positions))

    for coin in coins:
        coin_data = df[df['coin'] == coin].sort_values('end_date')

        st.markdown(f"### {coin}")
        col1, col2 = st.columns(2)

        # --- Risk Cluster Timeline ---
        with col1:
            fig, ax = plt.subplots(figsize=(6, 3))
            y_vals = coin_data['risk_label'].map(label_to_y)
            ax.scatter(
                coin_data['end_date'], y_vals,
                c=coin_data['color'], s=60, edgecolor='black'
            )
            ax.set_yticks(y_positions)
            ax.set_yticklabels(y_labels)
            ax.set_title("Risk Cluster Timeline")
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True)
            st.pyplot(fig)

        # --- Closing Price Chart ---
        with col2:
            if 'close' in coin_data.columns:
                fig_price = px.line(
                    coin_data,
                    x='end_date',
                    y='close',
                    title="Closing Price",
                    labels={'end_date': 'Date', 'close': 'Price'},
                )
                fig_price.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_price, use_container_width=True)
            else:
                st.warning("Column `close` not found for price chart.")

# Call the combined timeline and price plot
if selected_coins:
    st.subheader("Risk Cluster & Price Timelines")
    plot_multi_coin_risk_timelines_with_price(filtered_df, selected_coins)
else:
    st.info("Please select at least one coin.")

# --- Cluster Performance Table ---
def calculate_risk_cluster_stats(df):
    grouped = df.groupby('risk_label')
    stats = grouped.agg({
        'avg_return': ['mean', 'std'],
        'volatility': 'mean',
        'coin': 'count'
    })
    stats.columns = ['avg_return_mean', 'avg_return_std', 'volatility_mean', 'n_obs']
    stats['sharpe'] = stats['avg_return_mean'] / stats['avg_return_std']
    win_rates = (
        df[df['avg_return'] > 0]
        .groupby('risk_label')['avg_return']
        .count() / grouped['avg_return'].count()
    )
    stats['win_rate'] = win_rates.fillna(0)
    return stats.sort_values('sharpe', ascending=False)

cluster_stats = calculate_risk_cluster_stats(filtered_df)

st.subheader("Cluster Performance Stats")
st.dataframe(cluster_stats.style.format({
    'avg_return_mean': '{:.4f}',
    'avg_return_std': '{:.4f}',
    'volatility_mean': '{:.4f}',
    'sharpe': '{:.4f}',
    'win_rate': '{:.2%}'
}))

fig_perf = plt.figure(figsize=(8, 4))
plt.barh(cluster_stats.index.astype(str), cluster_stats['sharpe'], color='teal')
plt.xlabel('Sharpe Ratio')
plt.title('Sharpe Ratio by Risk Cluster')
plt.grid(axis='x', linestyle='--', alpha=0.6)
st.pyplot(fig_perf)

# --- PCA Plot ---
if 'pca_1' in risk_df.columns and 'pca_2' in risk_df.columns:
    st.subheader("PCA Visualization of Clusters")
    pca_filtered = filtered_df.copy()
    fig_pca = px.scatter(
        pca_filtered,
        x='pca_1',
        y='pca_2',
        color='risk_label',
        hover_data=['coin', 'end_date'],
        title="PCA of Crypto Features Colored by Risk Cluster",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig_pca, use_container_width=True)
else:
    st.info("PCA columns not found in risk_df.")