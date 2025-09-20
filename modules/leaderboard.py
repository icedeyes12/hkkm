# modules/leaderboard.py
from utils.db import get_leaderboard
from utils.helpers import format_currency

def display_leaderboard(profile):
    """Display the leaderboard menu"""
    leaderboard = get_leaderboard()
    
    print("\n" + "="*60)
    print("🏆 LEADERBOARD")
    print("="*60)
    
    while True:
        print(f"\n👤 {profile['nickname']} | 🪙 {format_currency(profile['balance'])} | ⭐ {profile['xp']} XP")
        print("\n1) Top XP Leaders")
        print("2) Top Wealth Leaders")
        print("3) My Rankings")
        print("9) Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            display_xp_leaderboard(leaderboard, profile)
        elif choice == "2":
            display_wealth_leaderboard(leaderboard, profile)
        elif choice == "3":
            display_my_rankings(leaderboard, profile)
        elif choice == "9":
            return
        else:
            print("❌ Invalid option. Please try again.")

def display_xp_leaderboard(leaderboard, profile):
    """Display XP leaderboard"""
    print("\n" + "="*40)
    print("⭐ TOP XP LEADERS")
    print("="*40)
    
    if not leaderboard.get("top_xp"):
        print("\nNo XP rankings yet! Be the first to earn XP!")
        return
    
    print(f"\n{'Rank':<6} {'Username':<15} {'XP':<10}")
    print("-" * 35)
    
    for entry in leaderboard["top_xp"]:
        highlight = " → " if entry["user_id"] == profile["id"] else "   "
        print(f"{highlight}{entry['rank']:<3} {entry['username']:<15} {entry['xp']:<10}")
    
    # Show user's position if not in top 10
    user_rank = get_user_rank(leaderboard["top_xp"], profile["id"])
    if user_rank > 10:
        user_xp = next((entry["xp"] for entry in leaderboard["top_xp"] if entry["user_id"] == profile["id"]), profile["xp"])
        print(f"\n... Your rank: #{user_rank} with {user_xp} XP")

def display_wealth_leaderboard(leaderboard, profile):
    """Display wealth leaderboard"""
    print("\n" + "="*40)
    print("💰 TOP WEALTH LEADERS")
    print("="*40)
    
    if not leaderboard.get("top_wealth"):
        print("\nNo wealth rankings yet! Be the first to earn money!")
        return
    
    print(f"\n{'Rank':<6} {'Username':<15} {'Wealth':<10}")
    print("-" * 35)
    
    for entry in leaderboard["top_wealth"]:
        highlight = " → " if entry["user_id"] == profile["id"] else "   "
        wealth = format_currency(entry["balance"])
        print(f"{highlight}{entry['rank']:<3} {entry['username']:<15} {wealth:<10}")
    
    # Show user's position if not in top 10
    user_rank = get_user_rank(leaderboard["top_wealth"], profile["id"])
    if user_rank > 10:
        user_balance = next((entry["balance"] for entry in leaderboard["top_wealth"] if entry["user_id"] == profile["id"]), profile["balance"])
        print(f"\n... Your rank: #{user_rank} with {format_currency(user_balance)}")

def display_my_rankings(profile):
    """Display current user's rankings"""
    leaderboard = get_leaderboard()
    
    print("\n" + "="*40)
    print("👤 MY RANKINGS")
    print("="*40)
    
    # XP Ranking
    xp_rank = get_user_rank(leaderboard.get("top_xp", []), profile["id"])
    total_xp_players = len(leaderboard.get("top_xp", []))
    
    print(f"\n⭐ XP Rank: #{xp_rank} of {total_xp_players} players")
    print(f"   Your XP: {profile['xp']}")
    
    # Wealth Ranking
    wealth_rank = get_user_rank(leaderboard.get("top_wealth", []), profile["id"])
    total_wealth_players = len(leaderboard.get("top_wealth", []))
    
    print(f"\n💰 Wealth Rank: #{wealth_rank} of {total_wealth_players} players")
    print(f"   Your balance: {format_currency(profile['balance'])}")
    
    # Level info
    print(f"\n🔼 Level: {profile['level']}")
    
    if xp_rank <= 10 or wealth_rank <= 10:
        print("\n🎉 You're in the top 10! Keep it up!")
    else:
        print(f"\n📈 Keep playing to reach the top 10!")

def get_user_rank(entries, user_id):
    """Get user's rank in a leaderboard category"""
    for entry in entries:
        if entry["user_id"] == user_id:
            return entry["rank"]
    # If not in the list, rank is length + 1
    return len(entries) + 1

def update_user_leaderboard(profile):
    """Update leaderboard with user's current stats"""
    from utils.db import update_leaderboard_entry
    update_leaderboard_entry(profile["id"], profile["username"], profile["xp"], profile["balance"])