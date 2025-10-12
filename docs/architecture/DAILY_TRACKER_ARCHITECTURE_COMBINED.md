````markdown
# Daily Tracker – Architecture (Original + Modifications)

Generated on: 2025-10-08

This document consolidates:
- Part A: The original architecture document (verbatim)
- Part B: The architecture modifications (verbatim)

---

## Part A: Original Architecture Document (verbatim)

# Daily Tracker - Software Architecture (Updated)

## 1. Checklist

- [ ] Design normalized database schema with role-based access control and soft deletes
- [ ] Define three-tier role hierarchy with promotion/demotion APIs
- [ ] Create GraphQL API with granular permission enforcement
- [ ] Implement non-resetting streak counter (increments only on completion)
- [ ] Add group-level timezone configuration (default GMT+5:30)
- [ ] Design responsive SPA UI with progress indicators and info tooltips
- [ ] Implement 2FA for Super Admins and notification system
- [ ] Set up automated daily backups at 00:00 HRS with point-in-time recovery
- [ ] Add analytics dashboard and content moderation features
- [ ] Ensure GDPR compliance with data export/deletion

---

## 2. DB Schema

| Table | Column | Type | Key/Constraint | Description |
|-------|--------|------|----------------|-------------|
| **Users** | id | UUID | PK | Unique user identifier |
| Users | email | VARCHAR(255) | UNIQUE, NOT NULL | User email for login |
| Users | password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| Users | name | VARCHAR(100) | NOT NULL | User display name |
| Users | role_id | INT | FK → Roles(id) | User's system role |
| Users | totp_secret | VARCHAR(255) | NULL | 2FA secret (Super Admin only) |
| Users | is_2fa_enabled | BOOLEAN | DEFAULT FALSE | 2FA activation status |
| Users | created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| Users | last_login | TIMESTAMP | NULL | Last login timestamp |
| Users | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| **Roles** | id | INT | PK | Role identifier |
| Roles | name | VARCHAR(50) | UNIQUE, NOT NULL | Role name (User, Group Admin, Super Admin) |
| Roles | description | TEXT | NULL | Role description |
| **Groups** | id | UUID | PK | Unique group identifier |
| Groups | name | VARCHAR(100) | NOT NULL | Group name |
| Groups | description | TEXT | NULL | Group description |
| Groups | timezone | VARCHAR(50) | DEFAULT 'Asia/Kolkata' | Group timezone (GMT+5:30 default) |
| Groups | admin_id | UUID | FK → Users(id) | Group admin user |
| Groups | created_at | TIMESTAMP | DEFAULT NOW() | Group creation time |
| Groups | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| **GroupMembers** | id | UUID | PK | Membership record ID |
| GroupMembers | group_id | UUID | FK → Groups(id) | Associated group |
| GroupMembers | user_id | UUID | FK → Users(id) | Member user |
| GroupMembers | joined_at | TIMESTAMP | DEFAULT NOW() | Join timestamp |
| GroupMembers | day_streak | INT | DEFAULT 0 | Non-resetting streak counter (increments only) |
| GroupMembers | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| GroupMembers | UNIQUE(group_id, user_id) WHERE deleted_at IS NULL | | CONSTRAINT | Prevent duplicate active memberships |
| **SectionEntries** | id | UUID | PK | Entry identifier |
| SectionEntries | user_id | UUID | FK → Users(id) | Entry author |
| SectionEntries | group_id | UUID | FK → Groups(id) | Associated group |
| SectionEntries | section_type | ENUM | 'Health', 'Happiness', 'Hela' | Section category (Hela = Money) |
| SectionEntries | content | TEXT | NOT NULL | Entry content |
| SectionEntries | entry_date | DATE | NOT NULL | Date of entry (in group timezone) |
| SectionEntries | edit_count | INT | DEFAULT 0 | Number of edits (max 2 per day) |
| SectionEntries | is_flagged | BOOLEAN | DEFAULT FALSE | Content moderation flag |
| SectionEntries | flagged_reason | TEXT | NULL | Reason for flagging |
| SectionEntries | created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| SectionEntries | updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| SectionEntries | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| SectionEntries | UNIQUE(user_id, group_id, section_type, entry_date) WHERE deleted_at IS NULL | | CONSTRAINT | One active entry per section per day |
| **Permissions** | id | INT | PK | Permission identifier |
| Permissions | role_id | INT | FK → Roles(id) | Associated role |
| Permissions | resource | VARCHAR(50) | NOT NULL | Resource type (e.g., 'group', 'entry') |
| Permissions | action | VARCHAR(50) | NOT NULL | Action type (e.g., 'create', 'edit', 'delete', 'view') |
| Permissions | scope | ENUM | 'own', 'group', 'all' | Permission scope |
| **Notifications** | id | UUID | PK | Notification identifier |
| Notifications | user_id | UUID | FK → Users(id) | Recipient user |
| Notifications | type | ENUM | 'incomplete_day', 'streak_milestone', 'admin_action', 'moderation' | Notification category |
| Notifications | title | VARCHAR(200) | NOT NULL | Notification title |
| Notifications | message | TEXT | NOT NULL | Notification content |
| Notifications | is_read | BOOLEAN | DEFAULT FALSE | Read status |
| Notifications | created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| **AuditLogs** | id | UUID | PK | Audit record ID |
| AuditLogs | user_id | UUID | FK → Users(id) | Actor user |
| AuditLogs | action | VARCHAR(100) | NOT NULL | Action performed |
| AuditLogs | resource_type | VARCHAR(50) | NOT NULL | Resource affected |
| AuditLogs | resource_id | UUID | NOT NULL | Resource identifier |
| AuditLogs | metadata | JSONB | NULL | Additional context |
| AuditLogs | ip_address | VARCHAR(45) | NULL | User IP address |
| AuditLogs | created_at | TIMESTAMP | DEFAULT NOW() | Action timestamp |
| **BackupLogs** | id | UUID | PK | Backup record ID |
| BackupLogs | backup_file | VARCHAR(255) | NOT NULL | Backup filename |
| BackupLogs | backup_size | BIGINT | NOT NULL | Backup size in bytes |
| BackupLogs | status | ENUM | 'success', 'failed' | Backup status |
| BackupLogs | created_at | TIMESTAMP | DEFAULT NOW() | Backup timestamp |

**Schema Validation Notes:**
- Soft delete implemented via `deleted_at` column across major tables
- `day_streak` increments only when all 3 sections completed; never decreases
- `edit_count` enforces max 2 edits per entry per day (same-day only)
- Group timezone stored as IANA timezone string (e.g., 'Asia/Kolkata' for GMT+5:30)
- Partial unique indexes (`WHERE deleted_at IS NULL`) prevent duplicate active records

---

## 3. Roles and Permissions

| Role | Resource | Actions Allowed | Scope | Notes |
|------|----------|-----------------|-------|-------|
| **User** | SectionEntries | Create, Edit (same day, max 2x), View | Own entries + Group members' view-only | Can only modify own entries created today |
| User | Groups | View | Own groups only | Can see groups they belong to |
| User | Users | View | Group members only | Can view profiles of users in same group |
| User | Notifications | View, Mark as Read | Own notifications | Receives alerts for incomplete sections, streak milestones |
| **Group Admin** | SectionEntries | Create, Edit, Soft Delete, View, Flag | All entries within managed groups | Can moderate content and soft delete inappropriate entries |
| Group Admin | Groups | Create, Edit, Soft Delete, View | Own managed groups | Can manage group metadata, timezone, and memberships |
| Group Admin | GroupMembers | Add, Remove (soft delete), View | Own managed groups | Control group membership |
| Group Admin | Analytics | View | Own managed groups | Access group-level analytics dashboard |
| Group Admin | Notifications | Create | Group members | Can send notifications to group members |
| **Super Admin** | SectionEntries | Create, Edit, Soft Delete, Restore, View | All groups and users | Unrestricted access across all data |
| Super Admin | Groups | Create, Edit, Soft Delete, Restore, View | All groups | Full group management globally |
| Super Admin | Users | Create, Edit, Soft Delete, Restore, View | All users | User account management |
| Super Admin | Roles | Assign, Promote, Demote | All users | Can change user roles (promote User → Group Admin, demote Group Admin → User) |
| Super Admin | Analytics | View | All groups | Global analytics dashboard |
| Super Admin | AuditLogs | View | All actions | Access to complete audit trail |
| Super Admin | BackupLogs | View, Trigger | All backups | Can view backup history and manually trigger backups
```