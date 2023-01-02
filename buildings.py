from main import governors, generals, General, Governor


class Building:
    def get_class(self):  # название класса
        return self.name


class University(Building):
    price = {'wood': 1000, 'processed_iron': 50, 'processed_gold': 10, 'science': 25}  # цена постройки
    data = {'science': 10, 'level': 1, 'years': 5}

    def __init__(self, area):
        self.name = 'University'
        self.year = 1
        self.area = area

    def next_turn(self):
        if self.year % self.data['years'] == 0:  # правители появляются раз в несколько лет
            for _ in range(self.data['level']):  # в зависимости от уровня университета, увеличивается
                # количество выпускаемых правителей
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
                    generals.append(General(self.area))
            self.year += 1
            return 'science', '', -self.data['science']

    def level_up(self):
        if self.data['level'] < 3:
            self.data['level'] += 1
            self.data['science'] += 5
