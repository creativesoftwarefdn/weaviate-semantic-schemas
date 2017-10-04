# Weaviate Semantic Schema Repo with Ontologies

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

Template EXAMPLE:

```
{
	"@context": "http://schema.org",
	"version": "x.x.x", // semver version number of this schema
	"type": "thing", // thing or action
	"name": "schema.org - Thing",
	"maintainer": "yourfriends@weaviate.com", // should be email
	"classes": [{
		"class": "Thing",
		"description": "This is a Thing",
		"properties": [{
			"name": "url",
			"@dataType": ["Person", "string"], // if a cref it has a capital (= Class) otherwise "string" or "int"
			"description": "URL of the item."
		}]
	}]
}
```

Golang Struct:

```
// Schema is a representation in GO for the custom schema provided.
type Schema struct {
	Context    string  `json:"@context"`
	Version    string  `json:"version"`
	Type       string  `json:"type"`
	Maintainer string  `json:"maintainer"`
	Name       string  `json:"name"`
	Classes    []Class `json:"classes"`
}

// Class is a representation of a class within the schema.
type Class struct {
	Class       string     `json:"class"`
	Description string     `json:"description"`
	Properties  []Property `json:"properties"`
}

// Property provides the structure for the properties of the class items.
type Property struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	DataType    []string `json:"@dataType"`
}
```

_Note: You can use the existing schemas as templates or examples_

## Generators

Generators are use to create custom schemas. They should be run from the ./generators dir of the repo. Like: `$ cd generators && python generate_schema.org.py`. The schema.org generator `generate_schema.org.py` needs one argument, the semver version of the schema you want to generate, like: `python generate_schema.org.py 1.0.0`.
