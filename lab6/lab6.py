import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import numpy as np
import json

class Vector3D:
    """Класс для работы с 3D векторами"""
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return self / length
        return Vector3D()
    
    def to_array(self):
        return [self.x, self.y, self.z]
    
    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    @staticmethod
    def from_array(arr):
        return Vector3D(arr[0], arr[1], arr[2])

class Matrix4x4:
    """Класс для работы с матрицами 4x4 (для 3D преобразований)"""
    def __init__(self, matrix=None):
        if matrix is None:
            self.matrix = np.identity(4, dtype=float)
        else:
            self.matrix = np.array(matrix, dtype=float)
    
    @staticmethod
    def translation(tx, ty, tz):
        """Матрица переноса"""
        m = np.identity(4, dtype=float)
        m[0, 3] = tx
        m[1, 3] = ty
        m[2, 3] = tz
        return Matrix4x4(m)
    
    @staticmethod
    def scaling(sx, sy, sz):
        """Матрица масштабирования"""
        m = np.identity(4, dtype=float)
        m[0, 0] = sx
        m[1, 1] = sy
        m[2, 2] = sz
        return Matrix4x4(m)
    
    @staticmethod
    def rotation_x(angle):
        """Матрица вращения вокруг оси X"""
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        m = np.identity(4, dtype=float)
        m[1, 1] = cos_a
        m[1, 2] = -sin_a
        m[2, 1] = sin_a
        m[2, 2] = cos_a
        return Matrix4x4(m)
    
    @staticmethod
    def rotation_y(angle):
        """Матрица вращения вокруг оси Y"""
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        m = np.identity(4, dtype=float)
        m[0, 0] = cos_a
        m[0, 2] = sin_a
        m[2, 0] = -sin_a
        m[2, 2] = cos_a
        return Matrix4x4(m)
    
    @staticmethod
    def rotation_z(angle):
        """Матрица вращения вокруг оси Z"""
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        m = np.identity(4, dtype=float)
        m[0, 0] = cos_a
        m[0, 1] = -sin_a
        m[1, 0] = sin_a
        m[1, 1] = cos_a
        return Matrix4x4(m)
    
    @staticmethod
    def rotation_axis(axis, angle):
        """Матрица вращения вокруг произвольной оси"""
        axis = axis.normalize()
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        one_minus_cos = 1 - cos_a
        
        x, y, z = axis.x, axis.y, axis.z
        
        m = np.array([
            [cos_a + x*x*one_minus_cos, x*y*one_minus_cos - z*sin_a, x*z*one_minus_cos + y*sin_a, 0],
            [y*x*one_minus_cos + z*sin_a, cos_a + y*y*one_minus_cos, y*z*one_minus_cos - x*sin_a, 0],
            [z*x*one_minus_cos - y*sin_a, z*y*one_minus_cos + x*sin_a, cos_a + z*z*one_minus_cos, 0],
            [0, 0, 0, 1]
        ], dtype=float)
        
        return Matrix4x4(m)
    
    def __mul__(self, other):
        if isinstance(other, Matrix4x4):
            return Matrix4x4(np.dot(self.matrix, other.matrix))
        elif isinstance(other, Vector3D):
            # Преобразуем вектор в однородные координаты
            v = np.array([other.x, other.y, other.z, 1.0])
            result = np.dot(self.matrix, v)
            return Vector3D(result[0], result[1], result[2])
        return None
    
    def __str__(self):
        return str(self.matrix.round(3))

class Object3D:
    """Класс для представления 3D объекта"""
    def __init__(self):
        self.vertices = []  # Список вершин
        self.edges = []     # Список ребер (пары индексов вершин)
        self.faces = []     # Список граней (списки индексов вершин)
        self.color = "blue"
        self.name = "Объект"
    
    def add_vertex(self, x, y, z):
        """Добавляет вершину"""
        self.vertices.append(Vector3D(x, y, z))
        return len(self.vertices) - 1
    
    def add_edge(self, v1, v2):
        """Добавляет ребро"""
        self.edges.append((v1, v2))
    
    def add_face(self, vertices_indices):
        """Добавляет грань"""
        self.faces.append(vertices_indices)
    
    def apply_transform(self, matrix):
        """Применяет матрицу преобразования ко всем вершинам"""
        for i in range(len(self.vertices)):
            self.vertices[i] = matrix * self.vertices[i]
    
    def get_center(self):
        """Возвращает центр объекта"""
        if not self.vertices:
            return Vector3D(0, 0, 0)
        
        center = Vector3D()
        for v in self.vertices:
            center = center + v
        return center / len(self.vertices)
    
    def copy(self):
        """Создает копию объекта"""
        obj = Object3D()
        obj.vertices = [Vector3D(v.x, v.y, v.z) for v in self.vertices]
        obj.edges = self.edges.copy()
        obj.faces = self.faces.copy()
        obj.color = self.color
        obj.name = self.name
        return obj
    
    def get_bounding_box(self):
        """Возвращает ограничивающий параллелепипед"""
        if not self.vertices:
            return (Vector3D(0, 0, 0), Vector3D(0, 0, 0))
        
        min_x = min(v.x for v in self.vertices)
        min_y = min(v.y for v in self.vertices)
        min_z = min(v.z for v in self.vertices)
        max_x = max(v.x for v in self.vertices)
        max_y = max(v.y for v in self.vertices)
        max_z = max(v.z for v in self.vertices)
        
        return (Vector3D(min_x, min_y, min_z), Vector3D(max_x, max_y, max_z))
    
    def to_dict(self):
        """Преобразует объект в словарь для сохранения"""
        return {
            'name': self.name,
            'vertices': [[v.x, v.y, v.z] for v in self.vertices],
            'edges': self.edges,
            'faces': self.faces,
            'color': self.color
        }
    
    @staticmethod
    def from_dict(data):
        """Создает объект из словаря"""
        obj = Object3D()
        obj.name = data.get('name', 'Объект')
        obj.color = data.get('color', 'blue')
        
        for v in data.get('vertices', []):
            obj.add_vertex(v[0], v[1], v[2])
        
        for e in data.get('edges', []):
            obj.add_edge(e[0], e[1])
        
        for f in data.get('faces', []):
            obj.add_face(f)
        
        return obj

class Letter3DGenerator:
    """Генератор 3D букв"""
    
    @staticmethod
    def create_letter_A():
        """Создает 3D букву A"""
        letter = Object3D()
        letter.name = "Буква A"
        letter.color = "red"
        
        # Вершины для буквы A
        vertices = [
            # Передняя грань
            (-1, 0, 0.5), (0, 2, 0.5), (1, 0, 0.5),
            (-0.5, 1, 0.5), (0.5, 1, 0.5),
            
            # Задняя грань
            (-1, 0, -0.5), (0, 2, -0.5), (1, 0, -0.5),
            (-0.5, 1, -0.5), (0.5, 1, -0.5)
        ]
        
        # Добавляем вершины
        for v in vertices:
            letter.add_vertex(*v)
        
        # Ребра передней грани
        letter.add_edge(0, 1)
        letter.add_edge(1, 2)
        letter.add_edge(0, 2)  # Основание
        letter.add_edge(3, 4)  # Перекладина
        
        # Ребра задней грани
        letter.add_edge(5, 6)
        letter.add_edge(6, 7)
        letter.add_edge(5, 7)  # Основание
        letter.add_edge(8, 9)  # Перекладина
        
        # Боковые ребра
        letter.add_edge(0, 5)
        letter.add_edge(1, 6)
        letter.add_edge(2, 7)
        letter.add_edge(3, 8)
        letter.add_edge(4, 9)
        
        # Грани
        letter.add_face([0, 1, 4, 3])  # Передняя левая
        letter.add_face([3, 4, 2, 0])  # Передняя правая
        letter.add_face([5, 6, 9, 8])  # Задняя левая
        letter.add_face([8, 9, 7, 5])  # Задняя правая
        
        return letter
    
    @staticmethod
    def create_letter_B():
        """Создает 3D букву B"""
        letter = Object3D()
        letter.name = "Буква B"
        letter.color = "green"
        
        # Вершины для буквы B
        vertices = []
        
        # Передняя грань - вертикальная линия
        vertices.extend([(-1, 0, 0.5), (-1, 2, 0.5)])
        
        # Передняя грань - верхний полукруг
        for i in range(9):  # 8 сегментов + начальная точка
            angle = math.pi * i / 8
            vertices.append((-0.8 + 0.6 * math.cos(angle), 1.5 + 0.5 * math.sin(angle), 0.5))
        
        # Передняя грань - нижний полукруг
        for i in range(9):
            angle = math.pi * i / 8
            vertices.append((-0.8 + 0.6 * math.cos(angle), 0.5 + 0.5 * math.sin(angle), 0.5))
        
        # Задняя грань
        vertices.extend([(-1, 0, -0.5), (-1, 2, -0.5)])
        
        for i in range(9):
            angle = math.pi * i / 8
            vertices.append((-0.8 + 0.6 * math.cos(angle), 1.5 + 0.5 * math.sin(angle), -0.5))
        
        for i in range(9):
            angle = math.pi * i / 8
            vertices.append((-0.8 + 0.6 * math.cos(angle), 0.5 + 0.5 * math.sin(angle), -0.5))
        
        # Добавляем вершины
        for v in vertices:
            letter.add_vertex(*v)
        
        # Ребра
        n = 9  # Количество точек в полукруге
        
        # Вертикальные ребра
        letter.add_edge(0, 1)
        letter.add_edge(2*n + 2, 2*n + 3)
        
        # Ребра передней грани
        for i in range(n):
            letter.add_edge(2 + i, 2 + (i + 1) % n)  # Верхний полукруг
            letter.add_edge(2 + n + i, 2 + n + (i + 1) % n)  # Нижний полукруг
        
        # Ребра задней грани
        for i in range(n):
            letter.add_edge(2*n + 4 + i, 2*n + 4 + (i + 1) % n)  # Верхний полукруг
            letter.add_edge(2*n + 4 + n + i, 2*n + 4 + n + (i + 1) % n)  # Нижний полукруг
        
        # Боковые ребра
        letter.add_edge(0, 2*n + 2)  # Нижняя левая
        letter.add_edge(1, 2*n + 3)  # Верхняя левая
        
        for i in range(2*n):
            letter.add_edge(2 + i, 2*n + 4 + i)
        
        return letter
    
    @staticmethod
    def create_letter_C():
        """Создает 3D букву C"""
        letter = Object3D()
        letter.name = "Буква C"
        letter.color = "blue"
        
        # Вершины для буквы C
        vertices = []
        
        # Передняя грань - внешний полукруг
        for i in range(13):  # 12 сегментов + начальная точка
            angle = math.pi/6 + math.pi * 5/6 * i / 12
            vertices.append((math.cos(angle), 1 + math.sin(angle), 0.5))
        
        # Передняя грань - внутренний полукруг
        for i in range(13):
            angle = math.pi/6 + math.pi * 5/6 * i / 12
            vertices.append((0.6 * math.cos(angle), 1 + 0.6 * math.sin(angle), 0.5))
        
        # Задняя грань
        for i in range(13):
            angle = math.pi/6 + math.pi * 5/6 * i / 12
            vertices.append((math.cos(angle), 1 + math.sin(angle), -0.5))
        
        for i in range(13):
            angle = math.pi/6 + math.pi * 5/6 * i / 12
            vertices.append((0.6 * math.cos(angle), 1 + 0.6 * math.sin(angle), -0.5))
        
        # Добавляем вершины
        for v in vertices:
            letter.add_vertex(*v)
        
        # Ребра
        n = 13
        
        # Ребра передней грани
        for i in range(n-1):
            letter.add_edge(i, i + 1)  # Внешний полукруг
            letter.add_edge(n + i, n + i + 1)  # Внутренний полукруг
        
        # Ребра задней грани
        for i in range(n-1):
            letter.add_edge(2*n + i, 2*n + i + 1)  # Внешний полукруг
            letter.add_edge(3*n + i, 3*n + i + 1)  # Внутренний полукруг
        
        # Боковые ребра
        letter.add_edge(0, 2*n)  # Начало внешнего
        letter.add_edge(n-1, 3*n-1)  # Конец внешнего
        letter.add_edge(n, 3*n)  # Начало внутреннего
        letter.add_edge(2*n-1, 4*n-1)  # Конец внутреннего
        
        return letter
    
    @staticmethod
    def create_cube():
        """Создает 3D куб для тестирования"""
        cube = Object3D()
        cube.name = "Куб"
        cube.color = "purple"
        
        # Вершины куба
        vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Нижняя грань
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)      # Верхняя грань
        ]
        
        for v in vertices:
            cube.add_vertex(*v)
        
        # Ребра
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Нижняя грань
            (4, 5), (5, 6), (6, 7), (7, 4),  # Верхняя грань
            (0, 4), (1, 5), (2, 6), (3, 7)   # Вертикальные ребра
        ]
        
        for e in edges:
            cube.add_edge(*e)
        
        # Грани
        cube.add_face([0, 1, 2, 3])  # Нижняя
        cube.add_face([4, 5, 6, 7])  # Верхняя
        cube.add_face([0, 1, 5, 4])  # Передняя
        cube.add_face([1, 2, 6, 5])  # Правая
        cube.add_face([2, 3, 7, 6])  # Задняя
        cube.add_face([3, 0, 4, 7])  # Левая
        
        return cube
    
    @staticmethod
    def get_letter(letter_char):
        """Возвращает 3D букву по символу"""
        letter_char = letter_char.upper()
        
        if letter_char == 'A':
            return Letter3DGenerator.create_letter_A()
        elif letter_char == 'B':
            return Letter3DGenerator.create_letter_B()
        elif letter_char == 'C':
            return Letter3DGenerator.create_letter_C()
        elif letter_char == 'D':
            return Letter3DGenerator.create_cube()  # Заглушка
        else:
            return Letter3DGenerator.create_cube()  # По умолчанию куб

class Camera:
    """Класс для представления камеры"""
    def __init__(self):
        self.position = Vector3D(0, 0, 10)
        self.target = Vector3D(0, 0, 0)
        self.up = Vector3D(0, 1, 0)
        self.fov = 60  # Угол обзора в градусах
        self.near = 0.1
        self.far = 100
    
    def get_view_matrix(self):
        """Возвращает матрицу вида"""
        # Вычисляем базис камеры
        z_axis = (self.position - self.target).normalize()
        x_axis = self.up.cross(z_axis).normalize()
        y_axis = z_axis.cross(x_axis)
        
        # Создаем матрицу вида
        view_matrix = np.identity(4, dtype=float)
        
        view_matrix[0, 0:3] = x_axis.to_array()
        view_matrix[1, 0:3] = y_axis.to_array()
        view_matrix[2, 0:3] = z_axis.to_array()
        
        view_matrix[0, 3] = -x_axis.dot(self.position)
        view_matrix[1, 3] = -y_axis.dot(self.position)
        view_matrix[2, 3] = -z_axis.dot(self.position)
        
        return Matrix4x4(view_matrix)
    
    def get_projection_matrix(self, width, height):
        """Возвращает матрицу проекции"""
        aspect = width / height
        fov_rad = math.radians(self.fov)
        
        # Перспективная проекция
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        proj_matrix = np.zeros((4, 4), dtype=float)
        proj_matrix[0, 0] = f / aspect
        proj_matrix[1, 1] = f
        proj_matrix[2, 2] = (self.far + self.near) / (self.near - self.far)
        proj_matrix[2, 3] = (2 * self.far * self.near) / (self.near - self.far)
        proj_matrix[3, 2] = -1
        
        return Matrix4x4(proj_matrix)
    
    def get_orthographic_matrix(self, width, height, scale=1.0):
        """Возвращает матрицу ортографической проекции"""
        aspect = width / height
        
        ortho_matrix = np.identity(4, dtype=float)
        ortho_matrix[0, 0] = scale / aspect
        ortho_matrix[1, 1] = scale
        
        return Matrix4x4(ortho_matrix)

class Canvas3D(tk.Canvas):
    """Холст для отображения 3D объектов"""
    def __init__(self, parent, width=800, height=600, **kwargs):
        super().__init__(parent, width=width, height=height, bg="white", **kwargs)
        self.width = width
        self.height = height
        
        # Камера
        self.camera = Camera()
        
        # Объекты
        self.objects = []
        self.selected_object = None
        
        # Настройки отображения
        self.show_axes = True
        self.show_grid = True
        self.projection_type = "perspective"  # "perspective" или "orthographic"
        self.show_projections = False
        
        # Цвета
        self.colors = {
            'axes_x': 'red',
            'axes_y': 'green',
            'axes_z': 'blue',
            'grid': '#e0e0e0',
            'selected': 'yellow'
        }
        
        # Инициализация
        self.draw_axes()
    
    def add_object(self, obj):
        """Добавляет объект"""
        self.objects.append(obj)
        if self.selected_object is None:
            self.selected_object = obj
        self.redraw()
    
    def remove_object(self, obj):
        """Удаляет объект"""
        if obj in self.objects:
            self.objects.remove(obj)
            if self.selected_object == obj:
                self.selected_object = None if not self.objects else self.objects[0]
            self.redraw()
    
    def clear_objects(self):
        """Очищает все объекты"""
        self.objects.clear()
        self.selected_object = None
        self.redraw()
    
    def draw_axes(self):
        """Рисует оси координат"""
        self.delete("axes")
        
        # Центр холста
        center_x = self.width // 2
        center_y = self.height // 2
        length = 100
        
        # Ось X (красная)
        self.create_line(center_x, center_y, center_x + length, center_y,
                        fill=self.colors['axes_x'], width=2, arrow=tk.LAST, tags="axes")
        self.create_text(center_x + length + 10, center_y, text="X",
                        fill=self.colors['axes_x'], font=("Arial", 10, "bold"), tags="axes")
        
        # Ось Y (зеленая)
        self.create_line(center_x, center_y, center_x, center_y - length,
                        fill=self.colors['axes_y'], width=2, arrow=tk.LAST, tags="axes")
        self.create_text(center_x, center_y - length - 10, text="Y",
                        fill=self.colors['axes_y'], font=("Arial", 10, "bold"), tags="axes")
        
        # Ось Z (синяя) - диагональ для 3D эффекта
        self.create_line(center_x, center_y, center_x - length//2, center_y + length//2,
                        fill=self.colors['axes_z'], width=2, arrow=tk.LAST, tags="axes")
        self.create_text(center_x - length//2 - 10, center_y + length//2 + 10, text="Z",
                        fill=self.colors['axes_z'], font=("Arial", 10, "bold"), tags="axes")
    
    def draw_grid(self):
        """Рисует координатную сетку"""
        self.delete("grid")
        
        center_x = self.width // 2
        center_y = self.height // 2
        grid_size = 50
        grid_lines = 5
        
        # Горизонтальные линии
        for i in range(-grid_lines, grid_lines + 1):
            y = center_y + i * grid_size
            self.create_line(center_x - grid_lines * grid_size, y,
                           center_x + grid_lines * grid_size, y,
                           fill=self.colors['grid'], width=1, tags="grid")
        
        # Вертикальные линии
        for i in range(-grid_lines, grid_lines + 1):
            x = center_x + i * grid_size
            self.create_line(x, center_y - grid_lines * grid_size,
                           x, center_y + grid_lines * grid_size,
                           fill=self.colors['grid'], width=1, tags="grid")
    
    def project_point(self, point):
        """Проецирует 3D точку на 2D плоскость"""
        # Преобразуем в вектор
        v = Vector3D(point[0], point[1], point[2])
        
        if self.projection_type == "perspective":
            # Перспективная проекция
            view_matrix = self.camera.get_view_matrix()
            proj_matrix = self.camera.get_projection_matrix(self.width, self.height)
            
            # Применяем преобразования
            v_view = view_matrix * v
            v_proj = proj_matrix * v_view
            
            # Преобразуем из клип-координат в экранные
            if v_proj.z != 0:
                x = (v_proj.x / abs(v_proj.z) + 1) * self.width / 2
                y = (1 - v_proj.y / abs(v_proj.z)) * self.height / 2
            else:
                x = (v_proj.x + 1) * self.width / 2
                y = (1 - v_proj.y) * self.height / 2
        else:
            # Ортографическая проекция
            ortho_matrix = self.camera.get_orthographic_matrix(self.width, self.height, 0.5)
            v_proj = ortho_matrix * v
            
            # Преобразуем в экранные координаты
            x = (v_proj.x + 1) * self.width / 2
            y = (1 - v_proj.y) * self.height / 2
        
        return (x, y)
    
    def draw_object(self, obj, is_selected=False):
        """Рисует 3D объект"""
        if not obj.vertices:
            return
        
        color = self.colors['selected'] if is_selected else obj.color
        
        # Проецируем все вершины
        projected_vertices = []
        for vertex in obj.vertices:
            projected = self.project_point(vertex.to_tuple())
            projected_vertices.append(projected)
        
        # Рисуем грани
        for face in obj.faces:
            if len(face) >= 3:
                points = [projected_vertices[i] for i in face]
                self.create_polygon(points, fill="", outline=color, width=1, tags="object")
        
        # Рисуем ребра
        for edge in obj.edges:
            v1, v2 = edge
            if v1 < len(projected_vertices) and v2 < len(projected_vertices):
                x1, y1 = projected_vertices[v1]
                x2, y2 = projected_vertices[v2]
                self.create_line(x1, y1, x2, y2, fill=color, width=2, tags="object")
        
        # Рисуем вершины
        for i, (x, y) in enumerate(projected_vertices):
            size = 3 if not is_selected else 4
            fill_color = color if not is_selected else self.colors['selected']
            self.create_oval(x - size, y - size, x + size, y + size,
                           fill=fill_color, outline=fill_color, tags="object")
            
            # Подписи вершин (для отладки)
            # self.create_text(x + 5, y - 5, text=str(i), fill="black", font=("Arial", 8), tags="object")
    
    def draw_projections(self):
        """Рисует три ортографические проекции"""
        if not self.objects:
            return
        
        # Размеры областей проекций
        width = self.width // 3
        height = self.height // 3
        offset = 20
        
        # Проекция на плоскость XY (вид сверху)
        xy_rect = (offset, offset, width - offset, height - offset)
        self.create_rectangle(xy_rect, outline="black", width=1, tags="projection")
        self.create_text(width // 2, offset - 10, text="XY", fill="black", font=("Arial", 10, "bold"), tags="projection")
        
        # Проекция на плоскость XZ (вид спереди)
        xz_rect = (width + offset, offset, 2*width - offset, height - offset)
        self.create_rectangle(xz_rect, outline="black", width=1, tags="projection")
        self.create_text(width + width // 2, offset - 10, text="XZ", fill="black", font=("Arial", 10, "bold"), tags="projection")
        
        # Проекция на плоскость YZ (вид сбоку)
        yz_rect = (2*width + offset, offset, 3*width - offset, height - offset)
        self.create_rectangle(yz_rect, outline="black", width=1, tags="projection")
        self.create_text(2*width + width // 2, offset - 10, text="YZ", fill="black", font=("Arial", 10, "bold"), tags="projection")
        
        # Рисуем проекции объектов
        for obj in self.objects:
            self.draw_projection_xy(obj, xy_rect)
            self.draw_projection_xz(obj, xz_rect)
            self.draw_projection_yz(obj, yz_rect)
    
    def draw_projection_xy(self, obj, rect):
        """Рисует проекцию на плоскость XY"""
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        
        # Масштабируем объект чтобы он поместился в область
        bbox_min, bbox_max = obj.get_bounding_box()
        obj_width = bbox_max.x - bbox_min.x
        obj_height = bbox_max.y - bbox_min.y
        
        if obj_width == 0 or obj_height == 0:
            return
        
        scale = min(width / obj_width, height / obj_height) * 0.8
        offset_x = x1 + width / 2 - (bbox_min.x + bbox_max.x) / 2 * scale
        offset_y = y1 + height / 2 - (bbox_min.y + bbox_max.y) / 2 * scale
        
        # Рисуем ребра
        for edge in obj.edges:
            v1, v2 = edge
            if v1 < len(obj.vertices) and v2 < len(obj.vertices):
                x1_proj = obj.vertices[v1].x * scale + offset_x
                y1_proj = (height - obj.vertices[v1].y * scale) + offset_y - height
                x2_proj = obj.vertices[v2].x * scale + offset_x
                y2_proj = (height - obj.vertices[v2].y * scale) + offset_y - height
                
                self.create_line(x1_proj, y1_proj, x2_proj, y2_proj,
                               fill=obj.color, width=1, tags="projection")
    
    def draw_projection_xz(self, obj, rect):
        """Рисует проекцию на плоскость XZ"""
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        
        bbox_min, bbox_max = obj.get_bounding_box()
        obj_width = bbox_max.x - bbox_min.x
        obj_depth = bbox_max.z - bbox_min.z
        
        if obj_width == 0 or obj_depth == 0:
            return
        
        scale = min(width / obj_width, height / obj_depth) * 0.8
        offset_x = x1 + width / 2 - (bbox_min.x + bbox_max.x) / 2 * scale
        offset_y = y1 + height / 2 - (bbox_min.z + bbox_max.z) / 2 * scale
        
        for edge in obj.edges:
            v1, v2 = edge
            if v1 < len(obj.vertices) and v2 < len(obj.vertices):
                x1_proj = obj.vertices[v1].x * scale + offset_x
                y1_proj = (height - obj.vertices[v1].z * scale) + offset_y - height
                x2_proj = obj.vertices[v2].x * scale + offset_x
                y2_proj = (height - obj.vertices[v2].z * scale) + offset_y - height
                
                self.create_line(x1_proj, y1_proj, x2_proj, y2_proj,
                               fill=obj.color, width=1, tags="projection")
    
    def draw_projection_yz(self, obj, rect):
        """Рисует проекцию на плоскость YZ"""
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        
        bbox_min, bbox_max = obj.get_bounding_box()
        obj_height = bbox_max.y - bbox_min.y
        obj_depth = bbox_max.z - bbox_min.z
        
        if obj_height == 0 or obj_depth == 0:
            return
        
        scale = min(width / obj_height, height / obj_depth) * 0.8
        offset_x = x1 + width / 2 - (bbox_min.y + bbox_max.y) / 2 * scale
        offset_y = y1 + height / 2 - (bbox_min.z + bbox_max.z) / 2 * scale
        
        for edge in obj.edges:
            v1, v2 = edge
            if v1 < len(obj.vertices) and v2 < len(obj.vertices):
                x1_proj = obj.vertices[v1].y * scale + offset_x
                y1_proj = (height - obj.vertices[v1].z * scale) + offset_y - height
                x2_proj = obj.vertices[v2].y * scale + offset_x
                y2_proj = (height - obj.vertices[v2].z * scale) + offset_y - height
                
                self.create_line(x1_proj, y1_proj, x2_proj, y2_proj,
                               fill=obj.color, width=1, tags="projection")
    
    def redraw(self):
        """Перерисовывает все объекты"""
        self.delete("all")
        
        if self.show_grid:
            self.draw_grid()
        
        self.draw_axes()
        
        # Рисуем объекты
        for obj in self.objects:
            is_selected = (obj == self.selected_object)
            self.draw_object(obj, is_selected)
        
        if self.show_projections:
            self.draw_projections()
    
    def set_projection(self, projection_type):
        """Устанавливает тип проекции"""
        self.projection_type = projection_type
        self.redraw()
    
    def toggle_projections(self):
        """Переключает отображение проекций"""
        self.show_projections = not self.show_projections
        self.redraw()
    
    def toggle_grid(self):
        """Переключает отображение сетки"""
        self.show_grid = not self.show_grid
        self.redraw()

class TransformPanel:
    """Панель для управления преобразованиями"""
    def __init__(self, parent, canvas):
        self.parent = parent
        self.canvas = canvas
        self.current_transform_matrix = Matrix4x4()
        
        # Создаем виджеты
        self.create_widgets()
    
    def create_widgets(self):
        """Создает элементы управления"""
        # Фрейм для преобразований
        transform_frame = ttk.LabelFrame(self.parent, text="3D Преобразования", padding=10)
        transform_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Масштабирование
        ttk.Label(transform_frame, text="Масштабирование:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(transform_frame, text="X:").grid(row=0, column=1, padx=(10, 0))
        self.scale_x_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.scale_x_var, width=8).grid(row=0, column=2, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=0, column=3, padx=(10, 0))
        self.scale_y_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.scale_y_var, width=8).grid(row=0, column=4, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=0, column=5, padx=(10, 0))
        self.scale_z_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.scale_z_var, width=8).grid(row=0, column=6, padx=2)
        
        ttk.Button(transform_frame, text="Применить", command=self.apply_scaling, width=10).grid(row=0, column=7, padx=(10, 0))
        
        # Перенос
        ttk.Label(transform_frame, text="Перенос:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(transform_frame, text="X:").grid(row=1, column=1, padx=(10, 0))
        self.translate_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.translate_x_var, width=8).grid(row=1, column=2, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=1, column=3, padx=(10, 0))
        self.translate_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.translate_y_var, width=8).grid(row=1, column=4, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=1, column=5, padx=(10, 0))
        self.translate_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.translate_z_var, width=8).grid(row=1, column=6, padx=2)
        
        ttk.Button(transform_frame, text="Применить", command=self.apply_translation, width=10).grid(row=1, column=7, padx=(10, 0))
        
        # Вращение вокруг осей
        ttk.Label(transform_frame, text="Вращение (градусы):").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(transform_frame, text="X:").grid(row=2, column=1, padx=(10, 0))
        self.rotate_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.rotate_x_var, width=8).grid(row=2, column=2, padx=2)
        ttk.Button(transform_frame, text="Вращать", command=lambda: self.apply_rotation('x'), width=8).grid(row=2, column=3, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=2, column=4, padx=(10, 0))
        self.rotate_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.rotate_y_var, width=8).grid(row=2, column=5, padx=2)
        ttk.Button(transform_frame, text="Вращать", command=lambda: self.apply_rotation('y'), width=8).grid(row=2, column=6, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=2, column=7, padx=(10, 0))
        self.rotate_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.rotate_z_var, width=8).grid(row=2, column=8, padx=2)
        ttk.Button(transform_frame, text="Вращать", command=lambda: self.apply_rotation('z'), width=8).grid(row=2, column=9, padx=2)
        
        # Вращение вокруг произвольной оси
        ttk.Label(transform_frame, text="Вращение вокруг произвольной оси:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(transform_frame, text="Ось (x,y,z):").grid(row=3, column=1, padx=(10, 0))
        self.axis_x_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.axis_x_var, width=6).grid(row=3, column=2, padx=2)
        
        self.axis_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.axis_y_var, width=6).grid(row=3, column=3, padx=2)
        
        self.axis_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.axis_z_var, width=6).grid(row=3, column=4, padx=2)
        
        ttk.Label(transform_frame, text="Угол:").grid(row=3, column=5, padx=(10, 0))
        self.axis_angle_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.axis_angle_var, width=8).grid(row=3, column=6, padx=2)
        
        ttk.Button(transform_frame, text="Вращать", command=self.apply_axis_rotation, width=10).grid(row=3, column=7, padx=(10, 0))
        
        # Сброс преобразований
        ttk.Button(transform_frame, text="Сбросить", command=self.reset_transforms, width=10).grid(row=4, column=0, pady=10)
        
        # Матрица преобразования
        matrix_frame = ttk.LabelFrame(self.parent, text="Матрица преобразования", padding=10)
        matrix_frame.pack(fill=tk.BOTH, expand=True)
        
        self.matrix_text = tk.Text(matrix_frame, height=6, width=50, font=("Courier", 9))
        self.matrix_text.pack(fill=tk.BOTH, expand=True)
        
        # Обновляем отображение матрицы
        self.update_matrix_display()
    
    def apply_scaling(self):
        """Применяет масштабирование к выбранному объекту"""
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект!")
            return
        
        sx = self.scale_x_var.get()
        sy = self.scale_y_var.get()
        sz = self.scale_z_var.get()
        
        scaling_matrix = Matrix4x4.scaling(sx, sy, sz)
        self.apply_transform(scaling_matrix, "Масштабирование")
    
    def apply_translation(self):
        """Применяет перенос к выбранному объекту"""
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект!")
            return
        
        tx = self.translate_x_var.get()
        ty = self.translate_y_var.get()
        tz = self.translate_z_var.get()
        
        translation_matrix = Matrix4x4.translation(tx, ty, tz)
        self.apply_transform(translation_matrix, "Перенос")
    
    def apply_rotation(self, axis):
        """Применяет вращение вокруг указанной оси"""
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект!")
            return
        
        if axis == 'x':
            angle = self.rotate_x_var.get()
            rotation_matrix = Matrix4x4.rotation_x(angle)
        elif axis == 'y':
            angle = self.rotate_y_var.get()
            rotation_matrix = Matrix4x4.rotation_y(angle)
        elif axis == 'z':
            angle = self.rotate_z_var.get()
            rotation_matrix = Matrix4x4.rotation_z(angle)
        else:
            return
        
        self.apply_transform(rotation_matrix, f"Вращение вокруг оси {axis.upper()}")
    
    def apply_axis_rotation(self):
        """Применяет вращение вокруг произвольной оси"""
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект!")
            return
        
        axis = Vector3D(
            self.axis_x_var.get(),
            self.axis_y_var.get(),
            self.axis_z_var.get()
        )
        
        angle = self.axis_angle_var.get()
        
        if axis.length() == 0:
            messagebox.showerror("Ошибка", "Ось не может быть нулевым вектором!")
            return
        
        rotation_matrix = Matrix4x4.rotation_axis(axis, angle)
        self.apply_transform(rotation_matrix, "Вращение вокруг произвольной оси")
    
    def apply_transform(self, matrix, operation_name):
        """Применяет матрицу преобразования"""
        # Обновляем общую матрицу преобразования
        self.current_transform_matrix = matrix * self.current_transform_matrix
        
        # Применяем преобразование к объекту
        self.canvas.selected_object.apply_transform(matrix)
        
        # Обновляем отображение
        self.canvas.redraw()
        self.update_matrix_display()
        
        # Выводим информацию
        print(f"{operation_name} применено")
    
    def reset_transforms(self):
        """Сбрасывает все преобразования"""
        if not self.canvas.selected_object:
            return
        
        # Создаем копию исходного объекта
        original_letter = Letter3DGenerator.get_letter(self.canvas.selected_object.name[-1])
        original_letter.color = self.canvas.selected_object.color
        
        # Заменяем объект
        index = self.canvas.objects.index(self.canvas.selected_object)
        self.canvas.objects[index] = original_letter
        self.canvas.selected_object = original_letter
        
        # Сбрасываем матрицу
        self.current_transform_matrix = Matrix4x4()
        
        # Обновляем отображение
        self.canvas.redraw()
        self.update_matrix_display()
    
    def update_matrix_display(self):
        """Обновляет отображение матрицы преобразования"""
        self.matrix_text.delete(1.0, tk.END)
        
        matrix_str = str(self.current_transform_matrix)
        lines = matrix_str.strip('[]').split('\n')
        
        for line in lines:
            formatted_line = '  '.join([f'{float(x):8.3f}' for x in line.strip().split()])
            self.matrix_text.insert(tk.END, f"[{formatted_line}]\n")

class ObjectPanel:
    """Панель для управления объектами"""
    def __init__(self, parent, canvas):
        self.parent = parent
        self.canvas = canvas
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создает элементы управления"""
        # Фрейм для объектов
        object_frame = ttk.LabelFrame(self.parent, text="Объекты", padding=10)
        object_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор буквы
        ttk.Label(object_frame, text="Буква:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.letter_var = tk.StringVar(value="A")
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        
        letter_combo = ttk.Combobox(object_frame, textvariable=self.letter_var,
                                  values=letters, state="readonly", width=5)
        letter_combo.grid(row=0, column=1, padx=(5, 10), pady=5)
        
        # Цвет
        ttk.Label(object_frame, text="Цвет:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.color_var = tk.StringVar(value="blue")
        colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'cyan', 'magenta']
        
        color_combo = ttk.Combobox(object_frame, textvariable=self.color_var,
                                 values=colors, state="readonly", width=10)
        color_combo.grid(row=0, column=3, padx=(5, 10), pady=5)
        
        # Кнопки управления объектами
        button_frame = ttk.Frame(object_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky=tk.EW)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_object).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Удалить", command=self.remove_object).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Очистить все", command=self.clear_objects).pack(side=tk.LEFT, padx=2)
        
        # Список объектов
        list_frame = ttk.LabelFrame(self.parent, text="Список объектов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview для отображения объектов
        columns = ('#1', '#2', '#3')
        self.object_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.object_tree.heading('#1', text='Объект')
        self.object_tree.heading('#2', text='Вершин')
        self.object_tree.heading('#3', text='Ребер')
        
        self.object_tree.column('#1', width=150)
        self.object_tree.column('#2', width=80)
        self.object_tree.column('#3', width=80)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.object_tree.yview)
        self.object_tree.configure(yscrollcommand=scrollbar.set)
        
        self.object_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязываем выбор объекта
        self.object_tree.bind('<<TreeviewSelect>>', self.on_object_selected)
    
    def add_object(self):
        """Добавляет новый объект"""
        letter = self.letter_var.get()
        color = self.color_var.get()
        
        # Создаем объект
        obj = Letter3DGenerator.get_letter(letter)
        obj.color = color
        obj.name = f"Буква {letter} ({len(self.canvas.objects) + 1})"
        
        # Добавляем на холст
        self.canvas.add_object(obj)
        
        # Добавляем в список
        self.update_object_list()
    
    def remove_object(self):
        """Удаляет выбранный объект"""
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект для удаления!")
            return
        
        self.canvas.remove_object(self.canvas.selected_object)
        self.update_object_list()
    
    def clear_objects(self):
        """Очищает все объекты"""
        self.canvas.clear_objects()
        self.update_object_list()
    
    def update_object_list(self):
        """Обновляет список объектов"""
        # Очищаем список
        for item in self.object_tree.get_children():
            self.object_tree.delete(item)
        
        # Добавляем объекты
        for i, obj in enumerate(self.canvas.objects):
            self.object_tree.insert('', 'end', values=(
                obj.name,
                len(obj.vertices),
                len(obj.edges)
            ))
        
        # Выделяем выбранный объект
        if self.canvas.selected_object:
            for i, obj in enumerate(self.canvas.objects):
                if obj == self.canvas.selected_object:
                    children = self.object_tree.get_children()
                    if i < len(children):
                        self.object_tree.selection_set(children[i])
                    break
    
    def on_object_selected(self, event):
        """Обработчик выбора объекта в списке"""
        selection = self.object_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.object_tree.index(item)
        
        if 0 <= index < len(self.canvas.objects):
            self.canvas.selected_object = self.canvas.objects[index]
            self.canvas.redraw()

class ProjectionPanel:
    """Панель для управления проекциями"""
    def __init__(self, parent, canvas):
        self.parent = parent
        self.canvas = canvas
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создает элементы управления"""
        # Фрейм для проекций
        projection_frame = ttk.LabelFrame(self.parent, text="Проекции", padding=10)
        projection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Тип проекции
        ttk.Label(projection_frame, text="Тип проекции:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.projection_var = tk.StringVar(value="perspective")
        
        perspective_radio = ttk.Radiobutton(projection_frame, text="Перспективная",
                                          variable=self.projection_var, value="perspective",
                                          command=self.update_projection)
        perspective_radio.grid(row=0, column=1, padx=(10, 20), pady=5)
        
        orthographic_radio = ttk.Radiobutton(projection_frame, text="Ортографическая",
                                           variable=self.projection_var, value="orthographic",
                                           command=self.update_projection)
        orthographic_radio.grid(row=0, column=2, pady=5)
        
        # Ортографические проекции
        ttk.Label(projection_frame, text="Ортографические проекции:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(projection_frame, text="Показать/Скрыть", command=self.toggle_projections).grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # Настройки камеры
        camera_frame = ttk.LabelFrame(self.parent, text="Настройки камеры", padding=10)
        camera_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(camera_frame, text="Положение камеры:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(camera_frame, text="X:").grid(row=0, column=1, padx=(10, 0))
        self.cam_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(camera_frame, textvariable=self.cam_x_var, width=8).grid(row=0, column=2, padx=2)
        
        ttk.Label(camera_frame, text="Y:").grid(row=0, column=3, padx=(10, 0))
        self.cam_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(camera_frame, textvariable=self.cam_y_var, width=8).grid(row=0, column=4, padx=2)
        
        ttk.Label(camera_frame, text="Z:").grid(row=0, column=5, padx=(10, 0))
        self.cam_z_var = tk.DoubleVar(value=10.0)
        ttk.Entry(camera_frame, textvariable=self.cam_z_var, width=8).grid(row=0, column=6, padx=2)
        
        ttk.Button(camera_frame, text="Применить", command=self.update_camera).grid(row=0, column=7, padx=(10, 0))
        
        # Настройки отображения
        display_frame = ttk.LabelFrame(self.parent, text="Настройки отображения", padding=10)
        display_frame.pack(fill=tk.X)
        
        self.grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Показывать сетку", variable=self.grid_var,
                       command=self.toggle_grid).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.axes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Показывать оси", variable=self.axes_var,
                       command=self.toggle_axes).grid(row=0, column=1, sticky=tk.W, padx=(20, 0), pady=5)
    
    def update_projection(self):
        """Обновляет тип проекции"""
        self.canvas.set_projection(self.projection_var.get())
    
    def toggle_projections(self):
        """Переключает отображение ортографических проекций"""
        self.canvas.toggle_projections()
    
    def toggle_grid(self):
        """Переключает отображение сетки"""
        self.canvas.show_grid = self.grid_var.get()
        self.canvas.redraw()
    
    def toggle_axes(self):
        """Переключает отображение осей"""
        self.canvas.show_axes = self.axes_var.get()
        self.canvas.redraw()
    
    def update_camera(self):
        """Обновляет положение камеры"""
        self.canvas.camera.position = Vector3D(
            self.cam_x_var.get(),
            self.cam_y_var.get(),
            self.cam_z_var.get()
        )
        self.canvas.redraw()

class MainApplication:
    """Главное окно приложения"""
    def __init__(self, root):
        self.root = root
        self.root.title("3D Визуализация букв с преобразованиями и проекциями")
        self.root.geometry("1400x800")
        
        # Создание интерфейса
        self.create_widgets()
        
        # Создание меню
        self.create_menu()
    
    def create_widgets(self):
        """Создает все виджеты интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - управление
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Холст для 3D отображения
        self.canvas = Canvas3D(main_frame, width=900, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Панель объектов
        self.object_panel = ObjectPanel(left_frame, self.canvas)
        
        # Панель проекций
        self.projection_panel = ProjectionPanel(left_frame, self.canvas)
        
        # Панель преобразований
        self.transform_panel = TransformPanel(left_frame, self.canvas)
        
        # Добавляем тестовый объект по умолчанию
        default_obj = Letter3DGenerator.create_letter_A()
        self.canvas.add_object(default_obj)
        self.object_panel.update_object_list()
    
    def create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить сцену", command=self.save_scene)
        file_menu.add_command(label="Загрузить сцену", command=self.load_scene)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт изображения", command=self.export_image)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Объекты"
        object_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Объекты", menu=object_menu)
        object_menu.add_command(label="Добавить куб", command=self.add_cube)
        object_menu.add_command(label="Добавить букву A", command=lambda: self.add_letter('A'))
        object_menu.add_command(label="Добавить букву B", command=lambda: self.add_letter('B'))
        object_menu.add_command(label="Добавить букву C", command=lambda: self.add_letter('C'))
        object_menu.add_separator()
        object_menu.add_command(label="Очистить все объекты", command=self.object_panel.clear_objects)
        
        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Сброс камеры", command=self.reset_camera)
        view_menu.add_checkbutton(label="Показать сетку", variable=self.projection_panel.grid_var,
                                 command=self.projection_panel.toggle_grid)
        view_menu.add_checkbutton(label="Показать оси", variable=self.projection_panel.axes_var,
                                 command=self.projection_panel.toggle_axes)
        view_menu.add_separator()
        view_menu.add_command(label="Ортографические проекции", command=self.projection_panel.toggle_projections)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def add_cube(self):
        """Добавляет куб"""
        cube = Letter3DGenerator.create_cube()
        cube.name = f"Куб ({len(self.canvas.objects) + 1})"
        cube.color = "purple"
        self.canvas.add_object(cube)
        self.object_panel.update_object_list()
    
    def add_letter(self, letter):
        """Добавляет букву"""
        obj = Letter3DGenerator.get_letter(letter)
        obj.name = f"Буква {letter} ({len(self.canvas.objects) + 1})"
        obj.color = "blue"
        self.canvas.add_object(obj)
        self.object_panel.update_object_list()
    
    def reset_camera(self):
        """Сбрасывает камеру в положение по умолчанию"""
        self.canvas.camera.position = Vector3D(0, 0, 10)
        self.canvas.camera.target = Vector3D(0, 0, 0)
        self.canvas.redraw()
        
        # Обновляем поля ввода
        self.projection_panel.cam_x_var.set(0.0)
        self.projection_panel.cam_y_var.set(0.0)
        self.projection_panel.cam_z_var.set(10.0)
    
    def save_scene(self):
        """Сохраняет сцену в файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить сцену",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                scene_data = {
                    'objects': [obj.to_dict() for obj in self.canvas.objects],
                    'selected_object_index': self.canvas.objects.index(self.canvas.selected_object) if self.canvas.selected_object else -1
                }
                
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(scene_data, file, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Успех", "Сцена сохранена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def load_scene(self):
        """Загружает сцену из файла"""
        filename = filedialog.askopenfilename(
            title="Загрузить сцену",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    scene_data = json.load(file)
                
                # Очищаем текущие объекты
                self.canvas.clear_objects()
                
                # Загружаем объекты
                for obj_data in scene_data.get('objects', []):
                    obj = Object3D.from_dict(obj_data)
                    self.canvas.add_object(obj)
                
                # Восстанавливаем выбранный объект
                selected_index = scene_data.get('selected_object_index', -1)
                if 0 <= selected_index < len(self.canvas.objects):
                    self.canvas.selected_object = self.canvas.objects[selected_index]
                
                # Обновляем список объектов
                self.object_panel.update_object_list()
                
                messagebox.showinfo("Успех", "Сцена загружена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")
    
    def export_image(self):
        """Экспортирует изображение с холста"""
        filename = filedialog.asksaveasfilename(
            title="Экспорт изображения",
            defaultextension=".eps",
            filetypes=[("EPS files", "*.eps"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.canvas.postscript(file=filename, colormode='color')
                messagebox.showinfo("Успех", "Изображение сохранено!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """3D Визуализация букв с преобразованиями и проекциями

Лабораторная работа по компьютерной графике

Реализованные функции:
1. Построение 3D моделей букв
2. Трехмерные преобразования (масштабирование, перенос, вращение)
3. Построение ортографических проекций
4. Сохранение и загрузка сцен
5. Интерактивное управление

Для учебных целей"""
        
        messagebox.showinfo("О программе", about_text)

def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()