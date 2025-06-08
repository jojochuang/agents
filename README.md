# agents

## setup

The scripts connect various services to perform tasks.
These scripts are called by Gemini Agentic API to execute the functions.

Add API access tokens to env.sh.

For example:

```
#!/bin/bash
export JIRA_API_TOKEN=xxxxx
```

## descriptions
add_user_to_apache_jira.py -- grant a user the contributor role in an Apache project.
