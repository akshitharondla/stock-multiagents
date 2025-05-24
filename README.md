🧠 Stock Multiagents

This project is an AI-based multi-agent system for analyzing and acting on stock market data. Each agent performs specific tasks (e.g., fetching data, analyzing trends, making predictions) in a modular and extensible way.

🚀 Features

- 📈 Stock data collection and analysis
- 🧠 Multi-agent architecture (modular and extensible)
- 🔐 Environment configuration via `.env` file
- 🐍 Built with Python
- 

🛠 Installation

1. Clone the repository
   git clone https://github.com/akshitharondla/stock-multiagents.git
   cd stock-multiagents
2. Setup a virtual environment
   python -m venv .venv
  .venv\Scripts\activate      # Windows
   source .venv/bin/activate  # macOS/Linux
3. Install dependencies
   pip install -r stock_agent/requirements.txt
4. Create a .env file inside stock_agent/
   ALPHAVANTAGE_API_KEY=your_api_key
   NEWS_API_KEY=your_api_key

USAGE

python stock_agent/agent.py

