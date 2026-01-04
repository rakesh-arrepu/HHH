# Changelog - 2026-01-04 (Session 2)

## Group Rename Feature (Owner-Only)

### Overview
Added the ability for group owners to rename their groups with an inline editing interface. Only the owner of a group can rename it, maintaining proper permission controls.

### Backend Changes

**File: `backend/main.py`**

1. **Added GroupUpdate Schema** (lines 169-180)
   - Pydantic model for validating group name updates
   - Name validation: non-empty, max 100 characters
   - Auto-trims whitespace

2. **Added PUT /api/groups/{group_id} Endpoint** (lines 499-538)
   - Owner-only permission check
   - Updates group name in database
   - Returns updated GroupResponse
   - Error handling:
     - 400: Validation error (empty name, too long)
     - 401: Not authenticated
     - 403: Only owner can update
     - 404: Group not found
     - 500: Database error

### Frontend Changes

**File: `frontend/src/api.ts`**

1. **Added updateGroup API Function** (lines 207-211)
   - Calls PUT /api/groups/{groupId} endpoint
   - Accepts groupId and new name
   - Returns updated group data with owner status

**File: `frontend/src/pages/Groups.tsx`**

1. **Added Imports** (lines 14-16)
   - Edit2, Check, X icons from lucide-react

2. **Added State Management** (lines 41-43)
   - `editingGroupId`: Tracks which group is being edited
   - `editingGroupName`: Stores the name being edited
   - `updating`: Loading state for update operation

3. **Added Editing Functions** (lines 157-195)
   - `startEditingGroup()`: Enters edit mode for a group
   - `cancelEditingGroup()`: Cancels editing and resets state
   - `updateGroupName()`: Saves the new group name
     - Validates non-empty name
     - Calls API
     - Updates both groups list and selected group
     - Handles errors

4. **Updated UI Rendering** (lines 176-253)
   - Conditional rendering based on `editingGroupId`
   - **Edit Mode UI**:
     - InputField with autofocus
     - Keyboard shortcuts:
       - `Enter`: Save changes
       - `Escape`: Cancel editing
     - Check ✓ button: Save (success variant)
     - X button: Cancel (danger variant)
     - Disabled state while updating
   - **Normal Display**:
     - Edit2 icon appears on hover (owner groups only)
     - Click edit icon to enter edit mode
     - stopPropagation to prevent group selection

### User Experience

**How It Works:**
1. Group owner hovers over their group in the list
2. Edit icon (✏️) appears next to the group name
3. Click edit icon to enter inline editing mode
4. Type new name and press Enter or click ✓ to save
5. Press Escape or click X to cancel
6. Group name updates in both the list and details panel

**Permissions:**
- Only group owners see the edit icon
- Only owners can rename their groups
- Backend enforces owner-only access
- Non-owners cannot access the edit functionality

### Technical Details

**Validation:**
- Frontend: Non-empty check before API call
- Backend:
  - Required field validation
  - Max length: 100 characters
  - Whitespace trimming

**State Updates:**
- Updates `groups` array with new name
- Updates `selectedGroup` if it's the edited group
- Maintains synchronization across UI

**Error Handling:**
- Displays error message in UI
- Backend returns appropriate HTTP status codes
- Failed updates don't clear the editing state

### Commit
- **Hash:** `2718b9a`
- **Message:** "feat: add group rename functionality (owner-only)"
- **Branch:** `claude/review-project-docs-IC7N8`

### Files Modified
1. `backend/main.py` - Added schema and endpoint
2. `frontend/src/api.ts` - Added API function
3. `frontend/src/pages/Groups.tsx` - Added UI and state management

### Testing Checklist
- [x] Owner can rename their group
- [x] Non-owners cannot see edit icon
- [x] Empty names are rejected
- [x] Names over 100 chars are rejected
- [x] Keyboard shortcuts work (Enter/Escape)
- [x] Group list updates after rename
- [x] Selected group updates after rename
- [x] Error messages display properly
- [x] Cancel button works
- [x] Check button works

### API Documentation

#### PUT /api/groups/{group_id}
Update a group's name (owner-only).

**Request:**
```json
{
  "name": "New Group Name"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "New Group Name",
  "owner_id": 123,
  "is_owner": true
}
```

**Error Responses:**
- `400`: Validation error (empty name, too long)
- `401`: Not authenticated
- `403`: Only owner can update group
- `404`: Group not found
- `500`: Database error
