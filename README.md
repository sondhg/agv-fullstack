# AGV System Web Application

This web application implements scheduling of a multi-AGV (Automated Guided Vehicle) coordination system for a fixed map layout, based on the Dynamic Spare Point Application (DSPA) algorithm.

The main purpose is to implement ideas in the paper "A Dynamic Spare Point Application Based Coordination for Multi-AGV Systems in a WIP Warehouse Environment" as in file `algorithms-pseudocode.tex` to the web application.

## Overview

The system coordinates multiple AGVs to efficiently deliver materials from storage locations to workstations while avoiding collisions and deadlocks. Key features include:

- Task assignment and dispatching by a central controller. In other words, users send orders, and the server generates smart schedules for AGVs. Schedules can be updated in real-time if needed.
- Local control of individual AGVs. Since I do not have physical AGVs, I will eventually create a simple simulation to represent the AGVs for testing position updates.
- Collision avoidance through point reservation
- Deadlock resolution using dynamic spare points
- Real-time monitoring and visualization of AGV movements

## Core Concepts

The system implements several key algorithms from the research paper:

1. Task Dispatching (Algorithm 1) - Central controller assigns tasks and calculates paths
2. Local Control Policy (Algorithm 2) - Individual AGV movement control and collision avoidance
3. Deadlock Resolution (Algorithm 3) - Central controller detects and resolves deadlocks
4. Spare Point Allocation (Algorithm 4) - Assigns temporary detour points to resolve conflicts

## System Architecture

The application consists of:

- Frontend UI for visualization and control
- Backend server implementing the control algorithms
- Database for storing system state and configuration
- HTTP and WebSocket for communication between the frontend and backend.
- MQTT for communication between the AGV simulation and the backend.

## Key Features

- Map layout
- Task creation and assignment interface
- Real-time status monitoring
- Configuration of warehouse layout and AGV parameters
- Visualization of collision/deadlock resolution

## Implementation Details

The system models the warehouse as a graph where:

- Nodes represent storage locations, workstations, and guide points
- Edges represent valid paths between nodes
- AGVs move along edges between nodes
- Point reservation prevents collisions
- Spare points provide temporary detour locations

This implementation aims to demonstrate the practical application of the DSPA algorithm in a real warehouse environment while providing an intuitive interface for monitoring and control.
