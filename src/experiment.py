class experiment():
    def __init__(self):
        self.screens = []
        self.reward = 0

    def format_money(self, amount=None):
        if amount == None:
            amount = self.money
        return "%d.%02d"%(amount/100,amount%100)

