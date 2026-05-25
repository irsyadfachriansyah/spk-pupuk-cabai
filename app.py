import streamlit as st
import pandas as pd

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Rekomendasi Pupuk - Sujahtera Farmers", page_icon="🌶️", layout="wide")

# --- 2. ENGINE PERHITUNGAN AHP-SAW ---
def hitung_ahp_saw_organik(fase_pilihan, luas_lahan):
    BIAYA_TAMBAHAN_TETAP = 5000 
    
    if fase_pilihan == 'Vegetatif':
        bobot = [0.1222, 0.4233, 0.2273, 0.2273]
        matriks = {
            'POC Urin Kelinci (Cair)': {'h': 10000, 'n': [10000, 5, 2, 2], 'dos': 0.08},
            'Pupuk Kandang Ayam (Padat)': {'h': 5000, 'n': [5000, 4, 3, 2], 'dos': 0.25},
            'Pupuk Guano Kelelawar (Padat)': {'h': 20000, 'n': [20000, 2, 5, 2], 'dos': 0.25},
            'Abu Janjang Kelapa Sawit (Padat)': {'h': 7000, 'n': [7000, 1, 2, 5], 'dos': 0.25}
        }
    else:
        bobot = [0.1088, 0.1893, 0.3509, 0.3509]
        matriks = {
            'POC Urin Kelinci (Cair)': {'h': 10000, 'n': [10000, 3, 3, 3], 'dos': 0.08},
            'Pupuk Kandang Ayam (Padat)': {'h': 5000, 'n': [5000, 2, 3, 2], 'dos': 0.25},
            'Pupuk Guano Kelelawar (Padat)': {'h': 20000, 'n': [20000, 1, 5, 3], 'dos': 0.25},
            'Abu Janjang Kelapa Sawit (Padat)': {'h': 7000, 'n': [7000, 1, 3, 5], 'dos': 0.25}
        }
    
    min_c1 = min([v['n'][0] for v in matriks.values()])
    max_c2, max_c3, max_c4 = max([v['n'][1] for v in matriks.values()]), max([v['n'][2] for v in matriks.values()]), max([v['n'][3] for v in matriks.values()])
    
    ranking, detail = [], []
    for nama, data in matriks.items():
        v = data['n']
        r = [round(min_c1/v[0], 2), round(v[1]/max_c2, 2), round(v[2]/max_c3, 2), round(v[3]/max_c4, 2)]
        skor = round((r[0]*bobot[0]) + (r[1]*bobot[1]) + (r[2]*bobot[2]) + (r[3]*bobot[3]), 4)
        modal = int((luas_lahan * data['dos']) * data['h']) + BIAYA_TAMBAHAN_TETAP
        ranking.append({"Pupuk": nama, "Skor": skor, "Harga/Kg": data['h'], "Estimasi Modal": modal})
        detail.append({"Nama": nama, "R": r, "Skor": skor})
    
    ranking.sort(key=lambda x: x['Skor'], reverse=True)
    return bobot, ranking, detail

# --- 3. DATA KRITERIA AHP ---
data_bobot_ahp = pd.DataFrame({
    "Kriteria": ["Biaya (C1)", "Nitrogen (N - C2)", "Fosfor (P - C3)", "Kalium (K - C4)"],
    "Bobot (Vegetatif)": [0.1222, 0.4233, 0.2273, 0.2273],
    "Bobot (Generatif)": [0.1088, 0.1893, 0.3509, 0.3509]
})

data_info = {
    'POC Urin Kelinci (Cair)': {"kelebihan": "Zat pengatur tumbuh (auxin/sitokinin) alami sangat tinggi.", "kekurangan": "Perlu fermentasi tepat agar tidak berbau menyengat.", "buat": "10L Urin + 100ml EM4 + 100ml Tetes Tebu. Fermentasi 14 hari.", "aplikasi": "Dosis: 50ml/10L air. Aplikasi pagi sebelum jam 09.00."},
    'Pupuk Kandang Ayam (Padat)': {"kelebihan": "Nitrogen tinggi; murah; struktur tanah gembur.", "kekurangan": "Rawan membawa biji gulma jika belum matang.", "buat": "Kotoran ayam + sekam (1:1), siram EM4, tutup 4 minggu.", "aplikasi": "Tabur 1-2 genggam di radius 10cm dari batang."},
    'Pupuk Guano Kelelawar (Padat)': {"kelebihan": "Kaya Fosfor (P) alami untuk pembungaan.", "kekurangan": "Harga relatif mahal; ketersediaan terbatas.", "buat": "Guano murni + dedak (10:1), fermentasi lembap 1 minggu.", "aplikasi": "1 sdm di lubang tanam (radius 10cm)."},
    'Abu Janjang Kelapa Sawit (Padat)': {"kelebihan": "Kalium (K) organik tinggi; memperkuat daya tahan buah.", "kekurangan": "pH sangat basa (bisa merusak tanah jika berlebihan).", "buat": "Bakar limbah janjang hingga jadi abu, dinginkan 24 jam.", "aplikasi": "100gr/10L air (siram) atau tabur tipis di permukaan tanah."}
}

# --- 4. TAMPILAN WEB ---
st.title("Sistem Rekomendasi Pupuk - Sujahtera Farmers")
st.subheader("Optimasi Fase Pertumbuhan Tanaman Cabai dengan Metode AHP-SAW")

with st.expander("Lihat Detail Bobot Kriteria (Metode AHP)"):
    st.write("Bobot kriteria yang digunakan berdasarkan analisis keputusan untuk kelompok tani:")
    st.table(data_bobot_ahp)

with st.sidebar:
    st.header("Input Data Lahan")
    fase = st.selectbox("Pilih Fase:", ("Vegetatif", "Generatif"))
    luas = st.number_input("Luas Lahan (m²):", value=500)
    btn = st.button("Hitung Analisis Organik", use_container_width=True)

if btn:
    bobot, rank, det = hitung_ahp_saw_organik(fase, luas)
    st.success(f"Rekomendasi Utama: {rank[0]['Pupuk']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Skor Kualitas", rank[0]['Skor'])
    c2.metric("Harga Satuan", f"Rp {rank[0]['Harga/Kg']:,}")
    c3.metric("Estimasi Modal Total", f"Rp {rank[0]['Estimasi Modal']:,}")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Tabel Peringkat")
        st.dataframe(pd.DataFrame(rank), use_container_width=True, hide_index=True)
    with col_b:
        st.subheader("Grafik Prioritas")
        st.bar_chart(pd.DataFrame([r['Skor'] for r in rank], index=[r['Pupuk'] for r in rank]), color="#22C55E")

    st.subheader("Transparansi Perhitungan")
    for d in det:
        with st.expander(f"Detail Perhitungan: {d['Nama']}"):
            st.latex(rf"\text{{{d['Nama']}}} : ({d['R'][0]:.2f} \times {bobot[0]}) + ({d['R'][1]:.2f} \times {bobot[1]}) + ({d['R'][2]:.2f} \times {bobot[2]}) + ({d['R'][3]:.2f} \times {bobot[3]}) = {d['Skor']}")

    st.subheader("SOP Lengkap & Analisis Teknis")
    df_sop = pd.DataFrame([{"Pupuk": k, "Kelebihan": v["kelebihan"], "Kekurangan": v["kekurangan"], "Cara Buat": v["buat"], "Cara Aplikasi": v["aplikasi"]} for k, v in data_info.items()])
    st.table(df_sop)
else:
    st.info("Selamat Datang! Masukkan Luas Lahan di sidebar kiri, lalu klik **Hitung Analisis Organik**.")

st.markdown("---")
st.markdown("© 2026 - Sistem Pendukung Keputusan untuk Kelompok Tani Sujahtera Farmers")