import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Ecommerce Toys Dashboard",
    page_icon="🧸",
    layout="wide"
)

# ---------------------------------------------------------
# Color Theme & Background
# ---------------------------------------------------------
def add_custom_css():
    css = """
    <style>
    .stApp {
        background-color: #D8BFD8 !important;
        color: #333333 !important;
    }
    .css-1d391kg, .css-1v3fvcr {
        background-color: #A3C4F3 !important;
        color: #000000 !important;
    }
    .css-1v3fvcr * {
        color: #000000 !important;
    }
    .stSidebar div[data-baseweb="select"] > div {
        background-color: #C6D8F9 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

add_custom_css()

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_data():

    # Small CSVs stored in GitHub
    orders = pd.read_csv("data/orders.csv")
    order_items = pd.read_csv("data/order_items.csv")
    products = pd.read_csv("data/products.csv")
    refunds = pd.read_csv("data/order_item_refunds.csv")

    # Large CSVs from Hugging Face (direct download)
    sessions_url = "https://huggingface.co/datasets/Snap-mango01/toy-ecommerce-data/resolve/main/website_sessions_clean.csv?download=1"
    pageviews_url = "https://huggingface.co/datasets/Snap-mango01/toy-ecommerce-data/resolve/main/website_pageviews.csv?download=1"

    website_sessions = pd.read_csv(sessions_url)
    pageviews = pd.read_csv(pageviews_url)

    return orders, order_items, products, refunds, website_sessions, pageviews


# Load all data
orders, order_items, products, refunds, website_sessions, pageviews = load_data()

# ---------------------------------------------------------
# Date Columns Prep
# ---------------------------------------------------------
orders["created_at"] = pd.to_datetime(orders["created_at"])
orders["year"] = orders["created_at"].dt.year
orders["month"] = orders["created_at"].dt.month

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("Filters")

years = ["All"] + sorted(orders["year"].unique().tolist())
months = ["All"] + sorted(orders["month"].unique().tolist())

selected_year = st.sidebar.selectbox("Select Year", years)
selected_month = st.sidebar.selectbox("Select Month", months)

utm_campaigns = ["All"] + sorted(website_sessions["utm_campaign"].dropna().unique().tolist())
utm_sources = ["All"] + sorted(website_sessions["utm_source"].dropna().unique().tolist())
device_types = ["All"] + sorted(website_sessions["device_type"].dropna().unique().tolist())

selected_campaign = st.sidebar.selectbox("Select UTM Campaign", utm_campaigns)
selected_source = st.sidebar.selectbox("Select UTM Source", utm_sources)
selected_device = st.sidebar.selectbox("Select Device Type", device_types)

# ---------------------------------------------------------
# Apply Filters
# ---------------------------------------------------------
filtered_orders = orders.copy()
filtered_sessions = website_sessions.copy()

if selected_year != "All":
    filtered_orders = filtered_orders[filtered_orders["year"] == selected_year]

if selected_month != "All":
    filtered_orders = filtered_orders[filtered_orders["month"] == selected_month]

if selected_campaign != "All":
    filtered_sessions = filtered_sessions[filtered_sessions["utm_campaign"] == selected_campaign]

if selected_source != "All":
    filtered_sessions = filtered_sessions[filtered_sessions["utm_source"] == selected_source]

if selected_device != "All":
    filtered_sessions = filtered_sessions[filtered_sessions["device_type"] == selected_device]

# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------
tab = st.radio(
    "Navigation",
    ["🏠 Home","📊 Sales Dashboard", "🧸 Product Performance", "📣 Marketing Insights", "💻 Website Analytics"],
    horizontal=True
)

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if tab == "🏠 Home":
    st.title("🧸 Ecommerce Toys Dashboard")
    st.subheader("Welcome to the Ecommerce Toys Dashboard! :)")

    st.write("""
    Explore sales trends, product performance, marketing insights,
    and website analytics using the navigation tabs above.
    """)

    try:
        st.image("data/Onlypic.png", use_container_width=True)
    except:
        st.warning("Image file 'Onlypic.png' not found.")

    st.markdown("---")
    st.write("### 👈 Use the sidebar filters to explore the data.")

# ---------------------------------------------------------
# SALES DASHBOARD
# ---------------------------------------------------------
elif tab == "📊 Sales Dashboard":

    st.title("📊 Sales Overview")

    order_data = order_items.merge(
        filtered_orders[["order_id", "created_at", "year", "month"]],
        on="order_id",
        how="inner"
    )

    order_data = order_data.merge(
        products[["product_id", "product_name"]],
        on="product_id",
        how="left"
    )

    total_revenue = order_data["price_usd"].sum()
    total_orders = filtered_orders["order_id"].nunique()
    aov = total_revenue / total_orders if total_orders > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", total_orders)
    col3.metric("Average Order Value", f"${aov:,.2f}")

    # Revenue by Year
    yearly_rev = order_data.groupby("year")["price_usd"].sum().reset_index()

    fig_year = px.line(
        yearly_rev, x="year", y="price_usd",
        markers=True, title="Revenue by Year"
    )
    st.plotly_chart(fig_year, use_container_width=True)

# ---------------------------------------------------------
# PRODUCT PERFORMANCE
# ---------------------------------------------------------
elif tab == "🧸 Product Performance":

    st.title("🧸 Product Performance Dashboard")

    prod_data = order_items.merge(
        filtered_orders[["order_id", "created_at", "year", "month", "website_session_id"]],
        on="order_id",
        how="inner"
    )
    prod_data = prod_data.merge(products, on="product_id", how="left")

    # FIX: Prevent MergeError by renaming refund created_at
    refunds = refunds.rename(columns={"created_at": "refund_created_at"})

    refunds_merged = prod_data.merge(refunds, on="order_item_id", how="left")
    refunds_merged["refund_amount_usd"] = refunds_merged["refund_amount_usd"].fillna(0)

    total_units = prod_data.shape[0]
    refunded_units = refunds_merged[refunds_merged["refund_amount_usd"] > 0].shape[0]
    refund_rate = refunded_units / total_units if total_units else 0

    col1, col2 = st.columns(2)
    col1.metric("Total Units Sold", f"{total_units:,}")
    col2.metric("Refund Rate", f"{refund_rate*100:.2f}%")

# ---------------------------------------------------------
# MARKETING INSIGHTS
# ---------------------------------------------------------
elif tab == "📣 Marketing Insights":

    st.title("📣 Marketing Insights Dashboard")

    # FIX: user_id does NOT exist in your database → removed
    total_sessions = website_sessions["website_session_id"].nunique()

    col1, col2 = st.columns(2)
    col1.metric("Total Sessions", total_sessions)
    col2.metric("Conversion Placeholder", "N/A")

    st.info("Note: No user_id column exists, so conversion rate cannot be calculated.")

# ---------------------------------------------------------
# WEBSITE ANALYTICS
# ---------------------------------------------------------
elif tab == "💻 Website Analytics":

    st.title("💻 Website Analytics Dashboard")

    website_sessions["created_at"] = pd.to_datetime(website_sessions["created_at"])
    pageviews["created_at"] = pd.to_datetime(pageviews["created_at"])

    total_sessions = website_sessions["website_session_id"].nunique()
    total_pageviews = pageviews.shape[0]

    col1, col2 = st.columns(2)
    col1.metric("Total Sessions", total_sessions)
    col2.metric("Total Pageviews", total_pageviews)
