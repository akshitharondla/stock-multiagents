import os
import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

# Load environment variables
load_dotenv()

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# 1) Identify ticker subagent 
identify_ticker = LlmAgent(
    name="IdentifyTicker",
    description="Extracts stock ticker symbol from user query.",
    instruction="Identify the stock ticker symbol from user query."
)

# 2) Fetch recent news about the ticker using NewsAPI
def fetch_news(ticker):
    url = (
        f"https://newsapi.org/v2/everything?q={ticker}&"
        f"sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if not articles:
            return "No recent news found."
        summaries = [f"- {art['title']} ({art['source']['name']})" for art in articles]
        return "\n".join(summaries)
    else:
        return "Failed to fetch news."

ticker_news = LlmAgent(
    name="TickerNews",
    description="Retrieves recent news about the stock ticker.",
    instruction="Use fetch_news to get latest news."
)

# 3) Fetch current price using Alpha Vantage
def fetch_current_price_alpha(ticker):
    url = (
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}"
        f"&apikey={ALPHAVANTAGE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    try:
        price = data["Global Quote"]["05. price"]
        return float(price)
    except (KeyError, ValueError):
        return None

ticker_price = LlmAgent(
    name="TickerPrice",
    description="Gets current stock price.",
    instruction="Use fetch_current_price_alpha to get price."
)

# 4) Calculate price change using Alpha Vantage daily time series
def price_change_alpha(ticker, days=7):
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}"
        f"&apikey={ALPHAVANTAGE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    try:
        time_series = data["Time Series (Daily)"]
        dates = sorted(time_series.keys(), reverse=True)
        latest = float(time_series[dates[0]]["4. close"])
        if len(dates) > days:
            past = float(time_series[dates[days]]["4. close"])
        else:
            past = float(time_series[dates[-1]]["4. close"])
        change = latest - past
        pct_change = (change / past) * 100
        return f"Price changed by ${change:.2f} ({pct_change:.2f}%) over last {days} days."
    except (KeyError, IndexError, ValueError):
        return "Not enough data to calculate price change."

ticker_price_change = LlmAgent(
    name="TickerPriceChange",
    description="Calculates price change over timeframe.",
    instruction="Use price_change_alpha to compute price movement."
)

# 5) Analyze price movement based on news and price change
def analyze_movement(ticker):
    news_summary = fetch_news(ticker)
    change_summary = price_change_alpha(ticker, days=7)
    analysis = (
        f"Analysis for {ticker}:\n{news_summary}\n\n"
        f"Price movement summary:\n{change_summary}\n\n"
        "Analysis: Recent news likely influenced the stock's price changes."
    )
    return analysis

ticker_analysis = LlmAgent(
    name="TickerAnalysis",
    description="Analyzes stock price movements using news and price data.",
    instruction="Use analyze_movement to generate a summary."
)

# Full pipeline orchestration (mock)
stock_query_pipeline = SequentialAgent(
    name="StockQueryPipeline",
    sub_agents=[
        identify_ticker,
        ticker_news,
        ticker_price,
        ticker_price_change,
        ticker_analysis
    ]
)

# Demo runner (mock ticker extraction + calls)
def run_stock_query(query):
    ticker_map = {"tesla": "TSLA", "apple": "AAPL", "google": "GOOGL", "amazon": "AMZN"}
    ticker = None
    for name, symbol in ticker_map.items():
        if name in query.lower():
            ticker = symbol
            break
    if not ticker:
        print("Could not identify a stock ticker in your query.")
        return

    print(f"IDENTIFIED TICKER: {ticker}")

    news = fetch_news(ticker)
    print("\nTICKER NEWS:")
    print(news)

    price = fetch_current_price_alpha(ticker)
    print(f"\nTICKER PRICE OF {ticker}: ${price}")

    change = price_change_alpha(ticker)
    print(f"\nTICKER PRICE CHANGE :")
    print(change)

    analysis = analyze_movement(ticker)
    print("\nTICKER ANALYSIS:")
    print(analysis)

if __name__ == "__main__":
    print("Enter your stock-related question:")
    user_query = input("> ")
    run_stock_query(user_query)
