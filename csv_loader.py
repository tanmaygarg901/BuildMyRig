import pandas as pd
import json
import sqlite3
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class CSVDataLoader:
    def __init__(self, db_path: str = "buildmyrig.db"):
        self.db_path = db_path
        self.price_data_dir = Path("price_data")
        self.performance_data_dir = Path("performance_data")
        
        # Filters for relevant parts
        self.relevant_cpu_patterns = [
            'Ryzen 9 7950X3D', 'Ryzen 9 7900X3D', 'Ryzen 7 7800X3D', 'Ryzen 5 7600X3D',
            'Ryzen 9 7950X', 'Ryzen 9 7900X', 'Ryzen 7 7700X', 'Ryzen 5 7600X', 'Ryzen 5 7600',
            'Ryzen 9 5950X', 'Ryzen 9 5900X', 'Ryzen 7 5800X3D', 'Ryzen 7 5800X', 'Ryzen 7 5700X',
            'Ryzen 5 5600X', 'Ryzen 5 5600', 'Ryzen 5 5500',
            'i9-14900K', 'i9-13900K', 'i9-12900K',
            'i7-14700K', 'i7-13700K', 'i7-12700K', 'i7-11700K',
            'i5-14600K', 'i5-13600K', 'i5-12600K', 'i5-12400F', 'i5-11400F',
            'i3-12100F', 'i3-13100F'
        ]
        
        self.relevant_gpu_patterns = [
            'RTX 4090', 'RTX 4080', 'RTX 4070 Ti', 'RTX 4070', 'RTX 4060 Ti', 'RTX 4060',
            'RTX 3090', 'RTX 3080', 'RTX 3070', 'RTX 3060',
            'RX 7900 XTX', 'RX 7900 XT', 'RX 7800 XT', 'RX 7700 XT', 'RX 7600',
            'RX 6950 XT', 'RX 6900 XT', 'RX 6800 XT', 'RX 6700 XT', 'RX 6600'
        ]
        
        self.min_price_thresholds = {
            'cpu': 50,
            'gpu': 100,
            'motherboard': 60,
            'ram': 30,
            'storage': 25,
            'psu': 40,
            'case': 30
        }
        
        self.max_price_thresholds = {
            'cpu': 800,
            'gpu': 2000,
            'motherboard': 500,
            'ram': 400,
            'storage': 300,
            'psu': 300,
            'case': 200
        }
        
    def load_all_data(self):
        """Load all CSV data and populate the database"""
        print("Loading CSV data...")
        
        # Initialize database
        self.init_database()
        
        # Load price data
        price_data = self.load_price_data()
        
        # Load performance data
        performance_data = self.load_performance_data()
        
        # Merge price and performance data
        merged_data = self.merge_price_performance_data(price_data, performance_data)
        
        # Populate database
        self.populate_database(merged_data)
        
        print("Database populated with real data!")
        
    def init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing table to start fresh
        cursor.execute("DROP TABLE IF EXISTS parts")
        
        # Create parts table with enhanced schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                performance_score INTEGER NOT NULL,
                compatibility_tags TEXT NOT NULL,
                brand TEXT NOT NULL,
                hardware_brand TEXT NOT NULL,
                specifications TEXT NOT NULL,
                benchmark_rank INTEGER,
                benchmark_samples INTEGER,
                benchmark_url TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_price_data(self) -> Dict[str, pd.DataFrame]:
        """Load all price data CSV files"""
        price_data = {}
        
        # Define CSV file mappings
        csv_files = {
            "cpu": "CPUs.csv",
            "gpu": "GPUs.csv",
            "motherboard": "Motherboards.csv",
            "ram": "RAMs.csv",
            "storage": "SSDs.csv",
            "psu": "Power Supply.csv",
            "case": "Cases.csv"
        }
        
        for category, filename in csv_files.items():
            filepath = self.price_data_dir / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                price_data[category] = df
                print(f"Loaded {len(df)} {category} parts from {filename}")
            else:
                print(f"Warning: {filename} not found")
                
        return price_data
    
    def load_performance_data(self) -> Dict[str, pd.DataFrame]:
        """Load all performance data CSV files"""
        performance_data = {}
        
        # Define performance CSV files
        perf_files = {
            "cpu": "CPU_UserBenchmarks.csv",
            "gpu": "GPU_UserBenchmarks.csv",
            "ram": "RAM_UserBenchmarks.csv",
            "storage": "SSD_UserBenchmarks.csv"
        }
        
        for category, filename in perf_files.items():
            filepath = self.performance_data_dir / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                performance_data[category] = df
                print(f"Loaded {len(df)} {category} benchmark entries from {filename}")
            else:
                print(f"Warning: {filename} not found")
                
        return performance_data
    
    def merge_price_performance_data(self, price_data: Dict[str, pd.DataFrame], 
                                    performance_data: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """Merge price and performance data"""
        merged_data = {}
        
        # Process each category
        for category in price_data.keys():
            print(f"Processing {category}...")
            merged_data[category] = []
            
            price_df = price_data[category]
            perf_df = performance_data.get(category)
            
            for _, row in price_df.iterrows():
                part_data = self._process_part_row(row, category, perf_df)
                if part_data:
                    merged_data[category].append(part_data)
                    
        return merged_data
    
    def _process_part_row(self, row: pd.Series, category: str, 
                         perf_df: Optional[pd.DataFrame]) -> Optional[Dict]:
        """Process a single part row"""
        try:
            # Extract basic info
            name = str(row['name']).strip()
            if pd.isna(row['price']) or row['price'] == '':
                return None
                
            price = float(row['price'])
            if price <= 0:
                return None
                
            # Extract manufacturer brand (MSI, ASUS, etc.)
            manufacturer = self._extract_manufacturer(name)
            
            # Extract hardware brand (AMD, NVIDIA, Intel)
            hardware_brand = self._extract_hardware_brand(name, category)
            
            # Get performance score
            performance_score = self._get_performance_score(name, category, perf_df)
            
            # Build compatibility tags and specifications
            compatibility_tags = self._build_compatibility_tags(row, category)
            specifications = self._build_specifications(row, category)
            
            # Add hardware brand to compatibility tags for filtering
            compatibility_tags['hardware_brand'] = hardware_brand
            
            # Get benchmark info if available
            benchmark_info = self._get_benchmark_info(name, category, perf_df)
            
            return {
                'name': name,
                'category': category,
                'price': price,
                'performance_score': performance_score,
                'compatibility_tags': json.dumps(compatibility_tags),
                'brand': manufacturer,
                'hardware_brand': hardware_brand,
                'specifications': json.dumps(specifications),
                'benchmark_rank': benchmark_info.get('rank'),
                'benchmark_samples': benchmark_info.get('samples'),
                'benchmark_url': benchmark_info.get('url')
            }
            
        except Exception as e:
            print(f"Error processing part {row.get('name', 'unknown')}: {e}")
            return None
    
    def _extract_manufacturer(self, name: str) -> str:
        """Extract manufacturer brand from part name (MSI, ASUS, etc.)"""
        manufacturers = {
            'MSI': ['MSI'],
            'ASUS': ['ASUS', 'Asus', 'ROG', 'TUF', 'PRIME', 'ProArt'],
            'Gigabyte': ['Gigabyte', 'AORUS'],
            'ASRock': ['ASRock'],
            'Corsair': ['Corsair'],
            'G.Skill': ['G.Skill', 'Trident', 'Ripjaws', 'Flare'],
            'Samsung': ['Samsung'],
            'Western Digital': ['Western Digital', 'WD'],
            'Seagate': ['Seagate'],
            'Crucial': ['Crucial'],
            'Kingston': ['Kingston'],
            'EVGA': ['EVGA'],
            'Seasonic': ['Seasonic', 'SeaSonic'],
            'Thermaltake': ['Thermaltake'],
            'Cooler Master': ['Cooler Master'],
            'NZXT': ['NZXT'],
            'Fractal Design': ['Fractal Design'],
            'Lian Li': ['Lian Li'],
            'be quiet!': ['be quiet!'],
            'Phanteks': ['Phanteks'],
            'Deepcool': ['Deepcool'],
            'Montech': ['Montech'],
            'TEAMGROUP': ['TEAMGROUP'],
            'Patriot': ['Patriot'],
            'Silicon Power': ['Silicon Power'],
            'ADATA': ['ADATA'],
            'PNY': ['PNY'],
            'Zotac': ['Zotac'],
            'Sapphire': ['Sapphire'],
            'PowerColor': ['PowerColor'],
            'XFX': ['XFX'],
            'Intel': ['Intel'],  # Intel is both manufacturer and hardware brand
            'AMD': ['AMD'],      # AMD is both manufacturer and hardware brand
        }
        
        name_upper = name.upper()
        for brand, patterns in manufacturers.items():
            if any(pattern.upper() in name_upper for pattern in patterns):
                return brand
                
        # Try to extract first word as brand
        first_word = name.split()[0] if name.split() else "Unknown"
        return first_word
    
    def _extract_hardware_brand(self, name: str, category: str) -> str:
        """Extract hardware brand (AMD, NVIDIA, Intel) from part name"""
        name_upper = name.upper()
        
        if category == "cpu":
            # CPU hardware brands
            if any(x in name_upper for x in ['INTEL', 'CORE I', 'CELERON', 'PENTIUM', 'XEON']):
                return 'Intel'
            elif any(x in name_upper for x in ['AMD', 'RYZEN', 'THREADRIPPER', 'ATHLON', 'FX']):
                return 'AMD'
        elif category == "gpu":
            # GPU hardware brands
            if any(x in name_upper for x in ['NVIDIA', 'GEFORCE', 'RTX', 'GTX', 'QUADRO', 'TITAN']):
                return 'NVIDIA'
            elif any(x in name_upper for x in ['AMD', 'RADEON', 'RX ', 'FIREPRO', 'VEGA']):
                return 'AMD'
            elif any(x in name_upper for x in ['INTEL', 'ARC', 'IRIS']):
                return 'Intel'
        elif category == "motherboard":
            # Motherboard chipset brands
            if any(x in name_upper for x in ['INTEL', 'LGA', 'Z790', 'Z690', 'B660', 'H610']):
                return 'Intel'
            elif any(x in name_upper for x in ['AMD', 'AM4', 'AM5', 'X570', 'B550', 'A520']):
                return 'AMD'
        
        # Default to manufacturer if no specific hardware brand detected
        return self._extract_manufacturer(name)
    
    def _get_performance_score(self, name: str, category: str, 
                              perf_df: Optional[pd.DataFrame]) -> int:
        """Get performance score from benchmark data"""
        if perf_df is None:
            return self._estimate_performance_score(name, category)
            
        # Try to match by name similarity
        best_match = self._find_best_match(name, perf_df)
        if best_match is not None:
            return int(best_match['Benchmark'])
            
        return self._estimate_performance_score(name, category)
    
    def _find_best_match(self, name: str, perf_df: pd.DataFrame) -> Optional[Dict]:
        """Find best matching benchmark entry"""
        name_clean = self._clean_name_for_matching(name)
        
        best_score = 0
        best_match = None
        
        for _, row in perf_df.iterrows():
            if 'Model' in row:
                model_clean = self._clean_name_for_matching(str(row['Model']))
                score = self._calculate_similarity_score(name_clean, model_clean)
                
                if score > best_score and score > 0.6:  # Threshold for similarity
                    best_score = score
                    best_match = row
                    
        return best_match
    
    def _clean_name_for_matching(self, name: str) -> str:
        """Clean name for better matching"""
        # Remove common words and normalize
        name = re.sub(r'\b(GB|TB|MHz|GHz|DDR[4-5]|ATX|mATX|Mini-ITX)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(Gaming|OC|Overclocked|Edition|Series|Black|White|RGB)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[^\w\s]', ' ', name)
        name = ' '.join(name.split())
        return name.lower()
    
    def _calculate_similarity_score(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two names"""
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _estimate_performance_score(self, name: str, category: str) -> int:
        """Estimate performance score when benchmark data is not available"""
        # Basic estimation based on part names and categories
        if category == "cpu":
            return self._estimate_cpu_performance(name)
        elif category == "gpu":
            return self._estimate_gpu_performance(name)
        elif category == "ram":
            return self._estimate_ram_performance(name)
        elif category == "storage":
            return self._estimate_storage_performance(name)
        else:
            return 70  # Default score for other components
    
    def _estimate_cpu_performance(self, name: str) -> int:
        """Estimate CPU performance score"""
        name_upper = name.upper()
        
        # High-end CPUs
        if any(x in name_upper for x in ['I9', 'RYZEN 9', 'THREADRIPPER']):
            return 95
        elif any(x in name_upper for x in ['I7', 'RYZEN 7']):
            return 85
        elif any(x in name_upper for x in ['I5', 'RYZEN 5']):
            return 75
        elif any(x in name_upper for x in ['I3', 'RYZEN 3']):
            return 65
        else:
            return 60
    
    def _estimate_gpu_performance(self, name: str) -> int:
        """Estimate GPU performance score"""
        name_upper = name.upper()
        
        # NVIDIA RTX series
        if 'RTX 4090' in name_upper:
            return 155
        elif 'RTX 4080' in name_upper:
            return 125
        elif 'RTX 4070' in name_upper:
            return 105
        elif 'RTX 4060' in name_upper:
            return 85
        elif 'RTX 3080' in name_upper:
            return 110
        elif 'RTX 3070' in name_upper:
            return 95
        elif 'RTX 3060' in name_upper:
            return 80
        elif 'RTX 2080' in name_upper:
            return 85
        elif 'RTX 2070' in name_upper:
            return 80
        elif 'RTX 2060' in name_upper:
            return 70
        elif 'GTX 1660' in name_upper:
            return 65
        elif 'GTX 1650' in name_upper:
            return 55
        # AMD RX series
        elif 'RX 7900' in name_upper:
            return 125
        elif 'RX 7800' in name_upper:
            return 115
        elif 'RX 7700' in name_upper:
            return 100
        elif 'RX 6900' in name_upper:
            return 105
        elif 'RX 6800' in name_upper:
            return 95
        elif 'RX 6700' in name_upper:
            return 85
        elif 'RX 6600' in name_upper:
            return 75
        elif 'RX 6500' in name_upper:
            return 60
        else:
            return 70  # Default for unrecognized GPUs
    
    def _estimate_ram_performance(self, name: str) -> int:
        """Estimate RAM performance score"""
        name_upper = name.upper()
        
        # DDR5 generally performs better than DDR4
        if 'DDR5' in name_upper or '5600' in name_upper or '6000' in name_upper:
            return 85
        elif 'DDR4' in name_upper:
            if '3600' in name_upper or '4000' in name_upper:
                return 80
            elif '3200' in name_upper:
                return 75
            else:
                return 70
        else:
            return 70
    
    def _estimate_storage_performance(self, name: str) -> int:
        """Estimate storage performance score"""
        name_upper = name.upper()
        
        if 'NVME' in name_upper or 'M.2' in name_upper:
            if 'PCIE 4.0' in name_upper or 'PCIE 5.0' in name_upper:
                return 90
            else:
                return 85
        elif 'SSD' in name_upper:
            return 75
        else:
            return 60  # HDD
    
    def _build_compatibility_tags(self, row: pd.Series, category: str) -> Dict:
        """Build compatibility tags for a part"""
        tags = {}
        
        if category == "cpu":
            tags["socket"] = self._extract_socket(row, category)
            tags["tdp"] = self._extract_tdp(row)
            tags["cores"] = self._extract_cores(row)
            
        elif category == "gpu":
            tags["pcie"] = "4.0"  # Default
            tags["power"] = self._extract_power(row)
            tags["length"] = self._extract_length(row)
            
        elif category == "motherboard":
            tags["socket"] = self._extract_socket(row, category)
            tags["form_factor"] = self._extract_form_factor(row)
            tags["ram_slots"] = self._extract_ram_slots(row)
            tags["max_memory"] = self._extract_max_memory(row)
            
        elif category == "ram":
            tags["type"] = self._extract_ram_type(row)
            tags["speed"] = self._extract_ram_speed(row)
            tags["capacity"] = self._extract_ram_capacity(row)
            
        elif category == "storage":
            tags["type"] = self._extract_storage_type(row)
            tags["capacity"] = self._extract_storage_capacity(row)
            tags["interface"] = self._extract_storage_interface(row)
            
        elif category == "psu":
            tags["wattage"] = self._extract_wattage(row)
            tags["efficiency"] = self._extract_efficiency(row)
            tags["modular"] = self._extract_modular(row)
            
        elif category == "case":
            tags["form_factor"] = self._extract_case_form_factor(row)
            tags["max_gpu_length"] = self._extract_max_gpu_length(row)
            
        return tags
    
    def _build_specifications(self, row: pd.Series, category: str) -> Dict:
        """Build specifications for a part"""
        specs = {}
        
        # Add all non-null columns as specifications
        for col in row.index:
            if col not in ['name', 'price'] and pd.notna(row[col]) and row[col] != '':
                specs[col] = str(row[col])
                
        return specs
    
    def _extract_socket(self, row: pd.Series, category: str) -> str:
        """Extract socket information"""
        if category == "cpu":
            name = str(row['name']).upper()
            if 'INTEL' in name or 'I3' in name or 'I5' in name or 'I7' in name or 'I9' in name:
                if '12' in name or '13' in name or '14' in name:
                    return "LGA1700"
                elif '10' in name or '11' in name:
                    return "LGA1200"
                else:
                    return "LGA1151"
            elif 'AMD' in name or 'RYZEN' in name:
                if '7000' in name or '8000' in name or '9000' in name:
                    return "AM5"
                else:
                    return "AM4"
        elif category == "motherboard" and 'socket' in row:
            return str(row['socket'])
        return "Unknown"
    
    def _extract_tdp(self, row: pd.Series) -> int:
        """Extract TDP from CPU data"""
        if 'tdp' in row and pd.notna(row['tdp']):
            return int(row['tdp'])
        return 65  # Default TDP
    
    def _extract_cores(self, row: pd.Series) -> int:
        """Extract core count from CPU data"""
        if 'core_count' in row and pd.notna(row['core_count']):
            return int(row['core_count'])
        return 4  # Default core count
    
    def _extract_power(self, row: pd.Series) -> int:
        """Extract power consumption from GPU data"""
        # Estimate based on GPU tier
        name = str(row['name']).upper()
        if 'RTX 4090' in name:
            return 450
        elif 'RTX 4080' in name:
            return 320
        elif 'RTX 4070' in name:
            return 200
        elif 'RTX 4060' in name:
            return 115
        elif 'RTX 30' in name:
            return 220
        elif 'RX 7900' in name:
            return 300
        elif 'RX 7800' in name:
            return 263
        elif 'RX 7700' in name:
            return 245
        return 150  # Default
    
    def _extract_length(self, row: pd.Series) -> int:
        """Extract GPU length"""
        if 'length' in row and pd.notna(row['length']):
            return int(row['length'])
        return 280  # Default length in mm
    
    def _extract_form_factor(self, row: pd.Series) -> str:
        """Extract motherboard form factor"""
        if 'form_factor' in row and pd.notna(row['form_factor']):
            return str(row['form_factor'])
        return "ATX"
    
    def _extract_ram_slots(self, row: pd.Series) -> int:
        """Extract RAM slots from motherboard"""
        if 'memory_slots' in row and pd.notna(row['memory_slots']):
            return int(row['memory_slots'])
        return 4
    
    def _extract_max_memory(self, row: pd.Series) -> int:
        """Extract max memory from motherboard"""
        if 'max_memory' in row and pd.notna(row['max_memory']):
            return int(row['max_memory'])
        return 128
    
    def _extract_ram_type(self, row: pd.Series) -> str:
        """Extract RAM type"""
        name = str(row['name']).upper()
        if 'DDR5' in name:
            return "DDR5"
        elif 'DDR4' in name:
            return "DDR4"
        elif 'DDR3' in name:
            return "DDR3"
        return "DDR4"  # Default
    
    def _extract_ram_speed(self, row: pd.Series) -> int:
        """Extract RAM speed"""
        if 'speed' in row and pd.notna(row['speed']):
            speed_str = str(row['speed'])
            # Extract number from speed string
            import re
            numbers = re.findall(r'\d+', speed_str)
            if numbers:
                return int(numbers[-1])  # Take the last number (usually the speed)
        return 3200  # Default
    
    def _extract_ram_capacity(self, row: pd.Series) -> str:
        """Extract RAM capacity"""
        name = str(row['name'])
        # Extract capacity from name
        import re
        capacity_match = re.search(r'(\d+)\s*GB', name, re.IGNORECASE)
        if capacity_match:
            return capacity_match.group(1) + "GB"
        return "16GB"  # Default
    
    def _extract_storage_type(self, row: pd.Series) -> str:
        """Extract storage type"""
        if 'type' in row and pd.notna(row['type']):
            return str(row['type'])
        name = str(row['name']).upper()
        if 'SSD' in name:
            return "SSD"
        elif 'HDD' in name:
            return "HDD"
        return "SSD"  # Default
    
    def _extract_storage_capacity(self, row: pd.Series) -> str:
        """Extract storage capacity"""
        if 'capacity' in row and pd.notna(row['capacity']):
            capacity = int(row['capacity'])
            if capacity >= 1000:
                return f"{capacity // 1000}TB"
            else:
                return f"{capacity}GB"
        return "1TB"  # Default
    
    def _extract_storage_interface(self, row: pd.Series) -> str:
        """Extract storage interface"""
        if 'interface' in row and pd.notna(row['interface']):
            return str(row['interface'])
        return "SATA 6.0 Gb/s"  # Default
    
    def _extract_wattage(self, row: pd.Series) -> int:
        """Extract PSU wattage"""
        if 'wattage' in row and pd.notna(row['wattage']):
            return int(row['wattage'])
        return 650  # Default
    
    def _extract_efficiency(self, row: pd.Series) -> str:
        """Extract PSU efficiency"""
        if 'efficiency' in row and pd.notna(row['efficiency']):
            return str(row['efficiency'])
        return "80+ Bronze"  # Default
    
    def _extract_modular(self, row: pd.Series) -> bool:
        """Extract PSU modularity"""
        if 'modular' in row and pd.notna(row['modular']):
            modular = str(row['modular']).lower()
            return modular in ['true', '1', 'yes', 'full', 'semi']
        return False
    
    def _extract_case_form_factor(self, row: pd.Series) -> str:
        """Extract case form factor"""
        if 'type' in row and pd.notna(row['type']):
            case_type = str(row['type']).lower()
            if 'atx' in case_type:
                return "ATX"
            elif 'micro' in case_type or 'matx' in case_type:
                return "mATX"
            elif 'mini' in case_type:
                return "Mini-ITX"
        return "ATX"  # Default
    
    def _extract_max_gpu_length(self, row: pd.Series) -> int:
        """Extract maximum GPU length for case"""
        # Default based on case type
        if 'type' in row and pd.notna(row['type']):
            case_type = str(row['type']).lower()
            if 'mini' in case_type:
                return 200
            elif 'micro' in case_type:
                return 300
        return 350  # Default for ATX cases
    
    def _get_benchmark_info(self, name: str, category: str, 
                           perf_df: Optional[pd.DataFrame]) -> Dict:
        """Get benchmark information"""
        info = {}
        
        if perf_df is not None:
            best_match = self._find_best_match(name, perf_df)
            if best_match is not None:
                info['rank'] = best_match.get('Rank')
                info['samples'] = best_match.get('Samples')
                info['url'] = best_match.get('URL')
                
        return info
    
    def populate_database(self, merged_data: Dict[str, List[Dict]]):
        """Populate database with merged data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total_parts = 0
        for category, parts in merged_data.items():
            print(f"Inserting {len(parts)} {category} parts...")
            
            for part in parts:
                cursor.execute('''
                    INSERT INTO parts (name, category, price, performance_score, 
                                     compatibility_tags, brand, hardware_brand, specifications,
                                     benchmark_rank, benchmark_samples, benchmark_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    part['name'],
                    part['category'],
                    part['price'],
                    part['performance_score'],
                    part['compatibility_tags'],
                    part['brand'],
                    part['hardware_brand'],
                    part['specifications'],
                    part['benchmark_rank'],
                    part['benchmark_samples'],
                    part['benchmark_url']
                ))
                
            total_parts += len(parts)
            
        conn.commit()
        conn.close()
        
        print(f"Successfully inserted {total_parts} parts into database!")

if __name__ == "__main__":
    loader = CSVDataLoader()
    loader.load_all_data()
