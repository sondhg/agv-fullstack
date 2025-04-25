# GitHub Copilot AI Assistant Instructions

## General Guidelines

- **Understand the Project**: Always read the `README.md` file in the root directory to gain context about the project.
- **Code Comments**: Add comments to explain the logic and flow of the code.
- **Testing**: Verify and test the code after writing to ensure it works as expected.
- Do not make unnecessary imports. Only import modules that are required for the code you are writing. It is preferable to use only existing librairies unless absolutely necessary to use external libraries or if external libraries can greatly improve the code quality and readability. If you accidentally import anything, remove it if it is not used in the code.

## Python and Django-Specific Guidelines

- **Docstrings**: For Python classes and functions in a Django server, include a docstring at the beginning of each class or function. The docstring should describe:
  - The purpose and usage of the class or function.
  - What parameters/arguments it takes.
  - The return values.

## Algorithm Implementation

- **DSPA Algorithm**: Refer to the `algorithms-pseudocode.tex` file located in the `docs/tex` folder for the correct implementation of the DSPA algorithm. Always use this file as the authoritative source.

## Clarifications

- **Ask Questions**: If instructions are unclear or if you are unsure about something, always ask for clarification.

## Code Structure and Refactoring

- Keep a flat and predictable structure for the codebase. Avoid deep nesting of folders and files.
- **New Code**: When writing new code, ensure it integrates seamlessly with the existing structure and logic unless changes are absolutely necessary for new functionality.
- **Refactoring**: When refactoring code:
  - Prevent redundancy as much as possible
  - Ensure consistency across the whole file.
  - Ensure the new code is clean, modular and highly reusable.
  - You must preserve existing functionalities. Do not break any existing features or functionalities while refactoring.
  - Improve readability and maintainability.
  - You can change files and folders structure if necessary for better organization. Ensure imports are updated accordingly.

## Summary

- Always prioritize clarity, correctness, and maintainability.
- Follow the project-specific guidelines and refer to the provided resources for context.
