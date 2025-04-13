# AGV System - Product Requirements Document (MVP)

## 1. Core System Architecture Setup

### 1.1 Backend Foundation
- [ ] Set up Django server
- [ ] Set up PostgreSQL database
- [ ] Implement basic API structure
- [ ] Configure WebSocket server for real-time updates
- [ ] Set up MQTT broker for AGV communication

### 1.2 Frontend Foundation
- [ ] Initialize React TypeScript Shadcn/UI TailwindCSS application
- [ ] Set up TypeScript configuration
- [ ] Implement basic routing structure
- [ ] Configure state management (Redux)
- [ ] Set up WebSocket client connection
- [ ] Create basic layout components

## 2. Map and Navigation System

### 2.1 Map Data Structure
- [ ] Design graph data structure for warehouse layout
- [ ] Implement node representation
- [ ] Implement edge representation
- [ ] Create database schema for map storage
- [ ] Add API endpoints for map CRUD operations

### 2.2 Map Visualization
- [ ] Implement node visualization
- [ ] Implement path visualization
- [ ] Add map editing capabilities

## 3. AGV Management System

### 3.1 AGV Data Structure
- [ ] Design AGV model and state representation
- [ ] Create database schema for AGV data
- [ ] Implement AGV status tracking
- [ ] Add API endpoints for AGV management
- [ ] Set up real-time AGV state updates

### 3.2 AGV Simulation (Testing Environment)
- [ ] Create basic AGV simulation module
- [ ] Implement MQTT communication for simulated AGVs
- [ ] Add movement simulation logic
- [ ] Implement basic collision detection
- [ ] Add visualization for simulated AGVs

## 4. Order Management System

### 4.1 Order (Task) Data Structure
- [ ] Design task model and states
- [ ] Create database schema for tasks
- [ ] Implement task queue management
- [ ] Add API endpoints for task CRUD operations
- [ ] Set up task status tracking

### 4.2 Order (Task) Assignment Interface
- [ ] Create task creation form
- [ ] Implement task list view
- [ ] Add task status visualization
- [ ] Implement task filtering and sorting
- [ ] Add task modification capabilities

## 5. Core Algorithms Implementation

### 5.1 Order Dispatching (Algorithm 1)
- [ ] Implement basic path calculation
- [ ] Add task assignment logic
- [ ] Implement priority handling
- [ ] Add basic optimization rules
- [ ] Create API endpoints for dispatching

### 5.2 Local Control Policy (Algorithm 2)
- [ ] Implement position update logic
- [ ] Add basic collision avoidance
- [ ] Implement movement control
- [ ] Add status reporting
- [ ] Create API endpoints for local control

### 5.3 Deadlock Resolution (Algorithm 3)
- [ ] Implement deadlock detection
- [ ] Add basic resolution strategy
- [ ] Implement path recalculation
- [ ] Create API endpoints for deadlock handling

### 5.4 Spare Point Allocation (Algorithm 4)
- [ ] Implement spare point identification
- [ ] Add allocation logic
- [ ] Implement deallocation rules
- [ ] Create API endpoints for spare point management

## 6. Monitoring and Control Interface

### 6.1 Real-time Monitoring
- [ ] Create system status dashboard
- [ ] Implement AGV status display
- [ ] Add task progress visualization
- [ ] Implement alert system
- [ ] Add performance metrics display

### 6.2 Control Interface
- [ ] Create manual control interface
- [ ] Implement emergency stop functionality
- [ ] Add system parameter configuration
- [ ] Implement user authentication
- [ ] Add access control

## Development Priorities

1. First Sprint (Core Infrastructure):
   - Complete sections 1.1 and 1.2
   - Begin work on 2.1

2. Second Sprint (Basic Functionality):
   - Complete sections 2.1 and 2.2
   - Begin work on 3.1 and 3.2

3. Third Sprint (Task Management):
   - Complete sections 3.1 and 3.2
   - Begin work on 4.1 and 4.2

4. Fourth Sprint (Algorithm Implementation):
   - Complete sections 4.1 and 4.2
   - Begin work on 5.1 and 5.2

5. Fifth Sprint (Advanced Features):
   - Complete remaining algorithms in section 5
   - Begin work on section 6

6. Sixth Sprint (Finalization):
   - Complete section 6
   - Testing and bug fixes
   - Documentation

## Success Criteria

1. System can successfully:
   - Display and manage warehouse map
   - Handle multiple AGV simulations
   - Assign and track tasks
   - Detect and avoid collisions
   - Resolve deadlocks
   - Provide real-time monitoring

2. Performance metrics:
   - Task assignment response time < 1s
   - Real-time updates latency < 100ms
   - Zero collisions in normal operation
   - Successful deadlock resolution > 99%
   - System uptime > 99.9%
