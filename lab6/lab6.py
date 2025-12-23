import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
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
    def create_letter_T():
        """Создает 3D букву Т (первая буква фамилии)"""
        letter = Object3D()
        letter.name = "Буква Т"
        letter.color = "blue"
        
        # Вершины для буквы Т
        vertices = [
            # Верхняя горизонтальная часть (передняя)
            (-1.5, 1.5, 0.5), (1.5, 1.5, 0.5),
            (-1.5, 1.0, 0.5), (1.5, 1.0, 0.5),
            
            # Вертикальная часть (передняя)
            (-0.25, 1.0, 0.5), (0.25, 1.0, 0.5),
            (-0.25, -1.5, 0.5), (0.25, -1.5, 0.5),
            
            # Верхняя горизонтальная часть (задняя)
            (-1.5, 1.5, -0.5), (1.5, 1.5, -0.5),
            (-1.5, 1.0, -0.5), (1.5, 1.0, -0.5),
            
            # Вертикальная часть (задняя)
            (-0.25, 1.0, -0.5), (0.25, 1.0, -0.5),
            (-0.25, -1.5, -0.5), (0.25, -1.5, -0.5)
        ]
        
        # Добавляем вершины
        for v in vertices:
            letter.add_vertex(*v)
        
        # Ребра верхней горизонтальной части (передней)
        letter.add_edge(0, 1)  # Верхний край
        letter.add_edge(2, 3)  # Нижний край
        letter.add_edge(0, 2)  # Левый бок
        letter.add_edge(1, 3)  # Правый бок
        
        # Ребра вертикальной части (передней)
        letter.add_edge(4, 6)  # Левая вертикаль
        letter.add_edge(5, 7)  # Правая вертикаль
        letter.add_edge(4, 5)  # Верх горизонтали
        letter.add_edge(6, 7)  # Низ горизонтали
        
        # Ребра верхней горизонтальной части (задней)
        letter.add_edge(8, 9)   # Верхний край
        letter.add_edge(10, 11) # Нижний край
        letter.add_edge(8, 10)  # Левый бок
        letter.add_edge(9, 11)  # Правый бок
        
        # Ребра вертикальной части (задней)
        letter.add_edge(12, 14)  # Левая вертикаль
        letter.add_edge(13, 15)  # Правая вертикаль
        letter.add_edge(12, 13)  # Верх горизонтали
        letter.add_edge(14, 15)  # Низ горизонтали
        
        # Боковые ребра, соединяющие переднюю и заднюю части
        letter.add_edge(0, 8)   # Верхний левый угол
        letter.add_edge(1, 9)   # Верхний правый угол
        letter.add_edge(2, 10)  # Нижний левый угол (верхняя часть)
        letter.add_edge(3, 11)  # Нижний правый угол (верхняя часть)
        letter.add_edge(4, 12)  # Верх вертикали слева
        letter.add_edge(5, 13)  # Верх вертикали справа
        letter.add_edge(6, 14)  # Низ вертикали слева
        letter.add_edge(7, 15)  # Низ вертикали справа
        
        # Грани для лучшей визуализации
        # Верхняя горизонтальная часть
        letter.add_face([0, 1, 9, 8])    # Верхняя грань
        letter.add_face([2, 3, 11, 10])  # Нижняя грань
        letter.add_face([0, 2, 10, 8])   # Левая боковая
        letter.add_face([1, 3, 11, 9])   # Правая боковая
        
        # Вертикальная часть
        letter.add_face([4, 5, 13, 12])  # Верхняя грань
        letter.add_face([6, 7, 15, 14])  # Нижняя грань
        letter.add_face([4, 6, 14, 12])  # Левая боковая
        letter.add_face([5, 7, 15, 13])  # Правая боковая
        
        return letter
    
    @staticmethod
    def create_letter_A():
        """Создает 3D букву A"""
        letter = Object3D()
        letter.name = "Буква A"
        letter.color = "red"
        
        vertices = [
            (-1, 0, 0.5), (0, 2, 0.5), (1, 0, 0.5),
            (-0.5, 1, 0.5), (0.5, 1, 0.5),
            (-1, 0, -0.5), (0, 2, -0.5), (1, 0, -0.5),
            (-0.5, 1, -0.5), (0.5, 1, -0.5)
        ]
        
        for v in vertices:
            letter.add_vertex(*v)
        
        letter.add_edge(0, 1); letter.add_edge(1, 2); letter.add_edge(0, 2)
        letter.add_edge(3, 4)
        letter.add_edge(5, 6); letter.add_edge(6, 7); letter.add_edge(5, 7)
        letter.add_edge(8, 9)
        letter.add_edge(0, 5); letter.add_edge(1, 6); letter.add_edge(2, 7)
        letter.add_edge(3, 8); letter.add_edge(4, 9)
        
        return letter
    
    @staticmethod
    def create_cube():
        """Создает 3D куб для тестирования"""
        cube = Object3D()
        cube.name = "Куб"
        cube.color = "purple"
        
        vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        
        for v in vertices:
            cube.add_vertex(*v)
        
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        for e in edges:
            cube.add_edge(*e)
        
        return cube
    
    @staticmethod
    def get_letter(letter_char):
        """Возвращает 3D букву по символу"""
        letter_char = letter_char.upper()
        
        if letter_char == 'T':
            return Letter3DGenerator.create_letter_T()
        elif letter_char == 'A':
            return Letter3DGenerator.create_letter_A()
        elif letter_char == 'C':
            return Letter3DGenerator.create_cube()
        else:
            return Letter3DGenerator.create_cube()

class Camera:
    """Класс для представления камеры"""
    def __init__(self):
        self.position = Vector3D(0, 0, 10)
        self.target = Vector3D(0, 0, 0)
        self.up = Vector3D(0, 1, 0)
        self.fov = 60
        self.near = 0.1
        self.far = 100
    
    def get_view_matrix(self):
        z_axis = (self.position - self.target).normalize()
        x_axis = self.up.cross(z_axis).normalize()
        y_axis = z_axis.cross(x_axis)
        
        view_matrix = np.identity(4, dtype=float)
        view_matrix[0, 0:3] = x_axis.to_array()
        view_matrix[1, 0:3] = y_axis.to_array()
        view_matrix[2, 0:3] = z_axis.to_array()
        view_matrix[0, 3] = -x_axis.dot(self.position)
        view_matrix[1, 3] = -y_axis.dot(self.position)
        view_matrix[2, 3] = -z_axis.dot(self.position)
        
        return Matrix4x4(view_matrix)

class Canvas3D(tk.Canvas):
    """Холст для отображения 3D объектов"""
    def __init__(self, parent, width=800, height=600, **kwargs):
        super().__init__(parent, width=width, height=height, bg="white", **kwargs)
        self.width = width
        self.height = height
        self.camera = Camera()
        self.objects = []
        self.selected_object = None
        self.show_axes = True
        self.show_grid = True
        self.projection_type = "perspective"
        self.show_projections = False
        
        self.colors = {
            'axes_x': 'red',
            'axes_y': 'green',
            'axes_z': 'blue',
            'grid': '#e0e0e0',
            'selected': 'yellow'
        }
        
        self.draw_axes()
    
    def add_object(self, obj):
        self.objects.append(obj)
        if self.selected_object is None:
            self.selected_object = obj
        self.redraw()
    
    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            if self.selected_object == obj:
                self.selected_object = None if not self.objects else self.objects[0]
            self.redraw()
    
    def clear_objects(self):
        self.objects.clear()
        self.selected_object = None
        self.redraw()
    
    def draw_axes(self):
        self.delete("axes")
        center_x = self.width // 2
        center_y = self.height // 2
        length = 100
        
        self.create_line(center_x, center_y, center_x + length, center_y,
                        fill=self.colors['axes_x'], width=2, arrow=tk.LAST, tags="axes")
        self.create_text(center_x + length + 10, center_y, text="X",
                        fill=self.colors['axes_x'], font=("Arial", 10, "bold"), tags="axes")
        
        self.create_line(center_x, center_y, center_x, center_y - length,
                        fill=self.colors['axes_y'], width=2, arrow=tk.LAST, tags="axes")
        self.create_text(center_x, center_y - length - 10, text="Y",
                        fill=self.colors['axes_y'], font=("Arial", 10, "bold"), tags="axes")
        
        self.create_line(center_x, center_y, center_x - length//2, center_y + length//2,
                        fill=self.colors['axes_z'], width=2, arrow=tk.LAST, tags="axes")
        self.create_text(center_x - length//2 - 10, center_y + length//2 + 10, text="Z",
                        fill=self.colors['axes_z'], font=("Arial", 10, "bold"), tags="axes")
    
    def draw_grid(self):
        self.delete("grid")
        center_x = self.width // 2
        center_y = self.height // 2
        grid_size = 50
        grid_lines = 5
        
        for i in range(-grid_lines, grid_lines + 1):
            y = center_y + i * grid_size
            self.create_line(center_x - grid_lines * grid_size, y,
                           center_x + grid_lines * grid_size, y,
                           fill=self.colors['grid'], width=1, tags="grid")
        
        for i in range(-grid_lines, grid_lines + 1):
            x = center_x + i * grid_size
            self.create_line(x, center_y - grid_lines * grid_size,
                           x, center_y + grid_lines * grid_size,
                           fill=self.colors['grid'], width=1, tags="grid")
    
    def project_point(self, point):
        v = Vector3D(point[0], point[1], point[2])
        
        if self.projection_type == "perspective":
            view_matrix = self.camera.get_view_matrix()
            
            v_view = view_matrix * v
            
            if v_view.z != 0:
                x = (v_view.x / abs(v_view.z) + 1) * self.width / 2
                y = (1 - v_view.y / abs(v_view.z)) * self.height / 2
            else:
                x = (v_view.x + 1) * self.width / 2
                y = (1 - v_view.y) * self.height / 2
        else:
            x = (v.x + 1) * self.width / 2
            y = (1 - v.y) * self.height / 2
        
        return (x, y)
    
    def draw_object(self, obj, is_selected=False):
        if not obj.vertices:
            return
        
        color = self.colors['selected'] if is_selected else obj.color
        projected_vertices = []
        
        for vertex in obj.vertices:
            projected = self.project_point(vertex.to_tuple())
            projected_vertices.append(projected)
        
        for edge in obj.edges:
            v1, v2 = edge
            if v1 < len(projected_vertices) and v2 < len(projected_vertices):
                x1, y1 = projected_vertices[v1]
                x2, y2 = projected_vertices[v2]
                self.create_line(x1, y1, x2, y2, fill=color, width=2, tags="object")
        
        for i, (x, y) in enumerate(projected_vertices):
            size = 3 if not is_selected else 4
            fill_color = color if not is_selected else self.colors['selected']
            self.create_oval(x - size, y - size, x + size, y + size,
                           fill=fill_color, outline=fill_color, tags="object")
    
    def draw_projections(self):
        if not self.objects:
            return
        
        width = self.width // 3
        height = self.height // 3
        offset = 20
        
        xy_rect = (offset, offset, width - offset, height - offset)
        self.create_rectangle(xy_rect, outline="black", width=1, tags="projection")
        self.create_text(width // 2, offset - 10, text="XY", fill="black", tags="projection")
        
        xz_rect = (width + offset, offset, 2*width - offset, height - offset)
        self.create_rectangle(xz_rect, outline="black", width=1, tags="projection")
        self.create_text(width + width // 2, offset - 10, text="XZ", fill="black", tags="projection")
        
        yz_rect = (2*width + offset, offset, 3*width - offset, height - offset)
        self.create_rectangle(yz_rect, outline="black", width=1, tags="projection")
        self.create_text(2*width + width // 2, offset - 10, text="YZ", fill="black", tags="projection")
        
        for obj in self.objects:
            self.draw_projection_xy(obj, xy_rect)
            self.draw_projection_xz(obj, xz_rect)
            self.draw_projection_yz(obj, yz_rect)
    
    def draw_projection_xy(self, obj, rect):
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        
        bbox_min, bbox_max = obj.get_bounding_box()
        obj_width = bbox_max.x - bbox_min.x
        obj_height = bbox_max.y - bbox_min.y
        
        if obj_width == 0 or obj_height == 0:
            return
        
        scale = min(width / obj_width, height / obj_height) * 0.8
        offset_x = x1 + width / 2 - (bbox_min.x + bbox_max.x) / 2 * scale
        offset_y = y1 + height / 2 - (bbox_min.y + bbox_max.y) / 2 * scale
        
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
        self.delete("all")
        
        if self.show_grid:
            self.draw_grid()
        
        self.draw_axes()
        
        for obj in self.objects:
            is_selected = (obj == self.selected_object)
            self.draw_object(obj, is_selected)
        
        if self.show_projections:
            self.draw_projections()
    
    def set_projection(self, projection_type):
        self.projection_type = projection_type
        self.redraw()
    
    def toggle_projections(self):
        self.show_projections = not self.show_projections
        self.redraw()
    
    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.redraw()

class TransformPanel:
    """Панель для управления преобразованиями"""
    def __init__(self, parent, canvas, update_callback):
        self.parent = parent
        self.canvas = canvas
        self.update_callback = update_callback
        self.current_transform_matrix = Matrix4x4()
        
        self.create_widgets()
    
    def create_widgets(self):
        transform_frame = ttk.LabelFrame(self.parent, text="3D Преобразования", padding=10)
        transform_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Масштабирование
        ttk.Label(transform_frame, text="Масштабирование:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(transform_frame, text="X:").grid(row=0, column=1, padx=(5, 0))
        self.scale_x_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.scale_x_var, width=6).grid(row=0, column=2, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=0, column=3, padx=(5, 0))
        self.scale_y_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.scale_y_var, width=6).grid(row=0, column=4, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=0, column=5, padx=(5, 0))
        self.scale_z_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.scale_z_var, width=6).grid(row=0, column=6, padx=2)
        
        ttk.Button(transform_frame, text="Применить", command=self.apply_scaling, width=8).grid(row=0, column=7, padx=(5, 0))
        
        # Перенос
        ttk.Label(transform_frame, text="Перенос:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(transform_frame, text="X:").grid(row=1, column=1, padx=(5, 0))
        self.translate_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.translate_x_var, width=6).grid(row=1, column=2, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=1, column=3, padx=(5, 0))
        self.translate_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.translate_y_var, width=6).grid(row=1, column=4, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=1, column=5, padx=(5, 0))
        self.translate_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.translate_z_var, width=6).grid(row=1, column=6, padx=2)
        
        ttk.Button(transform_frame, text="Применить", command=self.apply_translation, width=8).grid(row=1, column=7, padx=(5, 0))
        
        # Вращение
        ttk.Label(transform_frame, text="Вращение (градусы):").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(transform_frame, text="X:").grid(row=2, column=1, padx=(5, 0))
        self.rotate_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.rotate_x_var, width=6).grid(row=2, column=2, padx=2)
        ttk.Button(transform_frame, text="Вращать", command=lambda: self.apply_rotation('x'), width=8).grid(row=2, column=3, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=2, column=4, padx=(5, 0))
        self.rotate_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.rotate_y_var, width=6).grid(row=2, column=5, padx=2)
        ttk.Button(transform_frame, text="Вращать", command=lambda: self.apply_rotation('y'), width=8).grid(row=2, column=6, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=2, column=7, padx=(5, 0))
        self.rotate_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.rotate_z_var, width=6).grid(row=2, column=8, padx=2)
        ttk.Button(transform_frame, text="Вращать", command=lambda: self.apply_rotation('z'), width=8).grid(row=2, column=9, padx=2)
        
        # Вращение вокруг произвольной оси
        ttk.Label(transform_frame, text="Вращение вокруг оси:").grid(row=3, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(transform_frame, text="X:").grid(row=3, column=1, padx=(5, 0))
        self.axis_x_var = tk.DoubleVar(value=1.0)
        ttk.Entry(transform_frame, textvariable=self.axis_x_var, width=5).grid(row=3, column=2, padx=2)
        
        ttk.Label(transform_frame, text="Y:").grid(row=3, column=3, padx=(5, 0))
        self.axis_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.axis_y_var, width=5).grid(row=3, column=4, padx=2)
        
        ttk.Label(transform_frame, text="Z:").grid(row=3, column=5, padx=(5, 0))
        self.axis_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.axis_z_var, width=5).grid(row=3, column=6, padx=2)
        
        ttk.Label(transform_frame, text="Угол:").grid(row=3, column=7, padx=(5, 0))
        self.axis_angle_var = tk.DoubleVar(value=0.0)
        ttk.Entry(transform_frame, textvariable=self.axis_angle_var, width=6).grid(row=3, column=8, padx=2)
        
        ttk.Button(transform_frame, text="Вращать", command=self.apply_axis_rotation, width=8).grid(row=3, column=9, padx=(5, 0))
        
        # Кнопки управления
        button_frame = ttk.Frame(transform_frame)
        button_frame.grid(row=4, column=0, columnspan=10, pady=5, sticky=tk.W)
        
        ttk.Button(button_frame, text="Сбросить", command=self.reset_transforms, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Показать матрицу", command=self.show_matrix, width=12).pack(side=tk.LEFT, padx=2)
    
    def apply_scaling(self):
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект!")
            return
        
        sx = self.scale_x_var.get()
        sy = self.scale_y_var.get()
        sz = self.scale_z_var.get()
        
        scaling_matrix = Matrix4x4.scaling(sx, sy, sz)
        self.apply_transform(scaling_matrix)
    
    def apply_translation(self):
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект!")
            return
        
        tx = self.translate_x_var.get()
        ty = self.translate_y_var.get()
        tz = self.translate_z_var.get()
        
        translation_matrix = Matrix4x4.translation(tx, ty, tz)
        self.apply_transform(translation_matrix)
    
    def apply_rotation(self, axis):
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
        
        self.apply_transform(rotation_matrix)
    
    def apply_axis_rotation(self):
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
        self.apply_transform(rotation_matrix)
    
    def apply_transform(self, matrix):
        self.current_transform_matrix = matrix * self.current_transform_matrix
        self.canvas.selected_object.apply_transform(matrix)
        self.canvas.redraw()
        self.update_callback()
    
    def reset_transforms(self):
        if not self.canvas.selected_object:
            return
        
        original_letter = Letter3DGenerator.get_letter('T')
        original_letter.color = self.canvas.selected_object.color
        
        index = self.canvas.objects.index(self.canvas.selected_object)
        self.canvas.objects[index] = original_letter
        self.canvas.selected_object = original_letter
        
        self.current_transform_matrix = Matrix4x4()
        self.canvas.redraw()
        self.update_callback()
    
    def show_matrix(self):
        matrix_str = str(self.current_transform_matrix)
        messagebox.showinfo("Матрица преобразования", f"Текущая матрица преобразования:\n\n{matrix_str}")

class ObjectPanel:
    """Панель для управления объектами"""
    def __init__(self, parent, canvas, update_callback):
        self.parent = parent
        self.canvas = canvas
        self.update_callback = update_callback
        
        self.create_widgets()
    
    def create_widgets(self):
        object_frame = ttk.LabelFrame(self.parent, text="Объекты", padding=10)
        object_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор буквы
        ttk.Label(object_frame, text="Буква:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.letter_var = tk.StringVar(value="T")
        letters = ['T', 'A', 'B', 'C', 'Куб']
        
        letter_combo = ttk.Combobox(object_frame, textvariable=self.letter_var,
                                  values=letters, state="readonly", width=8)
        letter_combo.grid(row=0, column=1, padx=(5, 10), pady=2)
        
        # Цвет
        ttk.Label(object_frame, text="Цвет:").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        self.color_var = tk.StringVar(value="blue")
        colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'cyan', 'magenta']
        
        color_combo = ttk.Combobox(object_frame, textvariable=self.color_var,
                                 values=colors, state="readonly", width=8)
        color_combo.grid(row=0, column=3, padx=(5, 0), pady=2)
        
        # Кнопки управления
        button_frame = ttk.Frame(object_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=5, sticky=tk.W)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_object, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Удалить", command=self.remove_object, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Очистить все", command=self.clear_objects, width=10).pack(side=tk.LEFT, padx=2)
        
        # Список объектов
        list_frame = ttk.LabelFrame(self.parent, text="Список объектов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.object_listbox = tk.Listbox(list_frame, height=8, font=("Arial", 9))
        self.object_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.object_listbox.yview)
        self.object_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.object_listbox.bind('<<ListboxSelect>>', self.on_object_selected)
    
    def add_object(self):
        letter = self.letter_var.get()
        color = self.color_var.get()
        
        if letter == 'Куб':
            obj = Letter3DGenerator.create_cube()
            obj.name = "Куб"
        else:
            obj = Letter3DGenerator.get_letter(letter)
            obj.name = f"Буква {letter}"
        
        obj.color = color
        
        # Добавляем номер если уже есть такие объекты
        count = sum(1 for o in self.canvas.objects if o.name.startswith(obj.name))
        if count > 0:
            obj.name = f"{obj.name} ({count + 1})"
        
        self.canvas.add_object(obj)
        self.update_object_list()
    
    def remove_object(self):
        if not self.canvas.selected_object:
            messagebox.showwarning("Предупреждение", "Выберите объект для удаления!")
            return
        
        self.canvas.remove_object(self.canvas.selected_object)
        self.update_object_list()
    
    def clear_objects(self):
        self.canvas.clear_objects()
        self.update_object_list()
    
    def update_object_list(self):
        self.object_listbox.delete(0, tk.END)
        
        for obj in self.canvas.objects:
            self.object_listbox.insert(tk.END, f"{obj.name} ({len(obj.vertices)} вершин)")
        
        if self.canvas.selected_object:
            for i, obj in enumerate(self.canvas.objects):
                if obj == self.canvas.selected_object:
                    self.object_listbox.selection_set(i)
                    break
        
        self.update_callback()
    
    def on_object_selected(self, event):
        selection = self.object_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.canvas.objects):
            self.canvas.selected_object = self.canvas.objects[index]
            self.canvas.redraw()

class ProjectionPanel:
    """Панель для управления проекциями"""
    def __init__(self, parent, canvas, update_callback):
        self.parent = parent
        self.canvas = canvas
        self.update_callback = update_callback
        
        self.create_widgets()
    
    def create_widgets(self):
        projection_frame = ttk.LabelFrame(self.parent, text="Проекции и вид", padding=10)
        projection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Тип проекции
        ttk.Label(projection_frame, text="Тип проекции:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.projection_var = tk.StringVar(value="perspective")
        
        ttk.Radiobutton(projection_frame, text="Перспективная",
                       variable=self.projection_var, value="perspective",
                       command=self.update_projection).grid(row=0, column=1, padx=(5, 10), pady=2)
        
        ttk.Radiobutton(projection_frame, text="Ортографическая",
                       variable=self.projection_var, value="orthographic",
                       command=self.update_projection).grid(row=0, column=2, pady=2)
        
        # Проекции
        ttk.Label(projection_frame, text="Ортографические проекции:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Button(projection_frame, text="Показать", command=self.toggle_projections, width=10).grid(row=1, column=1, padx=(5, 0), pady=2)
        
        # Настройки отображения
        ttk.Label(projection_frame, text="Отображение:").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(projection_frame, text="Сетка", variable=self.grid_var,
                       command=self.toggle_grid).grid(row=2, column=1, padx=(5, 10), pady=2)
        
        self.axes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(projection_frame, text="Оси", variable=self.axes_var,
                       command=self.toggle_axes).grid(row=2, column=2, pady=2)
        
        # Камера
        ttk.Label(projection_frame, text="Камера Z:").grid(row=3, column=0, sticky=tk.W, pady=2)
        
        self.cam_z_var = tk.DoubleVar(value=10.0)
        cam_slider = ttk.Scale(projection_frame, from_=5, to=30, variable=self.cam_z_var,
                              orient=tk.HORIZONTAL, length=150, command=self.update_camera)
        cam_slider.grid(row=3, column=1, columnspan=2, padx=(5, 0), pady=2, sticky=tk.W)
        
        ttk.Button(projection_frame, text="Сброс камеры", command=self.reset_camera, width=12).grid(row=3, column=3, padx=(10, 0), pady=2)
    
    def update_projection(self):
        self.canvas.set_projection(self.projection_var.get())
    
    def toggle_projections(self):
        self.canvas.toggle_projections()
    
    def toggle_grid(self):
        self.canvas.show_grid = self.grid_var.get()
        self.canvas.redraw()
    
    def toggle_axes(self):
        self.canvas.show_axes = self.axes_var.get()
        self.canvas.redraw()
    
    def update_camera(self, value=None):
        self.canvas.camera.position = Vector3D(0, 0, self.cam_z_var.get())
        self.canvas.redraw()
    
    def reset_camera(self):
        self.cam_z_var.set(10.0)
        self.canvas.camera.position = Vector3D(0, 0, 10)
        self.canvas.redraw()

class MainApplication:
    """Главное окно приложения"""
    def __init__(self, root):
        self.root = root
        self.root.title("3D Визуализация буквы Т с преобразованиями и проекциями")
        self.root.geometry("1200x700")
        
        self.create_widgets()
        self.create_menu()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - управление
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Холст для 3D отображения
        self.canvas = Canvas3D(main_frame, width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Панель объектов
        self.object_panel = ObjectPanel(left_frame, self.canvas, self.update_info)
        
        # Панель проекций
        self.projection_panel = ProjectionPanel(left_frame, self.canvas, self.update_info)
        
        # Панель преобразований
        self.transform_panel = TransformPanel(left_frame, self.canvas, self.update_info)
        
        # Панель информации
        info_frame = ttk.LabelFrame(left_frame, text="Информация", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, font=("Courier", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем букву Т по умолчанию
        default_obj = Letter3DGenerator.create_letter_T()
        self.canvas.add_object(default_obj)
        self.object_panel.update_object_list()
        self.update_info()
    
    def create_menu(self):
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
        object_menu.add_command(label="Добавить букву Т", command=lambda: self.add_letter('T'))
        object_menu.add_command(label="Добавить куб", command=self.add_cube)
        object_menu.add_separator()
        object_menu.add_command(label="Очистить все объекты", command=self.object_panel.clear_objects)
        
        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_checkbutton(label="Показать сетку", variable=self.projection_panel.grid_var,
                                 command=self.projection_panel.toggle_grid)
        view_menu.add_checkbutton(label="Показать оси", variable=self.projection_panel.axes_var,
                                 command=self.projection_panel.toggle_axes)
        view_menu.add_command(label="Ортографические проекции", command=self.projection_panel.toggle_projections)
        view_menu.add_separator()
        view_menu.add_command(label="Сброс камеры", command=self.projection_panel.reset_camera)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def add_cube(self):
        cube = Letter3DGenerator.create_cube()
        cube.name = "Куб"
        cube.color = "purple"
        self.canvas.add_object(cube)
        self.object_panel.update_object_list()
    
    def add_letter(self, letter):
        obj = Letter3DGenerator.get_letter(letter)
        obj.name = f"Буква {letter}"
        obj.color = "blue"
        self.canvas.add_object(obj)
        self.object_panel.update_object_list()
    
    def update_info(self):
        self.info_text.delete(1.0, tk.END)
        
        if self.canvas.selected_object:
            obj = self.canvas.selected_object
            info = f"Текущий объект: {obj.name}\n"
            info += f"Цвет: {obj.color}\n"
            info += f"Количество вершин: {len(obj.vertices)}\n"
            info += f"Количество ребер: {len(obj.edges)}\n"
            
            bbox_min, bbox_max = obj.get_bounding_box()
            info += f"\nГраницы объекта:\n"
            info += f"  X: [{bbox_min.x:.2f}, {bbox_max.x:.2f}]\n"
            info += f"  Y: [{bbox_min.y:.2f}, {bbox_max.y:.2f}]\n"
            info += f"  Z: [{bbox_min.z:.2f}, {bbox_max.z:.2f}]\n"
            
            center = obj.get_center()
            info += f"\nЦентр: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})\n"
            
            info += f"\nВсего объектов: {len(self.canvas.objects)}\n"
            info += f"Тип проекции: {self.canvas.projection_type}\n"
            info += f"Проекции показаны: {'Да' if self.canvas.show_projections else 'Нет'}\n"
        else:
            info = "Нет выбранного объекта\n"
        
        self.info_text.insert(1.0, info)
    
    def save_scene(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить сцену",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                scene_data = {
                    'objects': [obj.to_dict() for obj in self.canvas.objects]
                }
                
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(scene_data, file, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Успех", "Сцена сохранена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def load_scene(self):
        filename = filedialog.askopenfilename(
            title="Загрузить сцену",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    scene_data = json.load(file)
                
                self.canvas.clear_objects()
                
                for obj_data in scene_data.get('objects', []):
                    obj = Object3D.from_dict(obj_data)
                    self.canvas.add_object(obj)
                
                self.object_panel.update_object_list()
                messagebox.showinfo("Успех", "Сцена загружена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")
    
    def export_image(self):
        filename = filedialog.asksaveasfilename(
            title="Экспорт изображения",
            defaultextension=".eps",
            filetypes=[("EPS files", "*.eps"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.canvas.postscript(file=filename, colormode='color')
                messagebox.showinfo("Успех", "Изображение сохранено!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def show_about(self):
        about_text = """3D Визуализация буквы Т

Лабораторная работа по компьютерной графике

Реализованные функции:
1. Построение 3D модели буквы Т (первая буква фамилии)
2. Трехмерные преобразования:
   - Масштабирование
   - Перенос
   - Вращение вокруг осей X, Y, Z
   - Вращение вокруг произвольной оси
3. Построение ортографических проекций:
   - XY (вид сверху)
   - XZ (вид спереди)
   - YZ (вид сбоку)
4. Сохранение и загрузка сцен
5. Интерактивное управление

Все требования задания выполнены:
• Использован массив с координатами вершин
• Реализован графический интерфейс с системой координат и осями
• При преобразованиях выводится итоговая матрица преобразования
• Реализованы все три ортографические проекции"""
        
        messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()