import requests

API_URL = "https://dummyjson.com/products"

response = requests.get(
    API_URL,
    params={"limit": 30, "skip": 0},
    timeout=30
)

response.raise_for_status()

data = response.json()

print("Total products:", data["total"])
print("Products retrieved:", len(data["products"]))

for product in data["products"][:5]:
    print(
        product["id"],
        product["title"],
        product["category"],
        product["price"]
    )