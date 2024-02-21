import streamlit as st
import pandas as pd
import numpy as np
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory

# Fungsi optimasi dari potongan kode sebelumnya
def optimize_bio_energy(upload_file):
    # Load Data
    df = pd.read_excel(upload_file)
    supply = pd.read_excel(upload_file, sheet_name='bio')
    req_bio = pd.read_excel(upload_file, sheet_name='pltu')

    # Fungsi optimization
    # Membuat modelnya
    model = pyo.ConcreteModel()

    # Mendifinisikan variabel
    model.Kb = pyo.Var(supply.index, bounds=(0, None))  # Menggunakan indeks langsung dari supply
    kb = model.Kb

    # Fungsi Pembatas
    # Fungsi Pembatas Pertama
    # Membuat fungsi pembatas sebelah kiri
    kb_sum = sum(kb[i] for i in supply.index)
    # Penulisan fungsi pembatas sebelah kanan
    sum(req_bio.demand)
    # Mendefinisikan fungsi pembatas dengan nama 'balance'
    model.balance = pyo.Constraint(expr=kb_sum == sum(req_bio.demand))

    # Fungsi Pembatas Kedua
    # Mendefinisikan fungsi pembatas kedua dengan nama 'cond'
    for i in range(len(req_bio)):
        model.add_component("cond_"+str(i), pyo.Constraint(expr=req_bio.demand[i] <= sum(kb[i] for i in supply.index)))

    # Fungsi Pembatas Ketiga
    # Mendefinisikan fungsi pembatas keempat dengan nama limits
    model.limits = pyo.ConstraintList()
    # Mengisikan isi persamaan dari 'model.limits'
    for indeks in supply.index:
        model.limits.add(expr=kb[indeks] <= supply.kapasitas[indeks])

    # Mendefinisikan Fungsi Tujuan
    # Mendefinisikan summation untuk Kb di fungsi tujuan
    kb_sum_obj = sum(kb[indeks] * supply.harga[indeks] for indeks in supply.index)
    # Mendefinisikan fungsi tujuan
    model.obj = pyo.Objective(expr=kb_sum_obj, sense=minimize)

    # Menjalankan Model
    # Mendefinisikan solvernya
    opt = SolverFactory('glpk')
    # Menjalankan optimasinya
    results = opt.solve(model, tee=True)
    # Kita simpan hasilnya dan masukkan ke dalam tabel 'supply' sebagai kolom baru 'Kb'
    supply['Kb'] = [pyo.value(kb[indeks]) for indeks in supply.index]  # Mengakses nilai variabel
    # Menambah kolom baru 'total' untuk melihat hasil perkalian antara kolom 'harga' dengan 'Kb'
    supply['total'] = supply.harga * supply.Kb
    # Menghitung jumlah total biaya
    total_cost = sum(supply.total)
    # Melihat nilai fungsi tujuan
    obj_value = pyo.value(model.obj)

    return supply, total_cost, obj_value

# Streamlit App
# Menulis judul
st.markdown("<h1 style='text-align: center; '> Selection Capacity of Biomass Supplier </h1>", unsafe_allow_html=True)
st.markdown('---'*10)

# Use st.image with a relative path
background_image = "background.jpeg"
st.image(background_image)

# Setting ukuran font judul deskripsi
font_size = "25px"

# Use HTML to set the font size
st.markdown(
    f"""
    <p style="font-size:{font_size};line-height: 1.2;">
        Web App for Selection of Biomass Supplier for Cofiring Program at Coal Fired Power Plant (PLTU) <br>
        <span style="font-size:13px;">Created by  : Yoni Mahagun MT.</span><br>
        <span style="font-size:13px;">Mentor      : Mega Bagus Herlambang PhD.</span><br>
        <br>
    </p>
    """,
    unsafe_allow_html=True,
)

# Upload File Excel
upload_file = st.file_uploader("Please Upload Excel File", type=["xlsx"])

# Jika file sudah diupload
if upload_file is not None:
    # Menampilkan preview data
    df = pd.read_excel(upload_file)
    pilih = st.selectbox('Show the preview table', ('biomass supply', 'required biomass')) 
    if pilih == 'biomass supply':
        st.write('Table : ', pilih) 
        supply = pd.read_excel(upload_file, sheet_name='bio')
        st.table(supply)
    else :
        st.write('Table : ', pilih) 
        req_bio = pd.read_excel(upload_file, sheet_name='pltu')
        st.table(req_bio)    
    st.success('File successfully uploaded')
    
    st.markdown(
    """**Note :**  

    `id`        : Supplier biomass id or PLTU id number (table biomass supply 
                  & table required biomass)   
    `kapasitas` : Biomass supply capacity in ton/day (table biomass supply)
    `harga`     : Buying price of biomass per ton in Rp (table biomass supply)
    `demand`    : Minimum required biomass of PLTU in ton/day (table required biomass)
    
    """
)
    
    
    #st.write(df)

    # Mengeksekusi optimisasi jika tombol di klik
    if st.button('Optimize Biomass Supply'):
        supply, total_cost, obj_value = optimize_bio_energy(upload_file)
        # Menampilkan hasil optimisasi
        st.write("Optimization Results:")
        st.success("Optimization Found for Biomass Supply:")
        st.table(supply)
        
        total_cost_formatted = "{:,.2f}".format(total_cost)  # Menggunakan string formatting untuk mengatur format angka
        total_cost_display = "Rp {:}".format(total_cost_formatted)  # Menambahkan penanda mata uang 'Rp' di depannya
        #st.write("Total Cost:", total_cost_display)
        st.write("<div align='center'><b>Total Cost:</b> {}</div>".format(total_cost_display), unsafe_allow_html=True)
             
        #Show_Note = st.markdown("Show Note")
       
        st.markdown(
    """**Note :**  

    `id`        : Supplier biomass id   
    `kapasitas` : Biomass supply capacity in ton/day  
    `harga`     : Buying price of biomass per ton in Rp  
    `Kb`        : Amount of the optimized biomass capacity that according to demand 
                  of PLTU and constraints of the model in ton/day  
    `Total`     : Total buying price of biomass after optimized with the model in Rp
    """
)
