"""
Recipe Parser for HowToCook
Parses markdown recipe files into structured data.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional


class RecipeParser:
    """Parse markdown recipe files into structured dictionaries."""

    # Difficulty time estimates (in minutes)
    TIME_ESTIMATES = {
        0: 5,
        1: 10,
        2: 20,
        3: 35,
        4: 50,
        5: 60,
        6: 75,
        7: 90,
        8: 120
    }

    # Category display names (Chinese)
    CATEGORY_NAMES = {
        "meat_dish": "荤菜",
        "vegetable_dish": "素菜",
        "soup": "汤品",
        "staple": "主食",
        "aquatic": "水产",
        "breakfast": "早餐",
        "dessert": "甜品",
        "drink": "饮品",
        "condiment": "酱料",
        "semi-finished": "半成品"
    }

    def parse(self, file_path: str) -> Dict:
        """
        Parse a recipe markdown file into structured data.

        Args:
            file_path: Path to the recipe markdown file

        Returns:
            Dictionary containing parsed recipe data
        """
        path = Path(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        recipe = {
            'name': self._extract_name(content),
            'description': self._extract_description(content),
            'difficulty': self._extract_difficulty(content),
            'category': self._extract_category(path),
            'time_estimate': 0,  # Will be set based on difficulty
            'ingredients': [],
            'steps': [],
            'tips': [],
            'path': str(path)
        }

        # Set time estimate based on difficulty
        recipe['time_estimate'] = self.TIME_ESTIMATES.get(recipe['difficulty'], 30)

        # Parse sections
        recipe['ingredients'] = self._extract_ingredients(content)
        recipe['steps'] = self._extract_steps(content)
        recipe['tips'] = self._extract_tips(content)

        return recipe

    def _extract_name(self, content: str) -> str:
        """Extract recipe name from the first heading."""
        match = re.search(r'^#\s+(.+?)的做法', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback: get first # heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            # Remove "的做法" suffix if present
            return name.replace('的做法', '').strip()

        return "未知菜谱"

    def _extract_description(self, content: str) -> str:
        """Extract the description paragraph after the title."""
        # Find content between first heading and first ## heading
        match = re.search(r'^#.*?\n\n(.+?)\n\n##', content, re.DOTALL)
        if match:
            desc = match.group(1).strip()
            # Remove difficulty line if present
            desc = re.sub(r'预估烹饪难度：[★]+', '', desc).strip()
            return desc
        return ""

    def _extract_difficulty(self, content: str) -> int:
        """Extract difficulty level from star rating."""
        match = re.search(r'预估烹饪难度：([★]+)', content)
        if match:
            stars = match.group(1)
            return len(stars)
        return 0  # Default difficulty

    def _extract_category(self, path: Path) -> str:
        """Extract category from file path."""
        parts = path.parts
        if 'dishes' in parts:
            idx = parts.index('dishes')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "unknown"

    def _extract_ingredients(self, content: str) -> List[str]:
        """Extract ingredients from the recipe."""
        ingredients = []

        # Find the ingredients section
        match = re.search(r'## 必备原料和工具\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if match:
            section = match.group(1)
            # Extract list items
            for line in section.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    ingredient = line[2:].strip()
                    # Remove quantities in parentheses
                    ingredient = re.sub(r'\s*\(.*?\)', '', ingredient).strip()
                    ingredient = re.sub(r'\s*（.*?）', '', ingredient).strip()
                    if ingredient and not any(skip in ingredient for skip in ['可选', '计算', '每次']):
                        ingredients.append(ingredient)

        return ingredients

    def _extract_steps(self, content: str) -> List[str]:
        """Extract cooking steps from the recipe."""
        steps = []

        # Find the 操作 section
        match = re.search(r'## 操作\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if match:
            section = match.group(1)
            for line in section.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    step = line[2:].strip()
                    # Clean up step text
                    step = re.sub(r'\*\*(.+?)\*\*', r'\1', step)  # Remove bold markdown
                    if step:
                        steps.append(step)

        return steps

    def _extract_tips(self, content: str) -> List[str]:
        """Extract tips from the 附加内容 section."""
        tips = []

        # Find the 附加内容 section
        match = re.search(r'## 附加内容\n(.*?)(?=##|$)', content, re.DOTALL)
        if match:
            section = match.group(1)
            for line in section.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    tip = line[2:].strip()
                    if tip:
                        tips.append(tip)
                # Also include numbered points
                elif line.startswith(tuple('0123456789')) and ('.' in line or ')' in line):
                    tip = re.sub(r'^\d+[\.)]\s*', '', line).strip()
                    if tip:
                        tips.append(tip)

        return tips

    def format_compact(self, recipe: Dict) -> str:
        """Format recipe as compact one-line summary."""
        difficulty_stars = '★' * recipe.get('difficulty', 0)
        # Calculate time from difficulty if not provided
        if 'time_estimate' in recipe:
            time = recipe['time_estimate']
        else:
            time = self.TIME_ESTIMATES.get(recipe.get('difficulty', 0), 30)
        category = self.CATEGORY_NAMES.get(recipe.get('category', ''), recipe.get('category', ''))
        return f"📍 {recipe.get('name', '未知')} | {category} | 难度:{difficulty_stars} | 约{time}分钟"

    def format_detailed(self, recipe: Dict) -> str:
        """Format recipe as detailed display."""
        difficulty_stars = '★' * recipe['difficulty']
        category = self.CATEGORY_NAMES.get(recipe['category'], recipe['category'])

        lines = [
            f"# {recipe['name']}",
            "",
            f"**难度等级:** {difficulty_stars}",
            f"**分类:** {category}",
            f"**预估时间:** 约 {recipe['time_estimate']} 分钟",
            ""
        ]

        if recipe['description']:
            lines.extend([
                f"**简介:**",
                recipe['description'],
                ""
            ])

        lines.extend([
            "**食材:**",
        ])
        for ing in recipe['ingredients'][:10]:  # Limit to first 10
            lines.append(f"  - {ing}")

        lines.extend([
            "",
            "**制作步骤:**",
        ])
        for i, step in enumerate(recipe['steps'], 1):
            lines.append(f"  {i}. {step}")

        if recipe['tips']:
            lines.extend([
                "",
                "**小贴士:**",
            ])
            for tip in recipe['tips']:
                lines.append(f"  - {tip}")

        return '\n'.join(lines)
