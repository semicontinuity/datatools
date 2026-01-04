#### Running

* Arg: folder
* Env var `NAME_PATTERN`

#### Keyboard

* `Delete`: delete current folder
* `Alt+Delete`: un-mark current folder
* `Alt+Insert`: mark current folder

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

