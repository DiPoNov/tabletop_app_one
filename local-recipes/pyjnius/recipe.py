# local-recipes/pyjnius/recipe.py
from pythonforandroid.recipes.pyjnius import PyjniusRecipe as BaseRecipe

class PyjniusFixedRecipe(BaseRecipe):
    # не обязательно менять version, он берётся из buildozer/requirements
    def prebuild_arch(self, arch):
        # применяем патчи перед сборкой
        self.apply_patch("patches/fix_long.patch")
        self.apply_patch("patches/fix_jsize_div.patch")
        super().prebuild_arch(arch)

recipe = PyjniusFixedRecipe()
