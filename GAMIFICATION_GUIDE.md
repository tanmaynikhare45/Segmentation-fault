# Gamification System Guide

## Overview

The Civic Eye complaint registration system now includes a comprehensive gamification system that rewards users for genuine complaints and penalizes fake or excessive complaints.

## How It Works

### Points System

#### Earning Points
- **Complaint Resolved**: +10 points (only for genuine complaints)
- **Starting Balance**: 0 points for new users

#### Losing Points
- **Fake Complaint Detected**: -15 points
- **Excessive Unresolved Complaints**: -5 points per complaint over the threshold

### User Levels

Users progress through different levels based on their total points:

| Level | Minimum Points | Badge Color |
|-------|---------------|-------------|
| Novice Citizen | 0 | Gray |
| Active Citizen | 50 | Blue |
| Super Citizen | 100 | Green |
| Elite Citizen | 200 | Purple |
| Guardian Citizen | 500 | Gold |

### Restrictions

#### Registration Blocking
Users are **blocked from registering new complaints** if:

1. **Points fall below -50**: Account is temporarily restricted
2. **More than 2 pending complaints**: Must wait for resolution

#### How to Restore Access
- Wait for pending complaints to be resolved by authorities
- Points will increase when genuine complaints are resolved
- Once points reach -50 or above, registration access is restored

## Badges System

Users can earn badges for achievements:

- **First Step**: Register your first complaint
- **Problem Solver**: First complaint resolved
- **Active Reporter**: 5 complaints resolved
- **Community Hero**: 10 complaints resolved
- **Civic Champion**: 25 complaints resolved
- **Point Master**: Earn 100+ points
- **Legendary Citizen**: Earn 500+ points
- **Trustworthy**: No fake complaints detected (minimum 5 complaints)

## User Statistics Tracked

The system tracks the following metrics:

1. **Total Points**: Current point balance
2. **Total Complaints**: All complaints registered
3. **Resolved Complaints**: Successfully resolved complaints
4. **Pending Complaints**: Complaints awaiting resolution
5. **Fake Complaints**: Complaints flagged as fake
6. **Success Rate**: Percentage of resolved complaints

## Viewing Your Stats

Visit your **Profile Page** to see:
- Current points and level
- Progress bar to next level
- Earned badges
- Detailed statistics
- Recent complaints history
- Account status (active/restricted)

## Fake Detection System

The system automatically detects potentially fake complaints using:

1. **Text Similarity**: Compares with recent complaints
2. **Location Proximity**: Checks for duplicate locations
3. **Temporal Patterns**: Monitors submission frequency
4. **Content Validation**: Analyzes complaint quality

## Tips for Maintaining Good Standing

### ✅ Do's
- Submit genuine, detailed complaints
- Include photos when possible
- Provide accurate location information
- Be patient while complaints are being resolved
- Check your profile regularly to monitor your status

### ❌ Don'ts
- Submit fake or spam complaints
- Register multiple complaints for the same issue
- Use vague or unclear descriptions
- Submit complaints without proper information
- Register new complaints when you have many pending ones

## Authority Actions

When authorities update complaint status:
- **Resolved**: User gains +10 points (if genuine)
- **Rejected**: No points awarded or deducted
- **In Progress**: No immediate point change

## Example Scenarios

### Scenario 1: Good Citizen
1. User registers 5 genuine complaints
2. All 5 get resolved
3. User earns: 5 × 10 = **50 points**
4. Achieves **Active Citizen** level
5. Earns badges: First Step, Problem Solver, Active Reporter

### Scenario 2: Problematic User
1. User registers 3 fake complaints
2. System detects all as fake
3. User loses: 3 × 15 = **-45 points**
4. User has 8 pending unresolved complaints
5. Additional penalty: 3 × 5 = **-15 points** (3 over threshold)
6. Total: **-60 points** → Account blocked

### Scenario 3: Recovery
1. Blocked user has -60 points
2. Authorities resolve 2 genuine complaints
3. User gains: 2 × 10 = **+20 points**
4. New balance: -40 points
5. Account access restored (above -50 threshold)

### Scenario 4: Pending Limit
1. User has 3 pending complaints
2. Tries to register a new complaint
3. System blocks: "You have 3 pending complaints. Maximum allowed: 2"
4. Authority resolves 1 complaint
5. User now has 2 pending → Can register new complaints

## Technical Details

### Database Schema
Each user document includes:
```json
{
  "username": "user123",
  "points": 0,
  "total_complaints": 0,
  "resolved_complaints": 0,
  "fake_complaints": 0,
  "pending_complaints": 0
}
```

### API Integration
The gamification system is automatically integrated with:
- Complaint submission (`/submit_report`)
- Status updates (`/update_status`, `/api/update_status`)
- Profile display (`/profile`)

## Configuration

Administrators can modify thresholds in `ai/gamification.py`:

```python
POINTS_RESOLVED = 10              # Points for resolved complaint
POINTS_FAKE_PENALTY = -15         # Penalty for fake complaint
POINTS_UNRESOLVED_PENALTY = -5    # Penalty per excess pending
MIN_POINTS_TO_REGISTER = -50      # Minimum points to register
MAX_PENDING_COMPLAINTS = 2        # Maximum pending before blocking
```

## Future Enhancements

Potential additions:
- Leaderboards showing top contributors
- Seasonal challenges and events
- Bonus points for high-priority issues
- Community voting on complaint validity
- Referral rewards for bringing new users
- Special badges for specific issue types

## Support

If you believe your account was incorrectly restricted:
1. Check your profile for detailed statistics
2. Review your pending complaints
3. Contact support through the Contact page
4. Wait for pending complaints to be resolved

---

**Remember**: The gamification system is designed to encourage genuine civic participation and maintain the quality of the complaint registration system. Be a responsible citizen! 🏆
