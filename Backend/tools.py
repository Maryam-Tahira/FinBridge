"""
FinBridge AI — Financial Tools
Currency conversion, remittance comparison, budget tracking, tuition guides
"""


class CurrencyTool:
    """Real-time currency conversion tool"""

    # Demo rates (in production, use an API like exchangerate-api.com)
    RATES_TO_USD = {
        "USD": 1.0, "BDT": 0.00824, "CNY": 0.1380, "EUR": 1.0850,
        "GBP": 1.2650, "JPY": 0.00667, "INR": 0.01195, "MYR": 0.2290,
        "SGD": 0.7500, "AUD": 0.6540, "CAD": 0.7350, "KRW": 0.000745,
        "PKR": 0.00357, "NPR": 0.00748, "THB": 0.02890, "VND": 0.0000398
    }

    async def convert(self, from_curr: str, to_curr: str, amount: float) -> dict:
        from_curr = from_curr.upper()
        to_curr = to_curr.upper()

        if from_curr not in self.RATES_TO_USD or to_curr not in self.RATES_TO_USD:
            return {"error": f"Unsupported currency pair: {from_curr}/{to_curr}"}

        # Convert: from_curr -> USD -> to_curr
        usd_amount = amount * self.RATES_TO_USD[from_curr]
        result = usd_amount / self.RATES_TO_USD[to_curr]
        rate = self.RATES_TO_USD[from_curr] / self.RATES_TO_USD[to_curr]

        return {
            "from": from_curr,
            "to": to_curr,
            "input_amount": amount,
            "converted_amount": round(result, 2),
            "rate": round(rate, 6),
            "inverse_rate": round(1 / rate, 6)
        }

    async def get_rates(self, base: str = "USD") -> dict:
        base = base.upper()
        if base not in self.RATES_TO_USD:
            return {"error": f"Unknown base currency: {base}"}

        base_to_usd = self.RATES_TO_USD[base]
        rates = {}
        for currency, to_usd in self.RATES_TO_USD.items():
            if currency != base:
                rates[currency] = round(base_to_usd / to_usd, 6)

        return {"base": base, "rates": rates}


class RemittanceTool:
    """Compare money transfer services"""

    PROVIDERS = {
        "wise": {
            "name": "Wise (TransferWise)",
            "type": "Online Transfer",
            "fee_pct": 0.0092,
            "fixed_fee": 0.50,
            "rate_markup": 0.0003,
            "delivery": "1-2 hours",
            "min_amount": 1,
            "max_amount": 1000000
        },
        "remitly": {
            "name": "Remitly",
            "type": "Online Transfer",
            "fee_pct": 0.0,
            "fixed_fee": 3.99,
            "rate_markup": 0.0035,
            "delivery": "Minutes to 3 days",
            "min_amount": 1,
            "max_amount": 10000
        },
        "western_union": {
            "name": "Western Union",
            "type": "Bank + Cash Pickup",
            "fee_pct": 0.01,
            "fixed_fee": 4.99,
            "rate_markup": 0.012,
            "delivery": "1-3 days",
            "min_amount": 1,
            "max_amount": 50000
        },
        "xoom": {
            "name": "Xoom (PayPal)",
            "type": "Online Transfer",
            "fee_pct": 0.0,
            "fixed_fee": 4.99,
            "rate_markup": 0.025,
            "delivery": "1-4 days",
            "min_amount": 10,
            "max_amount": 10000
        },
        "bank_swift": {
            "name": "Bank Wire (SWIFT)",
            "type": "Bank Transfer",
            "fee_pct": 0.0,
            "fixed_fee": 30.00,
            "rate_markup": 0.02,
            "delivery": "3-5 business days",
            "min_amount": 100,
            "max_amount": 999999
        }
    }

    async def compare(self, from_country: str, to_country: str, amount_usd: float) -> dict:
        results = []
        mid_rate = 7.245  # Example: USD/CNY mid-market rate

        for key, provider in self.PROVIDERS.items():
            fee = provider["fixed_fee"] + (amount_usd * provider["fee_pct"])
            effective_rate = mid_rate * (1 - provider["rate_markup"])
            net_amount = (amount_usd - fee) * effective_rate
            total_cost = fee + (amount_usd * provider["rate_markup"] * mid_rate / mid_rate)

            results.append({
                "provider": provider["name"],
                "type": provider["type"],
                "fee": round(fee, 2),
                "exchange_rate": round(effective_rate, 4),
                "recipient_gets": round(net_amount, 2),
                "delivery": provider["delivery"],
                "total_cost_usd": round(fee, 2)
            })

        # Sort by recipient_gets (highest first = best deal)
        results.sort(key=lambda x: x["recipient_gets"], reverse=True)
        results[0]["best_deal"] = True

        return {
            "from": from_country,
            "to": to_country,
            "amount_usd": amount_usd,
            "mid_market_rate": mid_rate,
            "providers": results
        }


class BudgetTool:
    """Student budget planning tool"""

    CITY_COSTS = {
        "hangzhou": {
            "country": "China", "currency": "CNY",
            "rent_dorm": 800, "rent_apartment": 2000,
            "food": 1200, "transport": 300,
            "phone_internet": 150, "study_materials": 300,
            "entertainment": 400, "health_insurance": 200
        },
        "beijing": {
            "country": "China", "currency": "CNY",
            "rent_dorm": 1000, "rent_apartment": 3500,
            "food": 1500, "transport": 400,
            "phone_internet": 150, "study_materials": 300,
            "entertainment": 500, "health_insurance": 200
        },
        "shenzhen": {
            "country": "China", "currency": "CNY",
            "rent_dorm": 900, "rent_apartment": 3000,
            "food": 1400, "transport": 350,
            "phone_internet": 150, "study_materials": 300,
            "entertainment": 500, "health_insurance": 200
        },
        "london": {
            "country": "UK", "currency": "GBP",
            "rent_dorm": 700, "rent_apartment": 1200,
            "food": 300, "transport": 150,
            "phone_internet": 30, "study_materials": 50,
            "entertainment": 100, "health_insurance": 0
        }
    }

    async def suggest(self, city: str, country: str, budget_usd: float = None) -> dict:
        city_key = city.lower().replace(" ", "")
        costs = self.CITY_COSTS.get(city_key)

        if not costs:
            return {
                "city": city,
                "country": country,
                "note": "City data not available. Contact us for personalized advice.",
                "general_range_usd": "300-800/month for most Asian cities"
            }

        total_min = costs["rent_dorm"] + costs["food"] + costs["transport"] + costs["phone_internet"]
        total_max = costs["rent_apartment"] + costs["food"] + costs["transport"] + costs["phone_internet"] + costs["study_materials"] + costs["entertainment"]

        return {
            "city": city,
            "country": country,
            "currency": costs["currency"],
            "breakdown": {
                "Rent (dorm)": costs["rent_dorm"],
                "Rent (off-campus)": costs["rent_apartment"],
                "Food & Dining": costs["food"],
                "Transport": costs["transport"],
                "Phone & Internet": costs["phone_internet"],
                "Study Materials": costs["study_materials"],
                "Entertainment": costs["entertainment"],
                "Health Insurance": costs["health_insurance"]
            },
            "total_min": total_min,
            "total_max": total_max,
            "tip": "Cooking at home and using campus facilities can save 30-40% on food costs."
        }


class TuitionTool:
    """Tuition payment guide tool"""

    GUIDES = {
        "china": {
            "country": "China",
            "tuition_range": "¥20,000 – ¥50,000/year (most programs)",
            "methods": [
                {
                    "name": "Bank Wire (SWIFT)",
                    "description": "Most common method. University provides bank details.",
                    "fees": "$25-40 per transfer",
                    "delivery": "3-5 business days",
                    "recommended": True
                },
                {
                    "name": "Flywire",
                    "description": "Partnered with many Chinese universities. Tracks payment.",
                    "fees": "Varies, often competitive",
                    "delivery": "2-3 business days",
                    "recommended": True
                },
                {
                    "name": "WeChat Pay / Alipay",
                    "description": "After arrival. Needs Chinese bank account.",
                    "fees": "No fee for domestic transfers",
                    "delivery": "Instant",
                    "recommended": False
                }
            ],
            "tips": [
                "Always use the EXACT university account details provided in your admission letter",
                "Keep transfer receipts — you'll need them for registration",
                "Some universities accept payment in USD; check first",
                "Consider paying full year to lock in exchange rate"
            ]
        },
        "usa": {
            "country": "United States",
            "tuition_range": "$15,000 – $55,000/year",
            "methods": [
                {
                    "name": "Flywire",
                    "description": "Most US universities partner with Flywire.",
                    "fees": "Included in rate",
                    "delivery": "2-4 business days",
                    "recommended": True
                },
                {
                    "name": "PayMyTuition",
                    "description": "Alternative to Flywire with competitive rates.",
                    "fees": "Varies",
                    "delivery": "2-3 business days",
                    "recommended": True
                },
                {
                    "name": "Wire Transfer",
                    "description": "Direct bank wire to university account.",
                    "fees": "$25-45",
                    "delivery": "3-5 business days",
                    "recommended": False
                }
            ],
            "tips": [
                "Check your I-20 for exact tuition amount",
                "Many universities offer installment plans",
                "Some accept credit cards (with 2-3% surcharge)"
            ]
        }
    }

    async def get_guide(self, country: str, university: str = None) -> dict:
        key = country.lower().strip()
        guide = self.GUIDES.get(key)

        if not guide:
            return {
                "country": country,
                "note": "Detailed guide not yet available for this country.",
                "general_advice": "Contact your university's international office for payment instructions."
            }

        return guide
