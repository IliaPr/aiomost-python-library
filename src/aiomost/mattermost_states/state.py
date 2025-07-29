from aiomost.mattermost_state_storage.matter_states import State, StatesGroup


class UserStates(StatesGroup):
    """
    Класс, определяющий состояния пользователя.
    """
    TEST_STATE = State()  # Состояние test_state, имя будет TEST_STATE
    TEST_STATE2 = State()  # Состояние test_state2, имя будет TEST_STATE2
