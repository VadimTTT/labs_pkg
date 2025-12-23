import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import math
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass
import random

@dataclass
class Point:
    x: float
    y: float
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def to_tuple(self):
        return (self.x, self.y)

@dataclass
class LineSegment:
    p1: Point
    p2: Point
    
    def get_parametric(self, t: float) -> Point:
        return self.p1 + (self.p2 - self.p1) * t
    
    def length(self) -> float:
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        return math.sqrt(dx * dx + dy * dy)

class ClippingAlgorithms:
    """Класс с реализацией алгоритмов отсечения"""
    
    @staticmethod
    def compute_code(x: float, y: float, clip_min: Point, clip_max: Point) -> int:
        """Вычисляет код области для точки (алгоритм Сазерленда-Коэна)"""
        code = 0
        
        # Бит 0 - слева
        if x < clip_min.x:
            code |= 1
        # Бит 1 - справа
        elif x > clip_max.x:
            code |= 2
        # Бит 2 - снизу
        if y < clip_min.y:
            code |= 4
        # Бит 3 - сверху
        elif y > clip_max.y:
            code |= 8
            
        return code
    
    @staticmethod
    def cohen_sutherland(line: LineSegment, clip_min: Point, clip_max: Point) -> Optional[LineSegment]:
        """Алгоритм отсечения Сазерленда-Коэна"""
        x1, y1 = line.p1.x, line.p1.y
        x2, y2 = line.p2.x, line.p2.y
        
        # Вычисляем коды концов отрезка
        code1 = ClippingAlgorithms.compute_code(x1, y1, clip_min, clip_max)
        code2 = ClippingAlgorithms.compute_code(x2, y2, clip_min, clip_max)
        
        while True:
            # Отрезок полностью видим
            if code1 == 0 and code2 == 0:
                return LineSegment(Point(x1, y1), Point(x2, y2))
            
            # Отрезок полностью невидим
            if (code1 & code2) != 0:
                return None
            
            # Выбираем точку вне окна
            code_out = code1 if code1 != 0 else code2
            
            # Находим точку пересечения
            x, y = 0.0, 0.0
            
            # Проверяем каждую границу
            if code_out & 8:  # Верхняя граница
                x = x1 + (x2 - x1) * (clip_max.y - y1) / (y2 - y1)
                y = clip_max.y
            elif code_out & 4:  # Нижняя граница
                x = x1 + (x2 - x1) * (clip_min.y - y1) / (y2 - y1)
                y = clip_min.y
            elif code_out & 2:  # Правая граница
                y = y1 + (y2 - y1) * (clip_max.x - x1) / (x2 - x1)
                x = clip_max.x
            elif code_out & 1:  # Левая граница
                y = y1 + (y2 - y1) * (clip_min.x - x1) / (x2 - x1)
                x = clip_min.x
            
            # Заменяем точку вне окна точкой пересечения
            if code_out == code1:
                x1, y1 = x, y
                code1 = ClippingAlgorithms.compute_code(x1, y1, clip_min, clip_max)
            else:
                x2, y2 = x, y
                code2 = ClippingAlgorithms.compute_code(x2, y2, clip_min, clip_max)
    
    @staticmethod
    def liang_barsky(line: LineSegment, clip_min: Point, clip_max: Point) -> Optional[LineSegment]:
        """Алгоритм отсечения Лианга-Барски"""
        x1, y1 = line.p1.x, line.p1.y
        x2, y2 = line.p2.x, line.p2.y
        
        dx = x2 - x1
        dy = y2 - y1
        
        p = [-dx, dx, -dy, dy]
        q = [x1 - clip_min.x, clip_max.x - x1, y1 - clip_min.y, clip_max.y - y1]
        
        u1, u2 = 0.0, 1.0
        
        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return None
                continue
            
            t = q[i] / p[i]
            
            if p[i] < 0:
                if t > u1:
                    u1 = t
            else:
                if t < u2:
                    u2 = t
        
        if u1 > u2:
            return None
        
        new_x1 = x1 + u1 * dx
        new_y1 = y1 + u1 * dy
        new_x2 = x1 + u2 * dx
        new_y2 = y1 + u2 * dy
        
        return LineSegment(Point(new_x1, new_y1), Point(new_x2, new_y2))
    
    @staticmethod
    def midpoint_clipping(line: LineSegment, clip_min: Point, clip_max: Point) -> Optional[LineSegment]:
        """Алгоритм отсечения средней точкой (разделяй и властвуй)"""
        
        def midpoint(x1, y1, x2, y2):
            return ((x1 + x2) / 2, (y1 + y2) / 2)
        
        def is_visible(x1, y1, x2, y2):
            code1 = ClippingAlgorithms.compute_code(x1, y1, clip_min, clip_max)
            code2 = ClippingAlgorithms.compute_code(x2, y2, clip_min, clip_max)
            return code1 == 0 and code2 == 0
        
        def is_invisible(x1, y1, x2, y2):
            code1 = ClippingAlgorithms.compute_code(x1, y1, clip_min, clip_max)
            code2 = ClippingAlgorithms.compute_code(x2, y2, clip_min, clip_max)
            return (code1 & code2) != 0
        
        stack = [(line.p1.x, line.p1.y, line.p2.x, line.p2.y)]
        result_segments = []
        
        epsilon = 0.1  # Точность
        
        while stack:
            x1, y1, x2, y2 = stack.pop()
            
            if is_visible(x1, y1, x2, y2):
                result_segments.append((x1, y1, x2, y2))
                continue
            
            if is_invisible(x1, y1, x2, y2):
                continue
            
            # Если отрезок достаточно короткий, считаем его видимым или невидимым
            if math.hypot(x2 - x1, y2 - y1) < epsilon:
                # Проверяем, находится ли он внутри окна
                if ClippingAlgorithms.compute_code((x1 + x2) / 2, (y1 + y2) / 2, clip_min, clip_max) == 0:
                    result_segments.append((x1, y1, x2, y2))
                continue
            
            # Разделяем отрезок
            mx, my = midpoint(x1, y1, x2, y2)
            stack.append((x1, y1, mx, my))
            stack.append((mx, my, x2, y2))
        
        if not result_segments:
            return None
        
        # Объединяем сегменты
        final_x1, final_y1, final_x2, final_y2 = result_segments[0]
        for i in range(1, len(result_segments)):
            x1, y1, x2, y2 = result_segments[i]
            if abs(final_x2 - x1) < epsilon and abs(final_y2 - y1) < epsilon:
                final_x2, final_y2 = x2, y2
        
        return LineSegment(Point(final_x1, final_y1), Point(final_x2, final_y2))
    
    @staticmethod
    def clip_polygon_weiler_atherton(polygon: List[Point], clip_polygon: List[Point]) -> List[Point]:
        """Алгоритм отсечения многоугольника (Вейлера-Азертона)"""
        if not polygon or len(polygon) < 3:
            return []
        
        # Простая реализация для выпуклого отсекающего многоугольника
        # Используем алгоритм Sutherland-Hodgman
        
        def inside(p: Point, edge_p1: Point, edge_p2: Point) -> bool:
            # Проверяем, находится ли точка p внутри ребра
            # Для выпуклого многоугольника
            return (edge_p2.x - edge_p1.x) * (p.y - edge_p1.y) - (edge_p2.y - edge_p1.y) * (p.x - edge_p1.x) >= 0
        
        def intersection(p1: Point, p2: Point, edge_p1: Point, edge_p2: Point) -> Point:
            # Находим пересечение отрезка p1-p2 с ребром edge_p1-edge_p2
            x1, y1 = p1.x, p1.y
            x2, y2 = p2.x, p2.y
            x3, y3 = edge_p1.x, edge_p1.y
            x4, y4 = edge_p2.x, edge_p2.y
            
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if denom == 0:
                return Point(x1, y1)
            
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            
            return Point(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        
        result = polygon[:]
        
        # Для каждого ребра отсекающего многоугольника
        for i in range(len(clip_polygon)):
            edge_p1 = clip_polygon[i]
            edge_p2 = clip_polygon[(i + 1) % len(clip_polygon)]
            
            input_list = result
            result = []
            
            if not input_list:
                break
            
            s = input_list[-1]
            for p in input_list:
                if inside(p, edge_p1, edge_p2):
                    if not inside(s, edge_p1, edge_p2):
                        result.append(intersection(s, p, edge_p1, edge_p2))
                    result.append(p)
                elif inside(s, edge_p1, edge_p2):
                    result.append(intersection(s, p, edge_p1, edge_p2))
                s = p
        
        return result
    
    @staticmethod
    def clip_line_by_polygon(line: LineSegment, polygon: List[Point]) -> List[LineSegment]:
        """Отсечение отрезка выпуклым многоугольником"""
        if len(polygon) < 3:
            return []
        
        # Используем алгоритм Cyrus-Beck для выпуклых многоугольников
        result = [line]
        
        for i in range(len(polygon)):
            edge_p1 = polygon[i]
            edge_p2 = polygon[(i + 1) % len(polygon)]
            
            new_result = []
            for segment in result:
                # Нормаль к ребру, направленная внутрь многоугольника
                edge_vector = edge_p2 - edge_p1
                normal = Point(-edge_vector.y, edge_vector.x)
                
                # Проверяем ориентацию
                test_point = polygon[(i + 2) % len(polygon)]
                if normal.dot(test_point - edge_p1) < 0:
                    normal = Point(-normal.x, -normal.y)
                
                # Вычисляем параметры
                w = segment.p1 - edge_p1
                d = segment.p2 - segment.p1
                
                n_dot_d = normal.dot(d)
                n_dot_w = normal.dot(w)
                
                if n_dot_d != 0:
                    t = -n_dot_w / n_dot_d
                    if 0 <= t <= 1:
                        intersection_point = segment.p1 + d * t
                        
                        # Разделяем отрезок
                        if n_dot_d > 0:
                            # Отрезок входит внутрь
                            new_result.append(LineSegment(segment.p1, intersection_point))
                        else:
                            # Отрезок выходит наружу
                            new_result.append(LineSegment(intersection_point, segment.p2))
                else:
                    # Параллельно ребру
                    if n_dot_w >= 0:
                        new_result.append(segment)
            
            result = new_result
        
        # Фильтруем отрезки, которые находятся внутри многоугольника
        final_result = []
        for segment in result:
            # Проверяем среднюю точку
            mid_point = segment.get_parametric(0.5)
            if ClippingAlgorithms.is_point_in_polygon(mid_point, polygon):
                final_result.append(segment)
        
        return final_result
    
    @staticmethod
    def is_point_in_polygon(point: Point, polygon: List[Point]) -> bool:
        """Проверка нахождения точки внутри многоугольника (метод ray casting)"""
        if len(polygon) < 3:
            return False
        
        inside = False
        j = len(polygon) - 1
        
        for i in range(len(polygon)):
            pi = polygon[i]
            pj = polygon[j]
            
            if ((pi.y > point.y) != (pj.y > point.y)) and \
               (point.x < (pj.x - pi.x) * (point.y - pi.y) / (pj.y - pi.y) + pi.x):
                inside = not inside
            
            j = i
        
        return inside

class DrawingCanvas(tk.Canvas):
    """Холст для рисования с координатной системой"""
    
    def __init__(self, parent, width=800, height=600, **kwargs):
        super().__init__(parent, width=width, height=height, bg="white", **kwargs)
        self.width = width
        self.height = height
        self.grid_size = 20
        self.origin_x = width // 2
        self.origin_y = height // 2
        self.scale_factor = 1.0
        
        # Данные
        self.lines = []
        self.polygons = []
        self.clip_window = None
        self.clip_polygon = []
        self.clipped_lines = []
        self.clipped_polygons = []
        
        # Цвета
        self.colors = {
            'clip_window': 'red',
            'clip_polygon': 'purple',
            'original_lines': 'blue',
            'original_polygons': 'green',
            'clipped_lines': 'orange',
            'clipped_polygons': 'darkgreen'
        }
        
        self.draw_coordinate_system()
    
    def draw_coordinate_system(self):
        """Рисует координатную систему"""
        self.delete("grid")
        
        # Сетка
        for x in range(0, self.width, self.grid_size):
            self.create_line(x, 0, x, self.height, fill="#f0f0f0", tags="grid", width=1)
        for y in range(0, self.height, self.grid_size):
            self.create_line(0, y, self.width, y, fill="#f0f0f0", tags="grid", width=1)
        
        # Оси
        self.create_line(0, self.origin_y, self.width, self.origin_y, 
                        fill="black", width=2, arrow=tk.LAST, tags="axes")
        self.create_line(self.origin_x, self.height, self.origin_x, 0, 
                        fill="black", width=2, arrow=tk.LAST, tags="axes")
        
        # Подписи
        self.create_text(self.width - 10, self.origin_y - 10, text="X", 
                        fill="black", font=("Arial", 12, "bold"), tags="axes")
        self.create_text(self.origin_x + 10, 10, text="Y", 
                        fill="black", font=("Arial", 12, "bold"), tags="axes")
        
        # Подписи сетки
        for i in range(-self.origin_x//self.grid_size, (self.width-self.origin_x)//self.grid_size):
            x = self.origin_x + i * self.grid_size
            if i != 0 and x > 0 and x < self.width:
                self.create_text(x, self.origin_y + 10, text=str(i), 
                               fill="gray", font=("Arial", 8), tags="grid_labels")
        
        for i in range(-self.origin_y//self.grid_size, (self.height-self.origin_y)//self.grid_size):
            y = self.origin_y - i * self.grid_size
            if i != 0 and y > 0 and y < self.height:
                self.create_text(self.origin_x - 10, y, text=str(i), 
                               fill="gray", font=("Arial", 8), tags="grid_labels")
    
    def clear_all(self):
        """Очищает все данные и рисунки"""
        self.delete("all")
        self.lines.clear()
        self.polygons.clear()
        self.clip_window = None
        self.clip_polygon.clear()
        self.clipped_lines.clear()
        self.clipped_polygons.clear()
        self.draw_coordinate_system()
    
    def world_to_screen(self, point: Point) -> Tuple[float, float]:
        """Преобразует мировые координаты в экранные"""
        screen_x = self.origin_x + point.x * self.grid_size * self.scale_factor
        screen_y = self.origin_y - point.y * self.grid_size * self.scale_factor
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Point:
        """Преобразует экранные координаты в мировые"""
        world_x = (screen_x - self.origin_x) / (self.grid_size * self.scale_factor)
        world_y = (self.origin_y - screen_y) / (self.grid_size * self.scale_factor)
        return Point(world_x, world_y)
    
    def draw_line(self, line: LineSegment, color: str, width: int = 2, tags: str = ""):
        """Рисует отрезок"""
        x1, y1 = self.world_to_screen(line.p1)
        x2, y2 = self.world_to_screen(line.p2)
        
        self.create_line(x1, y1, x2, y2, fill=color, width=width, tags=tags)
    
    def draw_polygon(self, polygon: List[Point], color: str, width: int = 2, fill: str = "", tags: str = ""):
        """Рисует многоугольник"""
        if len(polygon) < 2:
            return
        
        screen_points = [self.world_to_screen(p) for p in polygon]
        
        if len(polygon) == 2:
            self.create_line(screen_points[0][0], screen_points[0][1],
                           screen_points[1][0], screen_points[1][1],
                           fill=color, width=width, tags=tags)
        else:
            self.create_polygon(screen_points, fill=fill, outline=color, width=width, tags=tags)
    
    def draw_point(self, point: Point, color: str, size: int = 3, tags: str = ""):
        """Рисует точку"""
        x, y = self.world_to_screen(point)
        self.create_oval(x - size, y - size, x + size, y + size,
                        fill=color, outline=color, tags=tags)
    
    def draw_rectangle(self, min_point: Point, max_point: Point, color: str, width: int = 2, tags: str = ""):
        """Рисует прямоугольник"""
        x1, y1 = self.world_to_screen(min_point)
        x2, y2 = self.world_to_screen(max_point)
        
        self.create_rectangle(x1, y1, x2, y2, outline=color, width=width, tags=tags)
    
    def redraw_all(self):
        """Перерисовывает все объекты"""
        self.delete("all")
        self.draw_coordinate_system()
        
        # Отсекающее окно
        if self.clip_window:
            min_point, max_point = self.clip_window
            self.draw_rectangle(min_point, max_point, self.colors['clip_window'], 2, "clip_window")
        
        # Отсекающий многоугольник
        if self.clip_polygon:
            self.draw_polygon(self.clip_polygon, self.colors['clip_polygon'], 2, "", "clip_polygon")
        
        # Исходные отрезки
        for line in self.lines:
            self.draw_line(line, self.colors['original_lines'], 2, "original")
            self.draw_point(line.p1, self.colors['original_lines'], 3, "original")
            self.draw_point(line.p2, self.colors['original_lines'], 3, "original")
        
        # Исходные многоугольники
        for polygon in self.polygons:
            if len(polygon) >= 3:
                self.draw_polygon(polygon, self.colors['original_polygons'], 2, "", "original")
        
        # Отсеченные отрезки
        for line in self.clipped_lines:
            self.draw_line(line, self.colors['clipped_lines'], 3, "clipped")
            self.draw_point(line.p1, self.colors['clipped_lines'], 4, "clipped")
            self.draw_point(line.p2, self.colors['clipped_lines'], 4, "clipped")
        
        # Отсеченные многоугольники
        for polygon in self.clipped_polygons:
            if len(polygon) >= 3:
                self.draw_polygon(polygon, self.colors['clipped_polygons'], 3, "#a0ffa0", "clipped")

class ClippingApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация алгоритмов отсечения")
        self.root.geometry("1400x800")
        
        # Инициализация алгоритмов
        self.algorithms = ClippingAlgorithms()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Установка значений по умолчанию
        self.set_default_values()
        
        # Создание меню
        self.create_menu()
    
    def create_widgets(self):
        """Создает все виджеты интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - управление
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding=10, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # Вкладки
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка 1: Отсечение отрезков
        tab_lines = ttk.Frame(notebook)
        notebook.add(tab_lines, text="Отсечение отрезков")
        self.create_lines_tab(tab_lines)
        
        # Вкладка 2: Отсечение многоугольников
        tab_polygons = ttk.Frame(notebook)
        notebook.add(tab_polygons, text="Отсечение многоугольников")
        self.create_polygons_tab(tab_polygons)
        
        # Вкладка 3: Файлы
        tab_files = ttk.Frame(notebook)
        notebook.add(tab_files, text="Файлы")
        self.create_files_tab(tab_files)
        
        # Правая панель - холст и информация
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Холст (СНАЧАЛА создаем холст!)
        canvas_frame = ttk.LabelFrame(right_frame, text="Визуализация", padding=5)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = DrawingCanvas(canvas_frame, width=900, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Панель быстрого доступа (ПОСЛЕ создания холста!)
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="🗑️ Все", command=self.clear_all, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📏 Отрезки", command=self.clear_lines, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⬡ Многоуг.", command=self.clear_polygons, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✂️ Результаты", command=self.clear_results, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Обновить", command=self.canvas.redraw_all, width=8).pack(side=tk.LEFT, padx=2)
        
        # Панель информации
        info_frame = ttk.LabelFrame(right_frame, text="Информация", padding=10)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, font=("Courier", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Панель масштабирования
        scale_frame = ttk.Frame(right_frame)
        scale_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(scale_frame, text="Масштаб:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.scale_var = tk.DoubleVar(value=1.0)
        scale_slider = ttk.Scale(scale_frame, from_=0.5, to=3.0, variable=self.scale_var,
                               orient=tk.HORIZONTAL, length=200, command=self.on_scale_changed)
        scale_slider.pack(side=tk.LEFT)
        
        self.scale_label = ttk.Label(scale_frame, text="1.0x")
        self.scale_label.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(scale_frame, text="Очистить всё", command=self.clear_all).pack(side=tk.RIGHT)
    
    def create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить файл", command=self.load_file)
        file_menu.add_command(label="Сохранить изображение", command=self.save_image)
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Очистить всё", command=self.clear_all)
        edit_menu.add_command(label="Очистить отрезки", command=self.clear_lines)
        edit_menu.add_command(label="Очистить многоугольники", command=self.clear_polygons)
        edit_menu.add_command(label="Очистить результаты", command=self.clear_results)
        edit_menu.add_separator()
        edit_menu.add_command(label="Отсекающее окно по умолчанию", command=self.set_clip_window)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Горячие клавиши
        self.root.bind('<Control-l>', lambda e: self.clear_lines())
        self.root.bind('<Control-p>', lambda e: self.clear_polygons())
        self.root.bind('<Control-r>', lambda e: self.clear_results())
        self.root.bind('<Control-a>', lambda e: self.clear_all())
        self.root.bind('<Delete>', lambda e: self.clear_results())
    
    def create_lines_tab(self, parent):
        """Создает вкладку для отсечения отрезков"""
        # Алгоритм
        ttk.Label(parent, text="Алгоритм:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.line_algorithm_var = tk.StringVar()
        algorithms = [
            "Сазерленда-Коэна",
            "Лианга-Барски",
            "Средней точки"
        ]
        
        algorithm_combo = ttk.Combobox(parent, textvariable=self.line_algorithm_var,
                                     values=algorithms, state="readonly", width=20)
        algorithm_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Отсекающее окно
        ttk.Label(parent, text="Отсекающее окно:").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(parent, text="Xmin:").grid(row=2, column=0, sticky=tk.W)
        self.xmin_var = tk.DoubleVar()
        ttk.Entry(parent, textvariable=self.xmin_var, width=10).grid(row=2, column=1, padx=(5, 10), sticky=tk.W)
        
        ttk.Label(parent, text="Ymin:").grid(row=3, column=0, sticky=tk.W)
        self.ymin_var = tk.DoubleVar()
        ttk.Entry(parent, textvariable=self.ymin_var, width=10).grid(row=3, column=1, padx=(5, 10), sticky=tk.W)
        
        ttk.Label(parent, text="Xmax:").grid(row=4, column=0, sticky=tk.W)
        self.xmax_var = tk.DoubleVar()
        ttk.Entry(parent, textvariable=self.xmax_var, width=10).grid(row=4, column=1, padx=(5, 10), sticky=tk.W)
        
        ttk.Label(parent, text="Ymax:").grid(row=5, column=0, sticky=tk.W)
        self.ymax_var = tk.DoubleVar()
        ttk.Entry(parent, textvariable=self.ymax_var, width=10).grid(row=5, column=1, padx=(5, 10), sticky=tk.W)
        
        # Управление
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky=tk.EW)
        
        ttk.Button(button_frame, text="Установить окно", command=self.set_clip_window).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Добавить отрезок", command=self.add_line_dialog).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Случайные отрезки", command=self.generate_random_lines).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Выполнить отсечение", command=self.execute_line_clipping).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Очистить отрезки", command=self.clear_lines).pack(fill=tk.X, pady=2)
        
        # Статистика
        ttk.Label(parent, text="Статистика:").grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.stats_text = tk.Text(parent, height=6, width=30, font=("Courier", 8))
        self.stats_text.grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=5)
    
    def create_polygons_tab(self, parent):
        """Создает вкладку для отсечения многоугольников"""
        # Тип отсечения
        ttk.Label(parent, text="Тип отсечения:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.polygon_clip_type_var = tk.StringVar()
        types = [
            "Отрезок выпуклым многоугольником",
            "Выпуклый многоугольник"
        ]
        
        type_combo = ttk.Combobox(parent, textvariable=self.polygon_clip_type_var,
                                values=types, state="readonly", width=25)
        type_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Отсекающий многоугольник
        ttk.Label(parent, text="Отсекающий многоугольник:").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.clip_polygon_points = []
        self.clip_polygon_text = tk.Text(parent, height=5, width=30, font=("Courier", 8))
        self.clip_polygon_text.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        polygon_frame = ttk.Frame(parent)
        polygon_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        ttk.Button(polygon_frame, text="Добавить точку", command=self.add_clip_polygon_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(polygon_frame, text="Очистить", command=self.clear_clip_polygon).pack(side=tk.LEFT, padx=2)
        ttk.Button(polygon_frame, text="Случайный", command=self.generate_random_clip_polygon).pack(side=tk.LEFT, padx=2)
        
        # Управление
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky=tk.EW)
        
        ttk.Button(button_frame, text="Добавить многоугольник", command=self.add_polygon_dialog).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Случайные многоугольники", command=self.generate_random_polygons).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Выполнить отсечение", command=self.execute_polygon_clipping).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Очистить многоугольники", command=self.clear_polygons).pack(fill=tk.X, pady=2)
    
    def create_files_tab(self, parent):
        """Создает вкладку для работы с файлами"""
        # Загрузка файла
        ttk.Label(parent, text="Загрузка из файла:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.file_text = scrolledtext.ScrolledText(parent, height=15, width=35, font=("Courier", 8))
        self.file_text.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        file_button_frame = ttk.Frame(parent)
        file_button_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        ttk.Button(file_button_frame, text="Загрузить файл", command=self.load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="Пример данных", command=self.load_example_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="Очистить файл", command=self.clear_file_text).pack(side=tk.LEFT, padx=2)
        
        # Формат файла
        ttk.Label(parent, text="Формат файла:").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        format_text = """n                      # количество отрезков
x1 y1 x2 y2            # координаты первого отрезка
x1 y1 x2 y2            # координаты второго отрезка
...
x1 y1 x2 y2            # координаты n-го отрезка
xmin ymin xmax ymax    # координаты отсекающего окна"""
        
        format_label = tk.Text(parent, height=6, width=35, font=("Courier", 8), bg="#f0f0f0")
        format_label.insert(1.0, format_text)
        format_label.config(state=tk.DISABLED)
        format_label.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Сохранение
        ttk.Label(parent, text="Сохранение результатов:").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        save_button_frame = ttk.Frame(parent)
        save_button_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        ttk.Button(save_button_frame, text="Сохранить изображение", command=self.save_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(save_button_frame, text="Экспорт данных", command=self.export_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(save_button_frame, text="Очистить всё", command=self.clear_all).pack(side=tk.LEFT, padx=2)
    
    def set_default_values(self):
        """Устанавливает значения по умолчанию"""
        self.line_algorithm_var.set("Сазерленда-Коэна")
        self.polygon_clip_type_var.set("Выпуклый многоугольник")
        
        self.xmin_var.set(-10.0)
        self.ymin_var.set(-8.0)
        self.xmax_var.set(10.0)
        self.ymax_var.set(8.0)
        
        # Устанавливаем отсекающее окно по умолчанию
        self.set_clip_window()
        
        # Создаем пример отсекающего многоугольника
        self.clip_polygon_points = [
            Point(-8, -6),
            Point(-8, 6),
            Point(8, 6),
            Point(8, -6)
        ]
        self.update_clip_polygon_text()
    
    def on_scale_changed(self, value):
        """Обработчик изменения масштаба"""
        self.canvas.scale_factor = float(value)
        self.scale_label.config(text=f"{float(value):.1f}x")
        self.canvas.redraw_all()
    
    def clear_all(self):
        """Очищает все данные с подтверждением"""
        if messagebox.askyesno("Подтверждение", "Очистить все данные?\nЭто удалит все отрезки, многоугольники и результаты."):
            # Очищаем холст
            self.canvas.clear_all()
            
            # Очищаем текстовые поля
            self.info_text.delete(1.0, tk.END)
            
            if hasattr(self, 'stats_text'):
                self.stats_text.delete(1.0, tk.END)
            
            if hasattr(self, 'file_text'):
                self.file_text.delete(1.0, tk.END)
            
            # Восстанавливаем отсекающее окно по умолчанию
            self.set_clip_window()
            
            # Восстанавливаем отсекающий многоугольник по умолчанию
            self.clip_polygon_points = [
                Point(-8, -6),
                Point(-8, 6),
                Point(8, 6),
                Point(8, -6)
            ]
            self.update_clip_polygon_text()
            
            self.info_text.insert(tk.END, "Все данные очищены\n")
    
    def clear_lines(self):
        """Очищает только отрезки"""
        self.canvas.lines.clear()
        self.canvas.clipped_lines.clear()
        self.canvas.redraw_all()
        self.info_text.insert(tk.END, "Все отрезки очищены\n")
        
        # Очищаем статистику
        if hasattr(self, 'stats_text'):
            self.stats_text.delete(1.0, tk.END)

    def clear_polygons(self):
        """Очищает только многоугольники"""
        self.canvas.polygons.clear()
        self.canvas.clipped_polygons.clear()
        self.canvas.redraw_all()
        self.info_text.insert(tk.END, "Все многоугольники очищены\n")
    
    def clear_results(self):
        """Очищает только результаты отсечения"""
        self.canvas.clipped_lines.clear()
        self.canvas.clipped_polygons.clear()
        self.canvas.redraw_all()
        self.info_text.insert(tk.END, "Результаты отсечения очищены\n")
    
    def clear_file_text(self):
        """Очищает текстовое поле файла"""
        self.file_text.delete(1.0, tk.END)
    
    def set_clip_window(self):
        """Устанавливает отсекающее окно"""
        try:
            xmin = self.xmin_var.get()
            ymin = self.ymin_var.get()
            xmax = self.xmax_var.get()
            ymax = self.ymax_var.get()
            
            if xmin >= xmax or ymin >= ymax:
                messagebox.showerror("Ошибка", "Некорректные границы окна!")
                return
            
            self.canvas.clip_window = (Point(xmin, ymin), Point(xmax, ymax))
            self.canvas.redraw_all()
            self.info_text.insert(tk.END, f"Отсекающее окно установлено: ({xmin}, {ymin}) - ({xmax}, {ymax})\n")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовые значения!")
    
    def add_line_dialog(self):
        """Диалог добавления отрезка"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить отрезок")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Начальная точка:").grid(row=0, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Label(dialog, text="X1:").grid(row=1, column=0, padx=5, pady=5)
        x1_var = tk.DoubleVar(value=0.0)
        ttk.Entry(dialog, textvariable=x1_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Y1:").grid(row=2, column=0, padx=5, pady=5)
        y1_var = tk.DoubleVar(value=0.0)
        ttk.Entry(dialog, textvariable=y1_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Конечная точка:").grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Label(dialog, text="X2:").grid(row=4, column=0, padx=5, pady=5)
        x2_var = tk.DoubleVar(value=5.0)
        ttk.Entry(dialog, textvariable=x2_var, width=10).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Y2:").grid(row=5, column=0, padx=5, pady=5)
        y2_var = tk.DoubleVar(value=5.0)
        ttk.Entry(dialog, textvariable=y2_var, width=10).grid(row=5, column=1, padx=5, pady=5)
        
        def add_line():
            try:
                line = LineSegment(
                    Point(x1_var.get(), y1_var.get()),
                    Point(x2_var.get(), y2_var.get())
                )
                self.canvas.lines.append(line)
                self.canvas.redraw_all()
                self.info_text.insert(tk.END, f"Добавлен отрезок: ({x1_var.get()}, {y1_var.get()}) - ({x2_var.get()}, {y2_var.get()})\n")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите числовые значения!")
        
        ttk.Button(dialog, text="Добавить", command=add_line).grid(row=6, column=0, columnspan=2, pady=20)
    
    def generate_random_lines(self):
        """Генерирует случайные отрезки"""
        try:
            num_lines = 10
            self.canvas.lines.clear()
            
            for _ in range(num_lines):
                x1 = random.uniform(-15, 15)
                y1 = random.uniform(-12, 12)
                x2 = random.uniform(-15, 15)
                y2 = random.uniform(-12, 12)
                
                line = LineSegment(Point(x1, y1), Point(x2, y2))
                self.canvas.lines.append(line)
            
            self.canvas.redraw_all()
            self.info_text.insert(tk.END, f"Сгенерировано {num_lines} случайных отрезков\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации: {str(e)}")
    
    def execute_line_clipping(self):
        """Выполняет отсечение отрезков"""
        if not self.canvas.clip_window:
            messagebox.showwarning("Предупреждение", "Сначала установите отсекающее окно!")
            return
        
        if not self.canvas.lines:
            messagebox.showwarning("Предупреждение", "Нет отрезков для отсечения!")
            return
        
        clip_min, clip_max = self.canvas.clip_window
        algorithm_name = self.line_algorithm_var.get()
        
        self.canvas.clipped_lines.clear()
        
        start_time = time.perf_counter()
        
        for line in self.canvas.lines:
            if algorithm_name == "Сазерленда-Коэна":
                clipped = self.algorithms.cohen_sutherland(line, clip_min, clip_max)
            elif algorithm_name == "Лианга-Барски":
                clipped = self.algorithms.liang_barsky(line, clip_min, clip_max)
            elif algorithm_name == "Средней точки":
                clipped = self.algorithms.midpoint_clipping(line, clip_min, clip_max)
            else:
                clipped = None
            
            if clipped:
                self.canvas.clipped_lines.append(clipped)
        
        execution_time = time.perf_counter() - start_time
        
        # Обновляем отображение
        self.canvas.redraw_all()
        
        # Вывод информации
        self.info_text.delete(1.0, tk.END)
        info = f"Алгоритм: {algorithm_name}\n"
        info += f"Отсекающее окно: ({clip_min.x}, {clip_min.y}) - ({clip_max.x}, {clip_max.y})\n"
        info += f"Всего отрезков: {len(self.canvas.lines)}\n"
        info += f"Видимых отрезков: {len(self.canvas.clipped_lines)}\n"
        info += f"Время выполнения: {execution_time:.6f} сек\n\n"
        
        # Пример вычислений для первого отрезка
        if self.canvas.lines:
            info += "Пример вычислений для первого отрезка:\n"
            line = self.canvas.lines[0]
            info += f"Исходный: ({line.p1.x:.1f}, {line.p1.y:.1f}) - ({line.p2.x:.1f}, {line.p2.y:.1f})\n"
            
            if self.canvas.clipped_lines and len(self.canvas.clipped_lines) > 0:
                clipped = self.canvas.clipped_lines[0]
                info += f"Результат: ({clipped.p1.x:.1f}, {clipped.p1.y:.1f}) - ({clipped.p2.x:.1f}, {clipped.p2.y:.1f})\n"
            else:
                info += "Результат: полностью отсечен\n"
        
        self.info_text.insert(1.0, info)
        
        # Обновляем статистику
        if hasattr(self, 'stats_text'):
            self.stats_text.delete(1.0, tk.END)
            stats = f"Статистика:\n"
            stats += f"Алгоритм: {algorithm_name}\n"
            stats += f"Время: {execution_time:.6f} сек\n"
            stats += f"Эффективность: {len(self.canvas.clipped_lines)/len(self.canvas.lines)*100:.1f}%\n"
            stats += f"Отсечено: {len(self.canvas.lines) - len(self.canvas.clipped_lines)}\n"
            self.stats_text.insert(1.0, stats)
    
    def update_clip_polygon_text(self):
        """Обновляет текст отсекающего многоугольника"""
        self.clip_polygon_text.delete(1.0, tk.END)
        for point in self.clip_polygon_points:
            self.clip_polygon_text.insert(tk.END, f"({point.x:.1f}, {point.y:.1f})\n")
        
        # Обновляем на холсте
        self.canvas.clip_polygon = self.clip_polygon_points[:]
        self.canvas.redraw_all()
    
    def add_clip_polygon_point(self):
        """Добавляет точку в отсекающий многоугольник"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить точку")
        dialog.geometry("250x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Координаты точки:").pack(pady=(10, 0))
        
        frame = ttk.Frame(dialog)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="X:").grid(row=0, column=0, padx=5)
        x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=x_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(frame, text="Y:").grid(row=1, column=0, padx=5, pady=5)
        y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=y_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        def add_point():
            try:
                point = Point(x_var.get(), y_var.get())
                self.clip_polygon_points.append(point)
                self.update_clip_polygon_text()
                self.info_text.insert(tk.END, f"Добавлена точка: ({x_var.get()}, {y_var.get()})\n")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите числовые значения!")
        
        ttk.Button(dialog, text="Добавить", command=add_point).pack(pady=10)
    
    def clear_clip_polygon(self):
        """Очищает отсекающий многоугольник"""
        self.clip_polygon_points.clear()
        self.update_clip_polygon_text()
        self.info_text.insert(tk.END, "Отсекающий многоугольник очищен\n")
    
    def generate_random_clip_polygon(self):
        """Генерирует случайный отсекающий многоугольник"""
        self.clip_polygon_points.clear()
        
        # Создаем выпуклый многоугольник
        num_points = random.randint(3, 8)
        center_x = random.uniform(-5, 5)
        center_y = random.uniform(-4, 4)
        radius = random.uniform(3, 8)
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.clip_polygon_points.append(Point(x, y))
        
        self.update_clip_polygon_text()
        self.info_text.insert(tk.END, f"Сгенерирован {num_points}-угольник\n")
    
    def add_polygon_dialog(self):
        """Диалог добавления многоугольника"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить многоугольник")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Введите точки многоугольника (по одной в строке):").pack(pady=(10, 5))
        
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        polygon_text = scrolledtext.ScrolledText(text_frame, height=10, width=30, font=("Courier", 9))
        polygon_text.pack(fill=tk.BOTH, expand=True)
        polygon_text.insert(1.0, "0 0\n5 0\n5 5\n0 5")
        
        def add_polygon():
            try:
                points = []
                text = polygon_text.get(1.0, tk.END).strip()
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            x = float(parts[0])
                            y = float(parts[1])
                            points.append(Point(x, y))
                
                if len(points) >= 3:
                    self.canvas.polygons.append(points)
                    self.canvas.redraw_all()
                    self.info_text.insert(tk.END, f"Добавлен многоугольник с {len(points)} точками\n")
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Многоугольник должен иметь хотя бы 3 точки!")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат данных!")
        
        ttk.Button(dialog, text="Добавить", command=add_polygon).pack(pady=10)
    
    def generate_random_polygons(self):
        """Генерирует случайные многоугольники"""
        try:
            num_polygons = 3
            self.canvas.polygons.clear()
            
            for _ in range(num_polygons):
                num_points = random.randint(3, 6)
                center_x = random.uniform(-10, 10)
                center_y = random.uniform(-8, 8)
                radius = random.uniform(2, 5)
                
                points = []
                for i in range(num_points):
                    angle = 2 * math.pi * i / num_points
                    x = center_x + radius * math.cos(angle) + random.uniform(-1, 1)
                    y = center_y + radius * math.sin(angle) + random.uniform(-1, 1)
                    points.append(Point(x, y))
                
                self.canvas.polygons.append(points)
            
            self.canvas.redraw_all()
            self.info_text.insert(tk.END, f"Сгенерировано {num_polygons} случайных многоугольников\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации: {str(e)}")
    
    def execute_polygon_clipping(self):
        """Выполняет отсечение многоугольников"""
        clip_type = self.polygon_clip_type_var.get()
        
        if clip_type == "Выпуклый многоугольник":
            self.execute_polygon_by_polygon_clipping()
        else:
            self.execute_line_by_polygon_clipping()
    
    def execute_polygon_by_polygon_clipping(self):
        """Отсечение многоугольника многоугольником"""
        if not self.clip_polygon_points or len(self.clip_polygon_points) < 3:
            messagebox.showwarning("Предупреждение", "Задайте отсекающий многоугольник!")
            return
        
        if not self.canvas.polygons:
            messagebox.showwarning("Предупреждение", "Нет многоугольников для отсечения!")
            return
        
        self.canvas.clipped_polygons.clear()
        
        start_time = time.perf_counter()
        
        for polygon in self.canvas.polygons:
            if len(polygon) >= 3:
                clipped = self.algorithms.clip_polygon_weiler_atherton(polygon, self.clip_polygon_points)
                if clipped:
                    self.canvas.clipped_polygons.append(clipped)
        
        execution_time = time.perf_counter() - start_time
        
        # Обновляем отображение
        self.canvas.redraw_all()
        
        # Вывод информации
        self.info_text.delete(1.0, tk.END)
        info = f"Алгоритм: Вейлера-Азертона\n"
        info += f"Отсекающий многоугольник: {len(self.clip_polygon_points)} точек\n"
        info += f"Всего многоугольников: {len(self.canvas.polygons)}\n"
        info += f"Результатов: {len(self.canvas.clipped_polygons)}\n"
        info += f"Время выполнения: {execution_time:.6f} сек\n\n"
        
        # Пример вычислений
        if self.canvas.polygons and len(self.canvas.polygons) > 0:
            polygon = self.canvas.polygons[0]
            info += f"Первый многоугольник ({len(polygon)} точек):\n"
            for i, point in enumerate(polygon[:3]):
                info += f"  P{i}: ({point.x:.1f}, {point.y:.1f})\n"
            info += "  ...\n"
        
        self.info_text.insert(1.0, info)
    
    def execute_line_by_polygon_clipping(self):
        """Отсечение отрезков выпуклым многоугольником"""
        if not self.clip_polygon_points or len(self.clip_polygon_points) < 3:
            messagebox.showwarning("Предупреждение", "Задайте отсекающий многоугольник!")
            return
        
        if not self.canvas.lines:
            messagebox.showwarning("Предупреждение", "Нет отрезков для отсечения!")
            return
        
        self.canvas.clipped_lines.clear()
        
        start_time = time.perf_counter()
        
        for line in self.canvas.lines:
            clipped_segments = self.algorithms.clip_line_by_polygon(line, self.clip_polygon_points)
            self.canvas.clipped_lines.extend(clipped_segments)
        
        execution_time = time.perf_counter() - start_time
        
        # Обновляем отображение
        self.canvas.redraw_all()
        
        # Вывод информации
        self.info_text.delete(1.0, tk.END)
        info = f"Алгоритм: Cyrus-Beck\n"
        info += f"Отсекающий многоугольник: {len(self.clip_polygon_points)} точек\n"
        info += f"Всего отрезков: {len(self.canvas.lines)}\n"
        info += f"Результатов: {len(self.canvas.clipped_lines)}\n"
        info += f"Время выполнения: {execution_time:.6f} сек\n\n"
        
        # Пример вычислений
        if self.canvas.lines and len(self.canvas.lines) > 0:
            line = self.canvas.lines[0]
            info += f"Первый отрезок:\n"
            info += f"  Начало: ({line.p1.x:.1f}, {line.p1.y:.1f})\n"
            info += f"  Конец: ({line.p2.x:.1f}, {line.p2.y:.1f})\n"
        
        self.info_text.insert(1.0, info)
    
    def load_file(self):
        """Загружает данные из файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as file:
                content = file.read()
                self.file_text.delete(1.0, tk.END)
                self.file_text.insert(1.0, content)
                
                # Парсинг данных
                lines = content.strip().split('\n')
                if len(lines) < 2:
                    messagebox.showerror("Ошибка", "Некорректный формат файла!")
                    return
                
                # Очищаем текущие данные
                self.canvas.lines.clear()
                self.canvas.polygons.clear()
                
                # Читаем количество отрезков
                try:
                    n = int(lines[0].strip())
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректное количество отрезков!")
                    return
                
                # Читаем отрезки
                for i in range(1, min(n + 1, len(lines))):
                    parts = lines[i].strip().split()
                    if len(parts) >= 4:
                        try:
                            x1 = float(parts[0])
                            y1 = float(parts[1])
                            x2 = float(parts[2])
                            y2 = float(parts[3])
                            line = LineSegment(Point(x1, y1), Point(x2, y2))
                            self.canvas.lines.append(line)
                        except ValueError:
                            continue
                
                # Читаем отсекающее окно (последняя строка)
                if len(lines) > n + 1:
                    parts = lines[n + 1].strip().split()
                    if len(parts) >= 4:
                        try:
                            xmin = float(parts[0])
                            ymin = float(parts[1])
                            xmax = float(parts[2])
                            ymax = float(parts[3])
                            
                            self.xmin_var.set(xmin)
                            self.ymin_var.set(ymin)
                            self.xmax_var.set(xmax)
                            self.ymax_var.set(ymax)
                            self.set_clip_window()
                        except ValueError:
                            pass
                
                self.canvas.redraw_all()
                self.info_text.insert(tk.END, f"Загружен файл: {filename}\n")
                self.info_text.insert(tk.END, f"Загружено отрезков: {len(self.canvas.lines)}\n")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {str(e)}")
    
    def load_example_data(self):
        """Загружает пример данных"""
        example = """5
-15 -5 15 5
-10 10 10 -10
5 -15 5 15
-8 -8 8 8
-12 0 12 0
-10 -8 10 8"""
        
        self.file_text.delete(1.0, tk.END)
        self.file_text.insert(1.0, example)
        
        # Парсинг примера
        lines = example.strip().split('\n')
        n = int(lines[0].strip())
        
        self.canvas.lines.clear()
        
        for i in range(1, n + 1):
            parts = lines[i].strip().split()
            if len(parts) >= 4:
                x1 = float(parts[0])
                y1 = float(parts[1])
                x2 = float(parts[2])
                y2 = float(parts[3])
                line = LineSegment(Point(x1, y1), Point(x2, y2))
                self.canvas.lines.append(line)
        
        # Отсекающее окно
        if len(lines) > n + 1:
            parts = lines[n + 1].strip().split()
            if len(parts) >= 4:
                xmin = float(parts[0])
                ymin = float(parts[1])
                xmax = float(parts[2])
                ymax = float(parts[3])
                
                self.xmin_var.set(xmin)
                self.ymin_var.set(ymin)
                self.xmax_var.set(xmax)
                self.ymax_var.set(ymax)
                self.set_clip_window()
        
        self.canvas.redraw_all()
        self.info_text.insert(tk.END, "Загружен пример данных\n")
    
    def save_image(self):
        """Сохраняет изображение с холста"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".eps",
            filetypes=[("EPS files", "*.eps"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.canvas.postscript(file=filename, colormode='color')
                self.info_text.insert(tk.END, f"Изображение сохранено: {filename}\n")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def export_data(self):
        """Экспортирует данные"""
        filename = filedialog.asksaveasfilename(
            title="Экспорт данных",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as file:
                    # Исходные отрезки
                    file.write(f"{len(self.canvas.lines)}\n")
                    for line in self.canvas.lines:
                        file.write(f"{line.p1.x} {line.p1.y} {line.p2.x} {line.p2.y}\n")
                    
                    # Отсекающее окно
                    if self.canvas.clip_window:
                        clip_min, clip_max = self.canvas.clip_window
                        file.write(f"{clip_min.x} {clip_min.y} {clip_max.x} {clip_max.y}\n")
                    
                    # Результаты отсечения
                    file.write(f"\n# Результаты отсечения: {len(self.canvas.clipped_lines)} отрезков\n")
                    for line in self.canvas.clipped_lines:
                        file.write(f"{line.p1.x} {line.p1.y} {line.p2.x} {line.p2.y}\n")
                
                self.info_text.insert(tk.END, f"Данные экспортированы: {filename}\n")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def show_about(self):
        """Показывает окно 'О программе'"""
        about_text = """Визуализация алгоритмов отсечения

Версия 1.0

Реализованные алгоритмы:
• Сазерленда-Коэна
• Лианга-Барски
• Средней точки
• Cyrus-Beck
• Вейлера-Азертона

Для учебных целей по компьютерной графике

Управление очисткой:
• Ctrl+A - очистить всё
• Ctrl+L - очистить отрезки
• Ctrl+P - очистить многоугольники
• Ctrl+R или Delete - очистить результаты"""
        
        messagebox.showinfo("О программе", about_text)

def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = ClippingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()