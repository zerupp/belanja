import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from fpdf import FPDF

# 🚀 INTEGRASI GOOGLE SHEETS: Import library baru
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
USER_PIN = "030517"

# --- SETUP PAGE ---
st.set_page_config(page_title="Estimation Kewangan - ZN", page_icon="📊", layout="wide")

# 🚀 INTEGRASI GOOGLE SHEETS: Panggil connection awal-awal
conn = st.connection("gsheets", type=GSheetsConnection)

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
# FUNGSI PDF GENERATOR (Kekal sama macam asal)
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
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "1. SENARAI TRANSAKSI TERPERINCI", 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, 'TARIKH', 1, 0, 'C', 1)
    pdf.cell(80, 10, 'ITEM', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'MASUK', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'KELUAR', 1, 1, 'C', 1)
    
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

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(120, 10, "BAKI AKHIR SEKARANG:", 0, 0, 'R')
    pdf.set_text_color(0, 100, 0)
    pdf.cell(60, 10, f"RM {current_bal:.2f}", 0, 1, 'L')
    
    pdf.add_page() 
    pdf.set_text_color(0, 0, 0) 
    
    df_calc = dataframe.copy()
    df_calc['DT'] = pd.to_datetime(df_calc['Tarikh']) 
    df_calc['DateOnly'] = df_calc['DT'].dt.date
    df_calc['MonthStr'] = df_calc['DT'].dt.strftime('%B %Y')
    
    df_expenses = df_calc[df_calc['Keluar'] > 0]
    daily_stats = df_expenses.groupby('DateOnly')['Keluar'].sum().reset_index()
    monthly_stats = df_expenses.groupby('MonthStr')['Keluar'].sum().reset_index()
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "RINGKASAN PERBELANJAAN", 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "A. TOTAL BELANJA HARIAN (Daily)", 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220) 
    pdf.cell(60, 10, "TARIKH", 1, 0, 'C', 1)
    pdf.cell(60, 10, "TOTAL HANGUS (RM)", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 10)
    for index, row in daily_stats.iterrows():
        pdf.cell(60, 10, str(row['DateOnly']), 1, 0, 'C')
        pdf.cell(60, 10, f"RM {row['Keluar']:.2f}", 1, 1, 'C')
        
    pdf.ln(10)
    
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
# 🚀 INTEGRASI GOOGLE SHEETS: LOAD DATA BARU
# ==========================================
def load_data():
    # Tambah ttl=0 supaya dia tak simpan cache lama
    try:
        df = conn.read(worksheet="Transaksi", usecols=[0, 1, 2, 3], ttl=0)
        df = df.dropna(how="all") 
        if df.empty:
            df = pd.DataFrame(columns=["Tarikh", "Item", "Masuk", "Keluar"])
    except:
        df = pd.DataFrame(columns=["Tarikh", "Item", "Masuk", "Keluar"])
    
    config = {}
    try:
        # Tambah ttl=0 kat sini juga
        df_config = conn.read(worksheet="Config", usecols=[0, 1], ttl=0)
        df_config = df_config.dropna(how="all")
        if not df_config.empty:
            # Kita ambil row paling bawah (terbaru) kalau ada banyak entry
            config['budget'] = float(df_config.iloc[-1]['Budget'])
            config['target_date'] = str(df_config.iloc[-1]['Target_Date'])
    except Exception as e:
        # st.error(f"Error loading config: {e}") # Debug kalau perlu
        pass
        
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
            new_config = pd.DataFrame([{"Budget": input_duit, "Target_Date": str(input_tarikh)}])
            conn.update(worksheet="Config", data=new_config)
            st.cache_data.clear() # <--- Tambah ni
            st.rerun()
# --- FASA 2: DASHBOARD ---
else:
    initial_budget = config['budget']
    
    # Perbaiki isu tarikh dari sheets
    if len(config['target_date']) > 10:
        clean_date = config['target_date'][:10]
    else:
        clean_date = config['target_date']
    target_date_obj = datetime.strptime(clean_date, "%Y-%m-%d").date()
    
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
        
        sim_days = int(current_balance / sim_daily)
        sim_end_date = today + timedelta(days=sim_days)
        sim_extra = current_balance % sim_daily
        
        st.sidebar.markdown(f"## ⏳ **{sim_days} HARI**")
        st.sidebar.write(f"📅 Tarikh Licin: **{sim_end_date.strftime('%d %b %Y')}**")

        st.sidebar.divider()
        
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
                    # 🚀 INTEGRASI GOOGLE SHEETS: Tolak duit save ke Sheets
                    new_row = pd.DataFrame([{"Tarikh": ts, "Item": item_out, "Masuk": 0.0, "Keluar": price_out}])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(worksheet="Transaksi", data=updated_df)
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
                    # 🚀 INTEGRASI GOOGLE SHEETS: Tambah duit save ke Sheets
                    new_row = pd.DataFrame([{"Tarikh": ts, "Item": item_in, "Masuk": price_in, "Keluar": 0.0}])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(worksheet="Transaksi", data=updated_df)
                    st.balloons()
                    st.rerun()

    # SEJARAH & PDF
    st.divider()
    st.subheader("📂 Kewangan")
    
    if not df.empty:
        col_pdf1, col_pdf2, col_space = st.columns([1, 1, 3])
        
        with col_pdf1:
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
                # 🚀 INTEGRASI GOOGLE SHEETS: Delete row dari Sheets
                df_updated = df.drop(i)
                conn.update(worksheet="Transaksi", data=df_updated)
                st.rerun()
    else:
        st.info("Tiada rekod.")

    st.divider()
    
    with st.expander("⚙️ Tetapan / Ubah Tarikh"):
        st.write("### 📅 Ubah Tarikh Target")
        st.caption(f"Tarikh sekarang: {target_date_obj.strftime('%d %b %Y')}")
        new_target_date = st.date_input("Pilih Tarikh Baru:", value=target_date_obj)
        if st.button("Simpan Tarikh Baru"):
            # 🚀 INTEGRASI GOOGLE SHEETS: Update tarikh kat Sheets
            new_config = pd.DataFrame([{"Budget": initial_budget, "Target_Date": str(new_target_date)}])
            conn.update(worksheet="Config", data=new_config)
            st.rerun()
            
        st.divider()
        if st.button("FORMAT / RESET SEMUA DATA", type="primary"):
            # 🚀 INTEGRASI GOOGLE SHEETS: Clear data dalam Sheets
            conn.clear(worksheet="Transaksi")
            conn.clear(worksheet="Config")
            st.rerun()
