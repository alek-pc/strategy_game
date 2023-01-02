from npc import *

BASE_CHARACTERISTICS = {}
level = 1  # уровень сложности
governors = []  # все правители у ИГРОКА
generals = []
countries = []


class Area:  # область
    def __init__(self, country):  # страна к которой относится, ресурсы
        self.country = country
        self.buildings = []
        self.governor = None
        # вероятность появления, пределы распространенности
        self.probabilities = {'gold': [0.1, 100, 1000], 'forest': [0.85, 500, 40_000], 'soil': [0.85, 10, 40],
                              'black_earth': [0.25, 40, 100], 'iron': [0.15, 500, 5000],
                              'animals': [0.9, 5000, 20_000], 'people': [0.95, 1000, 70_000]}
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
                if self.characteristics[key] > round(self.characteristics['people'] * 0.01):
                    self.characteristics[key] -= round(self.characteristics['people'] * 0.01)
                else:
                    self.characteristics[key] = randrange(1000, 3000)
                self.characteristics[key] = round(self.characteristics[key] * 1.15)
            elif key == 'people':
                self.characteristics[key] = round(self.characteristics[key] * (1.005 + self.characteristics['animals'] *
                                                                               self.characteristics['soil'] // 1000000))
                if self.governor:
                    self.governor.next_turn()
                else:

                    # !!!должен быть ручной сбор ресурсов!!!

                    for building in self.buildings:  # проходимся по всем зданиям
                        if building.get_class() != 'University':
                            self.characteristics[building.next_turn()[0]] += building.next_turn()[2]
                        if building.get_class() != 'ArmyAcademy':
                            # + в добытые ресурсы
                            self.characteristics[building.next_turn()[1]] += abs(building.next_turn()[2])

    def build_building(self, building):  # добавить здание: класс здания
        # ограничение кол-ва зданий одного типа в одной области - 3 и кол-ва зданий - 6
        if [i.get_class() for i in self.buildings].count(building.get_class()) < 3 and len(self.buildings) < 6:
            # первые три здания одного типа в стране - бесплатно
            if [i.get_class() for x in self.country.areas for i in x.buildings].count(building.get_class()) <= 2:
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
        else:
            return 'недостаточно ресурсов'

    def del_building(self, building):
        self.buildings = self.buildings[:self.buildings.index(building)] + self.buildings[
                                                                           self.buildings.index(building) + 1:]

    def get_characteristics(self):
        return self.characteristics


class Country:
    def __init__(self, name, bot=1):
        self.name = name  # название страны - строка
        self.areas = []  # список всех областей этой страны
        self.characteristics = {}  # хар-ки страны - сумма хар-к всех областей
        self.pacts = {}
        self.contracts = {}
        self.AI = None

        if bot:
            self.AI = CountryAI(self)

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
        # если эта страна - бот, то ИИ делает ход
        for pact in list(self.pacts.keys()):
            if self.pacts[pact]:
                self.pacts[pact] -= 1

        if self.AI:
            self.AI.next_turn()

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

    # измерение силы страны влияет: население, наука, лес, залежи руды, кол-во зданий, кол-во областей
    def power_measuring(self):
        return (self.characteristics['people'] * self.characteristics['science'] * self.characteristics['forest']
                * self.characteristics['iron'] * sum([1 for area in self.areas for _ in area.buildings]) *
                len(self.areas))

    def make_pact(self, country):
        if country not in list(self.pacts.keys()) or self.pacts[country] == 0:
            # разница сил небольшая
            if (self.power_measuring() < country.power_measuring() or
                    abs(country.power_measuring() - self.power_measuring()) < self.power_measuring() // 2):
                self.pacts[country] = 15

    def make_union(self, country):
        # если союз не заключен и нет противоречий в союзах
        if country not in list(self.contracts.keys()) and all([self.contracts[i] == country.contracts[i] for i, k in
                                                               self.contracts if i in list(country.unions.keys())]):
            self.contracts[country] = 'union'
            country.contracts[self] = 'union'
            # союзник союзника - союзник, а враг союзника - враг => добавляем союзников и противников союзникам
            for c, cond in country.contracts:
                self.contracts[c] = cond
            for c, cond in self.contracts:
                country.contracts[c] = cond

    def start_war(self, country):
        if country not in list(self.contracts.keys()) + list(self.pacts.keys()):
            self.contracts[country] = 'war'
            country.contracts[self] = 'war'


if __name__ == '__main__':
    b = Country('Russia', bot=0)
    a = Area(b)
    b.add_area(a)
    a.build_building(University(a))
    a.build_building(GoldMine(a))
    a.build_building(IronMine(a))
    a.build_building(Sawmill(a))
    a.build_building(ArmyAcademy(a))

    b.next_turn()
    print(b.get_characteristics())
    a.build_building(MetallurgicalPlant(a))
    while not input():
        b.next_turn()
        print(b.get_characteristics())
