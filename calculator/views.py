from django.shortcuts import render
from .services import calculate_selling_price


def parse_money(value):
    if not value:
        return 0

    cleaned_value = value.replace(",", "").strip()
    return float(cleaned_value)


def calculator_home(request):
    result = None
    cost_input = ""
    desired_profit_input = ""

    if request.method == "POST":
        cost_input = request.POST.get("cost", "")
        desired_profit_input = request.POST.get("desired_profit", "")

        cost = parse_money(cost_input)
        desired_profit = parse_money(desired_profit_input)

        result = calculate_selling_price(cost, desired_profit)

    return render(request, "home.html", {
        "result": result,
        "cost_input": cost_input,
        "desired_profit_input": desired_profit_input,
    })