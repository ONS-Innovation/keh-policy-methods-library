# Adding Checks to the Library

This guide provides instructions on how to add new checks to the Policy Methods Library.
It covers the process of defining a new check, implementing its logic, and integrating it into the library for use in various policies.
The guide also covers any standards / patterns the new check needs to follow to ensure consistency across the library.

## Step 1: Understand the Check Requirements

Before you start implementing a new check, it's crucial to have a clear understanding of the requirements and criteria for the check.

Question to ask yourself:

- What is the purpose of the check?
- What data will the check need to access?
- Where will the data come from? (i.e. What API calls will be needed to retrieve the data?)
- What are the pass/fail criteria for the check?
- Are there any edge cases or error conditions that need to be handled?

## Step 2: Define the Check Logic

Once you have a clear understanding of the requirements, you can start defining the logic for the check.

Create a new Python file within the `policy_methods_library/checks` directory that will contain the implementation of your new check.
The name of this file must be descriptive of the check's purpose and follow the existing naming conventions in the library.

For example, if you were creating a check to verify that a repository isn't empty, you might name the file `empty_repository.py`.

Then, within this file, you will define a function that implements the logic of the check.

The function must meet the following criteria:

- It should be named using the convention `check_<check_name>`, where `<check_name>` is a descriptive name for the check.
    It can help if the check name is the same as the file name (without the `.py` extension) to maintain consistency and clarity.
- The check should allow for both direct data input and data retrieval from an API, to provide flexibility in how the check can be used.
- The function should return a dictionary containing the following keys:
  - `result`: A string indicating the result of the check, which can be "pass", "fail", or "error".
  - `message`: A string providing additional information about the result of the check, such as details on why the check passed or failed, or any error messages if applicable.
  - `details`: A dictionary containing any additional data. This should be left as an empty dictionary if there are no additional details to provide.

    > **Note:** It is very important that the contents of `details` is documented clearly so users of the check understand what data they can expect to receive in this field.

- Any helper functions or classes that are necessary for the implementation of the check should be defined within the same file, to keep all relevant code for the check in one place.
    Prefix these helper functions with an underscore to indicate that they are intended for internal use within the check implementation.

## Step 3: Test the Check Locally

Before continuing, make sure you have tested the check locally to ensure that it behaves as expected and meets the defined criteria.
You can create a simple test script that imports the check function and runs it with various inputs to verify that it returns the correct status and messages for different scenarios.

## Step 4: Write Unit Tests for the Check

Self-explanatory. Ensure to follow the existing patterns for unit tests in the library, and cover a range of test cases, including edge cases and error conditions.
Make sure that the coverage for the new check is realistic and as high as possible (aim for 100% coverage of the check function).

## Step 5: Document the Check

Create a new markdown file in the `docs/checks` directory with the same name as the check (e.g. `empty_repository.md`).

In this file, provide comprehensive documentation for the check, including:

- An overview of the check and its purpose.
- The origin of the check within Policy.
- Criteria on when the check would pass, fail, or return an error.
- A reference to the check function in the codebase (use MkDocStrings for this).
- Usage examples demonstrating how to use the check with both direct data input and data retrieval from an API.
- An explanation of the GitHub Integration / API endpoints used in the check, if applicable.
- A "Required Permissions" section documenting what GitHub App permissions are needed (if any). Include a note if permissions are only required when retrieving data via API vs. when data is passed directly.

> **Note:** The above list is a minimum standard. You should feel free to include any additional information that you think would be helpful.

## Step 6: Update General Documentation

In addition to the check documentation, you should also update any general documentation that references checks, such as overview pages or indexes, to include the new check.

An important page to highlight is the `github-app-permissions.md` page, which lists all the checks in the library and the GitHub App permissions they require. This **must** be updated to include the new check and its required permissions (if any).

## Step 7: Integrate the Check into the Library

Finally, you will need to integrate the new check into the library so that it can be easily imported and used.

This follows KEH's standard patterns for code integration, which includes:

1. Pull Request
2. Review
3. Merge
4. Deploy / Release (Guide available in the `README` at the root of the repository)
