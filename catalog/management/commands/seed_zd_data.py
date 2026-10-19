from decimal import Decimal
from django.core.management.base import BaseCommand
from catalog.models import Category, Product, ProductImage
from portal.models import SiteSettings


class Command(BaseCommand):
    help = 'Seeds initial electronics categories and products in Rwandan Francs (RWF) for Z&D ELECTRONIC DEALS'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Site Settings...")
        settings = SiteSettings.get_settings()
        settings.company_name = "Z&D ELECTRONIC DEALS"
        settings.slogan = "BEFORE YOU BUY ELECTRONICS, ASK Z&D."
        settings.primary_phone = "+250 788 456 789"
        settings.whatsapp_number = "250788456789"
        settings.email_contact = "deals@zdelectronics.rw"
        settings.physical_address = "CHIC Building, 2nd Floor, Kigali, Rwanda | Direct Hub: Shenzhen & Guangzhou, China"
        settings.announcement_banner = "🇷🇼 Direct China Factory Sourcing to Kigali & Worldwide | Tested Quality & Transparent Prices"
        settings.standard_kigali_shipping_rwf = Decimal('3000.00')
        settings.upcountry_shipping_rwf = Decimal('6000.00')
        settings.save()

        self.stdout.write("Seeding Categories...")
        categories_data = [
            {
                'name': 'Smartphones',
                'slug': 'smartphones',
                'icon': 'smartphone',
                'description': 'Flagship and mid-range smartphones sourced directly from authorized China distributors and global brands.',
                'display_order': 1
            },
            {
                'name': 'Laptops & Computers',
                'slug': 'laptops-computers',
                'icon': 'laptop',
                'description': 'High-performance business, coding, and creative laptops with international warranties.',
                'display_order': 2
            },
            {
                'name': 'Fast Chargers & Adapters',
                'slug': 'chargers-adapters',
                'icon': 'zap',
                'description': 'Certified GaN multi-port ultra-fast wall chargers for phones, tablets, and laptops.',
                'display_order': 3
            },
            {
                'name': 'Power Banks & Portable Power',
                'slug': 'power-banks',
                'icon': 'battery-charging',
                'description': 'High-capacity airline-approved battery banks with fast power delivery up to 100W.',
                'display_order': 4
            },
            {
                'name': 'Headphones & Audio',
                'slug': 'headphones-audio',
                'icon': 'headphones',
                'description': 'Active noise-cancelling headphones, wireless earbuds, and studio equipment.',
                'display_order': 5
            },
            {
                'name': 'Smartwatches & Wearables',
                'slug': 'smartwatches-wearables',
                'icon': 'watch',
                'description': 'Fitness trackers, cellular smartwatches, and health-monitoring devices.',
                'display_order': 6
            },
            {
                'name': 'Phone Accessories & Protection',
                'slug': 'phone-accessories',
                'icon': 'shield',
                'description': 'Shockproof protective cases, 9H tempered glass screen protectors, and camera lens guards.',
                'display_order': 7
            },
            {
                'name': 'Computer Accessories & Storage',
                'slug': 'computer-accessories',
                'icon': 'hard-drive',
                'description': 'High-speed external NVMe SSDs, mechanical keyboards, multi-port docking stations, and ergonomic mice.',
                'display_order': 8
            },
            {
                'name': 'Other Electronics & Gadgets',
                'slug': 'other-electronics',
                'icon': 'cpu',
                'description': 'Drones, action cameras, smart home sensors, and specialized tech gear.',
                'display_order': 9
            },
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat, _ = Category.objects.update_or_create(
                slug=cdata['slug'],
                defaults=cdata
            )
            cat_objs[cdata['slug']] = cat

        self.stdout.write("Seeding Electronic Products in RWF...")
        products_data = [
            {
                'category': cat_objs['smartphones'],
                'name': 'Apple iPhone 15 Pro Max (256GB, Natural Titanium)',
                'slug': 'iphone-15-pro-max-256gb-titanium',
                'sku': 'ZD-IP15PM-256',
                'short_description': 'A17 Pro chip, Titanium design, 48MP main camera system with 5x optical zoom. Sourced from China authorized stock (Dual Physical Nano SIM).',
                'description': 'The iPhone 15 Pro Max features aerospace-grade titanium design that is both strong and remarkably light. Powered by the groundbreaking A17 Pro chip for unprecedented gaming performance and efficiency. Includes custom Action button and high-speed USB-C connectivity.',
                'specifications': {
                    'Condition': 'Brand New (Sealed Box)',
                    'Chipset': 'Apple A17 Pro (3nm)',
                    'Storage': '256GB NVMe',
                    'Display': '6.7-inch Super Retina XDR OLED (120Hz ProMotion)',
                    'SIM Configuration': 'Dual Physical Nano SIM (China / Global Edition)',
                    'Camera': '48MP Main + 12MP Ultra-Wide + 12MP 5x Telephoto',
                    'Battery': '4,441 mAh with Fast Charging'
                },
                'selling_price': Decimal('1480000.00'),  # 1,480,000 RWF
                'cost_price': Decimal('1290000.00'),     # Owner Confidential: 1,290,000 RWF
                'stock_quantity': 4,
                'low_stock_threshold': 2,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['smartphones'],
                'name': 'Samsung Galaxy S24 Ultra 5G (512GB, Titanium Gray)',
                'slug': 'samsung-galaxy-s24-ultra-512gb',
                'sku': 'ZD-S24U-512G',
                'short_description': 'Snapdragon 8 Gen 3, integrated S Pen, Galaxy AI capabilities, and 200MP quad-tele camera system.',
                'description': 'The Samsung Galaxy S24 Ultra delivers the ultimate mobile AI experience with Live Translate, Circle to Search with Google, and Note Assist. Encased in durable titanium with Corning Gorilla Armor glass.',
                'specifications': {
                    'Condition': 'Brand New Factory Sealed',
                    'Processor': 'Snapdragon 8 Gen 3 for Galaxy (4nm)',
                    'RAM': '12GB LPDDR5X',
                    'Storage': '512GB UFS 4.0',
                    'Display': '6.8-inch Dynamic LTPO AMOLED 2X (2600 nits peak)',
                    'Battery': '5000 mAh (45W Fast Charging)',
                    'S Pen': 'Integrated Bluetooth S Pen'
                },
                'selling_price': Decimal('1550000.00'),  # 1,550,000 RWF
                'cost_price': Decimal('1340000.00'),     # Owner: 1,340,000 RWF
                'stock_quantity': 3,
                'low_stock_threshold': 2,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['laptops-computers'],
                'name': 'Lenovo ThinkPad X1 Carbon Gen 11 (Intel Core i7 / 16GB / 512GB)',
                'slug': 'lenovo-thinkpad-x1-carbon-gen-11',
                'sku': 'ZD-TPX1-G11',
                'short_description': 'Ultralight carbon-fiber business laptop. Intel Core i7-1365U vPro, 16GB RAM, 14-inch WUXGA Anti-Glare display.',
                'description': 'Engineered with Intel Evo, the ThinkPad X1 Carbon Gen 11 delivers incredible responsiveness, all-day battery life, and military-grade MIL-STD-810H durability. Perfect for corporate executives and software engineers.',
                'specifications': {
                    'Condition': 'Brand New (International Package)',
                    'Processor': 'Intel Core i7-1365U (10 Cores, up to 5.2 GHz)',
                    'Memory': '16GB LPDDR5 6400MHz',
                    'Storage': '512GB PCIe Gen4 Performance NVMe SSD',
                    'Screen': '14.0-inch WUXGA (1920 x 1200) IPS 400 nits',
                    'Weight': '1.12 kg (2.48 lbs)',
                    'Keyboard': 'Backlit spill-resistant with TrackPoint'
                },
                'selling_price': Decimal('1850000.00'),  # 1,850,000 RWF
                'cost_price': Decimal('1580000.00'),     # Owner: 1,580,000 RWF
                'stock_quantity': 2,
                'low_stock_threshold': 1,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': False,  # Sourced on request / in transit
                'is_featured': True,
                'is_new_arrival': False,
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['laptops-computers'],
                'name': 'Apple MacBook Air 13.6-inch M2 (8GB Unified Memory / 256GB SSD)',
                'slug': 'macbook-air-m2-13-inch-midnight',
                'sku': 'ZD-MBA-M2-MID',
                'short_description': 'Supercharged by Apple M2 silicon, striking 13.6-inch Liquid Retina display, silent fanless design, up to 18 hours battery.',
                'description': 'Redesigned around the next-generation M2 chip, MacBook Air is impossibly thin and brings exceptional speed and power efficiency inside its durable all-aluminum enclosure.',
                'specifications': {
                    'Condition': 'Brand New Sealed',
                    'Processor': 'Apple M2 (8-core CPU, 8-core GPU)',
                    'RAM': '8GB Unified Memory',
                    'Storage': '256GB High-Speed SSD',
                    'Display': '13.6-inch Liquid Retina Display with True Tone',
                    'Charging': 'MagSafe 3 with Two Thunderbolt ports',
                    'Battery Life': 'Up to 18 hours'
                },
                'selling_price': Decimal('1320000.00'),  # 1,320,000 RWF
                'cost_price': Decimal('1150000.00'),     # Owner: 1,150,000 RWF
                'stock_quantity': 5,
                'low_stock_threshold': 2,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['chargers-adapters'],
                'name': 'Anker 65W GaN Fast Charger Prime (3-Port: 2x USB-C + 1x USB-A)',
                'slug': 'anker-65w-gan-fast-charger-prime',
                'sku': 'ZD-ANK-65W',
                'short_description': 'Gallium Nitride (GaN) technology charges 3 devices simultaneously at lightning speed. Powers laptops, tablets, and phones.',
                'description': 'Power 3 Devices at Once: With 2 USB-C ports and one USB-A port, you can charge your phone, notebook, and earbuds all at once from a single charger. Connect a single device to charge at up to 65W.',
                'specifications': {
                    'Total Output': '65W Max',
                    'Ports': '2x USB-C Power Delivery 3.0, 1x USB-A PowerIQ',
                    'Technology': 'GaNPrime intelligent power allocation',
                    'Safety': 'ActiveShield 2.0 temperature monitoring',
                    'Compatibility': 'MacBook, Dell XPS, iPhone 15/14, Samsung Galaxy S24, iPad'
                },
                'selling_price': Decimal('75000.00'),   # 75,000 RWF
                'cost_price': Decimal('48000.00'),      # Owner: 48,000 RWF
                'stock_quantity': 25,
                'low_stock_threshold': 5,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['power-banks'],
                'name': 'Baseus 20,000mAh 65W Fast Charging Laptop & Phone Power Bank',
                'slug': 'baseus-20000mah-65w-power-bank',
                'sku': 'ZD-BAS-20K65W',
                'short_description': 'High-power 65W portable power station with digital LED display. Fully capable of charging laptops and high-end smartphones multiple times.',
                'description': 'Engineered in Shenzhen, this Baseus power bank packs a massive 20,000mAh capacity with 65W Power Delivery output, allowing full-speed charging for MacBooks, ThinkPads, iPads, and smartphones.',
                'specifications': {
                    'Capacity': '20,000mAh / 74Wh (Airline Safe)',
                    'Max Output': '65W USB-C PD',
                    'Display': 'Real-time numeric LED (Voltage, Current, Battery %)',
                    'Inputs': 'USB-C and Micro-USB',
                    'Outputs': '1x USB-C + 2x USB-A'
                },
                'selling_price': Decimal('85000.00'),   # 85,000 RWF
                'cost_price': Decimal('55000.00'),      # Owner: 55,000 RWF
                'stock_quantity': 18,
                'low_stock_threshold': 5,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': True,
                'is_new_arrival': False,
                'image_url': 'https://images.unsplash.com/photo-1609592426861-125026214152?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['headphones-audio'],
                'name': 'Sony WH-1000XM5 Wireless Noise-Cancelling Headphones',
                'slug': 'sony-wh-1000xm5-wireless-anc',
                'sku': 'ZD-SNY-XM5',
                'short_description': 'Industry-leading noise cancellation with two processors and 8 microphones. Hi-Res Audio, 30 hours battery life.',
                'description': 'Our industry-leading noise cancellation reaches new heights with two processors controlling eight microphones, Auto NC Optimizer for automatically optimizing noise cancellation based on your wearing conditions and environment, and a specially designed driver unit.',
                'specifications': {
                    'Noise Cancellation': 'Dual-chip V1 + QN1 Active Noise Cancelling',
                    'Microphones': '8 Microphones with Beamforming voice pickup',
                    'Battery Life': '30 Hours (ANC ON), 40 Hours (ANC OFF)',
                    'Quick Charge': '3 minutes charge = 3 hours playback',
                    'Audio Codecs': 'LDAC, AAC, SBC (Hi-Res Wireless Certified)'
                },
                'selling_price': Decimal('495000.00'),  # 495,000 RWF
                'cost_price': Decimal('390000.00'),     # Owner: 390,000 RWF
                'stock_quantity': 6,
                'low_stock_threshold': 2,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['smartwatches-wearables'],
                'name': 'Samsung Galaxy Watch 6 Classic (47mm Bluetooth / LTE, Black)',
                'slug': 'samsung-galaxy-watch-6-classic-47mm',
                'sku': 'ZD-GW6C-47B',
                'short_description': 'Iconic rotating bezel, Sapphire Crystal glass, advanced sleep coaching, ECG, Blood Pressure, and Body Composition sensor.',
                'description': 'Timeless design meets revolutionary health tracking. With a 15% thinner rotating bezel and a 20% larger display, Galaxy Watch 6 Classic empowers you to understand your heart health, workouts, and sleep quality.',
                'specifications': {
                    'Case Size': '47mm Stainless Steel',
                    'Display': '1.5-inch Super AMOLED with Sapphire Crystal Glass',
                    'Sensors': 'BioActive Sensor (Optical Heart Rate + Electrical Heart + BIA)',
                    'Water Resistance': '5ATM + IP68 / MIL-STD-810H',
                    'Battery': '425 mAh with WPC Wireless Fast Charging'
                },
                'selling_price': Decimal('420000.00'),  # 420,000 RWF
                'cost_price': Decimal('330000.00'),     # Owner: 330,000 RWF
                'stock_quantity': 4,
                'low_stock_threshold': 2,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': False,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['computer-accessories'],
                'name': 'Ugreen 9-in-1 USB-C Multiport Docking Station Hub (4K HDMI, Gigabit LAN, 100W PD)',
                'slug': 'ugreen-9-in-1-usb-c-docking-hub',
                'sku': 'ZD-UGR-9IN1',
                'short_description': 'Expand a single USB-C port into 4K@60Hz HDMI, 1000Mbps Gigabit Ethernet, 100W PD Pass-through, SD/TF card slots, and 3x USB 3.0 ports.',
                'description': 'The ultimate all-in-one connectivity dock for MacBook Pro/Air, Lenovo ThinkPad, Dell, and iPad Pro. Aluminum alloy body dissipates heat efficiently.',
                'specifications': {
                    'Video Output': 'HDMI 4K @ 60Hz Ultra HD',
                    'Networking': 'Gigabit RJ45 Ethernet (10/100/1000 Mbps)',
                    'Power Pass-through': '100W USB-C Power Delivery',
                    'Data Ports': '3x USB 3.0 (5Gbps Transfer Speed)',
                    'Card Reader': 'SD & MicroSD Dual Slot Simultaneous Read'
                },
                'selling_price': Decimal('68000.00'),   # 68,000 RWF
                'cost_price': Decimal('42000.00'),      # Owner: 42,000 RWF
                'stock_quantity': 15,
                'low_stock_threshold': 4,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': False,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1622434641406-a158123450f9?auto=format&fit=crop&w=800&q=80'
            },
            {
                'category': cat_objs['phone-accessories'],
                'name': 'Z&D Kevlar Magnetic Armor Shockproof Case for iPhone 15 Pro Max',
                'slug': 'zd-kevlar-magnetic-case-iphone-15-pro-max',
                'sku': 'ZD-CASE-15PM-KEV',
                'short_description': 'Aerospace 1500D Aramid Fiber with reinforced MagSafe ring. Ultra-slim 0.8mm profile with 10ft military drop protection.',
                'description': 'Precision manufactured from genuine 1500D Aramid Kevlar fiber. Resists scratches, fingerprints, and impacts without adding bulk.',
                'specifications': {
                    'Material': '1500D Genuine Aramid / Kevlar Fiber',
                    'MagSafe': 'N52 Ultra-strong neodymium magnet ring',
                    'Drop Protection': 'Military Grade 10ft drop tested',
                    'Weight': 'Only 22 grams'
                },
                'selling_price': Decimal('32000.00'),   # 32,000 RWF
                'cost_price': Decimal('16000.00'),      # Owner: 16,000 RWF
                'stock_quantity': 35,
                'low_stock_threshold': 5,
                'is_sourced_from_china': True,
                'in_stock_in_rwanda': True,
                'is_featured': False,
                'is_new_arrival': True,
                'image_url': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80'
            }
        ]

        for pdata in products_data:
            img_url = pdata.pop('image_url', None)
            prod, created = Product.objects.update_or_create(
                sku=pdata['sku'],
                defaults=pdata
            )
            if img_url:
                ProductImage.objects.update_or_create(
                    product=prod,
                    is_primary=True,
                    defaults={'image_url': img_url, 'alt_text': prod.name}
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Z&D Electronic Deals categories, products in RWF, and site configuration!"))
