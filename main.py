from random import randrange, random

BASE_CHARACTERISTICS = {}


class Area:  # область
    def __init__(self, country, resources):  # страна к которой относится, ресурсы
        self.country = country
        self.resources = resources
        self.buildings = []
        # вероятность появления, пределы распространенности
        self.probabilities = {'gold': [0.1, 100, 1000], 'forest': [0.85, 500, 40_000], 'soil': [0.85, 10, 40],
                              'black_earth': [0.25, 40, 100], 'iron': [0.15, 500, 5000],
                              'animals': [0.9, 100, 10_000], 'people': [0.95, 1000, 100_000]}
        self.characteristics = {'science': 0}
        self.extracted_resources = {'gold': 0, 'iron': 0, 'processed_gold': 0, 'processed_iron': 0, 'science': 0,
                                    'wood': 0, 'animals': 0}
        self.set_characteristic()

    def set_characteristic(self):  # рандомная генерация данных об области
        for key, el in self.probabilities.items():
            if key != 'black_earth':
                if random() <= el[0]:
                    self.characteristics[key] = randrange(*el[1:])
                    if random() <= self.probabilities['black_earth'][0] and key == 'soil':
                        self.characteristics[key] = randrange(*self.probabilities['black_earth'][1:])
                else:
                    self.characteristics[key] = 0

        print(self.characteristics)

    def next_turn(self):  # обновление данных области
        for key, el in self.characteristics.items():
            if key == 'forest':
                self.characteristics[key] = round(self.characteristics[key] * 1.05)
            elif key == 'animals':
                self.characteristics[key] = round(self.characteristics[key] * 1.05)
            elif key == 'people':
                self.characteristics[key] = round(self.characteristics[key] * 1.007)

        for building in self.buildings:
            if building.get_class() != 'MetallurgicalPlant':
                self.characteristics[building.next_turn()[0]] += building.next_turn()[2]
            else:
                self.extracted_resources[building.next_turn()[0]] += building.next_turn()[2]
            self.extracted_resources[building.next_turn()[1]] += abs(building.next_turn()[2])

        print(2, self.extracted_resources)

    def add_building(self, building):  # добавить здание: класс - здание
        self.buildings.append(building)

    def del_building(self, building):
        self.buildings = self.buildings[:self.buildings.index(building)] + self.buildings[
                                                                           self.buildings.index(building) + 1:]

    def get_characteristics(self):
        return self.characteristics


class Country:
    def __init__(self, name):
        self.name = name
        self.areas = []
        self.characteristics = {}

    def add_area(self, area):
        self.areas.append(area)
        if len(self.areas) == 1:
            self.characteristics = area.get_characteristics()

            for ind in list(area.extracted_resources.keys()):
                if ind == 'iron' or ind == 'gold':
                    self.characteristics['extracted_' + ind] = area.extracted_resources[ind]
                else:
                    self.characteristics[ind] = area.extracted_resources[ind]
        else:
            self.update(area)

    def update(self, area):
        for ind in list(area.extracted_resources.keys()):
            if ind == 'iron' or ind == 'gold':
                self.characteristics['extracted_' + ind] += area.extracted_resources[ind]
            else:
                self.characteristics[ind] += area.extracted_resources[ind]

        for ind in list(area.characteristics.keys()):
            self.characteristics[ind] += area.characteristics[ind]

    def del_area(self, area):
        self.areas = self.areas[:self.areas.index(area)] + self.areas[self.areas.index(area) + 1:]
        for ind, el in area.characteristics:
            self.characteristics[ind] -= area.characteristics[ind]

    def next_turn(self):
        for ind in list(self.areas[0].extracted_resources.keys()):
            if ind == 'iron' or ind == 'gold':
                self.characteristics['extracted_' + ind] = 0
            else:
                self.characteristics[ind] = 0

        for ind in list(self.areas[0].characteristics.keys()):
            self.characteristics[ind] = 0

        for area in self.areas:
            print(1, area.characteristics)
            area.next_turn()
            self.update(area)

    def get_characteristics(self):
        return self.characteristics


class Building:
    def get_class(self):
        return self.name


class University(Building):
    price = {'wood': 1000, 'processed_iron': 50, 'processed_gold': 10, 'science': 25}

    def __init__(self, area):
        self.name = 'University'
        self.data = {'science': 10, 'level': 1, 'years': 5}
        self.year = 0

    def next_turn(self):
        if self.year % self.data['years'] == 0:  # правители появляются раз в несколько лет
            for _ in range(self.data['level']):  # в зависимости от уровня университета, увеличивается
                # количество выпускаемых правителей
                pass  # создание правителей
        self.year += 1

        return 'science', 'science', self.data['science']

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['science'] += 7


class GoldMine(Building):
    price = {'wood': 300, 'iron': 15, 'science': 10}

    def __init__(self, area):
        self.data = {'mining': 10, 'level': 1}
        self.area = area
        self.name = 'GoldMine'

    def next_turn(self):
        if self.area.characteristics['gold']:
            if self.area.characteristics['gold'] < self.data['mining']:
                gold = self.area.characteristics['gold']
                return 'gold', 'gold', -gold
            else:
                return 'gold', 'gold', -self.data['mining']
        return 'gold', 'gold', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['mining'] += 5


class IronMine(Building):
    price = {'wood': 300, 'iron': 15, 'science': 10}

    def __init__(self, area):
        self.area = area
        self.data = {'mining': 25, 'level': 1}
        self.name = 'IronMine'

    def next_turn(self):
        if self.area.characteristics['iron']:
            if self.area.characteristics['iron'] < self.data['mining']:
                iron = self.area.characteristics['iron']
                return 'iron', 'iron', -iron
            return 'iron', 'iron', -self.data['mining']
        return 'iron', 'iron', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['mining'] += 20


class Sawmill(Building):
    price = {'wood': 300, 'iron': 30, 'science': 3}

    def __init__(self, area):
        self.data = {'mining': 100, 'level': 1}
        self.area = area
        self.name = 'Sawmill'

    def next_turn(self):
        if self.area.characteristics['forest']:
            if self.data['mining'] > self.area.characteristics['forest']:
                return 'forest', 'wood', -self.area.characteristics['forest']
            return 'forest', 'wood', -self.data['mining']
        return 'forest', 'wood', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['mining'] += 100
            self.data['level'] += 1


class MetallurgicalPlant(Building):
    price = {'iron': 70, 'wood': 1500, 'science': 30}

    def __init__(self, area):
        self.data = {'level': 1, 'processing': 20}
        self.area = area
        self.name = 'MetallurgicalPlant'

    def next_turn(self):
        if self.area.extracted_resources['iron']:
            if self.area.extracted_resources['iron'] < self.data['processing']:
                return 'iron', 'processed_iron', -self.area.extracted_resources['iron']
            return 'iron', 'processed_iron', -self.data['processing']
        return 'iron', 'processed_iron', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['processing'] += 20


b = Country('Russia')
a = Area(b, [])
b.add_area(a)
print()
b.areas[0].add_building(University(a))
b.areas[0].add_building(GoldMine(a))
b.areas[0].add_building(IronMine(a))
b.areas[0].add_building(Sawmill(a))

b.next_turn()
print(b.get_characteristics())
b.areas[0].add_building(MetallurgicalPlant(a))
while not input():
    b.next_turn()
    print(b.get_characteristics())
    print()
