# GitHub Copilot AI Assistant Instructions

## General Guidelines

- **Understand the Project**: Always read the `README.md` file in the root directory to gain context about the project.
- **Code Comments**: Add comments to explain the logic and flow of the code.
- **Testing**: Verify and test the code after writing to ensure it works as expected.

## Python and Django-Specific Guidelines

- **Docstrings**: For Python classes and functions in a Django server, include a docstring at the beginning of each class or function. The docstring should describe:
  - The purpose and usage of the class or function.
  - The parameters it takes.
  - The return values.

## Algorithm Implementation

- **DSPA Algorithm**: Refer to the `algorithms-pseudocode.tex` file located in the `docs/tex` folder for the correct implementation of the DSPA algorithm. Always use this file as the authoritative source.

## Clarifications

- **Ask Questions**: If instructions are unclear or if you are unsure about something, always ask for clarification.

## Code Structure and Refactoring

- **Preserve Existing Code**: Do not alter the structure or logic of existing code unless explicitly instructed to do so.
- **New Code**: When writing new code, ensure it integrates seamlessly with the existing structure and logic unless changes are absolutely necessary for new functionality.
- **Refactoring**: When refactoring code:
  - Avoid redundant code and ensure that the new code is efficient and clean.
  - Maintain existing functionality.
  - Improve readability, maintainability, and structure.
  - Create new files and folders if necessary for better organization.

## Summary

- Always prioritize clarity, correctness, and maintainability.
- Follow the project-specific guidelines and refer to the provided resources for context.
