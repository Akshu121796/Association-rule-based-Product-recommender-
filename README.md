
# 🛍️ ShopSense - Product Recommendation System

A beginner-friendly e-commerce product recommender app using **Association Rule Mining (Apriori)** with a modern, clean UI built with Gradio.

## 🎯 Features

- **Smart Recommendations**: Uses Apriori algorithm to find products frequently bought together
- **User Authentication**: Login/Signup system with user profiles
- **Product Management**: Like products and add to wishlist
- **Modern UI**: Clean, light-theme interface with gradient login page
- **Product Details**: Click on recommendations to view detailed product information

## 🔍 How It Works

- Uses **Apriori algorithm** (Association Rule Mining) to discover frequent itemsets
- Generates association rules using confidence metrics
- Recommends up to 4 products based on selected items
- Shows product details with images, prices, and descriptions

## 🚀 Tech Stack

- **Python** - Backend logic
- **Gradio** - Web interface framework
- **mlxtend** - Machine learning library for Apriori algorithm
- **pandas** - Data manipulation
- **numpy** - Numerical operations

---
title: association-rule-recommender
app_file: app.py
sdk: gradio
sdk_version: 6.2.0
---
## 📦 Installation & Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will start at `http://127.0.0.1:7860` (or next available port)

## 🌐 Deploy to Hugging Face Spaces

1. Create a Hugging Face account at [huggingface.co](https://huggingface.co)
2. Create a new Space:
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Gradio" as SDK
   - Name your space (e.g., `shop-sense-recommender`)
3. Upload your files:
   - `app.py`
   - `requirements.txt`
   - `data/` folder (with products.csv and transactions.csv)
   - `README.md`
4. Your app will automatically deploy!

## 📁 Project Structure

```
association-rule-recommender/
├── app.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── data/
│   ├── products.csv    # Product catalog
│   └── transactions.csv # Transaction history
└── .gitignore          # Git ignore file
```

## 🔐 Default Login

- **Username**: `admin`
- **Password**: `admin`

Or create a new account using the Sign Up button.

## 🛠️ Development Status

This project is in active development. Current features:
- ✅ User authentication (login/signup)
- ✅ Product recommendations using Apriori
- ✅ Product detail view
- ✅ Like and wishlist functionality
- ✅ Modern UI with responsive design

## 📝 License

This project is open source and available for educational purposes.
