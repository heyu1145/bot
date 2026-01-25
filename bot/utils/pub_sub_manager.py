"""
publish and subscribe system manager
"""
from collections.abc import Callable
from utils.logger import get_logger

logger = get_logger(__name__)


class Event[T, A]:
    def __init__(self, msg: T, action_type: A) -> None:
        self.msg = msg
        self.action_type = action_type

    def message(self) -> T:
        """
        return the message of the event
        """
        return self.msg

    def action(self) -> A:
        """
        return the action type of the event
        """
        return self.action_type

class Channel[T, A]:
    def __init__(self) -> None:
        self.subs: list[Callable[[Event[T, A]], None]] = []
        self.once_subs:list[Callable[[Event[T, A]], None]] = []
        self.events: list[Event[T, A]] = []
        self._try_it_lock = False

    def emit(self, event: Event[T, A]) -> None:
        """
        emit a event for channel
        """
        self.events.append(event)
        self._try_it()

    def on(self, callback: Callable[[Event[T, A]], None]) -> None:
        """
        call the callback when a event coming
        """
        self.subs.append(callback)
        self._try_it()

    def once(self, callback: Callable[[Event[T, A]], None]) -> None:
        """
        call the callback disposable when a event coming
        """
        self.once_subs.append(callback)
        self._try_it()

    def remove(self, callback: Callable[[Event[T, A]], None]) -> None:
        """
        remove the callback from both on and once
        """
        if callback in self.subs:
            self.subs.remove(callback)

        if callback in self.once_subs:
            self.once_subs.remove(callback)

    def _try_it(self) -> None:
        if (not self.events
            or not self.subs
            or not self.once_subs
            or self._try_it_lock): return
        self._try_it_lock = True
        while len(self.events) > 0:
            event = self.events.pop(0)
            for sub in self.subs[:]:
                try:
                    sub(event)
                except Exception as e:
                    logger.exception("error while running callback: %s", e)
            for sub in self.once_subs[:]:
                try:
                    sub(event)
                except Exception as e:
                    logger.exception("error while running callback: %s", e)
                finally:
                    self.once_subs.remove(sub)

        self._try_it_lock = False

    def __len__(self) -> int:
        """
        len of all events
        """
        return len(self.events)

    def __bool__(self) -> bool:
        """
        has any subscribers
        """
        return len(self.subs) != 0 or len(self.once_subs) != 0

class PubSubManager:
    _channels: dict[str, Channel] = {}

    def push(self, name: str, channel: Channel) -> None:
        """
        push a channel to manager that everyone can see it
        ( warning! lost type hint )
        """
        self._channels[name] = channel

    def get(self, name: str) -> (Channel | None):
        """
        get a channel from manager
        ( warning! lost type hint, use cost to get type hint )
        """
        return self._channels.get(name)

    def remove(self, name: str) -> (Channel | None):
        """
        remove the channel when don't needed
        """
        if name in self._channels:
            return self._channels.pop(name)
