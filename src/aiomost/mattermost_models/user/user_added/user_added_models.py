import json
from aiomost.mattermost_models.base_model.base_model import BaseModel


class Broadcast(BaseModel):
    def __init__(self, omit_users, user_id, channel_id, team_id, connection_id, omit_connection_id):
        self.omit_users = omit_users
        self.user_id = user_id
        self.channel_id = channel_id
        self.team_id = team_id
        self.connection_id = connection_id
        self.omit_connection_id = omit_connection_id


class UserAdded(BaseModel):
    def __init__(self, team_id, user_id):
        self.team_id = team_id
        self.user_id = user_id


class UserAddedEvent(BaseModel):
    def __init__(self, event, data, broadcast, seq):
        self.event = event
        self.data = UserAdded(**data) if isinstance(data, dict) else data
        self.broadcast = Broadcast(
            **broadcast) if isinstance(broadcast, dict) else broadcast
        self.seq = seq

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False, separators=(',', ':'))
