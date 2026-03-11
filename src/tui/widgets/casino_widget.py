"""Casino widget with gambling games."""

from __future__ import annotations

import random
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Input, Label, Static

from src.core.models.user import User
from src.core.repositories.activity_repository import ActivityRepository
from src.core.repositories.user_repository import UserRepository
from src.core.services.economy_service import EconomyService


class CasinoWidget(Static):
    """Casino section with various gambling games."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.user_repo = UserRepository()
        self.activity_repo = ActivityRepository()
        self.economy = EconomyService()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🎰 Casino", classes="section-title")
            yield Static(f"Your balance: {self.user.balance} 🪙")

            with Grid(id="casino-grid"):
                # Slots
                with Vertical(classes="casino-game"):
                    yield Label("🎰 Slot Machine", classes="title")
                    yield Static("Match 3 symbols to win!")
                    yield Static("Bet: 10-1000 coins")
                    with Horizontal():
                        yield Input(placeholder="Bet", value="50", id="slots-bet", classes="bet-input")
                        yield Button("Spin!", id="btn-slots")
                    yield Static("[ ] [ ] [ ]", id="slots-display")
                    yield Static("", id="slots-result")

                # Coin Flip
                with Vertical(classes="casino-game"):
                    yield Label("🪙 Coin Flip", classes="title")
                    yield Static("50/50 chance - double or nothing")
                    with Horizontal():
                        yield Input(placeholder="Bet", value="100", id="coin-bet", classes="bet-input")
                        yield Button("Heads", id="btn-heads")
                        yield Button("Tails", id="btn-tails")
                    yield Static("", id="coin-result")

                # Dice Roll
                with Vertical(classes="casino-game"):
                    yield Label("🎲 Dice Roll", classes="title")
                    yield Static("Roll > 7 to win 1.5x")
                    with Horizontal():
                        yield Input(placeholder="Bet", value="100", id="dice-bet", classes="bet-input")
                        yield Button("Roll!", id="btn-dice")
                    yield Static("", id="dice-result")

                # Roulette
                with Vertical(classes="casino-game"):
                    yield Label("🔴 Roulette", classes="title")
                    yield Static("Pick Red, Black, or Number")
                    with Horizontal():
                        yield Input(placeholder="Bet", value="100", id="roulette-bet", classes="bet-input")
                        yield Button("Red", id="btn-red")
                        yield Button("Black", id="btn-black")
                    yield Static("", id="roulette-result")

            yield Static("", id="casino-message", classes="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle casino game buttons."""
        btn_id = event.button.id

        if btn_id == "btn-slots":
            self._play_slots()
        elif btn_id == "btn-heads":
            self._play_coinflip("heads")
        elif btn_id == "btn-tails":
            self._play_coinflip("tails")
        elif btn_id == "btn-dice":
            self._play_dice()
        elif btn_id == "btn-red":
            self._play_roulette("red")
        elif btn_id == "btn-black":
            self._play_roulette("black")

    def _get_bet(self, input_id: str) -> int:
        """Get bet amount from input."""
        try:
            bet = int(self.query_one(f"#{input_id}", Input).value)
            return max(10, min(bet, self.user.balance, 10000))
        except ValueError:
            return 50

    def _play_slots(self):
        """Play slot machine."""
        bet = self._get_bet("slots-bet")
        display = self.query_one("#slots-display", Static)
        result = self.query_one("#slots-result", Static)

        if bet > self.user.balance:
            result.update("❌ Insufficient funds")
            return

        symbols = ["🍒", "🍋", "🍇", "💎", "7️⃣", "🎰"]
        weights = [30, 25, 20, 15, 8, 2]

        self.user.deduct(bet)

        # Spin animation
        import time
        for _ in range(3):
            spin = [random.choice(symbols) for _ in range(3)]
            display.update(f"[{spin[0]}] [{spin[1]}] [{spin[2]}]")

        # Final result
        final = [random.choices(symbols, weights=weights)[0] for _ in range(3)]
        display.update(f"[{final[0]}] [{final[1]}] [{final[2]}]")

        # Calculate winnings
        winnings = 0
        if final[0] == final[1] == final[2]:
            multiplier = {"🍒": 3, "🍋": 4, "🍇": 5, "💎": 10, "7️⃣": 25, "🎰": 50}
            winnings = bet * multiplier.get(final[0], 2)
            result.update(f"🎉 JACKPOT! {final[0]} x3! Won {winnings} 🪙")
        elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
            winnings = bet * 2
            result.update(f"✅ Match! Won {winnings} 🪙")
        else:
            result.update(f"❌ No match. Lost {bet} 🪙")

        if winnings > 0:
            self.user.add_coins(winnings)

        self.user_repo.update(self.user)
        self.activity_repo.log(self.user.id, "casino_slots", {"bet": bet, "winnings": winnings})
        self._refresh_stats()

    def _play_coinflip(self, choice: str):
        """Play coin flip."""
        bet = self._get_bet("coin-bet")
        result = self.query_one("#coin-result", Static)

        if bet > self.user.balance:
            result.update("❌ Insufficient funds")
            return

        self.user.deduct(bet)
        flip = random.choice(["heads", "tails"])

        if flip == choice:
            winnings = bet * 2
            self.user.add_coins(winnings)
            result.update(f"🪙 {flip.capitalize()}! You won {winnings} 🪙")
        else:
            result.update(f"🪙 {flip.capitalize()}! You lost {bet} 🪙")

        self.user_repo.update(self.user)
        self.activity_repo.log(self.user.id, "casino_coinflip", {"bet": bet, "choice": choice, "result": flip})
        self._refresh_stats()

    def _play_dice(self):
        """Play dice roll."""
        bet = self._get_bet("dice-bet")
        result = self.query_one("#dice-result", Static)

        if bet > self.user.balance:
            result.update("❌ Insufficient funds")
            return

        self.user.deduct(bet)
        roll1, roll2 = random.randint(1, 6), random.randint(1, 6)
        total = roll1 + roll2

        if total > 7:
            winnings = int(bet * 1.5)
            self.user.add_coins(winnings)
            result.update(f"🎲 {roll1}+{roll2}={total}! You won {winnings} 🪙")
        else:
            result.update(f"🎲 {roll1}+{roll2}={total}! You lost {bet} 🪙")

        self.user_repo.update(self.user)
        self.activity_repo.log(self.user.id, "casino_dice", {"bet": bet, "roll": total})
        self._refresh_stats()

    def _play_roulette(self, choice: str):
        """Play roulette."""
        bet = self._get_bet("roulette-bet")
        result = self.query_one("#roulette-result", Static)

        if bet > self.user.balance:
            result.update("❌ Insufficient funds")
            return

        self.user.deduct(bet)
        number = random.randint(0, 36)
        is_red = number % 2 == 1  # Odd numbers are red
        color = "red" if is_red else "black"

        if choice == color:
            winnings = bet * 2
            self.user.add_coins(winnings)
            result.update(f"🔴 {number} ({color})! You won {winnings} 🪙")
        else:
            result.update(f"⚫ {number} ({color})! You lost {bet} 🪙")

        self.user_repo.update(self.user)
        self.activity_repo.log(self.user.id, "casino_roulette", {"bet": bet, "choice": choice, "result": number})
        self._refresh_stats()

    def _refresh_stats(self):
        """Refresh parent screen stats."""
        try:
            parent = self.parent
            if parent and hasattr(parent, "refresh_user_stats"):
                parent.refresh_user_stats()
        except:
            pass
