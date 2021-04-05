#!/bin/bash

__fndr_cd__() {
  local dir
  dir=$(python3 -m datatools.tui.change_dir) && printf 'cd %q' "$dir"
}

# ALT-A - cd into the selected directory
bind '"\ea": "$(__fndr_cd__)\C-x\C-x\C-e\C-x\C-r\C-m\C-w"'
