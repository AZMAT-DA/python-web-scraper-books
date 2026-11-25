
import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

books = []

EXPECTED_BOOKS = 1000
EXPECTED_PER_PAGE = 20

# Scrape all 50 pages
for page in range(1, 51):

    url = BASE_URL.format(page)

    print(f"Scraping page {page}...")

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    book_items = soup.select("article.product_pod")

    # Check books found on this page
    if len(book_items) != EXPECTED_PER_PAGE:
        print(
            f"WARNING: Page {page} has "
            f"{len(book_items)} books instead of "
            f"{EXPECTED_PER_PAGE}"
        )

    for book in book_items:

        title_tag = book.select_one("h3 a")
        price_tag = book.select_one(".price_color")
        availability_tag = book.select_one(".availability")

        title = title_tag["title"].strip() if title_tag else ""
        price = price_tag.get_text(strip=True) if price_tag else ""
        availability = (
            availability_tag.get_text(strip=True)
            if availability_tag else ""
        )

        books.append({
            "Title": title,
            "Price": price,
            "Availability": availability
        })


# ---------------------------------
# DATA QUALITY CHECKS
# ---------------------------------

print("\n========== DATA QUALITY REPORT ==========")

# Check 1: Total rows
total_books = len(books)

print(f"Total books collected: {total_books}")

if total_books == EXPECTED_BOOKS:
    print("PASS: Expected row count received.")
else:
    print("WARNING: Row count does not match expected count.")


# Check 2: Empty prices
empty_prices = sum(
    1 for book in books if not book["Price"]
)

print(f"Books with empty prices: {empty_prices}")

if empty_prices == 0:
    print("PASS: No empty prices found.")
else:
    print("WARNING: Some books have missing prices.")


# Check 3: Empty titles
empty_titles = sum(
    1 for book in books if not book["Title"]
)

print(f"Books with empty titles: {empty_titles}")


# ---------------------------------
# SAVE CSV FILE
# ---------------------------------

with open("all_books_checked.csv", "w", newline="", encoding="utf-8") as file:

    fieldnames = ["Title", "Price", "Availability"]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(books)

print("\nCSV file saved: all_books_checked.csv")
print("========================================")
