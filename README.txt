🏘️ Israel Housing Market Dashboard
An interactive analytical platform to track and analyze trends in the Israeli housing market. This dashboard cross-references housing price indices with key macroeconomic indicators, such as Bank of Israel interest rates, and tracks the impact of historical national events.
________________
✨ Key Features
* 📊 Market Overview: A high-level snapshot of current market conditions with key indicators.
* 🏦 Macro Analysis: Correlation studies between Bank of Israel interest rates and housing price movements.
* ⚡ Event Analysis: Comparative tools to assess market performance before and after significant national events.
* 🔍 Advanced Filters: Customizable date ranges and category filtering for focused analysis.
* 💡 Business Insights: Analytical conclusions on market resilience, "pent-up demand," and interest rate lag effects.
⚙️ Technology Stack
* Python: Primary programming language.
* Streamlit: Interactive web application framework.
* Pandas: ETL processing and data manipulation.
* Plotly: Dynamic and responsive data visualization.
🔧 ETL Pipeline
Data flows through a structured, reproducible pipeline:
1. Extract: Automated data retrieval via the Israel Central Bureau of Statistics (CBS) API.
2. Transform: Data cleaning, type conversion, normalization, and feature engineering (e.g., annual change calculation, interest rate shifts).
3. Load, Analyze & Version Control: Integration into the interactive dashboard with source code managed via GitHub.
🚀 Getting Started
To run this dashboard locally, follow these steps:
1. Clone the repository:
  git clone https://github.com/YourUsername/Israel-Housing-Dashboard.git
  cd Israel-Housing-Dashboard

2. Install dependencies:
  pip install -r requirements.txt

3. Run the application:
  streamlit run app.py

📈 Data Sources
All housing market data is sourced from the Israel Central Bureau of Statistics (CBS).
________________
Developed by Ido Hazan.