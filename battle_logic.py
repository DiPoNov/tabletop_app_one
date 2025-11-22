from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import random
from enum import Enum


class GamePhase(Enum):
    CHOICE = "Выбор"
    MOVEMENT = "Передвижение"
    PLACEMENT = "Размещение"
    ATTACK = "Атака"
    COMPLETION = "Завершение"


@dataclass
class UnitType:
    name: str
    attack: int
    defence: int
    cost: int
    movement_range: int
    attack_range: int


@dataclass
class Province:
    name: str
    terrain: str
    owner: Optional[str] = None
    units: Dict[str, int] = field(default_factory=dict)
    forts: int = 0


@dataclass
class Side:
    name: str
    units: Dict[str, UnitType] = field(default_factory=dict)
    available: Dict[str, int] = field(default_factory=dict)
    bank: int = 0
    max_placements: Dict[str, int] = field(default_factory=dict)
    provinces: List[str] = field(default_factory=list)

    def add_units(self, unit_name: str, count: int):
        self.available[unit_name] = self.available.get(unit_name, 0) + count


class GameState:
    _sides = {}
    _current_player = 'СССР'
    _current_phase = GamePhase.CHOICE
    _current_dice = 0
    _provinces = {}
    _game_map = {}
    _selected_starting_sets = {'Германия': 0, 'СССР': 0}

    @classmethod
    def initialize(cls):
        # Германия
        germany_units = [
            ('Л. Пехота', 8, 10, 12, 1, 1),
            ('Т. Пехота', 10, 14, 16, 1, 1),
            ('Л. Танк', 12, 14, 18, 2, 1),
            ('Т. Танк', 18, 20, 22, 2, 1),
            ('Арта', 10, 4, 18, 1, 2),
            ('Укреп', 0, 2, 6, 0, 0),
        ]

        # СССР
        ussr_units = [
            ('Л. Пехота', 9, 10, 10, 1, 1),
            ('Т. Пехота', 11, 14, 14, 1, 1),
            ('Л. Танк', 13, 14, 18, 2, 1),
            ('Т. Танк', 19, 20, 22, 2, 1),
            ('Арта', 11, 4, 18, 1, 2),
            ('Укреп', 0, 2, 6, 0, 0),
        ]

        germany = Side('Германия')
        ussr = Side('СССР')

        for n, a, d, c, m, ar in germany_units:
            germany.units[n] = UnitType(n, a, d, c, m, ar)
            germany.available[n] = 0

        for n, a, d, c, m, ar in ussr_units:
            ussr.units[n] = UnitType(n, a, d, c, m, ar)
            ussr.available[n] = 0

        max_placements_data = {
            'Л. Пехота': 999,
            'Т. Пехота': 999,
            'Л. Танк': 2,
            'Т. Танк': 2,
            'Арта': 3,
            'Укреп': 999,
        }

        germany.max_placements = max_placements_data.copy()
        ussr.max_placements = max_placements_data.copy()

        cls._sides['Германия'] = germany
        cls._sides['СССР'] = ussr

        # Стартовые наборы
        cls._germany_starting_sets = [
            {'name': 'Всех под ружьё', 'units': {'Л. Пехота': 5, 'Т. Пехота': 2, 'Арта': 1, 'Укреп': 3}},
            {'name': 'Стандарт', 'units': {'Л. Пехота': 4, 'Т. Пехота': 1, 'Л. Танк': 1, 'Арта': 1, 'Укреп': 3}},
            {'name': 'Кошки', 'units': {'Л. Пехота': 3, 'Л. Танк': 2, 'Т. Танк': 1}},
            {'name': 'Ба-бах', 'units': {'Л. Пехота': 5, 'Арта': 2, 'Укреп': 2}},
        ]

        cls._ussr_starting_sets = [
            {'name': 'РОДИНА-МАТЬ ЗОВЕТ!', 'units': {'Л. Пехота': 5, 'Т. Пехота': 3, 'Арта': 1, 'Укреп': 3}},
            {'name': 'Стандарт', 'units': {'Л. Пехота': 4, 'Т. Пехота': 1, 'Т. Танк': 1, 'Арта': 1, 'Укреп': 3}},
            {'name': 'Танкоград', 'units': {'Л. Пехота': 4, 'Л. Танк': 1, 'Т. Танк': 2, 'Укреп': 1}},
            {'name': 'Столкнем гада!', 'units': {'Л. Пехота': 4, 'Т. Пехота': 1, 'Арта': 2, 'Укреп': 3}},
        ]

        cls._initialize_map()
        cls._current_player = 'СССР'
        cls._current_phase = GamePhase.CHOICE
        cls._current_dice = 0

    @classmethod
    def set_starting_set(cls, side: str, set_index: int):
        cls._selected_starting_sets[side] = set_index

        if side == 'Германия':
            sets = cls._germany_starting_sets
        else:
            sets = cls._ussr_starting_sets

        if 0 <= set_index < len(sets):
            selected_set = sets[set_index]
            side_obj = cls._sides[side]

            for unit_name in side_obj.available.keys():
                side_obj.available[unit_name] = 0

            for unit_name, count in selected_set['units'].items():
                side_obj.available[unit_name] = count

    @classmethod
    def get_starting_sets(cls, side: str):
        if side == 'Германия':
            return cls._germany_starting_sets
        else:
            return cls._ussr_starting_sets

    @classmethod
    def _initialize_map(cls):
        provinces = [
            Province('Москва', 'город', 'СССР'),
            Province('Смоленск', 'равнина', 'СССР'),
            Province('Киев', 'город', 'СССР'),
            Province('Берлин', 'город', 'Германия'),
            Province('Варшава', 'город', 'Германия'),
            Province('Прага', 'равнина', 'Германия'),
        ]

        for province in provinces:
            cls._provinces[province.name] = province

        cls._game_map = {
            'Москва': ['Смоленск'],
            'Смоленск': ['Москва', 'Киев', 'Варшава'],
            'Киев': ['Смоленск', 'Варшава'],
            'Варшава': ['Смоленск', 'Киев', 'Берлин', 'Прага'],
            'Берлин': ['Варшава', 'Прага'],
            'Прага': ['Варшава', 'Берлин'],
        }

    @classmethod
    def get_current_side(cls):
        return cls._sides[cls._current_player]

    @classmethod
    def get_enemy_side(cls):
        return cls._sides['Германия' if cls._current_player == 'СССР' else 'СССР']

    @classmethod
    def roll_dice(cls):
        if cls._current_phase == GamePhase.CHOICE:
            cls._current_dice = random.randint(1, 6)
            return cls._current_dice
        return 0

    @classmethod
    def choose_attack(cls):
        if cls._current_phase == GamePhase.CHOICE and cls._current_dice > 0:
            cls._current_phase = GamePhase.MOVEMENT
            return True
        return False

    @classmethod
    def choose_bank(cls):
        if cls._current_phase == GamePhase.CHOICE and cls._current_dice > 0:
            cls.get_current_side().bank += cls._current_dice
            cls._current_dice = 0
            cls._current_phase = GamePhase.MOVEMENT
            return True
        return False

    @classmethod
    def move_unit(cls, unit_name: str, to_province: str):
        if cls._current_phase == GamePhase.MOVEMENT:
            cls._current_phase = GamePhase.PLACEMENT
            return True
        return False

    @classmethod
    def end_turn(cls):
        if cls._current_phase == GamePhase.COMPLETION:
            cls._current_player = 'Германия' if cls._current_player == 'СССР' else 'СССР'
            cls._current_phase = GamePhase.CHOICE
            cls._current_dice = 0
            return True
        return False

    @classmethod
    def get_full_status(cls):
        lines = []
        for name, side in cls._sides.items():
            lines.append(f"=== {name} ===")
            lines.append(f"Ресурсы: {side.bank}")
            for unit_name, count in side.available.items():
                if count > 0:
                    max_place = side.max_placements.get(unit_name, 0)
                    lines.append(f"  {unit_name}: {count} (можно разместить: {max_place})")

        lines.append('')
        lines.append('')
        lines.append('')

        return lines

    @property
    def current_player(self):
        return self._current_player

    @property
    def current_phase(self):
        return self._current_phase

    @property
    def current_dice(self):
        return self._current_dice


# НЕЗАВИСИМЫЕ ФУНКЦИИ ДЛЯ КАЛЬКУЛЯТОРА БОЯ
def get_all_unit_types():
    """Возвращает все типы юнитов для независимого калькулятора"""
    return {
        'Германия': {
            'Л. Пехота': UnitType('Л. Пехота', 8, 10, 12, 1, 1),
            'Т. Пехота': UnitType('Т. Пехота', 10, 14, 16, 1, 1),
            'Л. Танк': UnitType('Л. Танк', 12, 14, 18, 2, 1),
            'Т. Танк': UnitType('Т. Танк', 18, 20, 22, 2, 1),
            'Арта': UnitType('Арта', 10, 4, 18, 1, 2),
            'Укреп': UnitType('Укреп', 0, 2, 6, 0, 0),
        },
        'СССР': {
            'Л. Пехота': UnitType('Л. Пехота', 9, 10, 10, 1, 1),
            'Т. Пехота': UnitType('Т. Пехота', 11, 14, 14, 1, 1),
            'Л. Танк': UnitType('Л. Танк', 13, 14, 18, 2, 1),
            'Т. Танк': UnitType('Т. Танк', 19, 20, 22, 2, 1),
            'Арта': UnitType('Арта', 11, 4, 18, 1, 2),
            'Укреп': UnitType('Укреп', 0, 2, 6, 0, 0),
        }
    }


def independent_battle_calculation(attacker_side: str, defender_side: str,
                                   attacker_units: List[str], defender_units: List[str],
                                   atk_die: int = 0, def_die: int = 0,
                                   forts: int = 0, terrain_bonus: int = 0) -> Tuple[str, int, int, List[str]]:
    """
    Независимый расчет боя, не зависящий от состояния игры
    """
    if not attacker_units:
        raise ValueError('Нужно выбрать хотя бы один атакующий батальон')

    if len(attacker_units) > 2:
        raise ValueError('Максимум 2 атакующих батальона')

    # Получаем характеристики юнитов
    all_units = get_all_unit_types()

    if attacker_side not in all_units or defender_side not in all_units:
        raise ValueError('Неверно указана сторона')

    attacker_units_data = all_units[attacker_side]
    defender_units_data = all_units[defender_side]

    # Проверяем, что все указанные юниты существуют
    for unit in attacker_units:
        if unit not in attacker_units_data:
            raise ValueError(f'Неизвестный атакующий юнит: {unit}')

    for unit in defender_units:
        if unit not in defender_units_data:
            raise ValueError(f'Неизвестный защищающийся юнит: {unit}')

    # Расчет сил (без проверки доступности)
    attack_total = sum(attacker_units_data[n].attack for n in attacker_units) + atk_die
    defence_total = (sum(defender_units_data[n].defence for n in defender_units) +
                     def_die +
                     forts * defender_units_data['Укреп'].defence +
                     terrain_bonus)

    killed = []
    outcome = ""

    if attack_total > 1.5 * defence_total:
        outcome = 'Атака подавляющая — оборона уничтожена.'
        # В независимом расчете просто указываем, что было бы уничтожено
        killed = defender_units.copy()
        if forts > 0:
            killed.append(f'Укреп x{forts}')
    elif attack_total > defence_total:
        outcome = 'Атака успешна — оборона отступает.'
    else:
        outcome = 'Атака отбита.'

    return outcome, attack_total, defence_total, killed


# Функции для основной игры
def can_move(unit_name: str, to_province: str) -> bool:
    return True


def can_attack(attacker_province: str, defender_province: str, unit_name: str) -> bool:
    return True


def calculate_battle(attacker: Side, defender: Side,
                     attacker_unit_names: List[str], defender_unit_names: List[str],
                     atk_die: int = 0, def_die: int = 0, forts: int = 0,
                     terrain_bonus: int = 0, consume: bool = True) -> Tuple[str, int, int, List[str]]:
    if not attacker_unit_names:
        raise ValueError('Нужно выбрать хотя бы один атакующий батальон')

    if len(attacker_unit_names) > 2:
        raise ValueError('Максимум 2 атакующих батальона')

    # Проверяем доступность юнитов только если consume=True
    if consume:
        for un in attacker_unit_names:
            if attacker.available.get(un, 0) < 1:
                raise ValueError(f'У атакующего нет {un}')

        for un in defender_unit_names:
            if defender.available.get(un, 0) < 1:
                raise ValueError(f'У обороняющегося нет {un}')

    forts = max(0, int(forts))
    if consume and forts > defender.available.get('Укреп', 0):
        raise ValueError('У обороняющегося нет такого количества укреплений')

    # Расчет сил
    attack_total = sum(attacker.units[n].attack for n in attacker_unit_names) + atk_die
    defence_total = (sum(defender.units[n].defence for n in defender_unit_names) +
                     def_die +
                     forts * defender.units['Укреп'].defence +
                     terrain_bonus)

    killed = []
    outcome = ""

    if attack_total > 1.5 * defence_total:
        outcome = 'Атака подавляющая — оборона уничтожена.'
        if consume:
            for n in defender_unit_names:
                defender.available[n] = max(0, defender.available.get(n, 0) - 1)
                killed.append(n)
            if forts > 0:
                avail = defender.available.get('Укреп', 0)
                destroyed = min(avail, forts)
                defender.available['Укреп'] = avail - destroyed
                killed.append(f'Укреп x{destroyed}')
    elif attack_total > defence_total:
        outcome = 'Атака успешна — оборона отступает.'
    else:
        outcome = 'Атака отбита.'

    return outcome, attack_total, defence_total, killed


# Инициализация при импорте
GameState.initialize()