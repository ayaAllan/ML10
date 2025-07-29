# Cluster Cryptos by Behavior

## Project Overview
This project aims to analyze and group cryptocurrencies based on their historical price behavior using clustering techniques. The objective is to discover hidden structure in the crypto market and provide insights into how different coins behave relative to one another over time.

By clustering coins based on key performance metrics like volatility, return, and correlation with Bitcoin, we aim to identify behavioral groupings such as high-volatility coins, stable performers, or Bitcoin-following coins. These insights may help investors, analysts, and developers better understand market dynamics, segment the market, or design targeted investment strategies.

## Business Motivation
The cryptocurrency market is known for its volatility, diversity, and lack of structure compared to traditional financial markets. Thousands of coins exist, but their behavior and investment risk profiles differ drastically.

Why this matters:

Investors often struggle to choose from a vast array of cryptos beyond Bitcoin and Ethereum.

Exchanges, funds, and portfolio managers can benefit from behavioral segmentation to create diversified portfolios.

Developers and researchers can use such clustering to study altcoin trends and market anomalies.

## Dataset
We use the All Crypto Currencies dataset from Kaggle provided by [JesseVent](https://www.kaggle.com/datasets/jessevent/all-crypto-currencies).

### Dataset Highlights

* Daily market data for thousands of cryptocurrencies from:
    * Earliest date: **2013-04-28**
    * Latest date: **2018-11-30**

* There are **13 Features** available:

    * **slug** - Unique identifier for each cryptocurrency (e.g., "bitcoin", "ethereum")
    * **symbol** - Trading symbol (e.g., "BTC", "ETH")
    * **name** - Full name of the cryptocurrency (e.g., "Bitcoin", "Ethereum")
    * **date** - Trading date
    * **ranknow** - Current rank (1 to 2000+)
    * **open** - Opening price 
    * **high** - Highest price of the day 
    * **low** - Lowest price of the day 
    * **close** - Closing price 
    * **volume** - Trading volume 
    * **market** - Market capitalization (labeled as "market" not "market_cap")
    * **close_ratio** - (Close-Low)/(High-Low) - normalized position of close within daily range
    * **spread** - USD difference between high and low prices

* **~1,584** unique coins across **~620,000** records.

* Initial preprocessing will include:
Filtering coins with sufficient data length (e.g., at least 180 days of trading).
* Handling missing values and low-volume/noisy coins.
* Aggregating per-coin behavioral metrics.

## Risks and Unknowns

### Data Sparsity & Inconsistency
There are instances where more than one slug/name shares the same trading symbol (e.g. webcoin and webchain share the symbol WEB). In addition, pricing information over the dataset timeframe is not consistent so either incomplete or coins have stopped trading.

Many altcoins are inactive, short-lived, or sparsely traded. Filtering appropriate coins will be essential.

### Time-Dependency of Features
Behavior can change over time. We'll explore using fixed windows (e.g., past 6 months) vs. full-history aggregates.

### Labeling & Validation
Unsupervised learning lacks ground truth. Lack of clarity in interpreting clusters and assessment performance.

## Techniques and Technologies
    * -Data stored in .csv formats and code stored in jupyter notebooks
    * -Python libraries used include: pandas, numpy, scikit-learn, matplotlib, seaborn, streamlit and plotly
    * -The k-Nearest Neighbors (KNN) algorithm selected from testing to group coins based on similar risk profiles

## Instructions & Key Findings

### KNN 30 Day Risk Profile Model
    * -Excute all cells in '/data/data_exploration.ipynb' which will process the raw dataset 'crypto-markets.csv' and output 'crypto-markets-processed.csv' which will be used for clustering.
    * -Execute all cells in 'src/knn_30day_risk_profile.ipynb' which will run the model, cluster the data and output performance metrics. It will also output 'risk_df.csv' which will be used as source data for the dashboard.
    * -To run the dashboard you must have streamlit installed in an appropriate environment: 'pip install streamlit'. To run the dashboard enter the following in bash terminal: 'streamlit run crypto_dashboard.py'

Coins can be seperated into 3 clusters based on traditional definitions of low, medium and high risk. Further clustering can be completed which seperates coins within these traditional categories based on certain key metrics such as volatility, market cap or returns. Three different methods were employed to optimize the hyperparameter k (number of clusters). The elbow (inertia) method measures within cluster compactness (how close points are to centroid) gives a k of 6. The silhouette score measures how well seperated the clusters are (reduces overlap and keeps them distinct) and highest score found is when k = 2. A hierarchical cluster (dendogram) shows us the split at different levels. Drawing a line at natural split points that maximize gaps between merges gives a k of 5 or 6. Ultimately we landed on optimzal k = 6.

To validate clusters, coins of known categories such as stable coins (Tether, USDC, Dai), layer-1 coins (Bitcoin, Ethereum, Cardano), DeFi coins (Compound Coin), and meme coins (Dogecoin, Pepe Cash) were reviewed to ensure they fell into expected buckets at expected times over their respective histories. For example certain coins like dogecoin, despite well known meme status, remained stable with little price volatility for years before having brief explosive meme status. Other stable coins like Tether behave as expected by not moving over time from their given label. The dashboard allows to explore individual coins of interest or make comparisons for the purposes of portfolio construction in alignment with risk tolerance or appetite.

The 'Average Return Over Time by Cluster Risk' graph provides insight that coins that are and remain sticky within the 'medium-high risk / high-volatility / positive return' provides the best risk-adjusted returns. However, this still comes with huge risks that typical retail investors may not be accustomed to.

## Individual Reflection Videos
   * **Xavier** - https://drive.google.com/file/d/1rhqMPu9IOVWo8FRuPL73OfLpTkzVqAxB/view?usp=drive_link
   * **Anitha** - - [Anitha Aravindaraman – Video Reflection](https://www.loom.com/share/8327044924c944a5ae3fe9b3a235601c?sid=5439185c-70bd-4bd6-9680-17ccf780e931)
   * **Tom** - [Tom Varghese Konikkara](https://drive.google.com/file/d/1K5OrcqOREWThcJpAXQm-6_98Qn9KwFVf/view?usp=drivesdk)
   * **Puneet** -
   * **Aya** - 
