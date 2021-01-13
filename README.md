# swbf2_animation_unmunger

Python scripts for decompiling munged animations for SWBF(1+2) Classic.  

## Usage:

```-file``` \<input-zaabin-file\> : Path to .zaabin file

```-dest``` \<output-directory-path\> : Destination directory for resulting .msh files

```-applyto``` \<msh-file-name\>  : MSH file containing a model which the animations should be unmunged with respect to
This option is important because some models may have skeletons with things like roots and effectors, which are
filtered out by ZenAsset.

The script will search for a .anims and a .zafbin file of the same name in the same directory of the .zaabin file.
If a .anims file is not available, you can write your own, or supply a list of possible animation names:

```-names``` \<list\> \<of\> \<possible\> \<names\> 

If the script is unable to match the CRCs in the ```.zaabin``` file with the supplied names, the output files 
will be named with their hex representations.


## Credits:

Sleepkiller - for the ```msh_writer``` and ```msh_scene_write``` classes


## Todo:

- Rewrite in C++ for integration into swbf-unmunge

- Slick docs like [these](https://schlechtwetterfront.github.io/ze_filetypes/msh.html) for ```zaa_``` and ```zaf_``` 

