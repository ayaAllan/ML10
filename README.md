# ML10
📊 Cluster Cryptos by Behavior

**Project Overview**
This project aims to analyze and group cryptocurrencies based on their historical price behavior using clustering techniques. The objective is to discover hidden structure in the crypto market and provide insights into how different coins behave relative to one another over time.

By clustering coins based on key performance metrics like volatility, return, and correlation with Bitcoin, we aim to identify behavioral groupings such as high-volatility coins, stable performers, or Bitcoin-following coins. These insights may help investors, analysts, and developers better understand market dynamics, segment the market, or design targeted investment strategies.

**Business Motivation**
The cryptocurrency market is known for its volatility, diversity, and lack of structure compared to traditional financial markets. Thousands of coins exist, but their behavior and investment risk profiles differ drastically.

Why this matters:

Investors often struggle to choose from a vast array of cryptos beyond Bitcoin and Ethereum.

Exchanges, funds, and portfolio managers can benefit from behavioral segmentation to create diversified portfolios.

Developers and researchers can use such clustering to study altcoin trends and market anomalies.

**Dataset**
We use the All Crypto Currencies dataset from Kaggle, provided by JesseVent. **Include link**

Dataset Highlights:

Daily market data for thousands of cryptocurrencies from ???.

Features include: open, high, low, close, volume, market_cap, and rank per coin per day verify???.

~1,600 unique coins across ~620,000 records. verify ????

Initial preprocessing will include:

Filtering coins with sufficient data length (e.g., at least 180 days of trading).

Handling missing values and low-volume/noisy coins.

Aggregating per-coin behavioral metrics (TBD).

**Risks and Unknowns**
Data Sparsity & Inconsistency
Many altcoins are inactive, short-lived, or sparsely traded. Filtering appropriate coins will be essential.

Time-Dependency of Features
Behavior can change over time. We'll explore using fixed windows (e.g., past 6 months) vs. full-history aggregates.

Labeling & Validation
Unsupervised learning lacks ground truth. How will we interpret clusters and assessment performance?
