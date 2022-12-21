import sqlite3
from fractions import Fraction
class bjmem:
    def __init__(self):
        self.player_and_dealer = []
        self.deck = {"A": 4, "2": 4, "3": 4, "4": 4, "5": 4, "6": 4, "7": 4, "8": 4, "9": 4, "10": 16}

    def count_points(self, hand):
        total_points = 0
        Aces = 0

        for card in hand:
        #deals with non Aces first
            if card != "A":
                total_points += int(card)
            else:
                Aces += 1
            
        if Aces == 0:
            return total_points
        
        elif Aces == 1:
            if total_points + 11 <= 21:
                total_points += 11
            else:
                total_points += 1

        else:
            total_points += Aces - 2
            points_left = 21 - total_points
            if points_left <= 11:
                total_points += 2
            else:
                total_points += 12
        return total_points

    def getAllComb(self, deck, dealer, player):
        for card in deck.keys():
            if deck[card] == 0:
                continue

            future_player = player.copy()
            future_player.append(card)

            if [dealer, sorted(future_player, key=lambda o: 1 if o == 'A' else int(o))] in self.player_and_dealer:
                continue

            future_deck = deck.copy()
            future_deck[card] -= 1
            
            if len(future_player) < 2:
                self.getAllComb(future_deck, dealer, future_player)

            elif self.count_points(future_player) >= 21:
                continue

            else:
                self.player_and_dealer.append([dealer, sorted(future_player, key=lambda o: 1 if o == 'A' else int(o))])
                self.getAllComb(future_deck, dealer, future_player)

    def start(self):
        for card in self.deck.keys():
            future_deck = self.deck.copy()
            future_deck[card] -= 1
            self.getAllComb(future_deck, [card], [])

class bjstats:
    def __init__(self):
        self.dealer = []
        self.player = []
        self.deck = {"A": 4, "2": 4, "3": 4, "4": 4, "5": 4, "6": 4, "7": 4, "8": 4, "9": 4, "10": 16}
        self.player_wins = 0
        self.dealer_wins = 0
    
    def count_points(self,hand):
        total_points = 0
        Aces = 0

        for card in hand:
        #deals with non Aces first
            if card != "A":
                total_points += int(card)
            else:
                Aces += 1
            
        if Aces == 0:
            return total_points
        
        elif Aces == 1:
            if total_points + 11 <= 21:
                total_points += 11
            else:
                total_points += 1

        else:
            total_points += Aces - 2
            points_left = 21 - total_points
            if points_left <= 11:
                total_points += 2
            else:
                total_points += 12
        return total_points

    def set_dealer(self,cards):
        self.dealer = ["10" if card in ("J", "Q", "K") else card for card in cards]
        self.deck[self.dealer[0]] -= 1

    def set_player(self,cards):
        self.player = ["10" if card in ("J", "Q", "K") else card for card in cards]
        for card in self.player:
            self.deck[card] -= 1

    def percent_hit(self):
        # for chances of hitting

        fails = 0
        success = 0
        exceeds = False

        for potential_card, card_count in self.deck.items():
            # short circuits loop since we’re looping through an ascending dictionary
            if exceeds:
                fails += card_count
                continue

            future_player = self.player.copy()
            future_player.append(potential_card)

            if self.count_points(future_player) > 21:
                fails += card_count
                exceeds = True
            else:
                success += card_count
            
        return success, fails

    def recal(self):
        self.player_wins = self.player_wins/(self.player_wins+self.dealer_wins+self.ties)
        self.dealer_wins = self.dealer_wins/(self.player_wins+self.dealer_wins+self.ties)
        self.ties = self.ties/(self.player_wins+self.dealer_wins+self.ties)

    def calc_percent_wins(self, current_deck, current_dealer, player_points, drawn_cards, carry_fraction, exceeds = False):
        drawn_cards += 1

        for potential_card, card_count in current_deck.items():
            if card_count == 0:
                continue

            if exceeds: # another short circuit here
                self.player_wins += Fraction(card_count, sum(current_deck.values())) * carry_fraction
                continue
            
            future_dealer = current_dealer.copy()
            future_dealer.append(potential_card)
            dealer_points = self.count_points(future_dealer)

            if dealer_points < 17 and drawn_cards < 4:
                future_deck = current_deck.copy()
                future_deck[potential_card] -= 1
                
                self.calc_percent_wins(future_deck, future_dealer.copy(), player_points, drawn_cards, carry_fraction * Fraction(card_count, sum(current_deck.values())))
                continue
            
            elif dealer_points > 21:
                exceeds = True

            if dealer_points == 21 and drawn_cards == 1:
                continue

            elif (dealer_points <= 21) and (drawn_cards == 4 or dealer_points > player_points):
                self.dealer_wins += Fraction(card_count, sum(current_deck.values())) * carry_fraction

            elif dealer_points == player_points:
                self.ties += Fraction(card_count, sum(current_deck.values())) * carry_fraction

            else:
                self.player_wins += Fraction(card_count, sum(current_deck.values())) * carry_fraction




bjmemory = bjmem()
bjcalc = bjstats()
# bjmemory.start()

dbase = sqlite3.connect("blackjack_stats.db")
cursor = dbase.cursor()
cursor.execute("SELECT stand_percent_ties FROM stats")
all_stats = cursor.fetchall()
a = lambda b: b[0]
print(sum(map(float, map(a, all_stats)))/len(all_stats) * 100)

# 15567
# count = 0
# total = len(bjmemory.player_and_dealer)
# for dealer, player in bjmemory.player_and_dealer:
#     count += 1
#     bjcalc.set_dealer(dealer)
#     bjcalc.set_player(player)
#     success, fails = bjcalc.percent_hit()
#     bjcalc.calc_percent_wins(bjcalc.deck.copy(), bjcalc.dealer.copy(), bjcalc.count_points(bjcalc.player), second_card = True, carry_fraction = 1)
#     bjcalc.recal()
#     cursor.execute("INSERT INTO stats (dealer, player, hit_percent, stand_percent_wins, stand_percent_ties) VALUES (?, ?, ?, ?, ?)", [dealer[0], "".join(sorted(player, key = lambda o: 1 if o == 'A' else int(o))), success / (fails+success) * 100, float(bjcalc.player_wins), float(bjcalc.ties)])
#     print(f"{count} of {total}")
#     bjcalc.reset()

# dbase.commit()
dbase.close()

