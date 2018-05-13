const https = require('https');

exports.handler = function (request, context) {
    if (request.directive.header.namespace === 'Alexa.Discovery' && request.directive.header.name === 'Discover') {
        log("DEBUG:", "Discover request", JSON.stringify(request));
        handleDiscovery(request, context, "");
    }
    else if (request.directive.header.namespace === 'Alexa.PowerController') {
        if (request.directive.header.name === 'TurnOn' || request.directive.header.name === 'TurnOff') {
            log("DEBUG:", "TurnOn or TurnOff Request", JSON.stringify(request));
            handlePowerControl(request, context);
        }
    }

    function handleDiscovery(request, context) {
        var payload = {
            "endpoints": [{
                "endpointId": "sonnenschutz",
                "manufacturerName": "Smart Home",
                "friendlyName": "Sonnenschutz",
                "description": "Markise",
                "displayCategories": ["SWITCH"],
                "capabilities": [{
                    "type": "AlexaInterface",
                    "interface": "Alexa",
                    "version": "3"
                },
                    {
                        "interface": "Alexa.PowerController",
                        "version": "3",
                        "type": "AlexaInterface",
                        "properties": {
                            "supported": [{
                                "name": "powerState"
                            }],
                            "retrievable": false
                        }
                    }
                ]
            }]
        };
        var header = request.directive.header;
        header.name = "Discover.Response";
        log("DEBUG", "Discovery Response: ", JSON.stringify({header: header, payload: payload}));
        context.succeed({event: {header: header, payload: payload}});
    }

    function log(message, message1, message2) {
        console.log(message + message1 + message2);
    }

    function sendRequest(command, powerState) {
        var options = {
            host: process.env.somfyServiceHost,
            port: 1111,
            path: '/somfy/MAIN/' + command,
            method: 'GET'
        };

        var req = https.request(options, function (res) {
            res.setEncoding('utf-8');

            var responseString = '';
            res.on('data', function (data) {
                responseString += data;
            });

            res.on('end', function () {
                console.log('Response: ' + responseString);

                var contextResult = {
                    "properties": [{
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": powerState,
                        "timeOfSample": new Date().toISOString(), //retrieve from result.
                        "uncertaintyInMilliseconds": 50
                    }]
                };
                var responseHeader = request.directive.header;
                responseHeader.name = "Response";
                responseHeader.namespace = "Alexa";

                var response = {
                    context: contextResult,
                    event: {
                        header: responseHeader,
                        endpoint: {
                            scope: {
                                type: "BearerToken",
                                token: "access-token-from-Amazon"
                            },
                            endpointId: "demo_id"
                        },
                        payload: {}

                    }
                };
                log("DEBUG", "Alexa.PowerController ", JSON.stringify(response));
                context.succeed(response);
            });
        });

        req.on('error', function (e) {
            console.error('HTTP error: ' + e.message);
            console.log('API request completed with error(s).');
        });

        req.end();
    }

    function handlePowerControl(request, context) {
        var requestMethod = request.directive.header.name;

        if (requestMethod === "TurnOn") {
            console.log("turnOn Called" + request.directive.endpoint.endpointId);
            sendRequest("DOWN", "ON");

        }
        else if (requestMethod === "TurnOff") {
            sendRequest("UP", "OFF");
        }
    }
}
