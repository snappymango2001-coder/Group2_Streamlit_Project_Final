import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
import streamlit_authenticator as stauth

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

passwords = ["TomPass123", "MorganPass123", "CindyPass123"]
hashed_passwords = stauth.Hasher(passwords).generate()

config = {
    "credentials": {
        "usernames": {
            "tom": {
                "name": "Tom Parmesan",
                "password": hashed_passwords[0]
            },
            "morgan": {
                "name": "Morgan Rockwell",
                "password": hashed_passwords[1]
            },
            "cindy": {
                "name": "Cindy Sharp",
                "password": hashed_passwords[2]
            },
        }
    },
    "cookie": {
        "name": "toyapp_cookie",
        "key": "toyapp_signature_key",
        "expiry_days": 7
    },
    "preauthorized": {
        "emails": []
    }
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# ---------------------------------------------------------
# 🔵 INSERT LOGIN PAGE UI **RIGHT HERE**
# ---------------------------------------------------------

st.markdown("""
<h2 style='text-align:center; color:#333;'>Welcome Back 👋</h2>

<p style='text-align:center; color:#555; font-size:16px;'>
    Use your company credentials to sign in  
    and unlock your personalized analytics experience.
</p>
""", unsafe_allow_html=True)

st.success("👋 Hi there! So good to see you again!")

# ---------------------------------------------------------
# LOGIN FORM
# ---------------------------------------------------------

name, auth_status, username = authenticator.login("Login", "main")

# ---------------------------------------------------------
# LOGIN RESPONSES
# ---------------------------------------------------------

if auth_status is False:
    st.error("❌ Incorrect username or password")

elif auth_status is None:
    st.warning("Please enter your username and password")

elif auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as {name}")

    # 🎉 Balloons after successful login
    st.balloons()

    # -----------------------------------------
    # EVERYTHING BELOW THIS POINT IS THE APP
    # -----------------------------------------


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
    # RADIO BUTTONS FOR NAVIGATION
    # ---------------------------------------------------------
    tab = st.radio(
        "Navigation",
        ["🏠 Home","📊 Sales Dashboard", "🧸 Product Performance", "📣 Marketing Insights", "💻 Website Analytics"],
        horizontal=True
    )
    
    # ---------------------------------------------------------
    # HOME PAGE (Introduction)
    # ---------------------------------------------------------
    if tab == "🏠 Home":
        st.title("🧸 Ecommerce Toys Dashboard")
    
        st.subheader("Welcome to the Ecommerce Toys Dashboard! :)")
        
        st.write("""
        This dashboard provides an analytical overview of the Ecommerce Toys Company - toyswithus.co. 
        
        Explore sales trends, product performance, marketing insights, and website analytics using the navigation above |^|
    
        Use the filters on the <- left to slice the data by year, month, campaign, traffic source, and device type.
                 
        Below is a glimpse of our product catalogue :)
        """)
    
        
    
        # Display an image (local file)
        st.image("data/Onlypic.png", use_container_width=True)
    
        st.markdown("---")
        st.write("### 👈 Use the sidebar filters and top menu to start exploring the data :) ")
    
    # ---------------------------------------------------------
    # SALES DASHBOARD
    # ---------------------------------------------------------
    if tab == "📊 Sales Dashboard":
    
        st.title("📊 Sales Overview")
    
        st.subheader("🔑Key Revenue Metrics")
    
        #  Orders + Order Items
        order_data = order_items.merge(
            filtered_orders[["order_id", "created_at", "year", "month"]],
            on="order_id",
            how="inner"
        )
    
        order_data = order_data.merge(products[["product_id", "product_name"]], 
                                      on="product_id", how="left")
    
        # ---------------------------------------------------------
        # Metrics
        # ---------------------------------------------------------
        total_revenue = order_data["price_usd"].sum()
        total_orders = filtered_orders["order_id"].nunique()
        aov = total_revenue / total_orders if total_orders > 0 else 0
    
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"${total_revenue:,.2f}")
        col2.metric("Total Orders", total_orders)
        col3.metric("Avg Order Value", f"${aov:,.2f}")
    
        # ---------------------------------------------------------
        # Revenue by Year 
        # ---------------------------------------------------------
        st.subheader("Revenue by Year")
    
        yearly_rev = (
            order_data.groupby("year")["price_usd"]
            .sum()
            .reset_index()
        )
    
        # Make sure the year is an integer
        yearly_rev["year"] = yearly_rev["year"].astype(int)
    
        # Visual
        fig_year = px.line(
            yearly_rev,
            x="year",
            y="price_usd",
            markers=True,
            title="Revenue by Year",
        )
    
        # Update the layout and x-axis formatting
        fig_year.update_layout(
            xaxis=dict(
                tickmode="linear",  
                tickformat="%Y"     
            ),
            height=350
        )
    
        
        st.plotly_chart(fig_year, use_container_width=True)
    
    
        # ---------------------------------------------------------
        # Revenue by Product
        # ---------------------------------------------------------
        st.subheader("🧸Revenue by Product")
    
        product_rev = (
            order_data.groupby("product_name")["price_usd"]
            .sum()
            .reset_index()
            .sort_values("price_usd", ascending=False)
        )
    
        fig_pie = px.pie(
            product_rev,
            names="product_name",
            values="price_usd",
            title="Revenue Share by Product",
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=400)
    
        st.plotly_chart(fig_pie, use_container_width=True)
    
        # ---------------------------------------------------------
        # Revenue by Campaign 
        # ---------------------------------------------------------
        st.subheader("Revenue by Campaign")
    
        order_data2 = order_items.merge(
            filtered_orders[
                ["order_id", "created_at", "year", "month", "website_session_id"]
            ],
            on="order_id",
            how="inner"
        )
    
        rev_with_sessions = order_data2.merge(
            website_sessions[["website_session_id", "utm_campaign", "utm_source"]],
            on="website_session_id",
            how="left"
        )
    
        campaign_rev = (
            rev_with_sessions.groupby("utm_campaign")["price_usd"]
            .sum()
            .reset_index()
            .sort_values("price_usd", ascending=False)
        )
    
        fig_campaign = px.bar(
            campaign_rev,
            x="utm_campaign",
            y="price_usd",
            title="Revenue by Campaign",
            text_auto=True
        )
    
        fig_campaign.update_traces(texttemplate="%{y:.2s}", textposition="outside", cliponaxis=False)
    
        fig_campaign.update_layout(xaxis_tickangle=45, height=350, margin=dict(t=80))
    
        st.plotly_chart(fig_campaign, use_container_width=True)
    
        # ---------------------------------------------------------
        # Revenue by UTM Source
        # ---------------------------------------------------------
        st.subheader("Revenue by UTM Source")
    
        source_rev = (
            rev_with_sessions.groupby("utm_source")["price_usd"]
            .sum()
            .reset_index()
            .sort_values("price_usd", ascending=False)
        )
    
        fig_source = px.bar(
            source_rev,
            x="utm_source",
            y="price_usd",
            title="Revenue by Traffic Source",
            text_auto=True
        )
    
        fig_source.update_traces(texttemplate="%{y:.2s}", textposition="outside", cliponaxis=False)
    
        fig_source.update_layout(xaxis_tickangle=45, height=350, margin=dict(t=80))
    
        st.plotly_chart(fig_source, use_container_width=True)
    
    
    # --------------------------------------------------------- 
    # PRODUCT DASHBOARD
    # ---------------------------------------------------------
    elif tab == "🧸 Product Performance":
    
        st.title("🧸 Product Performance Dashboard")
    
        st.subheader("🔑Key Product Metrics")
    
        # orders + products
        prod_data = order_items.merge(
            filtered_orders[["order_id", "created_at", "year", "month", "website_session_id"]],
            on="order_id",
            how="inner"
        )
    
        prod_data = prod_data.merge(products[["product_id", "product_name"]], 
                                    on="product_id", how="left")
    
        # Refunds
        order_item_refunds = pd.read_csv("data/order_item_refunds.csv")
    
        refunds_merged = prod_data.merge(
            order_item_refunds,
            on="order_item_id",
            how="left"
        )
    
        # Use correct refund column
        refunds_merged["refund_amount_usd"] = refunds_merged["refund_amount_usd"].fillna(0)
    
        # KPIs
        total_products = products["product_id"].nunique()
        total_units_sold = prod_data.shape[0]
        refunded_units = refunds_merged[refunds_merged["refund_amount_usd"] > 0].shape[0]
        refund_rate = refunded_units / total_units_sold if total_units_sold > 0 else 0
    
        top_product = prod_data["product_name"].value_counts().idxmax()
        
        total_refund_amount = refunds_merged["refund_amount_usd"].sum()
        total_revenue_products = prod_data["price_usd"].sum()
        pct_revenue_lost = total_refund_amount / total_revenue_products if total_revenue_products > 0 else 0
    
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            st.markdown("**Most Bought Product**")
            st.markdown(
                f"""
                <div style="font-size: 24px; font-weight: 600; line-height: 1.1;">
                    {top_product}
                </div>
                """,
                unsafe_allow_html=True
            )
    
        with col2:
            st.metric("Total Products", total_products)
    
        with col3:
            st.metric("Total Units Sold", f"{total_units_sold:,}")
    
        with col4:
            st.metric("Refund Rate", f"{refund_rate*100:.2f}%")
    
        col5, col6 = st.columns(2)
    
        with col5:
            st.metric("Total Refund Amount", f"${total_refund_amount:,.2f}")
    
        with col6:
            st.metric("% Revenue Lost to Refunds", f"{pct_revenue_lost*100:.2f}%")
    
    
        # Revenue Over Time
        st.subheader("Revenue Over Time — by Product")
    
        revenue_over_time = (
            prod_data.groupby(["year", "month", "product_name"])["price_usd"]
            .sum()
            .reset_index()
        )
    
        revenue_over_time["date"] = pd.to_datetime(
            revenue_over_time["year"].astype(str) + "-" + 
            revenue_over_time["month"].astype(str) + "-01"
        )
    
        fig_rev_product = px.line(
            revenue_over_time,
            x="date",
            y="price_usd",
            color="product_name",
            markers=True,
            title="Revenue Over Time by Product"
        )
        fig_rev_product.update_layout(height=400)
    
        st.plotly_chart(fig_rev_product, use_container_width=True)
    
        # ------------------------------
        # Conversion Rate Calculation 
        # ------------------------------
    
        st.subheader("Conversion Rate by Product")
    
        # Total sessions (filtered by year/month if applied)
        total_sessions = website_sessions["website_session_id"].nunique()
    
        # Orders per product
        orders_per_product = (
            prod_data.groupby("product_name")["order_id"]
            .nunique()
            .reset_index()
            .rename(columns={"order_id": "orders"})
        )
    
        orders_per_product["sessions"] = total_sessions
        orders_per_product["conversion_rate"] = (
            orders_per_product["orders"] / total_sessions
        )
    
        fig_conv_product = px.bar(
            orders_per_product,
            x="product_name",
            y="conversion_rate",
            title="Conversion Rate by Product",
            text=orders_per_product["conversion_rate"].apply(lambda x: f"{x*100:.2f}%")
        )
    
        fig_conv_product.update_layout(
            xaxis_tickangle=45,
            height=400,
            yaxis_title="Conversion Rate"
        )
    
        st.plotly_chart(fig_conv_product, use_container_width=True)
    
    
    
    # --------------------------------------------------------- 
    # MARKETING DASHBOARD
    # ---------------------------------------------------------
    elif tab == "📣 Marketing Insights":
    
        st.title("📣 Marketing Insights Dashboard")
    
        # ------------------ KPI CARDS ------------------
        st.subheader("🔑Key Marketing Metrics")
    
        # Unique Users
        unique_users = website_sessions["user_id"].nunique()
    
        # Total Site Traffic (sessions)
        total_traffic = website_sessions["website_session_id"].nunique()
    
        #Customer Conversion rate (Customers who purchased/unique users)
        # Unique users who visited the site
        unique_users = website_sessions["user_id"].nunique()
    
        # Unique customers who purchased (from orders)
        unique_purchasers = filtered_orders["user_id"].nunique()
    
        # Customer Conversion Rate
        customer_conversion_rate = unique_purchasers / unique_users if unique_users > 0 else 0
    
            # Repeat User Rate
        user_order_counts = filtered_orders.groupby("user_id")["order_id"].nunique()
        repeat_user_rate = (user_order_counts > 1).mean()
    
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Unique Users", f"{unique_users:,}")
        col2.metric("Total Site Traffic", f"{total_traffic:,}")
        col3.metric("Customer Conversion Rate", f"{customer_conversion_rate*100:.2f}%")
        col4.metric("Repeat User Rate", f"{repeat_user_rate*100:.2f}%")
    
        # ------------------ Website Sessions by UTM Source ------------------
        st.subheader("Website Sessions by UTM Source")
    
        utm_source_counts = (
            website_sessions.groupby("utm_source")["website_session_id"]
            .nunique()
            .reset_index(name="sessions")
            .sort_values("sessions", ascending=False)
        )
    
        fig_utm_pie = px.pie(
            utm_source_counts,
            names="utm_source",
            values="sessions",
            title="Website Sessions by UTM Source"
        )
        fig_utm_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_utm_pie, use_container_width=True)
    
        # ------------------ Conversion Rate Over Time ------------------
        st.subheader("Monthly Conversion Rate Over Time")
    
    
        filtered_orders['created_at'] = pd.to_datetime(filtered_orders['created_at'])
    
        # Total sessions per month
        sessions_per_month = website_sessions.copy()
        
        sessions_per_month['month'] = pd.to_datetime(sessions_per_month['created_at']).dt.to_period('M').dt.to_timestamp()
        sessions_per_month = sessions_per_month.groupby('month')['website_session_id'].nunique().reset_index(name='sessions')
    
        # Total orders per month
        orders_per_month = filtered_orders.copy()
        orders_per_month['month'] = orders_per_month['created_at'].dt.to_period('M').dt.to_timestamp()
        orders_per_month = orders_per_month.groupby('month')['order_id'].nunique().reset_index(name='orders')
    
        # Merging sessions and orders
        conv_over_time = sessions_per_month.merge(orders_per_month, on='month', how='left')
        conv_over_time['orders'] = conv_over_time['orders'].fillna(0)
        conv_over_time['conversion_rate'] = conv_over_time['orders'] / conv_over_time['sessions']
    
        
        fig_conv_time = px.line(
            conv_over_time,
            x='month',
            y='conversion_rate',
            markers=True,
            title="Monthly Conversion Rate Over Time"
        )
        fig_conv_time.update_layout(yaxis_title="Conversion Rate", height=400)
        st.plotly_chart(fig_conv_time, use_container_width=True)
    
    elif tab == "💻 Website Analytics":
    
        st.title("💻 Website Analytics Dashboard")
    
        # ------------------ KPI CARDS ------------------
        st.subheader("🔑Key Website Metrics")
    
        # Ensuring datetime
        website_sessions['created_at'] = pd.to_datetime(website_sessions['created_at'])
        pageviews['created_at'] = pd.to_datetime(pageviews['created_at'])
    
        # Converted flag from filtered_orders
        converted_sessions_df = filtered_orders[['website_session_id']].drop_duplicates()
        converted_sessions_df['converted'] = 1
    
        website_sessions = website_sessions.merge(
            converted_sessions_df,
            on='website_session_id',
            how='left'
        )
        website_sessions['converted'] = website_sessions['converted'].fillna(0).astype(int)
    
        # ------------------ KPI Cards ------------------
        total_sessions = website_sessions['website_session_id'].nunique()
        total_pageviews = pageviews.shape[0]
    
        # Session conversion rate
        converted_sessions = website_sessions['converted'].sum()
        overall_conversion_rate = converted_sessions / total_sessions if total_sessions > 0 else 0
    
        # Bounce Rate
        pageviews_per_session = (
            pageviews.groupby('website_session_id')['pageview_url']
            .count()
            .reset_index(name='pageviews_count')
        )
    
        bounces = pageviews_per_session[pageviews_per_session['pageviews_count'] == 1].shape[0]
        overall_bounce_rate = bounces / total_sessions if total_sessions > 0 else 0
    
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sessions", f"{total_sessions:,}")
        col2.metric("Total Pageviews", f"{total_pageviews:,}")
        col3.metric("Overall Bounce Rate", f"{overall_bounce_rate*100:.2f}%")
        col4.metric("Session Conversion Rate", f"{overall_conversion_rate*100:.2f}%")
    
        # ------------------ Bounce Rate Over Time ------------------
        st.subheader("Bounce Rate Over Time")
    
        sessions_with_pages = website_sessions.merge(
            pageviews_per_session,
            on='website_session_id',
            how='left'
        )
    
        sessions_with_pages['pageviews_count'] = sessions_with_pages['pageviews_count'].fillna(0)
        sessions_with_pages['month'] = sessions_with_pages['created_at'].dt.to_period('M').dt.to_timestamp()
    
    
        monthly_bounce = (
            sessions_with_pages.groupby('month')
            .apply(lambda x: (x['pageviews_count'] == 1).mean())
            .reset_index(name='bounce_rate')
        )
    
        fig_bounce = px.line(
            monthly_bounce,
            x='month',
            y='bounce_rate',
            markers=True,
            title="Monthly Bounce Rate Over Time"
        )
    
        fig_bounce.update_layout(
            yaxis_title="Bounce Rate",
            height=400
        )
    
        st.plotly_chart(fig_bounce, use_container_width=True)
    
        # ---------------------------------------------------------
        # CONVERSION FUNNEL BY PAGE
        # ---------------------------------------------------------
        st.header("Conversion Funnel by Page Group")
    
        # Mapping function for funnel stages
        def map_page_to_stage(page_url):
            if page_url in ["/lander-1", "/lander-2", "/lander-3", "/lander-4", "/lander-5", "/home"]:
                return "Landing Page"
            elif page_url in [
                "/the-hudson-river-mini-bear",
                "/the-forever-love-bear",
                "/the-birthday-sugar-panda",
                "/the-original-mr-fuzzy",
                "/products"
            ]:
                return "Product Page"
            elif page_url == "/cart":
                return "Cart"
            elif page_url in ["/billing", "/shipping", "/billing-2"]:
                return "Checkout"
            elif page_url == "/thank-you-for-your-order":
                return "Thank You"
            else:
                return None   # This replaces "Other" completely
    
        # Tag pageviews with funnel stage
        pageviews["funnel_stage"] = pageviews["pageview_url"].apply(map_page_to_stage)
    
        # Remove rows that are not part of the funnel
        pageviews = pageviews[pageviews["funnel_stage"].notna()]
    
        # -------------------------------
        # COUNT UNIQUE SESSIONS PER STAGE
        # -------------------------------
        sessions_per_stage = (
            pageviews.groupby("funnel_stage")["website_session_id"]
            .nunique()
            .reset_index(name="sessions")
        )
    
        # -------------------------------
        # CONVERTED SESSIONS
        # -------------------------------
        session_conversions = (
            filtered_orders.groupby("website_session_id")["order_id"]
            .nunique()
            .reset_index()
        )
        session_conversions["converted"] = session_conversions["order_id"] > 0
        session_conversions = session_conversions[["website_session_id", "converted"]]
    
        # Attach conversion status to each pageview
        pv = pageviews.merge(session_conversions, on="website_session_id", how="left")
        pv["converted"] = pv["converted"].fillna(False)
    
        # Count unique converting sessions per stage
        conversions_per_stage = (
            pv[pv["converted"]]
            .groupby("funnel_stage")["website_session_id"]
            .nunique()
            .reset_index(name="conversions")
        )
    
        # Merge sessions + conversions
        funnel_data = sessions_per_stage.merge(conversions_per_stage, on="funnel_stage", how="left")
        funnel_data["conversions"] = funnel_data["conversions"].fillna(0)
    
        # Conversion rate
        funnel_data["conversion_rate"] = funnel_data["conversions"] / funnel_data["sessions"]
    
        # -------------------------------
        # ORDER STAGES
        # -------------------------------
        stage_order = ["Landing Page", "Product Page", "Cart", "Checkout", "Thank You"]
    
        funnel_data["funnel_stage"] = pd.Categorical(
            funnel_data["funnel_stage"],
            categories=stage_order,
            ordered=True
        )
        funnel_data = funnel_data.sort_values("funnel_stage")
    
        # -------------------------------
        # PLOT FUNNEL
        # -------------------------------
        fig = px.funnel(
            funnel_data,
            x="sessions",
            y="funnel_stage",
            title="Conversion Funnel by WebPage",
            text=funnel_data["conversion_rate"].apply(lambda x: f"{x:.1%}"),
            labels={"sessions": "Sessions", "funnel_stage": "Funnel Stage"}
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    
        # ------------------ Device-based Sessions ------------------
        st.subheader("Device-based Website Sessions")
    
        device_data = (
            website_sessions.groupby('device_type')['website_session_id']
            .nunique()
            .reset_index(name='sessions')
        )
    
        fig_device = px.pie(
            device_data,
            names='device_type',
            values='sessions',
            title="Sessions by Device Type"
        )
    
        fig_device.update_traces(textposition='inside', textinfo='percent+label')
        fig_device.update_layout(height=400)
    
        st.plotly_chart(fig_device, use_container_width=True)
    








