"""
LLM Prompt Templates
All prompts used by the agent for analysis and fix generation
"""

from typing import List


class AgentPrompts:
    """Collection of all agent prompts"""

    # ============================================
    # ROOT CAUSE ANALYSIS PROMPTS
    # ============================================

    ROOT_CAUSE_SYSTEM = """You are a senior software engineer with deep expertise in debugging.
Your role is to analyze error logs and code to identify the root cause of issues.

Guidelines:
- Be precise and technical
- Focus on the actual problem, not symptoms
- Consider the full context (code, imports, recent changes)
- Explain in clear, actionable terms
- Keep your analysis concise (3-5 sentences)"""

    ROOT_CAUSE_USER = """# Error Information

**Language:** {language}
**Framework:** {framework}
**Error Type:** {error_type}
**Severity:** {severity}
**Category:** {category}

**Error Message:**
{message}

---

# Stack Trace

{stack_trace}

---

# Code Context

## Primary Files (Where Error Occurred)

{primary_files_context}

## Related Files (Imports/Dependencies)

{related_files_context}

## Configuration Files

{config_files_context}

---

# Recent Changes (Git)

{git_changes}

---

# Task

Analyze this error and provide:

1. **Root Cause** (2-3 sentences): What exactly went wrong and why?
2. **Key Location**: Which file and line is most critical to fix?
3. **Impact**: What breaks because of this error?

Be specific and actionable."""

    # ============================================
    # FIX GENERATION PROMPTS
    # ============================================

    FIX_GENERATION_SYSTEM = """You are an expert code fixer. Your task is to generate precise, minimal code patches.

Guidelines:
- Only change what's necessary to fix the issue
- Ensure fixes are syntactically correct
- Provide clear explanations
- Include confidence scores (0.0 to 1.0)
- Only suggest fixes you're confident about (>0.7 confidence)
- Consider edge cases and side effects"""

    FIX_GENERATION_USER = """# Root Cause Analysis

{root_cause_analysis}

---

# Error Details

**Language:** {language}
**Error Type:** {error_type}
**Message:** {message}

---

# Code to Fix

{code_context}

---

# Task

Generate 1-3 concrete code fix suggestions.

**IMPORTANT FORMATTING RULES:**
1. Return ONLY valid JSON, no markdown, no code blocks, no explanations outside JSON
2. In code snippets: use spaces (not tabs), keep consistent indentation
3. Make snippets complete and self-contained (no partial lines)
4. Match the original code's indentation style

**JSON Format:**

{{
  "fixes": [
    {{
      "file_path": "exact/path/to/file.py",
      "original_snippet": "complete line(s) of code to replace",
      "new_snippet": "complete fixed line(s)",
      "explanation": "why this fixes the issue",
      "confidence": 0.95,
      "line_number": 42
    }}
  ]
}}

**Rules:**
- Include 1-3 fixes maximum
- Only fixes with confidence > 0.7
- Use exact file paths from the error
- Keep code snippets simple and focused
- Ensure proper spacing in JSON (commas, colons)"""


    # ============================================
    # REFINEMENT PROMPTS (for retry with feedback)
    # ============================================

    REFINEMENT_SYSTEM = """You are an expert code fixer refining a previous fix attempt.
The previous fix failed validation. Analyze the feedback and provide a better solution."""

    REFINEMENT_USER = """# Previous Fix Attempt

The following fix was suggested but failed validation:

{previous_fix}

# Validation Feedback

{validation_feedback}

---

# Original Error Context

**Error Type:** {error_type}
**Message:** {message}

# Code Context

{code_context}

---

# Task

Analyze what went wrong with the previous fix and generate an improved version.

Respond with the same JSON format:

{{
"fixes": [
{{
"file_path": "path/to/file",
"original_snippet": "code to replace",
"new_snippet": "improved corrected code",
"explanation": "why this version is better",
"confidence": 0.9,
"line_number": 42
}}
]
}}

Focus on addressing the validation feedback."""

    # ============================================
    # HELPER METHODS
    # ============================================

    @staticmethod
    def format_stack_trace(parsed_error: "ParsedError") -> str:
        """Format stack trace for prompt"""
        if not parsed_error.stack_frames:
            return "No stack trace available"

        lines = []
        for i, frame in enumerate(parsed_error.stack_frames, 1):
            location = f"{frame.file_path}:{frame.line}"
            if frame.column:
                location += f":{frame.column}"

            line = f"{i}. {location}"
            if frame.function:
                line += f" in {frame.function}()"

            lines.append(line)

            if frame.code_snippet:
                lines.append(f"   > {frame.code_snippet}")

        return "\n".join(lines)

    @staticmethod
    def format_file_context(file_contexts: List, max_files: int = 3) -> str:
        """Format file contexts for prompt"""
        if not file_contexts:
            return "No files available"

        sections = []
        for fc in file_contexts[:max_files]:
            section = f"""### {fc.file_path}
Lines {fc.start_line}-{fc.end_line}
{fc.content}
"""
            sections.append(section)

        return "\n\n".join(sections)

    @staticmethod
    def format_git_changes(file_contexts: List) -> str:
        """Format git changes for prompt"""
        changes = []

        for fc in file_contexts:
            if fc.git_diff:
                changes.append(f"### {fc.file_path}\n\n```")

        return "\n\n".join(changes) if changes else "No recent changes available"
