import numpy as np, pandas as pd
rng = np.random.default_rng(42)

# Fictional brands & products (brand, category, product, unit price IDR per pack)
products = [
    ("Frosta Prima", "Nugget", "Chicken Nugget 500g", 42000),
    ("Frosta Prima", "Nugget", "Chicken Nugget Stick 1kg", 78000),
    ("Frosta Prima", "Sosis", "Sosis Ayam Bakar 500g", 36000),
    ("NusaBeku", "Sosis", "Sosis Sapi Jumbo 1kg", 89000),
    ("NusaBeku", "Bakso", "Bakso Sapi 50pcs", 55000),
    ("NusaBeku", "Bakso", "Bakso Ikan 500g", 32000),
    ("KulinaRia", "Dimsum", "Siomay Ayam 20pcs", 38000),
    ("KulinaRia", "Dimsum", "Hakau Udang 20pcs", 52000),
    ("KulinaRia", "Dimsum", "Lumpia Udang 10pcs", 34000),
    ("SeaMart", "Seafood", "Udang Kupas 500g", 98000),
    ("SeaMart", "Seafood", "Fillet Dori 1kg", 72000),
    ("SeaMart", "Seafood", "Otak-otak Ikan 500g", 29000),
    ("DapurBeku", "Siap Saji", "Kentang Goreng 1kg", 35000),
    ("DapurBeku", "Siap Saji", "Spring Roll Sayur 20pcs", 31000),
    ("DapurBeku", "Siap Saji", "Karaage Ayam 500g", 58000),
]
regions = {"Jabodetabek": 0.38, "Bandung": 0.17, "Surabaya": 0.20, "Semarang": 0.12, "Medan": 0.13}
channels = {"Supermarket": 0.32, "Minimarket": 0.26, "HoReCa": 0.22, "Agen/Reseller": 0.20}
customers = {
    "Supermarket": ["Mega Fresh Mart", "Sentosa Supermarket", "Harmoni Swalayan"],
    "Minimarket": ["Mini Hemat", "Toko Segar 24", "Warung Modern"],
    "HoReCa": ["Resto Nusantara", "Hotel Cendana", "Kafe Kopi Senja", "Catering Berkah"],
    "Agen/Reseller": ["Agen Beku Jaya", "Reseller Makmur", "Toko Frozen Mama"],
}
sales_reps = {"Jabodetabek": ["Rina", "Doni"], "Bandung": ["Asep"], "Surabaya": ["Siti", "Bayu"],
              "Semarang": ["Wulan"], "Medan": ["Hendra"]}

dates = pd.date_range("2026-07-01", "2026-09-30", freq="D")
brand_trend = {"Frosta Prima": 1.00, "NusaBeku": 0.98, "KulinaRia": 1.06, "SeaMart": 0.95, "DapurBeku": 1.03}
rows, inv = [], 1
for d in dates:
    m_idx = d.month - 7
    base = 38 * (1 + 0.06 * m_idx)          # overall growth month-to-month
    if d.dayofweek >= 5: base *= 1.25      # weekend peak
    if d.day <= 5: base *= 1.15            # early-month restock (payday)
    if d.month == 8 and 14 <= d.day <= 17: base *= 1.45   # HUT RI promo
    n = rng.poisson(base)
    for _ in range(n):
        p = products[rng.integers(len(products))]
        brand = p[0]
        if rng.random() > (brand_trend[brand] ** m_idx) * 0.95:  # brand trend
            continue
        region = rng.choice(list(regions), p=list(regions.values()))
        channel = rng.choice(list(channels), p=list(channels.values()))
        qty_base = {"Supermarket": 24, "Minimarket": 10, "HoReCa": 18, "Agen/Reseller": 30}[channel]
        qty = max(1, int(rng.gamma(2.0, qty_base / 2)))
        price = p[3]
        disc = rng.choice([0, 0, 0, 0.05, 0.10]) if not (d.month == 8 and 14 <= d.day <= 17) else rng.choice([0.10, 0.15])
        gross = qty * price
        net = round(gross * (1 - disc))
        cogs = round(gross * rng.uniform(0.68, 0.76))
        rows.append({
            "invoice_id": f"INV-{d:%y%m}-{inv:05d}", "tanggal": d.date(), "bulan": d.strftime("%B"),
            "hari": d.day_name(), "region": region, "sales_rep": rng.choice(sales_reps[region]),
            "channel": channel, "customer": rng.choice(customers[channel]),
            "brand": brand, "kategori": p[1], "produk": p[2], "harga_satuan": price,
            "qty": qty, "diskon_pct": disc, "penjualan_bruto": gross, "penjualan_neto": net,
            "hpp": cogs, "profit": net - cogs,
        })
        inv += 1

df = pd.DataFrame(rows)
bulan_id = {"July": "Juli", "August": "Agustus", "September": "September"}
hari_id = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis",
           "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
df["bulan"] = df["bulan"].map(bulan_id); df["hari"] = df["hari"].map(hari_id)
df.to_csv("penjualan_frozen_food_jul-sep_2026.csv", index=False)
with pd.ExcelWriter("penjualan_frozen_food_jul-sep_2026.xlsx") as w:
    df.to_excel(w, sheet_name="transaksi", index=False)

print(len(df), "rows")
g = df.groupby("bulan", sort=False).agg(neto=("penjualan_neto", "sum"), profit=("profit", "sum"), qty=("qty", "sum"), trx=("invoice_id", "count"))
print(g); print(df.groupby("brand").penjualan_neto.sum().sort_values(ascending=False))
print(df.groupby("region").penjualan_neto.sum().sort_values(ascending=False))
print(df.groupby("channel").penjualan_neto.sum().sort_values(ascending=False))
print(df[df.bulan=="September"].groupby("kategori").penjualan_neto.sum().sort_values(ascending=False))
print(df[df.bulan=="September"].groupby("produk").penjualan_neto.sum().sort_values(ascending=False).head(5))
sep = df[df.bulan=="September"].groupby("tanggal").penjualan_neto.sum()
print("Sep daily min/max", sep.min(), sep.idxmin(), sep.max(), sep.idxmax())
print("Sep brand", df[df.bulan=="September"].groupby("brand").penjualan_neto.sum().sort_values(ascending=False))
print("Aug brand", df[df.bulan=="Agustus"].groupby("brand").penjualan_neto.sum())
