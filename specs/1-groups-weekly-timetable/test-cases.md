# Test Cases: Weekly Group Timetables

## Unit Tests

### UT-1: Get All Groups (Admin)
- **Given**: Admin user
- **When**: Call `get_weekly_timetable(admin, date=2026-02-16)`
- **Then**: Return 5 groups with all fields (including emails)
- **Expected**: len(groups) >= 1, coach.email present

### UT-2: Get Coach Groups (Coach)
- **Given**: Coach with 2 groups assigned
- **When**: Call `get_weekly_timetable(coach, date=2026-02-16)`
- **Then**: Return only 2 groups, without family emails
- **Expected**: len(groups) == 2, no family emails visible

### UT-3: Get Family Groups (Family)
- **Given**: Family with 2 kids in 1 group
- **When**: Call `get_weekly_timetable(family, date=2026-02-16)`
- **Then**: Return 1 group, with only their 2 kids listed
- **Expected**: len(groups) == 1, len(kids) == 2, no other kids

### UT-4: Validate Date Format
- **Given**: Invalid date format
- **When**: Call API with `?date=invalid`
- **Then**: Return HTTP 400 error
- **Expected**: status_code == 400

### UT-5: Empty Timetable
- **Given**: Family with no groups
- **When**: Call `get_weekly_timetable(family, date=2026-02-16)`
- **Then**: Return empty groups list
- **Expected**: len(groups) == 0

## Integration Tests

### IT-1: API Endpoint Admin Access
- **Given**: Admin token
- **When**: GET /api/timetables/weekly?date=2026-02-16
- **Then**: Status 200, full data returned
- **Expected**: status 200, groups.length > 0

### IT-2: API Endpoint Coach Access
- **Given**: Coach token
- **When**: GET /api/timetables/weekly?date=2026-02-16
- **Then**: Status 200, only assigned groups returned
- **Expected**: status 200, no other coaches' groups

### IT-3: API Endpoint Unauthorized
- **Given**: No token
- **When**: GET /api/timetables/weekly
- **Then**: Status 401, redirect to login
- **Expected**: status 401 or redirect

### IT-4: Database Integrity
- **Given**: Valid group data
- **When**: INSERT into groups
- **Then**: All foreign keys maintained
- **Expected**: No FK violations

## E2E Tests (Playwright)

### E2E-1: Admin Views Schedule
1. Login as admin
2. Click "Schedules"
3. Verify all groups visible
4. Verify coach emails visible
5. Click "← Previous Week"
6. Verify URL changed to previous week

### E2E-2: Coach Views Only Own Groups
1. Login as coach
2. Click "My Groups"
3. Verify only 2 groups shown
4. Verify no family emails visible
5. Verify can see kid names

### E2E-3: Family Views Group
1. Login as family
2. Click "My Schedule"
3. Verify only their group shown
4. Verify only their kids listed
5. Verify no other kids visible

### E2E-4: Week Navigation
1. Visit schedule page
2. Click "Next Week" button
3. Verify date changes correctly
4. Click "← Previous Week" button
5. Verify returns to original date

---

## Manual Testing Checklist

- [ ] Test on Chrome, Firefox, Safari
- [ ] Test on iPhone SE (375px), iPad (768px), Desktop (1920px)
- [ ] Test week navigation (previous/next)
- [ ] Test with 0 groups assigned
- [ ] Test with 10+ kids in group
- [ ] Test with overlapping schedules
- [ ] Test logout/login flow
- [ ] Test concurrent user access
- [ ] Verify no emails leaked to coaches/families
- [ ] Verify SQL injection prevention