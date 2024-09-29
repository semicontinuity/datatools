from typing import Dict, Optional


def channel_created(row: Dict) -> Optional[str]:
    method = row.get('method')
    payload = row.get('payload')
    if method == 'CreateChannel' and payload is not None:
        if (channel_info := payload.get('channelInfo')) is not None:
            if (channel_id := channel_info.get('channelId')) is not None:
                return channel_id


def channel_deleted(row: Dict) -> Optional[str]:
    method = row.get('method')
    payload = row.get('payload')
    if method=='CloseChannel' and payload is not None:
        if (channel_id := payload.get('channelId')) is not None:
            return channel_id


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
