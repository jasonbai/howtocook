"""
Recipe Searcher for HowToCook
Indexes and searches recipes from the cookbook.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from recipe_parser import RecipeParser


class RecipeSearcher:
    """Search and filter recipes from the cookbook."""

    # Meat types for menu planning variety
    MEAT_TYPES = {
        '猪肉': ['猪肉', '五花肉', '排骨', '肉丝', '肉片', '肉末', '梅花肉', '里脊'],
        '鸡肉': ['鸡', '鸡翅', '鸡腿', '鸡胸', '整鸡'],
        '牛肉': ['牛肉', '牛腩', '牛排', '牛腱'],
        '羊肉': ['羊肉', '羊排'],
        '鸭肉': ['鸭', '鸭腿', '鸭翅'],
        '鱼肉': ['鱼', '鲫鱼', '草鱼', '鲈鱼', '带鱼', '黄鱼', '鲅鱼']
    }

    # Difficulty level descriptions
    DIFFICULTY_NAMES = {
        0: "极简单",
        1: "新手友好",
        2: "简单",
        3: "中等",
        4: "进阶",
        5: "困难",
        6: "较难",
        7: "很难",
        8: "大师级"
    }

    def __init__(self, cookbook_path: str = None):
        """
        Initialize the recipe searcher.

        Args:
            cookbook_path: Path to the HowToCook cookbook directory.
                          If None, tries to find it automatically.
        """
        if cookbook_path is None:
            cookbook_path = self._find_cookbook_path()

        self.cookbook_path = Path(cookbook_path)
        self.parser = RecipeParser()
        self._index: Optional[Dict] = None
        self._recipes_by_path: Dict[str, Dict] = {}

    def _find_cookbook_path(self) -> str:
        """Try to find the cookbook path automatically."""
        # Try skill-internal data directory first (independent deployment)
        # Note: Return the parent of 'dishes' directory
        skill_data_dir = Path(__file__).parent.parent / 'data'
        if (skill_data_dir / 'dishes').exists():
            return str(skill_data_dir)

        # Fallback to external reference during development
        candidates = [
            '/Users/jason/Documents/Github/howtoCook/HowToCook-master',
            './HowToCook-master',
            '../HowToCook-master',
        ]

        for path in candidates:
            if Path(path).exists() and (Path(path) / 'dishes').exists():
                return path

        # Default to skill-internal directory
        return str(skill_data_dir)

    def build_index(self, force_rebuild: bool = False) -> Dict:
        """
        Build the recipe index.

        Args:
            force_rebuild: If True, rebuild even if cached index exists

        Returns:
            The index dictionary
        """
        if self._index is not None and not force_rebuild:
            return self._index

        # Check for cached index
        index_file = Path(__file__).parent.parent / 'references' / 'recipe_index.json'

        if not force_rebuild and index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    self._index = json.load(f)
                return self._index
            except Exception:
                pass  # Fall through to rebuild

        # Build new index
        self._index = {
            'by_name': {},      # name -> recipe info
            'by_category': {},  # category -> list of recipe names
            'by_difficulty': {},  # difficulty -> list of recipe names
            'by_ingredient': {},  # ingredient -> list of recipe names
            'all_recipes': []    # list of all recipe info
        }

        dishes_dir = self.cookbook_path / 'dishes'

        # Skip template directory
        for category_dir in dishes_dir.iterdir():
            if category_dir.name == 'template' or not category_dir.is_dir():
                continue

            category = category_dir.name
            self._index['by_category'][category] = []

            # Find all .md files in this category
            for md_file in category_dir.rglob('*.md'):
                try:
                    recipe_info = self._parse_recipe_metadata(md_file)
                    if recipe_info:
                        self._add_to_index(recipe_info)
                        self._index['by_category'][category].append(recipe_info['name'])
                except Exception as e:
                    # Skip files that can't be parsed
                    continue

        # Save index for future use
        try:
            index_file.parent.mkdir(parents=True, exist_ok=True)
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self._index, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Continue without saving

        return self._index

    def _parse_recipe_metadata(self, file_path: Path) -> Optional[Dict]:
        """Parse basic metadata from a recipe file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract name
            name_match = re.search(r'^#\s+(.+?)的做法', content, re.MULTILINE)
            if not name_match:
                name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if not name_match:
                return None

            name = name_match.group(1).replace('的做法', '').strip()

            # Extract difficulty
            difficulty = 0
            diff_match = re.search(r'预估烹饪难度：([★]+)', content)
            if diff_match:
                difficulty = len(diff_match.group(1))

            # Extract category from path
            category = "unknown"
            parts = file_path.parts
            if 'dishes' in parts:
                idx = parts.index('dishes')
                if idx + 1 < len(parts):
                    category = parts[idx + 1]

            # Extract ingredients
            ingredients = []
            ing_match = re.search(r'## 必备原料和工具\n(.*?)(?=##|\Z)', content, re.DOTALL)
            if ing_match:
                section = ing_match.group(1)
                for line in section.split('\n'):
                    line = line.strip()
                    if line.startswith('- ') or line.startswith('* '):
                        ingredient = line[2:].strip()
                        # Clean up ingredient name
                        ingredient = re.sub(r'\s*\(.*?\)', '', ingredient).strip()
                        ingredient = re.sub(r'\s*（.*?）', '', ingredient).strip()
                        if ingredient and '可选' not in ingredient:
                            ingredients.append(ingredient)

            return {
                'name': name,
                'difficulty': difficulty,
                'category': category,
                'ingredients': ingredients[:5],  # Store main ingredients
                'path': str(file_path)
            }
        except Exception:
            return None

    def _add_to_index(self, recipe_info: Dict):
        """Add a recipe to all relevant indexes."""
        name = recipe_info['name']

        # By name
        self._index['by_name'][name] = recipe_info

        # By difficulty
        diff = recipe_info['difficulty']
        if diff not in self._index['by_difficulty']:
            self._index['by_difficulty'][diff] = []
        self._index['by_difficulty'][diff].append(name)

        # By ingredient
        for ingredient in recipe_info['ingredients']:
            if ingredient not in self._index['by_ingredient']:
                self._index['by_ingredient'][ingredient] = []
            self._index['by_ingredient'][ingredient].append(name)

        # All recipes
        self._index['all_recipes'].append(recipe_info)

    def search_by_name(self, query: str) -> List[Dict]:
        """
        Search for recipes by name.

        Args:
            query: Search query (supports partial matching)

        Returns:
            List of matching recipe info dictionaries
        """
        self.build_index()
        query = query.lower().strip()

        results = []
        for name, info in self._index['by_name'].items():
            if query in name.lower():
                results.append(info)

        return results

    def filter_by_difficulty(self, max_difficulty: int) -> List[Dict]:
        """
        Get recipes with difficulty <= max_difficulty.

        Args:
            max_difficulty: Maximum difficulty level (0-8)

        Returns:
            List of recipe info dictionaries
        """
        self.build_index()

        results = []
        for diff in range(max_difficulty + 1):
            if diff in self._index['by_difficulty']:
                for name in self._index['by_difficulty'][diff]:
                    if name in self._index['by_name']:
                        results.append(self._index['by_name'][name])

        return results

    def filter_by_category(self, category: str) -> List[Dict]:
        """
        Get recipes in a specific category.

        Args:
            category: Category name (e.g., 'meat_dish', 'vegetable_dish')

        Returns:
            List of recipe info dictionaries
        """
        self.build_index()

        if category not in self._index['by_category']:
            return []

        results = []
        for name in self._index['by_category'][category]:
            if name in self._index['by_name']:
                results.append(self._index['by_name'][name])

        return results

    def filter_by_time(self, max_minutes: int) -> List[Dict]:
        """
        Get recipes that can be made within max_minutes.

        Args:
            max_minutes: Maximum cooking time in minutes

        Returns:
            List of recipe info dictionaries
        """
        self.build_index()
        parser = RecipeParser()

        results = []
        for info in self._index['all_recipes']:
            # Estimate time from difficulty
            time_estimate = parser.TIME_ESTIMATES.get(info['difficulty'], 30)
            if time_estimate <= max_minutes:
                results.append(info)

        return results

    def filter_by_ingredient(self, ingredient: str) -> List[Dict]:
        """
        Get recipes containing a specific ingredient.

        Args:
            ingredient: Ingredient name to search for

        Returns:
            List of recipe info dictionaries
        """
        self.build_index()
        ingredient = ingredient.strip()

        results = []
        for ing, names in self._index['by_ingredient'].items():
            if ingredient in ing:
                for name in names:
                    if name in self._index['by_name']:
                        info = self._index['by_name'][name]
                        if info not in results:
                            results.append(info)

        return results

    def multi_filter(self, categories: List[str] = None,
                     max_difficulty: int = None,
                     max_time: int = None,
                     exclude_difficult: bool = False) -> List[Dict]:
        """
        Filter recipes by multiple criteria.

        Args:
            categories: List of categories to include (None = all)
            max_difficulty: Maximum difficulty level (None = no limit)
            max_time: Maximum cooking time in minutes (None = no limit)
            exclude_difficult: If True, exclude very difficult recipes (6+ stars)

        Returns:
            List of recipe info dictionaries matching all criteria
        """
        self.build_index()

        results = set()

        # Start with all recipes, then filter
        for info in self._index['all_recipes']:
            # Category filter
            if categories and info['category'] not in categories:
                continue

            # Difficulty filter
            if max_difficulty is not None and info['difficulty'] > max_difficulty:
                continue

            if exclude_difficult and info['difficulty'] >= 6:
                continue

            # Time filter
            if max_time is not None:
                time_estimate = RecipeParser.TIME_ESTIMATES.get(info['difficulty'], 30)
                if time_estimate > max_time:
                    continue

            results.add(info['name'])

        # Convert to recipe info list
        return [self._index['by_name'][name] for name in results
                if name in self._index['by_name']]

    def get_recipe(self, recipe_name: str = None, recipe_path: str = None) -> Optional[Dict]:
        """
        Get full parsed recipe data.

        Args:
            recipe_name: Name of the recipe (preferred way to lookup)
            recipe_path: Path to the recipe file (optional, for direct file access)

        Returns:
            Full parsed recipe dictionary or None if not found

        Examples:
            searcher.get_recipe('西红柿炒鸡蛋')  # Search by name
            searcher.get_recipe(recipe_path='/path/to/recipe.md')  # Direct path
        """
        if recipe_name and not recipe_path:
            self.build_index()
            if recipe_name in self._index['by_name']:
                recipe_path = self._index['by_name'][recipe_name]['path']
            else:
                # Fallback to fuzzy search if exact match fails
                search_results = self.search_by_name(recipe_name)
                if search_results:
                    recipe_path = search_results[0]['path']
                else:
                    return None

        if not recipe_path:
            return None

        # Check cache
        if recipe_path in self._recipes_by_path:
            return self._recipes_by_path[recipe_path]

        # Parse recipe
        try:
            recipe = self.parser.parse(recipe_path)
            self._recipes_by_path[recipe_path] = recipe
            return recipe
        except Exception:
            return None

    def detect_meat_type(self, recipe_info: Dict) -> Optional[str]:
        """
        Detect the type of meat in a recipe.

        Args:
            recipe_info: Recipe info dictionary

        Returns:
            Meat type ('猪肉', '鸡肉', etc.) or None
        """
        name = recipe_info['name'].lower()
        ingredients = [ing.lower() for ing in recipe_info.get('ingredients', [])]

        search_text = name + ' ' + ' '.join(ingredients)

        for meat_type, keywords in self.MEAT_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    return meat_type

        return None

    def get_stats(self) -> Dict:
        """Get statistics about the cookbook."""
        self.build_index()

        stats = {
            'total_recipes': len(self._index['all_recipes']),
            'by_category': {},
            'by_difficulty': {}
        }

        for category, recipes in self._index['by_category'].items():
            stats['by_category'][category] = len(recipes)

        for diff, recipes in self._index['by_difficulty'].items():
            stats['by_difficulty'][diff] = len(recipes)

        return stats


if __name__ == '__main__':
    # Test the searcher
    searcher = RecipeSearcher()
    searcher.build_index()

    print("Cookbook Statistics:")
    stats = searcher.get_stats()
    print(f"  Total recipes: {stats['total_recipes']}")
    print(f"  By category: {stats['by_category']}")
    print(f"  By difficulty: {stats['by_difficulty']}")
