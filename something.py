from random import randrange, random, choice

# from buildings import *

BASE_CHARACTERISTICS = {}
level = 1  # уровень сложности
governors = []  # все правители у ИГРОКА
countries = []


class Area:  # область
    def __init__(self, country, number, points, name, color):  # страна к которой относится, ресурсы
        self.number = number
        self.name = name
        self.points = points
        self.color = color
        self.country = country
        self.buildings = []
        self.governor = None
        self.neighbors = []
        # self.set_neighbors()
        lev = level
        if self.country.AI:
            lev = 1

        # вероятность появления, пределы распространенности
        self.probabilities = {'gold': [0.1, 100, 1000], 'forest': [0.85, 500, 40_000], 'soil': [0.9, 10, 40],
                              'black_earth': [0.25, 40, 100], 'iron': [0.2, 500, 5000],
                              'animals': [0.9, 5_000, 15_000], 'people': [0.95, 1000, 70_000]}
        self.characteristics = {'science': round(50 / lev), 'wood': round(500 / lev), 'animals': 0,
                                'extracted_iron': round(50 / lev), 'extracted_gold': round(35 / lev),
                                'processed_iron': round(50 / lev), 'processed_gold': round(40 / lev)}
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
                    self.characteristics[key] = 0  # иначе - 0\

    def set_neighbors(self, board):
        for point in self.points:
            for neighbor_y in range(-1, 2):
                for neighbor_x in range(-1, 2):
                    neighbor_point = board.board[point[0] + neighbor_y][point[1] + neighbor_x]
                    if neighbor_point != 0 and countries[neighbor_point[0]].areas[neighbor_point[1]] != self and \
                            countries[neighbor_point[0]].areas[neighbor_point[1]] not in self.neighbors:
                        self.neighbors.append(countries[neighbor_point[0]].areas[neighbor_point[1]])

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
                                                                               self.characteristics['soil']
                                                                               // 1_000_000))
        if self.governor:
            self.governor.next_turn()
        else:
            # если нет правителя, то автоматически только ПОТРЕБЛЯЮТСЯ ресурсы для зданий
            for building in self.buildings:  # проходимся по всем зданиям
                if building.get_class() != 'University':
                    self.characteristics[building.next_turn()[0]] += building.next_turn()[2]

    # ручной сбор налогов
    def get_taxes(self):
        for building in self.buildings:  # проходимся по всем зданиям
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
                for key, i in building.price.items():  # проход по необходимым ресурсам
                    if self.characteristics[key] < i:  # в области недостаточно ресурсов
                        i -= self.characteristics[key]
                        self.characteristics[key] = 0  # минус все ресурсы этого типа в областе

                        # все остальное берем из ресурсов страны (из всех областей поровну), но в большем количестве
                        for area in self.country.areas:
                            area.characteristics[key] -= round(i * 1.1) // len([x for x in self.country.areas
                                                                                if x.characteristics[key]
                                                                                > round(i * 1.1) //
                                                                                len(self.country.areas)])
                    else:
                        self.characteristics[key] -= i  # ресурсов этого типа достаточно - вычитаем цену

                self.buildings.append(building)
                print(f'построено {building.get_class()}')
            else:
                return 'недостаточно ресурсов'  # сообщение об ошибке
        else:
            return 'недостаточно ресурсов'

    def del_building(self, building):
        self.buildings = self.buildings[:self.buildings.index(building)] + self.buildings[
                                                                           self.buildings.index(building) + 1:]

    def get_characteristics(self):
        return self.characteristics

    # смена страны, в составе которой находится область
    def change_country(self, country):
        self.country.del_area(self)
        self.country = country
        country.add_area(self)
        # при переходе области из состава одной страны в другую кол-во ресурсов сокращается
        for resource in list(self.characteristics.keys()):
            self.characteristics[resource] = round(self.characteristics[resource] * 0.95)


class Country:
    def __init__(self, name, number, color, bot=True):
        self.number = number
        self.color = color
        self.name = name  # название страны - строка
        self.areas = []  # список всех областей этой страны
        self.characteristics = {}  # хар-ки страны - сумма хар-к всех областей
        self.pacts = {}
        self.contracts = {}
        self.generals = []
        self.neighbors = []
        self.AI = None

        if bot:
            self.AI = CountryAI(self)

    def set_neighbors(self):
        for area in self.areas:
            for neighbor in area.neighbors:
                if neighbor.country not in self.neighbors:
                    self.neighbors.append(neighbor.country)

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
            for c in [k for k, i in self.contracts if i == 'union']:
                c.contracts[country] = 'war'
            for c in [k for k, i in country.contracts if i == 'union']:
                c.contracts[self] = 'war'


class CountryAI:
    def __init__(self, country):
        self.country = country
        self.data = {'pact': 0.5, 'union': 0.35}

    def next_turn(self):
        max_force = 0  # стране с макс силой бот предлагает вступить в союз/заключить пакт с определённой вероятностью
        country_action = None
        for country in countries[:countries.index(self.country)] + countries[countries.index(self.country) + 1:]:
            if max_force < country.power_measuring() and country not in list(self.country.pacts.keys()):
                max_force = max(country.power_measuring(), max_force)
                country_action = country
        if country_action:
            if random() <= self.data['pact']:
                country_action.make_pact(self.country)
            if random() <= self.data['union']:
                country_action.make_union(self.country)

        min_force = None
        country_action = None

        for country in self.country.neighbors:
            if ((not min_force or min_force > country.power_measuring()) and country not in
                    list(self.country.pacts.keys()) and country not in list(self.country.contracts.keys())):
                min_force = country.power_measuring()
                country_action = country
        if country_action and country_action.power_measuring() <= self.country.power_measuring() // 1.3:
            self.country.start_war(country_action)

        # во всех областях будут управлять правители
        for area in self.country.areas:
            if not area.governor:
                area.governor = Governor(area)

        if 'war' in list(self.country.contracts.values()):
            self.war()

    def war(self):
        countries_war = [k for k, i in self.country.contracts if i == 'war']
        # нужно пройтись по областям соседним со странами-врагами (countries_war)
        for area in [a for a in [c for c in countries_war]]:
            soldiers = min([area.characteristics['people'], round(area.characteristics['animals'] // level * 1.5),
                            area.characteristics['extracted_iron'] // 0.05,
                            area.characteristics['wood'] // 0.7]) // 5  # макс кол-во солдат, которые можно нанять
            # в этой области деленные на 5 (чтобы не тратить все ресурсы)
            generals = [i for i in area.country.generals if i.area == area]  # генералы в этой области

            # кол-во генералов должно быть 2 в этой области
            if len(generals) < 2:
                for _ in range(2 - len(generals)):

                    area_neighbours = [a for a in area.neighbors if a.country == area.country and
                                       a.neighbors]
                    # генералы на соседней этой области не на границе НУЖНО ИСПОЛЬЗОВАТЬ ФУНКЦИЮ ОПРЕДЕЛЕНИЯ СОСЕДЕЙ

                    # если в соседних областях нет генералов, то берем случайного из тыла
                    if not [i for i in area.country.generals if i.area in area_neighbours]:
                        if [i for i in area.country.generals if i.area not in countries_war]:
                            # случайный генерал, который не находится на границе с врагом
                            general = choice([i for i in area.country.generals if i.area not in countries_war])

                            # без солдат генерал может премещаться на любое расстояние по стране, а с ним он может
                            # перемещаться только в соседнюю область
                            general.update_army(-general.soldiers)
                            general.change_area(area)  # переезжает в нужную область
                            general.update_army(soldiers)  # найм солдат уже в ней
                    else:
                        # случайный генерал из соседней области переходит в эту
                        general = choice(area_neighbours)
                        general.change_area(area)
                        # если у него недостаточно солдат, то нанимает новых
                        if general.soldiers < 1000:
                            general.update_army(soldiers)
            else:
                # проходим по всем генералам в этой области и, если надо, нанимаем солдат
                for general in generals:
                    if general.soldiers < 1000:
                        general.update_army(soldiers)
            attack_general = max(generals, key=lambda g: g.characteristics['attack'])  # атакующий генерал
            defence_general = max(generals, key=lambda g: g.characteristics['defence'])  # защищающийся генерал

            # КАААААААААААААК! КАААААААААААААААК ЭТО СДЕЛААААААААААААААААААААТЬ!!!
            attack_general.attack()
            defence_general.defence()


class Governor:
    def __init__(self, area):
        lev = not area.country.AI  # на бота не влияет уровень сложности
        self.characteristics = {'loyalty': randrange(85 - (level - 1) * lev * 10, 95 - (level - 1) * 10 * lev),
                                'intellect': randrange(75 - (level - 1) * 10 * lev, 90 - (level - 1) * 10 * lev),
                                'honesty': randrange(85 - (level - 1) * 10 * lev, 100 - (level - 1) * lev * 10)}
        self.area = area

    def next_turn(self):
        if self.area:
            # условие строительства здания
            for building in [University, GoldMine, IronMine, Sawmill, MetallurgicalPlant, ArmyAcademy]:
                if ((building(self.area).get_class() not in [i.get_class() for i in self.area.buildings] or
                     all([self.area.country.characteristics[i] >= k for i, k in building.price.items()])) and
                        random() * 100 <= self.characteristics['intellect'] and
                        self.area.characteristics[[i for i in list(building.data.keys()) if i != 'years'
                                                                                            and i != 'level'][0]]
                        >= building.data[[i for i in list(building.data.keys()) if i != 'year' and i != 'level'][0]]):
                    if building == ArmyAcademy:
                        if len(self.area.country.generals) < len(self.area.country.areas) // 2:
                            self.area.build_building(building(self.area))
                    else:
                        self.area.build_building(building(self.area))

            for building in self.area.buildings:  # проходимся по всем зданиям
                if building.get_class() != 'University':
                    # то, сколько минусуется ресурсов не зависит от честности правителя
                    self.area.characteristics[building.next_turn()[0]] += building.next_turn()[2]
                if building.get_class() != 'ArmyAcademy':
                    # + в добытые ресурсы, НО не все, тк это зависит от честности правителя
                    self.area.characteristics[building.next_turn()[1]] += round(abs(building.next_turn()[2]) *
                                                                                self.characteristics['honesty'] * 0.01)

            # если идет война, то с определённой вероятностью правитель предаёт страну + к вероятности - наличие границы
            # с вражеским государством
            if ('war' in list(self.area.country.contracts.values()) and random() > self.characteristics['loyalty'] +
                    sum([a.country in [i for k, i in self.area.country.contracts if i == 'war'] for a in
                         self.area.neighbors]) * 0.1):
                self.area.change_country(choice([k for k, i in list(self.area.country.contracts) if i == 'war']))

    # поменять область, которой руководит правитель
    def change_area(self, area):
        self.area = area


class General:
    def __init__(self, area):
        lev = not area.country.AI
        self.characteristics = {
            'attack': 1 + randrange(20 - (level - 1) * 10 * lev, 100 - (level - 1) * 10 * lev) // 100,
            'defence': 1 + randrange(20 - (level - 1) * 10 * lev, 100 - (level - 1) * 10 * lev) // 100,
            'level': 1 + randrange(20 - (level - 1) * 10 * lev, 100 - (level - 1) * 10 * lev) // 100}
        self.soldiers = 0  # количество солдат армии генерала
        self.area = area

    # обновить армию (количество солдат)
    def update_army(self, soldiers):
        if soldiers > 0:
            lev = level
            if self.area.country.AI:
                lev = 1
            if (self.area.characteristics['animals'] >= soldiers * level and self.area.characteristics['extracted_iron']
                    > soldiers * 0.1 and self.area.characteristics['wood'] > soldiers * 0.9 and
                    self.area.characteristics['people'] > soldiers):
                self.area.characteristics['animals'] -= round(soldiers * lev // 1.5)
                self.area.characteristics['extracted_iron'] -= round(soldiers * 0.05)
                self.area.characteristics['wood'] -= round(soldiers * 0.7)
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
    def defence(self):
        return self.characteristics['defence'] * self.soldiers * self.characteristics['level']

    def change_area(self, area):
        if self.soldiers == 0 or True:  # если нет солдат или self.area соседняя с area
            self.area = area


class Building:
    def get_class(self):  # название класса
        return self.name


class University(Building):
    price = {'wood': 1000, 'extracted_iron': 50, 'extracted_gold': 10, 'science': 25}  # цена постройки
    data = {'science': 10, 'level': 1, 'years': 5}

    def __init__(self, area):
        self.name = 'University'
        self.year = 1
        self.area = area

    def next_turn(self):
        if self.year % self.data['years'] == 0:  # правители появляются раз в несколько лет
            for _ in range(self.data['level']):  # в зависимости от уровня университета, увеличивается
                # количество выпускаемых правителей
                if not self.area.country.AI:
                    governors.append(Governor(self.area))  # создание правителей
                    self.area.governor = governors[-1]

        self.year += 1
        return 'science', 'science', self.data['science']

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['science'] += 7


class GoldMine(Building):
    price = {'wood': 300, 'iron': 15, 'science': 10}
    data = {'gold': 10, 'level': 1}

    def __init__(self, area):
        self.area = area
        self.name = 'GoldMine'

    def next_turn(self):
        if self.area.characteristics['gold']:
            if self.area.characteristics['gold'] < self.data['gold']:
                gold = self.area.characteristics['gold']
                return 'gold', 'extracted_gold', -gold
            else:
                return 'gold', 'extracted_gold', -self.data['gold']
        return 'gold', 'extracted_gold', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['gold'] += 5


class IronMine(Building):
    price = {'wood': 300, 'iron': 15, 'science': 10}
    data = {'iron': 25, 'level': 1}

    def __init__(self, area):
        self.area = area
        self.name = 'IronMine'

    def next_turn(self):
        if self.area.characteristics['iron']:
            if self.area.characteristics['iron'] < self.data['iron']:
                iron = self.area.characteristics['iron']
                return 'iron', 'extracted_iron', -iron
            return 'iron', 'extracted_iron', -self.data['iron']
        return 'iron', 'extracted_iron', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['iron'] += 20


class Sawmill(Building):
    price = {'wood': 300, 'extracted_iron': 30, 'science': 10}
    data = {'forest': 100, 'level': 1}

    def __init__(self, area):
        self.area = area
        self.name = 'Sawmill'

    def next_turn(self):
        if self.area.characteristics['forest']:
            if self.data['forest'] > self.area.characteristics['forest']:
                return 'forest', 'wood', -self.area.characteristics['forest']
            return 'forest', 'wood', -self.data['forest']
        return 'forest', 'wood', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['forest'] += 100
            self.data['level'] += 1


class MetallurgicalPlant(Building):
    price = {'extracted_iron': 70, 'wood': 1000, 'science': 40}
    data = {'level': 1, 'extracted_iron': 20}

    def __init__(self, area):
        self.area = area
        self.name = 'MetallurgicalPlant'

    def next_turn(self):
        if self.area.characteristics['extracted_iron']:
            if self.area.characteristics['extracted_iron'] < self.data['extracted_iron']:
                return 'extracted_iron', 'processed_iron', -self.area.characteristics['extracted_iron']
            return 'extracted_iron', 'processed_iron', -self.data['extracted_iron']
        return 'extracted_iron', 'processed_iron', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['extracted_iron'] += 20


class ArmyAcademy(Building):
    price = {'wood': 1000, 'processed_iron': 15, 'science': 40}
    data = {'years': 5, 'level': 1, 'science': 10}

    def __init__(self, area):
        self.name = 'ArmyAcademy'
        self.year = 0
        self.area = area

    def next_turn(self):
        if self.area.characteristics['science'] >= self.data['science']:
            if self.year % self.data['years'] == 0:
                for _ in range(self.data['level']):
                    # создание объекта класса "Генерал"
                    self.area.country.generals.append(General(self.area))
            self.year += 1
            return 'science', '', -self.data['science']
        return 'science', '', 0

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['science'] += 5


if __name__ == '__main__':
    b = Country('Russia', 1, 1, bot=True)
    countries.append(b)
    a = Area(b, 1, 1, 1, 1)
    a2 = Area(b, 1, 1, 1, 1)
    print(a.get_characteristics())
    print(a2.get_characteristics())
    print()
    b.add_area(a)
    b.add_area(a2)
    # a.build_building(University(a))
    # a.build_building(GoldMine(a))
    # a.build_building(IronMine(a))
    # a.build_building(Sawmill(a))
    # a.build_building(ArmyAcademy(a))

    b.next_turn()
    print(b.get_characteristics())
    # a.build_building(MetallurgicalPlant(a))
    while not input():
        b.next_turn()
        print(a.get_characteristics())
        print(a2.get_characteristics())
        print(b.get_characteristics())
        print(b.power_measuring(), [a.buildings for a in b.areas])
