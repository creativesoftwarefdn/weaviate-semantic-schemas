import json
import urllib.request
import sys
from pathlib import Path
import datetime

##
# Buildlog function
#
# i = output line
##
counter = 1
def buildLog( i ):
    global counter
    counter += 1
    print(str(counter).zfill(5)  + " | " + str(datetime.datetime.now().time()) + " | " + i)

##
# Create file process
# i = input Class
# processedClasses = skipp class array
##
def createFile( i, processedClasses ):

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
            if currentProp[0].isupper() == False:
                subArray = {}
                subArray["name"] = currentProp
                subArray["@dataType"] = [] # SHOULD BE FIXED, SEE GITHUB ISSUE
                if "rdfs:comment" in graph:
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
                    newTree["description"]  = graph["rdfs:comment"]
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
    # Set basic vars
    ##
    tree = {}
    tree['@context']     = 'http://schema.org'
    tree['type']        = i.lower()
    tree['name']        = 'Schema.org - ' + i
    tree['maintainer']  = 'yourfriends@weaviate.com'
    tree['classes']     = []

    ##
    # Start creation process of Class
    ##
    createTree(i)

    # sort classes
    tree['classes'] = sorted(tree['classes'], key=lambda k: k['class']);

    # write to file
    file = open("../weaviate-schema-" + i + "-schema_org.json","w") 
    file.write(json.dumps(tree , indent=4, sort_keys=True)) 
    file.close()

##
# START BUILD
##
createFile('Thing', ['Action'])
createFile('Action', [])

buildLog("DONE")