You are a software engineer refactoring Python code.

## Inputs
1) Existing implementation file (content inserted below)
2) Pytest file(s) for this task (content inserted below)

## Goal
Refactor the implementation to improve readability and maintainability while preserving behavior exactly as validated by the provided tests.


## Output Format (strict)
- Provide exactly one Python code block containing the full refactored implementation.
- After the code block, provide the checklist in 5 to 10 bullets.
- Do NOT include any additional text.
- Ensure functions have the correct return type
- Functions should be returning "None" instead of the boolean "False", but "True" in cases they are true
- Ensure floating-point values have correct mathematical precisions and are exact
- Ensure is_tree_balanced function has handling for various tree structures, including potential right-heavy and left-heavy trees, which should be False in such cases
- Ensure functions can account for edge cases such as empty strings correctly
- ensure mathematical calculations are precise and exact 
- do not refactor function names.
- the kth_element function should be returning the value at the position counting the first value as index 1
- follow original logic as closely as possible

---

## Implementation file content
<<<IMPLEMENTATION>>>
