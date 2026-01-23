#### Running

* Arg: folder
* Env var `NAME_PATTERN`

#### Keyboard

* `Delete`: delete current folder
* `Alt+Delete`: un-mark current folder
* `Alt+Insert`: mark current folder
* `Shift+Tab`: collapse current branch (top-level folder containing current node)

#### Folder Attributes

Extended attributes can be used to control folder behavior:

* `user.collapsed`: Folders with this attribute are automatically collapsed when the UI is initialized
* `user.hidden`: Folders with this attribute are completely hidden from the tree view
* `user.deleted`: Folders with this attribute are displayed with strike-through formatting

Set attributes using: `setfattr -n user.attribute_name -v "1" folder_path`
Remove attributes using: `setfattr -x user.attribute_name folder_path`

#### Coloring

Using permission bits for coloring:
* Values 0-7 of group permissions correspond to color 0-7
  * Overrides:
    * Sticky bit set: green
    * SGID bit set: yellow
    * SUID bit set: red
* Bit Read(Others) selects bright colors
* Bit Write(Others) selects italic font 
* Bit Execute(Others) selects bold font

