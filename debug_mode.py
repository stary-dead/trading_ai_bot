#!/usr/bin/env python3
"""
Запуск торгового агента в дебаг режиме
Автоматически включает debug_mode в конфигурации и запускает main_legacy.py
"""

import json
import subprocess
import sys
import os

def enable_debug_mode():
    """Включает дебаг режим в конфигурации"""
    config_path = 'config.json'
    
    try:
        # Читаем текущую конфигурацию
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Включаем дебаг режим
        if 'ai' not in config:
            config['ai'] = {}
        
        config['ai']['debug_mode'] = True
        
        # Сохраняем обновленную конфигурацию
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("[SUCCESS] Дебаг режим включен в config.json")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при включении дебаг режима: {e}")
        return False

def disable_debug_mode():
    """Отключает дебаг режим в конфигурации"""
    config_path = 'config.json'
    
    try:
        # Читаем текущую конфигурацию
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Отключаем дебаг режим
        if 'ai' in config:
            config['ai']['debug_mode'] = False
        
        # Сохраняем обновленную конфигурацию
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("[SUCCESS] Дебаг режим отключен в config.json")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при отключении дебаг режима: {e}")
        return False

def main():
    """Главная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == 'off':
        # Отключить дебаг режим
        disable_debug_mode()
        return
    
    print("[DEBUG] Запуск торгового агента в ДЕБАГ РЕЖИМЕ")
    print("=" * 50)
    print("В дебаг режиме:")
    print("[+] ИИ анализ отключен (экономия токенов)")
    print("[+] Используются fallback функции")
    print("[+] Техническая аналитика работает")
    print("[+] Риск-менеджмент работает")
    print("=" * 50)
    
    # Включаем дебаг режим
    if not enable_debug_mode():
        return
    
    # Запускаем торгового агента
    try:
        print("\n[START] Запуск main_legacy.py...")
        subprocess.run([sys.executable, 'main_legacy.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при запуске: {e}")
    except KeyboardInterrupt:
        print("\n[STOP] Получен сигнал остановки")
    finally:
        # Спрашиваем, нужно ли отключить дебаг режим
        try:
            choice = input("\n[?] Отключить дебаг режим? (y/N): ").strip().lower()
            if choice in ['y', 'yes', 'да', 'д']:
                disable_debug_mode()
        except:
            pass  # Игнорируем ошибки ввода

if __name__ == "__main__":
    main()
