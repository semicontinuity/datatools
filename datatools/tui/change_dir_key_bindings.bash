#!/bin/bash

__fndr_cd__() {
  local dir
  dir=$(python3 -m datatools.tui.change_dir) && printf 'cd %q' "$dir"
}

__fndr_widget__() {
  local selected="$(python3 -m datatools.tui.change_dir)"
  READLINE_LINE="${READLINE_LINE:0:$READLINE_POINT}$selected${READLINE_LINE:$READLINE_POINT}"
  READLINE_POINT=$(( READLINE_POINT + ${#selected} ))
}


# ALT-A - cd into the selected directory
bind '"\ea": "$(__fndr_cd__)\C-x\C-x\C-e\C-x\C-r\C-m\C-w"'
# CTRL-F: insert folder path to command line
bind -x '"\C-f": "__fndr_widget__"'
