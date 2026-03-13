# 🔍 AUDIT REPORT & REBUILD PLAN

## Current State (As of 2024-03-13)

### ✅ What's Working
| Component | Status | Notes |
|-----------|--------|-------|
| Dependencies | ✅ | textual 8.1.1, pydantic 2.12.5, rich 14.3.3, click 8.3.1, bcrypt 5.0.0 |
| Python imports | ✅ | All 49 src files import without errors |
| App instantiation | ✅ | HikikimoApp() creates successfully |
| Database schema | ✅ | SQLite tables initialize correctly |
| User model | ✅ | create_single_player() works |
| Repository layer | ✅ | UserRepository.save_single_player() works |

### ❌ What's Broken
| Component | Status | Issue |
|-----------|--------|-------|
| **Visual rendering** | ❌ | Black screen - text invisible (black-on-black) |
| StartScreen CSS | ⚠️ | `$surface` background too dark in dark mode |
| Text contrast | ⚠️ | `$text` variable may not contrast with `$surface` |
| Widget styling | ⚠️ | Old screen references (WelcomeScreen, etc.) still in CSS |

### 🔍 Root Cause Analysis

**The Black Screen Problem:**
```
[40m = ANSI black background (set by Textual dark mode)
$text in dark mode = light gray/white
$surface in dark mode = very dark gray (near black)
```

When `Screen { background: $surface; }` is set, but the container has no explicit
border/background, text renders but is invisible against the dark surface.

**Missing Pieces:**
- No explicit light theme or high-contrast mode
- Static widgets don't have explicit background/text colors
- Button variants not styled for visibility

---

## 🗺️ REBUILD PLAN

### Phase 1: Fix Visual Rendering (CRITICAL - BLOCKING)
**Goal: Make the UI actually visible**

#### Task 1.1: Diagnose Color Variables
- [ ] Create `test_colors.py` to display all Textual color variables
- [ ] Identify which `$` variables work in dark mode
- [ ] Document contrast ratios

#### Task 1.2: Fix StartScreen CSS
- [ ] Add explicit `background: $surface-darken-1` to container
- [ ] Add `border: solid $primary` for visual boundary
- [ ] Add `color: $text` to all Static and Label widgets
- [ ] Test: Screen should show white/light text on dark gray

#### Task 1.3: Fix Button Visibility
- [ ] Ensure Button with `variant="primary"` has visible text
- [ ] Ensure Button with `variant="error"` has visible text
- [ ] Add `background-tint` for hover states

#### Task 1.4: Verification Test
- [ ] Run app, verify StartScreen shows: Banner + Buttons (visible)
- [ ] Screenshot/verify visually
- [ ] Mark Phase 1 complete before proceeding

---

### Phase 2: Core Game Loop (CRITICAL)
**Goal: Player can start game, do actions, save progress**

#### Task 2.1: StartScreen → MainMenu Flow
- [ ] Click "Start Game" loads MainMenuScreen
- [ ] Verify user stats sidebar displays (XP, Level, Balance)
- [ ] Test "New Game (reset)" clears and restarts

#### Task 2.2: Job Center Widget
- [ ] "Work" button triggers economy_service.work()
- [ ] Progress bar animates
- [ ] Balance increases after work
- [ ] XP increases, level-up check

#### Task 2.3: Save/Load System
- [ ] Auto-save on every significant action
- [ ] Quit → Reopen → Progress restored
- [ ] Manual "New Game" resets everything

#### Task 2.4: Verification Test
- [ ] Complete work cycle 3 times
- [ ] Verify balance increases each time
- [ ] Quit, reopen, verify progress loaded

---

### Phase 3: Feature Completion (HIGH PRIORITY)
**Goal: All game features functional**

#### Task 3.1: Casino Widget
- [ ] Slots mini-game functional (random outcome)
- [ ] Balance updates correctly
- [ ] Visual feedback (win/lose)

#### Task 3.2: Yard Widget (Farming)
- [ ] Display 6 farm plots
- [ ] Plant seeds (deduct cost)
- [ ] Plots show growth progress
- [ ] Harvest when ready (add crops to inventory)

#### Task 3.3: Fishing Widget
- [ ] Display 4 fishing locations
- [ ] Select location → catch fish
- [ ] Inventory adds caught fish
- [ ] Sell fish for coins

#### Task 3.4: Shop Widget
- [ ] Display items (tools, bait, seeds, feed)
- [ ] Buy items (deduct balance)
- [ ] Items added to inventory
- [ ] Inventory displayed in sidebar

---

### Phase 4: Polish (MEDIUM PRIORITY)
**Goal: Professional look and feel**

#### Task 4.1: CSS Refinement
- [ ] Consistent spacing across all screens
- [ ] Color-coded sections (green for farming, blue for fishing, etc.)
- [ ] Hover effects on interactive elements

#### Task 4.2: Animation
- [ ] Smooth progress bar for "Work"
- [ ] Slot machine animation in casino
- [ ] Fish catching animation

#### Task 4.3: Help System
- [ ] F1 key shows help screen
- [ ] Contextual help per widget

---

### Phase 5: Testing & Release (LOW PRIORITY)
**Goal: Stable release**

#### Task 5.1: Test Suite
- [ ] Unit tests for economy calculations
- [ ] Integration tests for save/load
- [ ] Manual test checklist for all features

#### Task 5.2: Documentation
- [ ] Update README with accurate instructions
- [ ] Keyboard shortcuts reference
- [ ] Troubleshooting guide

#### Task 5.3: Packaging
- [ ] `pip install -e .` works cleanly
- [ ] `hkkm` command runs app
- [ ] Tag release v2.0.0

---

## 🎯 SUCCESS CRITERIA

| Phase | Success Metric |
|-------|---------------|
| 1 | User can see and interact with StartScreen |
| 2 | User can complete work → earn → save → load cycle |
| 3 | All 5 game sections (Job, Casino, Yard, Fishing, Shop) functional |
| 4 | UI feels polished and responsive |
| 5 | Can install via pip and run `hkkm` command |

---

## 🚫 STOP CONDITIONS

**Do NOT proceed to next phase until:**
- Current phase ALL tasks marked complete
- Visual verification (not just "no errors")
- User confirms working in their environment

---

## 📋 EXECUTION CHECKLIST

- [ ] Phase 1.1: Color diagnosis test created
- [ ] Phase 1.2: StartScreen CSS fixed
- [ ] Phase 1.3: Buttons visible
- [ ] Phase 1.4: Visual verification passed
- [ ] **GATE**: User confirms StartScreen visible
- [ ] Phase 2.1: Start → MainMenu flow works
- [ ] Phase 2.2: Work economy loop works
- [ ] Phase 2.3: Save/load verified
- [ ] Phase 2.4: Integration test passed
- [ ] **GATE**: User confirms core loop works
- [ ] ... (proceed to Phase 3 only after Phase 2 gate)

---

**Current Status: Phase 1 - Blocked on visual rendering**

Next Action: Create `test_colors.py` to diagnose Textual color variables.
