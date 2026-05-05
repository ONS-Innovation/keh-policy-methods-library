# Policy Methods Library

The Policy Methods Library is a collection of reusable methods that can be used to implement various policy-related functionalities. These methods are designed to be flexible and adaptable to different use cases, allowing developers to easily integrate them into their applications.

The library includes a series of methods to evaluate ONS' GitHub Usage Policy, which outlines the acceptable use of GitHub within the organisation. These methods can be used to check for compliance with the policy, identify potential violations, and provide guidance on how to address any issues that may arise.

## Getting Started

For detailed documentation on how to use the Policy Methods Library, or how to contribute to the project, please refer to the project's `README` at the root of the repository.

The README covers how to use the library, how to contribute to the project, and how to set up the development environment.
This documentation (`/docs`) provides more detailed information on the project, including an overview of the tech stack, details on implementation choices, and more.

## Aims of the Policy Methods Library

The Policy Methods Library aims to:

- Provide a centralised collection of methods for implementing policy-related functionalities, particularly around checking adherence to the GitHub Usage Policy within ONS.
- Encapsulate business logic related to policy adherence in a reusable way, allowing for consistent implementation across different applications and services.
- Facilitate easier maintenance and updates to policy-related logic by centralising it within a single library, rather than having it scattered across multiple codebases.
- Encourage best practices in software development by providing well-documented and tested methods that can be easily integrated into various projects.

## Tech Stack

- Python (`3.12+`): The primary programming language used for the library. The primary language within ONS and KEH.
- Poetry: Used for dependency management and packaging of the library.
- MkDocs: Used for building the documentation site.
- GitHub Actions: Used for CI/CD, including running tests, linting, and deploying documentation to GitHub Pages.
- Markdownlint: Used for linting Markdown files in the documentation.
- MegaLinter: Used for linting the codebase. Used as a "catch-all" linter.
- Ruff + MyPy: Used for linting and type checking the Python codebase. Used as the primary linters for the Python code, with MegaLinter as a secondary "catch-all" linter.

## Documentation Structure

The documentation is separated into areas of functionality, with the aim of making it easy for users to find the information they need.

```bash
docs/
├── index.md                    # This file.
├── documentation.md            # A guide on how the project documentation is structured (what to document in the README vs in the documentation, and why).
├── implementation_examples.md  # Some examples of how to implement the methods defined in the library, including example code snippets and explanations.
│
├── github/
│   ├── overview.md             # An overview of the GitHub-related methods defined in the library, including their purpose and how they fit into the overall library.
│   ├── clients.md              # Documentation on the GitHub API clients defined in the library, including how to use them and implementation details.
│   └── auth.md                 # Documentation on the authentication methods for the GitHub API defined in the library, including how to use them and implementation details.
│
├── checks/
│   ├── overview.md             # An overview of the checks defined in the library, including their purpose and how they fit into the overall library.
│   └── <specific_check>.md     # Documentation on specific checks defined in the library, including how to use them and implementation details.
│
├── dev_guides/
│   ├── ...                     # Any miscellaneous guides for developers working on the project, such as how to add new checks and what considerations to take into account when doing so.
└──
```
