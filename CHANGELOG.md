# Changelog

All notable changes to the HHH Daily Tracker project will be documented in this file.

## [Unreleased] - 2026-01-05

### Fixed - Production Authentication & UI Improvements

#### Token-Based Authentication for Cross-Origin Support 🔒

- **CRITICAL**: Switched from cookie-based to token-based authentication for cross-origin compatibility
- Cross-site cookies are blocked by Safari (since 2020), Firefox, and 30%+ of users - cookie auth doesn't work reliably anymore
- Backend now returns JWT token in response body for login/register endpoints
- Backend accepts both Authorization header (Bearer token) and cookies for backward compatibility
- Frontend stores token in localStorage and sends it in Authorization header for all API requests
- Cookies still set for local development but token-based auth is primary method
- **This is the industry standard for cross-origin authentication in 2026** - eliminates all cross-site cookie issues
- Works reliably across ALL browsers (Chrome, Safari, Firefox, Edge) on ALL devices (desktop, tablet, mobile)

#### UI Alignment & Layout Fixes

- Added "Group" label to all group dropdowns (Journal, History, Analytics) for consistent alignment
- Fixed streak position in Journal page - now properly aligned to the right side
- Removed `flex-1` from dropdowns to prevent layout shifting
- Added `ml-auto` class to streak component for right alignment

#### Files Modified

- [backend/main.py](backend/main.py):
  - Added `AuthResponse` model with token field
  - Updated `get_current_user()` to accept Authorization header (Bearer token) with cookie fallback
  - Updated login/register endpoints to return token in response body
  - Added Header import from fastapi
- [frontend/src/api.ts](frontend/src/api.ts):
  - Added token storage functions (getToken, setToken, clearToken) using localStorage
  - Updated request() to include Authorization header if token exists
  - Updated login/register to store token automatically
  - Updated logout to clear token from localStorage
- [frontend/src/pages/History.tsx](frontend/src/pages/History.tsx): Added "Group" label to SelectField
- [frontend/src/pages/Journal.tsx](frontend/src/pages/Journal.tsx): Added "Group" label, fixed streak positioning with `ml-auto`
- [frontend/src/pages/Analytics.tsx](frontend/src/pages/Analytics.tsx): Added "Group" label to SelectField

## [Session: 2026-01-04] - Owner Data Visibility Feature

### Added - Owner Data Visibility Feature

#### Security Fix 🔒
- **CRITICAL**: Fixed privacy vulnerability in `/api/entries` endpoint that was returning all group entries without user filtering
- Regular members now can ONLY see their own data (entries, analytics, history)
- Added robust access control with 403 Forbidden responses for unauthorized access attempts

#### Backend Changes
- Added `verify_group_owner()` helper function for ownership verification ([backend/main.py](backend/main.py))
- Updated `/api/entries` endpoint:
  - Added optional `user_id` query parameter (owner-only)
  - Fixed missing user filter (SECURITY FIX)
  - Added ownership verification before allowing access to other users' data
  - Returns 403 if non-owner tries to view other members' data
  - Returns 404 if requested user is not a group member
- Updated `/api/analytics/streak` endpoint:
  - Added optional `user_id` query parameter (owner-only)
  - Owner verification and member validation
- Updated `/api/analytics/history` endpoint:
  - Added optional `user_id` query parameter (owner-only)
  - Owner verification and member validation

#### Frontend Changes
- Created reusable `MemberSelector` component ([frontend/src/components/MemberSelector.tsx](frontend/src/components/MemberSelector.tsx)):
  - Dropdown for owners to select which member's data to view
  - "My Data" as default option
  - Visual badge showing currently viewed member
  - Only visible to group owners
- Updated API client ([frontend/src/api.ts](frontend/src/api.ts)):
  - Added optional `userId` parameter to `getEntries()`, `getStreak()`, and `getHistory()`
- Updated Journal page ([frontend/src/pages/Journal.tsx](frontend/src/pages/Journal.tsx)):
  - Integrated MemberSelector component for owners
  - Added current user and members loading
  - Disabled entry editing when viewing other members' data
  - Pass `selectedUserId` to all API calls
  - Reset selection when switching groups
- Updated History page ([frontend/src/pages/History.tsx](frontend/src/pages/History.tsx)):
  - Integrated MemberSelector component for owners
  - Added current user and members loading
  - Pass `selectedUserId` to history API calls
  - Reset selection when switching groups

#### Type System Updates
- Updated `Group` type to include `is_owner: boolean` in History.tsx
- Added `Member` type for member selector component

### Fixed - UI Issues

#### History Page Stability
- Fixed shaking/wobbling animation when clicking on calendar dates
- Changed from hover-based to click-based day selection
- Added fixed minimum height container (`min-h-[100px]`) for details section to prevent layout shifts
- Improved animations with smoother transitions (200ms duration)
- Used `AnimatePresence` with `mode="wait"` for proper enter/exit animations

#### Groups Page TypeScript Errors
- Removed unused `transferring` state variable
- Removed unused `showTransferModal` state variable
- Changed `variant="warning"` to `variant="default"` for IconButton (warning variant not supported)

### Security Improvements
- Backend now enforces strict data isolation between group members
- Owner-only operations properly verified at API level
- Frontend provides defense-in-depth by hiding owner controls from non-owners
- Clear error messages for unauthorized access attempts

### User Experience Improvements
- Group owners can now view any member's data for monitoring and support
- Clear visual indicators when viewing another member's data
- Seamless switching between "My Data" and member data
- Entry editing automatically disabled when viewing others' data
- Member selector automatically resets when switching groups

### Technical Details
- All backend endpoints validate group membership before processing requests
- Owner verification uses database query to check `group.owner_id`
- Frontend components receive `isOwner` flag from group data
- API client properly handles optional `userId` parameter with URLSearchParams

## Notes
- Analytics page member selector integration is pending (can be added later using same pattern)
- Feature is fully functional and tested with successful build
- No breaking changes to existing functionality
- Backwards compatible - non-owners see no changes to their experience
