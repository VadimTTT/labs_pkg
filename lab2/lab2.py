import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageFile, ImageTk
import os
from pathlib import Path
import time
from typing import Dict, List, Any
from collections import Counter
import threading

ImageFile.LOAD_TRUNCATED_IMAGES = True

class ImageMetadataExtractor:
    @staticmethod
    def get_basic_info(file_path: str) -> Dict[str, Any]:
        try:
            with Image.open(file_path) as img:
                info = {
                    'filename': os.path.basename(file_path),
                    'format': img.format or 'Unknown',
                    'size_pixels': f"{img.width} × {img.height}",
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'color_depth': ImageMetadataExtractor._get_color_depth(img),
                    'dpi': ImageMetadataExtractor._get_dpi(img),
                    'compression': ImageMetadataExtractor._get_compression(img),
                    'file_size': f"{os.path.getsize(file_path) / 1024:.1f} KB",
                    'path': file_path,
                    'additional_info': {}
                }
                
                info['additional_info'] = ImageMetadataExtractor._get_additional_info(img, file_path)
                return info
        except Exception as e:
            return {
                'filename': os.path.basename(file_path),
                'error': str(e),
                'size_pixels': 'N/A',
                'dpi': 'N/A', 
                'color_depth': 'N/A',
                'compression': 'N/A',
                'path': file_path
            }
    
    @staticmethod
    def _get_color_depth(img: Image.Image) -> str:
        bits_per_pixel = {
            '1': '1 bit (монохром)',
            'L': '8 bits (grayscale)',
            'P': '8 bits (палитра)',
            'RGB': '24 bits (True Color)',
            'RGBA': '32 bits (True Color + Alpha)',
            'CMYK': '32 bits (CMYK)',
            'LAB': '24 bits (LAB)',
            'HSV': '24 bits (HSV)',
            'I': '32 bits (целочисленные)',
            'F': '32 bits (с плавающей точкой)'
        }
        return bits_per_pixel.get(img.mode, f"Неизвестно ({img.mode})")
    
    @staticmethod
    def _get_dpi(img: Image.Image) -> str:
        dpi = img.info.get('dpi')
        if dpi:
            if isinstance(dpi, tuple):
                return f"{dpi[0]} × {dpi[1]} DPI"
            else:
                return f"{dpi} DPI"
        return "Не указано"
    
    @staticmethod
    def _get_compression(img: Image.Image) -> str:
        compression_names = {
            'tiff_lzw': 'LZW',
            'tiff_adobe_deflate': 'Adobe Deflate',
            'tiff_deflate': 'Deflate',
            'jpeg': 'JPEG',
            'zip': 'ZIP',
            'packbits': 'PackBits',
            'group4': 'Group 4 Fax',
            'group3': 'Group 3 Fax'
        }
        
        compression = img.info.get('compression')
        if compression:
            if isinstance(compression, str):
                return compression_names.get(compression, compression)
            else:
                return str(compression)
        
        if img.format == 'JPEG':
            return 'JPEG'
            
        return "Без сжатия"
    
    @staticmethod
    def _get_additional_info(img: Image.Image, file_path: str) -> Dict[str, Any]:
        additional = {}
        
        try:
            if img.format == 'JPEG':
                additional = ImageMetadataExtractor._get_jpeg_info(img)
            elif img.format == 'GIF':
                additional = ImageMetadataExtractor._get_gif_info(img)
            elif img.format == 'PNG':
                additional = ImageMetadataExtractor._get_png_info(img)
            elif img.format == 'TIFF':
                additional = ImageMetadataExtractor._get_tiff_info(img)
            elif img.format == 'BMP':
                additional = ImageMetadataExtractor._get_bmp_info(img)
            elif img.format == 'PCX':
                additional = ImageMetadataExtractor._get_pcx_info(img)
                
        except Exception as e:
            additional['error'] = f"Ошибка получения доп. информации: {str(e)}"
        
        return additional
    
    @staticmethod
    def _get_jpeg_info(img: Image.Image) -> Dict[str, Any]:
        info = {}
        
        quality = img.info.get('quality')
        if quality:
            info['Качество JPEG'] = f"{quality}%"
        
        progressive = img.info.get('progressive')
        if progressive is not None:
            info['Прогрессивный'] = "Да" if progressive else "Нет"
        
        exif = img._getexif()
        if exif:
            info['EXIF тегов'] = len(exif)
            
            exif_tags = {
                271: 'Производитель камеры',
                272: 'Модель камеры',
                274: 'Ориентация',
                306: 'Дата и время',
                36867: 'Дата съёмки',
                33434: 'Выдержка',
                33437: 'Диафрагма',
                34855: 'ISO'
            }
            
            for tag_id, tag_name in exif_tags.items():
                if tag_id in exif:
                    info[tag_name] = exif[tag_id]
        
        return info
    
    @staticmethod
    def _get_gif_info(img: Image.Image) -> Dict[str, Any]:
        info = {}
        
        try:
            frame_count = 0
            while True:
                frame_count += 1
                img.seek(frame_count)
        except EOFError:
            info['Количество кадров'] = frame_count
        
        if img.mode == 'P':
            palette = img.getpalette()
            if palette:
                info['Цветов в палитре'] = len(palette) // 3
        
        duration = img.info.get('duration')
        if duration:
            info['Длительность кадра (мс)'] = duration
        
        return info
    
    @staticmethod
    def _get_png_info(img: Image.Image) -> Dict[str, Any]:
        info = {}
        
        compression = img.info.get('compression')
        if compression:
            info['Тип сжатия PNG'] = compression
        
        gamma = img.info.get('gamma')
        if gamma:
            info['Гамма'] = gamma
        
        return info
    
    @staticmethod
    def _get_tiff_info(img: Image.Image) -> Dict[str, Any]:
        info = {}
        
        if hasattr(img, 'tag'):
            tags = img.tag
            info['Количество TIFF тегов'] = len(tags)
            
            tiff_tags = {
                256: 'Ширина',
                257: 'Высота', 
                258: 'Битов на выборку',
                259: 'Сжатие',
                262: 'Фотометрическая интерпретация',
                296: 'Разрешение',
                306: 'Дата и время'
            }
            
            for tag_id, tag_name in tiff_tags.items():
                if tag_id in tags:
                    info[tag_name] = tags[tag_id]
        
        return info
    
    @staticmethod
    def _get_bmp_info(img: Image.Image) -> Dict[str, Any]:
        return {'Тип': 'Bitmap без сжатия'}
    
    @staticmethod
    def _get_pcx_info(img: Image.Image) -> Dict[str, Any]:
        info = {}
        info['Формат'] = 'PCX (ZSoft Paintbrush)'
        return info

class ImageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Анализатор метаданных изображений")
        self.root.geometry("1200x800")
        
        self.current_file_info = None
        self.all_results = []
        self.image_extensions = {'.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.bmp', '.png', '.pcx'}
        self.extractor = ImageMetadataExtractor()
        
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Error.TLabel', foreground='red')
        style.configure('Success.TLabel', foreground='green')
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Анализатор метаданных изображений", style='Title.TLabel')
        title_label.pack(pady=10)
        
        desc_label = ttk.Label(main_frame, text="Поддерживаемые форматы: JPEG, GIF, TIFF, BMP, PNG, PCX", 
                              font=('Arial', 10))
        desc_label.pack()
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="Выбрать файл", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Выбрать папку", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Экспорт в CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Готово", font=('Arial', 9))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.single_file_frame = ttk.Frame(notebook)
        self.folder_frame = ttk.Frame(notebook)
        
        notebook.add(self.single_file_frame, text="Один файл")
        notebook.add(self.folder_frame, text="Папка с файлами")
        
        self.create_single_file_tab()
        self.create_folder_tab()
    
    def create_single_file_tab(self):
        top_frame = ttk.Frame(self.single_file_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        self.selected_file_label = ttk.Label(top_frame, text="Файл не выбран", font=('Arial', 10))
        self.selected_file_label.pack(side=tk.LEFT)
        
        content_frame = ttk.Frame(self.single_file_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_frame = ttk.LabelFrame(content_frame, text="Изображение", padding="10")
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.image_label = ttk.Label(self.image_frame, text="Изображение не выбрано")
        self.image_label.pack(expand=True)
        
        self.info_frame = ttk.LabelFrame(content_frame, text="Метаданные", padding="10")
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.info_text = tk.Text(self.info_frame, width=50, height=20, font=('Courier', 9))
        scrollbar = ttk.Scrollbar(self.info_frame, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_folder_tab(self):
        top_frame = ttk.Frame(self.folder_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        self.folder_path_label = ttk.Label(top_frame, text="Папка не выбрана", font=('Arial', 10))
        self.folder_path_label.pack(side=tk.LEFT)
        
        ttk.Button(top_frame, text="Начать обработку", command=self.start_folder_processing).pack(side=tk.RIGHT, padx=5)
        
        self.progress_frame = ttk.Frame(self.folder_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.folder_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        results_frame = ttk.Frame(self.folder_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Файл', 'Размер', 'DPI', 'Глубина цвета', 'Сжатие', 'Формат', 'Статус')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_tree.bind('<<TreeviewSelect>>', self.on_result_select)
        
        stats_frame = ttk.LabelFrame(self.folder_frame, text="Статистика", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=5, font=('Arial', 9))
        self.stats_text.pack(fill=tk.X)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл изображения",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.gif *.tif *.tiff *.bmp *.png *.pcx"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file_label.config(text=os.path.basename(file_path))
            self.process_single_file(file_path)
    
    def process_single_file(self, file_path):
        self.status_label.config(text="Обработка...")
        self.root.update()
        
        try:
            info = self.extractor.get_basic_info(file_path)
            self.current_file_info = info
            
            self.display_file_info(info)
            
            if 'error' not in info:
                self.display_image_preview(file_path)
                self.status_label.config(text="Готово", style='Success.TLabel')
            else:
                self.status_label.config(text=f"Ошибка: {info['error']}", style='Error.TLabel')
                
        except Exception as e:
            self.status_label.config(text=f"Ошибка: {str(e)}", style='Error.TLabel')
    
    def display_file_info(self, info):
        self.info_text.delete(1.0, tk.END)
        
        if 'error' in info:
            self.info_text.insert(tk.END, f"ОШИБКА ЧТЕНИЯ:\n{info['error']}\n\n")
            return
        
        basic_info = f"""Имя файла: {info['filename']}
Размер (пиксели): {info['size_pixels']}
Разрешение (DPI): {info['dpi']}
Глубина цвета: {info['color_depth']}
Сжатие: {info['compression']}
Формат: {info.get('format', 'N/A')}
Цветовая модель: {info.get('mode', 'N/A')}
Размер файла: {info.get('file_size', 'N/A')}
Путь: {info.get('path', 'N/A')}
"""
        
        self.info_text.insert(tk.END, "ОСНОВНАЯ ИНФОРМАЦИЯ:\n")
        self.info_text.insert(tk.END, basic_info)
        
        if info.get('additional_info'):
            self.info_text.insert(tk.END, "\nДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:\n")
            for key, value in info['additional_info'].items():
                self.info_text.insert(tk.END, f"{key}: {value}\n")
    
    def display_image_preview(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except:
            self.image_label.config(image='', text="Не удалось загрузить изображение")
    
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку с изображениями")
        
        if folder_path:
            self.folder_path_label.config(text=folder_path)
            self.all_results = []
            self.results_tree.delete(*self.results_tree.get_children())
            self.stats_text.delete(1.0, tk.END)
    
    def start_folder_processing(self):
        folder_path = self.folder_path_label.cget('text')
        
        if folder_path == "Папка не выбрана" or not os.path.exists(folder_path):
            messagebox.showwarning("Внимание", "Сначала выберите папку")
            return
        
        self.results_tree.delete(*self.results_tree.get_children())
        self.stats_text.delete(1.0, tk.END)
        self.status_label.config(text="Поиск файлов...")
        self.root.update()
        
        image_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if Path(file).suffix.lower() in self.image_extensions:
                    image_files.append(os.path.join(root, file))
        
        if not image_files:
            messagebox.showinfo("Информация", "В выбранной папке не найдено изображений")
            return
        
        if len(image_files) > 100000:
            if not messagebox.askyesno("Внимание", f"Найдено {len(image_files)} файлов. Обработка может занять много времени. Продолжить?"):
                return
        
        self.progress_bar['maximum'] = len(image_files)
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self.process_folder_files, args=(image_files,))
        thread.daemon = True
        thread.start()
    
    def process_folder_files(self, image_files):
        start_time = time.time()
        self.all_results = []
        
        for i, file_path in enumerate(image_files):
            if i % 10 == 0:
                self.root.after(0, self.update_progress, i, len(image_files), os.path.basename(file_path))
            
            info = self.extractor.get_basic_info(file_path)
            self.all_results.append(info)
            
            status = 'OK' if 'error' not in info else 'Ошибка'
            values = (
                os.path.basename(file_path),
                info.get('size_pixels', 'N/A'),
                info.get('dpi', 'N/A'),
                info.get('color_depth', 'N/A'),
                info.get('compression', 'N/A'),
                info.get('format', 'N/A'),
                status
            )
            
            self.root.after(0, self.add_tree_item, values, status)
        
        processing_time = time.time() - start_time
        
        self.root.after(0, self.finish_processing, len(image_files), processing_time)
    
    def update_progress(self, current, total, filename):
        self.progress_bar['value'] = current
        self.progress_label.config(text=f"Обработано: {current}/{total} ({filename})")
        self.status_label.config(text=f"Обработка... {current}/{total}")
    
    def add_tree_item(self, values, status):
        item = self.results_tree.insert('', 'end', values=values)
        if status == 'Ошибка':
            self.results_tree.item(item, tags=('error',))
        
        self.results_tree.tag_configure('error', foreground='red')
    
    def finish_processing(self, total_files, processing_time):
        self.progress_bar['value'] = total_files
        self.progress_label.config(text=f"Обработка завершена! Файлов: {total_files}")
        self.status_label.config(text=f"Готово ({processing_time:.1f} сек)", style='Success.TLabel')
        
        self.update_statistics(total_files, processing_time)
    
    def update_statistics(self, total_files, processing_time):
        successful = len([r for r in self.all_results if 'error' not in r])
        errors = total_files - successful
        
        formats_count = Counter()
        for result in self.all_results:
            if 'error' not in result:
                fmt = result.get('format', 'Unknown')
                formats_count[fmt] += 1
        
        stats_text = f"""ОБРАБОТКА ЗАВЕРШЕНА
----------------------
Всего файлов: {total_files}
Успешно: {successful}
Ошибок: {errors}
Время: {processing_time:.2f} сек
Скорость: {total_files/processing_time:.1f} файлов/сек

Распределение по форматам:
"""
        
        for fmt, count in formats_count.most_common():
            stats_text += f"  {fmt}: {count} файлов\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def on_result_select(self, event):
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        filename = self.results_tree.item(item)['values'][0]
        
        for result in self.all_results:
            if result['filename'] == filename:
                self.display_selected_result(result)
                break
    
    def display_selected_result(self, info):
        if 'path' in info and os.path.exists(info['path']):
            self.display_image_preview(info['path'])
        
        self.info_text.delete(1.0, tk.END)
        self.display_file_info(info)
    
    def clear_all(self):
        self.selected_file_label.config(text="Файл не выбран")
        self.folder_path_label.config(text="Папка не выбрана")
        self.image_label.config(image='', text="Изображение не выбрано")
        self.info_text.delete(1.0, tk.END)
        self.results_tree.delete(*self.results_tree.get_children())
        self.stats_text.delete(1.0, tk.END)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="")
        self.status_label.config(text="Готово")
        self.all_results = []
    
    def export_to_csv(self):
        if not self.all_results:
            messagebox.showinfo("Информация", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Экспорт в CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            import csv
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Файл', 'Размер', 'DPI', 'Глубина цвета', 'Сжатие', 'Формат', 'Статус', 'Путь']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.all_results:
                    row = {
                        'Файл': result['filename'],
                        'Размер': result.get('size_pixels', 'N/A'),
                        'DPI': result.get('dpi', 'N/A'),
                        'Глубина цвета': result.get('color_depth', 'N/A'),
                        'Сжатие': result.get('compression', 'N/A'),
                        'Формат': result.get('format', 'N/A'),
                        'Статус': 'OK' if 'error' not in result else f"Ошибка: {result['error']}",
                        'Путь': result.get('path', 'N/A')
                    }
                    writer.writerow(row)
            
            messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")

def main():
    root = tk.Tk()
    app = ImageAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()