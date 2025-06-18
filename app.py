import pandas as pd
import streamlit as st

# --- Load and preprocess data ---
df = pd.read_csv("latest_laptops.csv", encoding='ISO-8859-1')
df['Ram'] = df['Ram'].str.replace("GB", "").astype(int)
df['Price_INR'] = (df['Price_euros'] * 90).astype(int)

df[['Storage_Type', 'Storage_Size']] = df['Memory'].str.extract(r'([A-Za-z]+)\s?(\d+\.?\d*)?')
df['Storage_Size'] = pd.to_numeric(df['Storage_Size'], errors='coerce')

def simplify_cpu(cpu):
    if 'i7' in cpu: return 'i7'
    if 'i5' in cpu: return 'i5'
    if 'i3' in cpu: return 'i3'
    if 'Ryzen 7' in cpu: return 'Ryzen 7'
    if 'Ryzen 5' in cpu: return 'Ryzen 5'
    return 'Other'
df['CPU_Brand'] = df['Cpu'].apply(simplify_cpu)

# --- Streamlit Page Config ---
st.set_page_config(page_title="🎓 Laptop Selector for Students", layout="wide")

# --- Custom Style ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Segoe UI', sans-serif; }
    .block-container { padding-top: 2rem; }
    .title { font-size: 2.5rem; font-weight: 700; color: #1f4e79; }
    .subtitle { font-size: 1.2rem; color: #666; }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="title">🎓 Smart Laptop Selector</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find the perfect laptop based on your needs, budget, and preferences.</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Filters Layout ---
st.subheader("🛠️ Filter Your Preferences")

col1, col2, col3 = st.columns(3)

with col1:
    budget = st.slider("💰 Max Budget (₹)", 20000, 200000, 60000, step=5000)
    usage = st.radio("🎯 Primary Use", ['coding', 'gaming', 'design', 'general'])

with col2:
    brand = st.multiselect("🏷️ Brands", options=sorted(df['Company'].unique()))
    cpu_type = st.multiselect("🧠 CPU Type", options=sorted(df['CPU_Brand'].unique()))
    ram = st.selectbox("🔢 Minimum RAM (GB)", sorted(df['Ram'].unique()))

with col3:
    storage_type = st.multiselect("💾 Storage Type", options=df['Storage_Type'].dropna().unique())
    screen_range = st.slider("📏 Screen Size (inches)", float(df['Inches'].min()), float(df['Inches'].max()), (13.0, 17.0))
    product_search = st.text_input("🔎 Search by Product Name (optional)")

# --- Filtering Logic ---
filtered = df.copy()
filtered = filtered[(filtered['Price_INR'] <= budget) & (filtered['Ram'] >= ram)]
filtered = filtered[filtered['Inches'].between(screen_range[0], screen_range[1])]

if brand:
    filtered = filtered[filtered['Company'].isin(brand)]

if cpu_type:
    filtered = filtered[filtered['CPU_Brand'].isin(cpu_type)]

if storage_type:
    filtered = filtered[filtered['Storage_Type'].isin(storage_type)]

if product_search:
    filtered = filtered[filtered['Product'].str.contains(product_search, case=False, na=False)]

if usage == 'coding':
    filtered = filtered[filtered['CPU_Brand'].isin(['i5', 'i7', 'Ryzen 5', 'Ryzen 7'])]
elif usage == 'gaming':
    filtered = filtered[filtered['Gpu'].str.contains("NVIDIA|RTX", na=False)]
elif usage == 'design':
    filtered = filtered[filtered['Gpu'].str.contains("NVIDIA|AMD|RTX", na=False)]

# --- Display Results ---
st.markdown("### 🎉 Top Laptop Recommendations")
if not filtered.empty:
    st.dataframe(
        filtered[['Company', 'Product', 'Ram', 'CPU_Brand', 'Gpu', 'Storage_Type', 'Inches', 'Price_INR']]
        .sort_values(by='Price_INR')
        .reset_index(drop=True)
        .head(10)
    )
else:
    st.warning("❌ No matching laptops found. Try changing your filters.")
    # --- Disclaimer ---
st.info("📌 **Disclaimer:** Laptop prices shown here are based on past data and may vary on online platforms or local stores.")


st.markdown("---")
st.caption("Made with ❤️ by Bhavya • Helping students buy smarter 💻")
