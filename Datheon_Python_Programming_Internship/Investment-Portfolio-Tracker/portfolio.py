
import csv
import os
from datetime import datetime
import yfinance as yf

# File names
DATASET_FILE = "portfoliyo.csv"
OUTPUT_FILE = "portfolio_summary.csv"


# Load company information from the provided dataset
def load_companies():
    companies = {}

    with open(DATASET_FILE, "r", encoding="utf-8-sig") as file:
        lines = [
            line for line in file
            if line.strip() and not line.strip().startswith("```")
        ]

        reader = csv.DictReader(lines)

        for row in reader:
            symbol = row["Symbol"].strip().upper()
            company = row["Security"].strip()

            companies[symbol] = company

    return companies


# Get the latest available stock price
def get_current_price(symbol):

    # Yahoo Finance uses a hyphen for some ticker symbols
    yahoo_symbol = symbol.replace(".", "-")

    stock = yf.Ticker(yahoo_symbol)

    # First try to get the latest intraday price
    data = stock.history(period="1d", interval="1m")

    # If intraday data is unavailable, use daily closing data
    if data.empty or data["Close"].dropna().empty:
        data = stock.history(period="5d", interval="1d")

    if data.empty or data["Close"].dropna().empty:
        raise ValueError("Stock price is not available.")

    return float(data["Close"].dropna().iloc[-1])


# Accept a positive number
def get_positive_number(message):
    while True:
        try:
            value = float(input(message))

            if value <= 0:
                print("Please enter a number greater than zero.")
            else:
                return value

        except ValueError:
            print("Please enter a valid number.")


# Save portfolio information in CSV
def save_to_csv(portfolio):

    fields = [
        "Date",
        "Symbol",
        "Company",
        "Buy Price",
        "Quantity",
        "Current Price",
        "Invested Amount",
        "Current Value",
        "Profit/Loss",
        "Gain/Loss Percentage"
    ]

    file_exists = (
        os.path.exists(OUTPUT_FILE)
        and os.path.getsize(OUTPUT_FILE) > 0
    )

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        if not file_exists:
            writer.writeheader()

        for symbol, details in portfolio.items():

            invested = details["buy_price"] * details["quantity"]

            current_value = (
                details["current_price"] * details["quantity"]
            )

            profit_loss = current_value - invested

            percentage = (profit_loss / invested) * 100

            writer.writerow({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Symbol": symbol,
                "Company": details["company"],
                "Buy Price": round(details["buy_price"], 2),
                "Quantity": details["quantity"],
                "Current Price": round(details["current_price"], 2),
                "Invested Amount": round(invested, 2),
                "Current Value": round(current_value, 2),
                "Profit/Loss": round(profit_loss, 2),
                "Gain/Loss Percentage": round(percentage, 2)
            })

    print("\nPortfolio summary saved successfully!")


# Main program
def main():

    print("=" * 50)
    print("       INVESTMENT PORTFOLIO TRACKER")
    print("=" * 50)

    try:
        companies = load_companies()
        print("\nCompany dataset loaded successfully!")

    except FileNotFoundError:
        print("Dataset file not found!")
        print("Keep the dataset in the same folder as portfolio.py.")
        return

    except (KeyError, csv.Error):
        print("Dataset format is incorrect. Check its column names.")
        return

    portfolio = {}

    while True:

        symbol = input(
            "\nEnter stock ticker (or type DONE to finish): "
        ).strip().upper()

        if symbol == "DONE":
            break

        if symbol not in companies:
            print("Ticker not found in the provided dataset!")
            continue

        company = companies[symbol]

        print("Company:", company)

        buy_price = get_positive_number(
            "Enter buying price (USD): "
        )

        quantity = get_positive_number(
            "Enter number of shares: "
        )

        try:
            current_price = get_current_price(symbol)

        except Exception as error:
            print("Unable to fetch stock price:", error)
            continue

        # Store portfolio position in dictionary
        if symbol in portfolio:

            old = portfolio[symbol]

            total_quantity = old["quantity"] + quantity

            total_investment = (
                old["buy_price"] * old["quantity"]
                + buy_price * quantity
            )

            average_buy_price = total_investment / total_quantity

            portfolio[symbol] = {
                "company": company,
                "buy_price": average_buy_price,
                "quantity": total_quantity,
                "current_price": current_price
            }

        else:

            portfolio[symbol] = {
                "company": company,
                "buy_price": buy_price,
                "quantity": quantity,
                "current_price": current_price
            }

        print("Stock added successfully!")

    # Calculate portfolio results
    if not portfolio:
        print("\nNo stocks were added.")
        return

    total_invested = 0
    total_value = 0

    print("\n" + "=" * 75)
    print("                 PORTFOLIO SUMMARY")
    print("=" * 75)

    for symbol, details in portfolio.items():

        invested = details["buy_price"] * details["quantity"]

        current_value = (
            details["current_price"] * details["quantity"]
        )

        profit_loss = current_value - invested

        percentage = (profit_loss / invested) * 100

        total_invested += invested
        total_value += current_value

        print("\nStock:", symbol)
        print("Company:", details["company"])
        print("Buying Price: $", round(details["buy_price"], 2))
        print("Current Price: $", round(details["current_price"], 2))
        print("Quantity:", details["quantity"])
        print("Invested Amount: $", round(invested, 2))
        print("Current Value: $", round(current_value, 2))
        print("Profit/Loss: $", round(profit_loss, 2))
        print("Gain/Loss: ", round(percentage, 2), "%")

    total_profit_loss = total_value - total_invested

    if total_invested > 0:
        total_percentage = (
            total_profit_loss / total_invested
        ) * 100
    else:
        total_percentage = 0

    print("\n" + "=" * 75)
    print("TOTAL INVESTED: $", round(total_invested, 2))
    print("TOTAL PORTFOLIO VALUE: $", round(total_value, 2))
    print("TOTAL PROFIT/LOSS: $", round(total_profit_loss, 2))
    print("OVERALL GAIN/LOSS: ", round(total_percentage, 2), "%")
    print("=" * 75)

    save_to_csv(portfolio)


if __name__ == "__main__":
    main()
