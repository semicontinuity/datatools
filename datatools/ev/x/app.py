#!/usr/bin/env python3
import os

import datatools.ev.x.ch.app as ch_app
import datatools.ev.x.http.app as http_app

if __name__ == "__main__":
    if os.environ.get('YC_CH_DATABASE'):
        ch_app.main()
    elif os.environ.get('PROTOCOL'):
        http_app.main()
