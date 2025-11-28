"""
Agent Workflow Nodes
Each node is a step in the error fixing workflow
"""

import time
import json
from typing import Dict

from backend.parsers import ErrorClassifier
from backend.context import ContextBuilder
from backend.llm.provider_factory import LLMProviderFactory
from backend.llm_prompts import AgentPrompts
from .state import AgentState, FixSuggestion, ValidationResult


def parse_error_node(state: AgentState) -> AgentState:
    """
    Node 1: Parse raw error log
    Classifies error type and extracts structured information
    """
    print("🔍 [Node 1] Parsing error...")
    
    try:
        classifier = ErrorClassifier()
        parsed = classifier.classify_and_parse(state["raw_error_log"])
        
        state["parsed_error"] = parsed
        state["parse_success"] = True
        state["status"] = "gathering"
        
        print(f"   ✅ Detected: {parsed.language} - {parsed.error_type}")
        
    except Exception as e:
        state["parse_success"] = False
        state["status"] = "failed"
        state["error_message"] = f"Failed to parse error: {str(e)}"
        print(f"   ❌ Parse failed: {e}")
    
    return state


def gather_context_node(state: AgentState) -> AgentState:
    """
    Node 2: Gather code context
    Collects relevant files, imports, configs, git history
    """
    print("📚 [Node 2] Gathering context...")
    
    if not state["parse_success"]:
        return state
    
    try:
        builder = ContextBuilder(
            max_tokens=8000,
            project_root=state["project_root"]
        )
        context = builder.build(state["parsed_error"])
        
        state["code_context"] = context
        state["context_success"] = True
        state["tokens_used"] = context.total_tokens
        state["status"] = "analyzing"
        
        print(f"   ✅ Gathered {len(context.primary_files)} primary files")
        print(f"   ✅ Gathered {len(context.related_files)} related files")
        print(f"   ✅ Gathered {len(context.config_files)} config files")
        print(f"   📊 Token usage: {context.total_tokens} tokens")
        
    except Exception as e:
        state["context_success"] = False
        state["status"] = "failed"
        state["error_message"] = f"Failed to gather context: {str(e)}"
        print(f"   ❌ Context gathering failed: {e}")
    
    return state


def analyze_root_cause_node(state: AgentState) -> AgentState:
    """
    Node 3: Analyze root cause using LLM
    Uses LLM to understand what went wrong and why
    """
    print("🧠 [Node 3] Analyzing root cause with LLM...")
    
    if not state["context_success"]:
        return state
    
    try:
        # Get LLM provider
        provider = LLMProviderFactory.create(state["provider"])
        
        parsed = state["parsed_error"]
        context = state["code_context"]
        
        # Build prompt
        user_prompt = AgentPrompts.ROOT_CAUSE_USER.format(
            language=parsed.language,
            framework=parsed.framework or "None",
            error_type=parsed.error_type,
            severity=parsed.severity,
            category=parsed.category,
            message=parsed.message,
            stack_trace=AgentPrompts.format_stack_trace(parsed),
            primary_files_context=AgentPrompts.format_file_context(context.primary_files, max_files=2),
            related_files_context=AgentPrompts.format_file_context(context.related_files, max_files=2),
            config_files_context=AgentPrompts.format_file_context(context.config_files, max_files=2),
            git_changes=AgentPrompts.format_git_changes(context.primary_files)
        )
        
        # Call LLM
        response = provider.generate(
            system_prompt=AgentPrompts.ROOT_CAUSE_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        state["root_cause_analysis"] = response.content
        state["analysis_success"] = True
        state["status"] = "generating"
        
        print(f"   ✅ Analysis complete ({response.tokens_used} tokens)")
        print(f"   📝 Root cause: {response.content[:100]}...")
        
    except Exception as e:
        state["analysis_success"] = False
        state["status"] = "failed"
        state["error_message"] = f"Failed to analyze: {str(e)}"
        print(f"   ❌ Analysis failed: {e}")
    
    return state


def generate_fixes_node(state: AgentState) -> AgentState:
    """
    Node 4: Generate fix suggestions
    Uses LLM to create concrete code patches
    """
    print("🔧 [Node 4] Generating fix suggestions...")
    
    if not state["analysis_success"]:
        return state
    
    try:
        provider = LLMProviderFactory.create(state["provider"])
        
        parsed = state["parsed_error"]
        context = state["code_context"]
        
        # Build code context string
        code_context_str = AgentPrompts.format_file_context(
            context.primary_files,
            max_files=2
        )
        
        # Build prompt
        user_prompt = AgentPrompts.FIX_GENERATION_USER.format(
            root_cause_analysis=state["root_cause_analysis"],
            language=parsed.language,
            error_type=parsed.error_type,
            message=parsed.message,
            code_context=code_context_str
        )
        
        # Define JSON schema
        schema = {
            "fixes": [
                {
                    "file_path": "string",
                    "original_snippet": "string",
                    "new_snippet": "string",
                    "explanation": "string",
                    "confidence": "number",
                    "line_number": "number or null"
                }
            ]
        }
        
        # Call LLM with JSON mode
        response_json = provider.generate_json(
            system_prompt=AgentPrompts.FIX_GENERATION_SYSTEM,
            user_prompt=user_prompt,
            schema=schema
        )
        
        # Parse fixes
        fixes_data = response_json.get("fixes", [])
        fixes = []
        
        for fix_data in fixes_data:
            try:
                fix = FixSuggestion(**fix_data)
                if fix.confidence >= 0.7:  # Only keep high-confidence fixes
                    fixes.append(fix)
            except Exception as e:
                print(f"   ⚠️  Skipped invalid fix: {e}")
                continue
        
        state["fix_suggestions"] = fixes
        state["generation_success"] = True
        state["status"] = "validating"
        
        print(f"   ✅ Generated {len(fixes)} fix suggestion(s)")
        for i, fix in enumerate(fixes, 1):
            print(f"   {i}. {fix.file_path} (confidence: {fix.confidence:.2f})")
        
    except Exception as e:
        state["generation_success"] = False
        state["status"] = "failed"
        state["error_message"] = f"Failed to generate fixes: {str(e)}"
        print(f"   ❌ Fix generation failed: {e}")
    
    return state


def validate_fixes_node(state: AgentState) -> AgentState:
    """
    Node 5: Validate fix suggestions
    Checks basic validity of suggested fixes (relaxed for code snippets)
    """
    print("✓ [Node 5] Validating fixes...")
    
    if not state["generation_success"] or not state["fix_suggestions"]:
        state["validation_success"] = False
        return state
    
    try:
        validated_fixes = []
        failed_fixes = []
        
        for fix in state["fix_suggestions"]:
            # Basic validation checks (more lenient now)
            is_valid = True
            error_msg = None
            
            # Check 1: File path is not empty
            if not fix.file_path:
                is_valid = False
                error_msg = "Empty file path"
            
            # Check 2: Snippets are not empty
            elif not fix.original_snippet or not fix.new_snippet:
                is_valid = False
                error_msg = "Empty code snippet"
            
            # Check 3: Snippets are different
            elif fix.original_snippet.strip() == fix.new_snippet.strip():
                is_valid = False
                error_msg = "Fix doesn't change anything"
            
            # Check 4: Very basic syntax check (more lenient)
            # Only check if the new snippet is reasonably structured
            elif state["parsed_error"].language == "python":
                # Try to validate, but be lenient with incomplete code
                try:
                    # Remove leading whitespace to avoid indentation errors
                    dedented_code = fix.new_snippet.strip()
                    
                    # Try to parse - but don't fail if it's a snippet
                    try:
                        import ast
                        ast.parse(dedented_code)
                    except SyntaxError:
                        # If it fails, check if it's just a snippet (e.g., single line)
                        # Allow it if it looks like valid Python structure
                        if any(keyword in dedented_code for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', '=']):
                            # Looks like valid Python structure, allow it
                            pass
                        else:
                            # Actually invalid
                            is_valid = False
                            error_msg = "Invalid Python syntax"
                except:
                    # If we can't check, just allow it
                    pass
            
            if is_valid:
                validated_fixes.append(fix)
                print(f"   ✅ Valid: {fix.file_path}")
            else:
                failed_fixes.append((fix, error_msg))
                print(f"   ❌ Invalid: {fix.file_path} - {error_msg}")
        
        # Create validation result
        validation_result = ValidationResult(
            is_valid=len(validated_fixes) > 0,
            error_message=None if validated_fixes else "All fixes failed validation",
            validated_fixes=validated_fixes,
            failed_fixes=failed_fixes
        )
        
        state["validation_result"] = validation_result
        state["validation_success"] = validation_result.is_valid
        
        if validation_result.is_valid:
            state["final_fixes"] = validated_fixes
            state["status"] = "success"
            print(f"   ✅ {len(validated_fixes)} fix(es) validated successfully")
        else:
            state["status"] = "refining"
            state["retry_feedback"] = "; ".join([msg for _, msg in failed_fixes])
            print(f"   ⚠️  All fixes failed validation, will retry")
        
    except Exception as e:
        state["validation_success"] = False
        state["status"] = "failed"
        state["error_message"] = f"Validation failed: {str(e)}"
        print(f"   ❌ Validation error: {e}")
    
    return state



def refine_fixes_node(state: AgentState) -> AgentState:
    """
    Node 6: Refine fixes with feedback
    Regenerates fixes using validation feedback
    """
    print("🔄 [Node 6] Refining fixes with feedback...")
    
    # Check retry limit
    if state["retry_count"] >= state["max_retries"]:
        state["status"] = "failed"
        state["error_message"] = f"Max retries ({state['max_retries']}) reached"
        print(f"   ❌ Max retries reached")
        return state
    
    state["retry_count"] += 1
    print(f"   🔄 Retry attempt {state['retry_count']}/{state['max_retries']}")
    
    try:
        provider = LLMProviderFactory.create(state["provider"])
        
        # Build refinement prompt
        previous_fix_str = json.dumps(
            [fix.dict() for fix in state["fix_suggestions"]],
            indent=2
        )
        
        code_context_str = AgentPrompts.format_file_context(
            state["code_context"].primary_files,
            max_files=2
        )
        
        user_prompt = AgentPrompts.REFINEMENT_USER.format(
            previous_fix=previous_fix_str,
            validation_feedback=state["retry_feedback"],
            error_type=state["parsed_error"].error_type,
            message=state["parsed_error"].message,
            code_context=code_context_str
        )
        
        # Generate refined fixes
        response_json = provider.generate_json(
            system_prompt=AgentPrompts.REFINEMENT_SYSTEM,
            user_prompt=user_prompt,
            schema={"fixes": []}
        )
        
        # Parse refined fixes
        fixes_data = response_json.get("fixes", [])
        refined_fixes = []
        
        for fix_data in fixes_data:
            try:
                fix = FixSuggestion(**fix_data)
                if fix.confidence >= 0.7:
                    refined_fixes.append(fix)
            except:
                continue
        
        state["fix_suggestions"] = refined_fixes
        state["generation_success"] = True
        state["status"] = "validating"
        
        print(f"   ✅ Generated {len(refined_fixes)} refined fix(es)")
        
    except Exception as e:
        state["status"] = "failed"
        state["error_message"] = f"Refinement failed: {str(e)}"
        print(f"   ❌ Refinement failed: {e}")
    
    return state
