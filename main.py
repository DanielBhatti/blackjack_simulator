import random
from abc import ABC, abstractmethod
from typing import List, Tuple


class Card:
    def __init__(self, rank: str):
        self.rank = rank

    def value(self) -> int:
        if self.rank == "A":
            return 11
        elif self.rank in ["J", "Q", "K"]:
            return 10
        else:
            return int(self.rank)

    def __repr__(self) -> str:
        return self.rank


class Deck:
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, num_decks: int = 1):
        self.cards = []
        self.num_decks = num_decks
        self.reset()

    def reset(self) -> None:
        self.cards = [Card(rank) for _ in range(self.num_decks) for rank in self.RANKS * 4]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        if len(self.cards) < 10:
            self.reset()
        return self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def value(self) -> Tuple[int, bool]:
        total = 0
        aces = 0

        for card in self.cards:
            total += card.value()
            if card.rank == "A":
                aces += 1

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        is_soft = aces > 0
        return total, is_soft

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value()[0] == 21


class Strategy(ABC):
    @abstractmethod
    def get_bet(self, bankroll: float) -> float:
        pass

    @abstractmethod
    def should_hit(self, player_value: int, is_soft: bool, dealer_upcard: int) -> bool:
        pass


class BasicStrategy(Strategy):
    def get_bet(self, bankroll: float) -> float:
        return min(10.0, bankroll)

    def should_hit(self, player_value: int, is_soft: bool, dealer_upcard: int) -> bool:
        if is_soft:
            return player_value < 18
        else:
            return player_value < 17


class Game:
    def __init__(self, deck: Deck):
        self.deck = deck
        self.player_hand = Hand()
        self.dealer_hand = Hand()

    def deal(self) -> None:
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())

    def player_plays(self, strategy: Strategy) -> bool:
        while True:
            player_value, is_soft = self.player_hand.value()
            dealer_upcard = self.dealer_hand.cards[0].value()

            if strategy.should_hit(player_value, is_soft, dealer_upcard):
                self.player_hand.add_card(self.deck.draw())
                if self.player_hand.value()[0] > 21:
                    return False
            else:
                return True

    def dealer_plays(self) -> None:
        while self.dealer_hand.value()[0] < 17:
            self.dealer_hand.add_card(self.deck.draw())

    def get_result(self, bet: float) -> float:
        player_value = self.player_hand.value()[0]
        dealer_value = self.dealer_hand.value()[0]

        if player_value > 21:
            return -bet

        if self.player_hand.is_blackjack() and not self.dealer_hand.is_blackjack():
            return bet * 1.5

        if self.dealer_hand.is_blackjack() and not self.player_hand.is_blackjack():
            return -bet

        if self.player_hand.is_blackjack() and self.dealer_hand.is_blackjack():
            return 0.0

        if dealer_value > 21:
            return bet

        if player_value > dealer_value:
            return bet
        elif player_value < dealer_value:
            return -bet
        else:
            return 0.0


def play_hand(deck: Deck, strategy: Strategy, bankroll: float) -> Tuple[float, float]:
    bet = strategy.get_bet(bankroll)
    if bet <= 0 or bet > bankroll:
        raise ValueError(f"Invalid bet: {bet}")

    game = Game(deck)
    game.deal()

    player_still_active = game.player_plays(strategy)

    if player_still_active:
        game.dealer_plays()

    payoff = game.get_result(bet)
    new_bankroll = bankroll - bet + payoff

    return new_bankroll, payoff


def simulate(strategy: Strategy, num_hands: int, num_decks: int = 1, starting_bankroll: float = 10000.0) -> dict:
    deck = Deck(num_decks)
    bankroll = starting_bankroll

    wins = 0
    losses = 0
    pushes = 0

    for _ in range(num_hands):
        if bankroll <= 0:
            break
        bankroll, payoff = play_hand(deck, strategy, bankroll)

        if payoff > 0:
            wins += 1
        elif payoff < 0:
            losses += 1
        else:
            pushes += 1

    return {
        "final_bankroll": bankroll,
        "profit": bankroll - starting_bankroll,
        "roi": (bankroll - starting_bankroll) / starting_bankroll * 100,
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "win_rate": wins / num_hands * 100,
    }


if __name__ == "__main__":
    strategy = BasicStrategy()
    results = simulate(strategy, num_hands=10000, num_decks=1)

    print("=" * 50)
    print("Blackjack Simulation Results")
    print("=" * 50)
    print(f"Hands played: 10000")
    print(f"Wins: {results['wins']}")
    print(f"Losses: {results['losses']}")
    print(f"Pushes: {results['pushes']}")
    print(f"Win rate: {results['win_rate']:.2f}%")
    print(f"Final bankroll: ${results['final_bankroll']:.2f}")
    print(f"Profit/Loss: ${results['profit']:.2f}")
    print(f"ROI: {results['roi']:.2f}%")
