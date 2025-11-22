from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from battle_logic import GameState, GamePhase, calculate_battle, independent_battle_calculation

Window.clearcolor = (0.06, 0.09, 0.06, 1)


class SplashScreen(Screen):
    def on_enter(self):
        from kivy.clock import Clock
        Clock.schedule_once(self.go_to_starting_sets, 2)

    def go_to_starting_sets(self, dt):
        self.manager.current = 'starting_sets'


class StartingSetsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.germany_set = 0
        self.ussr_set = 0

    def on_enter(self):
        self.update_display()

    def update_display(self):
        germany_sets = GameState.get_starting_sets('Германия')
        ussr_sets = GameState.get_starting_sets('СССР')

        if germany_sets:
            self.ids.germany_set_label.text = f"Германия: {germany_sets[self.germany_set]['name']}"
        if ussr_sets:
            self.ids.ussr_set_label.text = f"СССР: {ussr_sets[self.ussr_set]['name']}"

        self.show_set_composition('germany_composition', germany_sets[self.germany_set] if germany_sets else {})
        self.show_set_composition('ussr_composition', ussr_sets[self.ussr_set] if ussr_sets else {})

    def show_set_composition(self, layout_id, starting_set):
        layout = self.ids[layout_id]
        layout.clear_widgets()

        if not starting_set:
            return

        for unit_name, count in starting_set.get('units', {}).items():
            label = Label(
                text=f"{unit_name}: {count}",
                size_hint_y=None,
                height='30dp',
                color=(1, 1, 1, 1),
                font_size='14sp'
            )
            layout.add_widget(label)

    def change_germany_set(self, direction):
        germany_sets = GameState.get_starting_sets('Германия')
        if germany_sets:
            self.germany_set = (self.germany_set + direction) % len(germany_sets)
            self.update_display()

    def change_ussr_set(self, direction):
        ussr_sets = GameState.get_starting_sets('СССР')
        if ussr_sets:
            self.ussr_set = (self.ussr_set + direction) % len(ussr_sets)
            self.update_display()

    def confirm_starting_sets(self):
        GameState.set_starting_set('Германия', self.germany_set)
        GameState.set_starting_set('СССР', self.ussr_set)
        self.manager.current = 'menu'


class MainMenu(Screen):
    def restart_game(self):
        GameState.initialize()
        self.manager.current = 'starting_sets'


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_unit = None
        self.selected_province = None

    def on_enter(self):
        self.update_display()

    def update_display(self):
        try:
            self.ids.current_player.text = f""
            self.ids.phase_label.text = f"Фаза: {GameState.current_phase.value}"
            self.ids.resources_label.text = f"Ресурсы: {GameState.get_current_side().bank}"
            self.ids.dice_label.text = f"Кубик: {GameState.current_dice}"

            self.update_buttons()
            self.update_army_status()
        except Exception as e:
            print(f"Error in update_display: {e}")

    def update_buttons(self):
        try:
            phase = GameState.current_phase

            self.ids.roll_dice_button.disabled = (phase != GamePhase.CHOICE)
            has_dice = GameState.current_dice > 0
            self.ids.choose_attack_button.disabled = (phase != GamePhase.CHOICE or not has_dice)
            self.ids.choose_bank_button.disabled = (phase != GamePhase.CHOICE or not has_dice)

            self.ids.move_button.disabled = (phase != GamePhase.MOVEMENT)
            self.ids.attack_button.disabled = (phase != GamePhase.ATTACK)
            self.ids.place_units_button.disabled = (phase != GamePhase.PLACEMENT)
            self.ids.end_turn_button.disabled = (phase != GamePhase.COMPLETION)

        except Exception as e:
            print(f"Error in update_buttons: {e}")

    def update_army_status(self):
        try:
            grid = self.ids.army_grid
            grid.clear_widgets()

            current_side = GameState.get_current_side()
            for unit_name, unit_type in current_side.units.items():
                if unit_name != 'Укреп':
                    available = current_side.available.get(unit_name, 0)
                    max_placement = current_side.max_placements.get(unit_name, 0)

                    grid.add_widget(Label(text=unit_name, color=(1, 1, 1, 1), size_hint_y=None, height='30dp'))
                    grid.add_widget(Label(text=str(available), color=(1, 1, 1, 1), size_hint_y=None, height='30dp'))
                    grid.add_widget(Label(text='∞' if max_placement > 100 else str(max_placement),
                                          color=(1, 1, 1, 1), size_hint_y=None, height='30dp'))

        except Exception as e:
            print(f"Error in update_army_status: {e}")

    def roll_dice(self):
        try:
            if GameState.current_phase == GamePhase.CHOICE:
                GameState.roll_dice()
                self.update_display()
        except Exception as e:
            self.show_message(f"Ошибка: {str(e)}")

    def choose_attack(self):
        try:
            if GameState.current_phase == GamePhase.CHOICE and GameState.current_dice > 0:
                GameState.choose_attack()
                self.update_display()
        except Exception as e:
            self.show_message(f"Ошибка: {str(e)}")

    def choose_bank(self):
        try:
            if GameState.current_phase == GamePhase.CHOICE and GameState.current_dice > 0:
                GameState.choose_bank()
                self.update_display()
        except Exception as e:
            self.show_message(f"Ошибка: {str(e)}")

    def end_turn(self):
        try:
            if GameState.current_phase == GamePhase.COMPLETION:
                GameState.end_turn()
                self.update_display()
        except Exception as e:
            self.show_message(f"Ошибка: {str(e)}")

    def show_move_dialog(self):
        if GameState.current_phase == GamePhase.MOVEMENT:
            self.show_message("Режим перемещения: выберите юнит и провинцию для перемещения")

    def show_attack_dialog(self):
        if GameState.current_phase == GamePhase.ATTACK:
            self.show_attack_units_selection()

    def show_attack_units_selection(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup = Popup(title='Выберите атакующие юниты (макс. 2)', content=content, size_hint=(0.8, 0.7))

        current_side = GameState.get_current_side()
        selected_units = []
        buttons = {}

        def toggle_unit(unit_name, button):
            if unit_name in selected_units:
                selected_units.remove(unit_name)
                button.background_color = (0.2, 0.2, 0.2, 1)
            else:
                if len(selected_units) < 2:
                    selected_units.append(unit_name)
                    button.background_color = (0, 0.5, 0, 1)

        for unit_name in current_side.units.keys():
            if unit_name != 'Укреп' and current_side.available.get(unit_name, 0) > 0:
                btn = Button(text=unit_name, size_hint_y=None, height='60dp')
                btn.background_color = (0.2, 0.2, 0.2, 1)
                buttons[unit_name] = btn
                btn.bind(on_release=lambda instance, u=unit_name: toggle_unit(u, buttons[u]))
                content.add_widget(btn)

        def confirm_attack():
            if len(selected_units) > 0:
                popup.dismiss()
                self.execute_attack(selected_units)
            else:
                self.show_message("Выберите хотя бы одного юнита для атаки")

        content.add_widget(Button(text='Атаковать', size_hint_y=None, height='60dp',
                                  on_release=lambda x: confirm_attack()))
        content.add_widget(Button(text='Отмена', size_hint_y=None, height='60dp',
                                  on_release=popup.dismiss))
        popup.open()

    def execute_attack(self, attacker_units):
        try:
            defender_units = ['Л. Пехота']

            outcome, attack_total, defence_total, killed = calculate_battle(
                attacker=GameState.get_current_side(),
                defender=GameState.get_enemy_side(),
                attacker_unit_names=attacker_units,
                defender_unit_names=defender_units,
                atk_die=GameState.current_dice,
                def_die=0,
                forts=0,
                consume=True
            )

            result = f"Атака: {attack_total}, Защита: {defence_total}\n{outcome}"
            if killed:
                result += f"\nУничтожено: {', '.join(killed)}"

            self.show_message(result)

            GameState._current_phase = GamePhase.COMPLETION
            self.update_display()

        except Exception as e:
            self.show_message(f"Ошибка атаки: {str(e)}")

    def show_placement_dialog(self):
        if GameState.current_phase == GamePhase.PLACEMENT:
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            popup = Popup(title='Размещение новых юнитов', content=content, size_hint=(0.8, 0.7))

            current_side = GameState.get_current_side()
            has_available = False

            for unit_name, unit_type in current_side.units.items():
                if unit_name != 'Укреп':
                    max_place = current_side.max_placements.get(unit_name, 0)
                    cost = unit_type.cost

                    if max_place > 0 and current_side.bank >= cost:
                        has_available = True
                        btn_text = f"{unit_name} (цена: {cost}, можно: {max_place})"
                        btn = Button(text=btn_text, size_hint_y=None, height='60dp')
                        btn.bind(on_release=lambda instance, u=unit_name: self.place_unit(u, popup))
                        content.add_widget(btn)

            if not has_available:
                content.add_widget(Label(text="Нет доступных юнитов для размещения", color=(1, 1, 1, 1)))

            content.add_widget(Button(text='Отмена', size_hint_y=None, height='60dp', on_release=popup.dismiss))
            popup.open()

    def place_unit(self, unit_name, popup):
        current_side = GameState.get_current_side()
        unit_type = current_side.units[unit_name]

        if current_side.bank >= unit_type.cost and current_side.max_placements.get(unit_name, 0) > 0:
            current_side.bank -= unit_type.cost
            current_side.available[unit_name] = current_side.available.get(unit_name, 0) + 1
            current_side.max_placements[unit_name] -= 1

            popup.dismiss()
            self.show_message(f"Размещен {unit_name}")
            self.update_display()

    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup = Popup(title='Информация', content=content, size_hint=(0.7, 0.4))

        content.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        content.add_widget(Button(text='OK', size_hint_y=None, height='50dp', on_release=popup.dismiss))
        popup.open()


class DependentBattleCalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attacker_side = 'СССР'
        self.defender_side = 'Германия'

    def on_enter(self):
        self.update_display()

    def update_display(self):
        # Очищаем и обновляем метки сторон
        self.ids.atk_side_label.text = f"Атакующий: {self.attacker_side}"
        self.ids.def_side_label.text = f"Защитник: {self.defender_side}"

        attacker_side_obj = GameState._sides[self.attacker_side]
        defender_side_obj = GameState._sides[self.defender_side]

        attacker_units = [name for name in attacker_side_obj.units.keys() if
                          name != 'Укреп' and attacker_side_obj.available.get(name, 0) > 0]
        defender_units = [name for name in defender_side_obj.units.keys() if
                          name != 'Укреп' and defender_side_obj.available.get(name, 0) > 0]

        # Обновляем списки юнитов
        self.ids.atk_unit1.values = attacker_units
        self.ids.atk_unit2.values = ['—'] + attacker_units
        self.ids.def_unit1.values = defender_units
        self.ids.def_unit2.values = ['—'] + defender_units

        # Установим значения по умолчанию, если текущие значения не в списке
        if attacker_units and (self.ids.atk_unit1.text not in attacker_units or self.ids.atk_unit1.text == ''):
            self.ids.atk_unit1.text = attacker_units[0]
        if defender_units and (self.ids.def_unit1.text not in defender_units or self.ids.def_unit1.text == ''):
            self.ids.def_unit1.text = defender_units[0]

        # Сбрасываем вторых юнитов если нужно
        if self.ids.atk_unit2.text not in (['—'] + attacker_units):
            self.ids.atk_unit2.text = '—'
        if self.ids.def_unit2.text not in (['—'] + defender_units):
            self.ids.def_unit2.text = '—'

    def switch_sides(self):
        self.attacker_side, self.defender_side = self.defender_side, self.attacker_side
        self.update_display()

    def do_calc(self):
        try:
            atk1 = self.ids.atk_unit1.text
            atk2 = self.ids.atk_unit2.text if self.ids.atk_unit2.text != '—' else None
            def1 = self.ids.def_unit1.text
            def2 = self.ids.def_unit2.text if self.ids.def_unit2.text != '—' else None

            atk_die = int(self.ids.atk_dice.text)
            def_die = int(self.ids.def_dice.text)
            forts = int(self.ids.forts.text)
            terrain_bonus = int(self.ids.terrain_bonus.text)

            attacker_side_obj = GameState._sides[self.attacker_side]
            defender_side_obj = GameState._sides[self.defender_side]

            outcome, attack_total, defence_total, killed = calculate_battle(
                attacker=attacker_side_obj,
                defender=defender_side_obj,
                attacker_unit_names=[n for n in (atk1, atk2) if n and n != '—'],
                defender_unit_names=[n for n in (def1, def2) if n and n != '—'],
                atk_die=atk_die,
                def_die=def_die,
                forts=forts,
                terrain_bonus=terrain_bonus,
                consume=True
            )

            result = f"Атака: {attack_total}, Защита: {defence_total}\n{outcome}"
            if killed:
                result += f"\nУничтожено: {', '.join(killed)}"

            self.ids.result_label.text = result
            self.update_display()

        except Exception as e:
            self.ids.result_label.text = f"Ошибка: {str(e)}"

    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup = Popup(title='Информация', content=content, size_hint=(0.7, 0.4))

        content.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        content.add_widget(Button(text='OK', size_hint_y=None, height='50dp', on_release=popup.dismiss))
        popup.open()


class IndependentBattleCalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attacker_side = 'СССР'
        self.defender_side = 'Германия'

    def on_enter(self):
        self.update_display()

    def update_display(self):
        self.ids.atk_side_label.text = f"Атакующий: {self.attacker_side}"
        self.ids.def_side_label.text = f"Защитник: {self.defender_side}"

        from battle_logic import get_all_unit_types
        all_units = get_all_unit_types()

        attacker_units = [name for name in all_units[self.attacker_side].keys() if name != 'Укреп']
        defender_units = [name for name in all_units[self.defender_side].keys() if name != 'Укреп']

        self.ids.atk_unit1.values = attacker_units
        self.ids.atk_unit2.values = ['—'] + attacker_units
        self.ids.def_unit1.values = defender_units
        self.ids.def_unit2.values = ['—'] + defender_units

    def switch_sides(self):
        self.attacker_side, self.defender_side = self.defender_side, self.attacker_side
        self.update_display()

    def do_calc(self):
        try:
            atk1 = self.ids.atk_unit1.text
            atk2 = self.ids.atk_unit2.text if self.ids.atk_unit2.text != '—' else None
            def1 = self.ids.def_unit1.text
            def2 = self.ids.def_unit2.text if self.ids.def_unit2.text != '—' else None

            atk_die = int(self.ids.atk_dice.text)
            def_die = int(self.ids.def_dice.text)
            forts = int(self.ids.forts.text)
            terrain_bonus = int(self.ids.terrain_bonus.text)

            outcome, attack_total, defence_total, killed = independent_battle_calculation(
                attacker_side=self.attacker_side,
                defender_side=self.defender_side,
                attacker_units=[n for n in (atk1, atk2) if n and n != '—'],
                defender_units=[n for n in (def1, def2) if n and n != '—'],
                atk_die=atk_die,
                def_die=def_die,
                forts=forts,
                terrain_bonus=terrain_bonus
            )

            result = f"Атака: {attack_total}, Защита: {defence_total}\n{outcome}"
            if killed:
                result += f"\nУничтожено: {', '.join(killed)}"

            self.ids.result_label.text = result

        except Exception as e:
            self.ids.result_label.text = f"Ошибка: {str(e)}"


class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_side = 'СССР'  # Начальная сторона по умолчанию

    def on_enter(self):
        self.update_display()

    def switch_side(self):
        """Переключение между сторонами СССР и Германия"""
        self.current_side = 'Германия' if self.current_side == 'СССР' else 'СССР'
        self.update_display()

    def update_display(self):
        """Обновление отображения магазина для текущей стороны"""
        current_side_obj = GameState._sides[self.current_side]
        self.ids.bank_label.text = f"{self.current_side}: Ресурсы: {current_side_obj.bank}"
        self.ids.current_side_label.text = f"Текущая сторона: {self.current_side}"

        # Очищаем и обновляем список доступных юнитов
        shop_grid = self.ids.shop_grid
        shop_grid.clear_widgets()

        # Заголовки
        shop_grid.add_widget(Label(text='Юнит', color=(1, 1, 1, 1), size_hint_y=None, height='40dp', bold=True))
        shop_grid.add_widget(Label(text='Цена', color=(1, 1, 1, 1), size_hint_y=None, height='40dp', bold=True))
        shop_grid.add_widget(Label(text='Доступно', color=(1, 1, 1, 1), size_hint_y=None, height='40dp', bold=True))
        shop_grid.add_widget(Label(text='Купить', color=(1, 1, 1, 1), size_hint_y=None, height='40dp', bold=True))

        # Список юнитов для покупки для текущей стороны
        for unit_name, unit_type in current_side_obj.units.items():
            if unit_name != 'Укреп':
                available = current_side_obj.max_placements.get(unit_name, 0)
                cost = unit_type.cost

                shop_grid.add_widget(Label(text=unit_name, color=(1, 1, 1, 1), size_hint_y=None, height='40dp'))
                shop_grid.add_widget(Label(text=str(cost), color=(1, 1, 1, 1), size_hint_y=None, height='40dp'))
                shop_grid.add_widget(Label(text=str(available), color=(1, 1, 1, 1), size_hint_y=None, height='40dp'))

                buy_btn = Button(
                    text='Купить',
                    size_hint_y=None,
                    height='40dp',
                    disabled=(current_side_obj.bank < cost or available <= 0)
                )
                buy_btn.bind(on_release=lambda instance, u=unit_name: self.buy_unit(u))
                shop_grid.add_widget(buy_btn)

    def add_resources(self):
        """Добавление ресурсов для текущей стороны"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup = Popup(title=f'Добавить ресурсы для {self.current_side}', content=content, size_hint=(0.6, 0.4))

        content.add_widget(Label(text='Выберите количество ресурсов:', color=(1, 1, 1, 1)))

        spinner = Spinner(
            text='10',
            values=[str(i) for i in range(1, 25)],
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(spinner)

        def confirm_add():
            amount = int(spinner.text)
            GameState._sides[self.current_side].bank += amount
            popup.dismiss()
            self.update_display()
            self.show_message(f"Добавлено {amount} ресурсов для {self.current_side}")

        content.add_widget(Button(text='Добавить', size_hint_y=None, height='40dp', on_release=lambda x: confirm_add()))
        content.add_widget(Button(text='Отмена', size_hint_y=None, height='40dp', on_release=popup.dismiss))
        popup.open()

    def buy_unit(self, unit_name):
        """Покупка юнита для текущей стороны"""
        current_side_obj = GameState._sides[self.current_side]
        unit_type = current_side_obj.units[unit_name]

        if current_side_obj.bank >= unit_type.cost and current_side_obj.max_placements.get(unit_name, 0) > 0:
            current_side_obj.bank -= unit_type.cost
            current_side_obj.available[unit_name] = current_side_obj.available.get(unit_name, 0) + 1
            current_side_obj.max_placements[unit_name] -= 1

            self.update_display()
            self.show_message(f"Куплен {unit_name} для {self.current_side}")
        else:
            self.show_message("Недостаточно ресурсов или достигнут лимит")

    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup = Popup(title='Информация', content=content, size_hint=(0.7, 0.4))

        content.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        content.add_widget(Button(text='OK', size_hint_y=None, height='50dp', on_release=popup.dismiss))
        popup.open()


class StatusScreen(Screen):
    def on_enter(self):
        self.update_status()

    def update_status(self):
        grid = self.ids.status_grid
        grid.clear_widgets()

        for line in GameState.get_full_status():
            label = Label(text=line, size_hint_y=None, height='30dp', color=(1, 1, 1, 1))
            grid.add_widget(label)


KV = '''
ScreenManager:
    SplashScreen:
    StartingSetsScreen:
    MainMenu:
    GameScreen:
    DependentBattleCalculatorScreen:
    IndependentBattleCalculatorScreen:
    ShopScreen:
    StatusScreen:

<SplashScreen>:
    name: 'splash'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'ИГРА ДЕСЯТЫЙ СТАЛИНСКИЙ УДАР'
            font_size: '32sp'
            bold: True
            color: 1, 1, 1, 1

<StartingSetsScreen>:
    name: 'starting_sets'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            text: 'ВЫБОР СТАРТОВЫХ НАБОРОВ'
            size_hint_y: None
            height: '50dp'
            color: 1, 1, 1, 1
            font_size: '20sp'
            bold: True

        BoxLayout:
            orientation: 'horizontal'
            spacing: 20

            # Германия
            BoxLayout:
                orientation: 'vertical'
                spacing: 10
                Label:
                    text: 'ГЕРМАНИЯ'
                    size_hint_y: None
                    height: '40dp'
                    color: 1, 1, 1, 1
                    font_size: '18sp'
                    bold: True

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: '40dp'
                    Label:
                        id: germany_set_label
                        text: ''
                        color: 1, 1, 1, 1
                    Button:
                        text: '<'
                        size_hint_x: 0.2
                        on_release: root.change_germany_set(-1)
                    Button:
                        text: '>'
                        size_hint_x: 0.2
                        on_release: root.change_germany_set(1)

                BoxLayout:
                    orientation: 'vertical'
                    id: germany_composition
                    size_hint_y: None
                    height: self.minimum_height

            # СССР
            BoxLayout:
                orientation: 'vertical'
                spacing: 10
                Label:
                    text: 'СССР'
                    size_hint_y: None
                    height: '40dp'
                    color: 1, 1, 1, 1
                    font_size: '18sp'
                    bold: True

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: '40dp'
                    Label:
                        id: ussr_set_label
                        text: ''
                        color: 1, 1, 1, 1
                    Button:
                        text: '<'
                        size_hint_x: 0.2
                        on_release: root.change_ussr_set(-1)
                    Button:
                        text: '>'
                        size_hint_x: 0.2
                        on_release: root.change_ussr_set(1)

                BoxLayout:
                    orientation: 'vertical'
                    id: ussr_composition
                    size_hint_y: None
                    height: self.minimum_height

        Button:
            text: 'Начать игру'
            size_hint_y: None
            height: '60dp'
            on_release: root.confirm_starting_sets()

<MainMenu>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: 'НАСТОЛЬНАЯ ВОЕННАЯ ИГРА'
            size_hint_y: None
            height: '60dp'
            bold: True
            color: 1, 1, 1, 1
            font_size: '24sp'
        Button:
            text: 'Калькулятор боя (Независимый)'
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'indep_calc'
        Button:
            text: 'Калькулятор боя'
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'dep_calc'
        Button:
            text: 'Магазин'
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'shop'
        Button:
            text: 'Статус игры'
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'status'
        Button:
            text: 'Начать заново'
            size_hint_y: None
            height: '60dp'
            on_release: root.restart_game()
        Button:
            text: 'Выход'
            size_hint_y: None
            height: '60dp'
            on_release: app.stop()

<GameScreen>:
    name: 'game'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10

        Label:
            id: current_player
            text: ''
            size_hint_y: None
            height: '40dp'
            color: 1, 1, 1, 1
            font_size: '18sp'
        Label:
            id: phase_label
            text: ''
            size_hint_y: None
            height: '40dp'
            color: 1, 1, 1, 1
            font_size: '18sp'
        Label:
            id: resources_label
            text: 'Ресурсы:'
            size_hint_y: None
            height: '40dp'
            color: 1, 1, 1, 1
            font_size: '18sp'
        Label:
            id: dice_label
            text: ''
            size_hint_y: None
            height: '40dp'
            color: 1, 1, 1, 1
            font_size: '18sp'

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 5
            Button:
                id: roll_dice_button
                text: 'Бросить кубик'
                on_release: root.roll_dice()
            Button:
                id: choose_attack_button
                text: 'Выбрать атаку'
                on_release: root.choose_attack()
            Button:
                id: choose_bank_button
                text: 'Положить в банк'
                on_release: root.choose_bank()

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 5
            Button:
                id: move_button
                text: 'Перемещение'
                on_release: root.show_move_dialog()
            Button:
                id: attack_button
                text: 'Атака'
                on_release: root.show_attack_dialog()
            Button:
                id: place_units_button
                text: 'Размещение'
                on_release: root.show_placement_dialog()

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            Button:
                id: end_turn_button
                text: 'Завершить ход'
                on_release: root.end_turn()

        Label:
            text: 'ВАША АРМИЯ:'
            size_hint_y: None
            height: '40dp'
            color: 1, 1, 1, 1
            font_size: '16sp'
            bold: True

        ScrollView:
            size_hint_y: 1
            GridLayout:
                id: army_grid
                cols: 3
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            Button:
                text: 'Главное меню'
                on_release: app.root.current = 'menu'

<DependentBattleCalculatorScreen>:
    name: 'dep_calc'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10

        Label:
            text: 'КАЛЬКУЛЯТОР БОЯ (ЗАВИСИМЫЙ)'
            size_hint_y: None
            height: '50dp'
            color: 1, 1, 1, 1
            font_size: '20sp'
            bold: True

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '40dp'
            spacing: 10
            Label:
                id: atk_side_label
                text: 'Атакующий: СССР'
                color: 1, 1, 1, 1
                font_size: '16sp'
            Button:
                text: 'поменять'
                size_hint_x: 0.4
                on_release: root.switch_sides()
            Label:
                id: def_side_label
                text: 'Защитник: Германия'
                color: 1, 1, 1, 1
                font_size: '16sp'

        GridLayout:
            cols: 2
            size_hint_y: None
            height: '350dp'
            spacing: 10
            padding: 10

            Label:
                text: 'Атакующие юниты'
                color: 1, 1, 1, 1
            Label:
                text: 'Защищающиеся юниты'
                color: 1, 1, 1, 1

            Spinner:
                id: atk_unit1
                text: 'Л. Пехота'
                values: []
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: def_unit1
                text: 'Л. Пехота'
                values: []
                size_hint_y: None
                height: '40dp'

            Spinner:
                id: atk_unit2
                text: '—'
                values: ['—']
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: def_unit2
                text: '—'
                values: ['—']
                size_hint_y: None
                height: '40dp'

            Label:
                text: 'Кубик атакующего'
                color: 1, 1, 1, 1
            Label:
                text: 'Кубик защитника'
                color: 1, 1, 1, 1

            Spinner:
                id: atk_dice
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: def_dice
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'

            Label:
                text: 'Укрепления'
                color: 1, 1, 1, 1
            Label:
                text: 'Бонус местности'
                color: 1, 1, 1, 1

            Spinner:
                id: forts
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: terrain_bonus
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'

        Label:
            id: result_label
            text: ''
            size_hint_y: None
            height: '100dp'
            color: 0.9, 0.9, 0.8, 1
            text_size: self.width, None

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Button:
                text: 'Рассчитать'
                on_release: root.do_calc()
            Button:
                text: 'Назад'
                on_release: app.root.current = 'menu'

<IndependentBattleCalculatorScreen>:
    name: 'indep_calc'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10

        Label:
            text: 'КАЛЬКУЛЯТОР БОЯ (НЕЗАВИСИМЫЙ)'
            size_hint_y: None
            height: '50dp'
            color: 1, 1, 1, 1
            font_size: '20sp'
            bold: True

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '40dp'
            spacing: 10
            Label:
                id: atk_side_label
                text: 'Атакующий: СССР'
                color: 1, 1, 1, 1
                font_size: '16sp'
            Button:
                text: 'поменять'
                size_hint_x: 0.4
                on_release: root.switch_sides()
            Label:
                id: def_side_label
                text: 'Защитник: Германия'
                color: 1, 1, 1, 1
                font_size: '16sp'

        GridLayout:
            cols: 2
            size_hint_y: None
            height: '350dp'
            spacing: 10
            padding: 10

            Label:
                text: 'Атакующие юниты'
                color: 1, 1, 1, 1
            Label:
                text: 'Защищающиеся юниты'
                color: 1, 1, 1, 1

            Spinner:
                id: atk_unit1
                text: 'Л. Пехота'
                values: []
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: def_unit1
                text: 'Л. Пехота'
                values: []
                size_hint_y: None
                height: '40dp'

            Spinner:
                id: atk_unit2
                text: '—'
                values: ['—']
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: def_unit2
                text: '—'
                values: ['—']
                size_hint_y: None
                height: '40dp'

            Label:
                text: 'Кубик атакующего'
                color: 1, 1, 1, 1
            Label:
                text: 'Кубик защитника'
                color: 1, 1, 1, 1

            Spinner:
                id: atk_dice
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: def_dice
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'

            Label:
                text: 'Укрепления'
                color: 1, 1, 1, 1
            Label:
                text: 'Бонус местности'
                color: 1, 1, 1, 1

            Spinner:
                id: forts
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'
            Spinner:
                id: terrain_bonus
                text: '0'
                values: [str(i) for i in range(0, 25)]
                size_hint_y: None
                height: '40dp'

        Label:
            id: result_label
            text: ''
            size_hint_y: None
            height: '100dp'
            color: 0.9, 0.9, 0.8, 1
            text_size: self.width, None

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Button:
                text: 'Рассчитать'
                on_release: root.do_calc()
            Button:
                text: 'Назад'
                on_release: app.root.current = 'menu'

<ShopScreen>:
    name: 'shop'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10

        Label:
            text: 'МАГАЗИН'
            size_hint_y: None
            height: '50dp'
            color: 1, 1, 1, 1
            font_size: '20sp'
            bold: True

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '40dp'
            spacing: 10
            Label:
                id: current_side_label
                text: 'Текущая сторона: СССР'
                color: 1, 1, 1, 1
                font_size: '16sp'
            Button:
                text: 'поменять'
                size_hint_x: 0.4
                on_release: root.switch_side()

        Label:
            id: bank_label
            text: 'СССР: Ресурсы: 0'
            size_hint_y: None
            height: '40dp'
            color: 1, 1, 1, 1
            font_size: '18sp'

        Button:
            text: 'Добавить ресурсы'
            size_hint_y: None
            height: '60dp'
            on_release: root.add_resources()

        ScrollView:
            GridLayout:
                id: shop_grid
                cols: 4
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            Button:
                text: 'Назад'
                on_release: app.root.current = 'menu'

<StatusScreen>:
    name: 'status'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10
        Label:
            text: 'СТАТУС ИГРЫ'
            size_hint_y: None
            height: '50dp'
            color: 1, 1, 1, 1
            font_size: '20sp'
            bold: True

        ScrollView:
            GridLayout:
                id: status_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Button:
                text: 'Обновить'
                on_release: root.update_status()
            Button:
                text: 'Назад'
                on_release: app.root.current = 'menu'
'''

ROOT = Builder.load_string(KV)

class TabletopApp(App):
    icon = 'icon.jpg'
    def build(self):
        GameState.initialize()
        Window.set_icon('icon.jpg')
        return ROOT

    def on_start(self):
        # Устанавливаем заголовок окна
        from kivy.core.window import Window
        Window.set_title('Десятый Сталинский Удар')



if __name__ == '__main__':
    TabletopApp().run()