# Helper Utilities (Internal)

This library includes a set of internal helper utilities that are used by the checks to perform common tasks, such as retrieving repository details from GitHub.
These utilities are available in the `policy_methods_library/utils` package and are intended for internal use within the library.

Due to their internal use, these utilities are not part of the public API and may change without notice. Users of the library should not rely on these utilities directly, but rather use the checks provided by the library. The utilities are not documented since they are intended for internal use only. Documentation for these utilities is available via docstrings and comments within the codebase.

Current utilities include:

- `get_details.py`: Contains methods for retrieving repository details from GitHub.
- `get_contents.py`: Contains methods for retrieving the contents of a repository from GitHub. This is commonly used in the checks to verify the presence of specific files or directories (i.e. `pirr.md`).
- `pagination.py`: Contains logic for handling GitHub API pagination. Abstracts the complexity of following pagination links to fetch all results across multiple pages.
- `organisation.py`: Contains methods for verifying that the authenticated client is an organisation (not an individual user). Used by checks that require organisation-level access to GitHub APIs.
