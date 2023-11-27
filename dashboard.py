import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk membaca data
def read_data():
    customers_df = pd.read_csv('customers_dataset.csv', delimiter=',')
    geolocation_df = pd.read_csv('geolocation_dataset.csv', delimiter=';')
    order_items_df = pd.read_csv('order_items_dataset.csv', delimiter=',')
    order_payments_df = pd.read_csv('order_payments_dataset.csv', delimiter=',')
    order_reviews_df = pd.read_csv('order_reviews_dataset.csv', delimiter=',')

    # Perubahan disini: Ubah format kolom tanggal
    orders_df = pd.read_csv('orders_dataset.csv', delimiter=',', 
                            parse_dates=['order_purchase_timestamp', 'order_approved_at', 
                                         'order_delivered_carrier_date', 'order_delivered_customer_date', 
                                         'order_estimated_delivery_date'])

    # Perubahan disini: Set kolom 'order_purchase_timestamp' sebagai indeks
    orders_df.set_index('order_purchase_timestamp', inplace=True)

    product_category_df = pd.read_csv('product_category_name_translation.csv', delimiter=',')
    products_df = pd.read_csv('products_dataset.csv', delimiter=',')
    sellers_df = pd.read_csv('sellers_dataset.csv', delimiter=',')

    return {
        'customers': customers_df,
        'geolocation': geolocation_df,
        'order_items': order_items_df,
        'order_payments': order_payments_df,
        'order_reviews': order_reviews_df,
        'orders': orders_df,
        'product_category': product_category_df,
        'products': products_df,
        'sellers': sellers_df
    }

def show_graph_by_month_and_year(orders_df, selected_month, selected_year):
    # Filter data berdasarkan rentang waktu yang lebih luas
    start_date = f"{selected_year}-{selected_month:02d}-01"
    end_date = f"{selected_year}-{selected_month + 1:02d}-01" if selected_month < 12 else f"{selected_year + 1}-01-01"
    
    filtered_data = orders_df[(orders_df.index >= start_date) & (orders_df.index < end_date)]

    # Sort filtered data berdasarkan tanggal
    filtered_data = filtered_data.sort_index()

    # Check if the filtered data is not empty
    if not filtered_data.empty:
        # Buat plot/grafik (contoh: jumlah pesanan per hari)
        fig, ax = plt.subplots(figsize=(15, 8))
        sns.countplot(x=filtered_data.index.day, palette='viridis', ax=ax, label='Order Purchase')

        ax.set_title(f'Orders Timeline in {selected_month}/{selected_year}')
        ax.set_xlabel('Day of Month')
        ax.set_ylabel('Number of Orders')
        ax.legend()
        st.pyplot(fig)

        # Tampilkan informasi tambahan
        st.write("Selected Month:", selected_month)
        st.write("Selected Year:", selected_year)
        st.write(f"Total Orders: {filtered_data['order_id'].nunique()}")
        st.write(f"Orders Delivered: {filtered_data['order_delivered_carrier_date'].count()}")
        st.write(f"Delivered to Customer: {filtered_data['order_delivered_customer_date'].count()}")
        st.write("Filtered Data (Sorted by Date):")
        st.write(filtered_data[['order_id', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'customer_id']])
    else:
        st.warning(f"No orders found for {selected_month}/{selected_year}")


# Fungsi untuk menampilkan jumlah score per kategori
def show_review_score_by_category(order_reviews_df, order_items_df, products_df, product_category_df, selected_category):
    # Gabungkan order_reviews_df dengan order_items_df berdasarkan order_id
    merged_reviews_items = pd.merge(order_reviews_df, order_items_df, on='order_id', how='left')

    # Gabungkan merged_reviews_items dengan products_df berdasarkan product_id
    merged_reviews_products = pd.merge(merged_reviews_items, products_df, on='product_id', how='left')

    # Gabungkan merged_reviews_products dengan product_category_df berdasarkan product_category_name
    merged_reviews_category = pd.merge(merged_reviews_products, product_category_df, on='product_category_name', how='left')

    # Filter data berdasarkan kategori yang dipilih
    filtered_data = merged_reviews_category[merged_reviews_category['product_category_name_english'] == selected_category]

    # Hitung jumlah review untuk setiap skor
    score_counts = filtered_data['review_score'].value_counts().sort_index()

    # Buat plot/grafik (contoh: diagram pie)
    fig, ax = plt.subplots()
    ax.pie(score_counts, labels=score_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('viridis'))
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    ax.set_title(f'Review Scores for {selected_category}')

    st.pyplot(fig)

    # Menampilkan tabel jumlah review_score per kategori
    st.write("Review Scores per Category:")
    st.write(pd.DataFrame({'Review Score': score_counts.index, 'Count': score_counts}))

# Fungsi untuk menampilkan jumlah pengguna aktif berdasarkan state
def show_active_users_by_state(customers_df, orders_df, geolocation_df, selected_state):
    # Gabungkan customers_df dan geolocation_df berdasarkan customer_zip_code_prefix dan geolocation_zip_code_prefix
    merged_customers_geolocation = pd.merge(customers_df, geolocation_df,
                                            left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')
    
    # Gabungkan merged_customers_geolocation dengan orders_df berdasarkan customer_id
    merged_customers_orders = pd.merge(merged_customers_geolocation, orders_df, on='customer_id', how='inner')

    # Filter data berdasarkan state yang dipilih
    filtered_data = merged_customers_orders[merged_customers_orders['geolocation_state'] == selected_state]

    # Hitung jumlah pengguna aktif
    active_users_count = len(filtered_data['customer_id'].unique())

    # Menampilkan jumlah pengguna aktif dalam sebuah kotak
    st.info(f"**Active Users in {selected_state}:** {active_users_count} 👥")

# Fungsi untuk menampilkan jumlah penjual per state
def show_sellers_per_state(sellers_df, geolocation_df, selected_state):
    # Gabungkan sellers_df dan geolocation_df berdasarkan seller_zip_code_prefix dan geolocation_zip_code_prefix
    merged_sellers_geolocation = pd.merge(sellers_df, geolocation_df,
                                           left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix')

    # Filter data penjual berdasarkan state yang dipilih
    filtered_data = merged_sellers_geolocation[merged_sellers_geolocation['geolocation_state'] == selected_state]

    # Hitung jumlah penjual (seller_id unik) per state
    unique_sellers_count = filtered_data['seller_id'].nunique()

    # Menampilkan jumlah penjual per state dalam sebuah kotak
    st.info(f"**Number of Sellers in {selected_state}:** {unique_sellers_count} 👥")

# Fungsi utama
def run():
    st.set_page_config(
        page_title="E-commerce Dashboard",
        page_icon="🛍️",
    )

    st.write("# Welcome to E-commerce Dashboard! 🛍️")

    # Membaca semua file CSV
    data = read_data()

    # Sidebar untuk pemilihan bulan dan tahun
    st.sidebar.header("Filter by Month and Year")
    selected_month = st.sidebar.slider("Select Month", 1, 12, 1)
    selected_year = st.sidebar.slider("Select Year", int(data['orders'].index.year.min()),
                                    int(data['orders'].index.year.max()), 2018)

    # Sidebar untuk pemilihan kategori produk
    st.sidebar.header("Filter by Product Category")
    selected_product_category = st.sidebar.selectbox("Select Product Category", data['product_category']['product_category_name_english'])

    # Sidebar untuk pemilihan state pelanggan
    st.sidebar.header("Filter by Customer State")
    
    # Ambil data unik geolocation_state untuk dropdown
    unique_customer_states = data['geolocation']['geolocation_state'].unique()
    
    # Dropdown untuk memilih geolocation_state pelanggan
    selected_customer_state = st.sidebar.selectbox("Select Customer State", unique_customer_states)

    # Sidebar untuk pemilihan state penjual
    st.sidebar.header("Filter by Seller State")
    
    # Ambil data unik geolocation_state untuk dropdown penjual
    unique_seller_states = data['geolocation']['geolocation_state'].unique()
    
    # Dropdown untuk memilih geolocation_state penjual
    selected_seller_state = st.sidebar.selectbox("Select Seller State", unique_seller_states)

    # Membuat dua kolom di halaman utama dengan lebar yang berbeda
    container = st.container()
    col1, col2 = st.columns([15, 10])

    # Menampilkan grafik sesuai dengan bulan dan tahun yang dipilih di kolom pertama
    with col1:
        st.write("## Orders Timeline")
        show_graph_by_month_and_year(data['orders'], selected_month, selected_year)

    # Menampilkan review_score untuk setiap kategori produk dalam bentuk diagram pie dan tabel di kolom kedua
    with col2:
        st.write("## Review Scores by Category")
        show_review_score_by_category(data['order_reviews'], data['order_items'], data['products'], data['product_category'], selected_product_category)

    # Menampilkan jumlah pengguna aktif berdasarkan state yang dipilih
    show_active_users_by_state(data['customers'], data['orders'], data['geolocation'], selected_customer_state)

    # Menampilkan jumlah penjual per state
    show_sellers_per_state(data['sellers'], data['geolocation'], selected_seller_state)

if __name__ == "__main__":
    run()

