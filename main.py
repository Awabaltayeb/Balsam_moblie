from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, ThreeLineListItem, TwoLineListItem
from kivy.uix.scrollview import ScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock

# --- دعم اللغة العربية ---
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.core.text import LabelBase

LabelBase.register(name='Roboto', fn_regular='arial.ttf', fn_bold='arial.ttf')
LabelBase.register(name='Roboto-Medium', fn_regular='arial.ttf')
LabelBase.register(name='Roboto-Light', fn_regular='arial.ttf')
LabelBase.register(name='Roboto-Bold', fn_regular='arial.ttf')

# حجم شاشة الموبايل للبروفة (امسح هذا السطر عند استخراج ה-APK)
Window.size = (360, 640)

# استدعاء الخلفية (Backend)
import auth
import analytics
import alerts
import database
import drug_management as dm
import sales_management as sm
import reports
import settings

def ar(text):
    """دالة لضبط الحروف العربية"""
    if text is None: return ""
    return get_display(arabic_reshaper.reshape(str(text)))

# ==========================================
# 1. شاشة تسجيل الدخول
# ==========================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # مسافة علوية
        layout.add_widget(MDLabel(size_hint_y=0.2))
        
        title = MDLabel(text=ar("نظام بلسم - نسخة الجوال"), halign="center", font_style="H5", theme_text_color="Primary")
        layout.add_widget(title)
        
        self.username = MDTextField(hint_text=ar("اسم المستخدم"), icon_right="account", pos_hint={"center_x": .5})
        self.password = MDTextField(hint_text=ar("كلمة المرور"), password=True, icon_right="key", pos_hint={"center_x": .5})
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        
        btn_login = MDRaisedButton(text=ar("تسجيل الدخول"), pos_hint={"center_x": .5}, size_hint_x=1, on_release=self.login)
        layout.add_widget(btn_login)
        
        self.error_label = MDLabel(text="", halign="center", theme_text_color="Error")
        layout.add_widget(self.error_label)
        
        layout.add_widget(MDLabel(size_hint_y=0.3))
        self.add_widget(layout)

    def login(self, instance):
        user, pwd = self.username.text, self.password.text
        uid, role = auth.login_user(user, pwd) or (None, None)
        if uid:
            app = MDApp.get_running_app()
            app.current_user_id = uid
            app.current_username = user
            app.current_role = role
            
            # توجيه حسب الصلاحية
            if role == 'admin':
                self.manager.current = 'dashboard'
            else:
                self.manager.current = 'pos'
            
            self.username.text = ""
            self.password.text = ""
            self.error_label.text = ""
        else:
            self.error_label.text = ar("بيانات خطأ أو غير مصرح لك")

# ==========================================
# الشاشة الأساسية (تحتوي على القائمة الجانبية والشاشات)
# ==========================================
class MainNavigationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. الحاوية الرئيسية للشاشة (عمودية)
        root_layout = MDBoxLayout(orientation='vertical')
        
        # 2. الشريط العلوي (نضعه أولاً في الحاوية الرئيسية)
        self.toolbar = MDTopAppBar(title=ar("لوحة القيادة"), elevation=4, left_action_items=[["menu", lambda x: self.nav_drawer.set_state("open")]])
        root_layout.add_widget(self.toolbar)
        
        # 3. حاوية القائمة الجانبية (صارمة: تقبل فقط ScreenManager و Drawer)
        self.nav_layout = MDNavigationLayout()
        
        # 4. مدير الشاشات (الشاشات التي تتغير في المنتصف)
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(DashboardUI(name='dashboard'))
        self.screen_manager.add_widget(POSUI(name='pos'))
        self.screen_manager.add_widget(InventoryUI(name='inventory'))
        self.screen_manager.add_widget(ReportsUI(name='reports'))
        self.screen_manager.add_widget(AlertsUI(name='alerts'))
        self.screen_manager.add_widget(SettingsUI(name='settings'))
        
        self.nav_layout.add_widget(self.screen_manager) # تمت الإضافة هنا مباشرة لحل الخطأ
        
        # 5. القائمة الجانبية المنسدلة
        self.nav_drawer = MDNavigationDrawer()
        nav_box = MDBoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        
        self.welcome_label = MDLabel(text=ar("مرحباً"), font_style="H6", size_hint_y=None, height=dp(50), theme_text_color="Primary")
        nav_box.add_widget(self.welcome_label)
        
        scroll_nav = ScrollView()
        list_nav = MDList()
        
        menus =[
            ("لوحة القيادة", "view-dashboard", 'dashboard'),
            ("نقطة البيع (POS)", "cart", 'pos'),
            ("إدارة المخزون", "pill", 'inventory'),
            ("التقارير المالية", "chart-bar", 'reports'),
            ("التنبيهات والنواقص", "alert", 'alerts'),
            ("الإعدادات", "cog", 'settings')
        ]
        
        for text, icon, screen_name in menus:
            item = TwoLineListItem(text=ar(text), secondary_text="", on_release=lambda x, sn=screen_name, t=text: self.switch_screen(sn, t))
            list_nav.add_widget(item)
            
        btn_logout = MDRaisedButton(text=ar("تسجيل خروج"), md_bg_color=(0.8, 0, 0, 1), size_hint_x=1, on_release=self.logout)
        
        scroll_nav.add_widget(list_nav)
        nav_box.add_widget(scroll_nav)
        nav_box.add_widget(btn_logout)
        self.nav_drawer.add_widget(nav_box)
        
        self.nav_layout.add_widget(self.nav_drawer) # تمت الإضافة هنا مباشرة لحل الخطأ
        
        # 6. إضافة حاوية القائمة تحت الشريط العلوي
        root_layout.add_widget(self.nav_layout)
        
        self.add_widget(root_layout)

    def on_enter(self):
        app = MDApp.get_running_app()
        self.welcome_label.text = ar(f"مرحباً، {app.current_username}")
        current_scr = self.screen_manager.current_screen
        if hasattr(current_scr, 'load_data'):
            current_scr.load_data()

    def switch_screen(self, screen_name, title):
        self.toolbar.title = ar(title)
        self.screen_manager.current = screen_name
        self.nav_drawer.set_state("close")
        if hasattr(self.screen_manager.current_screen, 'load_data'):
            self.screen_manager.current_screen.load_data()

    def logout(self, instance):
        self.nav_drawer.set_state("close")
        MDApp.get_running_app().root.current = 'login'

# ==========================================
# واجهة لوحة القيادة (Dashboard)
# ==========================================
class DashboardUI(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        self.layout = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10), size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        scroll.add_widget(self.layout)
        self.add_widget(scroll)

    def load_data(self):
        self.layout.clear_widgets()
        fin = analytics.get_financial_summary()
        
        self.layout.add_widget(MDLabel(text=ar("الملخص المالي"), theme_text_color="Primary", font_style="H6", size_hint_y=None, height=dp(30)))
        self.add_card(ar("مبيعات اليوم"), f"{fin['sales_today']} SDG", (0.1, 0.7, 0.3, 1))
        self.add_card(ar("أرباح اليوم"), f"{fin['profit_today']} SDG", (0.1, 0.4, 0.8, 1))
        self.add_card(ar("أرباح الشهر"), f"{fin['profit_month']} SDG", (0.5, 0.1, 0.5, 1))
        self.add_card(ar("عدد الفواتير"), f"{fin['invoices_today']}", (0.1, 0.6, 0.6, 1))
        
        self.layout.add_widget(MDLabel(text=ar("الأدوية الراكدة (تنبيه)"), theme_text_color="Error", font_style="H6", size_hint_y=None, height=dp(30)))
        stagnant = analytics.get_stagnant_drugs()
        if not stagnant:
            self.layout.add_widget(MDLabel(text=ar("لا توجد أدوية راكدة"), size_hint_y=None, height=dp(30)))
        else:
            for d in stagnant:
                self.layout.add_widget(MDLabel(text=ar(f"• {d['name']} (الكمية: {d['quantity']})"), size_hint_y=None, height=dp(20)))

    def add_card(self, title, value, color):
        card = MDCard(orientation='vertical', padding=dp(15), size_hint=(1, None), height=dp(90), md_bg_color=color)
        card.add_widget(MDLabel(text=title, theme_text_color="Custom", text_color=(1,1,1,1), font_style="Subtitle1"))
        card.add_widget(MDLabel(text=value, theme_text_color="Custom", text_color=(1,1,1,1), font_style="H5"))
        self.layout.add_widget(card)

# ==========================================
# واجهة نقطة البيع (POS)
# ==========================================
class POSUI(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.all_drugs =[]
        self.payment_dialog = None
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        
        # حقل البحث والكمية
        search_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(5))
        self.search_field = MDTextField(hint_text=ar("بحث (اسم/باركود)"), size_hint_x=0.7)
        self.qty_field = MDTextField(hint_text=ar("الكمية"), text="1", size_hint_x=0.15)
        btn_add = MDIconButton(icon="cart-plus", on_release=self.add_item)
        
        search_box.add_widget(self.search_field)
        search_box.add_widget(self.qty_field)
        search_box.add_widget(btn_add)
        layout.add_widget(search_box)

        # قائمة السلة
        scroll = ScrollView()
        self.cart_list = MDList()
        scroll.add_widget(self.cart_list)
        layout.add_widget(scroll)

        # الإجمالي والدفع
        bot_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), md_bg_color=(0.9,0.9,0.9,1), padding=dp(10))
        self.total_lbl = MDLabel(text=ar("الإجمالي: 0 SDG"), theme_text_color="Error", font_style="H6")
        btn_pay = MDRaisedButton(text=ar("إتمام البيع"), on_release=self.show_payment_dialog)
        
        bot_box.add_widget(self.total_lbl)
        bot_box.add_widget(btn_pay)
        layout.add_widget(bot_box)
        
        self.add_widget(layout)

    def load_data(self):
        self.all_drugs = dm.get_all_active_drugs()

    def add_item(self, inst):
        term = self.search_field.text.strip().lower()
        if not term: return
        qty = int(self.qty_field.text) if self.qty_field.text.isdigit() else 1
        
        found = next((d for d in self.all_drugs if term in str(d['barcode']).lower() or term in d['name'].lower()), None)
        if found:
            if found['quantity'] < qty:
                self.search_field.text = ar("الكمية لا تكفي!")
                return
            item_total = found['price'] * qty
            self.cart.append({'drug_id': found['drug_id'], 'name': found['name'], 'price': found['price'], 'qty': qty, 'total': item_total})
            self.refresh_cart()
            self.search_field.text = ""
        else:
            self.search_field.text = ar("غير موجود!")

    def refresh_cart(self):
        self.cart_list.clear_widgets()
        total = 0
        for item in self.cart:
            li = ThreeLineListItem(text=ar(item['name']), secondary_text=ar(f"الكمية: {item['qty']} | السعر: {item['price']} SDG"), tertiary_text=ar(f"المجموع: {item['total']} SDG"))
            self.cart_list.add_widget(li)
            total += item['total']
        self.total_lbl.text = ar(f"الإجمالي: {total} SDG")

    def show_payment_dialog(self, inst):
        if not self.cart: return
        if not self.payment_dialog:
            self.payment_dialog = MDDialog(
                title=ar("اختر طريقة الدفع"),
                type="custom",
                buttons=[
                    MDRaisedButton(text=ar("كاش (Cash)"), on_release=lambda x: self.process_payment("Cash")),
                    MDRaisedButton(text=ar("بنكك (Bankak)"), md_bg_color=(0.8,0.2,0.2,1), on_release=lambda x: self.process_payment("Bankak")),
                    MDFlatButton(text=ar("إلغاء"), on_release=lambda x: self.payment_dialog.dismiss())
                ],
            )
        self.payment_dialog.open()

    def process_payment(self, method):
        self.payment_dialog.dismiss()
        uid = MDApp.get_running_app().current_user_id
        msg, inv = sm.process_cart_sale(uid, self.cart, method)
        if msg == "Success":
            self.cart =[]
            self.refresh_cart()
            self.search_field.text = ar(f"تم البيع! رقم: {inv}")
            self.load_data() # تحديث المخزون

# ==========================================
# واجهة إدارة المخزون (Inventory)
# ==========================================
class InventoryUI(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        scroll = ScrollView()
        self.drug_list = MDList()
        scroll.add_widget(self.drug_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def load_data(self):
        self.drug_list.clear_widgets()
        drugs = dm.get_all_active_drugs()
        for d in drugs:
            item = ThreeLineListItem(
                text=ar(d['name']),
                secondary_text=ar(f"الكمية: {d['quantity']} | سعر البيع: {d['price']} SDG"),
                tertiary_text=ar(f"الباركود: {d['barcode']} | التكلفة: {d['cost_price']} SDG")
            )
            self.drug_list.add_widget(item)

# ==========================================
# واجهة التقارير المالية (Reports)
# ==========================================
class ReportsUI(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        scroll = ScrollView()
        self.rep_list = MDList()
        scroll.add_widget(self.rep_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def load_data(self):
        self.rep_list.clear_widgets()
        reps = reports.get_sales_report_data()
        for r in reps:
            item = ThreeLineListItem(
                text=ar(f"{r['name']} ({r['quantity_sold']}) - {r['total_amount']} SDG"),
                secondary_text=ar(f"الدفع: {r['payment_method']} | البائع: {r['username']}"),
                tertiary_text=ar(f"التاريخ: {r['sale_date']}")
            )
            self.rep_list.add_widget(item)

# ==========================================
# واجهة التنبيهات (Alerts)
# ==========================================
class AlertsUI(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        scroll = ScrollView()
        self.alert_list = MDList()
        scroll.add_widget(self.alert_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def load_data(self):
        self.alert_list.clear_widgets()
        low = alerts.get_low_stock_drugs()
        exp = alerts.get_expiring_drugs()

        if low:
            self.alert_list.add_widget(MDLabel(text=ar("⚠️ نواقص المخزون"), theme_text_color="Error", padding=(dp(10), dp(10)), size_hint_y=None, height=dp(40)))
            for d in low:
                self.alert_list.add_widget(TwoLineListItem(text=ar(d['name']), secondary_text=ar(f"الكمية المتبقية: {d['quantity']}")))

        if exp:
            self.alert_list.add_widget(MDLabel(text=ar("📅 قريبة الإنتهاء"), theme_text_color="Error", padding=(dp(10), dp(10)), size_hint_y=None, height=dp(40)))
            for d in exp:
                self.alert_list.add_widget(TwoLineListItem(text=ar(d['name']), secondary_text=ar(f"تاريخ الانتهاء: {d['expiry_date']}")))

# ==========================================
# واجهة الإعدادات (Settings)
# ==========================================
class SettingsUI(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        self.bkp_field = MDTextField(hint_text=ar("أيام النسخ الاحتياطي"))
        self.low_field = MDTextField(hint_text=ar("حد تنبيه المخزون"))
        self.exp_field = MDTextField(hint_text=ar("أيام تنبيه الصلاحية"))
        
        btn_save = MDRaisedButton(text=ar("حفظ الإعدادات"), on_release=self.save_settings)
        
        layout.add_widget(self.bkp_field)
        layout.add_widget(self.low_field)
        layout.add_widget(self.exp_field)
        layout.add_widget(btn_save)
        layout.add_widget(MDLabel(text=ar("(إدارة المستخدمين تتم عبر تطبيق الكمبيوتر لضمان الأمان)"), theme_text_color="Secondary"))
        layout.add_widget(MDLabel(size_hint_y=1))
        
        self.add_widget(layout)

    def load_data(self):
        self.bkp_field.text = str(settings.get_setting('backup_days') or 7)
        self.low_field.text = str(settings.get_setting('low_stock') or 10)
        self.exp_field.text = str(settings.get_setting('expiry_days') or 30)

    def save_settings(self, inst):
        try:
            settings.update_setting('backup_days', int(self.bkp_field.text))
            settings.update_setting('low_stock', int(self.low_field.text))
            settings.update_setting('expiry_days', int(self.exp_field.text))
            self.bkp_field.text = ar("تم الحفظ بنجاح!")
        except Exception:
            pass

# ==========================================
# التطبيق الرئيسي
# ==========================================
class BalsamMobileApp(MDApp):
    current_user_id = None
    current_username = None
    current_role = None

    def build(self):
        self.theme_cls.primary_palette = "Teal" 
        self.theme_cls.theme_style = "Light"
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        # نضيف الشاشة الأساسية التي بداخلها القائمة الجانبية
        sm.add_widget(MainNavigationScreen(name='dashboard')) 
        sm.add_widget(MainNavigationScreen(name='pos')) # نستخدم نفس الحاوية
        
        return sm

if __name__ == "__main__":
    database.initialize_database()
    auth.seed_admin()
    BalsamMobileApp().run()