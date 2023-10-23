
import matplotlib.ticker as ScalarFormatter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from matplotlib.ticker import ScalarFormatter

sns.set(style='dark')

#create_monthly_orders_df
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_date').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return monthly_orders_df

#create_city_order_revenue_df
def create_city_order_revenue_df(df):
    city_order_revenue_df = df.groupby(by='customer_state').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).sort_values(by="payment_value", ascending=False)

    city_order_revenue_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
        
    return city_order_revenue_df

#create_total_orders_product_df
def create_total_orders_product_df(df):
    total_orders_product_df = df.groupby(by='product_category_name').agg({
        "product_id": "nunique"
    }).sort_values(by="product_id", ascending=False)

    total_orders_product_df.rename(columns={
        "product_id": "order_product_count"
    }, inplace=True)
        
    return total_orders_product_df


#create_rfm_df
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_code", as_index=False).agg({
        "order_date": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_code", "max_order_timestamp", "frequency", "monetary"]
    
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = all_df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
        
    return rfm_df 
 

# Load cleaned data
all_df = pd.read_csv("orders_payments_customers.csv")
orders_product_df = pd.read_csv("orders_product.csv")

#conver to dateTime
datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
 
for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

 
datetime_columns = ["order_purchase_timestamp", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "shipping_limit_date"]
 
for column in datetime_columns:
  orders_product_df[column] = pd.to_datetime(orders_product_df[column]) 
 

#rename order_purchase_timestamp to order_date
all_df.rename(columns={
    "order_purchase_timestamp": "order_date"
}, inplace=True)
  
orders_product_df.rename(columns={
    "order_purchase_timestamp": "order_date"
}, inplace=True)

# Filter data
min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()  

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("ecommerce-logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    ) 

main_df = all_df[(all_df["order_date"] >= str(start_date)) & 
                (all_df["order_date"] <= str(end_date))]


main_orders_product_df = orders_product_df[(orders_product_df["order_date"] >= str(start_date)) & 
                (orders_product_df["order_date"] <= str(end_date))]

# st.dataframe(main_df)

# # Menyiapkan berbagai dataframe
monthly_orders_df = create_monthly_orders_df(main_df)
city_order_revenue_df = create_city_order_revenue_df(main_df)
total_orders_product_df = create_total_orders_product_df(main_orders_product_df)
rfm_df = create_rfm_df(main_df) 

# format_func
def format_func(value, tick_number):
    formatted_value = "{:,.0f}".format(value)
    return formatted_value

# plot number of Monthly orders
st.header('EgsuDotNet Collection Dashboard :sparkles:')
st.subheader('Monthly Orders') 

plt.figure(figsize=(10, 5)) 
plt.plot(monthly_orders_df["order_date"], monthly_orders_df["order_count"], marker='o', linewidth=1, color="#72BCD4") 
plt.title("Number of Orders per Month", loc="center", fontsize=20) 
plt.xticks(fontsize=8, rotation=75) 
plt.yticks(fontsize=8)

# Use ScalarFormatter to format y-axis labels as regular decimal numbers
plt.gca().get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_func))

plt.show()

st.pyplot(plt)


# plot number of Monthly Revenue 
st.subheader('Monthly Revenue') 

plt.figure(figsize=(10, 5)) 
plt.plot(monthly_orders_df["order_date"], monthly_orders_df["revenue"], marker='o', linewidth=1, color="#72BCD4") 
plt.title("Number of Revenue per Month", loc="center", fontsize=20) 
plt.xticks(fontsize=8, rotation=75) 
plt.yticks(fontsize=8)

# Use ScalarFormatter to format y-axis labels as regular decimal numbers
plt.gca().get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_func))

plt.show()

st.pyplot(plt)

# Product performance in each state
st.subheader("The highest number of orders and revenue in each state")

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"] 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

sns.barplot(x="customer_state", y="order_count", data=city_order_revenue_df.head(5),palette=colors,hue="customer_state", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Order", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)
 
# Apply the custom formatting function to the y-axis of the first subplot
ax[0].get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
ax[0].yaxis.set_major_formatter(plt.FuncFormatter(format_func))

sns.barplot(x="customer_state", y="revenue", data=city_order_revenue_df.head(5), palette=colors,hue="customer_state", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
# ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Revenue", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

# Apply the custom formatting function to the y-axis of the second subplot
ax[1].get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
ax[1].yaxis.set_major_formatter(plt.FuncFormatter(format_func))
 
plt.suptitle("Number of Order and Revenue", fontsize=20) 
st.pyplot(plt)

# Product performance
st.subheader("Best & Worst Performing Product Category") 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
 
sns.barplot(x="order_product_count", y="product_category_name", data=total_orders_product_df.head(5), palette=colors,hue="product_category_name", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)
 
sns.barplot(x="order_product_count", y="product_category_name", data=total_orders_product_df.sort_values(by="order_product_count", ascending=True).head(5), palette=colors,hue="product_category_name", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)
 
plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=20)
st.pyplot(plt) 

# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_code", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_code", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30, rotation=90)
ax[0].tick_params(axis='x', labelsize=35, rotation=90)

# Apply the custom formatting function to the y-axis of the first subplot
ax[0].get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
ax[0].yaxis.set_major_formatter(plt.FuncFormatter(format_func))

sns.barplot(y="frequency", x="customer_code", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_code", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30, rotation=90)
ax[1].tick_params(axis='x', labelsize=35, rotation=90)

# Apply the custom formatting function to the y-axis of the first subplot
ax[1].get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
ax[1].yaxis.set_major_formatter(plt.FuncFormatter(format_func))

sns.barplot(y="monetary", x="customer_code", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_code", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30, rotation=90)
ax[2].tick_params(axis='x', labelsize=35, rotation=90)

# Apply the custom formatting function to the y-axis of the first subplot
ax[2].get_yaxis().set_major_formatter(ScalarFormatter(useMathText=False))
ax[2].yaxis.set_major_formatter(plt.FuncFormatter(format_func))

st.pyplot(fig)

st.caption('Copyright © EgsuDotNet 2023')