from typing import Dict, Optional, Tuple


def channel_created(row: Dict) -> Optional[str]:
    method = row.get('method')
    payload = row.get('payload')
    if method == 'CreateChannel' and payload is not None:
        if (channel_info := payload.get('channelInfo')) is not None:
            if (channel_id := channel_info.get('channelId')) is not None:
                return channel_id


def channel_deleted(row: Dict) -> Optional[str]:
    method = row.get('method')
    if method == 'CloseChannel' and (payload := row.get('payload')) is not None:
        if (channel_id := payload.get('channelId')) is not None:
            return channel_id
    elif method == 'ReceiveRoomEvents' and row.get('msg') == 'Removing closed channel':
        if (channel_id := row.get('channelID')) is not None:
            return channel_id


def channel_use(row: Dict) -> Optional[Tuple[str, str]]:
    channel_id = used_channel_id(row)
    if channel_id is None:
        return None
    return channel_id, used_channel_icon(row)


def used_channel_id(row: Dict) -> Optional[str]:
    if (payload := row.get('payload')) is not None:
        if (info := payload.get('info')) is not None:
            if (channel_id := info.get('channelId')) is not None:
                return channel_id
        elif (channel_info := payload.get('channelInfo')) is not None:
            if (channel_id := channel_info.get('channelId')) is not None:
                return channel_id
        elif (event := payload.get('event')) is not None:
            if (channel_event := event.get('channelEvent')) is not None:
                if (channel_id := channel_event.get('channelId')) is not None:
                    return channel_id


def used_channel_icon(row: Dict) -> str:
    if row.get('method') == 'ReceiveRoomEvents':
        return '◀'
    elif row.get('method') is not None:
        return '▶'
    else:
        return '?'


def channel_color(channel_id: str) -> str:
    if channel_id.startswith('sip://'):
        return 'darkblue'
    elif channel_id.startswith('recording://'):
        return 'darkred'
    elif channel_id.startswith('s3://'):
        return 'darkgreen'
    elif channel_id.startswith('sk://'):
        return 'gold'
    elif channel_id.startswith('tg://'):
        return 'gray'


def channel_event_type(row: Dict) -> Optional[str]:
    if (payload := row.get('payload')) is not None:
        if (event := payload.get('event')) is not None:
            if (channel_event := event.get('channelEvent')) is not None:
                if (event2 := channel_event.get('event')) is not None:
                    if (event2.get('commandCompleted')) is not None:
                        return 'commandCompleted'
                    elif (event2.get('channelAppendedEvent')) is not None:
                        return 'channelAppendedEvent'
                    elif (event2.get('closed')) is not None:
                        return 'closed'
                    else:
                        return 'event'
