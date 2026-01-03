#### Running

* Arg: folder
* Env var `NAME_PATTERN`


#### Coloring

Using permission bits for coloring:
* Values 0-7 of group permissions correspond to color 0-7
* Bit Read(Others) selects bright colors
* Bit Write(Others) selects italic font 
* Bit Execute(Others) selects bold font

Overrides:
* Sticky bit set: green
* SGID bit set: yellow
* SUID bit set: red
