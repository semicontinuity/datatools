from datatools.intent.handler_json import process_json
from datatools.intent.handler_json_lines import handle_json_lines
from datatools.intent.handler_multipart import handle_multipart
from datatools.intent.handler_send_entity import handler_send_entity
from datatools.intent.targets import to_clipboard, write_temp_file, browse_new_tab, open_in_idea, html_to_browser, \
    open_in_browser
from datatools.tui.popup_selector import choose


def dispatch(headers, post_body):
    content_type = headers.get('Content-Type')
    mime_type = content_type.split(';')[0]
    print('mime_type ' + mime_type)
    the_title = headers.get('X-Title')
    match mime_type:
        case 'multipart/form-data':
            handle_multipart(post_body, content_type)
        case 'text/uri-list':
            browse_new_tab(post_body.decode('utf-8'))
        case 'text/plain':
            match choose(["Copy to Clipboard", "Open in Browser"], 'Choose'):
                case 0:
                    to_clipboard(post_body)
                case 1:
                    browse_new_tab(
                        write_temp_file(post_body, '.txt', the_title)
                    )
        case 'text/markdown':
            match choose(["Copy to Clipboard", "Open in IDEA"], 'Choose'):
                case 0:
                    to_clipboard(post_body)
                case 1:
                    open_in_idea(
                        write_temp_file(post_body, '.md', the_title)
                    )
        case 'text/html':
            html_to_browser(post_body, the_title)
        case 'image/svg+xml':
            open_in_browser(post_body, file_suffix='.svg', title=the_title)
        case 'application/x-basic-entity':
            realm_ctx = headers.get('X-Realm-Ctx')
            realm_ctx_dir = headers.get('X-Realm-Ctx-Dir')
            handler_send_entity.send_entity(
                realm_ctx, realm_ctx_dir, post_body
            )
        case 'application/sql':
            match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                case 0:
                    to_clipboard(post_body)
                case 1:
                    browse_new_tab(
                        write_temp_file(post_body, '.sql.txt', the_title)
                    )
        case 'application/json-lines':
            handle_json_lines(post_body, the_title)
        case 'application/json':
            process_json(post_body, the_title)
