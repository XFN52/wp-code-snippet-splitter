#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для разделения WP Code сниппетов из JSON экспорта на отдельные файлы
"""
import json
import os
import re
from pathlib import Path

def sanitize_filename(title):
    """Очистка имени файла от недопустимых символов"""
    # Убираем недопустимые символы для имён файлов Windows
    filename = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Ограничиваем длину до 100 символов
    filename = filename[:100].strip()
    # Убираем точки в конце
    filename = filename.rstrip('.')
    return filename if filename else 'snippet'

def get_file_extension(code_type):
    """Определяем расширение файла по типу кода"""
    extensions = {
        'php': '.php',
        'html': '.html', 
        'css': '.css',
        'js': '.js',
        'javascript': '.js',
        'text': '.txt'
    }
    return extensions.get(code_type.lower(), '.txt')

def split_snippets(json_file_path, output_dir='snippets'):
    """Основная функция разделения сниппетов"""
    
    # Создаём директорию для вывода
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"Загружаю JSON файл: {json_file_path}")
    
    try:
        # Читаем JSON файл
        with open(json_file_path, 'r', encoding='utf-8') as f:
            snippets = json.load(f)
        
        if not isinstance(snippets, list):
            print("Ошибка: JSON должен содержать массив сниппетов")
            return
        
        print(f"Найдено сниппетов: {len(snippets)}")
        
        # Обрабатываем каждый сниппет
        for i, snippet in enumerate(snippets, 1):
            try:
                # Получаем данные сниппета
                snippet_id = snippet.get('id', f'snippet_{i}')
                title = snippet.get('title', f'Сниппет {i}')
                code = snippet.get('code', '')
                code_type = snippet.get('code_type', 'text')
                location = snippet.get('location', 'everywhere')
                auto_insert = snippet.get('auto_insert', 0)
                priority = snippet.get('priority', 10)
                tags = snippet.get('tags', [])
                note = snippet.get('note', '')
                
                # Создаём имя файла
                safe_title = sanitize_filename(title)
                extension = get_file_extension(code_type)
                filename = f"{snippet_id}_{safe_title}{extension}"
                
                # Полный путь к файлу
                file_path = output_path / filename
                
                # Нормализуем переносы строк и очищаем от избыточных пустых строк
                normalized_code = code.replace('\r\n', '\n').replace('\r', '\n')
                cleaned_code = re.sub(r'\n\s*\n\s*\n+', '\n\n', normalized_code.strip())
                
                # Формируем содержимое файла
                if code_type == 'php':
                    content = '<?php\n' + cleaned_code
                else:
                    content = cleaned_code
                
                # Записываем в файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"[{i:3d}/{len(snippets)}] Создан: {filename}")
                
            except Exception as e:
                print(f"Ошибка при обработке сниппета {i}: {e}")
                continue
        
        print(f"\nГотово! Создано файлов в директории '{output_dir}'")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл {json_file_path} не найден")
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON: {e}")
    except Exception as e:
        print(f"Общая ошибка: {e}")

def main():
    """Основная функция"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python split_snippets.py <путь_к_json_файлу> [директория_вывода]")
        print("Пример: python split_snippets.py wpcode-snippets-export-2025-08-25.json output_snippets")
        return
    
    json_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output_snippets'
    
    split_snippets(json_file, output_dir)

if __name__ == '__main__':
    main()