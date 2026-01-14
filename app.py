import gradio as gr
import pandas as pd
import os
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

products_df = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
products_df["price"] = pd.to_numeric(products_df["price"], errors="coerce").fillna(999)

if "liked_count" not in products_df.columns:
    products_df["liked_count"] = 1200
if "cart_count" not in products_df.columns:
    products_df["cart_count"] = 800


transactions = []
try:
    with open(os.path.join(DATA_DIR, "transactions.csv"), "r", encoding="utf-8") as f:
        for line in f:
            items = [i.strip() for i in line.split(",") if i.strip()]
            if items:
                transactions.append(items)
except:
    transactions = [["Phone", "Phone Cover"], ["Phone", "Charger"]]

te = TransactionEncoder()
encoded = te.fit(transactions).transform(transactions)
df_encoded = pd.DataFrame(encoded, columns=te.columns_)
freq_items = apriori(df_encoded, min_support=0.001, use_colnames=True)
rules = association_rules(freq_items, metric="confidence", min_threshold=0.01)


USERS = {"admin": "admin"}
current_user = None
user_liked = {}
user_cart = {}
user_recent = {}


def profile_display():
    return f"**👤 Username:** {current_user}"

def liked_count_display():
    return f"❤️ {len(user_liked.get(current_user, []))} items"

def cart_count_display():
    return f"🛒 {len(user_cart.get(current_user, []))} items"


def login(un, pw):
    global current_user
    if un in USERS and USERS[un] == pw:
        current_user = un
        user_liked.setdefault(un, [])
        user_cart.setdefault(un, [])
        user_recent.setdefault(un, [])
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            profile_display(),
            liked_count_display(),
            cart_count_display(),
            ""
        )
    return gr.update(), gr.update(), "", "", "", "❌ Invalid credentials"

def signup(un, pw):
    global current_user
    USERS[un] = pw
    current_user = un
    user_liked[un] = []
    user_cart[un] = []
    user_recent[un] = []
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        profile_display(),
        liked_count_display(),
        cart_count_display(),
        ""
    )

def logout():
    global current_user
    current_user = None
    return gr.update(visible=True), gr.update(visible=False), "", "", "", ""

def like_product(product):
    if product not in user_liked[current_user]:
        user_liked[current_user].append(product)
        products_df.loc[
            products_df["product_name"] == product, "liked_count"
        ] += 1
    return liked_count_display(), cart_count_display()

def cart_product(product):
    if product not in user_cart[current_user]:
        user_cart[current_user].append(product)
        products_df.loc[
            products_df["product_name"] == product, "cart_count"
        ] += 1
    return liked_count_display(), cart_count_display()


    return liked_count_display(), cart_count_display()



def format_gallery_item(row, badge_text=""):
    
    label = f"{row['product_name']} | ₹{int(row['price'])}"
    if badge_text:
        label += f" ({badge_text})"
    return (row['image_url'], label)

def get_product_details(product_name):
    
    row = products_df[products_df["product_name"] == product_name].iloc[0]
    desc = f"Experience the premium quality of {product_name}. Perfect for your daily needs."
    stats = f"""
    *   **❤️ Liked by:** {int(row['liked_count'])} users
    *   **🛒 Added to cart by:** {int(row['cart_count'])} users
    """
    
    return (
        row['image_url'], 
        f"## {product_name}", 
        f"### ₹{int(row['price'])}", 
        desc, 
        stats
    )

def liked_dashboard():
    # Helper to return updates
    def clear_main(): return gr.update(visible=False, value=[])
    
    if not user_liked.get(current_user):
        msg = """
        <div style='text-align:center; padding:100px 20px;'>
            <h2 style='font-size: 2em; margin-bottom: 20px;'>💔 No Liked Products Yet</h2>
            <p style='font-size: 1.2em; color: #9ca3af;'>Start browsing to find items you love!</p>
        </div>
        """
        # OUTPUTS: [gallery_main, gallery_secondary, current_products_state, input_group, detail_view, empty_msg]
        return clear_main(), gr.update(visible=False, value=[]), [], gr.update(visible=False), gr.update(visible=False), gr.update(visible=True, value=msg)
    
    gallery_data = []
    product_list = []
    
    for p in user_liked.get(current_user, []):
        if p in product_list: continue 
        row = products_df[products_df["product_name"] == p].iloc[0]
        gallery_data.append(format_gallery_item(row, "❤️ Liked"))
        product_list.append(p)
        
    # Show Secondary, Hide Main
    return clear_main(), gr.update(visible=True, value=gallery_data), product_list, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False, value="")

def cart_dashboard():
    def clear_main(): return gr.update(visible=False, value=[])

    if not user_cart.get(current_user):
        msg = """
        <div style='text-align:center; padding:100px 20px;'>
            <h2 style='font-size: 2em; margin-bottom: 20px;'>🛒 Your Cart is Empty</h2>
            <p style='font-size: 1.2em; color: #9ca3af;'>Add items to your cart to see them here.</p>
        </div>
        """
        return clear_main(), gr.update(visible=False, value=[]), [], gr.update(visible=False), gr.update(visible=False), gr.update(visible=True, value=msg)
    
    gallery_data = []
    product_list = []
    for p in user_cart.get(current_user, []):
        if p in product_list: continue
        row = products_df[products_df["product_name"] == p].iloc[0]
        gallery_data.append(format_gallery_item(row, "🛒 In Cart"))
        product_list.append(p)
        
    return clear_main(), gr.update(visible=True, value=gallery_data), product_list, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False, value="")

def recent_dashboard():
    def clear_main(): return gr.update(visible=False, value=[])
    
    recent_items = user_recent.get(current_user, [])[::-1]
    
    if not recent_items:
        return clear_main(), gr.update(visible=False, value=[]), [], gr.update(visible=False), gr.update(visible=False), gr.update(visible=True, value="<div style='text-align:center'>No history</div>")
        
    gallery_data = []
    product_list = []
    seen = set()
    for p in recent_items:
        if p in seen: continue
        seen.add(p)
        row = products_df[products_df["product_name"] == p].iloc[0]
        gallery_data.append(format_gallery_item(row, "🕒 Recent"))
        product_list.append(p)
        
    return clear_main(), gr.update(visible=True, value=gallery_data), product_list, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False, value="")


def home_dashboard():
    # Show Main, Hide Secondary
    return (
        gr.update(visible=True, value=[]), # gallery_main (visible but empty initially or reset?)
        gr.update(visible=False, value=[]), # gallery_secondary
        gr.update(visible=False), 
        gr.update(visible=True, value="<div style='text-align:center; padding:50px;'><h3>👋 Welcome Back!</h3><p>Select a product to get started.</p></div>"),
        gr.update(visible=True), # input_group
    )


def recommend(product):
    # Show Main, Hide Secondary
    
    if current_user:
        if current_user not in user_recent:
            user_recent[current_user] = []
        user_recent[current_user].append(product)


    recs_map = {}
    
    for _, r in rules.iterrows():
        
        target_products = []
        trigger = ""
        conf = r["confidence"]
        
        if product in r["antecedents"]:
            target_products = list(r["consequents"])
            trigger = product 
        elif product in r["consequents"]:
            target_products = list(r["antecedents"])
            trigger = product 

        for p in target_products:
            if p == product: continue
            if p not in recs_map or conf > recs_map[p]['confidence']:
                recs_map[p] = {'confidence': conf, 'trigger': trigger}


    sorted_recs = sorted(recs_map.items(), key=lambda x: x[1]['confidence'], reverse=True)
    top_recs = sorted_recs[:4]
    
    if not top_recs:
        # gallery_main, gallery_secondary, current_products_state, input_group, detail_view, empty_msg
        return gr.update(visible=True, value=[]), gr.update(visible=False), [], gr.update(visible=True), gr.update(visible=False), gr.update(visible=True, value="<div style='text-align:center'>No recommendations found</div>")

    gallery_data = []
    product_list = []
    
    for name, info in top_recs:
        row_matches = products_df[products_df["product_name"] == name]
        if row_matches.empty: continue
        row = row_matches.iloc[0]
        
        
        badges = []
        if row['liked_count'] > 1000: badges.append("❤️ Hot")
        if row['cart_count'] > 800: badges.append("🔥 Popular")
        badge_str = " ".join(badges)
        
        gallery_data.append(format_gallery_item(row, badge_str))
        product_list.append(name)
        
    return gr.update(visible=True, value=gallery_data), gr.update(visible=False), product_list, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False, value="") 


def on_select(evt: gr.SelectData, product_list):
    if evt.index < len(product_list):
        selected_name = product_list[evt.index]
        img, title, price, desc, stats = get_product_details(selected_name)
        return (
            selected_name, 
            img, title, price, desc, stats, 
            gr.update(visible=False), # gallery_main
            gr.update(visible=False), # gallery_secondary
            gr.update(visible=False), # input_group
            gr.update(visible=True),  # detail_view
            gr.update(visible=False)  # empty_msg
        )
    return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

def back_to_results():
    # Note: We can't easily remember which gallery was active without extra state. 
    # For now, default to Home view interaction style or just show what was likely active?
    # Simpler: Make both visible=False, and user has to click nav? No, that's bad.
    # Quick fix: Show gallery_main by default (Home) or we need a state to track "active_tab".
    # User didn't ask for "active tab state", just split. 
    # Let's assume Back -> Home/Main for now, or just show the Main gallery.
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

def like_from_detail(product):
    return like_product(product)

def cart_from_detail(product):
    return cart_product(product) 


CSS = """
body, html, .gradio-container {
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important; 
    background: #0b1220;
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

.main-row {
    height: 100vh !important;
    display: flex !important;
    align-items: stretch !important;
}


.sidebar {
    background: #ffffff;
    height: 100vh !important;
    overflow-y: auto !important;
    padding: 25px !important;
    border-right: 1px solid #e5e7eb;
    flex-shrink: 0 !important;
}


.main-content {
    height: 100vh !important;
    overflow-y: auto !important;
    padding: 30px !important;
    flex-grow: 1 !important;
}

/* Login Page Styles */
.login-bg { background: linear-gradient(135deg,#667eea,#764ba2); height: 100vh; }
.login-card { background: #111827; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
.sidebar button { background: #f8fafc; border: 1px solid #cbd5e1; color: #334155; text-align: left; font-weight: 600; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; transition: all 0.2s ease; }
.sidebar button:hover { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; transform: translateY(-1px); }
.sidebar * { color: #111827 !important; }

#product-gallery {
    display: block !important;
    width: 100% !important;
    padding: 0 !important;
}


#product-gallery .grid-wrap, 
#product-gallery > div > div {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)) !important;
    gap: 30px !important;
    width: 100% !important;
}


/* The Card Container */
#product-gallery button, 
#product-gallery .gallery-item {
    display: flex !important;
    flex-direction: column !important;
    background: #1f2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4) !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    transition: transform 0.2s ease-in-out;
}

#product-gallery button:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5) !important;
}

/* The Image */
#product-gallery img {
    width: 100% !important;
    height: 250px !important; 
    object-fit: cover !important;
    border-bottom: 1px solid #374151 !important;
    border-radius: 16px 16px 0 0 !important;
    background: #fff; 
}

/* The Text/Caption */
#product-gallery .caption-label {
    padding: 16px !important;
    background: #1f2937 !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #f3f4f6 !important; 
    text-align: left !important;
    width: 100% !important;
    display: block !important;
}

/* Hide detail view borders */
.group-container { border: none !important; padding: 0 !important; }

/* ======================================
   SECONDARY PRODUCT CARDS (SMALL)
   Used for: Recently Viewed, Liked, Wishlist
   ====================================== */

.secondary-gallery {
    width: 100%;
}

/* Always 2 cards per row */
.secondary-gallery .grid-wrap,
.secondary-gallery > div > div {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 16px !important;
}

/* Smaller card container */
.secondary-gallery button,
.secondary-gallery .gallery-item {
    background: #1f2937 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 6px 10px rgba(0,0,0,0.35) !important;
    min-height: auto !important;
}

/* Smaller images */
/* Smaller images */
.secondary-gallery img {
    height: 250px !important;
    width: 100% !important;
    object-fit: contain !important;
    background: #ffffff !important;
    padding: 10px !important;
    border-radius: 10px 10px 0 0 !important;
}

/* Compact text */
.secondary-gallery .caption-label {
    padding: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    background: #1f2937 !important;
    color: #f3f4f6 !important;
}

/* Hide Fullscreen/Maximize & Share Buttons Globally */
button[aria-label="Fullscreen"],
button[aria-label="Maximize"],
button[aria-label="Share"],
.share-button,
.fullscreen-button {
    display: none !important;
}

"""


with gr.Blocks(theme=gr.themes.Soft()) as app:
    current_products_state = gr.State([])
    selected_product_state = gr.State("")

   
    with gr.Row(visible=True) as login_view:
        with gr.Column(scale=2, elem_classes="login-bg"):
            gr.HTML("""
                <div style='text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%; padding: 40px;'>
                    <h1 style='font-size: 4em; font-weight: 800; margin-bottom: 20px; color: white;'>🛍️ ShopSense</h1>
                    <p style='font-size: 1.5em; color: #e5e7eb; margin-top: 0;'>Smart Association-rule based Recommendations</p>
                </div>
            """)
        with gr.Column(scale=1):
            with gr.Column(elem_classes="login-card"):
                un = gr.Textbox(label="Username")
                pw = gr.Textbox(label="Password", type="password")
                login_btn = gr.Button("Login")
                signup_btn = gr.Button("Sign Up")
                status = gr.Markdown()

   
    with gr.Row(visible=False) as main_view:

        with gr.Column(scale=1, elem_classes="sidebar"):
            gr.HTML("<div style='text-align: center; margin-bottom: 20px;'><h2 style='font-size: 28px; font-weight: 800; color: #111827; margin: 0;'>🛍️ ShopSense</h2></div>") # Centered & Big Title
            profile = gr.Markdown()
            home_btn = gr.Button("🏠 Home")
            recent_btn = gr.Button("🕒 Recently Viewed")
            liked_btn = gr.Button("❤️ Liked Products")
            liked_count = gr.Markdown()
            cart_btn = gr.Button("🛒 Cart / Wishlist")
            cart_count = gr.Markdown()
            logout_btn = gr.Button("Logout")

        with gr.Column(scale=3):
           
            with gr.Column(visible=True) as input_group:
                dropdown = gr.Dropdown(products_df["product_name"].tolist(), label="Select Product")
                rec_btn = gr.Button("Get Recommendations")
            
            # --- MAIN GALLERY (Large cards) ---
            gallery_main = gr.Gallery(
                label="Products", 
                show_label=False, 
                visible=False,
                allow_preview=False,
                object_fit="contain",
                height="auto",
                elem_id="product-gallery",  # Uses Large CSS
                columns=2 
            )

            # --- SECONDARY GALLERY (Compact cards) ---
            gallery_secondary = gr.Gallery(
                label="Other Items",
                show_label=False,
                visible=False,
                allow_preview=False,
                object_fit="contain",
                height="auto",
                elem_classes=["secondary-gallery"], # Uses Compact CSS
                columns=2
            )

            empty_msg = gr.HTML(visible=True, value="<div style='text-align:center; padding:50px;'><h3>👋 Welcome Back!</h3><p>Select a product to get started.</p></div>")

            
            with gr.Group(visible=False) as detail_view:
                back_btn = gr.Button("← Back to Results")
                with gr.Row():
                    detail_img = gr.Image(label="Product Image", show_label=False, height=400, width=400, container=False)
                    with gr.Column():
                        detail_title = gr.Markdown()
                        detail_price = gr.Markdown()
                        detail_desc = gr.Markdown()
                        detail_stats = gr.Markdown()
                        with gr.Row():
                            detail_like_btn = gr.Button("❤️ Like", variant="secondary")
                            detail_cart_btn = gr.Button("🛒 Add to Cart", variant="primary")

   
    login_btn.click(login, [un, pw], [login_view, main_view, profile, liked_count, cart_count, status])
    signup_btn.click(signup, [un, pw], [login_view, main_view, profile, liked_count, cart_count, status])
    logout_btn.click(logout, outputs=[login_view, main_view, profile, liked_count, cart_count, status])

    # NOTE: Output order must match functions!
    # home_dashboard: gallery_main, gallery_secondary, detail_view, empty_msg, input_group
    home_btn.click(
        home_dashboard, 
        outputs=[gallery_main, gallery_secondary,  detail_view, empty_msg, input_group]
    )

    # liked, cart, recent: gallery_main, gallery_secondary, current_products, input_group, detail_view, empty_msg
    liked_btn.click(
        liked_dashboard, 
        outputs=[gallery_main, gallery_secondary, current_products_state, input_group, detail_view, empty_msg]
    )
    cart_btn.click(
        cart_dashboard, 
        outputs=[gallery_main, gallery_secondary, current_products_state, input_group, detail_view, empty_msg]
    )
    recent_btn.click(
        recent_dashboard, 
        outputs=[gallery_main, gallery_secondary, current_products_state, input_group, detail_view, empty_msg]
    )

    # recommend: gallery_main, gallery_secondary, current_products, input_group, detail_view, empty_msg
    rec_btn.click(
        recommend, 
        inputs=[dropdown], 
        outputs=[gallery_main, gallery_secondary, current_products_state, input_group, detail_view, empty_msg]
    )

    # Select handlers: Need ONE for each gallery
    gallery_main.select(
        on_select,
        inputs=[current_products_state],
        outputs=[selected_product_state, detail_img, detail_title, detail_price, detail_desc, detail_stats, gallery_main, gallery_secondary, input_group, detail_view, empty_msg]
    )

    gallery_secondary.select(
        on_select,
        inputs=[current_products_state],
        outputs=[selected_product_state, detail_img, detail_title, detail_price, detail_desc, detail_stats, gallery_main, gallery_secondary, input_group, detail_view, empty_msg]
    )

    back_btn.click(back_to_results, outputs=[gallery_main, gallery_secondary, detail_view])
    detail_like_btn.click(like_from_detail, selected_product_state, [liked_count, cart_count])
    detail_cart_btn.click(cart_from_detail, selected_product_state, [liked_count, cart_count])

if __name__ == "__main__":
    app.launch(css=CSS, allowed_paths=["."], share=True)
