#!/usr/bin/env python3
"""
Alpaca Paper Trading CLI
Called by Claude Code routines to interact with the Alpaca API.

Usage:
    python scripts/alpaca_client.py account
    python scripts/alpaca_client.py positions
    python scripts/alpaca_client.py orders [open|closed|all]
    python scripts/alpaca_client.py buy <symbol> <qty> <market|limit> [limit_price]
    python scripts/alpaca_client.py sell <symbol> <qty> <market|limit> [limit_price]
    python scripts/alpaca_client.py trailing_stop <symbol> <qty> <trail_percent>
    python scripts/alpaca_client.py stop <symbol> <qty> <stop_price>
    python scripts/alpaca_client.py close <symbol>
    python scripts/alpaca_client.py close-all
    python scripts/alpaca_client.py cancel <order_id>
    python scripts/alpaca_client.py cancel-all
    python scripts/alpaca_client.py clock
    python scripts/alpaca_client.py price <symbol>
    python scripts/alpaca_client.py daytrade-count
"""

import sys
import os
import json
from datetime import datetime

# Add parent dir so we can load .env from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    GetOrdersRequest,
    TrailingStopOrderRequest,
    StopOrderRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed


API_KEY = os.getenv("ALPACA_API_KEY", "")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

if not API_KEY or not SECRET_KEY:
    print("ERROR: ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env")
    sys.exit(1)

trading = TradingClient(API_KEY, SECRET_KEY, paper=True)
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)


def cmd_account():
    acct = trading.get_account()
    result = {
        "equity": float(acct.equity),
        "cash": float(acct.cash),
        "buying_power": float(acct.buying_power),
        "portfolio_value": float(acct.portfolio_value),
        "pnl_today": round(float(acct.equity) - float(acct.last_equity), 2),
        "status": acct.status.value if hasattr(acct.status, "value") else str(acct.status),
        "daytrade_count": int(acct.daytrade_count) if hasattr(acct, "daytrade_count") else None,
        "pattern_day_trader": bool(acct.pattern_day_trader) if hasattr(acct, "pattern_day_trader") else None,
    }
    # Capital deployment %
    try:
        deployed_pct = (float(acct.equity) - float(acct.cash)) / float(acct.equity) * 100
        result["deployed_pct"] = round(deployed_pct, 2)
    except Exception:
        result["deployed_pct"] = None
    print(json.dumps(result, indent=2))


def cmd_daytrade_count():
    """Quick read of just the day-trade count for PDT enforcement."""
    acct = trading.get_account()
    print(json.dumps({
        "daytrade_count": int(acct.daytrade_count) if hasattr(acct, "daytrade_count") else None,
        "pattern_day_trader": bool(acct.pattern_day_trader) if hasattr(acct, "pattern_day_trader") else None,
        "equity": float(acct.equity),
        "pdt_window_remaining": max(0, 3 - int(acct.daytrade_count)) if hasattr(acct, "daytrade_count") else None,
    }, indent=2))


def cmd_positions():
    positions = trading.get_all_positions()
    result = []
    for p in positions:
        result.append({
            "symbol": p.symbol,
            "qty": float(p.qty),
            "side": p.side.value if hasattr(p.side, "value") else str(p.side),
            "avg_entry": float(p.avg_entry_price),
            "current_price": float(p.current_price),
            "market_value": float(p.market_value),
            "unrealized_pnl": float(p.unrealized_pl),
            "unrealized_pnl_pct": round(float(p.unrealized_plpc) * 100, 2),
        })
    print(json.dumps(result, indent=2))


def cmd_orders(status="open"):
    query_map = {
        "open": QueryOrderStatus.OPEN,
        "closed": QueryOrderStatus.CLOSED,
        "all": QueryOrderStatus.ALL,
    }
    request = GetOrdersRequest(status=query_map.get(status, QueryOrderStatus.OPEN), limit=50)
    orders = trading.get_orders(request)
    result = []
    for o in orders:
        result.append({
            "order_id": str(o.id),
            "symbol": o.symbol,
            "side": o.side.value if hasattr(o.side, "value") else str(o.side),
            "qty": float(o.qty) if o.qty else None,
            "type": o.type.value if hasattr(o.type, "value") else str(o.type),
            "status": o.status.value if hasattr(o.status, "value") else str(o.status),
            "filled_avg_price": float(o.filled_avg_price) if o.filled_avg_price else None,
            "submitted_at": str(o.submitted_at),
        })
    print(json.dumps(result, indent=2))


def cmd_buy(symbol, qty, order_type, limit_price=None):
    _place_order(symbol, float(qty), "buy", order_type, limit_price)


def cmd_sell(symbol, qty, order_type, limit_price=None):
    _place_order(symbol, float(qty), "sell", order_type, limit_price)


def _place_order(symbol, qty, side, order_type, limit_price=None):
    order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL

    if order_type == "limit" and limit_price:
        request = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY,
            limit_price=float(limit_price),
        )
    else:
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY,
        )

    order = trading.submit_order(request)
    result = {
        "order_id": str(order.id),
        "symbol": order.symbol,
        "side": side,
        "qty": qty,
        "type": order_type,
        "status": order.status.value if hasattr(order.status, "value") else str(order.status),
    }
    if limit_price:
        result["limit_price"] = float(limit_price)
    print(json.dumps(result, indent=2))


def cmd_trailing_stop(symbol, qty, trail_percent):
    """Place a GTC trailing-stop sell order. Used after every entry to protect downside."""
    request = TrailingStopOrderRequest(
        symbol=symbol,
        qty=float(qty),
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC,
        trail_percent=float(trail_percent),
    )
    try:
        order = trading.submit_order(request)
        result = {
            "order_id": str(order.id),
            "symbol": symbol,
            "qty": float(qty),
            "type": "trailing_stop",
            "trail_percent": float(trail_percent),
            "time_in_force": "gtc",
            "status": order.status.value if hasattr(order.status, "value") else str(order.status),
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        # Fall back hint for caller
        print(json.dumps({
            "error": str(e),
            "fallback_suggestion": "Try fixed stop via: alpaca_client.py stop SYMBOL QTY STOP_PRICE",
        }))
        sys.exit(2)


def cmd_stop(symbol, qty, stop_price):
    """Place a GTC fixed-stop sell order. Fallback when trailing_stop is rejected."""
    request = StopOrderRequest(
        symbol=symbol,
        qty=float(qty),
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC,
        stop_price=float(stop_price),
    )
    try:
        order = trading.submit_order(request)
        result = {
            "order_id": str(order.id),
            "symbol": symbol,
            "qty": float(qty),
            "type": "stop",
            "stop_price": float(stop_price),
            "time_in_force": "gtc",
            "status": order.status.value if hasattr(order.status, "value") else str(order.status),
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)


def cmd_close(symbol):
    result = trading.close_position(symbol)
    print(json.dumps({"status": "closed", "symbol": symbol, "order_id": str(result.id)}, indent=2))


def cmd_close_all():
    trading.close_all_positions(cancel_orders=True)
    print(json.dumps({"status": "all_positions_closed"}))


def cmd_cancel(order_id):
    trading.cancel_order_by_id(order_id)
    print(json.dumps({"status": "cancelled", "order_id": order_id}))


def cmd_cancel_all():
    trading.cancel_orders()
    print(json.dumps({"status": "all_orders_cancelled"}))


def cmd_clock():
    clock = trading.get_clock()
    result = {
        "is_open": clock.is_open,
        "timestamp": str(clock.timestamp),
        "next_open": str(clock.next_open),
        "next_close": str(clock.next_close),
    }
    print(json.dumps(result, indent=2))


def cmd_price(symbol):
    from datetime import timedelta
    end = datetime.now()
    start = end - timedelta(days=5)
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame(1, TimeFrameUnit.Day),
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )
    bars = data_client.get_stock_bars(request)
    df = bars.df
    if hasattr(df.index, "droplevel"):
        try:
            df = df.droplevel("symbol")
        except Exception:
            pass
    if df.empty:
        print(json.dumps({"error": f"No data for {symbol}"}))
        return
    latest = df.iloc[-1]
    print(json.dumps({
        "symbol": symbol,
        "close": float(latest["close"]),
        "open": float(latest["open"]),
        "high": float(latest["high"]),
        "low": float(latest["low"]),
        "volume": int(latest["volume"]),
    }, indent=2))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    try:
        if cmd == "account":
            cmd_account()
        elif cmd == "positions":
            cmd_positions()
        elif cmd == "orders":
            status = sys.argv[2] if len(sys.argv) > 2 else "open"
            cmd_orders(status)
        elif cmd == "buy":
            symbol, qty, otype = sys.argv[2].upper(), sys.argv[3], sys.argv[4]
            limit_price = sys.argv[5] if len(sys.argv) > 5 else None
            cmd_buy(symbol, qty, otype, limit_price)
        elif cmd == "sell":
            symbol, qty, otype = sys.argv[2].upper(), sys.argv[3], sys.argv[4]
            limit_price = sys.argv[5] if len(sys.argv) > 5 else None
            cmd_sell(symbol, qty, otype, limit_price)
        elif cmd == "trailing_stop":
            symbol, qty, trail_pct = sys.argv[2].upper(), sys.argv[3], sys.argv[4]
            cmd_trailing_stop(symbol, qty, trail_pct)
        elif cmd == "stop":
            symbol, qty, stop_price = sys.argv[2].upper(), sys.argv[3], sys.argv[4]
            cmd_stop(symbol, qty, stop_price)
        elif cmd == "daytrade-count":
            cmd_daytrade_count()
        elif cmd == "close":
            cmd_close(sys.argv[2].upper())
        elif cmd == "close-all":
            cmd_close_all()
        elif cmd == "cancel":
            cmd_cancel(sys.argv[2])
        elif cmd == "cancel-all":
            cmd_cancel_all()
        elif cmd == "clock":
            cmd_clock()
        elif cmd == "price":
            cmd_price(sys.argv[2].upper())
        else:
            print(f"Unknown command: {cmd}")
            print(__doc__)
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
