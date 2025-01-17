class FVGData:
    def __init__(self, date, name, isBroken, isConsolidating, priceDiff):
        self.institution_holding = 0
        self.date = date
        self.name = name
        self.isBroken = isBroken
        self.isConsolidating = isConsolidating
        self.priceDiff = priceDiff
        self.count = 0
        self.awayFrom52WeekHigh = 0

    def set_count(self, count):
        self.count = count

    def set_away_from52_week_high(self, diff):
        if diff is not None:
            self.awayFrom52WeekHigh = diff * 100

    def set_institution_holding(self, holding):
        if holding is not None:
            self.institution_holding = holding * 100

    def get_name(self):
        return self.name

    def printName(self):
        print(f"\"{self.name}\"")

    def print(self):
        # print(f"{self.name} count {self.count} Diff - {self.priceDiff} C - {self.isConsolidating} Br - {self.isBroken}")
        try:
            print(f"{self.name} count {self.count} C - {self.isConsolidating} Br - {self.isBroken} awayFromHigh - {int(self.awayFrom52WeekHigh)} FIIDIItionHolding - {int(self.institution_holding)} Diff - {int(self.priceDiff)} %")
        except Exception as e:
            print(f"print {e}")
