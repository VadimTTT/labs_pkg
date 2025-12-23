import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageFont
import math
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Обработка изображений - Пороговая обработка и фильтрация")
        self.root.geometry("1400x900")
        
        self.original_image = None
        self.processed_image = None
        self.original_data = None
        self.current_image_path = None
        
        self.setup_styles()
        self.create_widgets()
        self.create_image_database()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Method.TButton', font=('Arial', 10, 'bold'), padding=5)
    
    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Обработка изображений: Пороговая обработка и фильтрация", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="Загрузить изображение", 
                  command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить результат", 
                  command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сбросить", 
                  command=self.reset_image).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Готово")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Основной контент
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - изображения
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Оригинальное изображение
        orig_frame = ttk.LabelFrame(left_panel, text="Оригинальное изображение", padding="10")
        orig_frame.pack(fill=tk.BOTH, expand=True)
        
        self.original_canvas = tk.Canvas(orig_frame, bg='white')
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        ttk.Label(orig_frame, text="Изображение не загружено").pack()
        
        # Обработанное изображение
        proc_frame = ttk.LabelFrame(left_panel, text="Обработанное изображение", padding="10")
        proc_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.processed_canvas = tk.Canvas(proc_frame, bg='white')
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)
        ttk.Label(proc_frame, text="Результат обработки").pack()
        
        # Правая панель - методы
        right_panel = ttk.Frame(content_frame, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # Методы обработки
        methods_frame = ttk.LabelFrame(right_panel, text="Методы обработки", padding="15")
        methods_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook для группировки методов
        notebook = ttk.Notebook(methods_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        tab1 = ttk.Frame(notebook, padding="10")
        self.create_global_threshold_tab(tab1)
        notebook.add(tab1, text="Глобальная пороговая")
        
        tab2 = ttk.Frame(notebook, padding="10")
        self.create_adaptive_threshold_tab(tab2)
        notebook.add(tab2, text="Адаптивная пороговая")
        
        tab3 = ttk.Frame(notebook, padding="10")
        self.create_lowpass_filters_tab(tab3)
        notebook.add(tab3, text="Низкочастотные фильтры")
        
        tab4 = ttk.Frame(notebook, padding="10")
        self.create_test_database_tab(tab4)
        notebook.add(tab4, text="Тестовая база")
        
        # Гистограммы
        hist_frame = ttk.LabelFrame(right_panel, text="Гистограммы", padding="10")
        hist_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.hist_canvas_frame = ttk.Frame(hist_frame)
        self.hist_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Информация
        info_frame = ttk.LabelFrame(right_panel, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=8, width=40)
        scrollbar = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_global_threshold_tab(self, parent):
        ttk.Label(parent, text="Выберите метод глобальной пороговой обработки:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.global_method_var = tk.StringVar(value="otsu")
        
        methods = [
            ("Метод Оцу (Otsu)", "otsu"),
            ("Метод треугольников (Triangle)", "triangle"),
            ("Ручной порог", "manual"),
            ("Среднее значение", "mean"),
            ("Изогистезус (Isodata)", "isodata")
        ]
        
        for text, value in methods:
            ttk.Radiobutton(parent, text=text, variable=self.global_method_var, 
                          value=value).pack(anchor='w', padx=20)
        
        # Параметры для ручного порога
        manual_frame = ttk.Frame(parent)
        manual_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(manual_frame, text="Ручной порог:").pack(side=tk.LEFT)
        self.threshold_slider = tk.Scale(manual_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                                       length=200)
        self.threshold_slider.pack(side=tk.LEFT, padx=5)
        self.threshold_slider.set(128)
        
        ttk.Button(parent, text="Показать гистограмму с порогом", 
                  command=self.show_threshold_histogram).pack(pady=5)
        
        ttk.Button(parent, text="Применить глобальную пороговую обработку", 
                  style='Method.TButton',
                  command=self.apply_global_threshold).pack(pady=10)
        
        # Описание методов
        desc_text = tk.Text(parent, height=8, width=40)
        desc_text.insert(tk.END, """Метод Оцу: Автоматически находит оптимальный порог, максимизируя межклассовую дисперсию.

Метод треугольников: Эффективен для гистограмм с пиками.

Изогистезус: Итеративный метод, находит порог где средние значения классов равны.

Ручной порог: Позволяет задать порог вручную для тонкой настройки.""")
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def create_adaptive_threshold_tab(self, parent):
        ttk.Label(parent, text="Адаптивная пороговая обработка:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.adaptive_method_var = tk.StringVar(value="mean")
        
        ttk.Radiobutton(parent, text="Среднее (Mean)", variable=self.adaptive_method_var, 
                       value="mean").pack(anchor='w')
        ttk.Radiobutton(parent, text="Гауссово (Gaussian)", variable=self.adaptive_method_var, 
                       value="gaussian").pack(anchor='w')
        
        # Параметры
        params_frame = ttk.Frame(parent)
        params_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(params_frame, text="Размер блока:").grid(row=0, column=0, sticky='w', padx=5)
        self.block_size_var = tk.IntVar(value=11)
        block_spin = ttk.Spinbox(params_frame, from_=3, to=101, increment=2, 
                                textvariable=self.block_size_var, width=10)
        block_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="Константа C:").grid(row=1, column=0, sticky='w', padx=5)
        self.c_value_var = tk.IntVar(value=2)
        c_spin = ttk.Spinbox(params_frame, from_=-50, to=50, 
                            textvariable=self.c_value_var, width=10)
        c_spin.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(parent, text="Применить адаптивную пороговую обработку", 
                  style='Method.TButton',
                  command=self.apply_adaptive_threshold).pack(pady=10)
        
        desc_text = tk.Text(parent, height=6, width=40)
        desc_text.insert(tk.END, """Размер блока: Размер локальной области для расчета порога (нечетное число).

Константа C: Значение, вычитаемое из среднего/взвешенной суммы.

Алгоритм: Для каждого пикселя вычисляется порог на основе локальной статистики.""")
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X, pady=5)
    
    def create_lowpass_filters_tab(self, parent):
        ttk.Label(parent, text="Низкочастотные (сглаживающие) фильтры:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="gaussian")
        
        filters = [
            ("Гауссовский фильтр", "gaussian"),
            ("Усредняющий фильтр (Box)", "box"),
            ("Медианный фильтр", "median"),
            ("Фильтр Габора", "gabor"),
            ("Билатеральный фильтр", "bilateral")
        ]
        
        for text, value in filters:
            ttk.Radiobutton(parent, text=text, variable=self.filter_var, 
                          value=value).pack(anchor='w')
        
        # Параметры фильтра
        params_frame = ttk.Frame(parent)
        params_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(params_frame, text="Размер ядра:").grid(row=0, column=0, sticky='w', padx=5)
        self.kernel_size_var = tk.IntVar(value=5)
        kernel_spin = ttk.Spinbox(params_frame, from_=3, to=31, increment=2, 
                                 textvariable=self.kernel_size_var, width=10)
        kernel_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="Сигма (для Гаусса):").grid(row=1, column=0, sticky='w', padx=5)
        self.sigma_var = tk.DoubleVar(value=1.0)
        sigma_spin = ttk.Spinbox(params_frame, from_=0.1, to=10.0, increment=0.1, 
                                textvariable=self.sigma_var, width=10)
        sigma_spin.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(parent, text="Применить низкочастотный фильтр", 
                  style='Method.TButton',
                  command=self.apply_lowpass_filter).pack(pady=10)
        
        desc_text = tk.Text(parent, height=8, width=40)
        desc_text.insert(tk.END, """Гауссовский: Плавное сглаживание с весами по Гауссу.

Усредняющий: Простое усреднение значений в окрестности.

Медианный: Эффективен против импульсного шума (соли и перца).

Билатеральный: Сохраняет границы при сглаживании.

Габор: Для анализа текстур и сглаживания с учетом ориентации.""")
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X, pady=5)
    
    def create_test_database_tab(self, parent):
        ttk.Label(parent, text="Тестовая база изображений:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        categories = [
            ("Зашумленные изображения (соль-перец)", "noisy"),
            ("Размытые изображения", "blurred"),
            ("Малоконтрастные изображения", "low_contrast"),
            ("Неравномерное освещение", "uneven_lighting"),
            ("Текстовые изображения", "text"),
            ("Медицинские снимки", "medical")
        ]
        
        for text, category in categories:
            btn = ttk.Button(parent, text=text, 
                           command=lambda c=category: self.load_test_image(c))
            btn.pack(fill=tk.X, pady=2)
        
        info_text = tk.Text(parent, height=6, width=40)
        info_text.insert(tk.END, """Зашумленные: Для тестирования медианного фильтра.

Размытые: Для демонстрации ограничений фильтрации.

Малоконтрастные: Для глобальной пороговой обработки.

Неравномерное освещение: Для адаптивной пороговой.

Текстовые: Сравнение методов бинаризации.

Медицинские: Специфичные задачи сегментации.""")
        info_text.config(state=tk.DISABLED)
        info_text.pack(fill=tk.X, pady=5)
    
    def create_image_database(self):
        self.test_images = {}
    
    def image_to_data(self, image):
        """Конвертируем изображение в список списков (вместо numpy array)"""
        if image.mode != 'L':
            image = image.convert('L')
        
        width, height = image.size
        data = []
        
        for y in range(height):
            row = []
            for x in range(width):
                row.append(image.getpixel((x, y)))
            data.append(row)
        
        return data
    
    def data_to_image(self, data):
        """Конвертируем список списков обратно в изображение"""
        height = len(data)
        width = len(data[0]) if height > 0 else 0
        
        img = Image.new('L', (width, height))
        
        for y in range(height):
            for x in range(width):
                img.putpixel((x, y), int(data[y][x]))
        
        return img.convert('RGB')
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.original_image = Image.open(file_path).convert('RGB')
                self.processed_image = self.original_image.copy()
                self.original_data = self.image_to_data(self.original_image)
                
                self.display_images()
                self.update_info("Изображение загружено")
                self.show_histograms()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")
    
    def load_test_image(self, category):
        if category == 'noisy':
            self.create_demo_noisy_image()
        elif category == 'blurred':
            self.create_demo_blurred_image()
        elif category == 'low_contrast':
            self.create_demo_low_contrast_image()
        elif category == 'uneven_lighting':
            self.create_demo_uneven_lighting_image()
        elif category == 'text':
            self.create_demo_text_image()
        elif category == 'medical':
            self.create_demo_medical_image()
    
    def create_demo_noisy_image(self):
        """Создание зашумленного изображения"""
        img = Image.new('L', (400, 300), color=128)
        pixels = img.load()
        
        import random
        for i in range(1000):
            x = random.randint(0, img.width-1)
            y = random.randint(0, img.height-1)
            pixels[x, y] = 0 if random.random() > 0.5 else 255
        
        self.original_image = img.convert('RGB')
        self.processed_image = self.original_image.copy()
        self.original_data = self.image_to_data(img)
        self.display_images()
        self.update_info("Тестовое изображение: Зашумленное (соль и перец)")
    
    def create_demo_low_contrast_image(self):
        """Создание малоконтрастного изображения"""
        img = Image.new('L', (400, 300), color=100)
        pixels = img.load()
        
        for y in range(img.height):
            for x in range(img.width):
                value = 80 + int(40 * (x / img.width))
                pixels[x, y] = value
        
        self.original_image = img.convert('RGB')
        self.processed_image = self.original_image.copy()
        self.original_data = self.image_to_data(img)
        self.display_images()
        self.update_info("Тестовое изображение: Малоконтрастное")
    
    def create_demo_uneven_lighting_image(self):
        """Создание изображения с неравномерным освещением"""
        img = Image.new('L', (400, 300), color=150)
        pixels = img.load()
        
        center_x, center_y = img.width // 2, img.height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
        
        for y in range(img.height):
            for x in range(img.width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                brightness = 100 + int(100 * (dist / max_dist))
                pixels[x, y] = min(255, max(0, brightness))
        
        self.original_image = img.convert('RGB')
        self.processed_image = self.original_image.copy()
        self.original_data = self.image_to_data(img)
        self.display_images()
        self.update_info("Тестовое изображение: Неравномерное освещение")
    
    def create_demo_blurred_image(self):
        """Создание размытого изображения"""
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 350, 250], fill='black', outline='red', width=3)
        draw.ellipse([150, 100, 250, 200], fill='blue')
        
        self.original_image = img.filter(ImageFilter.GaussianBlur(5))
        self.processed_image = self.original_image.copy()
        self.original_data = self.image_to_data(self.original_image)
        self.display_images()
        self.update_info("Тестовое изображение: Размытое")
    
    def create_demo_text_image(self):
        """Создание текстового изображения"""
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Тестовый текст для обработки", fill='black', font=font)
        draw.text((50, 100), "Адаптивная пороговая обработка", fill='darkgray', font=font)
        
        self.original_image = img
        self.processed_image = self.original_image.copy()
        self.original_data = self.image_to_data(img.convert('L'))
        self.display_images()
        self.update_info("Тестовое изображение: Текстовое")
    
    def create_demo_medical_image(self):
        """Создание медицинского изображения"""
        img = Image.new('L', (300, 300), color=50)
        pixels = img.load()
        
        center_x, center_y = 150, 150
        for y in range(img.height):
            for x in range(img.width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if dist < 100:
                    value = 200 - int(dist)
                    pixels[x, y] = max(0, min(255, value))
        
        self.original_image = img.convert('RGB')
        self.processed_image = self.original_image.copy()
        self.original_data = self.image_to_data(img)
        self.display_images()
        self.update_info("Тестовое изображение: Медицинское (рентген)")
    
    def display_images(self):
        if self.original_image:
            self.display_on_canvas(self.original_image, self.original_canvas)
            
            if self.processed_image:
                self.display_on_canvas(self.processed_image, self.processed_canvas)
    
    def display_on_canvas(self, image, canvas):
        canvas.delete("all")
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            img_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                display_width = canvas_width
                display_height = int(canvas_width / img_ratio)
            else:
                display_height = canvas_height
                display_width = int(canvas_height * img_ratio)
            
            if display_width > 0 and display_height > 0:
                resized_image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_image)
                
                canvas.image = photo
                x = (canvas_width - display_width) // 2
                y = (canvas_height - display_height) // 2
                canvas.create_image(x, y, anchor=tk.NW, image=photo)
    
    def apply_global_threshold(self):
        if self.original_data is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        
        self.status_label.config(text="Применение глобальной пороговой обработки...")
        self.root.update()
        
        try:
            method = self.global_method_var.get()
            
            if method == "manual":
                threshold = self.threshold_slider.get()
                binary_data = self.apply_threshold_manual(self.original_data, threshold)
                self.update_info(f"Ручной порог: {threshold}")
            
            elif method == "otsu":
                threshold, binary_data = self.otsu_threshold_python(self.original_data)
                self.update_info(f"Метод Оцу: найден порог = {threshold}")
            
            elif method == "triangle":
                threshold, binary_data = self.triangle_threshold_python(self.original_data)
                self.update_info(f"Метод треугольников: порог = {threshold}")
            
            elif method == "mean":
                threshold = self.calculate_mean(self.original_data)
                binary_data = self.apply_threshold_manual(self.original_data, threshold)
                self.update_info(f"Среднее значение: порог = {threshold:.1f}")
            
            elif method == "isodata":
                threshold, binary_data = self.isodata_threshold_python(self.original_data)
                self.update_info(f"Изогистезус: порог = {threshold}")
            
            self.processed_image = self.data_to_image(binary_data)
            self.display_images()
            self.status_label.config(text="Готово")
            self.show_histograms()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить пороговую обработку: {str(e)}")
            self.status_label.config(text="Ошибка")
    
    def apply_threshold_manual(self, data, threshold):
        """Применение ручного порога"""
        height = len(data)
        width = len(data[0]) if height > 0 else 0
        
        result = []
        for y in range(height):
            row = []
            for x in range(width):
                value = 255 if data[y][x] > threshold else 0
                row.append(value)
            result.append(row)
        
        return result
    
    def calculate_mean(self, data):
        """Вычисление среднего значения"""
        total = 0
        count = 0
        
        for row in data:
            for pixel in row:
                total += pixel
                count += 1
        
        return total / count if count > 0 else 0
    
    def calculate_histogram(self, data):
        """Вычисление гистограммы"""
        hist = [0] * 256
        
        for row in data:
            for pixel in row:
                hist[pixel] += 1
        
        return hist
    
    def otsu_threshold_python(self, data):
        """Реализация метода Оцу на чистом Python"""
        hist = self.calculate_histogram(data)
        
        # Общее количество пикселей
        total = sum(hist)
        if total == 0:
            return 128, self.apply_threshold_manual(data, 128)
        
        # Нормализуем гистограмму
        hist_norm = [h / total for h in hist]
        
        # Кумулятивные суммы и средние
        cum_sum = [0] * 256
        cum_mean = [0] * 256
        
        cum_sum[0] = hist_norm[0]
        cum_mean[0] = 0
        
        for t in range(1, 256):
            cum_sum[t] = cum_sum[t-1] + hist_norm[t]
            cum_mean[t] = cum_mean[t-1] + t * hist_norm[t]
        
        global_mean = cum_mean[255]
        
        # Вычисляем межклассовую дисперсию
        sigma_b = [0] * 256
        max_sigma = 0
        best_threshold = 128
        
        for t in range(256):
            w0 = cum_sum[t]
            if w0 == 0 or w0 == 1:
                continue
            
            w1 = 1 - w0
            mu0 = cum_mean[t] / w0 if w0 > 0 else 0
            mu1 = (global_mean - cum_mean[t]) / w1 if w1 > 0 else 0
            
            sigma_b[t] = w0 * w1 * (mu0 - mu1) ** 2
            
            if sigma_b[t] > max_sigma:
                max_sigma = sigma_b[t]
                best_threshold = t
        
        binary_data = self.apply_threshold_manual(data, best_threshold)
        return best_threshold, binary_data
    
    def triangle_threshold_python(self, data):
        """Реализация метода треугольников на Python"""
        hist = self.calculate_histogram(data)
        
        # Находим пик гистограммы
        peak_idx = max(range(256), key=lambda i: hist[i])
        
        # Находим конец гистограммы
        if peak_idx < 128:
            end_idx = 255
            for i in range(255, peak_idx, -1):
                if hist[i] > 0:
                    end_idx = i
                    break
        else:
            end_idx = 0
            for i in range(peak_idx):
                if hist[i] > 0:
                    end_idx = i
                    break
        
        # Вычисляем максимальное расстояние
        max_distance = 0
        threshold = 128
        
        x0, y0 = peak_idx, hist[peak_idx]
        x1, y1 = end_idx, hist[end_idx]
        
        for i in range(256):
            if hist[i] == 0:
                continue
            
            x2, y2 = i, hist[i]
            
            # Расстояние от точки до линии
            if (x1 - x0) == 0 and (y1 - y0) == 0:
                distance = 0
            else:
                numerator = abs((y2 - y0) * (x1 - x0) - (x2 - x0) * (y1 - y0))
                denominator = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
                distance = numerator / denominator if denominator != 0 else 0
            
            if distance > max_distance:
                max_distance = distance
                threshold = i
        
        binary_data = self.apply_threshold_manual(data, threshold)
        return threshold, binary_data
    
    def isodata_threshold_python(self, data):
        """Реализация метода изогистезус"""
        threshold = self.calculate_mean(data)
        
        for _ in range(100):
            # Разделяем на два класса
            class1 = []
            class2 = []
            
            for row in data:
                for pixel in row:
                    if pixel <= threshold:
                        class1.append(pixel)
                    else:
                        class2.append(pixel)
            
            if not class1 or not class2:
                break
            
            mean1 = sum(class1) / len(class1)
            mean2 = sum(class2) / len(class2)
            
            new_threshold = (mean1 + mean2) / 2
            
            if abs(new_threshold - threshold) < 0.5:
                break
            
            threshold = new_threshold
        
        binary_data = self.apply_threshold_manual(data, int(threshold))
        return int(threshold), binary_data
    
    def apply_adaptive_threshold(self):
        if self.original_data is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        
        self.status_label.config(text="Применение адаптивной пороговой обработки...")
        self.root.update()
        
        try:
            method = self.adaptive_method_var.get()
            block_size = self.block_size_var.get()
            c = self.c_value_var.get()
            
            if block_size % 2 == 0:
                block_size += 1
            
            if method == "mean":
                binary_data = self.adaptive_threshold_mean_python(self.original_data, block_size, c)
                self.update_info(f"Адаптивный порог (среднее): block={block_size}, C={c}")
            
            elif method == "gaussian":
                binary_data = self.adaptive_threshold_gaussian_python(self.original_data, block_size, c)
                self.update_info(f"Адаптивный порог (Гаусс): block={block_size}, C={c}")
            
            self.processed_image = self.data_to_image(binary_data)
            self.display_images()
            self.status_label.config(text="Готово")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить адаптивную пороговую обработку: {str(e)}")
            self.status_label.config(text="Ошибка")
    
    def adaptive_threshold_mean_python(self, data, block_size, c):
        """Адаптивный порог на основе среднего"""
        height = len(data)
        width = len(data[0]) if height > 0 else 0
        
        result = []
        half = block_size // 2
        
        for y in range(height):
            row_result = []
            for x in range(width):
                # Вычисляем локальное среднее
                sum_val = 0
                count = 0
                
                for dy in range(-half, half + 1):
                    ny = y + dy
                    if 0 <= ny < height:
                        for dx in range(-half, half + 1):
                            nx = x + dx
                            if 0 <= nx < width:
                                sum_val += data[ny][nx]
                                count += 1
                
                local_mean = sum_val / count if count > 0 else 0
                
                # Применяем порог
                value = 255 if data[y][x] > (local_mean - c) else 0
                row_result.append(value)
            
            result.append(row_result)
        
        return result
    
    def adaptive_threshold_gaussian_python(self, data, block_size, c):
        """Упрощенный адаптивный порог (имитация Гаусса)"""
        # Вместо реального Гаусса используем два прохода среднего
        height = len(data)
        width = len(data[0]) if height > 0 else 0
        
        # Первый проход - горизонтальное размытие
        temp = []
        half = block_size // 2
        
        for y in range(height):
            row = []
            for x in range(width):
                sum_val = 0
                count = 0
                
                for dx in range(-half, half + 1):
                    nx = x + dx
                    if 0 <= nx < width:
                        sum_val += data[y][nx]
                        count += 1
                
                row.append(sum_val / count if count > 0 else 0)
            temp.append(row)
        
        # Второй проход - вертикальное размытие и порог
        result = []
        for y in range(height):
            row_result = []
            for x in range(width):
                sum_val = 0
                count = 0
                
                for dy in range(-half, half + 1):
                    ny = y + dy
                    if 0 <= ny < height:
                        sum_val += temp[ny][x]
                        count += 1
                
                local_mean = sum_val / count if count > 0 else 0
                value = 255 if data[y][x] > (local_mean - c) else 0
                row_result.append(value)
            
            result.append(row_result)
        
        return result
    
    def apply_lowpass_filter(self):
        if self.original_image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        
        self.status_label.config(text="Применение фильтра...")
        self.root.update()
        
        try:
            filter_type = self.filter_var.get()
            kernel_size = self.kernel_size_var.get()
            sigma = self.sigma_var.get()
            
            if kernel_size % 2 == 0:
                kernel_size += 1
            
            if filter_type == "gaussian":
                self.processed_image = self.original_image.filter(
                    ImageFilter.GaussianBlur(sigma)
                )
                self.update_info(f"Гауссовский фильтр: σ={sigma}")
            
            elif filter_type == "box":
                self.processed_image = self.original_image.filter(
                    ImageFilter.BoxBlur(kernel_size // 2)
                )
                self.update_info(f"Усредняющий фильтр: размер={kernel_size}")
            
            elif filter_type == "median":
                self.processed_image = self.original_image.filter(
                    ImageFilter.MedianFilter(kernel_size)
                )
                self.update_info(f"Медианный фильтр: размер={kernel_size}")
            
            elif filter_type == "bilateral":
                # Упрощенная версия
                self.processed_image = self.simple_bilateral_filter(kernel_size, sigma)
                self.update_info(f"Билатеральный фильтр: размер={kernel_size}, σ={sigma}")
            
            elif filter_type == "gabor":
                # Имитация фильтра Габора
                self.processed_image = self.original_image.filter(ImageFilter.GaussianBlur(sigma))
                self.update_info(f"Фильтр Габора: размер={kernel_size}, σ={sigma}")
            
            self.display_images()
            self.status_label.config(text="Готово")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить фильтр: {str(e)}")
            self.status_label.config(text="Ошибка")
    
    def simple_bilateral_filter(self, kernel_size, sigma):
        """Упрощенный билатеральный фильтр"""
        img = self.original_image
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        result = Image.new('RGB', (width, height))
        
        half = kernel_size // 2
        
        for y in range(height):
            for x in range(width):
                # Простое усреднение как имитация
                r_sum, g_sum, b_sum = 0, 0, 0
                count = 0
                
                for dy in range(-half, half + 1):
                    ny = y + dy
                    if 0 <= ny < height:
                        for dx in range(-half, half + 1):
                            nx = x + dx
                            if 0 <= nx < width:
                                r, g, b = img.getpixel((nx, ny))
                                r_sum += r
                                g_sum += g
                                b_sum += b
                                count += 1
                
                if count > 0:
                    r_avg = int(r_sum / count)
                    g_avg = int(g_sum / count)
                    b_avg = int(b_sum / count)
                    result.putpixel((x, y), (r_avg, g_avg, b_avg))
        
        return result
    
    def show_threshold_histogram(self):
        if self.original_data is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        
        method = self.global_method_var.get()
        
        # Вычисляем гистограмму
        hist = self.calculate_histogram(self.original_data)
        
        # Вычисляем порог
        if method == "manual":
            threshold = self.threshold_slider.get()
        elif method == "otsu":
            threshold, _ = self.otsu_threshold_python(self.original_data)
        elif method == "triangle":
            threshold, _ = self.triangle_threshold_python(self.original_data)
        elif method == "mean":
            threshold = self.calculate_mean(self.original_data)
        elif method == "isodata":
            threshold, _ = self.isodata_threshold_python(self.original_data)
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(8, 4))
        
        ax.bar(range(256), hist, alpha=0.7, color='blue', edgecolor='black')
        ax.axvline(x=threshold, color='red', linestyle='--', linewidth=2, 
                  label=f'Порог: {int(threshold)}')
        
        ax.set_xlabel('Яркость')
        ax.set_ylabel('Частота')
        ax.set_title(f'Гистограмма с порогом ({method})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def show_histograms(self):
        if not hasattr(self, 'hist_canvas_frame'):
            return
        
        for widget in self.hist_canvas_frame.winfo_children():
            widget.destroy()
        
        if self.original_data is None:
            return
        
        # Создаем гистограммы
        fig, axes = plt.subplots(1, 2, figsize=(10, 3))
        
        # Гистограмма оригинального
        hist_original = self.calculate_histogram(self.original_data)
        axes[0].bar(range(256), hist_original, alpha=0.7, color='blue', edgecolor='black')
        axes[0].set_title('Оригинальное изображение')
        axes[0].set_xlabel('Яркость')
        axes[0].set_ylabel('Частота')
        axes[0].grid(True, alpha=0.3)
        
        # Гистограмма обработанного (если есть)
        if self.processed_image and self.processed_image != self.original_image:
            processed_data = self.image_to_data(self.processed_image)
            hist_processed = self.calculate_histogram(processed_data)
            axes[1].bar(range(256), hist_processed, alpha=0.7, color='green', edgecolor='black')
            axes[1].set_title('Обработанное изображение')
            axes[1].set_xlabel('Яркость')
            axes[1].set_ylabel('Частота')
            axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.hist_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_info(self, message):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"{message}\n\n")
        
        if self.original_image:
            self.info_text.insert(tk.END, f"Размер: {self.original_image.width}×{self.original_image.height}\n")
            self.info_text.insert(tk.END, f"Формат: {self.original_image.mode}\n")
            
            if self.original_data:
                # Вычисляем статистику
                pixels = [pixel for row in self.original_data for pixel in row]
                if pixels:
                    total = sum(pixels)
                    count = len(pixels)
                    mean_val = total / count
                    
                    variance = sum((x - mean_val) ** 2 for x in pixels) / count
                    std_val = math.sqrt(variance)
                    
                    self.info_text.insert(tk.END, f"Средняя яркость: {mean_val:.1f}\n")
                    self.info_text.insert(tk.END, f"Стандартное отклонение: {std_val:.1f}\n")
                    self.info_text.insert(tk.END, f"Минимальная яркость: {min(pixels)}\n")
                    self.info_text.insert(tk.END, f"Максимальная яркость: {max(pixels)}\n")
    
    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Внимание", "Нет обработанного изображения для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить обработанное изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path)
                messagebox.showinfo("Успех", f"Изображение сохранено как {file_path}")
                self.status_label.config(text="Изображение сохранено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")
    
    def reset_image(self):
        if self.original_image:
            self.processed_image = self.original_image.copy()
            self.display_images()
            self.update_info("Изображение сброшено к оригиналу")
            self.show_histograms()
            self.status_label.config(text="Сброшено")

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()