import pandas as pd
import numpy as np


def load_data() -> pd.DataFrame:
    """
    Load the Online Retail II dataset (UCI).
    Contains ~1M transactions from a UK-based e-commerce store (2009–2011).
    Falls back to synthetic data if the URL is unavailable.
    """
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/online_retail.csv"

    try:
        print("Loading dataset...")
        df = pd.read_csv(url, encoding="ISO-8859-1")
        df = _clean(df)
        print(f"✅ Loaded {len(df):,} transactions")
        return df
    except Exception as e:
        print(f"⚠️  Could not load from URL ({e}). Generating synthetic data...")
        return _synthetic()


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the raw dataset."""
    df.columns = [c.strip() for c in df.columns]

    # Rename to consistent snake_case
    rename = {
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Parse dates
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

    # Drop nulls in key columns
    df = df.dropna(subset=["customer_id", "invoice_date"])

    # Remove cancellations (invoices starting with 'C')
    df = df[~df["invoice_no"].astype(str).str.startswith("C")]

    # Remove returns / bad rows
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]

    # Revenue column
    df["revenue"] = df["quantity"] * df["unit_price"]

    # Date parts
    df["year"] = df["invoice_date"].dt.year
    df["month"] = df["invoice_date"].dt.month
    df["month_name"] = df["invoice_date"].dt.strftime("%b")
    df["year_month"] = df["invoice_date"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["invoice_date"].dt.day_name()

    df["customer_id"] = df["customer_id"].astype(int).astype(str)

    return df.reset_index(drop=True)


def _synthetic() -> pd.DataFrame:
    """Generate realistic synthetic retail data as fallback."""
    np.random.seed(42)
    n = 50_000

    countries = ["United Kingdom"] * 80 + ["Germany", "France", "Netherlands", "Spain", "Belgium"] * 4
    products = [
        "WHITE HANGING HEART T-LIGHT HOLDER", "REGENCY CAKESTAND 3 TIER",
        "JUMBO BAG RED RETROSPOT", "PARTY BUNTING", "LUNCH BAG RED RETROSPOT",
        "SET OF 3 CAKE TINS PANTRY DESIGN", "ALARM CLOCK BAKELIKE PINK",
        "NATURAL SLATE HEART CHALKBOARD", "RABBIT NIGHT LIGHT",
        "CERAMIC STORAGE JAR", "GLASS STAR FROSTED T-LIGHT HOLDER",
        "SPOTTY BUNTING", "CHRISTMAS TREE LIGHTS",
    ]

    dates = pd.date_range("2010-01-01", "2011-12-31", freq="H")
    invoice_dates = pd.to_datetime(np.random.choice(dates, n))

    df = pd.DataFrame({
        "invoice_no": np.random.randint(500000, 600000, n).astype(str),
        "stock_code": np.random.randint(10000, 99999, n).astype(str),
        "description": np.random.choice(products, n),
        "quantity": np.random.randint(1, 20, n),
        "invoice_date": invoice_dates,
        "unit_price": np.round(np.random.uniform(0.5, 25.0, n), 2),
        "customer_id": np.random.randint(12000, 18000, n).astype(str),
        "country": np.random.choice(countries, n),
    })

    df["revenue"] = df["quantity"] * df["unit_price"]
    df["year"] = df["invoice_date"].dt.year
    df["month"] = df["invoice_date"].dt.month
    df["month_name"] = df["invoice_date"].dt.strftime("%b")
    df["year_month"] = df["invoice_date"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["invoice_date"].dt.day_name()

    return df
