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

Template in pseudo-JSON:

```
{
	"@context": URL,
	"type": thing or action,
	"name": string,
	"maintainer": email,
	"classes": [{
		"class": class with capital,
		"description": string,
		"properties": [{
			"name": string,
			"@dataType": [url of data type],
			"description": description of the property
		}]
	}]
}
```

### Example of JSON file

```
{
    "@context": "http://schema.org",
    "type": "thing",
    "name": "schema.org - Thing",
    "maintainer": "yourfriends@weaviate.com",
    "classes": [
        {
            "class": "Thing",
            "description": "This is a Thing",
            "properties": [
                {
                    "name": "url",
                    "@dataType": ["URL"],
                    "description": "URL of the item."
                },
                {
                    "name": "additionalType",
                    "@dataType": ["URL"],
                    "description": "An additional type for the item, typically used for adding more specific types from external vocabularies in microdata syntax. This is a relationship between something and a class that the thing is in. In RDFa syntax, it is better to use the native RDFa syntax - the 'typeof' attribute - for multiple types. Schema.org tools may have only weaker understanding of extra types, in particular those defined externally."
                }
            ]
        },
        {
            "class": "Event",
            "description": "This is an Event",
            "properties": [
                {
                    "name": "composer",
                    "@dataType": [
                        "Person",
                        "Organization"
                    ],
                    "description": "The person or organization who wrote a composition, or who is the composer of a work performed at some event."
                },
                {
                    "name": "attendees",
                    "@dataType": [
                        "Person",
                        "Organization"
                    ],
                    "description": "A person attending the event."
                }
            ]
        },
        {
            "class": "Person",
            "description": "This is a Person",
            "properties": [
                {
                    "name": "givenName",
                    "@dataType": [
                        "Text"
                    ],
                    "description": "Given name. In the U.S., the first name of a Person. This can be used along with familyName instead of the name property."
                },
                {   "name": "faxNumber",
                    "@dataType": [
                        "Text"
                    ],
                    "description": "The fax number."
                }
            ]
        }   
    ]
}
```

### Golang Struct:

```
// Schema is a representation in GO for the custom schema provided.
type Schema struct {
	Context    string  `json:"@context"`
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

Generators are use to create custom schemas. They should be run from the ./generators dir of the repo. Like: `$ cd generators && node create_schema.org.js`
