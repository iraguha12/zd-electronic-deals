from django import forms
from catalog.models import Product, ProductImage, Category
from orders.models import Order
from portal.models import SiteSettings
from accounts.models import CustomUser


class ProductForm(forms.ModelForm):
    primary_photo = forms.ImageField(
        required=False,
        label="Product Photo (upload from your computer/phone)",
        widget=forms.FileInput(attrs={
            'class': 'w-full text-xs text-slate-500 file:mr-3 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-zdroyal-50 file:text-zdroyal-700 hover:file:bg-zdroyal-100',
            'accept': 'image/*'
        })
    )
    image_url = forms.URLField(
        required=False,
        label="OR Direct Cloud Image Link",
        widget=forms.URLInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm',
            'placeholder': 'https://example.com/image.jpg'
        })
    )
    specs_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-mono',
            'rows': 4,
            'placeholder': 'Storage: 256GB\nRAM: 8GB\nBattery: 5000 mAh\nCondition: Brand New (China Sourced)'
        }),
        required=False,
        help_text="Enter key: value pairs, one per line (e.g. RAM: 8GB)"
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'sku', 'selling_price', 'cost_price',
            'stock_quantity', 'low_stock_threshold', 'short_description', 'description',
            'video_file', 'video_url',
            'is_sourced_from_china', 'in_stock_in_rwanda', 'requires_quote',
            'is_featured', 'is_new_arrival', 'is_published',
            'warranty_info', 'estimated_delivery_days'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'e.g. iPhone 15 Pro Max'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'sku': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Optional (leave blank to auto-generate)'}),
            'selling_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Price in RWF'}),
            'cost_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Cost in RWF (Owner Only)'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'short_description': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Brief 1-sentence summary'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 4, 'placeholder': 'Full details, condition, inbox items'}),
            'video_file': forms.FileInput(attrs={'class': 'w-full text-xs text-slate-500 file:mr-3 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100', 'accept': 'video/mp4,video/webm,video/quicktime'}),
            'video_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'https://www.youtube.com/watch?v=... or video link'}),
            'warranty_info': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'estimated_delivery_days': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sku'].required = False
        self.fields['category'].required = False
        if self.instance and self.instance.pk:
            if self.instance.specifications:
                lines = [f"{k}: {v}" for k, v in self.instance.specifications.items()]
                self.fields['specs_text'].initial = "\n".join(lines)
            primary_img = self.instance.images.filter(is_primary=True).first()
            if primary_img and primary_img.image_url:
                self.fields['image_url'].initial = primary_img.image_url

    def save(self, commit=True):
        instance = super().save(commit=False)
        specs = {}
        specs_data = self.cleaned_data.get('specs_text', '')
        for line in specs_data.split('\n'):
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                specs[key.strip()] = val.strip()
        instance.specifications = specs
        if commit:
            instance.save()
            photo = self.cleaned_data.get('primary_photo')
            img_url = self.cleaned_data.get('image_url')
            if photo or img_url:
                primary = instance.images.filter(is_primary=True).first()
                if primary:
                    if photo:
                        primary.image = photo
                    if img_url:
                        primary.image_url = img_url
                    primary.save()
                else:
                    ProductImage.objects.create(
                        product=instance,
                        image=photo,
                        image_url=img_url,
                        is_primary=True,
                        alt_text=instance.name
                    )
        return instance


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'image_url', 'alt_text', 'is_primary']
        widgets = {
            'image_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'https://example.com/image.jpg'}),
            'alt_text': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Description of image'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded border-slate-300'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'icon', 'display_order', 'is_active', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'e.g. smartphone, laptop, zap, headphones'}),
            'display_order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'image_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded border-slate-300'}),
        }


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'tracking_number', 'staff_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-semibold'}),
            'payment_status': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-semibold'}),
            'tracking_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Airway Bill or Local Courier Tracking Code'}),
            'staff_notes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 3, 'placeholder': 'Internal notes (China supplier contact, flight number, Kigali pickup dispatch)'}),
        }


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'company_name', 'slogan', 'primary_phone', 'whatsapp_number',
            'email_contact', 'physical_address', 'announcement_banner', 'show_announcement',
            'standard_kigali_shipping_rwf', 'upcountry_shipping_rwf',
            'about_company', 'shipping_guide', 'return_policy', 'privacy_policy', 'terms_conditions'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'slogan': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'primary_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': '250788123456'}),
            'email_contact': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'physical_address': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'announcement_banner': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'show_announcement': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded border-slate-300'}),
            'standard_kigali_shipping_rwf': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'upcountry_shipping_rwf': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'about_company': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 4}),
            'shipping_guide': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 4}),
            'return_policy': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 3}),
            'privacy_policy': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 3}),
            'terms_conditions': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 3}),
        }


class StaffRoleUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded border-slate-300'}),
        }
