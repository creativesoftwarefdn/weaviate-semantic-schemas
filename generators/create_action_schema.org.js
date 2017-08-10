'use strict';
/*                          _       _
 *__      _____  __ ___   ___  __ _| |_ ___
 *\ \ /\ / / _ \/ _` \ \ / / |/ _` | __/ _ \
 * \ V  V /  __/ (_| |\ V /| | (_| | ||  __/
 *  \_/\_/ \___|\__,_| \_/ |_|\__,_|\__\___|
 *
 * Copyright © 2016 Weaviate. All rights reserved.
 * LICENSE: https://github.com/weaviate/weaviate/blob/master/LICENSE
 * AUTHOR: Bob van Luijt (bob@weaviate.com)
 * See www.weaviate.com for details
 * Contact: @weaviate_iot / yourfriends@weaviate.com
 */

/*
 * Include props
 */
var http    = require('http'),
    url     = require("url"),
    path    = require("path"),
    fs      = require('fs'),
    Sync    = require('sync'),
    tree    = { 
        "context": "http://schema.org",
        "type": "action",
        "name": "schema.org - Action",
        "maintainer": "yourfriends@weaviate.com",
        "schema": {}
    },
    count = 0;

Sync(function(){
    /**
     * Log files
     * @param {*string} i Create Logs
     */
    function log(i){
        console.log(new Date() + " | " + i);
    }

    /**
     * Prefix number with leading zeros
     * @param {*int} num  Number to pad
     * @param {*int} size Size of the padding
     */
    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }

    /**
     * Write to result.json file
     */
    function writeToFile(){
        for (var propName in tree) {
            if(tree["schema"][propName] !== undefined){
                if(tree["schema"][propName] === {} || tree["schema"][propName] === null || tree["schema"][propName] === undefined) {
                    delete tree["schema"][propName];
                }
            }
        }
        // merge the tree before writing to the file
        //weaviateJson.definitions.schema = tree.schema
        // write to file
        fs.writeFileSync('../weaviate-schema-Action-schema_org.json', JSON.stringify(tree, null, 4));
    }

    /**
     * Get a schema json-ld
     * @param {*string} i URL
     * @param {*function} cb Callback function
     */
    function getschema(i, cb){
        // set cache path
        var cachePath = 'cache/' + path.basename(url.parse(i).pathname);
        // check if file is cached else download from source
        if(fs.existsSync(cachePath)) {
            log("PROCESS[" + pad(count++, 4) + "]: " + cachePath);
            // return results
            cb(JSON.parse(fs.readFileSync(cachePath).toString()));
        } else {
            try {
                var request = http.get(i, function(response) {
                    if(response.statusCode === 200){
                        log("PROCESS[" + pad(count++, 4) + "]: " + i)
                        var body = '';
                        response.on('data', function(chunk) {
                            body += chunk;
                        });
                        response.on('end', function() {
                            // cache the content for later use
                            if (!fs.existsSync('cache')){
                                fs.mkdirSync('cache');
                            }
                            // write to cache file
                            fs.writeFileSync(cachePath, body);
                            // return body
                            cb(JSON.parse(body))
                        });
                    } else {
                        cb({});
                    }
                });
            } catch (e) {
                log("CONNECTION ERROR, SKIP " + i);
                cb({});
            }
        }
    }

    /**
     * Build the complete tree
     * @param {*string} context context url
     * @param {*string} schemaClass schemaClass (like: Thing)
     */
    function buildTree(context, schemaClass){
        getschema("http://" + context + "/" + schemaClass + ".jsonld", function(result){
            if(result["@graph"] !== undefined){
                result["@graph"].forEach(function(element) {
                    if(element["@id"] !== undefined){
                        var schema = element["@id"].split(":");
                        // it is uppercase therfor a class, load schema
                        if(schema[1][0] == schema[1][0].toUpperCase()){
                            if(element["rdfs:subClassOf"] !== undefined && element["rdfs:subClassOf"]["@id"] == "schema:" + schemaClass){
                                if(tree["schema"][schema[1]] === undefined){
                                    tree["schema"][schema[1]] = {};
                                    buildTree("schema.org", schema[1]);
                                }
                            }
                        } else {
                            // it is not a class, add properties
                            
                            var inRange         = false,
                                inDomain        = false,
                                rangeIncludes   = element['schema:rangeIncludes'],
                                domainIncludes  = element['schema:domainIncludes'];
                            
                            if(tree["schema"][schemaClass] === undefined){
                                tree["schema"][schemaClass] = {};
                            }

                            if (domainIncludes !== undefined) {
                                if (!Array.isArray(domainIncludes)) {
                                    domainIncludes = [domainIncludes];
                                }

                                for (var i = 0, len = domainIncludes.length; i < len; i++) {
                                    if (domainIncludes[i]['@id'] == "schema:" + schemaClass) {
                                        inDomain = true
                                    }
                                }
                            }

                            if (rangeIncludes !== undefined) {
                                if (!Array.isArray(rangeIncludes)) {
                                    rangeIncludes = [rangeIncludes];
                                }
                                
                                for (var i = 0, len = rangeIncludes.length; i < len; i++) {
                                    if (rangeIncludes[i]['@id'] == "schema:" + schemaClass) {
                                        inRange = true
                                    }
                                }
                            }

                            if (!(inRange && !inDomain)) {
                                tree["schema"][schemaClass][schema[1]] = {};
                                tree["schema"][schemaClass][schema[1]]["type"] = "string";
                                tree["schema"][schemaClass][schema[1]]["description"] = element["rdfs:comment"];
                            }
                        }
                    }
                }, this);
            };
        })
    }

    /**
     * Load weaviate Swagger and start building the tree
     */
    // build the tree
    buildTree("schema.org", "Action");
    // write to result file
    log("ADDING TO CONFIG FILE");
    writeToFile();
})