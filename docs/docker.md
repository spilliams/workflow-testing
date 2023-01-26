# Docker goals

1. only run the build/push if something in the image recipe changes
2. reuse as much previously-built container as possible
3. handle the chicken-egg intelligently. Downstream jobs should use the latest thing we have available, and if that latest thing has to be built, the downstream should wait until the build is done.
4. clean up after a closed branch

Currently we generate our own tags for a build. We generate:

- commit-SHA
- branch-BRANCH
- latest (if we're on `main`)

We also generate a list of tags to cache *from* (however, without caching *to* these beforehand, they're useless):

- commit-SHA (10 of the most recent)
- branch-BRANCH (some recent ones if we're on main?)
- latest (always)

Having access to all the `commit-SHA` tags is nice, because it lets us cache from them (when building a new commit on a feature branch). Same goes for all the branch tags (when we're building a new latest on `main`).
