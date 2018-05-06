# perkeeppy

**perkeeppy** is a library for interacting with the HTTP API of a Perkeep server from Python 3.

This library provides an interface for interacting with API endpoints that the [Perkeep](https://perkeep.org/) (previously called Camlistore)  daemon exposes. It supports the basic operations, such as put/get, as well as some higher level APIs, such as the signing helper.

## Background ##
This library is based on the earlier work of Martin Atkins – the [camlistore](https://pypi.org/project/camlistore/) ([repository](https://github.com/apparentlymart/python-camlistore)) library. *perkeeppy* updates the original library to Python 3. It also adds extra functionality for uploading schema blobs, using the signing endpoint, and using the unofficial upload helper. 

## Installation ##

Install with `pip`:

```shellsession
$ pip install .
```

## Usage ##
Generally, you will want to obtain a connection first. Currently, only localhost authentication is supported.

```Python
import perkeeppy

conn = perkeeppy.connect('http://localhost:3179')  # Use the base URL for the Perkeep server

my_blob = perkeeppy.Blob(b'Hello, world!')  # Blobs carry bytes
blobref = conn.blobs.put(my_blob)

received_blob = conn.blob_root.get(blobref)
print(f'{received_blob.blobref}: {received_blob.data.decode()}')
```

### Documentation ###
Documentation uses Sphinx. You can have `setup.py` build it:

```shellsession
$ python setup.py build_sphinx
```

The rendered HTML files will be in `docs/build/html`, with the index at `docs/build/html/index.html`.

## Project ##
You can find the project repository at [github.com/DeeUnderscore/perkeeppy](https://github.com/DeeUnderscore/perkeeppy).

This library is licensed under the MIT license. For details, see [LICENSE](/LICENSE).