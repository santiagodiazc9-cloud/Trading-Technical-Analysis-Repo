# Complete Beginner's Guide — AI Trading Agent

This guide assumes you've never done anything like this before. It walks you through every single step from zero to a working AI trading agent that analyzes the stock market and manages a paper (fake money) trading account.

**No real money is involved.** This uses Alpaca's paper trading, which gives you $100,000 of simulated money to practice with.

---

## What You're Building

You're setting up an AI agent (powered by Claude) that:
1. Scans a list of stocks every day using technical indicators (RSI, MACD, moving averages, etc.)
2. Decides whether to buy or sell based on those signals
3. Places orders on a simulated brokerage account (Alpaca paper trading)
4. Keeps a journal of every decision so it learns over time
5. Runs on a schedule — just like a real trader's day

The agent runs through **Claude Code**, which is a command-line tool that lets Claude read files, run scripts, and take actions on your computer. You tell it what to do using plain English, and it executes.

---

## Part 1: Install the Tools You Need

### 1.1 — Install VS Code

VS Code is the code editor where you'll work.

1. Go to https://code.visualstudio.com
2. Click the big blue download button
3. Open the downloaded file and follow the installer
4. Launch VS Code when it's done

### 1.2 — Install Python

Python is the programming language the helper scripts are written in.

1. Go to https://www.python.org/downloads/
2. Download the latest version (3.11 or 3.12)
3. **IMPORTANT (Mac):** During install, there may be a checkbox that says "Add Python to PATH" — make sure it's checked
4. **On Mac**, you may already have Python. Open Terminal (search "Terminal" in Spotlight) and type:
   ```
   python3 --version
   ```
   If you see something like `Python 3.11.5`, you're good.

### 1.3 — Install Node.js

Node.js is needed to install Claude Code.

1. Go to https://nodejs.org
2. Download the **LTS** version (the one that says "Recommended")
3. Run the installer, accept all defaults
4. Verify it worked — open a terminal and type:
   ```
   node --version
   ```
   You should see something like `v20.11.0`

### 1.4 — Install Claude Code

Claude Code is the command-line tool that lets Claude act as your trading agent.

1. Open your terminal (Terminal app on Mac, or the terminal inside VS Code)
2. Run this command:
   ```
   npm install -g @anthropic-ai/claude-code
   ```
3. Wait for it to finish. Then verify:
   ```
   claude --version
   ```

---

## Part 2: Create Your Accounts

### 2.1 — Create an Alpaca Paper Trading Account

Alpaca is an online brokerage that has a free paper trading mode (fake money, real market data).

1. Go to https://app.alpaca.markets/signup
2. Sign up with your email
3. Verify your email
4. Once logged in, look at the left sidebar — you should see **"Paper Trading"**
5. Click on **Paper Trading** to switch to the paper account
6. Now go to **API Keys** (also in the sidebar, or under your account settings)
7. Click **"Generate New Key"** (or "Regenerate" if one exists)
8. You'll see two values:
   - **API Key** — looks like `PKXXXXXXXXXXXXXXXXXX`
   - **Secret Key** — looks like a long random string
9. **COPY BOTH OF THESE and save them somewhere safe** (a note, a password manager, etc.)
   - The secret key is only shown ONCE — if you lose it, you'll need to regenerate

### 2.2 — Get Your Anthropic API Key

This is what lets the agent use Claude's AI to make trading decisions. (You need an Anthropic account with API access — this is separate from your Claude.ai chat account.)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to **API Keys** in the sidebar
4. Click **"Create Key"**
5. Name it something like "trading-agent"
6. **Copy the key** — it starts with `sk-ant-...`
7. Save it alongside your Alpaca keys

**Note:** The Anthropic API is pay-per-use. Using Claude Sonnet for trading analysis will cost roughly $0.01–$0.05 per routine run, so maybe $0.50–$1.00 per trading day. You can set spending limits in the console.

---

## Part 3: Set Up the Project

### 3.1 — Open the Project in VS Code

1. Open VS Code
2. Click **File → Open Folder**
3. Navigate to this folder: `Documents/Claude/Projects/Agent With API Key, For Trading Technical Analysis`
4. Click **Open**
5. You should see all the project files in the left sidebar (CLAUDE.md, scripts/, memory/, etc.)

### 3.2 — Open the Terminal in VS Code

1. In VS Code, go to the menu bar: **Terminal → New Terminal**
2. A terminal panel opens at the bottom of VS Code
3. You should see your project folder path in the prompt

### 3.3 — Install Python Dependencies

In that VS Code terminal, run:

```bash
pip3 install -r requirements.txt
```

This installs the Python libraries the scripts need (Alpaca API, pandas for data, technical analysis library, etc.). If that command doesn't work, try:

```bash
python3 -m pip install -r requirements.txt
```

### 3.4 — Create Your .env File

The `.env` file stores your secret API keys. It's never shared or uploaded anywhere.

1. In the VS Code terminal, run:
   ```bash
   cp .env.example .env
   ```
2. Now open the new `.env` file in VS Code (click on it in the sidebar)
3. Replace the placeholder values with your actual keys:
   ```
   ALPACA_API_KEY=PK1234567890ABCDEF
   ALPACA_SECRET_KEY=your_actual_secret_key_here
   ```
4. Save the file (Cmd+S on Mac, Ctrl+S on Windows)

---

## Part 4: Test Everything

Before running the agent, let's make sure the pieces work.

### 4.1 — Test Alpaca Connection

In the VS Code terminal:

```bash
python3 scripts/alpaca_client.py account
```

**What you should see:** JSON output showing your paper account with ~$100,000 in equity:
```json
{
  "equity": 100000.0,
  "cash": 100000.0,
  "buying_power": 200000.0,
  ...
}
```

**If you get an error:** Double-check your API keys in `.env`. Make sure there are no extra spaces or quotes around the values.

### 4.2 — Test Market Data

```bash
python3 scripts/alpaca_client.py clock
```

This tells you if the stock market is currently open or closed.

### 4.3 — Test Technical Analysis

```bash
python3 scripts/research.py analyze AAPL
```

**What you should see:** A big JSON output with Apple's current price, indicator values (RSI, MACD, moving averages, etc.), and signal readings. This is the data the AI agent uses to make decisions.

### 4.4 — Test a Full Watchlist Scan

```bash
python3 scripts/research.py scan
```

This scans all 10 symbols in your watchlist and returns technical analysis for each one. It takes about 30 seconds.

---

## Part 5: Run the Agent with Claude Code

This is where it all comes together. Claude Code reads the `CLAUDE.md` file (the agent's brain) and becomes your trading agent.

### 5.1 — Start Claude Code

In your VS Code terminal, make sure you're in the project folder, then:

```bash
claude
```

This opens Claude Code in interactive mode. It automatically reads `CLAUDE.md` and understands it's a trading agent.

### 5.2 — Try These Commands

Once Claude Code is running, you can type in plain English. Try these:

**Check your account:**
```
Show me my account status and whether the market is open
```

**Run a market scan:**
```
Run the pre-market research routine — read routines/1_pre_market_research.md and follow all the steps
```

**Analyze a specific stock:**
```
Analyze NVDA — run the research script and tell me if there's a trade setup
```

**See your positions:**
```
Check my open positions and how they're performing
```

**Run end-of-day review:**
```
Run the end-of-day review routine — read routines/4_end_of_day_review.md and follow all the steps
```

### 5.3 — How a Typical Session Works

1. Claude reads its memory files to know what happened yesterday
2. It runs `python3 scripts/research.py scan` to check all watchlist stocks
3. It analyzes the indicator signals and decides if any setup is worth trading
4. If yes, it runs `python3 scripts/alpaca_client.py buy AAPL 5 market` (for example)
5. It updates `memory/open_positions.md` with the new trade details
6. It writes a journal entry in `journal/` explaining its reasoning
7. Before exiting, it saves everything back to the memory files

---

## Part 6: Set Up Automated Routines (Optional — Advanced)

If you want the agent to run on its own schedule (like in the video), you can set up **Claude Code cloud routines**. This requires a Claude Code subscription with cloud access.

### The 5 Daily Routines

| Routine | Time (ET) | What it does |
|---------|-----------|--------------|
| Pre-Market Research | 8:00 AM | Scans watchlist, identifies trade setups |
| Market Open Execution | 9:35 AM | Executes planned trades |
| Midday Scan | 12:30 PM | Checks positions, adjusts stops |
| End-of-Day Review | 3:45 PM | Closes day trades, writes journal |
| Friday Weekly Review | 4:30 PM Fri | Analyzes the week, refines strategy |

### Setting Them Up

Run each of these commands in your terminal (not inside Claude Code):

```bash
claude routine create \
  --name "pre-market-research" \
  --schedule "0 8 * * 1-5" \
  --prompt "$(cat routines/1_pre_market_research.md)"

claude routine create \
  --name "market-open" \
  --schedule "35 9 * * 1-5" \
  --prompt "$(cat routines/2_market_open_execution.md)"

claude routine create \
  --name "midday-scan" \
  --schedule "30 12 * * 1-5" \
  --prompt "$(cat routines/3_midday_scan.md)"

claude routine create \
  --name "eod-review" \
  --schedule "45 15 * * 1-5" \
  --prompt "$(cat routines/4_end_of_day_review.md)"

claude routine create \
  --name "weekly-review" \
  --schedule "30 16 * * 5" \
  --prompt "$(cat routines/5_weekly_review.md)"
```

**The schedule codes explained:**
- `0 8 * * 1-5` means "at minute 0, hour 8, every day of month, every month, Monday through Friday"
- `35 9 * * 1-5` means "at 9:35 AM, weekdays only"
- `30 16 * * 5` means "at 4:30 PM on Fridays"

---

## Part 7: Understanding the Project Structure

Here's what every file and folder does:

```
Your Project/
│
├── CLAUDE.md                 ← The agent's brain. All its rules, strategy,
│                                and personality live here. Edit this to change
│                                how the agent trades.
│
├── .env                      ← Your secret API keys. NEVER share this file.
│
├── requirements.txt          ← List of Python libraries to install.
│
├── scripts/                  ← Helper tools the agent uses
│   ├── alpaca_client.py      ← Talks to Alpaca (buy, sell, check account)
│   └── research.py           ← Fetches stock data and computes indicators
│
├── memory/                   ← The agent's memory (reads on start, writes on exit)
│   ├── watchlist.json        ← Which stocks to watch
│   ├── strategy.md           ← Current trading rules and adjustments
│   ├── market_context.md     ← Latest market conditions
│   ├── trade_log.json        ← History of all trades
│   ├── learnings.md          ← Lessons the agent has learned
│   └── open_positions.md     ← Current open trades with stop/target levels
│
├── routines/                 ← Scheduled routine instructions
│   ├── 1_pre_market_research.md
│   ├── 2_market_open_execution.md
│   ├── 3_midday_scan.md
│   ├── 4_end_of_day_review.md
│   └── 5_weekly_review.md
│
└── journal/                  ← Daily trade journals the agent writes
    └── (YYYY-MM-DD.md files appear here as the agent trades)
```

---

## Part 8: Key Concepts Explained

### What is Paper Trading?
Paper trading is simulated trading with fake money. You get $100,000 of play money from Alpaca. The stock prices are real, but no actual money changes hands. It's for learning and testing strategies without risk.

### What is Technical Analysis?
Technical analysis means using math-based indicators on stock price/volume data to predict where a stock might go next. The agent uses these indicators:

- **RSI (Relative Strength Index):** Measures if a stock is "overbought" (might drop) or "oversold" (might bounce). Scale 0–100; below 30 = oversold, above 70 = overbought.
- **MACD:** Shows momentum — when its two lines cross, it can signal a trend change.
- **SMA/EMA (Moving Averages):** Smooth out price to show the trend. When a fast average crosses above a slow one, it's bullish.
- **Bollinger Bands:** Show if a stock is trading unusually high or low compared to its recent range.
- **ATR (Average True Range):** Measures how volatile a stock is — used to set stop-losses.
- **VWAP:** The average price weighted by volume — a benchmark for intraday traders.
- **Stochastic RSI:** Another momentum indicator for spotting extremes.

### What is a Stop-Loss?
A stop-loss is a price where you automatically sell to limit your loss. For example, if you buy at $100, you might set a stop-loss at $97, meaning you'd lose at most $3 per share if the trade goes wrong.

### What are Claude Code Routines?
Claude Code can run on a schedule without you being there. Each "routine" is a set of instructions that tell Claude what to do at a specific time (scan the market, place trades, write a journal, etc.). Between runs, Claude has no memory — it relies entirely on the files in the `memory/` folder.

---

## Part 9: Customization

### Change the Watchlist
Edit `memory/watchlist.json` to add or remove stocks. Each entry has:
- `symbol` — the ticker (e.g., "AAPL")
- `notes` — your notes about why it's on the list
- `strategy` — "day", "swing", or "both"

### Change Trading Rules
Edit `CLAUDE.md` to adjust:
- Max position size (default $1,000)
- Max number of open positions (default 5)
- Daily loss cap (default 2%)
- Which indicators to prioritize
- Entry/exit criteria

### Change the Schedule
Edit the cron schedules when creating routines. Use https://crontab.guru to design your schedule.

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'alpaca'"**
→ Run `pip3 install -r requirements.txt` again

**"ALPACA_API_KEY is not set"**
→ Make sure your `.env` file exists and has the correct keys without quotes or spaces

**"403 Forbidden" from Alpaca**
→ You might be using live trading keys instead of paper trading keys. Go to Alpaca → Paper Trading → API Keys

**Scripts return empty data**
→ The market might be closed (weekends, holidays, after hours). Run `python3 scripts/alpaca_client.py clock` to check.

**"claude: command not found"**
→ Claude Code isn't installed. Run `npm install -g @anthropic-ai/claude-code`

**Claude Code doesn't seem to know about the trading agent**
→ Make sure you're running `claude` from inside the project folder (the one with CLAUDE.md in it)
