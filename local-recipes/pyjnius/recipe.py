# local-recipes/pyjnius/recipe.py
from pythonforandroid.recipes.pyjnius import PyjniusRecipe as BaseRecipe

class PyjniusFixedRecipe(BaseRecipe):
    def prebuild_arch(self, arch):
        print(">>> pyjnius: applying local patches (fix_long, fix_jsize_div)")
        # патчи берутся относительно папки рецепта
        self.apply_patch("patches/fix_long.patch")
        self.apply_patch("patches/fix_jsize_div.patch")
        super().prebuild_arch(arch)

recipe = PyjniusFixedRecipe()
