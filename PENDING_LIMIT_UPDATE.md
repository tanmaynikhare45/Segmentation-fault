# Pending Complaints Limit Update

## Change Summary

**Maximum pending complaints reduced from 5 to 2**

### What Changed
- Users can now have a maximum of **2 pending complaints**
- If a user has **3 or more pending complaints**, they will be blocked from registering new ones
- This encourages users to wait for resolution before submitting more complaints

## Updated Rules

### ✅ Allowed Scenarios
- **0 pending complaints**: Can register ✓
- **1 pending complaint**: Can register ✓
- **2 pending complaints**: Can register ✓

### ❌ Blocked Scenarios
- **3 pending complaints**: BLOCKED - "You have 3 pending complaints. Maximum allowed: 2"
- **4+ pending complaints**: BLOCKED - Must wait for resolution

## Example Flow

### User Journey
```
Day 1: Submit complaint #1
  → Pending: 1 ✅ Can register more

Day 2: Submit complaint #2
  → Pending: 2 ✅ Can still register

Day 3: Try to submit complaint #3
  → Pending: 2 ❌ BLOCKED
  → Message: "You have 2 pending complaints. Please wait for 
             some of them to be resolved before registering new ones.
             Maximum allowed pending complaints: 2."

Day 5: Authority resolves complaint #1
  → Pending: 1 ✅ Can register again

Day 6: Submit complaint #3
  → Pending: 2 ✅ Success
```

## Benefits

1. **Prevents Spam**: Users can't flood the system with complaints
2. **Encourages Quality**: Users think carefully before submitting
3. **Fair Distribution**: Authorities can focus on existing complaints
4. **System Balance**: Maintains manageable complaint queue

## Technical Details

### File Modified
- `ai/gamification.py` - Line 31

### Change
```python
# Before
MAX_PENDING_COMPLAINTS = 5

# After
MAX_PENDING_COMPLAINTS = 2
```

### Validation Logic
The system checks pending count in `can_register_complaint()`:
```python
if pending_count >= MAX_PENDING_COMPLAINTS:
    return False, "You have {pending_count} pending complaints..."
```

## Testing

### Test Case 1: At Limit
```
Pending: 2
Action: Try to register
Result: ✅ Allowed (at limit, not over)
```

### Test Case 2: Over Limit
```
Pending: 3
Action: Try to register
Result: ❌ Blocked
Message: "You have 3 pending complaints. Maximum allowed: 2"
```

### Test Case 3: After Resolution
```
Initial: 3 pending (blocked)
Authority resolves 1 complaint
New: 2 pending
Action: Try to register
Result: ✅ Allowed
```

## User Communication

When blocked, users see:
> **"You have X pending complaints. Please wait for some of them to be resolved before registering new ones. Maximum allowed pending complaints: 2."**

## Impact on Existing Users

- Users with 3+ pending complaints will be blocked immediately
- They must wait for authorities to resolve complaints
- No retroactive penalties applied
- Points remain unchanged

## Adjusting the Limit

To change this limit in the future, edit `ai/gamification.py`:
```python
MAX_PENDING_COMPLAINTS = 2  # Change this number
```

Common values:
- `1`: Very strict (only 1 pending allowed)
- `2`: Strict (current setting)
- `3`: Moderate
- `5`: Lenient (previous setting)
- `10`: Very lenient

---

**Updated**: October 11, 2025  
**Status**: ✅ Implemented and Active
