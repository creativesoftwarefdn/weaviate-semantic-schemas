# Weaviate Semantic Schema Repo

In this repo you can find a set of commonly used semantic schemas like [schema.org](schema.org)

Within Weaviate, you can use these schema's to define things or actions.

You can find more info in the [Weaviate Repo](https://github.com/weaviate/weaviate)

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
            "type": [string, array, object, integer, ref] // ref = expected = reference
        }
    }
}
```

_Note: You can use the existing templates as examples_

## Generators

Generators are use to create custom schemas. They should be run from the ./generators dir of the repo. Like: `$ cd generators && node create_schema.org.js`