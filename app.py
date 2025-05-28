import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
from io import BytesIO
import base64

# Konfigurasi halaman
st.set_page_config(
        page_title="Color Palette Generator",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def rgb_to_hex(rgb):
    """Konversi RGB ke format HEX"""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def extract_dominant_colors(image, num_colors=5):
    """Ekstrak warna dominan dari gambar menggunakan K-Means clustering"""
    # Konversi gambar ke array numpy
    img_array = np.array(image)
    
    # Reshape gambar menjadi array 2D (pixel, RGB)
    pixels = img_array.reshape(-1, 3)
    
    # Hapus pixel yang terlalu gelap atau terlalu terang untuk hasil yang lebih baik
    mask = np.all(pixels > 20, axis=1) & np.all(pixels < 235, axis=1)
    pixels = pixels[mask]
    
    # Gunakan K-Means untuk menemukan warna dominan
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Dapatkan warna dominan
    colors = kmeans.cluster_centers_
    
    # Hitung persentase setiap warna
    labels = kmeans.labels_
    percentages = []
    for i in range(num_colors):
        count = np.sum(labels == i)
        percentage = (count / len(labels)) * 100
        percentages.append(percentage)
    
    # Urutkan berdasarkan persentase
    color_data = list(zip(colors, percentages))
    color_data.sort(key=lambda x: x[1], reverse=True)
    
    return color_data

def display_color_palette(color_data):
    """Tampilkan palet warna dalam format yang menarik"""
    html_content = "<div style='text-align: center; margin: 2rem 0;'>"
    
    for i, (color, percentage) in enumerate(color_data):
        hex_color = rgb_to_hex(color)
        rgb_str = f"rgb({int(color[0])}, {int(color[1])}, {int(color[2])})"
        
        html_content += (
            f"<div class='color-box' style='background-color: {hex_color};'>"
            f"<div style='height: 80px; display: flex; align-items: center; justify-content: center; color: {'white' if sum(color) < 400 else 'black'};'>"
            f"<strong>#{i+1}</strong>"
            f"</div>"
            f"<div class='color-info'>"
            f"<div>{hex_color.upper()}</div>"
            f"<div>{int(percentage):.1f}%</div>"
            f"</div>"
            f"</div>"
        )

        
        
    
    html_content += "</div>"
    return html_content

def create_palette_image(color_data):
    """Buat gambar palet warna untuk diunduh"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 3))
    
    colors = [color[0]/255.0 for color in color_data]  # Normalisasi ke 0-1
    percentages = [color[1] for color in color_data]
    
    # Buat bar chart horizontal
    y_pos = 0
    left = 0
    
    for i, (color, percentage) in enumerate(zip(colors, percentages)):
        width = percentage
        ax.barh(y_pos, width, left=left, color=color, height=0.8, 
                edgecolor='white', linewidth=2)
        
        # Tambahkan label
        hex_color = rgb_to_hex(np.array(color) * 255)
        text_color = 'white' if sum(color) < 1.5 else 'black'
        ax.text(left + width/2, y_pos, f'{hex_color}\n{percentage:.1f}%', 
                ha='center', va='center', fontweight='bold', 
                color=text_color, fontsize=10)
        
        left += width
    
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('Persentase Dominasi Warna (%)', fontsize=12, fontweight='bold')
    ax.set_title('Palet Warna Dominan', fontsize=16, fontweight='bold', pad=20)
    
    # Hilangkan sumbu Y
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Simpan ke buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buf.seek(0)
    plt.close()
    
    return buf

def main():
    

    # Header utama
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Color Palette Generator</h1>
        <p>Ekstrak 5 warna dominan dari gambar Anda dengan teknologi AI</p>
    </div>
    """, unsafe_allow_html=True)

    
    # Custom CSS untuk styling
    st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
        
        .main-header {
            text-align: center;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .color-box {
            display: inline-block;
            width: 120px;
            height: 120px;
            margin: 10px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border: 3px solid white;
            text-align: center;
            vertical-align: top;
        }
        
        .color-info {
            background: white;
            padding: 10px;
            border-radius: 0 0 12px 12px;
            font-weight: bold;
            font-size: 12px;
            color: #333;
        }
        
        .palette-container {
            background: rgba(255,255,255,0.95);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .metric-container {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Upload gambar
    uploaded_file = st.file_uploader(
        "Pilih gambar untuk dianalisis", 
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Format yang didukung: PNG, JPG, JPEG, BMP, TIFF"
    )
    
    if uploaded_file is not None:
        # Tampilkan gambar yang diupload
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📷 Gambar Asli")
            image = Image.open(uploaded_file)
            
            # Resize gambar jika terlalu besar
            if image.size[0] > 800 or image.size[1] > 800:
                image.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            st.image(image, use_container_width=True, caption="Gambar yang dianalisis")
            
            # Info gambar
            st.markdown(f"""
            <div class="metric-container">
                <strong>Informasi Gambar</strong><br>
                Ukuran: {image.size[0]} × {image.size[1]} px<br>
                Mode: {image.mode}<br>
                Format: {uploaded_file.type}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎯 Analisis Warna")
            
            # Konversi ke RGB jika perlu
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Ekstrak warna dominan
            status_text.text("🔍 Menganalisis gambar...")
            progress_bar.progress(25)
            
            color_data = extract_dominant_colors(image, num_colors=5)
            progress_bar.progress(75)
            
            status_text.text("🎨 Membuat palet warna...")
            progress_bar.progress(100)
            
            status_text.text("✅ Analisis selesai!")
            
            # Tampilkan palet warna
            st.markdown("### 🌈 Palet Warna Dominan")
            palette_html = display_color_palette(color_data)
            st.markdown(f'<div class="palette-container">{palette_html}</div>', 
                       unsafe_allow_html=True)
        
        # Tabel detail warna
        st.markdown("### 📊 Detail Warna")
        color_df = pd.DataFrame([
            {
                'Ranking': i + 1,
                'Warna': f'<div style="width:50px;height:30px;background-color:{rgb_to_hex(color)};border-radius:5px;display:inline-block;margin-right:10px;"></div>',
                'HEX': rgb_to_hex(color),
                'RGB': f"({int(color[0])}, {int(color[1])}, {int(color[2])})",
                'Dominasi (%)': f"{percentage:.1f}%"
            }
            for i, (color, percentage) in enumerate(color_data)
        ])
        
        st.markdown(color_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # Tombol download
        st.markdown("### 💾 Unduh Palet Warna")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            # Buat gambar palet untuk diunduh
            palette_buffer = create_palette_image(color_data)
            
            st.download_button(
                label="📥 Unduh Palet Warna (PNG)",
                data=palette_buffer.getvalue(),
                file_name="color_palette.png",
                mime="image/png",
                use_container_width=True
            )
            
            # Unduh data CSV
            csv_data = pd.DataFrame([
                {
                    'Ranking': i + 1,
                    'HEX': rgb_to_hex(color),
                    'RGB_R': int(color[0]),
                    'RGB_G': int(color[1]),
                    'RGB_B': int(color[2]),
                    'Dominasi_Persen': round(percentage, 1)
                }
                for i, (color, percentage) in enumerate(color_data)
            ])
            
            st.download_button(
                label="📋 Unduh Data (CSV)",
                data=csv_data.to_csv(index=False),
                file_name="color_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    else:
        # Tampilan awal ketika belum ada gambar
        st.markdown("""
        <div class="palette-container" style="text-align: center; padding: 3rem;">
            <h3>🖼️ Belum ada gambar yang dipilih</h3>
            <p>Silakan upload gambar di atas untuk memulai analisis warna dominan</p>
            <br>
            <p><strong>Tips untuk hasil terbaik:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Gunakan gambar dengan resolusi yang baik</li>
                <li>Pastikan gambar memiliki variasi warna yang jelas</li>
                <li>Format gambar yang didukung: PNG, JPG, JPEG, BMP, TIFF</li>
                <li>Ukuran file maksimal: 200MB</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎨 <strong>Color Palette Generator</strong> - Dibuat menggunakan Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()