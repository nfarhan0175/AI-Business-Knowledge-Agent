import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")

def load_product_documents():
    products = pd.read_csv(PROCESSED_DIR / "products.csv")
    products = products.head(200)
    documents = []

    for _, row in products.iterrows():
        category = row["product_category_name"]
        document = f"""
Product Information

Product ID: {row["product_id"]}
Category: {category}
Product Name Length: {row["product_name_lenght"]}
Product Description Length: {row["product_description_lenght"]}
Product Photos Quantity: {row["product_photos_qty"]}
Product Weight: {row["product_weight_g"]} grams
Product Length: {row["product_length_cm"]} cm
Product Height: {row["product_height_cm"]} cm
Product Width: {row["product_width_cm"]} cm
""".strip()
        documents.append({
            "id": f"product_{row['product_id']}",
            "text": document,
            "metadata": {
                "source": "products",
                "product_id": row["product_id"],
                "category": str(category)
            }
        })
    return documents

if __name__ == "__main__":
    documents = load_product_documents()
    print("Total documents:", len(documents))

    print("\nFirst document:")
    print(documents[0]["text"])

    print("\nMetadata:")
    print(documents[0]["metadata"])