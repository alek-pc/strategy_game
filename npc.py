from random import randrange, random
from main import level, countries
from buildings import *


class CountryAI:
    def __init__(self, country):
        self.country = country
        self.data = {'pact': 0.5, 'union': 0.35}

    def next_turn(self):
        max_force = 0  # стране с макс силой бот предлагает вступить в союз/заключить пакт с определённой вероятностью
        country_action = None
        for country in countries:
            if max_force < country.power_measuring() and country not in list(self.country.pacts.keys()):
                max_force = max(country.power_measuring(), max_force)
                country_action = country

        if random() <= self.data['pact']:
            country_action.make_pact(self.country)
        if random() <= self.data['union']:
            country_action.make_union(self.country)

        min_force = None
        country_action = None

        # !!! НАДО ПРОХОДИТЬ ПО СОСЕДЯМ, А НЕ ПО ВСЕМ СТРАНАМ !!!
        for country in countries:
            if ((min_force > country.power_measuring() or not min_force) and country not in
                    list(self.country.pacts.keys())):
                min_force = country.power_measuring()
                country_action = country
        self.country.start_war(country_action)
        # во всех областях будут управлять правители
        for area in self.country.areas:
            if not area.governor:
                area.governor = Governor(area)


class Governor:
    def __init__(self, area):
        self.characteristics = {'loyalty': randrange(75 - (level - 1) * 10, 90 - (level - 1) * 10),
                                'intellect': randrange(65 - (level - 1) * 10, 80 - (level - 1) * 10),
                                'honesty': randrange(80 - (level - 1) * 10, 100 - (level - 1) * 10)}
        self.area = area

    def next_turn(self):
        if self.area:
            # условие строительства здания
            for building in [University, GoldMine, IronMine, Sawmill, MetallurgicalPlant]:
                if ((building(self.area).get_class() not in [i.get_class() for i in self.area.buildings] or
                     all([self.area.country.characteristics[i] >= k for i, k in building.price.items()])) and
                        random() * 100 <= self.characteristics['intellect'] and
                        self.area.characteristics[[i for i in list(building.data.keys()) if i != 'year' != 'level'][0]]
                        >= building.data[[i for i in list(building.data.keys()) if i != 'year' and i != 'level'][0]]):
                    self.area.build_building(building(self.area))

            for building in self.area.buildings:  # проходимся по всем зданиям
                if building.get_class() != 'University':
                    # то, сколько минусуется ресурсов не зависит от честности правителя
                    self.area.characteristics[building.next_turn()[0]] += building.next_turn()[2]
                if building.get_class() != 'ArmyAcademy':
                    # + в добытые ресурсы, НО не все, тк это зависит от честности правителя
                    self.area.characteristics[building.next_turn()[1]] += round(abs(building.next_turn()[2]) *
                                                                                self.characteristics['honesty'] * 0.01)

            # СДЕЛАТЬ !!!если начинается война, то с определённой вероятностью правитель предаёт страну!!! СДЕЛАТЬ

    # поменять область, которой руководит правитель
    def change_area(self, area):
        self.area = area


class General:
    def __init__(self, area):
        self.characteristics = {'attack': 1 + randrange(20 - (level - 1) * 10, 100 - (level - 1) * 10) // 100,
                                'defence': 1 + randrange(20 - (level - 1) * 10, 100 - (level - 1) * 10) // 100,
                                'level': 1 + randrange(20 - (level - 1) * 10, 100, 100 - (level - 1) * 10) // 100}
        self.soldiers = 0  # количество солдат армии генерала
        self.area = area

    # обновить армию (количество солдат)
    def update_army(self, soldiers):
        if soldiers > 0:
            if (self.area.characteristics['animals'] >= soldiers * level and self.area.characteristics['extracted_iron']
                    > soldiers * 0.1 and self.area.characteristics['wood'] > soldiers * 0.9 and
                    self.area.characteristics['people'] > soldiers):
                self.area.characteristics['animals'] -= soldiers * level
                self.area.characteristics['extracted_iron'] -= soldiers * 0.1
                self.area.characteristics['wood'] -= soldiers * 0.9
                self.area.characteristics['people'] -= soldiers
                self.soldiers += soldiers
            else:
                return 'недостаточно ресурсов'
        else:
            if self.soldiers >= abs(soldiers):
                self.area.characteristics['people'] += abs(soldiers)
                self.soldiers += soldiers
            else:
                return 'нет столько солдат'

    # усилить армию (поднять уровень)
    def powering_army(self, force):
        self.characteristics['level'] = force

    # атака, возвращает атаку (солдаты * общий коэффицент силы * коэффицент атаки)
    def attack(self):
        return self.characteristics['attack'] * self.soldiers * self.characteristics['level']

    # оборона, возвращает защиту (солдаты * общий коэффицент силы * коэффицент обороны)
    def defense(self):
        return self.characteristics['defense'] * self.soldiers * self.characteristics['level']

    def change_area(self, area):
        self.area = area
