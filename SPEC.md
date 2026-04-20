# HomeNet - Parental Network Controller

## Project Overview

**Project Name:** HomeNet
**Type:** Desktop Application (Python 3)
**Core Feature:** Parental network control with time-based blocking, traffic monitoring, and bilingual UI
**Target Users:** Parents who want to monitor and control their home network, especially for child safety
**Platform:** Raspberry Pi 3 / Linux Desktop
**Language:** Python 3.10+
**Development:** Proudly developed in UAE, Al Ain

## UI/UX Specification

### Layout Structure

#### Multi-Window Model
- **Main Window:** Primary application interface with sidebar navigation
- **Login Dialog:** Authentication screen on startup
- **Settings Dialog:** Configuration and user management
- **Alert Popup:** System notifications for new hosts and high traffic

#### OS-Native Style Adaptation
- CustomTkinter for modern, cross-platform GUI
- System tray integration for background operation
- Native window decorations with custom theming

#### Major Layout Areas
1. **Sidebar Navigation (Left/Right based on language)**
   - Dashboard
   - Hosts
   - Traffic
   - Rules
   - Alerts
   - Settings
   - About

2. **Main Content Area**
   - Dynamic content based on selected navigation
   - Data tables, charts, and controls

3. **Status Bar (Bottom)**
   - Connection status
   - Current time
   - Active blocking status

### Visual Design

#### Color Palette
- **Primary:** #1E88E5 (Blue - Trust/Security)
- **Secondary:** #43A047 (Green - Allowed/Active)
- **Accent:** #FF7043 (Orange - Warnings)
- **Danger:** #E53935 (Red - Blocked/Alert)
- **Background Dark:** #1A1A2E
- **Background Light:** #16213E
- **Surface:** #0F3460
- **Text Primary:** #FFFFFF
- **Text Secondary:** #B0B0B0

#### Typography
- **Font Family:** Segoe UI, Tahoma (for Arabic: Amiri, Tajawal)
- **Heading 1:** 24px, Bold
- **Heading 2:** 20px, SemiBold
- **Body:** 14px, Regular
- **Caption:** 12px, Regular

#### Spacing System
- **Base Unit:** 8px
- **Margins:** 16px, 24px, 32px
- **Padding:** 8px, 12px, 16px
- **Border Radius:** 8px, 12px

#### Visual Effects
- Subtle shadows on cards (0 4px 6px rgba(0,0,0,0.3))
- Smooth transitions (200ms ease-in-out)
- Hover effects with slight brightness increase
- Active navigation highlight with accent color border

### Components

#### Navigation Sidebar
- Icon + Text menu items
- Active state: Accent background + left border
- Hover: Slight brightness increase

#### Data Tables
- Zebra striping
- Sortable columns
- Row hover highlight
- Action buttons per row

#### Cards
- Rounded corners (12px)
- Shadow on hover
- Icon + Title + Content structure

#### Buttons
- Primary: Filled with primary color
- Secondary: Outlined
- Danger: Red filled
- Disabled: 50% opacity

#### Toggle Switches
- On: Green with checkmark
- Off: Gray with X

#### Input Fields
- Rounded borders
- Focus state with accent border
- RTL support for Arabic

## Functionality Specification

### Core Features

#### 1. Authentication System
- **Login:** Username + Password
- **Default Credentials:** admin / 123456
- **Session Management:** Auto-logout after inactivity
- **Password Reset:** Email-based reset capability
- **User Management:** Add/Edit/Delete users

#### 2. Dashboard
- Network status overview
- Active hosts count
- Current traffic summary
- Blocking status indicator
- Quick actions (Enable/Disable blocking)

#### 3. Host Management
- **Discovery:** Automatic network scanning (ARP)
- **Host List:** IP, MAC, Hostname, OS Detection, Device Type
- **Host Details:** Full hardware/software information
- **Host Actions:** Block/Unblock, Set priority, Add to groups
- **Device Recognition:** Smart device type detection

#### 4. Traffic Monitoring
- **Real-time:** Live bandwidth usage per host
- **Historical:** Traffic volume by hour/day/week
- **Top Consumers:** List of heaviest users
- **Traffic Types:** Browsing, Gaming, Streaming, Social Media
- **Charts:** Line graphs, bar charts, pie charts

#### 5. Time-Based Blocking
- **Schedule:** 11 PM to 12 PM (configurable)
- **Days:** Select specific days of week
- **Actions:** Block all internet or selective blocking
- **Override:** Temporary bypass with password

#### 6. Application Blocking
- **Categories:**
  - Gaming (Steam, Epic, Roblox, etc.)
  - Social Media (Facebook, Instagram, TikTok, Snapchat)
  - Streaming (Netflix, YouTube, Disney+, etc.)
- **Custom Rules:** Add by domain/IP/port
- **Whitelist:** Exempt certain apps

#### 7. Alert System
- **New Host Alert:** Notify when unknown device connects
- **High Traffic Alert:** When usage exceeds threshold
- **Blocked Attempt:** Log blocked connection attempts
- **Alert Channels:** In-app notifications, Email
- **Alert History:** Searchable log

#### 8. Speed Test
- **Download Speed:** Mbps
- **Upload Speed:** Mbps
- **Latency:** ms
- **Jitter:** ms
- **Server Selection:** Auto/Manual

#### 9. Settings
- **Language:** Arabic / English toggle
- **Theme:** Dark mode (default)
- **Network Interface:** Select adapter
- **Blocking Mode:** Full block / Selective
- **Email Configuration:** SMTP settings
- **User Management:** Change password, add email

### User Interactions and Flows

#### Login Flow
1. App starts → Login screen
2. Enter credentials → Validate
3. Success → Main dashboard
4. Failure → Error message, retry

#### Blocking Activation
1. Dashboard → Toggle blocking ON
2. System activates iptables rules
3. All traffic blocked for blocked hosts
4. Timer countdown displayed
5. Auto-disable at scheduled end time

#### New Host Detection
1. ARP scan detects new MAC
2. Alert generated with host details
3. User chooses: Block / Allow / Ignore
4. Rule created based on choice

### Data Handling

#### Local Storage (SQLite)
- Users table
- Hosts table
- Traffic logs table
- Rules table
- Alerts table
- Settings table

#### Configuration Files
- config.json: App settings
- rules.json: Blocking rules
- schedule.json: Time schedules

### Edge Cases
- Multiple devices with same hostname
- Unknown device types
- Network interface changes
- Database corruption recovery
- Concurrent admin sessions
- System sleep/wake handling

## Technical Specification

### Required Packages
```
customtkinter>=5.2.0
psutil>=5.9.0
scapy>=2.5.0
matplotlib>=3.7.0
Pillow>=10.0.0
plyer>=2.0.0
requests>=2.31.0
speedtest-cli>=2.1.0
```

### System Requirements
- Python 3.10+
- Linux (Raspberry Pi OS) / macOS / Windows
- Network interface with monitor capability
- Root/sudo for iptables modifications

### Architecture
```
homenet/
├── main.py                 # Entry point
├── app.py                  # Main application class
├── gui/
│   ├── __init__.py
│   ├── login.py            # Login window
│   ├── dashboard.py         # Dashboard view
│   ├── hosts.py             # Host management
│   ├── traffic.py            # Traffic monitoring
│   ├── rules.py             # Rule configuration
│   ├── alerts.py            # Alert management
│   ├── settings.py          # Settings view
│   └── widgets.py           # Custom widgets
├── core/
│   ├── __init__.py
│   ├── network.py           # Network scanning
│   ├── monitor.py           # Traffic monitoring
│   ├── blocker.py           # iptables blocking
│   ├── database.py          # SQLite operations
│   └── speedtest.py         # Speed test
├── utils/
│   ├── __init__.py
│   ├── i18n.py              # Internationalization
│   ├── logger.py            # Logging
│   └── config.py            # Configuration
├── resources/
│   └── icons/               # App icons
└── requirements.txt
```

## Acceptance Criteria

### Authentication
- [ ] Login with default credentials works
- [ ] Password change functionality works
- [ ] Email configuration for reset works

### Dashboard
- [ ] Shows current network status
- [ ] Displays active host count
- [ ] Shows blocking toggle
- [ ] Quick action buttons functional

### Host Management
- [ ] Scans and lists all hosts
- [ ] Shows IP, MAC, hostname
- [ ] Detects OS type
- [ ] Block/Unblock hosts works

### Traffic Monitoring
- [ ] Real-time bandwidth display
- [ ] Historical data charts
- [ ] Per-host traffic breakdown

### Time Blocking
- [ ] Schedule blocking 11 PM - 12 PM
- [ ] Day selection works
- [ ] Auto-enable/disable works

### Alerts
- [ ] New host notifications appear
- [ ] High traffic alerts work
- [ ] Alert history accessible

### Bilingual
- [ ] English fully translated
- [ ] Arabic fully translated
- [ ] RTL layout correct for Arabic

### Visual Checkpoints
- [ ] Modern dark theme applied
- [ ] Responsive layout
- [ ] Smooth animations
- [ ] Consistent spacing
