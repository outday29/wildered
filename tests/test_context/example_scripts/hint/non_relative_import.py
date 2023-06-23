from aggregate_hint import dummy_function_1
import wildered

@wildered.hint([dummy_function_1])
@wildered.autocomplete()
def ok():
    pass
