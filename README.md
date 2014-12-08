MACH
====

first:

```python
import mach
```

then:

```python
struct = mach.utils.preprocess.Structure('./mach/data/feed/article1777.txt')
mach.functions.clavin_geoparse(struct) # gets and tags named geographical entities
mach.functions.freebase_query(struct) # gets and tags all entities it can guess
```

even simpler now:

```python
struct = mach.utils.preprocess.Structure('./mach/data/feed/article1777.txt')
mach.main.run(struct)
```

or, finally (it just can't get easier):

``` python
struct = mach.main.run('./mach/data/feed/article1777.txt')
```

struct is a class that wraps a text and offers various utilities for accessing parts of it, and tagging it. Sooner it will include a rdfa() feature to transform the tags into rdfa-parseable stuff.
