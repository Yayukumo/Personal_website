from django.shortcuts import render
from .services import calculate_selling_price


def parse_money(value):
    if not value:
        return 0

    cleaned_value = (
        value
        .replace(",", "")
        .replace(".", "")
        .replace("đ", "")
        .strip()
    )

    return float(cleaned_value)


def parse_percent(value, default):
    if not value:
        return default

    cleaned_value = (
        value
        .replace("%", "")
        .replace(",", ".")
        .strip()
    )

    return float(cleaned_value)


def calculator_home(request):
    result = None

    cost_input = ""
    desired_profit_input = ""

    marketing_rate_percent = 4
    service_allowance_rate_percent = 2

    if request.method == "POST":
        cost_input = request.POST.get("cost", "")
        desired_profit_input = request.POST.get("desired_profit", "")

        marketing_rate_percent = parse_percent(
            request.POST.get("marketing_rate", ""),
            4
        )

        service_allowance_rate_percent = parse_percent(
            request.POST.get("service_allowance_rate", ""),
            2
        )

        cost = parse_money(cost_input)
        desired_profit = parse_money(desired_profit_input)

        marketing_rate = marketing_rate_percent / 100
        service_allowance_rate = service_allowance_rate_percent / 100

        result = calculate_selling_price(
            cost,
            desired_profit,
            marketing_rate=marketing_rate,
            service_allowance_rate=service_allowance_rate,
        )

    return render(request, "calculator.html", {
        "result": result,
        "cost_input": cost_input,
        "desired_profit_input": desired_profit_input,
        "marketing_rate_percent": marketing_rate_percent,
        "service_allowance_rate_percent": service_allowance_rate_percent,
    })