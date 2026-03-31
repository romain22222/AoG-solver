from constraints.base import Constraint, GridSymbol
from regionHelper import joinRegions, separateRegions


class SolitudeConstraint(Constraint):
    def __init__(self):
        super().__init__()
        self.all_symbols = []

    def set_symbols(self, constraints: list[Constraint]) -> None:
        symbols = []
        for constraint in constraints:
            hasattr(constraint, 'symbols') and symbols.extend(constraint.symbols)
        self.all_symbols = symbols

    def propagate(self, state) -> bool:
        region_symbols = {}
        for symbol in self.all_symbols:
            region_id = state.uf.find(symbol.position)
            if region_id not in region_symbols:
                region_symbols[region_id] = symbol
            else:
                return False
        for region_id in state.uf.parentList:
            region_has_symbol = region_id in region_symbols
            symbol_count = 1 if region_has_symbol else 0
            connectables = state.uf.connectables[region_id]
            
            if len(connectables) == 0:
                if symbol_count != 1:
                    return False
            elif symbol_count == 0:
                connectable = next(iter(connectables))
                if not joinRegions(state, region_id, connectable):
                    return False
                return self.propagate(state)
            else:
                for connectable in connectables:
                    if connectable in region_symbols[region_id]:
                        if not separateRegions(state, region_id, connectable):
                            return False

        return True
