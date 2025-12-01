# ultra_hesap_makinesi.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import math
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import requests
from pint import UnitRegistry
from datetime import datetime, timedelta


ureg = UnitRegistry()
Q_ = ureg.Quantity


x = sp.symbols('x')


root = tk.Tk()
root.title("TAM ÖZELLİKLİ HESAP MAKİNESİ (CAS + Grafik + Birimler + Döviz + Daha Fazlası)")
root.geometry("980x720")
root.minsize(900, 600)

tema_acik = {
    "bg": "#f5f5f5",
    "fg": "#111111",
    "button": "#e0e0e0",
    "screen": "#ffffff"
}
tema_koyu = {
    "bg": "#111318",
    "fg": "#e7eef6",
    "button": "#1f2428",
    "screen": "#202427"
}
aktif_tema = tema_acik

def uygula_tema():
    root.config(bg=aktif_tema["bg"])
    style.configure("TFrame", background=aktif_tema["bg"])
    style.configure("TLabel", background=aktif_tema["bg"], foreground=aktif_tema["fg"])
    style.configure("TButton", background=aktif_tema["button"], foreground=aktif_tema["fg"])

    for e in root.winfo_children():
        pass

def degistir_tema():
    global aktif_tema
    aktif_tema = tema_koyu if aktif_tema == tema_acik else tema_acik
    uygula_tema()

    for widget in root.winfo_children():
        widget.configure(bg=aktif_tema["bg"]) if isinstance(widget, tk.Frame) else None


style = ttk.Style()
style.theme_use('clam')
uygula_tema()


notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=8, pady=8)


frame_hesap = ttk.Frame(notebook)
frame_cas = ttk.Frame(notebook)
frame_grafik = ttk.Frame(notebook)
frame_birim = ttk.Frame(notebook)
frame_doviz = ttk.Frame(notebook)
frame_arac = ttk.Frame(notebook)

notebook.add(frame_hesap, text="Hesap Makinesi")
notebook.add(frame_cas, text="Bilimsel / CAS")
notebook.add(frame_grafik, text="Grafik Çiz")
notebook.add(frame_birim, text="Birim Dönüştürücü")
notebook.add(frame_doviz, text="Döviz (Canlı)")
notebook.add(frame_arac, text="Araçlar & Dönüşümler")

history = []

def history_add(text):
    history.append(text)

    txt_gecmis.configure(state='normal')
    txt_gecmis.insert(tk.END, text + "\n")
    txt_gecmis.configure(state='disabled')


right_frame = ttk.Frame(root, width=260)
right_frame.place(relx=0.74, rely=0.03, relheight=0.94, relwidth=0.25)

lbl_gecmis = ttk.Label(right_frame, text="Geçmiş (History)")
lbl_gecmis.pack(anchor='nw', padx=6, pady=(6,0))

txt_gecmis = ScrolledText(right_frame, height=40, state='disabled', wrap='word')
txt_gecmis.pack(fill='both', expand=True, padx=6, pady=6)

def clear_history():
    global history
    history = []
    txt_gecmis.configure(state='normal')
    txt_gecmis.delete(1.0, tk.END)
    txt_gecmis.configure(state='disabled')

ttk.Button(right_frame, text="Geçmişi Temizle", command=clear_history).pack(padx=6, pady=(0,6))


ekran_var = tk.StringVar()
entry_hesap = ttk.Entry(frame_hesap, textvariable=ekran_var, font=("Arial", 20))
entry_hesap.pack(fill='x', padx=10, pady=10)

def calc_eval(expr):

    try:
        expr = expr.replace('^', '**')
        sympy_expr = sp.sympify(expr, evaluate=True)
        val = sympy_expr.evalf()
        return val
    except Exception as e:
        raise e

def btn_tikla_deger(d):
    cur = ekran_var.get()
    ekran_var.set(cur + d)

def hesapla_basit(event=None):
    expr = ekran_var.get().strip()
    if not expr:
        return
    try:
        sonuc = calc_eval(expr)
        ekran_var.set(str(sonuc))
        history_add(f"{expr} = {sonuc}")
    except Exception as e:
        messagebox.showerror("Hata", f"Hesaplama hatası:\n{e}")
        ekran_var.set("")

buttons = [
    ('7','8','9','/','sin('),
    ('4','5','6','*','cos('),
    ('1','2','3','-','tan('),
    ('0','.','^','+','sqrt('),
]
frame_btns = ttk.Frame(frame_hesap)
frame_btns.pack(padx=10, pady=6)
for r,row in enumerate(buttons):
    for c,lab in enumerate(row):
        ttk.Button(frame_btns, text=lab, width=7, command=lambda v=lab: btn_tikla_deger(v)).grid(row=r,column=c,padx=4,pady=4)

ttk.Button(frame_hesap, text='=', command=hesapla_basit).pack(fill='x', padx=10, pady=(8,4))
ttk.Button(frame_hesap, text='Temizle', command=lambda: ekran_var.set("")).pack(fill='x', padx=10, pady=(0,8))

entry_hesap.bind('<Return>', hesapla_basit)


lbl_cas = ttk.Label(frame_cas, text="SymPy ile Sembolik İşlemler (ör: sin(x)*x^2, integrate(...), diff(...))")
lbl_cas.pack(anchor='w', padx=10, pady=(10,4))

txt_cas_input = ScrolledText(frame_cas, height=6)
txt_cas_input.pack(fill='x', padx=10, pady=(0,6))

frame_cas_buttons = ttk.Frame(frame_cas)
frame_cas_buttons.pack(fill='x', padx=10, pady=6)

def cas_evaluate():
    expr_text = txt_cas_input.get("1.0", "end").strip()
    if not expr_text:
        return
    try:

        result = eval(expr_text, {"__builtins__": None}, {"sin":sp.sin,"cos":sp.cos,"tan":sp.tan,"sqrt":sp.sqrt,"log":sp.log,"exp":sp.exp,"pi":sp.pi,"E":sp.E,"x":x,"sp":sp,"integrate":sp.integrate,"diff":sp.diff,"simplify":sp.simplify,"factor":sp.factor,"solve":sp.solve,"limit":sp.limit})
        out = sp.pretty(result)
        txt_cas_output.configure(state='normal')
        txt_cas_output.delete(1.0, tk.END)
        txt_cas_output.insert(tk.END, out)
        txt_cas_output.configure(state='disabled')
        history_add(f"CAS: {expr_text} => {str(result)}")
    except Exception as e:
        messagebox.showerror("CAS Hatası", f"Hata:\n{e}")

ttk.Button(frame_cas_buttons, text="Çalıştır", command=cas_evaluate).pack(side='left', padx=6)
ttk.Button(frame_cas_buttons, text="Örnek: diff(sin(x)*x**2, x)", command=lambda: txt_cas_input.insert(tk.END, "diff(sin(x)*x**2, x)")).pack(side='left', padx=6)
ttk.Button(frame_cas_buttons, text="Örnek: integrate(x**2*sin(x),(x,0,pi))", command=lambda: txt_cas_input.insert(tk.END, "integrate(x**2*sin(x),(x,0,pi))")).pack(side='left', padx=6)

txt_cas_output = ScrolledText(frame_cas, height=10, state='disabled')
txt_cas_output.pack(fill='both', padx=10, pady=(6,10), expand=True)


lbl_graph_info = ttk.Label(frame_grafik, text="Fonksiyon grafiği: x değişkenini kullan (ör: sin(x)/x, x**2+3)")
lbl_graph_info.pack(anchor='w', padx=10, pady=(10,4))
entry_graph = ttk.Entry(frame_grafik, font=("Arial", 14))
entry_graph.pack(fill='x', padx=10, pady=6)

frame_graph_ctrl = ttk.Frame(frame_grafik)
frame_graph_ctrl.pack(fill='x', padx=10, pady=6)

ttk.Label(frame_graph_ctrl, text="xmin:").pack(side='left')
xmin_e = ttk.Entry(frame_graph_ctrl, width=8); xmin_e.pack(side='left', padx=4)
xmin_e.insert(0, "-10")
ttk.Label(frame_graph_ctrl, text="xmax:").pack(side='left')
xmax_e = ttk.Entry(frame_graph_ctrl, width=8); xmax_e.pack(side='left', padx=4)
xmax_e.insert(0, "10")

def grafik_cizim():
    expr = entry_graph.get().strip()
    if not expr:
        messagebox.showinfo("Bilgi", "Lütfen bir fonksiyon gir.")
        return
    try:
        expr = expr.replace('^','**')
        xmin = float(xmin_e.get()); xmax = float(xmax_e.get())
        xs = np.linspace(xmin, xmax, 800)
        # sympy lambdify
        f = sp.lambdify(x, sp.sympify(expr), modules=["numpy", {"sin": np.sin, "cos": np.cos, "tan": np.tan, "sqrt": np.sqrt, "log": np.log, "exp": np.exp}])
        ys = f(xs)
        plt.figure(figsize=(6,4))
        plt.plot(xs, ys)
        plt.title(f"y = {expr}")
        plt.axhline(0, color='gray', linewidth=0.6)
        plt.axvline(0, color='gray', linewidth=0.6)
        plt.grid(True)
        plt.show()
        history_add(f"Grafik: y={expr} [{xmin},{xmax}]")
    except Exception as e:
        messagebox.showerror("Grafik Hatası", f"Hata:\n{e}")

ttk.Button(frame_graph_ctrl, text="Grafiği Çiz", command=grafik_cizim).pack(side='left', padx=6)


lbl_unit = ttk.Label(frame_birim, text="Birim Dönüştürücü (ör: 10 meter to cm)")
lbl_unit.pack(anchor='w', padx=10, pady=(10,4))
frame_unit = ttk.Frame(frame_birim)
frame_unit.pack(fill='x', padx=10, pady=6)

lbl_from = ttk.Label(frame_unit, text="Miktar ve birim:")
lbl_from.pack(anchor='w')
entry_unit = ttk.Entry(frame_unit)
entry_unit.pack(fill='x', pady=(0,6))

def unit_convert():
    q = entry_unit.get().strip()
    if not q:
        return

    try:
        if ' to ' in q:
            left, right = q.split(' to ')
            qty = ureg(left)
            res = qty.to(right)
        else:
            messagebox.showinfo("Bilgi", "Kullanım örneği: '10 meter to cm' veya '5 kg to g'")
            return
        messagebox.showinfo("Sonuç", f"{res}")
        history_add(f"Birim: {q} => {res}")
    except Exception as e:
        messagebox.showerror("Birim Hatası", f"Hata:\n{e}")

ttk.Button(frame_unit, text="Dönüştür", command=unit_convert).pack(padx=6, pady=6)


frame_unit_examples = ttk.Frame(frame_birim)
frame_unit_examples.pack(fill='x', padx=10, pady=(0,10))
ttk.Button(frame_unit_examples, text="10 m -> cm", command=lambda: entry_unit.insert(0, "10 meter to cm")).pack(side='left', padx=4)
ttk.Button(frame_unit_examples, text="2 hour -> second", command=lambda: entry_unit.insert(0, "2 hour to second")).pack(side='left', padx=4)
ttk.Button(frame_unit_examples, text="5 GB -> MB", command=lambda: entry_unit.insert(0, "5 gigabyte to megabyte")).pack(side='left', padx=4)


lbl_fx = ttk.Label(frame_doviz, text="Döviz çevirici (canlı oran: exchangerate.host kullanılır)")
lbl_fx.pack(anchor='w', padx=10, pady=(10,4))
frame_fx = ttk.Frame(frame_doviz)
frame_fx.pack(fill='x', padx=10, pady=6)

entry_amount = ttk.Entry(frame_fx, width=12)
entry_amount.pack(side='left', padx=4)
entry_amount.insert(0,"1")

entry_from = ttk.Entry(frame_fx, width=8)
entry_from.pack(side='left', padx=4)
entry_from.insert(0,"USD")

entry_to = ttk.Entry(frame_fx, width=8)
entry_to.pack(side='left', padx=4)
entry_to.insert(0,"EUR")

lbl_fx_note = ttk.Label(frame_doviz, text="(Kullanım: miktar, kaynak para kodu (USD), hedef para kodu (EUR))")
lbl_fx_note.pack(anchor='w', padx=10, pady=(2,6))

lbl_fx_result = ttk.Label(frame_doviz, text="Sonuç: -")
lbl_fx_result.pack(anchor='w', padx=10, pady=(0,6))

def fetch_rate_and_convert(amount, frm, to):

    try:
        url = f"https://api.exchangerate.host/convert?from={frm}&to={to}&amount={amount}"
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data.get("success", True) is False:
            raise Exception("API hatası")
        result = data.get("result", None)
        info = f"{amount} {frm} = {result} {to}"
        lbl_fx_result.config(text="Sonuç: " + str(info))
        history_add(f"Döviz: {info}")
    except Exception as e:
        messagebox.showerror("Döviz Hatası", f"Döviz çekilemedi:\n{e}")

def btn_doviz():
    amt = entry_amount.get().strip()
    frm = entry_from.get().strip().upper()
    to = entry_to.get().strip().upper()
    try:
        amt_f = float(amt)
    except:
        messagebox.showerror("Hata", "Miktarı sayısal girin.")
        return
    fetch_rate_and_convert(amt_f, frm, to)

ttk.Button(frame_fx, text="Çevir", command=btn_doviz).pack(side='left', padx=6)

lbl_tools = ttk.Label(frame_arac, text="Araçlar: Veri / Zaman / Para / Birimler - hızlı dönüşümler")
lbl_tools.pack(anchor='w', padx=10, pady=(10,4))

frame_tools_inner = ttk.Frame(frame_arac)
frame_tools_inner.pack(fill='both', expand=True, padx=10, pady=6)


def bytes_convert():
    s = simpledialog.askstring("Veri Dönüştür", "Örnek: '1024 B to KB' veya '5 GB to MB'")
    if not s:
        return
    try:
        if ' to ' not in s:
            messagebox.showinfo("Bilgi", "Örnek format: '1024 B to KB'")
            return
        left,right = s.split(' to ')
        qty = ureg(left)
        res = qty.to(right)
        messagebox.showinfo("Sonuç", f"{res}")
        history_add(f"Veri: {s} => {res}")
    except Exception as e:
        messagebox.showerror("Hata", f"{e}")

ttk.Button(frame_tools_inner, text="Veri (Bytes) Dönüştür", command=bytes_convert).pack(fill='x', pady=4)


def zaman_farki():
    s1 = simpledialog.askstring("Tarih", "Başlangıç tarih (YYYY-MM-DD HH:MM) örn: 2025-01-01 08:30")
    s2 = simpledialog.askstring("Tarih", "Bitiş tarih (YYYY-MM-DD HH:MM)")
    if not s1 or not s2:
        return
    try:
        t1 = datetime.strptime(s1, "%Y-%m-%d %H:%M")
        t2 = datetime.strptime(s2, "%Y-%m-%d %H:%M")
        diff = t2 - t1
        messagebox.showinfo("Zaman Farkı", f"Fark: {diff} (gün,saat:dakika:sn)")
        history_add(f"Zaman farkı: {s1} -> {s2} = {diff}")
    except Exception as e:
        messagebox.showerror("Hata", f"{e}")

ttk.Button(frame_tools_inner, text="Zaman Farkı Hesapla", command=zaman_farki).pack(fill='x', pady=4)


def faiz_hesapla():
    try:
        p = float(simpledialog.askstring("Anaparayı girin", "Anapara (P):"))
        r = float(simpledialog.askstring("Yıllık oran (%)", "Yıllık faiz oranı (yüzde):"))
        t = float(simpledialog.askstring("Yıl", "Yıl sayısı:"))
        n = int(simpledialog.askstring("Dönem/yıl", "Dönem sayısı / yıl (bileşik için):"))
    except Exception:
        messagebox.showerror("Hata", "Geçersiz giriş.")
        return
    simple = p * (1 + r/100 * t)
    compound = p * (1 + r/100 / n)**(n*t)
    messagebox.showinfo("Faiz Sonuçları", f"Basit: {simple}\nBileşik: {compound}")
    history_add(f"Faiz: P={p}, r={r}%, t={t}, n={n} -> simple={simple}, compound={compound}")

ttk.Button(frame_tools_inner, text="Faiz Hesapla (Basit/Bileşik)", command=faiz_hesapla).pack(fill='x', pady=4)

def diff_prompt():
    expr = simpledialog.askstring("Türev", "İfade (x kullanın): örn: sin(x)*x**2")
    if not expr:
        return
    try:
        res = sp.diff(sp.sympify(expr), x)
        messagebox.showinfo("Türev", f"d/dx {expr} = {sp.pretty(res)}")
        history_add(f"diff({expr}) = {res}")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def integral_prompt():
    expr = simpledialog.askstring("İntegral", "İfade (x kullanın), örn: x**2*sin(x) veya definite: integrate(x**2,(x,0,1))")
    if not expr:
        return
    try:

        if expr.strip().startswith("integrate"):
            res = eval(expr, {"__builtins__": None}, {"integrate":sp.integrate,"x":x,"sin":sp.sin,"cos":sp.cos,"tan":sp.tan,"sqrt":sp.sqrt,"log":sp.log,"exp":sp.exp})
        else:
            res = sp.integrate(sp.sympify(expr), x)
        messagebox.showinfo("İntegral", f"İntegral sonucu:\n{sp.pretty(res)}")
        history_add(f"integrate({expr}) = {res}")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

ttk.Button(frame_tools_inner, text="Türev Al (Hızlı)", command=diff_prompt).pack(fill='x', pady=4)
ttk.Button(frame_tools_inner, text="İntegral Al (Hızlı)", command=integral_prompt).pack(fill='x', pady=4)


def on_key(event):

    if event.keysym == 'Return':
        hesapla_basit()
    elif event.keysym == 'Escape':
        ekran_var.set('')
    elif event.state & 0x4 and event.keysym.lower() == 'l':  # ctrl+l
        ekran_var.set('')
    elif event.state & 0x4 and event.keysym.lower() == 't':  # ctrl+t tema
        degistir_tema()

root.bind_all("<Key>", on_key)


history_add("Uygulama başlatıldı.")
uygula_tema()

bottom_frame = ttk.Frame(root)
bottom_frame.place(relx=0.02, rely=0.96, relwidth=0.7, relheight=0.03)
ttk.Button(bottom_frame, text="Tema Değiştir (Ctrl+T)", command=degistir_tema).pack(side='left', padx=6)
ttk.Label(bottom_frame, text="Klavye: Enter=Hesapla, Esc=Temizle, Ctrl+L=Temizle").pack(side='left', padx=6)

root.mainloop()
