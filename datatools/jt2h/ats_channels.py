from typing import Dict, Optional, Tuple


def channel_created(row: Dict) -> Optional[str]:
    if row.get('method') == 'CreateChannel':
        if (payload := row.get('payload')) is not None:
            if (channel_info := payload.get('channelInfo')) is not None:
                if (channel_id := channel_info.get('channelId')) is not None:
                    return channel_id


def channel_deleted(row: Dict) -> Optional[str]:
    if (payload := row.get('payload')) is not None:
        if (event := payload.get('event')) is not None:
            if (channel_event := event.get('channelEvent')) is not None:
                if (event2 := channel_event.get('event')) is not None:
                    if (event2.get('closed')) is not None:
                        return channel_event.get('channelId')


def channel_use(row: Dict) -> Optional[Tuple[str, str]]:
    channel_id = used_channel_id(row)
    if channel_id is None:
        return None
    return channel_id, used_channel_icon(row)


def used_channel_id(row: Dict) -> Optional[str]:
    if (channel_id := row.get('channelID')) is not None:
        return channel_id
    elif (payload := row.get('payload')) is not None:
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
            elif (channel_appended := event.get('channelAppended')) is not None:
                if (channel := channel_appended.get('channel')) is not None:
                    if (channel_id := channel.get('channelId')) is not None:
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
        return 'deepskyblue'
    elif channel_id.startswith('recording://'):
        return 'darkred'
    elif channel_id.startswith('s3://'):
        return 'green'
    elif channel_id.startswith('sk://'):
        return '#c0c000'
    elif channel_id.startswith('tg://'):
        return 'gray'


def channel_event_type(row: Dict) -> Optional[str]:
    if (payload := row.get('payload')) is not None:
        if (payload.get('channelInfo')) is not None:
            return 'created'
        elif (event := payload.get('event')) is not None:
            if (channel_event := event.get('channelEvent')) is not None:
                if (event2 := channel_event.get('event')) is not None:
                    if (event2.get('commandCompleted')) is not None:
                        return 'commandCompleted'
                    elif (event2.get('channelAppendedEvent')) is not None:
                        return 'channelAppendedEvent'
                    elif (event2.get('closed')) is not None:
                        return 'closed'
                    elif (event2.get('speechkitChannelEvent')) is not None:
                        return 'speechkitChannelEvent'
                    else:
                        return 'connected?'
            elif (event.get('channelAppended')) is not None:
                return 'channelAppended'
