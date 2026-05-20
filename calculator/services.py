# calculator/services.py

# Normal Shopee fees
SHOPEE_PERCENT_FEES = {
    "Platform": {
        "percent": 0.165,
        "description": "Phí sàn cố định",
    },
    "Payment": {
        "percent": 0.06,
        "description": "Phí thanh toán",
    },
    "TNCN_Shopee": {
        # IMPORTANT: The total is 3.5%, Shopee collects 1.5% on behalf.
        # We are still responsible for the remaining 2%.
        "percent": 0.015,
        "description": "Thuế TNCN sàn thu",
    },
}

SHOPEE_FIXED_FEES = {
    "Piship": {
        "fixed": 2700,
        "description": "Phí chương trình Piship",
    },
    "Ha_tang": {
        "fixed": 3000,
        "description": "Phí hạ tầng",
    },
}

# Special capped fee
VOUCHER_EXTRA_PERCENT = 0.055
VOUCHER_EXTRA_MAX = 50000

# Tax TNCN. This is the tax that HKD pays based on the profit,
# after deducting all the fees and costs including Shopee fees.
TAX_HKD_RATE = 0.17

# For the meantime, I consider these as costs per item imposed directly on the final selling price.
# In the future, we may add costs per item calculated based on the production cost.
HKD_PERCENT_COST = {
    "Vat_HKD": {
        "percent": 0.02,
        "description": "VAT - HKD tự nộp, bên cạnh VAT 1% Shopee thu hộ.",
    },

    "Marketing": {
        "percent": 0.04,
        "description": "Marketing - ước tính cho mỗi sản phẩm",
    },

    "Service_allowance": {
        "percent": 0.02,
        "description": "Thất thoát - ước tính mỗi sản phẩm phải chịu để bù đắp cho các chi phí không tính toán được, như chiết khấu, hoàn trả, v.v.",
    },
}

# Basic functions setups:
def shopee_total_percent_fee():
    return sum(fee["percent"] for fee in SHOPEE_PERCENT_FEES.values())


def hkd_total_percent_cost(hkd_percent_cost=None):
    if hkd_percent_cost is None:
        hkd_percent_cost = HKD_PERCENT_COST
    return sum(fee["percent"] for fee in hkd_percent_cost.values())


def shopee_total_fixed_fee():
    return sum(fee["fixed"] for fee in SHOPEE_FIXED_FEES.values())


def hkd_total_fixed_cost():  # This one is for the future
    return None


def total_tax_hkd(net_profit_desired):
    pre_tax_profit = net_profit_desired / (1 - TAX_HKD_RATE)
    return pre_tax_profit * TAX_HKD_RATE


def voucher_extra_fee(selling_price):
    return min(
        selling_price * VOUCHER_EXTRA_PERCENT,
        VOUCHER_EXTRA_MAX
    )


def build_percent_breakdown(fees, selling_price):
    breakdown = []

    for name, fee in fees.items():
        rate = fee["percent"]

        breakdown.append({
            "name": name,
            "description": fee["description"],
            "amount": selling_price * rate,
            "rate": rate,
            "rate_percent": rate * 100,
        })

    return breakdown


def build_fixed_breakdown(fees):
    breakdown = []

    for name, fee in fees.items():
        breakdown.append({
            "name": name,
            "description": fee["description"],
            "amount": fee["fixed"],
            "rate": None,
            "rate_percent": None,
        })

    return breakdown


def build_voucher_breakdown(selling_price):
    voucher_amount = voucher_extra_fee(selling_price)

    if voucher_amount >= VOUCHER_EXTRA_MAX:
        description = "Phí tham gia voucher Extra, đã chạm mức tối đa"
        rate = None
        rate_percent = None
    else:
        description = "Phí tham gia voucher Extra"
        rate = VOUCHER_EXTRA_PERCENT
        rate_percent = VOUCHER_EXTRA_PERCENT * 100

    return {
        "name": "Voucher_Extra",
        "description": description,
        "amount": voucher_amount,
        "rate": rate,
        "rate_percent": rate_percent,
    }


def build_hkd_percent_cost(marketing_rate=0.04, service_allowance_rate=0.02):
    hkd_percent_cost = {
        **HKD_PERCENT_COST,
        "Marketing": {
            **HKD_PERCENT_COST["Marketing"],
            "percent": marketing_rate,
        },
        "Service_allowance": {
            **HKD_PERCENT_COST["Service_allowance"],
            "percent": service_allowance_rate,
        },
    }

    return hkd_percent_cost


def shopee_selling_price(
    cost,
    net_profit_desired,
    marketing_rate=0.04,
    service_allowance_rate=0.02,
):
    tax = total_tax_hkd(net_profit_desired)

    base_amount = cost + net_profit_desired + tax

    hkd_percent_cost = build_hkd_percent_cost(
        marketing_rate=marketing_rate,
        service_allowance_rate=service_allowance_rate,
    )

    normal_percent_fee = shopee_total_percent_fee() + hkd_total_percent_cost(hkd_percent_cost)
    normal_fixed_fee = shopee_total_fixed_fee()  # Add hkd_total_fixed_cost() in the future

    # Case 1:
    # Voucher Extra is still 4% because it has not reached 50,000
    price_if_voucher_is_percent = (
        base_amount + normal_fixed_fee
    ) / (
        1 - normal_percent_fee - VOUCHER_EXTRA_PERCENT
    )

    voucher_if_percent = price_if_voucher_is_percent * VOUCHER_EXTRA_PERCENT

    if voucher_if_percent <= VOUCHER_EXTRA_MAX:
        return price_if_voucher_is_percent

    # Case 2:
    # Voucher Extra reaches the maximum, so it becomes fixed at 50,000
    price_if_voucher_is_fixed = (
        base_amount + normal_fixed_fee + VOUCHER_EXTRA_MAX
    ) / (
        1 - normal_percent_fee
    )

    return price_if_voucher_is_fixed


def calculate_selling_price(
    cost,
    desired_profit,
    marketing_rate=0.04,
    service_allowance_rate=0.02,
):
    selling_price = shopee_selling_price(
        cost,
        desired_profit,
        marketing_rate=marketing_rate,
        service_allowance_rate=service_allowance_rate,
    )

    tax = total_tax_hkd(desired_profit)
    voucher_extra = voucher_extra_fee(selling_price)

    hkd_percent_cost = build_hkd_percent_cost(
        marketing_rate=marketing_rate,
        service_allowance_rate=service_allowance_rate,
    )

    hkd_fee_breakdown = build_percent_breakdown(
        hkd_percent_cost,
        selling_price,
    )

    fee_breakdown = []

    fee_breakdown += build_percent_breakdown(
        SHOPEE_PERCENT_FEES,
        selling_price,
    )

    fee_breakdown += build_fixed_breakdown(
        SHOPEE_FIXED_FEES,
    )

    fee_breakdown.append(
        build_voucher_breakdown(selling_price)
    )

    total_shopee_fee = sum(fee["amount"] for fee in fee_breakdown)
    total_hkd_cost = tax + sum(fee["amount"] for fee in hkd_fee_breakdown)

    return {
        "cost": cost,
        "desired_profit": desired_profit,
        "total_hkd_cost": total_hkd_cost,
        "tax": tax,
        "voucher_extra": voucher_extra,
        "shopee_fee": total_shopee_fee,
        "selling_price": selling_price,
        "fee_breakdown": fee_breakdown,
        "hkd_fee_breakdown": hkd_fee_breakdown,
    }