# 🔌 Salla Integration & Theme Development - Complete Implementation Plan

## 📋 Project Overview

**Target Store**: https://bloomore.shop/ar  
**Goal**: Create an out-of-the-box Salla data import system + custom theme development capability

---

## ✅ Phase 1: Salla Data Import System

### 🎯 **Objective**
Build a production-ready import page that works with Bloomore.shop and any Salla store.

### 📦 **What You'll Need**

#### **1. Salla OAuth 2.0 Integration**
- [ ] **Salla Partner Account** → [Sign up here](https://salla.partners/)
- [ ] **Create OAuth App** in Partner Portal
  - App Name: "Advanced Analytics for Salla"
  - Redirect URI: `http://localhost:8501` (dev) / `https://your-domain.com` (prod)
  - Scopes needed:
    - `offline_access` - for refresh tokens
    - `orders.read` - read order data
    - `products.read` - read product catalog
    - `customers.read` - read customer info
    - `sales.read` - sales analytics

- [ ] **Get Credentials**:
  - `CLIENT_ID`
  - `CLIENT_SECRET`
  - `WEBHOOK_SECRET`

#### **2. Backend API (FastAPI)**
- [ ] **Database**: PostgreSQL (production) / SQLite (development)
- [ ] **Models** (SQLModel ORM):
  ```python
  - Store (id, merchant_id, domain, access_token, refresh_token, expires_at)
  - WebhookLog (id, store_id, event_type, payload, processed_at)
  ```

- [ ] **API Endpoints**:
  ```
  GET  /auth/salla/authorize     - Redirect to Salla OAuth
  GET  /auth/salla/callback      - Handle OAuth callback
  POST /webhooks/salla           - Receive Salla webhooks
  GET  /api/stores               - List authorized stores
  GET  /api/stores/{id}/orders   - Fetch orders (paginated)
  GET  /api/stores/{id}/products - Fetch products
  GET  /api/stores/{id}/customers- Fetch customers
  ```

- [ ] **Salla Client** (Python):
  ```python
  class SallaClient:
      def __init__(self, access_token)
      def get_orders(page=1, per_page=50) → DataFrame
      def get_products(page=1, per_page=50) → DataFrame
      def get_customers(page=1, per_page=50) → DataFrame
      def refresh_token() → bool
  ```

#### **3. Frontend Import Page (Streamlit)**
- [ ] **Authorization Flow**:
  ```
  1. Click "Connect Salla Store"
  2. Redirect to Salla OAuth
  3. User authorizes app
  4. Callback saves tokens
  5. Show connected stores
  ```

- [ ] **Import Interface**:
  - Store selector dropdown
  - Data type selector (Orders / Products / Customers)
  - Date range picker (optional)
  - Page limit slider (1-100 pages)
  - Progress bar with cancel button
  - Preview table (first 100 rows)
  - Download CSV button
  - "Load into Analytics" button

- [ ] **Features**:
  - Automatic token refresh
  - Error handling with retry
  - Rate limit handling
  - Multi-store support
  - Incremental imports (sync new data only)

---

## 🎨 Phase 2: Custom Theme Development for Bloomore.shop

### 🎯 **Objective**
Create a custom Twilight theme matching Bloomore's brand identity.

### 📦 **What You'll Need**

#### **1. Development Environment**
- [ ] **Salla CLI** → [Install from GitHub](https://github.com/SallaApp/Salla-CLI)
  ```bash
  npm install -g @salla.sa/cli
  salla theme create bloomore-theme
  ```

- [ ] **GitHub Repository** (for theme hosting)
- [ ] **Node.js & npm** (for asset building)
- [ ] **Text Editor** (VS Code recommended)

#### **2. Theme Structure**
```
bloomore-theme/
├── twilight.json           # Theme configuration
├── assets/
│   ├── styles/
│   │   ├── main.scss       # Main stylesheet
│   │   ├── _variables.scss # Brand colors, fonts
│   │   └── _components.scss
│   ├── js/
│   │   └── app.js          # Custom JS
│   └── images/
│       └── logo.svg
├── views/
│   ├── layouts/
│   │   └── master.twig     # Main layout
│   ├── pages/
│   │   ├── home.twig       # Homepage
│   │   ├── product.twig    # Product page
│   │   ├── cart.twig       # Cart
│   │   └── checkout.twig   # Checkout
│   └── components/
│       ├── header.twig
│       ├── footer.twig
│       └── product-card.twig
├── locales/
│   ├── ar.json             # Arabic translations
│   └── en.json             # English translations
└── README.md
```

#### **3. Bloomore Brand Analysis**
Based on https://bloomore.shop/ar, the theme should have:

- [ ] **Color Palette** (extract from site):
  - Primary: #[extract]
  - Secondary: #[extract]
  - Accent: #[extract]
  - Background: #[extract]
  - Text: #[extract]

- [ ] **Typography**:
  - Headings: [Font family from site]
  - Body: [Font family from site]
  - RTL support (Arabic first-class)

- [ ] **Layout**:
  - Header: Logo left, nav center, icons right
  - Footer: Multi-column with social links
  - Product grid: 3-4 columns responsive
  - Mobile-first approach

- [ ] **Key Features**:
  - Mega menu navigation
  - Product quick view
  - Ajax cart
  - Wishlist integration
  - Instagram feed
  - Newsletter signup
  - WhatsApp chat integration

#### **4. Theme Configuration (twilight.json)**
```json
{
  "name": "Bloomore Theme",
  "version": "1.0.0",
  "author": "Your Name",
  "repository": "https://github.com/yourusername/bloomore-theme",
  "support_email": "support@yourdomain.com",
  "categories": ["Fashion", "Beauty"],
  "screenshots": [
    "screenshot1.png",
    "screenshot2.png"
  ],
  "settings": {
    "colors": {
      "primary": "#000000",
      "secondary": "#666666",
      "accent": "#ff6b6b"
    },
    "typography": {
      "heading_font": "Tajawal",
      "body_font": "Cairo"
    },
    "layout": {
      "header_style": "sticky",
      "footer_style": "multi-column"
    }
  }
}
```

---

## 🔗 Phase 3: Integration Architecture

### **Data Flow**

```
┌─────────────────┐
│  Bloomore.shop  │
│  (Salla Store)  │
└────────┬────────┘
         │ OAuth 2.0
         │ Webhooks
         ▼
┌─────────────────┐
│  FastAPI Backend│
│  (Port 8000)    │
│  ├── Auth       │
│  ├── Webhooks   │
│  └── Data API   │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│ Streamlit App   │
│ (Port 8501)     │
│  ├── Import UI  │
│  ├── Analytics  │
│  └── Reports    │
└─────────────────┘
```

### **Storage Strategy**

1. **Tokens** → PostgreSQL/SQLite (encrypted)
2. **Raw Data** → CSV exports + Session state
3. **Analytics** → In-memory DataFrames
4. **Reports** → Excel downloads

---

## 📝 Implementation Checklist

### **Priority 1: MVP Import System** (2-3 days)

- [ ] Set up Salla Partner account
- [ ] Create OAuth app + get credentials
- [ ] Build FastAPI backend:
  - [ ] Database models (Store, WebhookLog)
  - [ ] OAuth endpoints (/auth/salla/*)
  - [ ] Salla API client (SallaClient class)
  - [ ] Data endpoints (/api/stores/*/orders)
- [ ] Build Streamlit import page:
  - [ ] "Connect Store" button
  - [ ] Store selector
  - [ ] Data type + filters
  - [ ] Import with progress
  - [ ] Preview + download
- [ ] Test with Bloomore.shop:
  - [ ] Authorize app
  - [ ] Import 100 orders
  - [ ] Verify data quality
  - [ ] Load into analytics

### **Priority 2: Production Features** (1-2 days)

- [ ] Token refresh automation
- [ ] Webhook handling (real-time updates)
- [ ] Error handling + retry logic
- [ ] Rate limit protection
- [ ] Multi-store support
- [ ] Incremental sync (delta imports)
- [ ] Data validation + cleaning
- [ ] Loading states + error messages

### **Priority 3: Theme Development** (3-5 days)

- [ ] Extract Bloomore brand assets:
  - [ ] Colors (inspect site)
  - [ ] Fonts (check CSS)
  - [ ] Logo + images
  - [ ] Layout structure
- [ ] Set up theme project:
  - [ ] Initialize with Salla CLI
  - [ ] Create GitHub repo
  - [ ] Connect to Partners Portal
- [ ] Build theme:
  - [ ] Configure twilight.json
  - [ ] Create base layout (master.twig)
  - [ ] Build homepage template
  - [ ] Style product pages
  - [ ] Customize cart/checkout
  - [ ] Add components (header, footer, etc.)
- [ ] Test & deploy:
  - [ ] Preview on test store
  - [ ] Test responsiveness
  - [ ] Verify RTL support
  - [ ] Submit for review

---

## 🛠️ Technical Requirements

### **Backend Stack**
```
Python 3.10+
FastAPI 0.109+
SQLModel 0.0.14+
httpx 0.26+ (API calls)
cryptography 42.0+ (token encryption)
alembic 1.13+ (migrations)
```

### **Frontend Stack**
```
Streamlit 1.28+
pandas 2.1+
requests 2.31+
```

### **Theme Stack**
```
Node.js 18+
Salla CLI
Twig template engine
Sass/SCSS
Tailwind CSS (optional)
```

---

## 💡 Key Features Breakdown

### **Import Page Features**

1. **Store Management**
   - Connect unlimited Salla stores
   - Auto-detect store name + logo
   - Show authorization status
   - One-click reconnect

2. **Smart Importing**
   - Choose data type (Orders/Products/Customers)
   - Filter by date range
   - Set page limits (prevent timeouts)
   - Show estimated rows/time
   - Cancel mid-import

3. **Data Preview**
   - Display first 100 rows
   - Show column mapping
   - Highlight missing fields
   - Data quality indicators

4. **Export Options**
   - Download as CSV
   - Load into analytics engine
   - Save to session state
   - Auto-map columns

### **Theme Features**

1. **Bloomore-Specific**
   - Match exact colors
   - Use same fonts
   - Mirror layout structure
   - Brand consistency

2. **General E-commerce**
   - Product filtering
   - Search functionality
   - Cart management
   - Wishlist
   - Reviews/ratings
   - Social sharing

3. **Performance**
   - Lazy loading images
   - Minified CSS/JS
   - CDN for assets
   - SEO optimized

---

## 🎯 Success Criteria

### **Import System**
- ✅ Connect to Bloomore.shop successfully
- ✅ Import 1000+ orders without errors
- ✅ Map all columns correctly
- ✅ Load data into analytics in <30 seconds
- ✅ Handle token refresh automatically
- ✅ Support multiple stores simultaneously

### **Theme**
- ✅ Match Bloomore brand 95%+
- ✅ Pass Salla review requirements
- ✅ Mobile responsive (100% score)
- ✅ RTL support (Arabic native)
- ✅ Load time <3 seconds
- ✅ Convert better than default theme

---

## 📚 Resources

### **Salla Documentation**
- [Partner Portal](https://salla.partners/)
- [API Docs](https://docs.salla.dev/)
- [Theme Docs](https://docs.salla.dev/421877m0)
- [CLI Docs](https://docs.salla.dev/429774m0)
- [OAuth Guide](https://docs.salla.dev/oauth2)

### **Code Examples**
- [Salla PHP SDK](https://github.com/SallaApp/Salla-PHP-SDK)
- [Example Themes](https://github.com/SallaApp/theme-raed)
- [Webhook Examples](https://github.com/SallaApp/Salla-CLI)

---

## 🚀 Next Steps

**To get started immediately:**

1. **Create Salla Partner Account** → https://salla.partners/
2. **Set up OAuth App** → Get CLIENT_ID + CLIENT_SECRET
3. **I'll build the import system** (2-3 days)
4. **Extract Bloomore theme** (inspect colors, fonts)
5. **I'll create custom theme** (3-5 days)

**Total Timeline: ~1 week for full integration**

---

## ❓ Questions to Answer

Before we start, please provide:

1. **OAuth Credentials**:
   - [ ] Salla CLIENT_ID
   - [ ] Salla CLIENT_SECRET
   - [ ] Webhook SECRET

2. **Store Access**:
   - [ ] Do you own Bloomore.shop or just want to analyze it?
   - [ ] Will you authorize the app on the store?

3. **Theme Scope**:
   - [ ] Just Bloomore or multiple stores?
   - [ ] Custom features needed?
   - [ ] Timeline priority?

4. **Deployment**:
   - [ ] Local only or production?
   - [ ] Hosting provider? (Railway, Heroku, etc.)
   - [ ] Domain name?

---

## ✅ YES, I CAN DO THIS!

**I can build:**
1. ✅ **Salla Import System** - Complete OAuth + API integration
2. ✅ **Custom Theme** - Matching Bloomore's exact design
3. ✅ **Analytics Integration** - Seamless data flow
4. ✅ **Multi-store Support** - Works with any Salla store
5. ✅ **Production-Ready** - Error handling, security, performance

**Let's build it! 🚀**
