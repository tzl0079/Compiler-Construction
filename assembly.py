# Author: Thomas Lander
# Date: 12/12/24
# assembly.py

class TACtoAssemblyConverter:
    def __init__(self, tac):
        self.tac = tac
        self.registers = ["eax", "ebx", "ecx", "edx"]
        self.register_map = {}
        self.assembly_code = []

    # Allocate a register for a variable, if not already mapped
    def allocate_register(self, var):
        if var not in self.register_map:
            for reg in self.registers:
                if reg not in self.register_map.values():
                    self.register_map[var] = reg
                    return reg
            raise Exception("No free registers available.")
        return self.register_map[var]

    # Clearing a register when a variable is no longer needed
    def free_register(self, var):
        if var in self.register_map:
            del self.register_map[var]

    # Converst TAC to x86
    def convert(self):
        for line in self.tac:
            if " = " in line:
                var, expr = line.split(" = ", 1)
                expr_parts = expr.split()

                # Assignments / Constants
                if len(expr_parts) == 1:
                    if expr_parts[0].isdigit():
                        reg = self.allocate_register(var)
                        self.assembly_code.append(f"mov {reg}, {expr_parts[0]}")
                    else:
                        src_reg = self.allocate_register(expr_parts[0])
                        dest_reg = self.allocate_register(var)
                        self.assembly_code.append(f"mov {dest_reg}, {src_reg}")

                # Binary Operations
                elif len(expr_parts) == 3: 
                    left, op, right = expr_parts
                    left_reg = self.allocate_register(left)

                    if right.isdigit():
                        temp_reg = self.allocate_register(var)
                        self.assembly_code.append(f"mov {temp_reg}, {left_reg}")
                        if op == "+":
                            self.assembly_code.append(f"add {temp_reg}, {right}")
                        elif op == "-":
                            self.assembly_code.append(f"sub {temp_reg}, {right}")
                        elif op == "*":
                            self.assembly_code.append(f"imul {temp_reg}, {right}")
                        elif op == "/":
                            self.assembly_code.append(f"mov edx, 0")  # Clear edx for division
                            self.assembly_code.append(f"mov eax, {left_reg}")
                            self.assembly_code.append(f"div {right}")
                            self.assembly_code.append(f"mov {temp_reg}, eax")
                        elif op == "%":
                            self.assembly_code.append(f"mov edx, 0")  # Clear edx for division
                            self.assembly_code.append(f"mov eax, {left_reg}")
                            self.assembly_code.append(f"div {right}")
                            self.assembly_code.append(f"mov {temp_reg}, edx")  # Remainder in edx
                        #else:
                            #raise Exception(f"Unsupported operator: {op}")

                    # If the right-hand operand is a variable
                    else: 
                        right_reg = self.allocate_register(right)
                        temp_reg = self.allocate_register(var)
                        self.assembly_code.append(f"mov {temp_reg}, {left_reg}")
                        if op == "+":
                            self.assembly_code.append(f"add {temp_reg}, {right_reg}")
                        elif op == "-":
                            self.assembly_code.append(f"sub {temp_reg}, {right_reg}")
                        elif op == "*":
                            self.assembly_code.append(f"imul {temp_reg}, {right_reg}")
                        elif op == "/":
                            self.assembly_code.append(f"mov edx, 0")  # Clear edx for division
                            self.assembly_code.append(f"mov eax, {left_reg}")
                            self.assembly_code.append(f"div {right_reg}")
                            self.assembly_code.append(f"mov {temp_reg}, eax")
                        elif op == "%":
                            self.assembly_code.append(f"mov edx, 0")  # Clear edx for division
                            self.assembly_code.append(f"mov eax, {left_reg}")
                            self.assembly_code.append(f"div {right_reg}")
                            self.assembly_code.append(f"mov {temp_reg}, edx")  # Remainder stored in edx
                        elif op == ">":
                            self.assembly_code.append(f"cmp {left_reg}, {right_reg}")
                            self.assembly_code.append(f"setg {temp_reg}")  # Set if greater 
                        elif op == "<":
                            self.assembly_code.append(f"cmp {left_reg}, {right_reg}")
                            self.assembly_code.append(f"setl {temp_reg}")  # Set if less
                        else:
                            raise Exception(f"Unsupported operator: {op}")

            elif "goto" in line:  # Jump statement
                if "if" in line:
                    condition, target = line.split(" goto ", 1)
                    cond_var = condition.split()[1]
                    reg = self.allocate_register(cond_var)
                    self.assembly_code.append(f"cmp {reg}, 0")
                    self.assembly_code.append(f"jne {target}")
                else:
                    label = line.split()[1]
                    self.assembly_code.append(f"jmp {label}")

            elif ":" in line:  # Label
                label = line.split(":")[0]
                self.assembly_code.append(f"{label}:")

            elif "RETURN" in line:  # Return statement
                var = line.split()[1]
                if var.isdigit():  # Handle constant returns
                    self.assembly_code.append(f"mov eax, {var}")
                else:
                    reg = self.allocate_register(var)
                    self.assembly_code.append(f"mov eax, {reg}")
                self.assembly_code.append("ret")

        return "\n".join(self.assembly_code)
