import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ====== ไฟล์ฐานข้อมูล (CSV) ======
ITEMS_FILE = "items.csv"
LOCATIONS_FILE = "locations.csv"
CATEGORIES_FILE = "categories.csv"

# ====== ฟังก์ชันโหลดข้อมูล ======
def load_items():
    if os.path.exists(ITEMS_FILE):
        return pd.read_csv(ITEMS_FILE)
    return pd.DataFrame(columns=[
        "ItemID", "Name", "Category", "Location",
        "Quantity", "Unit", "MinThreshold", "UpdatedDate"
    ])

def load_locations():
    if os.path.exists(LOCATIONS_FILE):
        return pd.read_csv(LOCATIONS_FILE)
    df = pd.DataFrame({"LocationName": ["ห้องครัว", "ห้องน้ำ", "ห้องเก็บของ", "ห้องนอน"]})
    df.to_csv(LOCATIONS_FILE, index=False)
    return df

def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        return pd.read_csv(CATEGORIES_FILE)
    df = pd.DataFrame({"CategoryName": ["อาหาร/เครื่องปรุง", "ของใช้ในห้องน้ำ", "ยาและเวชภัณฑ์", "อุปกรณ์ทำความสะอาด", "อื่นๆ"]})
    df.to_csv(CATEGORIES_FILE, index=False)
    return df

def save_items(df):
    df.to_csv(ITEMS_FILE, index=False)

def save_locations(df):
    df.to_csv(LOCATIONS_FILE, index=False)

def save_categories(df):
    df.to_csv(CATEGORIES_FILE, index=False)

# ====== ตั้งค่าหน้าเว็บ ======
st.set_page_config(page_title="Home Inventory", page_icon="📦", layout="wide")

# ====== CSS แต่งหน้าตาให้ทันสมัย ======
st.markdown("""
<style>
    /* พื้นหลังหลัก */
    .main {
        background-color: #F7F9FC;
    }

    /* หัวเรื่องหลักแบบไล่เฉดสี */
    .main-header {
        background: linear-gradient(135deg, #6C63FF 0%, #4834D4 100%);
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(108, 99, 255, 0.25);
    }
    .main-header h1 {
        color: white;
        font-size: 28px;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #E8E6FF;
        margin: 4px 0 0 0;
        font-size: 14px;
    }

    /* การ์ดเมตริก */
    .metric-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        border: 1px solid #EEF0F5;
    }
    .metric-card .number {
        font-size: 34px;
        font-weight: 800;
        margin: 4px 0;
    }
    .metric-card .label {
        font-size: 13px;
        color: #8A8D9F;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-total .number { color: #4834D4; }
    .metric-low .number { color: #F39C12; }
    .metric-out .number { color: #E74C3C; }

    /* ป้ายสถานะ (Badge) */
    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-ok { background-color: #D5F5E3; color: #1E8449; }
    .badge-low { background-color: #FDEBD0; color: #B9770E; }
    .badge-out { background-color: #FADBD8; color: #C0392B; }

    /* การ์ดสินค้า */
    .item-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border-left: 5px solid #6C63FF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* หัวข้อ section */
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #2D2D3A;
        margin-bottom: 14px;
        border-bottom: 3px solid #6C63FF;
        display: inline-block;
        padding-bottom: 6px;
    }

    /* ปุ่ม Streamlit ปรับให้มนขึ้น */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #EEF0F5;
    }
</style>
""", unsafe_allow_html=True)

items_df = load_items()
locations_df = load_locations()
categories_df = load_categories()

# ====== Header หลัก ======
st.markdown("""
<div class="main-header">
    <h1>📦 Home Inventory</h1>
    <p>ระบบจัดการคลังของใช้ในบ้าน รู้ตำแหน่ง รู้จำนวน ไม่ซื้อซ้ำ</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "📂 เมนูหลัก",
    ["🏠 ภาพรวม (Dashboard)", "➕ เพิ่มสินค้าใหม่", "🔍 ค้นหา/จัดการสินค้า",
     "⚠️ ของใกล้หมด/หมด", "⚙️ จัดการสถานที่และหมวดหมู่"]
)

def get_status_badge(qty, threshold):
    if qty <= 0:
        return '<span class="badge badge-out">🔴 หมดแล้ว</span>'
    elif qty <= threshold:
        return '<span class="badge badge-low">🟠 ใกล้หมด</span>'
    else:
        return '<span class="badge badge-ok">🟢 ปกติ</span>'

# ========================================================
# หน้า 1: Dashboard
# ========================================================
if menu == "🏠 ภาพรวม (Dashboard)":
    st.markdown('<div class="section-title">ภาพรวมคลังของใช้ในบ้าน</div>', unsafe_allow_html=True)

    total_items = len(items_df)
    out_of_stock = len(items_df[items_df["Quantity"] <= 0]) if not items_df.empty else 0
    low_stock = len(items_df[(items_df["Quantity"] > 0) & (items_df["Quantity"] <= items_df["MinThreshold"])]) if not items_df.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card metric-total">
            <div class="label">รายการทั้งหมด</div>
            <div class="number">{total_items}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card metric-low">
            <div class="label">ใกล้หมด</div>
            <div class="number">{low_stock}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-out">
            <div class="label">หมดแล้ว</div>
            <div class="number">{out_of_stock}</div>
        </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">รายการสินค้าทั้งหมด</div>', unsafe_allow_html=True)

    if items_df.empty:
        st.info("ยังไม่มีข้อมูลสินค้า ลองเพิ่มสินค้าใหม่จากเมนูด้านข้างได้เลยครับ")
    else:
        for _, row in items_df.iterrows():
            badge = get_status_badge(row["Quantity"], row["MinThreshold"])
            st.markdown(f"""
            <div class="item-card">
                <b>{row['Name']}</b> &nbsp; {badge}<br>
                <span style="color:#8A8D9F; font-size:13px;">
                📍 {row['Location']} &nbsp;|&nbsp; 🏷️ {row['Category']} &nbsp;|&nbsp;
                จำนวน: <b>{row['Quantity']} {row['Unit']}</b>
                </span>
            </div>
            """, unsafe_allow_html=True)

# ========================================================
# หน้า 2: เพิ่มสินค้าใหม่
# ========================================================
elif menu == "➕ เพิ่มสินค้าใหม่":
    st.markdown('<div class="section-title">เพิ่มสิ่งของเข้าคลัง</div>', unsafe_allow_html=True)

    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("ชื่อสินค้า")
        category = st.selectbox("หมวดหมู่", categories_df["CategoryName"].tolist())
        location = st.selectbox("สถานที่จัดเก็บ", locations_df["LocationName"].tolist())

        col1, col2, col3 = st.columns(3)
        with col1:
            quantity = st.number_input("จำนวนคงเหลือ", min_value=0, value=1)
        with col2:
            unit = st.text_input("หน่วยนับ", value="ชิ้น")
        with col3:
            min_threshold = st.number_input("แจ้งเตือนเมื่อต่ำกว่า", min_value=0, value=1)

        submitted = st.form_submit_button("💾 บันทึกสินค้า", use_container_width=True)

        if submitted:
            if name.strip() == "":
                st.error("กรุณากรอกชื่อสินค้า")
            else:
                new_id = int(items_df["ItemID"].max() + 1) if not items_df.empty else 1
                new_row = pd.DataFrame([{
                    "ItemID": new_id,
                    "Name": name,
                    "Category": category,
                    "Location": location,
                    "Quantity": quantity,
                    "Unit": unit,
                    "MinThreshold": min_threshold,
                    "UpdatedDate": datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                items_df = pd.concat([items_df, new_row], ignore_index=True)
                save_items(items_df)
                st.success(f"✅ เพิ่มสินค้า '{name}' เรียบร้อยแล้ว")

# ========================================================
# หน้า 3: ค้นหา/จัดการสินค้า
# ========================================================
elif menu == "🔍 ค้นหา/จัดการสินค้า":
    st.markdown('<div class="section-title">ค้นหาและจัดการสินค้า</div>', unsafe_allow_html=True)

    if items_df.empty:
        st.info("ยังไม่มีข้อมูลสินค้า")
    else:
        c1, c2 = st.columns(2)
        with c1:
            search_text = st.text_input("🔎 ค้นหาด้วยชื่อสินค้า").lower()
        with c2:
            filter_location = st.selectbox("📍 กรองตามสถานที่", ["ทั้งหมด"] + locations_df["LocationName"].tolist())

        filtered = items_df.copy()
        if search_text:
            filtered = filtered[filtered["Name"].str.lower().str.contains(search_text)]
        if filter_location != "ทั้งหมด":
            filtered = filtered[filtered["Location"] == filter_location]

        if filtered.empty:
            st.warning("ไม่พบสินค้าตามเงื่อนไขที่ค้นหา")
        else:
            for _, row in filtered.iterrows():
                badge = get_status_badge(row["Quantity"], row["MinThreshold"])
                with st.expander(f"{row['Name']}  |  📍 {row['Location']}"):
                    st.markdown(badge, unsafe_allow_html=True)
                    st.write("")
                    st.write(f"**หมวดหมู่:** {row['Category']}")
                    st.write(f"**จำนวนคงเหลือ:** {row['Quantity']} {row['Unit']}")
                    st.write(f"**เกณฑ์แจ้งเตือน:** {row['MinThreshold']} {row['Unit']}")
                    st.write(f"**อัปเดตล่าสุด:** {row['UpdatedDate']}")

                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("➖ ใช้ 1", key=f"minus_{row['ItemID']}", use_container_width=True):
                            idx = items_df["ItemID"] == row["ItemID"]
                            if items_df.loc[idx, "Quantity"].values[0] > 0:
                                items_df.loc[idx, "Quantity"] -= 1
                                items_df.loc[idx, "UpdatedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                save_items(items_df)
                                st.rerun()
                    with b2:
                        if st.button("➕ เติม 1", key=f"plus_{row['ItemID']}", use_container_width=True):
                            idx = items_df["ItemID"] == row["ItemID"]
                            items_df.loc[idx, "Quantity"] += 1
                            items_df.loc[idx, "UpdatedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            save_items(items_df)
                            st.rerun()
                    with b3:
                        if st.button("🗑️ ลบ", key=f"del_{row['ItemID']}", use_container_width=True):
                            items_df = items_df[items_df["ItemID"] != row["ItemID"]]
                            save_items(items_df)
                            st.rerun()

# ========================================================
# หน้า 4: ของใกล้หมด/หมด
# ========================================================
elif menu == "⚠️ ของใกล้หมด/หมด":
    st.markdown('<div class="section-title">รายการที่ต้องซื้อเพิ่ม</div>', unsafe_allow_html=True)

    if items_df.empty:
        st.info("ยังไม่มีข้อมูลสินค้า")
    else:
        low_df = items_df[items_df["Quantity"] <= items_df["MinThreshold"]]
        if low_df.empty:
            st.success("🎉 ตอนนี้ไม่มีของใกล้หมดเลยครับ")
        else:
            st.warning(f"พบสินค้าที่ต้องเติม {len(low_df)} รายการ")
            for _, row in low_df.iterrows():
                badge = get_status_badge(row["Quantity"], row["MinThreshold"])
                st.markdown(f"""
                <div class="item-card">
                    <b>{row['Name']}</b> &nbsp; {badge}<br>
                    <span style="color:#8A8D9F; font-size:13px;">
                    📍 {row['Location']} &nbsp;|&nbsp; เหลือ: <b>{row['Quantity']} {row['Unit']}</b>
                    &nbsp;|&nbsp; เกณฑ์: {row['MinThreshold']} {row['Unit']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

# ========================================================
# หน้า 5: จัดการสถานที่และหมวดหมู่
# ========================================================
elif menu == "⚙️ จัดการสถานที่และหมวดหมู่":
    st.markdown('<div class="section-title">ตั้งค่าสถานที่จัดเก็บและหมวดหมู่</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📍 สถานที่จัดเก็บ", "🏷️ หมวดหมู่"])

    with tab1:
        st.table(locations_df)
        new_loc = st.text_input("➕ เพิ่มสถานที่ใหม่")
        if st.button("เพิ่มสถานที่", use_container_width=True):
            if new_loc.strip() and new_loc not in locations_df["LocationName"].values:
                locations_df = pd.concat([locations_df, pd.DataFrame([{"LocationName": new_loc}])], ignore_index=True)
                save_locations(locations_df)
                st.success(f"✅ เพิ่มสถานที่ '{new_loc}' แล้ว")
                st.rerun()

    with tab2:
        st.table(categories_df)
        new_cat = st.text_input("➕ เพิ่มหมวดหมู่ใหม่")
        if st.button("เพิ่มหมวดหมู่", use_container_width=True):
            if new_cat.strip() and new_cat not in categories_df["CategoryName"].values:
                categories_df = pd.concat([categories_df, pd.DataFrame([{"CategoryName": new_cat}])], ignore_index=True)
                save_categories(categories_df)
                st.success(f"✅ เพิ่มหมวดหมู่ '{new_cat}' แล้ว")
                st.rerun()
