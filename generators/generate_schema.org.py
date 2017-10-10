import json
import urllib.request
import sys
from pathlib import Path
import datetime
import copy
import os, errno

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
# Create file process
# i = input Class
# processedClasses = skipp class array
##
def createFile( i, processedClasses, version ):

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
                        subArray["description"] = ' '.join(graph["rdfs:comment"])
                    else:
                        subArray["description"] = graph["rdfs:comment"]
                else:
                    subArray["description"] = None
                # append the array
                returnArray.append(subArray)
        # sort the array and return
        return sorted(returnArray, key=lambda k: k['name']) 

    ##
    # Create the Tree
    #
    # i = the startpoint of the tree
    ##
    def createTree( i ):
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
                        newTree["class"]        = currentClass
                        if isinstance(graph["rdfs:comment"], list):
                            newTree["description"] = ' '.join(graph["rdfs:comment"])
                        else:
                            newTree["description"] = graph["rdfs:comment"]
                        newTree["properties"]   = properties
                        tree["classes"].append(newTree)
                    else :
                        # request and run the new schema
                        if currentClass not in processedClasses:
                            if "rdfs:subClassOf" in graph:
                                # check if string or array
                                if "@id" in graph["rdfs:subClassOf"]:
                                    # check if it has the correct subClass settings
                                    if graph["rdfs:subClassOf"]["@id"] == "schema:" + i:
                                        createTree(currentClass)
                                else:
                                    # loop through the array
                                    for subSubClass in graph["rdfs:subClassOf"]:
                                        # check if string or array
                                        if "@id" in subSubClass:
                                            # check if it has the correct subClass settings
                                            if subSubClass["@id"] == "schema:" + i:
                                                createTree(currentClass)

    ##
    # Clean the tree function
    ##
    def cleanTree( iTree ):
        newTree = copy.deepcopy(iTree)
        newTree["classes"] = []
        for treeClass in iTree["classes"]:
            for treeProps in treeClass["properties"]:
                if "string" in treeProps["@dataType"]:
                    treeProps["@dataType"] = ["string"];
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
    createTree(i)

    # cleanup files
    # If there is a string and a ref, always use only the string
    # This might be depricated in the future
    treeToClean = tree
    tree = cleanTree(treeToClean)

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
    buildLog("ERROR: Add one argument with the semver version of the schema.")
elif (len(arguments) == 1):
    createFile('Thing', ['Action'], arguments[0])
    createFile('Action', [], arguments[0])
    buildLog("DONE")
else:
    buildLog("ERROR: Too many arguments given.")