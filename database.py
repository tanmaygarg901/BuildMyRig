import sqlite3
import logging
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "buildmyrig.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_real_data()
    
    def init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create parts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                performance_score INTEGER NOT NULL,
                compatibility_tags TEXT NOT NULL,
                brand TEXT NOT NULL,
                hardware_brand TEXT,
                specifications TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Populate database with sample PC parts data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        sample_parts = [
            # CPUs
            ("AMD Ryzen 5 5600X", "cpu", 199.99, 85, json.dumps({"socket": "AM4", "tdp": 65}), "AMD", json.dumps({"cores": 6, "threads": 12, "base_clock": "3.7GHz"})),
            ("AMD Ryzen 7 5800X", "cpu", 299.99, 95, json.dumps({"socket": "AM4", "tdp": 105}), "AMD", json.dumps({"cores": 8, "threads": 16, "base_clock": "3.8GHz"})),
            ("Intel Core i5-12400F", "cpu", 179.99, 82, json.dumps({"socket": "LGA1700", "tdp": 65}), "Intel", json.dumps({"cores": 6, "threads": 12, "base_clock": "2.5GHz"})),
            ("Intel Core i7-12700K", "cpu", 349.99, 98, json.dumps({"socket": "LGA1700", "tdp": 125}), "Intel", json.dumps({"cores": 12, "threads": 20, "base_clock": "3.6GHz"})),
            ("AMD Ryzen 9 5900X", "cpu", 429.99, 105, json.dumps({"socket": "AM4", "tdp": 105}), "AMD", json.dumps({"cores": 12, "threads": 24, "base_clock": "3.7GHz"})),
            
            # GPUs
            ("NVIDIA RTX 3060", "gpu", 329.99, 75, json.dumps({"pcie": "4.0", "power": 170}), "NVIDIA", json.dumps({"vram": "12GB", "memory_type": "GDDR6"})),
            ("NVIDIA RTX 3070", "gpu", 499.99, 90, json.dumps({"pcie": "4.0", "power": 220}), "NVIDIA", json.dumps({"vram": "8GB", "memory_type": "GDDR6"})),
            ("NVIDIA RTX 4060", "gpu", 299.99, 78, json.dumps({"pcie": "4.0", "power": 115}), "NVIDIA", json.dumps({"vram": "8GB", "memory_type": "GDDR6"})),
            ("AMD RX 6700 XT", "gpu", 379.99, 85, json.dumps({"pcie": "4.0", "power": 230}), "AMD", json.dumps({"vram": "12GB", "memory_type": "GDDR6"})),
            ("AMD RX 7600", "gpu", 269.99, 72, json.dumps({"pcie": "4.0", "power": 165}), "AMD", json.dumps({"vram": "8GB", "memory_type": "GDDR6"})),
            
            # Motherboards
            ("MSI B450 TOMAHAWK MAX", "motherboard", 109.99, 70, json.dumps({"socket": "AM4", "ram_slots": 4, "max_ram": "128GB"}), "MSI", json.dumps({"chipset": "B450", "form_factor": "ATX"})),
            ("ASUS ROG STRIX B550-F", "motherboard", 189.99, 85, json.dumps({"socket": "AM4", "ram_slots": 4, "max_ram": "128GB"}), "ASUS", json.dumps({"chipset": "B550", "form_factor": "ATX"})),
            ("MSI PRO B660M-A", "motherboard", 129.99, 75, json.dumps({"socket": "LGA1700", "ram_slots": 4, "max_ram": "128GB"}), "MSI", json.dumps({"chipset": "B660", "form_factor": "mATX"})),
            ("ASUS PRIME Z690-P", "motherboard", 199.99, 90, json.dumps({"socket": "LGA1700", "ram_slots": 4, "max_ram": "128GB"}), "ASUS", json.dumps({"chipset": "Z690", "form_factor": "ATX"})),
            
            # RAM
            ("Corsair Vengeance LPX 16GB DDR4-3200", "ram", 59.99, 70, json.dumps({"type": "DDR4", "speed": "3200", "capacity": "16GB"}), "Corsair", json.dumps({"modules": 2, "timing": "16-18-18-36"})),
            ("G.Skill Ripjaws V 32GB DDR4-3600", "ram", 119.99, 85, json.dumps({"type": "DDR4", "speed": "3600", "capacity": "32GB"}), "G.Skill", json.dumps({"modules": 2, "timing": "16-19-19-39"})),
            ("Corsair Vengeance LPX 16GB DDR5-5600", "ram", 89.99, 90, json.dumps({"type": "DDR5", "speed": "5600", "capacity": "16GB"}), "Corsair", json.dumps({"modules": 2, "timing": "36-36-36-76"})),
            ("G.Skill Trident Z5 32GB DDR5-6000", "ram", 179.99, 95, json.dumps({"type": "DDR5", "speed": "6000", "capacity": "32GB"}), "G.Skill", json.dumps({"modules": 2, "timing": "36-36-36-76"})),
            
            # Storage
            ("Samsung 980 1TB NVMe SSD", "storage", 79.99, 85, json.dumps({"type": "NVMe", "capacity": "1TB", "interface": "PCIe 3.0"}), "Samsung", json.dumps({"read_speed": "3500MB/s", "write_speed": "3000MB/s"})),
            ("WD Black SN850X 1TB NVMe SSD", "storage", 99.99, 95, json.dumps({"type": "NVMe", "capacity": "1TB", "interface": "PCIe 4.0"}), "WD", json.dumps({"read_speed": "7300MB/s", "write_speed": "6600MB/s"})),
            ("Crucial MX4 1TB SATA SSD", "storage", 69.99, 75, json.dumps({"type": "SATA", "capacity": "1TB", "interface": "SATA 3.0"}), "Crucial", json.dumps({"read_speed": "560MB/s", "write_speed": "510MB/s"})),
            ("Seagate Barracuda 2TB HDD", "storage", 54.99, 60, json.dumps({"type": "HDD", "capacity": "2TB", "interface": "SATA 3.0"}), "Seagate", json.dumps({"rpm": "7200", "cache": "256MB"})),
            
            # PSUs
            ("Corsair CV650 650W", "psu", 69.99, 75, json.dumps({"wattage": 650, "efficiency": "80+ Bronze", "modular": False}), "Corsair", json.dumps({"certification": "80+ Bronze", "warranty": "3 years"})),
            ("EVGA SuperNOVA 750W", "psu", 119.99, 90, json.dumps({"wattage": 750, "efficiency": "80+ Gold", "modular": True}), "EVGA", json.dumps({"certification": "80+ Gold", "warranty": "10 years"})),
            ("Seasonic Focus GX-850", "psu", 149.99, 95, json.dumps({"wattage": 850, "efficiency": "80+ Gold", "modular": True}), "Seasonic", json.dumps({"certification": "80+ Gold", "warranty": "10 years"})),
            ("Corsair RM1000x", "psu", 199.99, 98, json.dumps({"wattage": 1000, "efficiency": "80+ Gold", "modular": True}), "Corsair", json.dumps({"certification": "80+ Gold", "warranty": "10 years"})),
            
            # Cases
            ("Fractal Design Define R5", "case", 109.99, 80, json.dumps({"form_factor": "ATX", "max_gpu_length": "440mm"}), "Fractal Design", json.dumps({"type": "Mid Tower", "color": "Black"})),
            ("NZXT H510", "case", 79.99, 75, json.dumps({"form_factor": "ATX", "max_gpu_length": "381mm"}), "NZXT", json.dumps({"type": "Mid Tower", "color": "Black/White"})),
            ("Corsair 4000D", "case", 94.99, 85, json.dumps({"form_factor": "ATX", "max_gpu_length": "360mm"}), "Corsair", json.dumps({"type": "Mid Tower", "color": "Black"})),
            ("Cooler Master MasterBox Q300L", "case", 44.99, 65, json.dumps({"form_factor": "mATX", "max_gpu_length": "360mm"}), "Cooler Master", json.dumps({"type": "Mini Tower", "color": "Black"})),
        ]
        
        cursor.executemany('''
            INSERT INTO parts (name, category, price, performance_score, compatibility_tags, brand, specifications)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_parts)
        
        conn.commit()
        conn.close()
    
    def populate_real_data(self):
        """Populate database with real PC parts data from CSV files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Check if CSV files exist
        if not (Path("price_data").exists() and Path("performance_data").exists()):
            print("CSV data directories not found. Loading sample data instead.")
            conn.close()
            self.populate_sample_data()
            return
        
        # Load real data using CSV loader
        try:
            from csv_loader import CSVDataLoader
            loader = CSVDataLoader(self.db_path)
            loader.load_all_data()
            print("Real data loaded successfully!")
        except Exception as e:
            print(f"Error loading real data: {e}")
            print("Falling back to sample data...")
            conn.close()
            self.populate_sample_data()
    
    def get_parts_by_category(self, category: str, brand_preference: Optional[Tuple[str, str]] = None) -> List[Dict]:
        """Get parts by category with optional brand filtering. Tuple indicates (brand, hardware_brand)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM parts WHERE category = ?"
        params = [category]
        
        if brand_preference:
            brand, hardware_brand = brand_preference
            brand_condition = "brand = ?"
            hardware_brand_condition = "hardware_brand = ?"
            if brand != "any":
                query += f" AND {brand_condition}"
                params.append(brand)
            if hardware_brand != "any":
                query += f" AND {hardware_brand_condition}"
                params.append(hardware_brand)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        parts = []
        for row in results:
            parts.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "price": row[3],
                "performance_score": row[4],
                "compatibility_tags": json.loads(row[5]),
                "brand": row[6],
                "hardware_brand": row[7],
                "specifications": json.loads(row[8])
            })
        
        conn.close()
        return parts
    
    def get_parts_by_category_paginated(self, category: str, brand_preference: Optional[Tuple[str, str]] = None, 
                                       limit: int = 50, offset: int = 0, 
                                       sort_by: str = "performance_score", sort_order: str = "desc") -> List[Dict]:
        """Get parts by category with pagination and sorting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM parts WHERE category = ?"
        params = [category]
        
        if brand_preference:
            brand, hardware_brand = brand_preference
            if brand != "any":
                query += " AND brand = ?"
                params.append(brand)
            if hardware_brand != "any":
                query += " AND hardware_brand = ?"
                params.append(hardware_brand)
        
        # Add sorting
        if sort_by in ["performance_score", "price", "name"]:
            query += f" ORDER BY {sort_by}"
            if sort_order.lower() == "desc":
                query += " DESC"
            else:
                query += " ASC"
        
        # Add pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        parts = []
        for row in results:
            parts.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "price": row[3],
                "performance_score": row[4],
                "compatibility_tags": json.loads(row[5]),
                "brand": row[6],
                "hardware_brand": row[7],
                "specifications": json.loads(row[8])
            })
        
        conn.close()
        return parts

    def get_all_parts(self) -> List[Dict]:
        """Get all parts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, category, price, performance_score, compatibility_tags, brand, hardware_brand, specifications FROM parts")
        results = cursor.fetchall()
        
        parts = []
        for row in results:
            parts.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "price": row[3],
                "performance_score": row[4],
                "compatibility_tags": json.loads(row[5]),
                "brand": row[6],
                "hardware_brand": row[7],
                "specifications": json.loads(row[8])
            })
        
        conn.close()
        return parts
