# AI Development Assistant Instructions

This guide defines the expected practices and standards for AI-assisted development across Django server backend and React frontend of this web app project.

## Universal Development Standards

1. **Code Quality**

   - Follow project-specific style guides and conventions
   - Write clear, self-documenting code with meaningful names
   - Keep functions under 30 lines and files under 300 lines
   - Document complex logic and public interfaces
   - Include comprehensive unit tests
   - Run linters and formatters before commits
   - Remove unused imports and dependencies

2. **Documentation Requirements**

   ```python
   def example_function(param1: type, param2: type = default) -> return_type:
       """
       Purpose: Brief description

       Args:
           param1 (type): Description
           param2 (type, optional): Description. Default: default

       Returns:
           return_type: Description

       Raises:
           ExceptionType: Description

       Example:
           >>> example_function("test", param2=123)
           expected_output
       """
   ```

3. **Project Integration**

   - Review project README and architecture docs
   - Use established patterns and conventions
   - Do not try to install any new dependencies. Only use what has been installed in the project. All necessary dependencies are already installed using pnpm and pip.
   - Group related code by feature
   - Extract reusable components
   - Implement proper error handling
   - Optimize for performance when necessary

## Language-Specific Guidelines

### Python/Django

- Use type hints and docstrings
- Follow PEP 257 for documentation
- Document class attributes and inheritance
- Try to use functions instead of class methods

### React

- Use React hooks and TypeScript
- Group code by feature
- Lazy load large modules
- Maintain flat directory structure
- Extract shared utilities
- Monitor bundle size

## References

- PEP 257: https://peps.python.org/pep-0257/
- Project style guide
- Architecture documentation

For unclear requirements or edge cases, request clarification before proceeding.

<!-- ## Notes
- Right now, I want to build the "Dashboard" page in PageDashboard.tsx. It is a rebuilt version of the "AGVs" page, with full MQTT and WebSocket implementation instead of just HTTP. There will be files that have the same names, so I want you to focus only on the `dashboard` folder, not the `agvs` folder in the `admin` folder when helping me with frontend code. Do not care about the `agvs` folder in the `admin` folder at all.  -->
