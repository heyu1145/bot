"""
the wrapper of channel for duplex data
"""
from collections.abc import Callable
from typing import Self, cast
from pub_sub_manager import Event, Channel, PubSubManager

pub_sub = PubSubManager()


class DuplexChannel[T, A]:
    def __init__(self, name: str) -> None:
        self.name = name
        client = pub_sub.get(f'{name}:client')
        if not client:
            self.client_to_server: Channel[T, A] = Channel[T, A]()
            pub_sub.push(f'{name}:client', self.client_to_server)
        else:
            self.client_to_server = cast(Channel[T, A], client)

        server = pub_sub.get(f'{name}:server')
        if not server:
            self.server_to_client: Channel[T, A] = Channel[T, A]()
            pub_sub.push(f'{name}:server', self.server_to_client)
        else:
            self.server_to_client = cast(Channel[T, A], server)

    def server_emit(self, event: Event[T, A]) -> None:
        self.server_to_client.emit(event)

    def server_on(self, callback: Callable[[Event[T, A]], None]) -> None:
        self.client_to_server.on(callback)

    def server_once(self, callback: Callable[[Event[T, A]], None]) -> None:
        self.client_to_server.once(callback)

    def server_remove(self, callback: Callable[[Event[T, A]], None]) -> None:
        self.client_to_server.remove(callback)

    def client_emit(self, event: Event[T, A]) -> None:
        return self.client_to_server.emit(event)

    def client_on(self, callback: Callable[[Event[T, A]], None]) -> None:
        self.server_to_client.on(callback)

    def client_once(self, callback: Callable[[Event[T, A]], None]) -> None:
        self.server_to_client.once(callback)

    def client_remove(self, callback: Callable[[Event[T, A]], None]) -> None:
        self.server_to_client.remove(callback)

    def remove(self) -> None:
        """
        remove the channel from manager
        ( warning! after remove, this channel no longer support to be find from manager )
        """
        pub_sub.remove(f'{self.name}:client')
        pub_sub.remove(f'{self.name}:server')

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.remove()
        _ = args, kwargs

    def __del__(self) -> None:
        try:
            self.remove()  # need to remove after delete for memory/direct del
        except:
            pass  # failed? just do nothing because we can't to anything even raise
