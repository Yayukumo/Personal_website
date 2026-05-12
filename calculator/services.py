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

HKD_PERCENT_COST = {
    "Vat_HKD": {
        "percent": 0.02,
        "description": "VAT responsible by HKD, apart from what Shopee collects on behalf.",
    },

    "Marketing": {
        "percent": 0.05,
        "description": "Estimated Marketing cost the product.",
    },

    "Service_allowance" : {
        "percent": 0.03,
        "description": "Money to fix small problems smoothly./ That thoat",
    },
}


def shopee_total_percent_fee():
    return sum(fee["percent"] for fee in SHOPEE_PERCENT_FEES.values())

def hkd_total_percent_cost():
    return sum(fee["percent"] for fee in HKD_PERCENT_COST.values())


def shopee_total_fixed_fee():
    return sum(fee["fixed"] for fee in SHOPEE_FIXED_FEES.values())

def hkd_total_fixed_cost(): # This one is for the future
    return None


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

    normal_percent_fee = shopee_total_percent_fee() + hkd_total_percent_cost()
    normal_fixed_fee = shopee_total_fixed_fee() # Add hkd_total_fixed_cost() in the future

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

    hkd_fee_breakdown = []

    hkd_fee_breakdown.append({
        "name": "VAT HKD",
        "description": "VAT HKD tự nộp, bên cạnh VAT 1% Shopee thu hộ",
        "amount": selling_price * 0.02,
        "rate": 0.02,
        "rate_percent": 2
    })
    
    hkd_fee_breakdown.append({
        "name": "Marketing",
        "description": "Chi phí Marketing ước tính cho mỗi sản phẩm",
        "amount": selling_price * 0.05,
        "rate": 0.05,
        "rate_percent": 5,
    })

    hkd_fee_breakdown.append({
        "name": "Service allowance",
        "description": "Thất thoát",
        "amount": selling_price * 0.03,
        "rate": 0.03,
        "rate_percent": 3
    })

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
        "amount": selling_price * 0.015,
        "rate": 0.015,
        "rate_percent": 1.5,
    })

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