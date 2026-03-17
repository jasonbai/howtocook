"""
Menu Planner for HowToCook
Plans balanced menus for multiple people.
"""
import math
from typing import Dict, List, Optional, Set
from recipe_search import RecipeSearcher


class MenuPlanner:
    """Plan balanced menus for multiple people."""

    # Meat priority order (from 如何选择现在吃什么.md)
    MEAT_PRIORITY = ['猪肉', '鸡肉', '牛肉', '羊肉', '鸭肉', '鱼肉']

    # Categories that count as meat dishes
    MEAT_CATEGORIES = ['meat_dish', 'aquatic']

    # Categories that count as vegetable dishes
    VEGETABLE_CATEGORIES = ['vegetable_dish', 'soup']

    # Other categories
    SIDE_CATEGORIES = ['staple', 'breakfast', 'dessert']

    def __init__(self, searcher: RecipeSearcher):
        """
        Initialize the menu planner.

        Args:
            searcher: RecipeSearcher instance
        """
        self.searcher = searcher

    def plan_menu(self, people_count: int,
                  max_difficulty: int = 3,
                  max_time: int = 40,
                  preferences: Dict = None) -> List[Dict]:
        """
        Plan a balanced menu for a given number of people.

        Algorithm from 如何选择现在吃什么.md:
        - Total dishes = people_count + 1
        - Meat dishes = ceil(total_dishes / 2)
        - Vegetable dishes = floor(total_dishes / 2)

        Args:
            people_count: Number of people eating
            max_difficulty: Maximum difficulty level (default: 3, intermediate)
            max_time: Maximum cooking time in minutes (default: 40)
            preferences: Optional preferences dict with keys:
                - 'include_categories': List of categories to include
                - 'exclude_ingredients': List of ingredients to avoid
                - 'has_children': bool, add sweet dishes if true
                - 'prefer_easy': bool, prefer easier dishes if true

        Returns:
            List of recipe info dictionaries forming a balanced menu
        """
        preferences = preferences or {}

        # Calculate dish counts
        total_dishes = people_count + 1
        meat_count = math.ceil(total_dishes / 2)
        vegetable_count = math.floor(total_dishes / 2)

        menu = []
        used_meat_types: Set[str] = set()

        # Select meat dishes
        meat_dishes = self._select_meat_dishes(
            count=meat_count,
            max_difficulty=max_difficulty,
            max_time=max_time,
            used_meat_types=used_meat_types,
            preferences=preferences
        )
        menu.extend(meat_dishes)

        # Select vegetable dishes
        vegetable_dishes = self._select_vegetable_dishes(
            count=vegetable_count,
            max_difficulty=max_difficulty,
            max_time=max_time,
            exclude_names=[d['name'] for d in meat_dishes],
            preferences=preferences
        )
        menu.extend(vegetable_dishes)

        # Add special dishes for large groups
        if people_count >= 8:
            self._add_seafood_dish(menu, max_difficulty, max_time)

        # Add sweet dish if children are present
        if preferences.get('has_children', False):
            self._add_sweet_dish(menu, max_difficulty, max_time)

        return menu

    def _select_meat_dishes(self, count: int, max_difficulty: int,
                            max_time: int, used_meat_types: Set[str],
                            preferences: Dict) -> List[Dict]:
        """Select meat dishes ensuring variety in meat types."""
        dishes = []
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops

        # Get available meat dishes
        all_meat = self.searcher.multi_filter(
            categories=self.MEAT_CATEGORIES,
            max_difficulty=max_difficulty,
            max_time=max_time
        )

        # Sort by meat type priority
        all_meat = self._sort_by_meat_priority(all_meat)

        while len(dishes) < count and attempts < max_attempts:
            attempts += 1

            for recipe in all_meat:
                if len(dishes) >= count:
                    break

                # Skip if already selected
                if any(d['name'] == recipe['name'] for d in dishes):
                    continue

                # Check meat type variety
                meat_type = self.searcher.detect_meat_type(recipe)
                if meat_type and meat_type in used_meat_types:
                    # Skip duplicate meat types unless we've exhausted options
                    if len(used_meat_types) >= len(self.MEAT_PRIORITY):
                        continue  # All meat types used, allow duplicates
                    else:
                        continue  # Skip to ensure variety

                # Check excluded ingredients
                if self._has_excluded_ingredient(recipe, preferences):
                    continue

                dishes.append(recipe)
                if meat_type:
                    used_meat_types.add(meat_type)

        return dishes

    def _select_vegetable_dishes(self, count: int, max_difficulty: int,
                                 max_time: int, exclude_names: List[str],
                                 preferences: Dict) -> List[Dict]:
        """Select vegetable dishes."""
        dishes = []

        # Get available vegetable dishes
        all_veg = self.searcher.multi_filter(
            categories=self.VEGETABLE_CATEGORIES,
            max_difficulty=max_difficulty,
            max_time=max_time
        )

        # Prefer easier dishes if requested
        if preferences.get('prefer_easy', False):
            all_veg.sort(key=lambda x: x['difficulty'])

        for recipe in all_veg:
            if len(dishes) >= count:
                break

            # Skip excluded names
            if recipe['name'] in exclude_names:
                continue

            # Skip if already selected
            if any(d['name'] == recipe['name'] for d in dishes):
                continue

            # Check excluded ingredients
            if self._has_excluded_ingredient(recipe, preferences):
                continue

            dishes.append(recipe)

        return dishes

    def _add_seafood_dish(self, menu: List[Dict], max_difficulty: int, max_time: int):
        """Add a seafood dish for large groups."""
        if any(d['category'] == 'aquatic' for d in menu):
            return  # Already has seafood

        seafood = self.searcher.multi_filter(
            categories=['aquatic'],
            max_difficulty=max_difficulty,
            max_time=max_time
        )

        if seafood:
            menu.append(seafood[0])

    def _add_sweet_dish(self, menu: List[Dict], max_difficulty: int, max_time: int):
        """Add a sweet dish for children."""
        # Look for dessert or naturally sweet dishes
        sweet_keywords = ['糖', '甜', '蜜', '南瓜', '红薯', '玉米', '南瓜']

        desserts = self.searcher.multi_filter(
            categories=['dessert'],
            max_difficulty=max_difficulty,
            max_time=max_time
        )

        if desserts:
            menu.append(desserts[0])
            return

        # Look for naturally sweet dishes in other categories
        all_dishes = self.searcher.multi_filter(
            max_difficulty=max_difficulty,
            max_time=max_time
        )

        for recipe in all_dishes:
            if any(keyword in recipe['name'] for keyword in sweet_keywords):
                if not any(d['name'] == recipe['name'] for d in menu):
                    menu.append(recipe)
                    return

    def _sort_by_meat_priority(self, dishes: List[Dict]) -> List[Dict]:
        """Sort dishes by meat type priority."""
        def get_priority(recipe):
            meat_type = self.searcher.detect_meat_type(recipe)
            if meat_type and meat_type in self.MEAT_PRIORITY:
                return self.MEAT_PRIORITY.index(meat_type)
            return len(self.MEAT_PRIORITY)  # Lowest priority for unknown

        return sorted(dishes, key=get_priority)

    def _has_excluded_ingredient(self, recipe: Dict, preferences: Dict) -> bool:
        """Check if recipe contains excluded ingredients."""
        excluded = preferences.get('exclude_ingredients', [])
        if not excluded:
            return False

        recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
        recipe_name = recipe['name'].lower()

        for excluded_item in excluded:
            excluded_item = excluded_item.lower()
            if excluded_item in recipe_name:
                return True
            for ingredient in recipe_ingredients:
                if excluded_item in ingredient:
                    return True

        return False

    def format_menu(self, menu: List[Dict]) -> str:
        """Format a menu for display."""
        from recipe_parser import RecipeParser

        parser = RecipeParser()
        lines = ["# 🍽️ 推荐菜单", ""]

        # Group by type
        meat_dishes = [d for d in menu if d['category'] in self.MEAT_CATEGORIES]
        veg_dishes = [d for d in menu if d['category'] in self.VEGETABLE_CATEGORIES and d not in meat_dishes]
        other_dishes = [d for d in menu if d not in meat_dishes and d not in veg_dishes]

        if meat_dishes:
            lines.append("## 🥩 荤菜")
            for dish in meat_dishes:
                lines.append(f"- {parser.format_compact(dish)}")
            lines.append("")

        if veg_dishes:
            lines.append("## 🥬 素菜")
            for dish in veg_dishes:
                lines.append(f"- {parser.format_compact(dish)}")
            lines.append("")

        if other_dishes:
            lines.append("## 🍚 其他")
            for dish in other_dishes:
                lines.append(f"- {parser.format_compact(dish)}")
            lines.append("")

        lines.append(f"**总计: {len(menu)} 道菜**")
        lines.append("")
        lines.append("*💡 输入菜名可查看详细做法*")

        return '\n'.join(lines)


if __name__ == '__main__':
    # Test the menu planner
    searcher = RecipeSearcher()
    planner = MenuPlanner(searcher)

    # Plan for 4 people
    menu = planner.plan_menu(people_count=4, max_difficulty=2)
    print(planner.format_menu(menu))
