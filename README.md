# KEH Policy Methods Library

The Policy Methods Library is a collection of functions to encapsulate the business logic when it comes checking policy adherence to the GitHub Usage Policy within ONS.

## Table of Contents

- [KEH Policy Methods Library](#keh-policy-methods-library)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Makefile](#makefile)
  - [Using the Package](#using-the-package)
  - [Package Structure](#package-structure)
  - [Deployment](#deployment)
  - [Documentation](#documentation)
    - [GitHub Actions for Documentation](#github-actions-for-documentation)
    - [Local Development of Documentation](#local-development-of-documentation)
  - [Linting and Testing](#linting-and-testing)
    - [GitHub Actions](#github-actions)
    - [Running Tests and Linters Locally](#running-tests-and-linters-locally)
      - [Primary Language](#primary-language)
      - [MegaLinter](#megalinter)
      - [Documentation linting and building](#documentation-linting-and-building)

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management
- Node.js and npm for documentation linting (Markdownlint)

## Makefile

This project uses a Makefile to simplify common tasks.
To see the available commands, run:

```bash
make help
```

## Using the Package

TODO: Add instructions for how to use the package in other repositories, including how to install it as a dependency and import the functions.

## Package Structure

```bash
src/
└── policy_methods_library/
   ├── checks/                # Core business logic for checking policy adherence.
   │   ├── __init__.py
   │   └── ...                # files for each specific check
   │
   ├── github/                # GitHub API integrations.
   │   ├── __init__.py
   │   ├── auth.py            # Functions to handle authentication with the GitHub API.
   │   └── rest_client.py     # Client for making REST API calls to GitHub.
   │
   └── __init__.py            # Init file for the package.
```

Further documentation can be found within the `docs` directory.

## Deployment

The package can be deployed to GitHub Releases using the GitHub Actions workflow defined in `.github/workflows/publish-release.yml`.

This workflow is triggered on pushes to tags matching the pattern "v\*". The tag must follow the format "v0.0.0" (e.g. "v0.1.0", "v1.0.0", etc.) for the workflow to run successfully.

A production release will be created when a tag is pushed that follows the format "v0.0.0" (e.g. "v0.1.0", "v1.0.0", etc.). A pre-release will be created when a tag is pushed that follows the format "v0.0.0-rc" (e.g. "v0.1.0-rc", "v1.0.0-rc", etc.). This allows for both stable releases and pre-releases to be created and published to GitHub Releases.

To create a new release, you can use the following command to create a new tag and push it to the repository:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This will tag the current commit with the version "v0.1.0" and push the tag to the remote repository, which will trigger the GitHub Actions workflow to build and publish the package to GitHub Releases.

**Note:** Is is important that GitHub Releases are _only_ created via the GitHub Actions workflow, and not manually via the GitHub UI. This is because the workflow ensures that the package is built and published correctly.

## Documentation

This repository uses [MkDocs](https://www.mkdocs.org/) for documentation. The documentation source files are located in the `docs` directory.

### GitHub Actions for Documentation

MkDocs gets deployed to GitHub Pages using GitHub Actions. The workflow for this is located at `.github/workflows/deploy-docs.yml`.
Before deployment, another GitHub Action workflow runs to check that the documentation builds correctly and has no linting or formatting issues.
This workflow is located at `.github/workflows/ci-docs.yml`.

### Local Development of Documentation

To run the documentation locally:

1. Create a Python virtual environment and activate it.

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the dependencies for MkDocs.

   ```bash
   make docs-install
   ```

3. Run the MkDocs development server.

   ```bash
   make docs-serve
   ```

## Linting and Testing

### GitHub Actions

This repository has GitHub Actions workflows set up for linting and testing. The workflows are located at:

- `.github/workflows/ci-fmt.yml` for linting and formatting checks (primary language).
- `.github/workflows/ci-test.yml` for running automated tests.
- `.github/workflows/ci-docs.yml` for checking that the documentation builds correctly and has no linting or formatting issues.
- `.github/workflows/megalinter.yml` for running MegaLinter, which checks for linting and formatting issues across multiple languages and file types (this is a catch-all linter).
- `.github/workflows/deploy-docs.yml` for deploying documentation to GitHub Pages.

### Running Tests and Linters Locally

#### Primary Language

To run the linters and formatters for the primary language (Python) locally, you can use the following command:

```bash
make lint
```

To apply automatic fixes for any linting or formatting issues found, you can use:

```bash
make fmt
```

To run the tests locally, you can use:

```bash
make test-unit
```

#### MegaLinter

This repository uses MegaLinter for comprehensive linting across multiple languages and file types.
We use this so that all additional assets in the repository (e.g. YAML files, Markdown files, etc.) are also linted and checked for formatting issues, without having to set up specific linters for each file type.

To run MegaLinter locally, you can use the following command:

```bash
make megalinter
```

#### Documentation linting and building

This repository uses Markdownlint for linting the documentation. To run Markdownlint locally, you can use the following:

```bash
make docs-lint
```

**Note:** This will install `markdownlint-cli` globally via npm if it is not already installed.

To apply automatic fixes for any linting issues found by Markdownlint, you can use:

```bash
make docs-fix
```

To test that the documentation builds correctly, you can use the following command:

```bash
make docs-build
```

**Note:** This depends on MkDocs being set up for the repository. Instructions for setting up MkDocs can be found in the [Documentation](#documentation) section of this README.
