# calculator/services.py

# Normal Shopee fees
SHOPEE_PERCENT_FEES = {
    "Platform": {
        "percent": 0.135,
        "description": "Phí sàn cố định",
    },
    "Payment": {
        "percent": 0.05,
        "description": "Phí thanh toán",
    },
    "TNCN_Shopee": {   
        # IMPORTANT: The total is 3.5%, Shopee collects 1.5% on behalf. We are still responsible for the remaining 2%.
        "percent": 0.015,
        "description": "Thuế TNCN sàn thu",
    },
}

SHOPEE_FIXED_FEES = {
    "Piship": {
        "fixed": 1700,
        "description": "Phí chương trình Piship",
    },
    "Ha_tang": {
        "fixed": 3000,
        "description": "Phí hạ tầng",
    },
}

# Special capped fee
VOUCHER_EXTRA_PERCENT = 0.04
VOUCHER_EXTRA_MAX = 50000

# Tax
TAX_HKD_RATE = 0.17

# VAT for HKD
vat_hkd = 0.02 # The total VAT is actually 3%. 1% is collected on behalf by Shopee

def shopee_total_percent_fee():
    return sum(fee["percent"] for fee in SHOPEE_PERCENT_FEES.values())


def shopee_total_fixed_fee():
    return sum(fee["fixed"] for fee in SHOPEE_FIXED_FEES.values())


def total_tax_hkd(net_profit_desired):
    pre_tax_profit = net_profit_desired / (1 - TAX_HKD_RATE)
    return pre_tax_profit * TAX_HKD_RATE


def voucher_extra_fee(selling_price):
    return min(
        selling_price * VOUCHER_EXTRA_PERCENT,
        VOUCHER_EXTRA_MAX
    )


def shopee_selling_price(cost, net_profit_desired):
    tax = total_tax_hkd(net_profit_desired)

    base_amount = cost + net_profit_desired + tax

    normal_percent_fee = shopee_total_percent_fee() + vat_hkd
    normal_fixed_fee = shopee_total_fixed_fee()

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


def calculate_selling_price(cost, desired_profit):
    selling_price = shopee_selling_price(cost, desired_profit)

    tax = total_tax_hkd(desired_profit)
    voucher_extra = voucher_extra_fee(selling_price)

    vat_redbean = shopee_selling_price(cost,desired_profit)*vat_hkd

    fee_breakdown = []

    fee_breakdown.append({
        "name": "Platform",
        "description": "Phí sàn cố định",
        "amount": selling_price * 0.135,
        "rate": 0.135,
        "rate_percent": 13.5,
    })

    fee_breakdown.append({
        "name": "Piship",
        "description": "Phí chương trình PiShip",
        "amount": 1700,
        "rate": None,
        "rate_percent": None,
    })

    fee_breakdown.append({
        "name": "Payment",
        "description": "Phí thanh toán",
        "amount": selling_price * 0.05,
        "rate": 0.05,
        "rate_percent": 5.0,
    })

    fee_breakdown.append({
        "name": "Ha_tang",
        "description": "Phí hạ tầng",
        "amount": 3000,
        "rate": None,
        "rate_percent": None,
    })

    fee_breakdown.append({
        "name": "Voucher_Extra",
        "description": "Phí tham gia voucher Extra",
        "amount": voucher_extra_fee(selling_price),
        "rate": 0.04,
        "rate_percent": 4.0,
    })

    fee_breakdown.append({
        "name": "TNCN_Shopee",
        "description": "Thuế TNCN sàn thu",
        "amount": selling_price * 0.035,
        "rate": 0.015,
        "rate_percent": 1.5,
    })

    total_shopee_fee = sum(fee["amount"] for fee in fee_breakdown)
    
    return {
        "cost": cost,
        "desired_profit": desired_profit,
        "tax": tax,
        "vat": vat_redbean,
        "voucher_extra": voucher_extra,
        "shopee_fee": total_shopee_fee,
        "selling_price": selling_price,
        "fee_breakdown": fee_breakdown,
    }