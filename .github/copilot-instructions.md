# Custom Instructions for Copilot

This file contains custom instructions for Copilot to follow when generating code.

## Project Overview

This project consists of:

- **Frontend**: A React TypeScript Vite application responsible for rendering the user interface and handling user interactions.
- **Backend**: A Django project that processes data and serves API requests.

The two parts communicate via a REST API. The web app is designed to control a multi-AGV system, where:

- The **web server** acts as the central controller.
- The **physical AGVs** act as local controllers. Because the AGVs are not yet available, simulation will need to be implemented.

The primary focus is implementing the **Dynamic Spare Point Application (DSPA)** algorithm, as described in the `docs/algorithms-pseudocode.md` file. This document provides detailed explanations and pseudocode for DSPA, which is central to the system's functionality. The backend app `schedule_generate` is the main area for developing scheduling algorithms.

## Guidelines for Copilot

When interacting with me, follow these guidelines:

### General Communication

- Use clear and concise language.
- Provide code examples when necessary.
- Use comments in the code to explain complex logic or important sections.
- Always ask for clarification if you do not understand the context.

### Code Quality

- Follow best practices for code organization and structure.
- Use consistent naming conventions for variables and functions.
- Ensure the code is well-formatted and easy to read.
- Use appropriate error handling and validation.
- Avoid using deprecated or outdated libraries and methods.

### File and Folder Management

- If creating new files, specify:
  - File names.
  - Their contents.
  - Their locations.
- If creating new folders, specify:
  - Folder names.
  - Their contents.
  - Their locations.
- If editing a file, provide code of the entire edited file, not just the modified section.

### Context Awareness

- Use attached context to provide accurate answers.
- Remember and reuse context in future interactions.
- Be cautious when handling files with the same names in different folders.
- Pay extra attention to API endpoints and their expected inputs and outputs, their formats, and the data types used in the frontend and backend.

### Transparency

- Inform me if:
  - You are unsure about something.
  - You are unable to do something.
  - You cannot find, understand, or learn something.

### Additional Suggestions

- Provide alternative solutions or approaches when applicable.
- Highlight potential issues or limitations in the code or logic.

By following these instructions, Copilot can better assist in developing and maintaining this project.
