import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys

class ColorConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Конвертер цветовых моделей")
        self.root.geometry("1100x850")
        self.root.minsize(900, 700)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.source_model = 'rgb'
        self.rgb = [128, 128, 128]
        self.cmyk = [0, 0, 0, 50]
        self.hsv = [0, 0, 50]
        self.hls = [0, 50, 0]
        self.xyz = [20.517, 21.586, 23.507]
        self.lab = [53.585, 0.003, -0.006]
        
        self.colors = {
            'bg': '#f0f0f0',
            'card': '#ffffff',
            'primary': '#4a6ee0',
            'secondary': '#6a11cb',
            'text': '#333333'
        }
        
        self.setup_styles()
        self.create_widgets()
        self.update_all_displays()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Card.TFrame', background=self.colors['card'], relief='raised', borderwidth=1)
        style.configure('Card.TLabel', background=self.colors['card'], font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground=self.colors['primary'])
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
    
    def rgb_to_cmyk(self, rgb):
        r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
        k = 1 - max(r, g, b)
        if k == 1:
            return [0.0, 0.0, 0.0, 100.0]
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)
        return [c*100, m*100, y*100, k*100]
    
    def cmyk_to_rgb(self, cmyk):
        c, m, y, k = cmyk[0]/100.0, cmyk[1]/100.0, cmyk[2]/100.0, cmyk[3]/100.0
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        return [int(max(0, min(255, r))), 
                int(max(0, min(255, g))), 
                int(max(0, min(255, b)))]
    
    def rgb_to_hsv(self, rgb):
        r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return [h * 360, s * 100, v * 100]
    
    def hsv_to_rgb(self, hsv):
        h, s, v = hsv[0]/360.0, hsv[1]/100.0, hsv[2]/100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def rgb_to_hls(self, rgb):
        r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return [h * 360, l * 100, s * 100]
    
    def hls_to_rgb(self, hls):
        h, l, s = hls[0]/360.0, hls[1]/100.0, hls[2]/100.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def rgb_to_xyz(self, rgb):
        r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
        
        r = r/12.92 if r <= 0.04045 else ((r + 0.055)/1.055) ** 2.4
        g = g/12.92 if g <= 0.04045 else ((g + 0.055)/1.055) ** 2.4
        b = b/12.92 if b <= 0.04045 else ((b + 0.055)/1.055) ** 2.4
        
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        return [x * 100, y * 100, z * 100]
    
    def xyz_to_rgb(self, xyz):
        x, y, z = xyz[0]/100.0, xyz[1]/100.0, xyz[2]/100.0
        
        r_linear = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
        g_linear = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
        b_linear = x * 0.0556434 + y * -0.2040259 + z * 1.0572252
        
        r = 12.92 * r_linear if r_linear <= 0.0031308 else 1.055 * (r_linear ** (1/2.4)) - 0.055
        g = 12.92 * g_linear if g_linear <= 0.0031308 else 1.055 * (g_linear ** (1/2.4)) - 0.055
        b = 12.92 * b_linear if b_linear <= 0.0031308 else 1.055 * (b_linear ** (1/2.4)) - 0.055
        
        return [int(max(0, min(255, r * 255))), 
                int(max(0, min(255, g * 255))), 
                int(max(0, min(255, b * 255)))]
    
    def xyz_to_lab(self, xyz):
        ref_x, ref_y, ref_z = 95.047, 100.000, 108.883
        x, y, z = xyz[0], xyz[1], xyz[2]
        
        x = x / ref_x
        y = y / ref_y
        z = z / ref_z
        
        x = x ** (1/3) if x > 0.008856 else (7.787 * x) + (16/116)
        y = y ** (1/3) if y > 0.008856 else (7.787 * y) + (16/116)
        z = z ** (1/3) if z > 0.008856 else (7.787 * z) + (16/116)
        
        l = max(0, min(100, (116 * y) - 16))
        a = max(-128, min(127, 500 * (x - y)))
        b = max(-128, min(127, 200 * (y - z)))
        
        return [l, a, b]
    
    def lab_to_xyz(self, lab):
        ref_x, ref_y, ref_z = 95.047, 100.000, 108.883
        l, a, b = lab[0], lab[1], lab[2]
        
        y = (l + 16) / 116
        x = a / 500 + y
        z = y - b / 200
        
        x3 = x ** 3
        y3 = y ** 3
        z3 = z ** 3
        
        x = x3 if x3 > 0.008856 else (x - 16/116) / 7.787
        y = y3 if y3 > 0.008856 else (y - 16/116) / 7.787
        z = z3 if z3 > 0.008856 else (z - 16/116) / 7.787
        
        return [x * ref_x, y * ref_y, z * ref_z]
    
    def rgb_to_lab(self, rgb):
        xyz = self.rgb_to_xyz(rgb)
        return self.xyz_to_lab(xyz)
    
    def lab_to_rgb(self, lab):
        xyz = self.lab_to_xyz(lab)
        return self.xyz_to_rgb(xyz)
    
    def create_widgets(self):
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self.create_top_panel(main_container)
        ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, pady=15)
        self.create_color_preview_panel(main_container)
        ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, pady=15)
        self.create_tabs(main_container)
        ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, pady=15)
        self.create_all_values_panel(main_container)
    
    def create_top_panel(self, parent):
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.color_btn = ttk.Button(top_frame, text="🎨 Выбрать цвет из палитры", 
                                   command=self.choose_color, style='Primary.TButton')
        self.color_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        hex_frame = ttk.Frame(top_frame)
        hex_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(hex_frame, text="HEX:").pack(side=tk.LEFT)
        self.hex_entry = ttk.Entry(hex_frame, width=10)
        self.hex_entry.pack(side=tk.LEFT, padx=5)
        self.hex_entry.bind('<Return>', self.update_from_hex)
        
        ttk.Label(top_frame, text="RGB:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.r_entry = ttk.Spinbox(top_frame, from_=0, to=255, width=5)
        self.r_entry.pack(side=tk.LEFT, padx=2)
        self.r_entry.bind('<Return>', lambda e: self.update_from_rgb_entries())
        
        self.g_entry = ttk.Spinbox(top_frame, from_=0, to=255, width=5)
        self.g_entry.pack(side=tk.LEFT, padx=2)
        self.g_entry.bind('<Return>', lambda e: self.update_from_rgb_entries())
        
        self.b_entry = ttk.Spinbox(top_frame, from_=0, to=255, width=5)
        self.b_entry.pack(side=tk.LEFT, padx=2)
        self.b_entry.bind('<Return>', lambda e: self.update_from_rgb_entries())
        
        ttk.Button(top_frame, text="Применить", 
                  command=self.update_from_rgb_entries).pack(side=tk.LEFT, padx=10)
    
    def create_color_preview_panel(self, parent):
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(preview_frame, text="Текущий цвет:", style='Header.TLabel').pack(anchor='w')
        self.color_preview = tk.Canvas(preview_frame, width=400, height=80, 
                                      highlightthickness=1, highlightbackground="#ccc")
        self.color_preview.pack(pady=5)
    
    def create_tabs(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        rgb_frame = ttk.Frame(notebook, padding="15")
        self.create_rgb_tab(rgb_frame)
        notebook.add(rgb_frame, text="RGB")
        
        cmyk_frame = ttk.Frame(notebook, padding="15")
        self.create_cmyk_tab(cmyk_frame)
        notebook.add(cmyk_frame, text="CMYK")
        
        hsv_frame = ttk.Frame(notebook, padding="15")
        self.create_hsv_tab(hsv_frame)
        notebook.add(hsv_frame, text="HSV")
        
        hls_frame = ttk.Frame(notebook, padding="15")
        self.create_hls_tab(hls_frame)
        notebook.add(hls_frame, text="HLS")
        
        xyz_frame = ttk.Frame(notebook, padding="15")
        self.create_xyz_tab(xyz_frame)
        notebook.add(xyz_frame, text="XYZ")
        
        lab_frame = ttk.Frame(notebook, padding="15")
        self.create_lab_tab(lab_frame)
        notebook.add(lab_frame, text="LAB")
    
    def create_rgb_tab(self, parent):
        for i, (color, label) in enumerate([("R", "Красный"), ("G", "Зеленый"), ("B", "Синий")]):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label} ({color}):", width=15).pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=0, to=255, orient=tk.HORIZONTAL,
                            length=300, resolution=1,
                            command=lambda val, c=i: self.update_from_slider('rgb', c, val))
            slider.pack(side=tk.LEFT, padx=10)
            setattr(self, f'{color.lower()}_slider', slider)
            
            entry = ttk.Entry(frame, width=6)
            entry.pack(side=tk.LEFT)
            entry.bind('<Return>', lambda e, c=color: self.update_from_entry('rgb', c))
            setattr(self, f'{color.lower()}_slider_entry', entry)
    
    def create_cmyk_tab(self, parent):
        for i, (color, label) in enumerate([("C", "Голубой"), ("M", "Пурпурный"), 
                                           ("Y", "Желтый"), ("K", "Черный")]):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label} ({color}):", width=15).pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL,
                            length=300, resolution=0.1,
                            command=lambda val, c=i: self.update_from_slider('cmyk', c, val))
            slider.pack(side=tk.LEFT, padx=10)
            setattr(self, f'cmyk_{color.lower()}_slider', slider)
            
            entry = ttk.Entry(frame, width=6)
            entry.pack(side=tk.LEFT)
            entry.bind('<Return>', lambda e, c=color: self.update_from_entry('cmyk', c))
            setattr(self, f'cmyk_{color.lower()}_entry', entry)
    
    def create_hsv_tab(self, parent):
        for i, (color, label, max_val) in enumerate([("H", "Тон", 360), ("S", "Насыщенность", 100), ("V", "Яркость", 100)]):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label} ({color}):", width=15).pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=0, to=max_val, orient=tk.HORIZONTAL,
                            length=300, resolution=0.1,
                            command=lambda val, c=i: self.update_from_slider('hsv', c, val))
            slider.pack(side=tk.LEFT, padx=10)
            setattr(self, f'hsv_{color.lower()}_slider', slider)
            
            entry = ttk.Entry(frame, width=6)
            entry.pack(side=tk.LEFT)
            entry.bind('<Return>', lambda e, c=color: self.update_from_entry('hsv', c))
            setattr(self, f'hsv_{color.lower()}_entry', entry)
    
    def create_hls_tab(self, parent):
        for i, (color, label, max_val) in enumerate([("H", "Тон", 360), ("L", "Светлота", 100), ("S", "Насыщенность", 100)]):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label} ({color}):", width=15).pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=0, to=max_val, orient=tk.HORIZONTAL,
                            length=300, resolution=0.1,
                            command=lambda val, c=i: self.update_from_slider('hls', c, val))
            slider.pack(side=tk.LEFT, padx=10)
            setattr(self, f'hls_{color.lower()}_slider', slider)
            
            entry = ttk.Entry(frame, width=6)
            entry.pack(side=tk.LEFT)
            entry.bind('<Return>', lambda e, c=color: self.update_from_entry('hls', c))
            setattr(self, f'hls_{color.lower()}_entry', entry)
    
    def create_xyz_tab(self, parent):
        for i, (color, label) in enumerate([("X", "X"), ("Y", "Y"), ("Z", "Z")]):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label}:", width=15).pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL,
                            length=300, resolution=0.1,
                            command=lambda val, c=i: self.update_from_slider('xyz', c, val))
            slider.pack(side=tk.LEFT, padx=10)
            setattr(self, f'xyz_{color.lower()}_slider', slider)
            
            entry = ttk.Entry(frame, width=10)
            entry.pack(side=tk.LEFT)
            entry.bind('<Return>', lambda e, c=color: self.update_from_entry('xyz', c))
            setattr(self, f'xyz_{color.lower()}_entry', entry)
    
    def create_lab_tab(self, parent):
        params = [("L", "L*", 0, 100), ("A", "a*", -128, 127), ("B", "b*", -128, 127)]
        
        for i, (color, label, min_val, max_val) in enumerate(params):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label}:", width=15).pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                            length=300, resolution=0.1,
                            command=lambda val, c=i: self.update_from_slider('lab', c, val))
            slider.pack(side=tk.LEFT, padx=10)
            setattr(self, f'lab_{color.lower()}_slider', slider)
            
            entry = ttk.Entry(frame, width=8)
            entry.pack(side=tk.LEFT)
            entry.bind('<Return>', lambda e, c=color: self.update_from_entry('lab', c))
            setattr(self, f'lab_{color.lower()}_entry', entry)
    
    def create_all_values_panel(self, parent):
        ttk.Label(parent, text="Значения во всех моделях:", style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        models = [
            ("RGB", ["R:", "G:", "B:"]),
            ("CMYK", ["C:", "M:", "Y:", "K:"]),
            ("HSV", ["H:", "S:", "V:"]),
            ("HLS", ["H:", "L:", "S:"]),
            ("XYZ", ["X:", "Y:", "Z:"]),
            ("LAB", ["L*:", "a*:", "b*:"])
        ]
        
        self.value_labels = {}
        
        for idx, (model_name, channels) in enumerate(models):
            row = idx // 3
            col = idx % 3
            
            card = ttk.Frame(grid_frame, style='Card.TFrame', padding="10")
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=model_name, style='Header.TLabel').pack(anchor='w', pady=(0, 10))
            
            labels = {}
            for channel in channels:
                frame = ttk.Frame(card)
                frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(frame, text=channel, width=4).pack(side=tk.LEFT)
                lbl = ttk.Label(frame, text="0.0", font=('Arial', 10, 'bold'))
                lbl.pack(side=tk.LEFT, padx=5)
                labels[channel] = lbl
            
            self.value_labels[model_name] = labels
        
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1)
        for i in range(2):
            grid_frame.rowconfigure(i, weight=1)
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Выберите цвет")
        if color[0]:
            rgb = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
    
    def update_from_hex(self, event=None):
        hex_str = self.hex_entry.get().strip().lstrip('#')
        try:
            if len(hex_str) == 6:
                rgb = [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]
                self.rgb = rgb
                self.cmyk = self.rgb_to_cmyk(rgb)
                self.hsv = self.rgb_to_hsv(rgb)
                self.hls = self.rgb_to_hls(rgb)
                self.xyz = self.rgb_to_xyz(rgb)
                self.lab = self.rgb_to_lab(rgb)
                self.update_all_displays()
        except:
            pass
    
    def update_from_rgb_entries(self, event=None):
        try:
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())
            rgb = [r, g, b]
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
        except:
            pass
    
    def update_from_slider(self, model, channel, value):
        value = float(value)
        
        if model == 'rgb':
            rgb = self.rgb.copy()
            rgb[channel] = int(value)
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
        
        elif model == 'cmyk':
            cmyk = self.cmyk.copy()
            cmyk[channel] = value
            rgb = self.cmyk_to_rgb(cmyk)
            self.rgb = rgb
            self.cmyk = cmyk
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
        
        elif model == 'hsv':
            hsv = self.hsv.copy()
            hsv[channel] = value
            rgb = self.hsv_to_rgb(hsv)
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = hsv
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
        
        elif model == 'hls':
            hls = self.hls.copy()
            hls[channel] = value
            rgb = self.hls_to_rgb(hls)
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = hls
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
        
        elif model == 'xyz':
            xyz = self.xyz.copy()
            xyz[channel] = value
            rgb = self.xyz_to_rgb(xyz)
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = xyz
            self.lab = self.rgb_to_lab(rgb)
            self.update_all_displays()
        
        elif model == 'lab':
            lab = self.lab.copy()
            lab[channel] = value
            rgb = self.lab_to_rgb(lab)
            self.rgb = rgb
            self.cmyk = self.rgb_to_cmyk(rgb)
            self.hsv = self.rgb_to_hsv(rgb)
            self.hls = self.rgb_to_hls(rgb)
            self.xyz = self.rgb_to_xyz(rgb)
            self.lab = lab
            self.update_all_displays()
    
    def update_from_entry(self, model, channel):
        try:
            if model == 'rgb':
                entry = getattr(self, f'{channel.lower()}_slider_entry')
                value = float(entry.get())
                self.update_from_slider(model, {'R':0, 'G':1, 'B':2}[channel], value)
            
            elif model == 'cmyk':
                entry = getattr(self, f'cmyk_{channel.lower()}_entry')
                value = float(entry.get())
                self.update_from_slider(model, {'C':0, 'M':1, 'Y':2, 'K':3}[channel], value)
            
            elif model == 'hsv':
                entry = getattr(self, f'hsv_{channel.lower()}_entry')
                value = float(entry.get())
                self.update_from_slider(model, {'H':0, 'S':1, 'V':2}[channel], value)
            
            elif model == 'hls':
                entry = getattr(self, f'hls_{channel.lower()}_entry')
                value = float(entry.get())
                self.update_from_slider(model, {'H':0, 'L':1, 'S':2}[channel], value)
            
            elif model == 'xyz':
                entry = getattr(self, f'xyz_{channel.lower()}_entry')
                value = float(entry.get())
                self.update_from_slider(model, {'X':0, 'Y':1, 'Z':2}[channel], value)
            
            elif model == 'lab':
                entry = getattr(self, f'lab_{channel.lower()}_entry')
                value = float(entry.get())
                self.update_from_slider(model, {'L':0, 'A':1, 'B':2}[channel], value)
                
        except:
            pass
    
    def update_all_displays(self):
        hex_color = f'#{self.rgb[0]:02x}{self.rgb[1]:02x}{self.rgb[2]:02x}'
        
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, hex_color.upper())
        
        self.r_entry.delete(0, tk.END)
        self.r_entry.insert(0, str(self.rgb[0]))
        self.g_entry.delete(0, tk.END)
        self.g_entry.insert(0, str(self.rgb[1]))
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, str(self.rgb[2]))
        
        self.color_preview.delete("all")
        self.color_preview.create_rectangle(0, 0, 400, 80, 
                                          fill=hex_color, outline="")
        
        self.update_sliders()
        self.update_value_labels()
    
    def update_sliders(self):
        self.r_slider.set(self.rgb[0])
        self.g_slider.set(self.rgb[1])
        self.b_slider.set(self.rgb[2])
        
        for i, color in enumerate(['c', 'm', 'y', 'k']):
            getattr(self, f'cmyk_{color}_slider').set(round(self.cmyk[i], 1))
        
        for i, color in enumerate(['h', 's', 'v']):
            getattr(self, f'hsv_{color}_slider').set(round(self.hsv[i], 1))
        
        for i, color in enumerate(['h', 'l', 's']):
            getattr(self, f'hls_{color}_slider').set(round(self.hls[i], 1))
        
        for i, color in enumerate(['x', 'y', 'z']):
            getattr(self, f'xyz_{color}_slider').set(round(self.xyz[i], 1))
        
        for i, color in enumerate(['l', 'a', 'b']):
            getattr(self, f'lab_{color}_slider').set(round(self.lab[i], 1))
        
        self.update_entry_fields()
    
    def update_entry_fields(self):
        for i, color in enumerate(['c', 'm', 'y', 'k']):
            entry = getattr(self, f'cmyk_{color}_entry')
            entry.delete(0, tk.END)
            entry.insert(0, f"{self.cmyk[i]:.1f}")
        
        for i, color in enumerate(['h', 's', 'v']):
            entry = getattr(self, f'hsv_{color}_entry')
            entry.delete(0, tk.END)
            entry.insert(0, f"{self.hsv[i]:.1f}")
        
        for i, color in enumerate(['h', 'l', 's']):
            entry = getattr(self, f'hls_{color}_entry')
            entry.delete(0, tk.END)
            entry.insert(0, f"{self.hls[i]:.1f}")
        
        for i, color in enumerate(['x', 'y', 'z']):
            entry = getattr(self, f'xyz_{color}_entry')
            entry.delete(0, tk.END)
            entry.insert(0, f"{self.xyz[i]:.2f}")
        
        for i, color in enumerate(['l', 'a', 'b']):
            entry = getattr(self, f'lab_{color}_entry')
            entry.delete(0, tk.END)
            entry.insert(0, f"{self.lab[i]:.2f}")
    
    def update_value_labels(self):
        self.value_labels["RGB"]["R:"].config(text=f"{self.rgb[0]}")
        self.value_labels["RGB"]["G:"].config(text=f"{self.rgb[1]}")
        self.value_labels["RGB"]["B:"].config(text=f"{self.rgb[2]}")
        
        self.value_labels["CMYK"]["C:"].config(text=f"{self.cmyk[0]:.1f}%")
        self.value_labels["CMYK"]["M:"].config(text=f"{self.cmyk[1]:.1f}%")
        self.value_labels["CMYK"]["Y:"].config(text=f"{self.cmyk[2]:.1f}%")
        self.value_labels["CMYK"]["K:"].config(text=f"{self.cmyk[3]:.1f}%")
        
        self.value_labels["HSV"]["H:"].config(text=f"{self.hsv[0]:.1f}°")
        self.value_labels["HSV"]["S:"].config(text=f"{self.hsv[1]:.1f}%")
        self.value_labels["HSV"]["V:"].config(text=f"{self.hsv[2]:.1f}%")
        
        self.value_labels["HLS"]["H:"].config(text=f"{self.hls[0]:.1f}°")
        self.value_labels["HLS"]["L:"].config(text=f"{self.hls[1]:.1f}%")
        self.value_labels["HLS"]["S:"].config(text=f"{self.hls[2]:.1f}%")
        
        self.value_labels["XYZ"]["X:"].config(text=f"{self.xyz[0]:.2f}")
        self.value_labels["XYZ"]["Y:"].config(text=f"{self.xyz[1]:.2f}")
        self.value_labels["XYZ"]["Z:"].config(text=f"{self.xyz[2]:.2f}")
        
        self.value_labels["LAB"]["L*:"].config(text=f"{self.lab[0]:.2f}")
        self.value_labels["LAB"]["a*:"].config(text=f"{self.lab[1]:.2f}")
        self.value_labels["LAB"]["b*:"].config(text=f"{self.lab[2]:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorConverterApp(root)
    root.mainloop()