# Documentation

One way to get involved with the project is to add and improve the
documentation of the project. As the Community grows, the numbers of people
who will be attending, the number of events, and the overall activity on the
Platform is expected to grow. Clear and concise documentation ensures that the
team is able to effectively communicate how the Platform should be used to the
respective audience.

As you can see, a part of the documentation is meant for volunteers who
actively manage events and such in the Community and the rest of the
documentation is oriented meant for the rest of the Community e.g. event
participants. Please keep this in mind when adding or improving the
documentation.

The documentation is built from [Markdown](https://www.markdownguide.org/)
files in the [fossunited GitHub](https://github.com/fossunited/fossunited/tree/develop/docs)
repository. The documentation is built using the [MkDocs](https://www.mkdocs.org/)
Python project and uses the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
and the [MkDocs GLightbox](https://squidfunk.github.io/mkdocs-material/)
plugins. Every time changes are made in the `develop` branch to the `docs/*`
folder on the Git repository, a [GitHub Action](https://github.com/fossunited/fossunited/blob/develop/.github/workflows/docs.yml)
gets triggered, which builds and pushes the documentation to the `gh-pages`
branch, to be served using [GitHub pages](https://docs.github.com/en/pages).
