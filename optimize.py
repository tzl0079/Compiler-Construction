# Author: Thomas Lander
# Date: 12/02/24
# three_address_code.py

class Optimizer:
    def __init__(self, tac):
        self.tac = tac
        self.constants = {} 


    # Main Optimization function, checks for true flags and applies the appropriate optimization techniques
    def optimize(self, constant_folding = False, constant_propagation = False, dead_code_elimination = False):
        optimized_tac = self.tac

        if constant_folding:
            optimized_tac = self.apply_constant_folding(optimized_tac)
        if constant_propagation:
            optimized_tac = self.apply_constant_propagation(optimized_tac)
        if dead_code_elimination:
            optimized_tac = self.apply_dead_code_elimination(optimized_tac)

        return optimized_tac


    # Constant Folding Optimization 
    # t1 = 1 + 3 --> t1 = 4
    def apply_constant_folding(self, tac):
        optimized_tac = []

        for line in tac:
            # Check for assignments
            if " = " in line:
                var, expr = line.split(" = ", 1)
                expr_parts = expr.split(" ")

                # Try to evaluate expressions directly
                if all(part.isdigit() or part.replace('.', '', 1).isdigit() for part in expr_parts \
                        if part not in ['+', '-', '*', '/', '%']):
                    try:
                        result = self.evaluate_expression(expr_parts)
                        optimized_tac.append(f"{var} = {result}")
                        continue  
                    # If evaluation fails, just skip to next
                    except Exception:
                        pass 

            # Append unchanged line if can't fold 
            optimized_tac.append(line)

        return optimized_tac


    # Constant Propagation Optimization
    # t1 = x + 2 --> t1 = 3 + 2 (where x = 3)
    def apply_constant_propagation(self, tac):
        optimized_tac = [] 
        self.constants = {}
        inside_loop = False  

        for line in tac:
            # Detect loop entry via labels (e.g., "L2:")
            if ":" in line and "goto" not in line:  
                label = line.split(":")[0]
                # Set loop flag
                if label.startswith("L"):
                    inside_loop = True
                optimized_tac.append(line) 
                continue

            # Reset loop flag when no longer in loop body
            if "goto" in line and not "if" in line:
                inside_loop = False
                optimized_tac.append(line)
                continue

            # Check for assignments
            if " = " in line:
                var, expr = line.split(" = ", 1)
                expr_parts = expr.split(" ")

                # Replace variables in the expression with their constant values only if outside loops
                if not inside_loop:
                    expr_parts = [str(self.constants.get(part, part)) for part in expr_parts]

                # If the entire expression becomes a constant, evaluate it
                if all(part.isdigit() or part.replace('.', '', 1).isdigit() for part in expr_parts \
                        if part not in ['+', '-', '*', '/', '%']):
                    try:
                        result = self.evaluate_expression(expr_parts)
                        # Only update the constants map if outside a loop
                        if not inside_loop:
                            self.constants[var] = result
                        optimized_tac.append(f"{var} = {result}")
                    except Exception:
                        optimized_tac.append(f"{var} = {' '.join(expr_parts)}")
                else:
                    # Keep partial propagation and update constants for direct assignments
                    if not inside_loop and len(expr_parts) == 1 and expr_parts[0].isdigit():
                        self.constants[var] = int(expr_parts[0])
                    else:
                        # Remove if not a constant
                        self.constants.pop(var, None)
                    optimized_tac.append(f"{var} = {' '.join(expr_parts)}")
            else:
                # Handle non-assignment lines (e.g., RETURN x)
                parts = line.split(" ")
                replaced_parts = [str(self.constants.get(part, part)) for part in parts]
                optimized_tac.append(" ".join(replaced_parts))

        return optimized_tac


    # Dead Code Elimination
    # Removes any code that unused / unreachable
    # ChatGPT helped me debug this as I was having variables be deleted 
    # despite being vital for the function of a loop, (i.e., "i" and such)
    def apply_dead_code_elimination(self, tac):
        used_vars = set()  # Variables used in the program
        referenced_labels = set()  # Labels referenced in control flow (goto)
        loop_dependent_vars = set()  # Variables that influence loop conditions or body
        optimized_tac = []  # Store optimized TAC
        label_positions = {}  # Track original label positions

        print("\n[DEBUG] Starting Dead Code Elimination...")

        # Step 1: Identify referenced labels and variables in control flow
        for i, line in enumerate(tac):
            print(f"[DEBUG] Processing Line {i}: {line}")
            if ":" in line and "goto" not in line:  # Label (e.g., L1:)
                label = line.split(":")[0]
                label_positions[label] = i
                print(f"[DEBUG] Found Label: {label}")
            elif "goto" in line:
                parts = line.split()
                if "if" in parts:  # Conditional goto
                    condition_var = parts[1]  # Condition variable (e.g., t1)
                    used_vars.add(condition_var)
                    loop_dependent_vars.add(condition_var)
                    print(f"[DEBUG] Adding Conditional Variable to Used Vars: {condition_var}")
                target_label = parts[-1]
                referenced_labels.add(target_label)
                print(f"[DEBUG] Adding Referenced Label: {target_label}")

        # Step 2: Backward pass to find all used variables and retain control flow
        for line in reversed(tac):
            print(f"[DEBUG] Backward Processing Line: {line}")
            if ":" in line and "goto" not in line:  # Label (e.g., L2:)
                label = line.split(":")[0]
                if label in referenced_labels:
                    optimized_tac.insert(0, line)  # Retain labels
                    print(f"[DEBUG] Retaining Label: {label}")
                continue

            if "goto" in line:  # Goto statement (e.g., if t1 goto L2)
                parts = line.split()
                if "if" in parts:  # Conditional goto
                    condition_var = parts[1]  # Condition variable
                    used_vars.add(condition_var)
                    loop_dependent_vars.add(condition_var)
                    print(f"[DEBUG] Adding Conditional Variable to Used Vars: {condition_var}")
                target_label = parts[-1]
                referenced_labels.add(target_label)
                optimized_tac.insert(0, line)  # Retain the goto statement
                print(f"[DEBUG] Retaining Goto Statement: {line}")
                continue

            if " = " in line:  # Assignment statement
                var, expr = line.split(" = ", 1)
                expr_vars = expr.split(" ")

                # Mark variables as loop-dependent if they influence the loop
                if any(part in loop_dependent_vars for part in expr_vars) or var in loop_dependent_vars:
                    loop_dependent_vars.add(var)
                    loop_dependent_vars.update(part for part in expr_vars if part.isidentifier())
                    used_vars.add(var)
                    used_vars.update(part for part in expr_vars if part.isidentifier())
                    optimized_tac.insert(0, line)  # Retain assignment
                    print(f"[DEBUG] Retaining Loop-Dependent Assignment: {line}")
                    continue

                # Retain assignments that are otherwise used
                if var in used_vars or any(part in used_vars for part in expr_vars):
                    used_vars.add(var)
                    used_vars.update(part for part in expr_vars if part.isidentifier())
                    optimized_tac.insert(0, line)  # Retain assignment
                    print(f"[DEBUG] Retaining Relevant Assignment: {line}")
                else:
                    print(f"[DEBUG] Removing Unused Assignment: {line}")
                continue

            # Non-assignment lines (e.g., RETURN x)
            for part in line.split():
                if part.isidentifier():
                    used_vars.add(part)
                    print(f"[DEBUG] Adding Used Variable from Non-Assignment Line: {part}")
            optimized_tac.insert(0, line)  # Retain the line

        # Step 3: Ensure labels and control flow integrity
        for label, pos in label_positions.items():
            if label in referenced_labels and all(f"{label}:" not in line for line in optimized_tac):
                # Insert label at its original position if missing
                optimized_tac.insert(pos, f"{label}:")
                print(f"[DEBUG] Reinserting Missing Label: {label}")

        # Ensure "END" stays at the end and labels are not misplaced
        end_index = len(optimized_tac)
        for i, line in enumerate(optimized_tac):
            if "END" in line:
                end_index = i
                break

        # Place all misplaced labels before "END"
        labels_to_move = [line for line in optimized_tac[end_index:] if ":" in line and "goto" not in line]
        optimized_tac = [line for line in optimized_tac if line not in labels_to_move]
        optimized_tac = optimized_tac[:end_index] + labels_to_move + optimized_tac[end_index:]

        print("[DEBUG] Finished Dead Code Elimination.\n")
        return optimized_tac


    # Helper function to evaluate TAC expressions, used in constant folding and propagation
    def evaluate_expression(self, expr_parts):
        # Separate parts of the variable
        if len(expr_parts) == 1:  # Single constant value
            return int(expr_parts[0])  # Directly return the value
        elif len(expr_parts) == 3:  # Binary operation
            left = int(expr_parts[0])
            operator = expr_parts[1]
            right = int(expr_parts[2])

            # Evaluate the expression
            if operator == '+':
                return left + right
            elif operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                return left / right
            elif operator == '%':
                return left % right
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        else:
            raise ValueError(f"Unexpected expression format: {expr_parts}")

