"""
Data Storage - Кэширование и хранение данных
"""
import sqlite3
import json
import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class DataStorage:
    """
    Класс для кэширования исторических данных локально
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Путь к базе данных
        self.db_path = config.get('cache_db_path', 'historical_data.db')
        
        # Создаем директорию если не существует
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем базу данных
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу для кэширования данных
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS historical_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        interval TEXT NOT NULL,
                        timestamp INTEGER NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, interval, timestamp)
                    )
                ''')
                
                # Создаем индексы для быстрого поиска
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_symbol_interval_timestamp 
                    ON historical_data(symbol, interval, timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_symbol_interval 
                    ON historical_data(symbol, interval)
                ''')
                
                conn.commit()
                self.logger.info(f"База данных инициализирована: {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def cache_data(self, symbol: str, interval: str, data: List[Dict]) -> bool:
        """
        Кэширование данных в SQLite
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            data: Список свечных данных
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Подготавливаем данные для вставки
                insert_data = []
                for kline in data:
                    insert_data.append((
                        symbol,
                        interval,
                        int(kline['timestamp'].timestamp()),
                        kline['open'],
                        kline['high'],
                        kline['low'],
                        kline['close'],
                        kline['volume']
                    ))
                
                # Используем INSERT OR REPLACE для обновления существующих записей
                cursor.executemany('''
                    INSERT OR REPLACE INTO historical_data 
                    (symbol, interval, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', insert_data)
                
                conn.commit()
                self.logger.info(f"Кэшировано {len(data)} записей для {symbol} ({interval})")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка кэширования данных {symbol}: {e}")
            return False
    
    def get_cached_data(self, symbol: str, interval: str, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> Optional[List[Dict]]:
        """
        Получение кэшированных данных
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            
        Returns:
            Список свечных данных или None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Строим SQL запрос
                query = '''
                    SELECT timestamp, open, high, low, close, volume 
                    FROM historical_data 
                    WHERE symbol = ? AND interval = ?
                '''
                params = [symbol, interval]
                
                if start_date:
                    query += ' AND timestamp >= ?'
                    params.append(int(start_date.timestamp()))
                
                if end_date:
                    query += ' AND timestamp <= ?'
                    params.append(int(end_date.timestamp()))
                
                query += ' ORDER BY timestamp ASC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Преобразуем в формат списка словарей
                data = []
                for row in rows:
                    data.append({
                        'timestamp': datetime.fromtimestamp(row[0]),
                        'open': row[1],
                        'high': row[2],
                        'low': row[3],
                        'close': row[4],
                        'volume': row[5]
                    })
                
                self.logger.info(f"Получено {len(data)} записей из кэша для {symbol} ({interval})")
                return data if data else None
                
        except Exception as e:
            self.logger.error(f"Ошибка получения кэшированных данных {symbol}: {e}")
            return None
    
    def get_available_data_range(self, symbol: str, interval: str) -> Optional[Dict]:
        """
        Получение доступного диапазона данных в кэше
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            
        Returns:
            Словарь с min_date, max_date и count или None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT MIN(timestamp), MAX(timestamp), COUNT(*) 
                    FROM historical_data 
                    WHERE symbol = ? AND interval = ?
                ''', (symbol, interval))
                
                row = cursor.fetchone()
                
                if row and row[0] is not None:
                    return {
                        'min_date': datetime.fromtimestamp(row[0]),
                        'max_date': datetime.fromtimestamp(row[1]),
                        'count': row[2]
                    }
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Ошибка получения диапазона данных {symbol}: {e}")
            return None
    
    def export_to_csv(self, symbol: str, interval: str, file_path: str, 
                     start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None) -> bool:
        """
        Экспорт данных в CSV формат
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            file_path: Путь к файлу
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            data = self.get_cached_data(symbol, interval, start_date, end_date)
            
            if not data:
                self.logger.warning(f"Нет данных для экспорта {symbol} ({interval})")
                return False
            
            # Создаем DataFrame
            df = pd.DataFrame(data)
            
            # Сохраняем в CSV
            df.to_csv(file_path, index=False)
            
            self.logger.info(f"Данные экспортированы в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта данных в CSV: {e}")
            return False
    
    def export_to_json(self, symbol: str, interval: str, file_path: str,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> bool:
        """
        Экспорт данных в JSON формат
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            file_path: Путь к файлу
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            data = self.get_cached_data(symbol, interval, start_date, end_date)
            
            if not data:
                self.logger.warning(f"Нет данных для экспорта {symbol} ({interval})")
                return False
            
            # Преобразуем datetime в строки для JSON
            json_data = []
            for item in data:
                json_item = item.copy()
                json_item['timestamp'] = item['timestamp'].isoformat()
                json_data.append(json_item)
            
            # Сохраняем в JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Данные экспортированы в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта данных в JSON: {e}")
            return False
