from typing import List, Dict, Optional, Tuple
from itertools import product
import json
from database import Database
from models import BuildResponse, PartResponse

class RecommendationEngine:
    def __init__(self, database: Database):
        self.db = database
        self.required_categories = ["cpu", "gpu", "motherboard", "ram", "storage", "psu", "case"]
        
    def get_recommendations(self, budget: float, brand_preferences: Dict[str, str], use_case: str) -> List[BuildResponse]:
        """Generate optimized PC build recommendations"""
        
        # Get filtered parts for each category
        parts_by_category = {}
        for category in self.required_categories:
            brand_pref = brand_preferences.get(category)
            # Convert brand preference to tuple format (brand, hardware_brand)
            if brand_pref:
                if category in ["cpu", "gpu"]:
                    # For CPU and GPU, use hardware_brand for filtering
                    brand_tuple = ("any", brand_pref)
                else:
                    # For other categories, use brand for filtering
                    brand_tuple = (brand_pref, "any")
            else:
                brand_tuple = None
            parts_by_category[category] = self.db.get_parts_by_category(category, brand_tuple)
        
        # Apply use case filtering and scoring adjustments
        parts_by_category = self._apply_use_case_filtering(parts_by_category, use_case)
        
        # Generate all possible combinations within budget
        valid_builds = self._generate_valid_builds(parts_by_category, budget, use_case)
        
        # Sort by performance with emphasis on using more of the budget
        def build_score(build):
            performance_weight = 0.6
            budget_utilization_weight = 0.4
            
            normalized_performance = build.performance_score / 1000
            budget_utilization = build.total_price / budget
            
            return (normalized_performance * performance_weight) + (budget_utilization * budget_utilization_weight)

        valid_builds.sort(key=build_score, reverse=True)
        
        # Ensure we have diverse builds by filtering out very similar ones
        diverse_builds = self._ensure_build_diversity(valid_builds)
        
        return diverse_builds[:3]
    
    def _apply_use_case_filtering(self, parts_by_category: Dict, use_case: str) -> Dict:
        """Apply use case specific filtering and scoring adjustments"""
        
        if use_case.lower() == "gaming":
            # For gaming, prioritize GPU and CPU performance
            for part in parts_by_category.get("gpu", []):
                part["performance_score"] = int(part["performance_score"] * 1.15)  # Moderate boost
            for part in parts_by_category.get("cpu", []):
                part["performance_score"] = int(part["performance_score"] * 1.1)  # Moderate boost
                
        elif use_case.lower() == "workstation":
            # For workstation, prioritize CPU and RAM
            for part in parts_by_category.get("cpu", []):
                part["performance_score"] = int(part["performance_score"] * 1.2)  # Higher CPU boost
            for part in parts_by_category.get("ram", []):
                part["performance_score"] = int(part["performance_score"] * 1.15)  # RAM boost
            for part in parts_by_category.get("storage", []):
                if part["compatibility_tags"].get("type") == "NVMe":
                    part["performance_score"] = int(part["performance_score"] * 1.1)  # NVMe boost

        elif use_case.lower() == "general":
            # For general use, balance components
            for part in parts_by_category.get("cpu", []):
                part["performance_score"] = int(part["performance_score"] * 1.05)  # Small boost
            for part in parts_by_category.get("gpu", []):
                part["performance_score"] = int(part["performance_score"] * 1.05)  # Small boost
        
        return parts_by_category
    
    def _generate_valid_builds(self, parts_by_category: Dict, budget: float, use_case: str) -> List[BuildResponse]:
        """Generate all valid build combinations within budget"""
        valid_builds = []
        
        # Filter parts by budget constraints (rough filtering)
        filtered_parts = self._filter_by_budget_constraints(parts_by_category, budget, use_case)
        
        # Generate combinations (limited to prevent explosion)
        max_combinations_per_category = 6  # Reduced for better performance
        
        for category in filtered_parts:
            # Sort by a weighted combination of performance and value
            def calculate_weighted_score(part):
                performance_score = part["performance_score"]
                price = part["price"]
                
                if price > 0:
                    value_score = performance_score / price
                    # More balanced weighting
                    weighted_score = (performance_score * 0.6) + (value_score * 0.4)
                else:
                    weighted_score = 0
                    
                return weighted_score
            
            filtered_parts[category].sort(key=calculate_weighted_score, reverse=True)
            filtered_parts[category] = filtered_parts[category][:max_combinations_per_category]
        
        # Generate build combinations
        categories = list(filtered_parts.keys())
        if len(categories) == len(self.required_categories):
            for combination in product(*[filtered_parts[cat] for cat in categories]):
                build_dict = {cat: part for cat, part in zip(categories, combination)}
                
                # Check compatibility, budget, and minimum requirements
                if (self._check_compatibility(build_dict) and 
                    self._check_budget(build_dict, budget) and 
                    self._check_minimum_requirements(build_dict)):
                    build_response = self._create_build_response(build_dict)
                    valid_builds.append(build_response)
        
        return valid_builds
    
    def _check_minimum_requirements(self, build: Dict) -> bool:
        """Check if build meets minimum requirements"""
        try:
            ram = build["ram"]
            ram_capacity = self._get_ram_capacity(ram)
            
            # Minimum 8GB RAM requirement
            if ram_capacity < 8:
                return False
            
            # Check minimum storage size
            storage = build["storage"]
            storage_name = storage.get("name", "").lower()
            
            # Ensure reasonable storage capacity (at least 240GB)
            if "32gb" in storage_name or "64gb" in storage_name or "128gb" in storage_name:
                return False
            
            return True
            
        except (KeyError, ValueError, TypeError):
            return False
    
    def _get_ram_capacity(self, part: Dict) -> int:
        """Extracts the RAM capacity from the part name."""
        try:
            name = part.get("name", "")
            # Extract capacity from name using common patterns
            import re
            capacity_match = re.search(r'(\d+)\s*GB', name, re.IGNORECASE)
            if capacity_match:
                return int(capacity_match.group(1))
            return 16  # Default to 16GB if not found
        except (ValueError, AttributeError):
            return 16  # Default to 16GB if parsing fails
    
    def _filter_by_budget_constraints(self, parts_by_category: Dict, budget: float, use_case: str) -> Dict:
        """Filter parts by rough budget constraints with intelligent balancing"""
        filtered = {}
        
        # Define minimum and maximum spending limits per component to prevent extreme imbalances
        component_limits = {
            "cpu": {"min": 0.15, "max": 0.35},
            "gpu": {"min": 0.15, "max": 0.40},
            "motherboard": {"min": 0.08, "max": 0.20},
            "ram": {"min": 0.08, "max": 0.25},
            "storage": {"min": 0.05, "max": 0.15},
            "psu": {"min": 0.05, "max": 0.12},
            "case": {"min": 0.03, "max": 0.10}
        }
        
        # Balanced budget allocation that prevents extreme spending on any single component
        if use_case.lower() == "gaming":
            budget_allocation = {
                "cpu": 0.25,
                "gpu": 0.30,
                "motherboard": 0.12,
                "ram": 0.12,
                "storage": 0.08,
                "psu": 0.08,
                "case": 0.05
            }
        elif use_case.lower() == "workstation":
            budget_allocation = {
                "cpu": 0.28,
                "gpu": 0.25,  # Ensure workstation still gets decent GPU
                "motherboard": 0.12,
                "ram": 0.18,
                "storage": 0.10,
                "psu": 0.07,
                "case": 0.05
            }
        else:  # general
            budget_allocation = {
                "cpu": 0.26,
                "gpu": 0.28,
                "motherboard": 0.12,
                "ram": 0.14,
                "storage": 0.08,
                "psu": 0.07,
                "case": 0.05
            }
        
        for category, parts in parts_by_category.items():
            # Use only well-known brands
            popular_brands = {"Intel", "AMD", "NVIDIA", "Corsair", "MSI", "Asus", "Samsung", "G.Skill", "Crucial", "EVGA", "Seasonic", "Western Digital", "WD", "Gigabyte", "ASRock", "Thermaltake", "Cooler Master", "NZXT", "Fractal Design", "be quiet!", "Seagate", "Kingston", "Patriot", "TEAMGROUP", "ADATA", "SilverStone", "Antec", "Phanteks", "Lian Li"}
            valid_parts = [part for part in parts if part["price"] > 0 and part["price"] <= budget * 0.8 and part["brand"] in popular_brands]

            # Apply category-specific filtering
            if category == "ram":
                if use_case.lower() == "gaming" or use_case.lower() == "general":
                    # For gaming/general, prefer 8GB-32GB
                    valid_parts = [part for part in valid_parts if 8 <= self._get_ram_capacity(part) <= 32]
                elif use_case.lower() == "workstation":
                    # For workstation, allow up to 64GB
                    valid_parts = [part for part in valid_parts if 8 <= self._get_ram_capacity(part) <= 64]
            
            if not valid_parts:
                # More relaxed fallback
                valid_parts = [part for part in parts if part["price"] > 0 and part["price"] <= budget]
                if not valid_parts:
                    valid_parts = sorted(parts, key=lambda x: x["price"])[:50]
            
            # Create a more balanced selection
            category_parts = []
            
            # Calculate balanced budget ranges using min/max limits
            category_budget = budget * budget_allocation.get(category, 0.1)
            min_limit = budget * component_limits[category]["min"]
            max_limit = budget * component_limits[category]["max"]
            
            # Set reasonable price ranges that prevent extreme spending
            min_price = max(min_limit * 0.5, category_budget * 0.4)  # At least 40% of category budget
            max_price = min(max_limit, category_budget * 2.5)  # No more than 2.5x category budget or component max
            
            # 1. Add parts within balanced price range
            balanced_parts = [part for part in valid_parts if min_price <= part["price"] <= max_price]
            if balanced_parts:
                # Sort by performance within balanced price range
                balanced_parts = sorted(balanced_parts, key=lambda x: x["performance_score"], reverse=True)
                category_parts.extend(balanced_parts[:12])
            
            # 2. Add some budget-friendly options (but not too cheap)
            budget_friendly_min = min_limit * 0.8
            budget_friendly_max = category_budget * 1.2
            budget_parts = [part for part in valid_parts if budget_friendly_min <= part["price"] <= budget_friendly_max]
            budget_parts = sorted(budget_parts, key=lambda x: x["performance_score"] / x["price"], reverse=True)
            for part in budget_parts[:8]:
                if part["id"] not in [p["id"] for p in category_parts]:
                    category_parts.append(part)
            
            # 3. Add some premium options (but within limits)
            premium_min = category_budget * 1.2
            premium_max = max_limit * 0.9
            if premium_max > premium_min:
                premium_parts = [part for part in valid_parts if premium_min <= part["price"] <= premium_max]
                premium_parts = sorted(premium_parts, key=lambda x: x["performance_score"], reverse=True)
                for part in premium_parts[:5]:
                    if part["id"] not in [p["id"] for p in category_parts]:
                        category_parts.append(part)
            
            # 4. Fill remaining slots with balanced options
            if len(category_parts) < 15 and valid_parts:
                remaining_parts = [part for part in valid_parts if part["id"] not in [p["id"] for p in category_parts]]
                # Filter out extremely cheap or expensive parts
                remaining_parts = [part for part in remaining_parts if min_limit * 0.6 <= part["price"] <= max_limit * 0.8]
                remaining_parts = sorted(remaining_parts, key=lambda x: x["performance_score"], reverse=True)
                category_parts.extend(remaining_parts[:15 - len(category_parts)])
            
            filtered[category] = category_parts[:20]  # Limit to 20 parts per category
        
        return filtered
    
    def _check_compatibility(self, build: Dict) -> bool:
        """Check comprehensive compatibility between components"""
        try:
            cpu = build["cpu"]
            motherboard = build["motherboard"]
            ram = build["ram"]
            gpu = build["gpu"]
            psu = build["psu"]
            case = build["case"]
            
            # Check CPU-Motherboard socket compatibility
            cpu_socket = cpu["compatibility_tags"].get("socket", "Unknown")
            mb_socket = motherboard["compatibility_tags"].get("socket", "Unknown")
            
            if cpu_socket != mb_socket:
                return False
            
            # Check RAM type compatibility (DDR4 vs DDR5)
            ram_type = ram["compatibility_tags"].get("type", "DDR4")
            
            # AM5 and LGA1700 motherboards support DDR5, older sockets support DDR4
            if mb_socket in ["AM5", "LGA1700"]:
                # These can support both DDR4 and DDR5, but prefer DDR5
                pass
            elif mb_socket in ["AM4", "LGA1200", "LGA1151"]:
                # These primarily support DDR4
                if ram_type == "DDR5":
                    return False
            
            # Check power supply wattage with safety margin
            cpu_tdp = cpu["compatibility_tags"].get("tdp", 65)
            gpu_power = gpu["compatibility_tags"].get("power", 150)
            psu_wattage = psu["compatibility_tags"].get("wattage", 650)
            
            # Add overhead for other components (motherboard, RAM, storage, fans)
            total_power_needed = cpu_tdp + gpu_power + 100  # 100W overhead
            
            # Require 20% headroom for PSU efficiency and aging
            if psu_wattage < total_power_needed * 1.2:
                return False
            
            # Check case form factor compatibility
            mb_form_factor = motherboard["compatibility_tags"].get("form_factor", "ATX")
            case_form_factor = case["compatibility_tags"].get("form_factor", "ATX")
            
            # Form factor compatibility matrix
            compatible_combinations = {
                "ATX": ["ATX", "Full Tower", "Mid Tower"],
                "mATX": ["ATX", "mATX", "Full Tower", "Mid Tower", "Mini Tower"],
                "Mini-ITX": ["ATX", "mATX", "Mini-ITX", "Full Tower", "Mid Tower", "Mini Tower", "Desktop"]
            }
            
            if mb_form_factor not in compatible_combinations:
                mb_form_factor = "ATX"  # Default fallback
            
            if case_form_factor not in compatible_combinations[mb_form_factor]:
                return False
            
            # Check GPU length compatibility
            gpu_length = gpu["compatibility_tags"].get("length", 280)
            case_max_gpu_length = case["compatibility_tags"].get("max_gpu_length", 350)
            
            if gpu_length > case_max_gpu_length:
                return False
            
            # Check RAM capacity compatibility
            ram_capacity_str = ram["compatibility_tags"].get("capacity", "16GB")
            ram_capacity = int(ram_capacity_str.replace("GB", ""))
            mb_max_memory = motherboard["compatibility_tags"].get("max_memory", 128)
            
            if ram_capacity > mb_max_memory:
                return False
            
            return True
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"Compatibility check error: {e}")
            return False
    
    def _check_budget(self, build: Dict, budget: float) -> bool:
        """Check if build is within budget"""
        total_cost = sum(part["price"] for part in build.values())
        return total_cost <= budget
    
    def _create_build_response(self, build: Dict) -> BuildResponse:
        """Create a BuildResponse from a build dictionary"""
        parts = []
        total_price = 0
        total_performance = 0
        budget_allocation = {}
        
        for category, part in build.items():
            part_response = PartResponse(**part)
            parts.append(part_response)
            total_price += part["price"]
            total_performance += part["performance_score"]
            budget_allocation[category] = part["price"]
        
        bang_for_buck_score = total_performance / total_price if total_price > 0 else 0
        
        return BuildResponse(
            parts=parts,
            total_price=round(total_price, 2),
            performance_score=total_performance,
            budget_allocation=budget_allocation,
            compatibility_status="All parts compatible",
            bang_for_buck_score=round(bang_for_buck_score, 4)
        )
    
    def _ensure_build_diversity(self, builds: List) -> List:
        """Ensure builds are diverse by filtering out very similar ones"""
        if not builds:
            return builds
            
        diverse_builds = [builds[0]]  # Always include the top build
        
        for build in builds[1:]:
            is_diverse = True
            for existing_build in diverse_builds:
                # Check if builds are too similar (same CPU and GPU)
                build_cpu = next((p for p in build.parts if p.category == "cpu"), None)
                build_gpu = next((p for p in build.parts if p.category == "gpu"), None)
                existing_cpu = next((p for p in existing_build.parts if p.category == "cpu"), None)
                existing_gpu = next((p for p in existing_build.parts if p.category == "gpu"), None)
                
                if (build_cpu and existing_cpu and build_cpu.id == existing_cpu.id and
                    build_gpu and existing_gpu and build_gpu.id == existing_gpu.id):
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_builds.append(build)
                
            # Stop when we have enough diverse builds
            if len(diverse_builds) >= 5:
                break
                
        return diverse_builds
