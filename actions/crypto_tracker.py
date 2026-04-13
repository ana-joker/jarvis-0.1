# actions/crypto_tracker.py — ALBEDO Crypto & Stock Tracker
# Real-time prices via free CoinGecko API.

import requests
from datetime import datetime


def _get_crypto_price(crypto_id: str, currency: str = "usd") -> dict:
    """Get crypto price from CoinGecko (free, no API key)."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency}&include_24hr_change=true"
    r = requests.get(url, timeout=10)
    data = r.json()
    if crypto_id in data:
        return {
            "price": data[crypto_id][currency],
            "change_24h": data[crypto_id].get(f"{currency}_24h_change", 0),
            "currency": currency.upper(),
        }
    return {}


def _get_top_crypto(limit: int = 10) -> list:
    """Get top cryptocurrencies by market cap."""
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={limit}&page=1"
    r = requests.get(url, timeout=10)
    return r.json()


def crypto_tracker(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    Crypto & Stock Tracker — Real-time prices.

    parameters:
        action : price | top | portfolio
        crypto : bitcoin | ethereum | solana | dogecoin | etc.
        limit  : Number of top cryptos (default: 10)
    """
    params = parameters or {}
    action = params.get("action", "price").lower().strip()

    if player:
        player.write_log(f"[Crypto] {action}")

    try:
        if action == "price":
            crypto = params.get("crypto", "bitcoin").lower().strip()
            data = _get_crypto_price(crypto)
            if data:
                change = data.get("change_24h", 0)
                direction = "up" if change >= 0 else "down"
                return (
                    f"{crypto.title()}: {data['price']:,.2f} {data['currency']}, "
                    f"{abs(change):.1f}% {direction} in 24h, sir."
                )
            return f"Could not find price for {crypto}, sir."

        elif action == "top":
            limit = int(params.get("limit", 10))
            coins = _get_top_crypto(limit)
            lines = [f"Top {limit} cryptocurrencies:"]
            for i, c in enumerate(coins[:limit], 1):
                change = c.get("price_change_percentage_24h", 0)
                direction = "🟢" if change >= 0 else "🔴"
                lines.append(f"  {i}. {c['name']:15s} ${c['current_price']:>12,.2f} {direction} {abs(change or 0):.1f}%")
            return "\n".join(lines)

        else:
            return f"Unknown crypto action: '{action}', sir."

    except Exception as e:
        return f"Crypto tracker error: {e}, sir."
