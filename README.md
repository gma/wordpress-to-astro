WordPress to Astro
==================

This is a script that I wrote to convert the XML exported from WordPress into a new copy of the web site, running on [Astro].

I've only used it to convert a blog site to Astro, so the focus is on:

- converting the text of posts exported from WordPress into Markdown files in an Astro site, and 
- downloading any images used within those posts, preparing them for use in Astro

## Install

You'll need Python 3.10 or above installed. Then you can get the script running by entering the following commands:

```sh
python3 -m venv .venv      # creates a virtual environment
source .venv/bin/activate  # enables the virtual environment
```

Now we can install our dependencies:

```sh
pip install --upgrade pip
pip install pip-tools
pip-sync requirements.txt dev-requirements.txt
```

[Astro]: https://astro.build
