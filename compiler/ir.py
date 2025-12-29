class IRConst:
    """Konstante Literalwerte im IR."""
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"IRConst({self.value!r})"


class IRTemp:
    """Temporärer Wert, der Ergebnis einer Instruktion sein kann."""
    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"IRTemp({self.name})"


class IRInstruction:
    """
    Eine IR-Instruction mit:
      - opcode: str (z.B. "add", "jump_if_false", "make_iter")
      - operands: Liste aus IRConst / IRTemp / Strings (z.B. Variablennamen, Labelnamen)
      - result: IRTemp oder None

    Beispiele:
      IRInstruction("load_const", [IRConst(42)], result=%t0)
      IRInstruction("jump_if_false", [%t0, "Lend"])
    """
    __slots__ = ("opcode", "operands", "result")

    def __init__(self, opcode: str, operands=None, result=None):
        self.opcode = opcode
        self.operands = operands or []
        self.result = result  # IRTemp oder None

    def __repr__(self):
        base = f"{self.opcode}(" + ", ".join(repr(o) for o in self.operands) + ")"
        if self.result is not None:
            return f"{self.result} = {base}"
        return base


class IRBlock:
    """Ein Basic Block mit einer Folge von IRInstructions."""
    __slots__ = ("name", "instructions")

    def __init__(self, name: str):
        self.name = name
        self.instructions = []

    def add(self, instr: IRInstruction):
        self.instructions.append(instr)

    def __repr__(self):
        lines = [f"{self.name}:"]
        for instr in self.instructions:
            lines.append(f"  {instr}")
        return "\n".join(lines)


class IRFunction:
    """
    Repräsentiert eine Funktion:
      - name: Funktionsname
      - params: Parameterliste (Strings)
      - blocks: Liste von IRBlocks
      - temps: Zähler für temporäre Werte
    """
    __slots__ = ("name", "params", "blocks", "_temp_counter")

    def __init__(self, name: str, params=None):
        self.name = name
        self.params = params or []
        self.blocks = []
        self._temp_counter = 0

    def new_block(self, name: str) -> IRBlock:
        block = IRBlock(name)
        self.blocks.append(block)
        return block

    def new_temp(self) -> IRTemp:
        name = f"%t{self._temp_counter}"
        self._temp_counter += 1
        return IRTemp(name)

    def __repr__(self):
        lines = [f"func {self.name}({', '.join(self.params)})"]
        for block in self.blocks:
            lines.append(repr(block))
        return "\n".join(lines)


class IRModule:
    """
    Sammlung von IRFunctions.
    """
    __slots__ = ("name", "functions")

    def __init__(self, name: str):
        self.name = name
        self.functions = []

    def add_function(self, func: IRFunction):
        self.functions.append(func)

    def __repr__(self):
        lines = [f"module {self.name}"]
        for f in self.functions:
            lines.append(repr(f))
        return "\n\n".join(lines)
