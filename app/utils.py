def format_salary_range(low: float | None, high: float | None) -> str:
    def format_salary(value: float | None) -> str:
        return f"${value:,.2f}" if value is not None else "N/A"

    formatted_low = format_salary(low)
    formatted_high = format_salary(high)
    
    if formatted_low == "N/A" and formatted_high == "N/A":
        return "N/A"
    elif formatted_low == "N/A":
        return f"Up to {formatted_high}"
    elif formatted_high == "N/A":
        return f"{formatted_low}+"
    elif low == high:
        return formatted_low
    else:
        return f"{formatted_low} - {formatted_high}"