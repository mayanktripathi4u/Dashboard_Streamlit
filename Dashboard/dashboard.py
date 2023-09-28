"""
Run

streamlit run Dashboard\dashboard.py 

streamlit run Dashboard\dashboard.py --server.port 8888
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import matplotlib
warnings.filterwarnings('ignore')

st.set_page_config(page_title = "Super Store", page_icon = ":bar_chart:", layout = "wide")
# for more emojis refer https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/


st.title(" :bar_chart: Sample Super Store EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html = True)

fl = st.file_uploader(" :file_folder: Upload a file", type=(["csv", "txt", "xlxs", "xls"]))

if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
    # df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir(r"C:\Mayank\GitHub_Repo\Dashboard_Streamlit\data")
    df = pd.read_csv("SuperStore.csv")
    st.write(df.head())
    # df = pd.read_csv("SuperStore.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df["Order Date"])

# Getting the min and max date.
startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))    

df = df[(df["Order Date"] >= date1 ) & (df["Order Date"] <= date2 )].copy() 


st.sidebar.header("Choose your filter : ")

# Filter for Region
region = st.sidebar.multiselect("Pick your Region", df['Region'].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Filter for State
state = st.sidebar.multiselect("Pick your State", df2['State'].unique())

if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Filter for City
city = st.sidebar.multiselect("Pick your City", df3['City'].unique())

# Filter based on Region / State / City
if not region and not state and not city:
    df_filtered = df
elif not state and not city:
    df_filtered = df[df["Region"].isin(region)]
elif not region and not city:
    df_filtered = df[df["State"].isin(state)]
elif state and city:
    df_filtered = df3[df3["State"].isin(state) & df3["City"].isin(city)] 
elif region and city:
    df_filtered = df3[df3["Region"].isin(region) & df3["City"].isin(city)] 
elif state and region:
    df_filtered = df3[df3["Region"].isin(region) & df3["State"].isin(state)]    
elif city:
    df_filtered = df3[df3["City"].isin(city)]
else:
    df_filtered = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]    

# Filter By Category
category_df = df_filtered.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]], template = "seaborn")
    st.plotly_chart(fig, use_container_width = True, height = 200)


with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(df_filtered, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = df_filtered["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width = True, height = 200)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category_Wise_Sales.csv", mime = "text/csv", help = "Click here to download the filtered data in csv format")

with cl2:
    with st.expander("Region_ViewData"):
        region = df_filtered.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region_Wise_Sales.csv", mime = "text/csv", help = "Click here to download the filtered data in csv format")

df_filtered["month_year"] = df_filtered["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(df_filtered.groupby(df_filtered["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()

fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales" : "Amount"}, height = 500, width = 1000, template = 'gridon')

st.plotly_chart(fig2, use_container_width = True, height = 200)

with st.expander("View Data of Time Series"):
    
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index = False).encode('utf-8')
    st.download_button("Download Data", data = csv, file_name = "TimeSeries_Sales.csv", mime = "text/csv", help = "Click here to download the filtered data in csv format")


# Tree Map based on Region / Category and Sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3  =px.treemap(df_filtered, path = ["Region", "Category", "Sub-Category"], values = "Sales", hover_data = ["Sales"], color ="Sub-Category")

fig3.update_layout(width = 800, height =650)
st.plotly_chart(fig3, use_container_width = True, height = 200)



chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment Wise Sales")
    fig = px.pie(df_filtered, values = "Sales", names = "Segment", template = 'plotly_dark')
    fig.update_traces(text = df_filtered["Segment"], textposition = "inside")
    st.plotly_chart(fig, use_container_width = True, height = 200)

with chart2:
    st.subheader("Category Wise Sales")
    fig = px.pie(df_filtered, values = "Sales", names = "Category", template = 'plotly_dark')
    fig.update_traces(text = df_filtered["Category"], textposition = "inside")
    st.plotly_chart(fig, use_container_width = True, height = 200)    

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")    
with st.expander("Summary"):
    df_sample= df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale = 'cividis')
    st.plotly_chart(fig, use_container_width = True)

    st.markdown("Month wise Sub-Category Table")
    df_filtered["month"] = df_filtered["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data = df_filtered, values = "Sales", index = ["Sub-Category"], columns = "month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))

# Create Scatter Plot
data1 = px.scatter(df_filtered, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(
    title = "Relationship between Sales and Proffit using Scatter Plot",
    titlefont = dict(size=20),
    xaxis = dict(title = "Sales", titlefont = dict(size = 19)),
    yaxis = dict(title = "Profit", titlefont = dict(size = 19)),
)

st.plotly_chart(data1, use_container_width = True)    


with st.expander("View Data"):
    st.write(df_filtered.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download Original Data
csv = df.to_csv(index = False).encode('utf-8')
st.download_button("Download Data", data = csv, file_name = "Original_Data.csv", mime = "text/csv", help = "Click here to download the filtered data in csv format")
