import json
import urllib.request
import sys
from pathlib import Path
import datetime
import copy
import os, errno
import re

##
# Buildlog function
#
# i = output line
##
counter = 1
def buildLog( i ):
    global counter
    counter += 1
    print(str(counter).zfill(7)  + " | " + str(datetime.datetime.now().time()) + " | " + i)

##
# find camelcase
##
def camelCaseSplit(i):
    matches = re.sub('([a-z])([A-Z])', r'\1 \2', i).split()
    return matches

##
# Removes CamelCase from a sentene
#
# i = input sentence
def sentenceToNonCamel(i):

    # remove HTML
    i = re.sub('<[^<]+?>', '', i)

    # start with empty string
    cleanSentence = ""

    for word in i.split():
        # check if cammel, (true or false)
        if ((word != word.lower() and word != word.upper()) == True):

            # split into camelcase words
            splittedWord = camelCaseSplit(word)

            # IF MORE THAN ONE WORD ALL TO LOWER
            if len(splittedWord) > 1:
                for cleanWord in splittedWord:
                    # add the word to the sentence
                    cleanSentence += cleanWord.lower() + " "
            # One word, keep capital (maybe name like Michael)
            else:
                cleanSentence += word.lower() + " "
        else:
            # add the regular word
            cleanSentence += word + " "

    return cleanSentence[:-1]

##
# Create file process
# i = input Class
# processedClasses = skipp class array
##
def createFile( i, processedClasses, version, taggerUrl ):

    ##
    # Load jsonld file from cache
    #
    # i = jsonld file
    ##
    def loadJsonld( i ):
        with open(i) as jsonldFile:    
            return json.load(jsonldFile) 

    ##
    # Download and cache Json Schemas
    #
    # i = complete path like: http://schema.org/Thing.jsonld
    ##
    def getSchema( i ):
        # set cache path
        cachePath = 'cache/' + i[i.rfind("/")+1:]
        # check if file is there
        if Path(cachePath).is_file():
            buildLog("CACHED: " + cachePath)
            return loadJsonld(cachePath)
        else:
            # Download file
            try:
                buildLog("DOWNLOAD: " + i)
                urllib.request.urlretrieve(i, cachePath)
                return loadJsonld(cachePath)
            except:
                buildLog("FAILED AND SKIP: " + i)

    ##
    # Check if it should be a string. This validate if it should be a string, if there are ONLY schema:rangeIncludes, it should be a string
    #
    # i = Class to check
    ##
    def shouldBeString( i ):
        workFile = getSchema("http://schema.org/" + i + ".jsonld")
        for graph in workFile["@graph"]:
            if "@type" in graph and graph["@type"] == "rdf:Property":
                return False
        return True

    ##
    # Load and get props
    #
    # i = class to load
    ##
    def getDataTypesInArray( i ):
        if isinstance(i, list):
            returnArray = []
            for subI in i:
                currentProp = subI["@id"].split(":")[1]
                if currentProp[0].isupper() == True and shouldBeString(currentProp) == False:
                    returnArray.append(currentProp)
                elif shouldBeString(currentProp) == True:
                    if "string" not in returnArray:
                        returnArray.append("string")
            return returnArray
        else:
            currentProp = i["@id"].split(":")[1]
            if currentProp[0].isupper() == True and shouldBeString(currentProp) == False:
                return [currentProp]
            elif shouldBeString(currentProp) == True:
                return ["string"]

    ##
    # Gets an array of props
    #
    # i = based on the current graph
    ##
    def getProps( i ):
        # returnArray prep
        returnArray = []
        # loop through the input and find props
        for graph in i:
            currentProp = graph["@id"].split(":")[1]
            # If first of schema is lower = prop
            if currentProp[0].isupper() == False and "@type" in graph and graph["@type"] == "rdf:Property":
                subArray = {}
                subArray["name"] = currentProp
                subArray["@dataType"] = getDataTypesInArray(graph["schema:rangeIncludes"])
                if "rdfs:comment" in graph:
                    if isinstance(graph["rdfs:comment"], list):
                        subArray["description"] = sentenceToNonCamel(' '.join(graph["rdfs:comment"]))
                    else:
                        subArray["description"] = sentenceToNonCamel(graph["rdfs:comment"])
                else:
                    subArray["description"] = None
                # append the array
                returnArray.append(subArray)
        # sort the array and return
        return sorted(returnArray, key=lambda k: k['name']) 

    ##
    # Adds the weights to the types.
    # Main classes always count as heavy, where the value accumulates down
    # Types as second heavy, where the value accumulates down
    # description (Nouns are used) is third heave, where the value accumulates down
    #
    ##
    def addKeyWordsFromString(mainClasses, mainTypes, description, NERurl):

        # receives all return objects
        returner = []

        # add classes
        mainClasses = camelCaseSplit(mainClasses)

        # Add all main classes
        for mainClass in mainClasses:
            returner.append({
                "keyword":  mainClass.lower(),
                "weight": 1.0 # main class always has a weight of 1.0
            })

        # Add the types if available
        if mainTypes != False:
            for mainType in mainTypes:
                for typeSplit in camelCaseSplit(mainType):
                    # add if class (= uppercase)
                    if typeSplit[0].isupper():
                        returner.append({
                            "keyword": typeSplit.lower(),
                            "weight": 0.5 # main class always has a weight of 1.0
                        })

        # add keywords
        buildLog("DOWNLOAD NER")
        # download NER
        response = urllib.request.urlopen("http://" + NERurl + "/?sentence=" + urllib.parse.quote_plus(description))
        for NERitem in json.loads(response.read().decode()):
            if NERitem["potentialThing"] == True:
                returner.append({
                    "keyword":  NERitem["word"].lower(),
                    "weight": 0.25 # main class always has a weight of 1.0
                })

        return returner

    ##
    # Create the Tree
    #
    # i = the startpoint of the tree
    ##
    def createTree( i, taggerUrl ):
        # add to processedClasses
        processedClasses.append(i)
        workFile = getSchema("http://schema.org/" + i + ".jsonld")
        #
        if "@graph" in workFile:
            # get a list of properties
            properties = getProps(workFile["@graph"])
            # loop through the file and find Classes
            for graph in workFile["@graph"]:
                currentClass = graph["@id"].split(":")[1]
                # If first of schema is Upper = class
                if currentClass[0].isupper() == True:
                    # Check if it is the current schema to extend tree
                    if currentClass == i:
                        # extend the tree
                        newTree = {}
                        newTree["class"] = currentClass
                        if isinstance(graph["rdfs:comment"], list):
                            newTree["description"] = sentenceToNonCamel(' '.join(graph["rdfs:comment"]))
                        else:
                            newTree["description"] = sentenceToNonCamel(graph["rdfs:comment"])
                        newTree["properties"]   = properties
                        newTree["keywords"] = addKeyWordsFromString(newTree["class"], False, newTree["description"],taggerUrl)
                        tree["classes"].append(newTree)
                    else :
                        # request and run the new schema
                        if currentClass not in processedClasses:
                            if "rdfs:subClassOf" in graph:
                                # check if string or array
                                if "@id" in graph["rdfs:subClassOf"]:
                                    # check if it has the correct subClass settings
                                    if graph["rdfs:subClassOf"]["@id"] == "schema:" + i:
                                        createTree(currentClass, taggerUrl)
                                else:
                                    # loop through the array
                                    for subSubClass in graph["rdfs:subClassOf"]:
                                        # check if string or array
                                        if "@id" in subSubClass:
                                            # check if it has the correct subClass settings
                                            if subSubClass["@id"] == "schema:" + i:
                                                createTree(currentClass, taggerUrl)

    ##
    # Clean the tree function
    ##
    def cleanTree( iTree, taggerUrl ):
        newTree = copy.deepcopy(iTree)
        newTree["classes"] = []
        for treeClass in iTree["classes"]:
            for treeProps in treeClass["properties"]:
                # add keywords
                treeProps["keywords"] = addKeyWordsFromString(treeProps["name"], treeProps["@dataType"], treeProps["description"], taggerUrl)
                # set string
                if "string" in treeProps["@dataType"]:
                    treeProps["@dataType"] = ["string"]
            newTree["classes"].append(treeClass)
        return newTree

    ##
    # Set basic vars
    ##
    tree = {}
    tree['@context']     = 'http://schema.org'
    tree['version']     = version
    tree['type']        = i.lower()
    tree['name']        = 'Schema.org - ' + i
    tree['maintainer']  = 'yourfriends@weaviate.com'
    tree['classes']     = []

    ##
    # Create cache dir
    ##
    if not os.path.exists("cache/"):
        os.makedirs("cache/")

    ##
    # Start creation process of Class
    ##
    createTree(i, taggerUrl)

    # cleanup files
    # If there is a string and a ref, always use only the string
    # This might be depricated in the future
    treeToClean = tree
    tree = cleanTree(treeToClean, taggerUrl)

    # sort classes
    tree['classes'] = sorted(tree['classes'], key=lambda k: k['class'])

    # write to file
    file = open("../weaviate-" + i + "-ontology-schema_org.json","w") 
    file.write(json.dumps(tree , indent=4, sort_keys=True))

    # write to minified file
    file = open("../weaviate-" + i + "-ontology-schema_org.min.json","w") 
    file.write(json.dumps(tree, separators=(',',':')))

    file.close()

##
# START BUILD
##

arguments = sys.argv[1:]

if (len(arguments) == 0):
    buildLog("ERROR: Add one argument with the semver version (like 0.0.1) of the schema or add second argument with server of tagger.")
    buildLog("EXAMPLE: generate_schema.org.py 0.0.1 www.example.com")
elif (len(arguments) == 1):
    buildLog("NOT USING TAGGER")
    createFile('Thing', ['Action'], arguments[0], None)
    createFile('Action', [], arguments[0], None)
    buildLog("DONE")
elif (len(arguments) == 2):
    buildLog("NOT USING TAGGER")
    createFile('Thing', ['Action'], arguments[0], arguments[1])
    createFile('Action', [], arguments[0], arguments[1])
    buildLog("DONE")
else:
    buildLog("ERROR: Too many arguments given.")