# Z&D ELECTRONIC DEALS — Complete E-Commerce Platform

> **Main Slogan**: "BEFORE YOU BUY ELECTRONICS, ASK Z&D."  
> **Brand Palette**: Deep Navy Blue (`#0B1B3D`), Royal Blue (`#1E56A0`), Clean White (`#FFFFFF`), Gold/Yellow Accents (`#D4AF37`)  
> **Primary Currency**: Rwandan Francs (RWF)  
> **Specialization**: Direct electronics sourcing from China (Shenzhen & Guangzhou) to Kigali, Rwanda and worldwide.

---

## 🌟 Overview for the Business Owner

This is a full-stack, enterprise-grade, secure e-commerce application designed specifically for **Z&D ELECTRONIC DEALS**. It is fully working and built with Python 3, Django, Tailwind CSS, and Lucide icons.

### Key Capabilities Built for You:
1. **Public Storefront**: Modern, mobile-responsive homepage, catalogue filtering, search, and device specification tables priced in **Rwandan Francs (RWF)**.
2. **Owner Management Portal (`/portal/`)**:
   - Add, edit, publish, or delete products and manage product photos.
   - Adjust selling prices (RWF) and stock quantities.
   - View confidential procurement costs and **estimated gross profit margins** (strictly hidden from staff and customers).
   - **Edit website content directly**: Change your company phone, WhatsApp direct number, top announcement banner, office address, and policies right from the browser.
   - Track and update customer order fulfillment (Pending → Confirmed → China Sourcing → In Transit → Arrived in Kigali → Delivered).
   - View customer contact messages and reply via WhatsApp.
   - Promote or assign staff roles (Order Staff, Manager, Owner).
   - View security and activity audit logs.
3. **Strict Customer Privacy & Account Isolation**:
   - Customer A can **never** see or modify Customer B's orders, profile, or addresses.
   - Enforced cryptographically on the server and database (`customer=request.user`).
   - Tampered URLs or IDs return `404 Not Found` without disclosing any customer data.
4. **WhatsApp Ordering & Quoting**:
   - Pre-formatted WhatsApp order messages allow customers in Rwanda to confirm orders and arrange delivery directly with your sales team.

---

## 🚀 How to Run the Website on Your Computer

### 1. Open PowerShell in the project directory
```powershell
cd "d:\maze\Z&D WEBSITE"
```

### 2. Start the Development Server
```powershell
python manage.py runserver
```

Now open your web browser and visit:
- **Public Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Owner Management Portal**: [http://127.0.0.1:8000/portal/](http://127.0.0.1:8000/portal/)
- **Customer Sign In**: [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)

---

## 🔑 Pre-Configured Accounts for Testing

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `owner@zdelectronics.rw` | `OwnerPassword123!` | Full control over website, products, prices, profit estimates, staff roles, and settings. |
| **Customer 1** | `jean.claud@rwanda.rw` | `CustomerPass123!` | Can only access Order `ZD-2026-1001` and own profile. |
| **Customer 2** | `marie.grace@rwanda.rw` | `CustomerPass123!` | Can only access Order `ZD-2026-1002` and own profile. |

---

## 🛡️ Running the Automated Security & Isolation Tests

To verify that Customer A cannot access Customer B's records, and customers cannot access the management portal:

```powershell
python manage.py test accounts
```

You will see:
```text
Ran 9 tests in ...s
OK
```

All 9 security assertions pass, confirming customer isolation, IDOR protection, and server-side pricing integrity.

---

## ⚙️ How to Make Edits as the Business Owner

1. Go to [http://127.0.0.1:8000/portal/](http://127.0.0.1:8000/portal/) and log in with your Owner credentials.
2. **To Edit Website Content & Contact Info**: Click **"Website Content & Edit"** in the sidebar. You can edit your phone number, WhatsApp link, top announcement banner, shipping fees in RWF, and policies. Click **Save All Website Changes** to update the public site instantly.
3. **To Add or Edit Products**: Click **"Products & Stock"**. Click on any product to update prices in RWF, stock on hand, specifications, or upload photos.
4. **To Manage Orders**: Click **"Customer Orders"**. You can open any order, update its status (e.g., mark as "In Transit to Rwanda"), assign an Airway Bill tracking code, and add internal staff notes.

---

## 🌐 Production Deployment & Hosting Guide

When you are ready to publish Z&D Electronic Deals to the internet:

1. **Hosting Provider**:
   - **Render** or **Railway** (Recommended for beginners): Offers 1-click Python deployment with free or $5/month tiers.
   - **PythonAnywhere**: $5/month simple web hosting.
2. **Database**:
   - Managed PostgreSQL database on Supabase or Render (Free tier covers initial launch).
3. **Custom Domain**:
   - Purchase your domain name (e.g. `zdelectronics.rw` via IGIHE/RITA or `.com` via Namecheap) for ~$10–$25/year.
4. **SSL / HTTPS**:
   - Free automated SSL certificate via Let's Encrypt / Cloudflare.
5. **Estimated Recurring Costs**:
   - **Development**: $0.00
   - **First Year Hosting + Domain**: ~$10 to $25 total.
