# Updated Gamification Rules - Stricter System

## 🚨 IMPORTANT CHANGES

The gamification system has been updated with **stricter penalties** to maintain complaint quality.

---

## New Point System

### Points Awarded
- ✅ **Genuine complaint resolved**: **+10 points**

### Points Deducted
- ❌ **Fake complaint detected**: **-5 points** (reduced from -15)

---

## New Thresholds

### 1️⃣ Temporary Block: **-20 Points**
- **Previous**: -50 points
- **New**: **-20 points**
- **Effect**: Cannot register new complaints until resolved
- **Recovery**: Get complaints resolved to earn points back

### 2️⃣ Permanent Ban: **-40 Points** 🔴
- **NEW FEATURE**: Account permanently banned
- **Effect**: 
  - Cannot login anymore
  - Cannot register new complaints
  - Account is locked forever
  - Cannot create new account with same credentials
- **No Recovery**: This is permanent!

---

## How It Works

### Point Progression

```
Starting Points: 0

Submit fake complaint #1: -5 points
Total: -5 (✅ Can still register)

Submit fake complaint #2: -5 points
Total: -10 (✅ Can still register)

Submit fake complaint #3: -5 points
Total: -15 (✅ Can still register)

Submit fake complaint #4: -5 points
Total: -20 (⚠️ TEMPORARILY BLOCKED)
Message: "Account temporarily blocked. Need -20 or higher to register."

Submit fake complaint #5: -5 points
Total: -25 (⚠️ Still blocked)

Submit fake complaint #6: -5 points
Total: -30 (⚠️ Still blocked)

Submit fake complaint #7: -5 points
Total: -35 (⚠️ Still blocked)

Submit fake complaint #8: -5 points
Total: -40 (🔴 PERMANENTLY BANNED!)
Message: "Account permanently banned. Cannot login anymore."
```

---

## Detailed Scenarios

### Scenario 1: Good User
```
Day 1: Register 5 genuine complaints
  Points: 0
  Pending: 5

Day 7: All 5 resolved by authority
  Points: 0 + (5 × 10) = 50 points ✅
  Level: Active Citizen 🌟
```

### Scenario 2: User Gets Temporarily Blocked
```
Day 1: Submit 4 fake complaints
  4 × (-5) = -20 points
  Status: ⚠️ TEMPORARILY BLOCKED

Day 3: Cannot login? NO - Can still login
Day 3: Can register complaints? NO - Blocked

Day 5: Authority resolves 2 genuine complaints
  -20 + (2 × 10) = 0 points
  Status: ✅ UNBLOCKED - Can register again
```

### Scenario 3: User Gets Permanently Banned
```
Day 1: Submit 8 fake complaints
  8 × (-5) = -40 points
  Status: 🔴 PERMANENTLY BANNED

Day 2: Try to login
  Result: ❌ "Account permanently banned"
  Redirected to login page

Day 3: Try to register new complaint
  Result: ❌ Cannot even login

Day 4: Contact support
  Result: Account cannot be recovered
```

### Scenario 4: Close Call
```
Starting: -35 points (7 fake complaints)
Status: ⚠️ Temporarily blocked but can login

Submit 1 more fake: -35 + (-5) = -40
Status: 🔴 PERMANENTLY BANNED
Next login attempt: ❌ Blocked

Recovery: NONE - Account is gone forever
```

---

## Comparison: Old vs New

| Feature | Old System | New System |
|---------|-----------|------------|
| Fake penalty | -15 points | **-5 points** |
| Temporary block | -50 points | **-20 points** |
| Permanent ban | None | **-40 points** 🔴 |
| Fake complaints to block | ~3-4 | **4 fake complaints** |
| Fake complaints to ban | Never | **8 fake complaints** |
| Can recover from ban? | Yes | **NO** |

---

## Math Breakdown

### How Many Fake Complaints?

**To Get Temporarily Blocked (-20 points):**
```
-20 ÷ -5 = 4 fake complaints
```

**To Get Permanently Banned (-40 points):**
```
-40 ÷ -5 = 8 fake complaints
```

**To Recover from -20 (blocked):**
```
Need +20 points = 2 resolved genuine complaints
```

**To Recover from -35 (near ban):**
```
Need +35 points = 3.5 → 4 resolved genuine complaints
```

---

## Visual Scale

```
Points:  -40  -35  -30  -25  -20  -15  -10  -5   0   +10  +20
         |    |    |    |    |    |    |    |    |    |    |
Status:  🔴  ⚠️   ⚠️   ⚠️   ⚠️   ✅   ✅   ✅   ✅   ✅   ✅
         BAN  BLOCKED  BLOCKED  BLOCKED  OK   OK   OK   OK   OK
              
         ↑                      ↑
    Permanent Ban          Temp Block
    (-40 points)          (-20 points)
```

---

## Login Behavior

### Points: 0 to +∞
- ✅ Can login
- ✅ Can register complaints
- ✅ Full access

### Points: -19 to -1
- ✅ Can login
- ✅ Can register complaints
- ⚠️ Warning: Be careful!

### Points: -20 to -39
- ✅ **Can still login**
- ❌ **Cannot register complaints**
- ⚠️ Temporarily blocked
- 💡 Get complaints resolved to recover

### Points: -40 or below
- ❌ **Cannot login**
- ❌ **Cannot register**
- 🔴 **Permanently banned**
- ⛔ **No recovery possible**

---

## Important Notes

### ⚠️ Warning Signs
- **-5 points**: First fake detected - Be careful!
- **-10 points**: Second fake - Warning!
- **-15 points**: Third fake - Danger zone!
- **-20 points**: BLOCKED from registering
- **-35 points**: One more fake = permanent ban!
- **-40 points**: BANNED forever!

### 🛡️ Protection Tips
1. Only submit genuine complaints
2. Include photos and accurate location
3. Provide detailed descriptions
4. Monitor your points on profile page
5. If blocked, wait for resolutions

### 🚫 What Happens at Ban
1. Immediate logout if currently logged in
2. Cannot login with that username anymore
3. All future login attempts blocked
4. Account permanently disabled
5. Must contact support (no guarantee of recovery)

---

## Recovery Examples

### Example 1: Recover from -20
```
Current: -20 points (blocked)
Need: Get to -19 or higher

Solution: Get 1 genuine complaint resolved
-20 + 10 = -10 points ✅ UNBLOCKED
```

### Example 2: Recover from -35 (Critical!)
```
Current: -35 points (5 points from ban!)
Need: Get to -19 or higher

Solution: Get 2 genuine complaints resolved
-35 + 20 = -15 points ✅ UNBLOCKED

⚠️ WARNING: Do NOT submit any more fake complaints!
One more fake = -35 + (-5) = -40 = PERMANENT BAN
```

### Example 3: Cannot Recover from -40
```
Current: -40 points
Status: PERMANENTLY BANNED 🔴

No amount of resolved complaints will help
Account is locked forever
Must create new account (if allowed)
```

---

## FAQ

**Q: Can I recover from a permanent ban?**
A: No. Once you hit -40 points, the account is permanently banned.

**Q: Can I create a new account if banned?**
A: The system prevents the same credentials, but you may contact support.

**Q: How do I avoid getting banned?**
A: Only submit genuine, legitimate complaints with proper details.

**Q: What if the AI wrongly flags my complaint as fake?**
A: Contact support immediately. Admins can review and adjust points.

**Q: Can I see my points before getting banned?**
A: Yes! Check your profile page regularly to monitor your points.

**Q: How many fake complaints until ban?**
A: 8 fake complaints = -40 points = Permanent ban

**Q: How many fake complaints until temporary block?**
A: 4 fake complaints = -20 points = Temporary block

---

## Configuration

These values are set in `ai/gamification.py`:

```python
POINTS_RESOLVED = 10              # Points for resolved complaint
POINTS_FAKE_PENALTY = -5          # Penalty for fake complaint
MIN_POINTS_TO_REGISTER = -20      # Temporary block threshold
PERMANENT_BAN_THRESHOLD = -40     # Permanent ban threshold
MAX_PENDING_COMPLAINTS = 2        # Maximum pending complaints
```

---

**⚠️ BE RESPONSIBLE! The system is now much stricter. Submit only genuine complaints!**
