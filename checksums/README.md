# File integrity check

This package helps computing and validating file checksums in a format that is
compatible with POSIX file checksum utilities (such es `md5sum`, `sha512sum`,
etc.)

## Installation

In the directory with the `setup.py`.

```bash
pip install .
```

Now `checksums` command should be available. If not:

- Try installing with `sudo` to make sure that it is added to `/usr/bin`, which
  should be in the `PATH`.
- Or add it to the path manually (it is likely to be installed in
  `~/.local/share/bin/`).

If still does not work, give up and substitute `checksums` with
`python -m checksums.cli`.

## Usage

### Compute checksums

Compute SHA512 checksums for all files in the folder (but do not traverse into
sub-folders) and print them to the standard output.

```bash
checksums compute '*'
```

Note the mandatory use of single quotes around the glob pattern. This is needed,
so that the glob expansion is delegated to the Python script rather than the
shell itself. I.e., if you run `checksums compute *`, the asterisks will be
substituted with the directory contents and the actual command invoked will be
something like `checksums compute dir1 dir2 file1 file2`. This is not the format
that the script expects.

Specify a different hashing algorithm:

```bash
checksums compute --algorithm=md5 '*'
```

Change logging level and save logs to a file:

```bash
checksums compute --log-level DEBUG --log-file checksums.log '*'
```

Traverse all sub-directories recursively and compute checksums for files in
these sub-directories too (not the double asterisk):

```bash
checksums compute -r '**'
```

Compute hashes for all JPEGs in the directory and its sub-directories:

```bash
checksums compute -r '**/*.jpeg,**/*.JPEG,**/*.jpg,**/*.JPG'
```

Save checksums to a file:

```bash
checksums compute '*' > .checksums.sha512
```

Using hidden files (starting with dots) is useful, so that it does not attempt
to compute a hash for the files with checksums.

#### Using POSIX utilities

`sha512sum *` should be equivalent (except for commented out metadata and some
special cases) to `checksums compute '*'`.

Playing around with `find` options in the command below, it should be possible
to achieve all teh functionality as above. 

E.g., the following 2 command are equivalent

```bash
find -type f -exec sha512sum {} +
checksums compute -r '**'
```

and these are equivalent too:

```bash
find **/*.jpeg -type f -exec sha512sum {} +
checksums compute -r '**/*.jpeg'
```

### Validate checksums

Validate checksums of the file in `.checksums.sha512`:

```bash
checksums check --algorithm SHA512 .checksums.sha512
```

#### Using POSIX utilities

The same functionality (although with different output) cane be obtained using
`sha512sum`, `md5sum`, etc.:

```bash
sha512sum --check .checksums.sha512
```

or if we want to see errors only:

```bash
sha512sum --quiet --check .checksums.sha512
```
