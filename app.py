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

items_df = load_items()
locations_df = load_locations()
categories_df = load_categories()

st.title("📦 ระบบจัดการคลังของใช้ในบ้าน")

menu = st.sidebar.radio(
    "เมนูหลัก",
    ["🏠 ภาพรวม (Dashboard)", "➕ เพิ่มสินค้าใหม่", "🔍 ค้นหา/จัดการสินค้า",
     "⚠️ ของใกล้หมด/หมด", "⚙️ จัดการสถานที่และหมวดหมู่"]
)

# ========================================================
# หน้า 1: Dashboard
# ========================================================
if menu == "🏠 ภาพรวม (Dashboard)":
    st.header("ภาพรวมคลังของใช้ในบ้าน")

    total_items = len(items_df)
    out_of_stock = len(items_df[items_df["Quantity"] <= 0]) if not items_df.empty else 0
    low_stock = len(items_df[(items_df["Quantity"] > 0) & (items_df["Quantity"] <= items_df["MinThreshold"])]) if not items_df.empty else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนรายการทั้งหมด", total_items)
    col2.metric("ใกล้หมด", low_stock)
    col3.metric("หมดแล้ว", out_of_stock)

    st.subheader("รายการสินค้าทั้งหมด")
    if items_df.empty:
        st.info("ยังไม่มีข้อมูลสินค้า ลองเพิ่มสินค้าใหม่จากเมนูด้านข้างได้เลยครับ")
    else:
        st.dataframe(items_df, use_container_width=True)

# ========================================================
# หน้า 2: เพิ่มสินค้าใหม่
# ========================================================
elif menu == "➕ เพิ่มสินค้าใหม่":
    st.header("เพิ่มสิ่งของเข้าคลัง")

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

        submitted = st.form_submit_button("บันทึกสินค้า")

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
                st.success(f"เพิ่มสินค้า '{name}' เรียบร้อยแล้ว")

# ========================================================
# หน้า 3: ค้นหา/จัดการสินค้า
# ========================================================
elif menu == "🔍 ค้นหา/จัดการสินค้า":
    st.header("ค้นหาและจัดการสินค้า")

    if items_df.empty:
        st.info("ยังไม่มีข้อมูลสินค้า")
    else:
        c1, c2 = st.columns(2)
        with c1:
            search_text = st.text_input("ค้นหาด้วยชื่อสินค้า").lower()
        with c2:
            filter_location = st.selectbox("กรองตามสถานที่", ["ทั้งหมด"] + locations_df["LocationName"].tolist())

        filtered = items_df.copy()
        if search_text:
            filtered = filtered[filtered["Name"].str.lower().str.contains(search_text)]
        if filter_location != "ทั้งหมด":
            filtered = filtered[filtered["Location"] == filter_location]

        if filtered.empty:
            st.warning("ไม่พบสินค้าตามเงื่อนไขที่ค้นหา")
        else:
            for _, row in filtered.iterrows():
                status = "🔴 หมดแล้ว" if row["Quantity"] <= 0 else ("🟠 ใกล้หมด" if row["Quantity"] <= row["MinThreshold"] else "🟢 ปกติ")
                with st.expander(f"{row['Name']} | 📍 {row['Location']} | {status}"):
                    st.write(f"**หมวดหมู่:** {row['Category']}")
                    st.write(f"**จำนวนคงเหลือ:** {row['Quantity']} {row['Unit']}")
                    st.write(f"**เกณฑ์แจ้งเตือน:** {row['MinThreshold']} {row['Unit']}")
                    st.write(f"**อัปเดตล่าสุด:** {row['UpdatedDate']}")

                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("➖ ใช้ 1", key=f"minus_{row['ItemID']}"):
                            idx = items_df["ItemID"] == row["ItemID"]
                            if items_df.loc[idx, "Quantity"].values[0] > 0:
                                items_df.loc[idx, "Quantity"] -= 1
                                items_df.loc[idx, "UpdatedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                save_items(items_df)
                                st.rerun()
                    with b2:
                        if st.button("➕ เติม 1", key=f"plus_{row['ItemID']}"):
                            idx = items_df["ItemID"] == row["ItemID"]
                            items_df.loc[idx, "Quantity"] += 1
                            items_df.loc[idx, "UpdatedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            save_items(items_df)
                            st.rerun()
                    with b3:
                        if st.button("🗑️ ลบรายการนี้", key=f"del_{row['ItemID']}"):
                            items_df = items_df[items_df["ItemID"] != row["ItemID"]]
                            save_items(items_df)
                            st.rerun()

# ========================================================
# หน้า 4: ของใกล้หมด/หมด
# ========================================================
elif menu == "⚠️ ของใกล้หมด/หมด":
    st.header("รายการที่ต้องซื้อเพิ่ม")

    if items_df.empty:
        st.info("ยังไม่มีข้อมูลสินค้า")
    else:
        low_df = items_df[items_df["Quantity"] <= items_df["MinThreshold"]]
        if low_df.empty:
            st.success("ตอนนี้ไม่มีของใกล้หมดเลยครับ")
        else:
            st.warning(f"พบสินค้าที่ต้องเติม {len(low_df)} รายการ")
            st.dataframe(low_df, use_container_width=True)

# ========================================================
# หน้า 5: จัดการสถานที่และหมวดหมู่
# ========================================================
elif menu == "⚙️ จัดการสถานที่และหมวดหมู่":
    st.header("ตั้งค่าสถานที่จัดเก็บและหมวดหมู่")

    tab1, tab2 = st.tabs(["📍 สถานที่จัดเก็บ", "🏷️ หมวดหมู่"])

    with tab1:
        st.subheader("สถานที่จัดเก็บทั้งหมด")
        st.table(locations_df)
        new_loc = st.text_input("เพิ่มสถานที่ใหม่")
        if st.button("เพิ่มสถานที่"):
            if new_loc.strip() and new_loc not in locations_df["LocationName"].values:
                locations_df = pd.concat([locations_df, pd.DataFrame([{"LocationName": new_loc}])], ignore_index=True)
                save_locations(locations_df)
                st.success(f"เพิ่มสถานที่ '{new_loc}' แล้ว")
                st.rerun()

    with tab2:
        st.subheader("หมวดหมู่ทั้งหมด")
        st.table(categories_df)
        new_cat = st.text_input("เพิ่มหมวดหมู่ใหม่")
        if st.button("เพิ่มหมวดหมู่"):
            if new_cat.strip() and new_cat not in categories_df["CategoryName"].values:
                categories_df = pd.concat([categories_df, pd.DataFrame([{"CategoryName": new_cat}])], ignore_index=True)
                save_categories(categories_df)
                st.success(f"เพิ่มหมวดหมู่ '{new_cat}' แล้ว")
                st.rerun()