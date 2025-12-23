import tkinter as tk
from tkinter import ttk, messagebox
import time
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Point:
    """Точка на плоскости"""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

class RasterAlgorithms:
    """Класс с реализацией алгоритмов растризации"""
    
    @staticmethod
    def step_by_step(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Пошаговый алгоритм"""
        points = []
        
        if x1 == x2:  # Вертикальная линия
            y_start, y_end = sorted([y1, y2])
            for y in range(y_start, y_end + 1):
                points.append((x1, y))
        elif y1 == y2:  # Горизонтальная линия
            x_start, x_end = sorted([x1, x2])
            for x in range(x_start, x_end + 1):
                points.append((x, y1))
        else:
            # Линия под углом
            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy))
            
            x_inc = dx / steps
            y_inc = dy / steps
            
            x, y = float(x1), float(y1)
            for _ in range(steps + 1):
                points.append((round(x), round(y)))
                x += x_inc
                y += y_inc
                
        return points
    
    @staticmethod
    def dda(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Алгоритм ЦДА (Digital Differential Analyzer)"""
        points = []
        
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            points.append((x1, y1))
            return points
            
        x_increment = dx / steps
        y_increment = dy / steps
        
        x, y = x1, y1
        points.append((round(x), round(y)))
        
        for _ in range(steps):
            x += x_increment
            y += y_increment
            points.append((round(x), round(y)))
            
        return points
    
    @staticmethod
    def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Алгоритм Брезенхема для отрезков"""
        points = []
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        # Определяем направление движения
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            # Наклон меньше 45 градусов
            err = dx / 2.0
            while x1 != x2:
                points.append((x1, y1))
                err -= dy
                if err < 0:
                    y1 += sy
                    err += dx
                x1 += sx
        else:
            # Наклон больше 45 градусов
            err = dy / 2.0
            while y1 != y2:
                points.append((x1, y1))
                err -= dx
                if err < 0:
                    x1 += sx
                    err += dy
                y1 += sy
                
        points.append((x1, y1))
        return points
    
    @staticmethod
    def bresenham_circle(xc: int, yc: int, r: int) -> List[Tuple[int, int]]:
        """Алгоритм Брезенхема для окружности"""
        points = []
        
        x = 0
        y = r
        d = 3 - 2 * r
        
        # Добавляем начальные точки
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ])
        
        while y >= x:
            x += 1
            
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
                
            if x > y:
                break
                
            # Добавляем 8 симметричных точек
            points.extend([
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x)
            ])
            
        return points
    
    @staticmethod
    def castle_pitway(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Алгоритм Кастла-Питвея (Castle-Pitway) - модификация Брезенхема"""
        points = []
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dy <= dx:
            # Наклон меньше 45 градусов
            d = 2 * dy - dx
            d1 = 2 * dy
            d2 = 2 * (dy - dx)
            
            x, y = x1, y1
            points.append((x, y))
            
            while x != x2:
                x += sx
                if d < 0:
                    d += d1
                else:
                    y += sy
                    d += d2
                points.append((x, y))
        else:
            # Наклон больше 45 градусов
            d = 2 * dx - dy
            d1 = 2 * dx
            d2 = 2 * (dx - dy)
            
            x, y = x1, y1
            points.append((x, y))
            
            while y != y2:
                y += sy
                if d < 0:
                    d += d1
                else:
                    x += sx
                    d += d2
                points.append((x, y))
                
        return points
    
    @staticmethod
    def wu_line(x1: float, y1: float, x2: float, y2: float) -> List[Tuple[Tuple[int, int], float]]:
        """Алгоритм Ву для сглаживания линий (возвращает точки с интенсивностью)"""
        points_with_intensity = []
        
        def plot(x: int, y: int, intensity: float):
            points_with_intensity.append(((x, y), intensity))
        
        steep = abs(y2 - y1) > abs(x2 - x1)
        
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0:
            gradient = 1.0
        else:
            gradient = dy / dx
            
        # Первая конечная точка
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = 1 - (x1 + 0.5) % 1
        xpxl1 = xend
        ypxl1 = int(yend)
        
        if steep:
            plot(ypxl1, xpxl1, (1 - (yend % 1)) * xgap)
            plot(ypxl1 + 1, xpxl1, (yend % 1) * xgap)
        else:
            plot(xpxl1, ypxl1, (1 - (yend % 1)) * xgap)
            plot(xpxl1, ypxl1 + 1, (yend % 1) * xgap)
            
        intery = yend + gradient
        
        # Вторая конечная точка
        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = (x2 + 0.5) % 1
        xpxl2 = xend
        ypxl2 = int(yend)
        
        if steep:
            plot(ypxl2, xpxl2, (1 - (yend % 1)) * xgap)
            plot(ypxl2 + 1, xpxl2, (yend % 1) * xgap)
        else:
            plot(xpxl2, ypxl2, (1 - (yend % 1)) * xgap)
            plot(xpxl2, ypxl2 + 1, (yend % 1) * xgap)
            
        # Основная часть линии
        if steep:
            for x in range(xpxl1 + 1, xpxl2):
                plot(int(intery), x, 1 - (intery % 1))
                plot(int(intery) + 1, x, intery % 1)
                intery += gradient
        else:
            for x in range(xpxl1 + 1, xpxl2):
                plot(x, int(intery), 1 - (intery % 1))
                plot(x, int(intery) + 1, intery % 1)
                intery += gradient
                
        return points_with_intensity

class DrawingCanvas(tk.Canvas):
    """Холст для рисования с координатной сеткой"""
    
    def __init__(self, parent, width=800, height=600, **kwargs):
        super().__init__(parent, width=width, height=height, bg="white", **kwargs)
        self.width = width
        self.height = height
        self.grid_size = 20  # Размер ячейки сетки
        self.origin_x = width // 2
        self.origin_y = height // 2
        self.scale_factor = 1.0
        
        # Списки для хранения нарисованных объектов
        self.points_history = []
        self.current_algorithm = None
        
        # Рисуем координатную систему
        self.draw_coordinate_system()
    
    def draw_coordinate_system(self):
        """Рисует координатную систему с осями и сеткой"""
        self.delete("grid")  # Удаляем старую сетку
        
        # Рисуем сетку
        for x in range(0, self.width, self.grid_size):
            self.create_line(x, 0, x, self.height, fill="#e0e0e0", tags="grid", width=1)
        for y in range(0, self.height, self.grid_size):
            self.create_line(0, y, self.width, y, fill="#e0e0e0", tags="grid", width=1)
        
        # Рисуем оси
        self.create_line(0, self.origin_y, self.width, self.origin_y, 
                        fill="blue", width=2, arrow=tk.LAST, tags="axes")
        self.create_line(self.origin_x, self.height, self.origin_x, 0, 
                        fill="red", width=2, arrow=tk.LAST, tags="axes")
        
        # Подписи осей
        self.create_text(self.width - 10, self.origin_y - 10, text="X", 
                        fill="blue", font=("Arial", 12, "bold"), tags="axes")
        self.create_text(self.origin_x + 10, 10, text="Y", 
                        fill="red", font=("Arial", 12, "bold"), tags="axes")
        
        # Подписи к сетке
        for x in range(-self.width//2, self.width//2, self.grid_size):
            if x != 0:
                screen_x = self.origin_x + x
                self.create_text(screen_x, self.origin_y + 10, text=str(x), 
                               fill="black", font=("Arial", 8), tags="grid_labels")
        
        for y in range(-self.height//2, self.height//2, self.grid_size):
            if y != 0:
                screen_y = self.origin_y - y
                self.create_text(self.origin_x - 10, screen_y, text=str(y), 
                               fill="black", font=("Arial", 8), tags="grid_labels")
    
    def clear_drawing(self):
        """Очищает нарисованные точки и линии"""
        self.delete("point")
        self.delete("line")
        self.delete("circle")
        self.delete("wu_line")
        self.points_history.clear()
    
    def draw_pixel(self, x: int, y: int, color="black", size=2):
        """Рисует пиксель (квадратик) в заданных координатах"""
        screen_x = self.origin_x + x * self.grid_size
        screen_y = self.origin_y - y * self.grid_size
        
        return self.create_rectangle(
            screen_x - size, screen_y - size,
            screen_x + size, screen_y + size,
            fill=color, outline=color, tags="point"
        )
    
    def draw_line_between_points(self, x1: int, y1: int, x2: int, y2: int, color="green"):
        """Рисует линию между двумя точками"""
        screen_x1 = self.origin_x + x1 * self.grid_size
        screen_y1 = self.origin_y - y1 * self.grid_size
        screen_x2 = self.origin_x + x2 * self.grid_size
        screen_y2 = self.origin_y - y2 * self.grid_size
        
        return self.create_line(
            screen_x1, screen_y1, screen_x2, screen_y2,
            fill=color, width=2, tags="line"
        )
    
    def draw_circle(self, xc: int, yc: int, r: int, color="purple"):
        """Рисует окружность"""
        screen_xc = self.origin_x + xc * self.grid_size
        screen_yc = self.origin_y - yc * self.grid_size
        screen_r = r * self.grid_size
        
        return self.create_oval(
            screen_xc - screen_r, screen_yc - screen_r,
            screen_xc + screen_r, screen_yc + screen_r,
            outline=color, width=2, tags="circle"
        )
    
    def draw_wu_line(self, points_with_intensity, color="blue"):
        """Рисует сглаженную линию по алгоритму Ву"""
        for (x, y), intensity in points_with_intensity:
            # Преобразуем интенсивность в оттенок серого
            gray_value = int(255 * (1 - intensity))
            hex_color = f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
            
            screen_x = self.origin_x + x * self.grid_size
            screen_y = self.origin_y - y * self.grid_size
            
            self.create_rectangle(
                screen_x - 1, screen_y - 1,
                screen_x + 1, screen_y + 1,
                fill=hex_color, outline=hex_color, tags="wu_line"
            )

class RasterAlgorithmsApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация алгоритмов растризации")
        self.root.geometry("1200x700")
        
        # Инициализация алгоритмов
        self.algorithms = RasterAlgorithms()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Установка значений по умолчанию
        self.set_default_values()
    
    def create_widgets(self):
        """Создает все виджеты интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - управление
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Выбор алгоритма
        ttk.Label(control_frame, text="Алгоритм:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.algorithm_var = tk.StringVar()
        algorithms = [
            "Пошаговый алгоритм",
            "Алгоритм ЦДА",
            "Алгоритм Брезенхема (отрезок)",
            "Алгоритм Брезенхема (окружность)",
            "Алгоритм Кастла-Питвея",
            "Алгоритм Ву (сглаживание)"
        ]
        
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var, 
                                     values=algorithms, state="readonly", width=25)
        algorithm_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_changed)
        
        # Параметры для отрезка
        self.line_frame = ttk.Frame(control_frame)
        self.line_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Label(self.line_frame, text="Начальная точка:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.line_frame, text="X1:").grid(row=1, column=0, sticky=tk.W)
        self.x1_var = tk.IntVar()
        ttk.Entry(self.line_frame, textvariable=self.x1_var, width=8).grid(row=1, column=1, padx=(5, 10))
        
        ttk.Label(self.line_frame, text="Y1:").grid(row=1, column=2, sticky=tk.W)
        self.y1_var = tk.IntVar()
        ttk.Entry(self.line_frame, textvariable=self.y1_var, width=8).grid(row=1, column=3)
        
        ttk.Label(self.line_frame, text="Конечная точка:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(self.line_frame, text="X2:").grid(row=3, column=0, sticky=tk.W)
        self.x2_var = tk.IntVar()
        ttk.Entry(self.line_frame, textvariable=self.x2_var, width=8).grid(row=3, column=1, padx=(5, 10))
        
        ttk.Label(self.line_frame, text="Y2:").grid(row=3, column=2, sticky=tk.W)
        self.y2_var = tk.IntVar()
        ttk.Entry(self.line_frame, textvariable=self.y2_var, width=8).grid(row=3, column=3)
        
        # Параметры для окружности
        self.circle_frame = ttk.Frame(control_frame)
        self.circle_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Label(self.circle_frame, text="Центр окружности:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.circle_frame, text="Xc:").grid(row=1, column=0, sticky=tk.W)
        self.xc_var = tk.IntVar()
        ttk.Entry(self.circle_frame, textvariable=self.xc_var, width=8).grid(row=1, column=1, padx=(5, 10))
        
        ttk.Label(self.circle_frame, text="Yc:").grid(row=1, column=2, sticky=tk.W)
        self.yc_var = tk.IntVar()
        ttk.Entry(self.circle_frame, textvariable=self.yc_var, width=8).grid(row=1, column=3)
        
        ttk.Label(self.circle_frame, text="Радиус:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.r_var = tk.IntVar()
        ttk.Entry(self.circle_frame, textvariable=self.r_var, width=8).grid(row=2, column=1, padx=(5, 10))
        
        # Скрываем фрейм окружности по умолчанию
        self.circle_frame.grid_remove()
        
        # Кнопки управления
        ttk.Button(control_frame, text="Выполнить", command=self.execute_algorithm).grid(
            row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        ttk.Button(control_frame, text="Очистить", command=self.clear_canvas).grid(
            row=4, column=0, columnspan=2, pady=5, sticky=tk.EW)
        ttk.Button(control_frame, text="Случайные точки", command=self.random_points).grid(
            row=5, column=0, columnspan=2, pady=5, sticky=tk.EW)
        ttk.Button(control_frame, text="Справка", command=self.show_help).grid(
            row=6, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(control_frame, text="Информация", padding=10)
        info_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(20, 0))
        
        self.info_text = tk.Text(info_frame, height=8, width=30, font=("Courier", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Правая панель - холст
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = DrawingCanvas(canvas_frame, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Панель масштабирования
        scale_frame = ttk.Frame(canvas_frame)
        scale_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(scale_frame, text="Масштаб сетки:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.scale_var = tk.DoubleVar(value=1.0)
        scale_slider = ttk.Scale(scale_frame, from_=0.5, to=3.0, variable=self.scale_var, 
                               orient=tk.HORIZONTAL, length=200, command=self.on_scale_changed)
        scale_slider.pack(side=tk.LEFT)
        
        self.scale_label = ttk.Label(scale_frame, text="1.0x")
        self.scale_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def set_default_values(self):
        """Устанавливает значения по умолчанию"""
        self.algorithm_var.set("Алгоритм Брезенхема (отрезок)")
        self.x1_var.set(-10)
        self.y1_var.set(-5)
        self.x2_var.set(10)
        self.y2_var.set(8)
        self.xc_var.set(0)
        self.yc_var.set(0)
        self.r_var.set(8)
        self.on_algorithm_changed()
    
    def on_algorithm_changed(self, event=None):
        """Обработчик изменения выбранного алгоритма"""
        algorithm = self.algorithm_var.get()
        
        if "окружность" in algorithm.lower():
            self.line_frame.grid_remove()
            self.circle_frame.grid()
        else:
            self.circle_frame.grid_remove()
            self.line_frame.grid()
    
    def on_scale_changed(self, value):
        """Обработчик изменения масштаба"""
        self.scale_label.config(text=f"{float(value):.1f}x")
        # В реальном приложении здесь можно было бы изменить масштаб сетки
    
    def execute_algorithm(self):
        """Выполняет выбранный алгоритм"""
        algorithm = self.algorithm_var.get()
        execution_time = 0
        
        try:
            if "окружность" in algorithm.lower():
                xc = self.xc_var.get()
                yc = self.yc_var.get()
                r = self.r_var.get()
                
                if r <= 0:
                    messagebox.showerror("Ошибка", "Радиус должен быть положительным!")
                    return
                
                # Выполнение алгоритма
                start_time = time.perf_counter()
                
                if "Брезенхема" in algorithm:
                    points = self.algorithms.bresenham_circle(xc, yc, r)
                else:
                    points = []
                
                execution_time = time.perf_counter() - start_time
                
                # Очистка и рисование
                self.canvas.clear_drawing()
                self.canvas.draw_circle(xc, yc, r, "purple")
                
                # Рисуем точки
                for x, y in points:
                    self.canvas.draw_pixel(x, y, "purple", 3)
                
                # Вывод информации
                info = f"Алгоритм: Брезенхема (окружность)\n"
                info += f"Центр: ({xc}, {yc})\n"
                info += f"Радиус: {r}\n"
                info += f"Количество точек: {len(points)}\n"
                info += f"Время выполнения: {execution_time:.6f} сек\n"
                
                # Пример вычислений для первых 5 точек
                info += "\nПервые 5 точек:\n"
                for i, (x, y) in enumerate(points[:5]):
                    info += f"  ({x}, {y})\n"
                
            else:
                x1 = self.x1_var.get()
                y1 = self.y1_var.get()
                x2 = self.x2_var.get()
                y2 = self.y2_var.get()
                
                # Выполнение алгоритма
                start_time = time.perf_counter()
                
                if "Пошаговый" in algorithm:
                    points = self.algorithms.step_by_step(x1, y1, x2, y2)
                elif "ЦДА" in algorithm:
                    points = self.algorithms.dda(x1, y1, x2, y2)
                elif "Кастла-Питвея" in algorithm:
                    points = self.algorithms.castle_pitway(x1, y1, x2, y2)
                elif "Ву" in algorithm:
                    points_with_intensity = self.algorithms.wu_line(x1, y1, x2, y2)
                    points = [p for p, _ in points_with_intensity]
                else:
                    points = self.algorithms.bresenham_line(x1, y1, x2, y2)
                
                execution_time = time.perf_counter() - start_time
                
                # Очистка и рисование
                self.canvas.clear_drawing()
                self.canvas.draw_line_between_points(x1, y1, x2, y2, "green")
                
                if "Ву" in algorithm:
                    # Рисуем сглаженную линию
                    self.canvas.draw_wu_line(points_with_intensity, "blue")
                    color = "gray"
                else:
                    color = "red"
                
                # Рисуем точки для обычных алгоритмов
                if "Ву" not in algorithm:
                    for x, y in points:
                        self.canvas.draw_pixel(x, y, color, 3)
                
                # Вывод информации
                info = f"Алгоритм: {algorithm}\n"
                info += f"Точка 1: ({x1}, {y1})\n"
                info += f"Точка 2: ({x2}, {y2})\n"
                info += f"Δx: {x2 - x1}, Δy: {y2 - y1}\n"
                info += f"Количество точек: {len(points)}\n"
                info += f"Время выполнения: {execution_time:.6f} сек\n"
                
                # Пример вычислений
                info += "\nПример вычислений:\n"
                if len(points) >= 3:
                    info += f"  Точка 1: ({points[0][0]}, {points[0][1]})\n"
                    info += f"  Точка 2: ({points[1][0]}, {points[1][1]})\n"
                    info += f"  Точка 3: ({points[2][0]}, {points[2][1]})\n"
            
            # Обновляем информационную панель
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            
            # Сохраняем историю
            self.canvas.points_history.append({
                'algorithm': algorithm,
                'points': points if 'points' in locals() else [],
                'time': execution_time
            })
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения!")
    
    def clear_canvas(self):
        """Очищает холст"""
        self.canvas.clear_drawing()
        self.info_text.delete(1.0, tk.END)
    
    def random_points(self):
        """Генерирует случайные точки"""
        import random
        
        if "окружность" in self.algorithm_var.get().lower():
            self.xc_var.set(random.randint(-15, 15))
            self.yc_var.set(random.randint(-10, 10))
            self.r_var.set(random.randint(3, 12))
        else:
            self.x1_var.set(random.randint(-20, 5))
            self.y1_var.set(random.randint(-15, 5))
            self.x2_var.set(random.randint(5, 20))
            self.y2_var.set(random.randint(5, 15))
        
        self.execute_algorithm()
    
    def show_help(self):
        """Показывает справку"""
        help_text = """
        Визуализация алгоритмов растризации
        
        Доступные алгоритмы:
        1. Пошаговый алгоритм - простейший алгоритм
        2. Алгоритм ЦДА - Digital Differential Analyzer
        3. Алгоритм Брезенхема (отрезок) - целочисленный алгоритм
        4. Алгоритм Брезенхема (окружность) - для рисования окружностей
        5. Алгоритм Кастла-Питвея - модификация Брезенхема
        6. Алгоритм Ву - для сглаживания линий (антиалиасинг)
        
        Использование:
        1. Выберите алгоритм из списка
        2. Введите параметры (координаты точек или центра и радиуса)
        3. Нажмите "Выполнить"
        4. Наблюдайте результат на холсте и вычисления в информационной панели
        
        Особенности:
        • Система координат с центром в середине холста
        • Сетка помогает визуализировать дискретные координаты
        • Каждая ячейка сетки соответствует одному пикселю
        """
        
        messagebox.showinfo("Справка", help_text)

def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = RasterAlgorithmsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()