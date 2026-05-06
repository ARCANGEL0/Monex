from django.conf import settings

CURRENCIES = {
    "EUR": "€",
    "USD": "$",
    "GBP": "£",
    "JPY": "¥",
    "CHF": "Fr",
    "CAD": "C$",
    "AUD": "A$",
    "CNY": "¥",
    "INR": "₹",
    "BRL": "R$",
    "KRW": "₩",
    "MXN": "MX$",
    "SEK": "kr",
    "NOK": "kr",
    "DKK": "kr",
    "PLN": "zł",
    "TRY": "₺",
    "ZAR": "R",
    "RUB": "₽",
    "THB": "฿",
    "SGD": "S$",
    "HKD": "HK$",
    "NZD": "NZ$",
    "AED": "د.إ",
    "SAR": "﷼",
}

LANGUAGE_OPTIONS = [
    {"code": "en", "label": "English", "flag": "🇺🇸"},
    {"code": "es", "label": "Español", "flag": "🇪🇸"},
    {"code": "pt", "label": "Português", "flag": "🇵🇹"},
    {"code": "pl", "label": "Polski", "flag": "🇵🇱"},
]

def currency_ctx(request):
    sym = request.session.get("currency", settings.CURRENCY_SYMBOL)
    code = request.session.get("currency_code", settings.CURRENCY_CODE)
    return {
        "currency_symbol": sym,
        "currency_code": code,
        "currencies": CURRENCIES,
        "language_options": LANGUAGE_OPTIONS,
    }
