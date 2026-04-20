import streamlit as st
import pandas as pd
import os
from datetime import date, datetime, timedelta
from fpdf import FPDF

# --- CONFIGURATION ---
USER_PIN = "030517"

# --- SETUP PAGE ---
st.set_page_config(page_title="Estimation Kewangan - ZN", page_icon="📊", layout="wide")

# ==========================================
# 0. SISTEM KESELAMATAN (LOGIN)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 KUNCI KESELAMATAN")
    st.write("Sistem ni dikunci.")
    col1, col2 = st.columns([2,1])
    with col1:
        input_pin = st.text_input("Passcode:", type="password")
    if st.button("MASUK"):
        if input_pin == USER_PIN:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ SALAH TU BROO!")
    st.stop()

# ==========================================
# FUNGSI PDF GENERATOR (V19 UPDATED)
# ==========================================
class PDF(FPDF):
    def __init__(self, title="LAPORAN KEWANGAN"):
        super().__init__()
        self.report_title = title

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.report_title, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%d-%m-%Y %H:%M")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(dataframe, current_bal):
    pdf = PDF(title="LAPORAN PENUH & ANALISIS")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- BAHAGIAN 1: SENARAI TRANSAKSI (DETAIL) ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "1. SENARAI TRANSAKSI TERPERINCI", 0, 1, 'L')
    
    # Table Header
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, 'TARIKH', 1, 0, 'C', 1)
    pdf.cell(80, 10, 'ITEM', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'MASUK', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'KELUAR', 1, 1, 'C', 1)
    
    # Table Body
    pdf.set_font('Arial', '', 10)
    for index, row in dataframe.iterrows():
        item_text = str(row['Item']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(40, 10, str(row['Tarikh']), 1)
        pdf.cell(80, 10, item_text[:35], 1)
        
        if row['Masuk'] > 0:
            pdf.cell(30, 10, f"{row['Masuk']:.2f}", 1, 0, 'R')
            pdf.cell(30, 10, "-", 1, 1, 'C')
        else:
            pdf.cell(30, 10, "-", 1, 0, 'C')
            pdf.cell(30, 10, f"{row['Keluar']:.2f}", 1, 1, 'R')

    # Total Balance
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(120, 10, "BAKI AKHIR SEKARANG:", 0, 0, 'R')
    pdf.set_text_color(0, 100, 0)
    pdf.cell(60, 10, f"RM {current_bal:.2f}", 0, 1, 'L')
    
    # --- BAHAGIAN 2: ANALISIS GROUPING (NEW!) ---
    pdf.add_page() # Masuk page baru supaya kemas
    pdf.set_text_color(0, 0, 0) # Reset warna hitam
    
    # Proses Data (Pandas Magic)
    df_calc = dataframe.copy()
    # Convert string tarikh ke object datetime
    df_calc['DT'] = pd.to_datetime(df_calc['Tarikh']) 
    df_calc['DateOnly'] = df_calc['DT'].dt.date
    df_calc['MonthStr'] = df_calc['DT'].dt.strftime('%B %Y')
    
    # Filter: Kita cuma nak kira DUIT KELUAR (Belanja)
    df_expenses = df_calc[df_calc['Keluar'] > 0]
    
    # Grouping Harian
    daily_stats = df_expenses.groupby('DateOnly')['Keluar'].sum().reset_index()
    
    # Grouping Bulanan
    monthly_stats = df_expenses.groupby('MonthStr')['Keluar'].sum().reset_index()
    
    # --- TABLE A: TOTAL HARIAN ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "RINGKASAN PERBELANJAAN", 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "A. TOTAL BELANJA HARIAN (Daily)", 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220) # Kelabu cair
    pdf.cell(60, 10, "TARIKH", 1, 0, 'C', 1)
    pdf.cell(60, 10, "TOTAL HANGUS (RM)", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 10)
    for index, row in daily_stats.iterrows():
        pdf.cell(60, 10, str(row['DateOnly']), 1, 0, 'C')
        pdf.cell(60, 10, f"RM {row['Keluar']:.2f}", 1, 1, 'C')
        
    pdf.ln(10)
    
    # --- TABLE B: TOTAL BULANAN ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "B. TOTAL BELANJA BULANAN (Monthly)", 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(60, 10, "BULAN", 1, 0, 'C', 1)
    pdf.cell(60, 10, "TOTAL HANGUS (RM)", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 10)
    for index, row in monthly_stats.iterrows():
        pdf.cell(60, 10, str(row['MonthStr']), 1, 0, 'C')
        pdf.cell(60, 10, f"RM {row['Keluar']:.2f}", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

def create_expense_pdf(dataframe):
    df_expense = dataframe[dataframe['Keluar'] > 0]
    total_expense = df_expense['Keluar'].sum()

    pdf = PDF(title="REKOD DUIT KELUAR")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(255, 200, 200) 
    pdf.cell(40, 10, 'TARIKH', 1, 0, 'C', 1)
    pdf.cell(100, 10, 'BUTIRAN BELANJA', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'HARGA (RM)', 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 10)
    for index, row in df_expense.iterrows():
        item_text = str(row['Item']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(40, 10, str(row['Tarikh']), 1)
        pdf.cell(100, 10, item_text[:45], 1)
        pdf.cell(40, 10, f"{row['Keluar']:.2f}", 1, 1, 'R')

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(140, 10, "JUMLAH BELANJA:", 0, 0, 'R')
    pdf.set_text_color(180, 0, 0)
    pdf.cell(40, 10, f"RM {total_expense:.2f}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# LOAD DATA
# ==========================================
DATA_FILE = 'data_survival.csv'
CONFIG_FILE = 'config_survival.txt'

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Tarikh", "Item", "Masuk", "Keluar"])
        df.to_csv(DATA_FILE, index=False)
    else:
        df = pd.read_csv(DATA_FILE)
        if "Masuk" not in df.columns:
            df = pd.DataFrame(columns=["Tarikh", "Item", "Masuk", "Keluar"])
    
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                config['budget'] = float(lines[0].strip())
                config['target_date'] = lines[1].strip()
    return df, config

# ==========================================
# MAIN APP
# ==========================================
st.title("🤕 Estimation Duit")

with st.sidebar:
    if st.button("🔒 LOGOUT", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()

df, config = load_data()

# --- FASA 1: SETUP ---
if not config:
    st.warning("⚠️ Setup Misi Baru.")
    with st.form("setup_form"):
        input_duit = st.number_input("Duit Bersih Di Tangan (RM):", min_value=0.0, step=0.1, format="%.2f")
        input_tarikh = st.date_input("Target Hari:", min_value=date.today())
        submitted = st.form_submit_button("MULA")
        if submitted:
            with open(CONFIG_FILE, "w") as f:
                f.write(f"{input_duit}\n")
                f.write(f"{input_tarikh}")
            st.rerun()

# --- FASA 2: DASHBOARD ---
else:
    initial_budget = config['budget']
    target_date_obj = datetime.strptime(config['target_date'], "%Y-%m-%d").date()
    
    total_masuk = df['Masuk'].sum()
    total_keluar = df['Keluar'].sum()
    current_balance = (initial_budget + total_masuk) - total_keluar
    
    today = date.today()
    days_left = (target_date_obj - today).days
    
    if days_left <= 0:
        daily_budget = 0
        status_msg = "MERDEKA!"
    else:
        daily_budget = current_balance / days_left
        status_msg = f"RM {daily_budget:.2f} /hari"

    # ==========================================
    # SIDEBAR: SIMULASI (HARI UTAMA)
    # ==========================================
    
    if current_balance > 0:
        st.sidebar.header("🧮 Simulation DUIT")
        st.sidebar.caption("Tarik slider untuk tengok realiti:")
        
        sim_daily = st.sidebar.slider("Belanja Harian (RM):", 1.0, 50.0, 5.0, step=0.5)
        
        # LOGIC PENGIRAAN
        sim_days = int(current_balance / sim_daily)
        sim_end_date = today + timedelta(days=sim_days)
        sim_extra = current_balance % sim_daily
        
        # DISPLAY UTAMA (HARI)
        st.sidebar.markdown(f"## ⏳ **{sim_days} HARI**")
        st.sidebar.write(f"📅 Tarikh Licin: **{sim_end_date.strftime('%d %b %Y')}**")
        #st.sidebar.caption(f"Syiling baki: RM {sim_extra:.2f}")

        st.sidebar.divider()
        
        # Check vs Target (Merah/Hijau sekadar info)
        if sim_days < days_left:
            amount_needed = (sim_daily * days_left) - current_balance
            st.sidebar.error(
                f"🚨 **TAK CUKUP!**\n"
                f"Target exam lagi {days_left} hari.\n"
                f"Defisit: **-RM {amount_needed:.2f}**"
            )
        else:
            amount_left = current_balance - (sim_daily * days_left)
            st.sidebar.success(
                f"✅ **LEPAS TARGET!**\n"
                f"Extra hujung sem: **+RM {amount_left:.2f}**"
            )
            
    else:
        st.sidebar.error("Duit dah habis bro!")

    # HUD UTAMA
    col1, col2, col3 = st.columns(3)
    col1.metric("Baki Nyawa", f"RM {current_balance:.2f}")
    col2.metric("Hari Tinggal", f"{days_left}")
    col3.metric("Limit Sehari", status_msg)

    if days_left > 0 and current_balance > 0:
        if daily_budget < 5.00:
            st.error(f"💀 BAHAYA: RM{daily_budget:.2f}. Telur & Kicap.")
        elif daily_budget < 8.00:
            st.warning(f"🟠 BERJAGA: RM{daily_budget:.2f}. Masak.")
        else:
            st.success(f"🟢 OKAY: RM{daily_budget:.2f}. Sedap.")

    st.divider()

    # INPUT DATA
    st.subheader("📝 Rekod Transaksi")
    tab_keluar, tab_masuk = st.tabs(["💸 DUIT KELUAR", "💰 DUIT MASUK"])
    
    with tab_keluar:
        with st.form("expense"):
            c1, c2 = st.columns([3, 1])
            item_out = c1.text_input("Beli apa?")
            price_out = c2.number_input("Harga (RM)", min_value=0.0, step=0.1, format="%.2f", key="p_out")
            if st.form_submit_button("🔥 TOLAK BAKI", use_container_width=True):
                if item_out and price_out > 0:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_row = pd.DataFrame({"Tarikh": [ts], "Item": [item_out], "Masuk": [0.0], "Keluar": [price_out]})
                    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    st.toast("✅ Disimpan")
                    st.rerun()

    with tab_masuk:
        with st.form("income"):
            c1, c2 = st.columns([3, 1])
            item_in = c1.text_input("Duit dari mana?")
            price_in = c2.number_input("Jumlah (RM)", min_value=0.0, step=0.1, format="%.2f", key="p_in")
            if st.form_submit_button("💚 TAMBAH DUIT", type="primary", use_container_width=True):
                if item_in and price_in > 0:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_row = pd.DataFrame({"Tarikh": [ts], "Item": [item_in], "Masuk": [price_in], "Keluar": [0.0]})
                    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    st.balloons()
                    st.rerun()

    # SEJARAH & PDF
    st.divider()
    st.subheader("📂 Kewangan")
    
    if not df.empty:
        col_pdf1, col_pdf2, col_space = st.columns([1, 1, 3])
        
        with col_pdf1:
            # PANGGIL FUNGSI PDF BARU DI SINI
            pdf_full = create_pdf(df, current_balance)
            st.download_button("📄 Full Report + Analisa", pdf_full, f"Laporan_Lengkap_{date.today()}.pdf", "application/pdf")
            
        with col_pdf2:
            if df['Keluar'].sum() > 0:
                pdf_out = create_expense_pdf(df)
                st.download_button("💸 Report Belanja Sahaja", pdf_out, f"Rekod_Belanja_{date.today()}.pdf", "application/pdf")

        df_sorted = df.sort_index(ascending=False)
        c1, c2, c3, c4, c5 = st.columns([2, 3, 1.5, 1.5, 1])
        c1.caption("Tarikh")
        c2.caption("Item")
        c3.caption("Masuk")
        c4.caption("Keluar")
        c5.caption("Padam")
        st.divider()

        for i, row in df_sorted.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 3, 1.5, 1.5, 1])
            c1.write(row['Tarikh'])
            if row['Masuk'] > 0:
                c2.markdown(f"🟢 **{row['Item']}**")
                c3.markdown(f":green[{row['Masuk']:.2f}]")
                c4.write("-")
            else:
                c2.write(row['Item'])
                c3.write("-")
                c4.write(f"{row['Keluar']:.2f}")

            if c5.button("❌", key=f"d_{i}"):
                df = df.drop(i)
                df.to_csv(DATA_FILE, index=False)
                st.rerun()
    else:
        st.info("Tiada rekod.")

    st.divider()
    
    with st.expander("⚙️ Tetapan / Ubah Tarikh"):
        st.write("### 📅 Ubah Tarikh Target")
        st.caption(f"Tarikh sekarang: {target_date_obj.strftime('%d %b %Y')}")
        new_target_date = st.date_input("Pilih Tarikh Baru:", value=target_date_obj)
        if st.button("Simpan Tarikh Baru"):
            with open(CONFIG_FILE, "w") as f:
                f.write(f"{initial_budget}\n")
                f.write(f"{new_target_date}")
            st.rerun()
            
        st.divider()
        if st.button("FORMAT / RESET SEMUA DATA", type="primary"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            st.rerun()