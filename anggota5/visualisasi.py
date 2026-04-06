# visualisasi.py

import matplotlib.pyplot as plt
import numpy as np

def buat_grafik_perbandingan(data_obat, output_filename='grafik_obat_temp.png'):
    """
    Menerima data dictionary obat dan menyimpannya menjadi file gambar grafik.
    Mengembalikan path file gambar tersebut.
    """
    obat_labels = data_obat["obat"]
    x = np.arange(len(obat_labels))
    width = 0.25 
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    rects1 = ax.bar(x - width, data_obat["efek_samping_ringan"], width, label='Ringan', color='#D8BFD8')
    rects2 = ax.bar(x, data_obat["efek_samping_sedang"], width, label='Sedang', color='#800080')
    rects3 = ax.bar(x + width, data_obat["efek_samping_berat"], width, label='Berat', color='#1A1A1A')

    ax.set_ylabel('Jumlah Kasus Dilaporkan')
    ax.set_title('Perbandingan Profil Efek Samping Obat')
    ax.set_xticks(x)
    ax.set_xticklabels(obat_labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)

    fig.tight_layout()
    
    # Simpan grafik
    plt.savefig(output_filename)
    plt.close(fig) # Tutup figure agar tidak memakan memori
    
    return output_filename