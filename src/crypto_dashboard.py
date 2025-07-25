import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

ordered_risk_labels = [
        "Low Risk / High Market Cap / Low Return",
        "Low Risk / Low Liquidity / Low Return / Outlier Spread",
        "Medium Risk / Mod Volatility / Negative Return",
        "Medium-High Risk / High Volatility / Positive Return",
        "High Risk / High Volatility / Strong Positive Return",
        "High Risk / Microcap Movers / Spiky Volume"
    ]

# --- Load Data ---
risk_df = pd.read_csv('risk_df.csv', parse_dates=['end_date'])

# Ensure correct types
risk_df['risk_label'] = risk_df['risk_label'].astype(str)
risk_df['risk_cluster'] = risk_df['risk_cluster'].astype(str)

# Sidebar filters
st.sidebar.title("Filters")

coins = risk_df['coin'].unique()
selected_coins = st.sidebar.multiselect("Select Coins", options=sorted(coins), default=sorted(coins)[:5])

min_date = risk_df['end_date'].min()
max_date = risk_df['end_date'].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter Data
filtered_df = risk_df[
    (risk_df['coin'].isin(selected_coins)) &
    (risk_df['end_date'] >= pd.to_datetime(selected_dates[0])) &
    (risk_df['end_date'] <= pd.to_datetime(selected_dates[1]))
]

# Title
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

# --- Existing Dominant Cluster and Cluster Transition tables side by side ---
# Cluster Consistency as % of Time in Dominant Cluster
cluster_counts = filtered_df.groupby(['coin', 'risk_label']).size().reset_index(name='count')
total_counts = filtered_df.groupby('coin').size().reset_index(name='total')
cluster_counts = cluster_counts.merge(total_counts, on='coin')
cluster_counts['percentage'] = cluster_counts['count'] / cluster_counts['total']
dominant_cluster = (
    cluster_counts.sort_values(['coin', 'percentage'], ascending=[True, False])
    .drop_duplicates('coin')
    .reset_index(drop=True)
    .rename(columns={'risk_label': 'dominant_risk_label', 'percentage': 'dominant_cluster_pct'})
)
dominant_cluster['dominant_cluster_pct'] = (dominant_cluster['dominant_cluster_pct'] * 100).round(2)
dominant_cluster = dominant_cluster.sort_values(by='count', ascending=False)
dominant_cluster_display = dominant_cluster.drop(columns=['count'])

# Cluster Transitions (Time Stability)
coin_cluster_changes = (
    filtered_df.sort_values(['coin', 'end_date'])
    .groupby('coin')['risk_cluster']
    .apply(lambda x: (x != x.shift()).sum() - 1)
    .reset_index(name='cluster_transitions')
    .sort_values(by='cluster_transitions', ascending=False)
)

st.subheader("Cluster Consistency & Transition Metrics")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Dominant Cluster per Coin (% of Time)**")
    st.dataframe(dominant_cluster_display.style.format({'dominant_cluster_pct': '{:.2f}%'}))
with col2:
    st.markdown("**Cluster Transition Counts per Coin (Time Stability)**")
    st.dataframe(coin_cluster_changes)

# Filter those tables by selected coins
dominant_filtered = dominant_cluster_display[dominant_cluster_display['coin'].isin(selected_coins)]
transitions_filtered = coin_cluster_changes[coin_cluster_changes['coin'].isin(selected_coins)]


# --- Risk Cluster Timeline + Price Chart ---
def plot_multi_coin_risk_timelines_with_price(df, coins):
    
    y_positions = list(range(len(ordered_risk_labels)))
    label_to_y = dict(zip(ordered_risk_labels, y_positions))

    for coin in coins:
        coin_data = df[df['coin'] == coin].sort_values('end_date')

        st.markdown(f"### {coin}")
        col1, col2 = st.columns([1,1])

        # Risk Cluster Timeline
        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))  # increased height for parity with price
            y_vals = coin_data['risk_label'].map(label_to_y)
            ax.scatter(
                coin_data['end_date'], y_vals,
                c=coin_data['color'], s=60, edgecolor='black'
            )
            ax.set_yticks(y_positions)
            ax.set_yticklabels(ordered_risk_labels)
            ax.set_title("Risk Cluster Timeline")
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True)
            st.pyplot(fig)

        # Closing Price Chart with dots at each point
        with col2:
            if 'close' in coin_data.columns:
                fig_price = px.line(
                    coin_data,
                    x='end_date',
                    y='close',
                    title="Closing Price",
                    labels={'end_date': 'Date', 'close': 'Price'},
                )
                fig_price.update_traces(mode='lines+markers', marker=dict(symbol='circle', size=6))
                fig_price.update_layout(height=500, margin=dict(l=10, r=10, t=30, b=10))
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

# --- Cluster Distribution Over Time ---
st.subheader("Cluster Distribution Over Time")

dist_df = filtered_df.groupby(['end_date', 'risk_label']).size().reset_index(name='count')
total_per_date = dist_df.groupby('end_date')['count'].transform('sum')
dist_df['pct'] = dist_df['count'] / total_per_date

fig_dist = px.area(
    dist_df,
    x='end_date',
    y='pct',
    color='risk_label',
    category_orders={"risk_label": ordered_risk_labels},
    labels={'pct': 'Proportion', 'end_date': 'Date', 'risk_label': 'Risk Cluster'},
    title='Proportion of Coins in Each Risk Cluster Over Time'
)
st.plotly_chart(fig_dist, use_container_width=True)

# --- Volatility vs Return Scatterplot by Cluster ---
st.subheader("Volatility vs Return by Cluster")
scatter_df = filtered_df.copy()
fig_scatter = px.scatter(
    scatter_df,
    x='volatility',
    y='avg_return',
    color='risk_label',
    hover_data=['coin', 'end_date'],
    category_orders={"risk_label": ordered_risk_labels},
    labels={'volatility': 'Volatility', 'avg_return': 'Average Return', 'risk_label': 'Risk Cluster'},
    title='Volatility vs Average Return'
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- Correlation Heatmap ---
st.subheader("Feature Correlation Heatmap")

corr_features = ['volatility', 'avg_spread', 'avg_volume_volatility', 'avg_rsi', 'avg_atr', 'avg_return', 'market_beta']
corr_df = filtered_df[corr_features]
corr_matrix = corr_df.corr()

fig_corr, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
st.pyplot(fig_corr)

