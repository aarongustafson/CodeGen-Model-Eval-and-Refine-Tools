# CodeGen Model Evaluation and Refinement Tools

A test suite for evaluating & refining generative models’ “knowledge“ of code pattern best practices.

## Install & Setup

Before you begin, you’ll want to create a new repository based on this template. Then configure the repository to your specific needs.

To configure your repository, you’ll need to

1. Create [an Azure OpenAI resource](https://portal.azure.com/#view/Microsoft_Azure_Marketplace/GalleryItemDetailsBladeNopdl/id/Microsoft.CognitiveServicesOpenAI/)
2. [Set up a deployment of the LLM model](https://oai.azure.com/) of your choosing
3. Put the credentials & such in an [`.env` file](#env-file-setup) in the root of the project (you can copy over `.env.sample`)
4. [Install the dependencies](#dependencies)

### .env File Setup

You will need the following keys in your `.env` file:

```env
AZURE_OPENAI_API_BASE=https://YOUR_PROJECT.openai.azure.com/
AZURE_OPENAI_API_KEY=*******************
AZURE_OPENAI_API_MODEL=YOUR_DEPLOYENT_NAME
AZURE_OPENAI_API_VERSION=THE_API_VERSION
ITERATIONS_PER_PROMPT=10
TEMPERATURE=0.95
TOP_P=0.95
MAX_TOKENS=800
SLEEP_TIME=10
OUTPUT_EXTENSION=.html
```

* `AZURE_OPENAI_API_BASE` - This is the deployment you’re testing against
* `AZURE_OPENAI_API_KEY` - This is your secret key to access the API endpoint
* `AZURE_OPENAI_API_MODEL` - This is the model you are testing against within that deployment
* `AZURE_OPENAI_API_VERSION` - This is the current API version (_not_ the model version)
* `ITERATIONS_PER_PROMPT` - How many times you’d like to run each prompt against the model (recommend at least 5, but more will give you a better sense of variability)
* `TEMPERATURE` - The temperature value you’d like applied to the prompts. Higher allows the model to improvise more and is likely to give you a better sense of the the range of potential responses the model may give.
* `TOP_P` - A high “Top p” value tells the model to consider more potential words and can yield a greater variety in responses.
* `MAX_TOKENS` - The maximum number of tokens you want to allow between the prompt and the response. Depending on the type of code generation you are testing, you could keep this low. The absolute max may depend on the model you’re using.
* `SLEEP_TIME` - How long (in seconds) to wait between prompts; helps you avoid getting throttled.

The best place to gather many of these details is in [Azure AI Studio’s Playground](https://oai.azure.com/portal/playground). Pick the "Chat" playground and then click `View Code > Key Authentication` to find the Endpoint (API Base), API Key, and API version (at the end of the ENDPOINT string in the sample Python code).

### Dependencies

You’ll need Python and both the `openai` and `dotenv` modules to run the script and pull in the environment variables:

```bash
$> pip install openai
$> pip install python-dotenv
```

## Running an Evaluation

To run an evaluation, you will follow these steps:

1. Document your test & evaluation criteria
1. Configure your tests
1. Run the tests
1. Evaluate the results
1. Generate diffs

### Document Test & Evaluation Criteria

Before you write your tests, I recommend spending some time documenting

1. Your ideal code output (which may be one thing or one of several acceptable patterns)
1. Acceptable variations (e.g., if the value of a particular property can be improvised, note it)
1. Unacceptable variations (e.g., if a specific property must exist, note it)
1. A list of prompts you would reasonably expect to result in a model returning the code sample you’re looking for. Being too prescriptive will result in very little variance in the proposed code samples, so be as specific as you need to be to point the model in the right direction, but keep it open to interpretation. Try some more specific prompts and some less specific ones too. Use specific keywords from documentation in some prompts and synonyms for those keywords in others.

This documentation will not only help you generate your tests, it will help with [evaluating the results](#evaluating-the-results) too.

 If you want to include these docs in the directory structure of this project, be sure to commit them before proceeding.

### Configuring the tests

Tests are stored in the `tests.json` file. Each test contains a `title` string, `prompts` array of prompt strings, and an optional `prefix` string that will be added before each prompt in the test. For example, if I wanted to test the model’s understanding of best practices for building an HTML radio group, I could include the following:

```json
{
  "title": "Radio Group",
  "prefix": "Given the options light, dark, and high contrast, create the HTML only (no JavaScript) for",
  "prompts": [
    "a radio group to choose a theme",
    "a “theme” picker using radio controls",
    "a radio control-based theme chooser",
    "an accessible theme chooser with radio controls"
  ]
}
```

This will trigger the tool to run a test titled “Radio Group.” It will execute the following prompts against the model:

1. Given the options light, dark, and high contrast, create the HTML only (no JavaScript) for a radio group to choose a theme
1. Given the options light, dark, and high contrast, create the HTML only (no JavaScript) for a “theme” picker using radio controls
1. Given the options light, dark, and high contrast, create the HTML only (no JavaScript) for a radio control-based theme chooser
1. Given the options light, dark, and high contrast, create the HTML only (no JavaScript) for an accessible theme chooser with radio controls

The number of prompt variations you choose to include is up to you. Try to describe the component in a few different ways to see how well the model “understands” key coding concepts (e.g., semantics, accessibility, performance).

Once you have your tests written, you’re ready to begin running them. Commit your files to the repository and then proceed to the next step.

### Running the Tests

To run your tests against the model, open the command line and run the Python script

```bash
$> python run_tests.py
```

If all goes well (and you aren’t throttled), the Python code should work its way through your test suite and store the results of the evaluations in the `./output` directory. For every test, it will create a directory that is named to match the test name. Within that directory, it will create numbered subdirectories for each prompt. And within those directories, the response from each individual iteration of the prompt will be captured to a file named with a UUID + the extension you configured in your `.env`. 

For example, running one iteration of each prompt from the test above would result in something like this:

```bash
output
   |-- Radio Group
   |   |-- 1
   |   |   |-- f9b6abd4-5952-4df6-b638-a49fee156a21.html
   |   |-- 2
   |   |   |-- 594caf29-05bb-4699-ad50-362347132ca9.html
   |   |-- 3
   |   |   |-- 4625cc9e-a38a-480d-bdee-4c80065e362e.html
   |   |-- 4
   |   |   |-- 42159a0b-1273-49a1-a517-c99ce56480fd.html
```

If you run into issues with your tests running to completion, you might consider breaking the tests into batches or running the tests overnight or at a time when there is less network traffic.

Once you have your results, commit them to the repository before proceeding. You will want to keep track of the commit ID for later.

### Evaluating the results

Once you have your results, it’s time to begin evaluating. Use [your documentation](#document-test--evaluation-criteria) to evaluate each code suggestion. 

When the output falls outside the acceptable bounds of your evaluation (because it includes something it shouldn’t or missed something critical), edit the file to align it with your ideal result. Then commit that individual file to the repo with a commit message that enumerates each individual error on its own line. Be as descriptive and instructive as possible. Your commit messages can be used to help improve the model.

For example:

```txt
Error: Current page must be indicated using `aria-current="page"`
Error: Style changes (such as bold) must not be the only means of indicating a link is the current page
```

Repeat this process for every file in the output directory.

If you are looking to speed up this process a bit, you could tackle the output on a per-test basis. Make the necessary changes to every file first and save the files, but don’t commit them yet. As you go, make a scratch file containing the commit message you plan to use for each error you encountered. Then go through the files and commit them one-by-one using the appropriate commit messages from your scratch file. This can make things faster, but you do need to be careful not to commit more than one file at a time because the next step relies on them being individual commits.

When you’re done and all output files have been aligned with your ideal code snippets and committed to the repo with descriptive error messages, proceed to the final step.

### Generate Diff Files

The last step is to generate the diff files that can be used to refine the model’s output. To generate them, run the shell script and provide the commit ID that was the last commit _before_ you began evaluating the code samples:

```bash
$> ./diff-generator.sh 7189a15dd6fc785314af2dc4e035de83ec83b5a8
```

The script will run through every commit and generate a `.diff` file for it. At the top of each file will be the commit message associated with that commit (which is why having them as individual commits is super helpful). If you’d like to improve the readability of the files, you might consider running a batch conversion of " Error:" to "\r\nError:" in the text editor of your choice as this will ensure each Error from you commit messages appears on its own line.
