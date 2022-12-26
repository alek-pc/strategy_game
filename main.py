from random import randrange, random

BASE_CHARACTERISTICS = {}
level = 1   # уровень сложности


class Area:  # область
    def __init__(self, country, resources):  # страна к которой относится, ресурсы
        self.country = country
        self.resources = resources
        self.buildings = []
        # вероятность появления, пределы распространенности
        self.probabilities = {'gold': [0.1, 100, 1000], 'forest': [0.85, 500, 40_000], 'soil': [0.85, 10, 40],
                              'black_earth': [0.25, 40, 100], 'iron': [0.15, 500, 5000],
                              'animals': [0.9, 100, 10_000], 'people': [0.95, 1000, 100_000]}
        self.characteristics = {'science': round(50 / level), 'wood': round(500 / level), 'animals': 0,
                                'extracted_iron': round(50 / level), 'extracted_gold': round(35 / level),
                                'processed_iron': round(50 / level), 'processed_gold': round(40 / level)}
        # базовое количество добываемых ресурсов (необходимые для построек) определяется уровнем (больше уровень -
        # меньше базовых ресурсов)

        self.set_characteristic()

    def set_characteristic(self):  # рандомная генерация данных об области
        for key, el in self.probabilities.items():
            if key != 'black_earth':  # black_earth - вероятность появления чернозёма
                if random() <= el[0]:  # эта вещь будет
                    self.characteristics[key] = randrange(*el[1:])  # есть - рандомное кол-во предмета
                    if random() <= self.probabilities['black_earth'][0] and key == 'soil':
                        self.characteristics[key] = randrange(*self.probabilities['black_earth'][1:])
                else:
                    self.characteristics[key] = 0  # иначе - 0

    def next_turn(self):  # обновление данных области
        for key, el in self.characteristics.items():
            if key == 'forest':
                self.characteristics[key] = round(self.characteristics[key] * 1.05)
            elif key == 'animals':
                self.characteristics[key] = round(self.characteristics[key] * 1.05)
            elif key == 'people':
                self.characteristics[key] = round(self.characteristics[key] * 1.007)

        for building in self.buildings:  # проходимся по всем зданиям

            if building.get_class() != 'University':
                self.characteristics[building.next_turn()[0]] += building.next_turn()[2]
            # + в добытые ресурсы
            self.characteristics[building.next_turn()[1]] += abs(building.next_turn()[2])

    def build_building(self, building):  # добавить здание: класс здания
        if building.get_class() not in [i.get_class() for i in self.buildings]:  # первое здание - бесплатно
            self.buildings.append(building)
        elif all([self.country.characteristics[i] >= k for i, k in building.price.items()]):  # достаточно ресурсов
            for i, k in building.price.items():  # проход по необходимым ресурсам
                if self.characteristics[i] < k:  # в области недостаточно ресурсов
                    k -= self.characteristics[i]
                    self.characteristics[i] = 0  # минус все ресурсы этого типа в областе
                    self.country.characteristics[i] -= k * 1.1  # все остальное берем из ресурсов страны,
                    # но в большем количестве
                else:
                    self.characteristics[i] -= k  # ресурсов этого типа достаточно - вычитаем цену

            self.buildings.append(building)
        else:
            return 'недостаточно ресурсов'  # сообщение об ошибке

    def del_building(self, building):
        self.buildings = self.buildings[:self.buildings.index(building)] + self.buildings[
                                                                           self.buildings.index(building) + 1:]

    def get_characteristics(self):
        return self.characteristics


class Country:
    def __init__(self, name):
        self.name = name  # название страны - строка
        self.areas = []  # список всех областей этой страны
        self.characteristics = {}  # хар-ки страны - сумма хар-к всех областей

    def add_area(self, area):  # добавление территории в страну
        self.areas.append(area)
        if len(self.areas) == 1:  # если до этого территорий было ноль
            # хар-ка области - хар-ка страны
            for ind in list(area.get_characteristics().keys()):
                self.characteristics[ind] = area.get_characteristics()[ind]
        else:
            for ind in list(area.characteristics.keys()):  # суммируем хар-ки области и страны
                self.characteristics[ind] += area.characteristics[ind]

    def del_area(self, area):  # удалить область из страны (захватили)
        self.areas = self.areas[:self.areas.index(area)] + self.areas[self.areas.index(area) + 1:]
        for ind, el in area.characteristics:
            self.characteristics[ind] -= area.characteristics[ind]

    def next_turn(self):  # следующий ход
        # обнуление хар-к страны
        for ind in list(self.areas[0].characteristics.keys()):
            self.characteristics[ind] = 0

        # следующий ход для каждой области
        for area in self.areas:
            area.next_turn()
            for ind in list(area.characteristics.keys()):  # обновление хар-к страны
                self.characteristics[ind] += area.characteristics[ind]

    def get_characteristics(self):
        return self.characteristics


class Building:
    def get_class(self):  # название класса
        return self.name


class University(Building):
    price = {'wood': 1000, 'processed_iron': 50, 'processed_gold': 10, 'science': 25}  # цена постройки

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
                return 'gold', 'extracted_gold', -gold
            else:
                return 'gold', 'extracted_gold', -self.data['mining']
        return 'gold', 'extracted_gold', 0

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
                return 'iron', 'extracted_iron', -iron
            return 'iron', 'extracted_iron', -self.data['mining']
        return 'iron', 'extracted_iron', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['mining'] += 20


class Sawmill(Building):
    price = {'wood': 300, 'extracted_iron': 30, 'science': 3}

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
    price = {'extracted_iron': 70, 'wood': 1000, 'science': 40}

    def __init__(self, area):
        self.data = {'level': 1, 'processing': 20}
        self.area = area
        self.name = 'MetallurgicalPlant'

    def next_turn(self):
        if self.area.characteristics['extracted_iron']:
            if self.area.characteristics['extracted_iron'] < self.data['processing']:
                return 'extracted_iron', 'processed_iron', -self.area.characteristics['extracted_iron']
            return 'extracted_iron', 'processed_iron', -self.data['processing']
        return 'extracted_iron', 'processed_iron', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['processing'] += 20


class ArmyAcademy(Building):
    price = {'wood': 1000, 'processed_iron': 15, 'science': 30}

    def __init__(self, area):
        self.name = 'ArmyAcademy'
        self.data = {'years': 5, 'level': 1, 'science': 10}
        self.year = 0
        self.area = area

    def next_turn(self):
        if self.area.characteristics['science'] >= self.data['science']:
            if self.year % self.data['years'] == 0:
                for _ in range(self.data['level']):
                    # создание объекта класса "Генерал"
                    pass
            self.year += 1
            return 'science', '', -self.data['science']

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['science'] += 5


if __name__ == '__main__':
    b = Country('Russia')
    a = Area(b, [])
    b.add_area(a)
    print()
    a.build_building(University(a))
    a.build_building(GoldMine(a))
    a.build_building(IronMine(a))
    a.build_building(Sawmill(a))

    b.next_turn()
    print(b.get_characteristics())
    a.build_building(MetallurgicalPlant(a))
    while not input():
        b.next_turn()
        print(b.get_characteristics())
        print(a.build_building(Sawmill(a)))
        print(b.get_characteristics())
