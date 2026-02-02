"""
publish and subscribe system manager
"""
from collections.abc import Callable
from typing import Protocol
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


class BasicChannel[T, A]:
    """
    the basic channel with message system
    complete the health manage by yourself
    """

    def __init__(self) -> None:
        self._subs: list[Callable[[Event[T, A]], None]] = []
        self._once_subs: list[Callable[[Event[T, A]], None]] = []
        self._events: list[Event[T, A]] = []
        self._try_it_lock = False

    def emit(self, event: Event[T, A]) -> None:
        """
        emit a event for channel
        """
        self._events.append(event)
        self._try_it()

    def on(self, callback: Callable[[Event[T, A]], None]) -> None:
        """
        call the callback when a event coming
        """
        self._subs.append(callback)
        self._try_it()

    def once(self, callback: Callable[[Event[T, A]], None]) -> None:
        """
        call the callback disposable when a event coming
        """
        self._once_subs.append(callback)
        self._try_it()

    def remove(self, callback: Callable[[Event[T, A]], None]) -> None:
        """
        remove the callback from both on and once
        """
        if callback in self._subs:
            self._subs.remove(callback)

        if callback in self._once_subs:
            self._once_subs.remove(callback)

    def _try_it(self) -> None:
        if self._try_it_lock:
            return
        self._try_it_lock = True
        while len(self._events) > 0:
            event = self._events.pop(0)
            for sub in self._subs[:]:
                try:
                    sub(event)
                except Exception as e:
                    logger.exception("error while running callback: %s", e)
            for sub in self._once_subs[:]:
                try:
                    sub(event)
                except Exception as e:
                    logger.exception("error while running callback: %s", e)
                finally:
                    self._once_subs.remove(sub)

        self._try_it_lock = False

    def __len__(self) -> int:
        """
        len of all subscribers
        """
        return len(self._subs) + len(self._once_subs)

    def __bool__(self) -> bool:
        """
        has any subscribers
        """
        return len(self) != 0


class ChannelLike(Protocol):
    """
    the channellike which needs have emit, on, once and remove
    """

    def emit(self, event: Event) -> None: ...
    def on(self, callback: Callable[[Event], None]) -> None: ...
    def once(self, callback: Callable[[Event], None]) -> None: ...
    def remove(self, callback: Callable[[Event], None]) -> None: ...


class PubSubManager:
    _channels: dict[str, ChannelLike] = {}

    def push(self, name: str, channel: ChannelLike) -> None:
        """
        push a channel to manager that everyone can see it
        ( warning! lost type hint )
        """
        self._channels.setdefault(name, channel)

    def get(self, name: str) -> (ChannelLike | None):
        """
        get a channel from manager
        ( warning! lost type hint, use cost to get type hint )
        """
        return self._channels.get(name)

    def remove(self, name: str) -> (ChannelLike | None):
        """
        remove the channel when don't needed
        """
        if name in self._channels:
            return self._channels.pop(name)

        return None

