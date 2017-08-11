# Weaviate Semantic Schema Repo

In this repo you can find a set of commonly used semantic schemas like [schema.org](schema.org)

Within Weaviate, you can use these schema's to define things or actions.

You can find more info in the [Weaviate Repo](https://github.com/weaviate/weaviate)

_Note: The available schemas in Weaviate are based on schema.org and cover already. In case you have a valuable schema that you want to share, feel free to issue a pull request_

## Schema types

Weaviate knows two types of schemas:

1. Thing schemas
2. Action schemas

The Thing schemas are used to define actual things. The Action schemas are used to define actions. These actions will also be made available to the things. For example, to execute a command.

## Creating a custom schema

This repo contains examples of ready to use schemas. But you can create your own schema.

Template:

```
{
    "context": string           // example: http://schema.org
    "type": ["thing", "action"] // is it to describe an action or a thing?
    "maintainer" email          // email of maintainer
    "name": string              // name of schema
    "schema": {
        "Class": {              // class should have capital first letter
            "description": string
            "@dataType": [ urlOfType ] // example: http://schema.org/URL
        }
    }
}
```

_Note: You can use the existing schemas as templates or examples_

## Generators

Generators are use to create custom schemas. They should be run from the ./generators dir of the repo. Like: `$ cd generators && node create_schema.org.js`